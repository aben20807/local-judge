#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2020 Huang Po-Hsuan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = '1.14.0'

import re
import logging
import time
from subprocess import PIPE
import subprocess
import os
from glob import glob as globbing
from itertools import repeat
from collections import namedtuple
import configparser
import argparse
import sys
import errno
from shutil import copyfile
from shutil import copymode
if sys.version_info < (3,):
    raise ImportError(
        "You are running local-judge {} on Python 2\n".format(__version__) +
        "Please use Python 3")


GREEN = '\033[32m'
RED = '\033[31m'
NC = '\033[0m'

ERR_HANDLER = None


def get_filename(path):
    """ Get the filename without extension

    input/a.txt -> a
    """
    head, tail = os.path.split(path)
    return os.path.splitext(tail or os.path.basename(head))[0]


def expand_path(dir, filename, extension):
    """ Expand a directory and extension for filename

    a -> answer/a.out
    """
    return os.path.abspath(os.path.join(dir, filename+extension))


def create_specific_input(input_name_or_path, config):
    if os.path.isfile(input_name_or_path):
        specific_input = input_name_or_path
    else:
        parent = os.path.split(config['Config']['Inputs'])[0]
        ext = os.path.splitext(config['Config']['Inputs'])[1]
        specific_input = parent+os.sep+input_name_or_path+ext
    specific_input = os.path.abspath(specific_input)
    if not os.path.isfile(specific_input):
        ERR_HANDLER.handle(specific_input +
                           " not found for specific input.")
    return specific_input


class LocalJudge:
    def __init__(self, config):
        """ Set the member from the config file.
        """
        try:
            self._config = config['Config']
            self.build_command = self._config['BuildCommand']
            self.executable = self._config['Executable']
            self.run_command = self._config['RunCommand']
            self.temp_output_dir = self._config['TempOutputDir']
            self.diff_command = self._config['DiffCommand']
            self.delete_temp_output = self._config['DeleteTempOutput']
            self._ans_dir = self._config['AnswerDir']
            self._ans_ext = self._config['AnswerExtension']
            self.timeout = self._config['Timeout']
            self._inputs = [
                os.path.abspath(path) for path in globbing(self._config['Inputs'])]
        except KeyError as e:
            print(str(e) +
                  " field was not found in config file. " +
                  "Please check `judge.conf` first.")
            ERR_HANDLER.handle(exit_or_log='exit')
        try:
            # Create the temporary directory for output
            # Suppress the error when the directory already exists
            os.makedirs(self.temp_output_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                ERR_HANDLER.handle(str(e))
        # tests contains corresponding input and answer path
        Test = namedtuple('Test', ('test_name', 'input_filepath', 'answer_filepath'))
        self.tests = [
            Test(get_filename(path), path,
                 expand_path(self._ans_dir, get_filename(path), self._ans_ext)) for path in self._inputs]
        self.tests.sort(key=lambda t: t.test_name)

    def build(self):
        """ Build the executable which needs to be judged.
        """
        process = subprocess.Popen(
            self.build_command, stdout=PIPE, stderr=PIPE, shell=True, executable='bash')
        out, err = process.communicate()
        if process.returncode != 0:
            ERR_HANDLER.handle(
                "Failed in build stage.\n" +
                str(err, encoding='utf8') +
                " Please check `Makefile` or your file architecture first.")
        if not os.path.isfile(self.executable):
            ERR_HANDLER.handle(
                "Failed in build stage. " +
                "executable `"+self.executable+"` not found." +
                " Please check `Makefile` first.")

    def run(self, input_filepath, with_timestamp=True):
        """ Run the executable with input.

        The output will be temporarily placed in specific location,
        and the path will be returned for the validation.
        """
        if not os.path.isfile(self.executable):
            return "no_executable_to_run"
        output_filepath = os.path.join(
                self.temp_output_dir,
                get_filename(input_filepath))
        if with_timestamp:
            output_filepath += "_"+str(int(time.time()))
        output_filepath += self._ans_ext
        cmd = self.run_command
        if self.timeout != -1:
            # self.run_command = "timeout "+str(self.timeout)+" "
            cmd = "".join(["timeout ", self.timeout, " " , self.run_command])
        cmd = re.sub(r'{input}', input_filepath, cmd)
        cmd = re.sub(r'{output}', output_filepath, cmd)
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, executable='bash')
        out, err = process.communicate()
        if process.returncode == 124:
            ERR_HANDLER.handle("TLE")
        elif process.returncode != 0:
            ERR_HANDLER.handle(
                "Failed in run stage. " +
                str(err, encoding='utf8') +
                "Please check `your program` first.")
        return output_filepath

    def compare(self, output_filepath, answer_filepath):
        """ Verify the differences between output and answer.

        If the files are identical, the accept will be set to True.
        Another return value is the diff result.
        """
        if output_filepath == "no_executable_to_run":
            return False, output_filepath
        if not os.path.isfile(output_filepath):
            ERR_HANDLER.handle(
                "There was no any output from your program to compare with `" +
                answer_filepath +
                "` Please check `your program` first.")
            return False, "no_output_file"
        if not os.path.isfile(answer_filepath):
            ERR_HANDLER.handle(
                "There was no any corresponding answer. " +
                "Did you set the `AnswerDir` correctly? " +
                "Please check `judge.conf` first.")
            return False, "no_answer_file"
        # Sync the file mode
        copymode(answer_filepath, output_filepath)
        cmd = re.sub(r'{output}', output_filepath, self.diff_command)
        cmd = re.sub(r'{answer}', answer_filepath, cmd)
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, executable='bash')
        out, err = process.communicate()
        # If there is difference between two files, the return code is not 0
        if str(err, encoding='utf8').strip() != "":
            ERR_HANDLER.handle("Failed in compare stage. " +
                               str(err, encoding='utf8'))
        if self.delete_temp_output == "true":
            os.remove(output_filepath)
        accept = process.returncode == 0
        return accept, str(out, encoding='utf8', errors='ignore')


class Report:
    def __init__(self, report_verbose=0, total_score=100):
        self.total_score = total_score
        self.report_verbose = report_verbose
        self.table = []

    def print_report(self):
        """ Print the report into table view.
        """
        self.table.sort(key=lambda x: x['test'])
        tests = [x['test'] for x in self.table]

        # Return directly when the test is empty.
        if len(tests) == 0:
            ERR_HANDLER.handle(
                "Failed in report stage. " +
                "There was no any result to report. " +
                "Did you set the `Inputs` correctly? " +
                "Please check `judge.conf` first.")
            return

        # Get the window size of the current terminal.
        _, columns = subprocess.check_output(['stty', 'size']).split()

        test_len = max(len(max(tests, key=len)), len("Sample"))
        doubledash = ''.join(list(repeat("=", int(columns))))
        doubledash = doubledash[:test_len+1]+'+'+doubledash[test_len+2:]
        dash = ''.join(list(repeat("-", int(columns))))
        dash = dash[:test_len+1]+'+'+dash[test_len+2:]

        print(doubledash)
        print("{:>{width}} | {}".format("Sample", "Accept", width=test_len))
        for row in self.table:
            print(doubledash)
            mark = GREEN+"✔"+NC if row['accept'] else RED+"✘"+NC
            print("{:>{width}} | {}".format(row['test'], mark, width=test_len))
            if not row['accept'] and int(self.report_verbose) > 0:
                print(dash)
                print(row['diff'])
        print(doubledash)
        correct_cnt = [row['accept'] for row in self.table].count(True)
        correct_rate = float(100*correct_cnt/len(tests))
        obtained_score = float(self.total_score)*correct_cnt/len(tests)
        print("Correct rate: {}%\nObtained/Total scores: {}/{}".format(
            str(correct_rate), str(obtained_score), self.total_score))
        returncode = 0
        if obtained_score < float(self.total_score) and int(self.report_verbose) < 1:
            print("\n[INFO] set `-v 1` to get diff result.")
            print("For example: `python3 judge/judge.py -v 1`")
            returncode = 1
        return returncode


class ErrorHandler:
    def __init__(self, exit_or_log, **logging_config):
        self.exit_or_log = exit_or_log
        self.student_id = ""
        self.cache_log = ""
        if logging_config == {}:
            logging_config['format'] = '%(asctime)-15s [%(levelname)s] %(message)s'
        logging.basicConfig(**logging_config)

    def set_student_id(self, student_id):
        self.student_id = student_id

    def clear_cache_log(self):
        self.cache_log = ""

    def handle(self, msg="", exit_or_log=None):
        action = self.exit_or_log
        if not exit_or_log == None:
            action = exit_or_log
        if action == 'exit':
            print(self.student_id+" "+msg)
            exit(1)
        elif action == 'log':
            self.cache_log += (str(msg)+str("\n"))
            logging.error(self.student_id+" "+msg)
        else:
            print("Cannot handle `" + action +
                  "`. Check ErrorHandler setting.")
            exit(1)


def get_args():
    """ Init argparser and return the args from cli.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        help="the config file",
        type=str,
        default=os.getcwd()+os.sep+"judge.conf")
    parser.add_argument(
        "-v", "--verbose",
        help="the verbose level",
        type=int,
        default=0)
    parser.add_argument(
        "-i", "--input",
        help="judge only one input with showing diff result",
        type=str,
        default=None)
    parser.add_argument(
        "-o", "--output",
        help="used to save outputs to a given directory without judgement",
        type=str,
        default=None)
    return parser.parse_args()


def judge_all_tests(config, verbose_level, total_score):
    """ Judge all tests for given program.

    If `--input` is set, there is only one input in this judgement.
    """
    judge = LocalJudge(config)
    judge.build()

    report = Report(report_verbose=verbose_level, total_score=total_score)
    for test in judge.tests:
        output_filepath = judge.run(test.input_filepath)
        accept, diff = judge.compare(output_filepath, test.answer_filepath)
        report.table.append(
            {'test': test.test_name, 'accept': accept, 'diff': diff})
    return report.print_report()


def copy_output_to_dir(config, output_dir, delete_temp_output, ans_ext):
    """ Copy output files into given directory without judgement.

    Usually used to create answer files or save the outputs for debugging.
    """
    try:
        # Create the temporary directory for output
        # Suppress the error when the directory already exists
        os.makedirs(output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            ERR_HANDLER.handle(str(e))
    judge = LocalJudge(config)
    judge.build()

    for test in judge.tests:
        output_filepath = judge.run(test.input_filepath, with_timestamp=False)
        copyfile(output_filepath,
                 expand_path(output_dir, get_filename(output_filepath), ans_ext))
        if delete_temp_output == "true":
            os.remove(output_filepath)
    return 0


if __name__ == '__main__':
    args = get_args()
    config = configparser.RawConfigParser()
    config.read(args.config)
    ERR_HANDLER = ErrorHandler(config['Config']['ExitOrLog'])
    returncode = 0

    # Check if the config file is empty or not exist.
    if config.sections() == []:
        print("Failed in config stage. `"+str(args.config)+"` not found.")
        ERR_HANDLER.handle(exit_or_log='exit')

    # Assign specific input for this judgement
    if not args.input == None:
        args.verbose = True
        config['Config']['Inputs'] = create_specific_input(args.input, config)

    # Copy output files into given directory without judgement
    if not args.output == None:
        copy_output_to_dir(config, args.output,
                config['Config']['DeleteTempOutput'],
                config['Config']['AnswerExtension'])
        exit(returncode)

    returncode = judge_all_tests(config, args.verbose, config['Config']['TotalScore'])
    exit(returncode)
