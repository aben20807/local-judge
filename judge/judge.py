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

__version__ = '1.3.0'

import argparse
import configparser
from collections import namedtuple
from itertools import repeat
from glob import glob as globbing
import os
import subprocess
from subprocess import PIPE
import time

GREEN = '\033[32m'
RED = '\033[31m'
BLUE = '\033[34m'
NC = '\033[0m'

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


class LocalJudge:
    def __init__(self, config):
        """ Set the member from the config file.
        """
        try:
            self._config = config['Config']
            self.build_command = self._config['BuildCommand']
            self.executable = self._config['Executable']
            self.temp_output_dir = self._config['TempOutputDir']
            self.diff_command = self._config['DiffCommand']
            self.delete_temp_output = self._config['DeleteTempOutput']
            self._inputs = [os.path.abspath(path) for path in globbing(self._config['Inputs'])]
            self._tests = [get_filename(path) for path in self._inputs]
            self._answers = [expand_path(self._config['AnswerDir'], filename,
                                         self._config['AnswerExtension']) for filename in self._tests]
        except KeyError as e:
            print(RED + "[ERROR] " + NC + str(e) +
                  " field was not found in config file.")
            print("Please check `judge.conf` first.")
            exit(1)
        try:
            # Create the temporary directory for output
            # Suppress the error when the directory already exists
            os.makedirs(self.temp_output_dir)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                print(RED + "[ERROR] " + NC + str(e))
                exit(1)
        # io_map contains corresponding input and answer files
        self.io_map = dict(zip(self._tests, zip(self._inputs, self._answers)))

    def build(self):
        """ Build the executable which needs to be judged.
        """
        process = subprocess.Popen(
            self.build_command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate()
        if process.returncode != 0:
            print(RED + "[ERROR] " + NC + "failed in build stage.")
            print(str(err, encoding='utf8'))
            print("Please check `Makefile` first.")
            exit(1)

    def run(self, input_filepath):
        """ Run the executable with input.

        The output will be temporarily placed in specific location,
        and the path will be returned for the validation.
        """
        output_filepath = os.path.join(self.temp_output_dir, get_filename(
            input_filepath)+"_"+str(int(time.time()))+".out")
        cmd = "".join(["./", self.executable, " < ",
                       input_filepath, " > ", output_filepath])
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate()
        if process.returncode != 0:
            print(RED + "[ERROR] " + NC + "failed in run stage.")
            print(str(err, encoding='utf8'))
            print("Please check `your program` first.")
            exit(1)
        return output_filepath

    def compare(self, output_filepath, answer_filepath):
        """ Verify the differences between output and answer.

        If the files are identical, the accept will be set to True.
        Another return value is the diff result.
        """
        cmd = "".join(
            [self.diff_command, " ", output_filepath, " ", answer_filepath])
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate()
        # If there is difference between two files, the return code is not 0
        if str(err, encoding='utf8').strip() != "":
            print(RED + "[ERROR] " + NC + "failed in compare stage.")
            print(str(err, encoding='utf8'))
            print(
                "There was no any corresponding answer. Did you set the `AnswerDir` correctly?")
            print("Please check `judge.conf` first.")
            exit(1)
        if self.delete_temp_output == "true":
            os.remove(output_filepath)
        accept = process.returncode == 0
        return accept, str(out, encoding='utf8')


class Report:
    def __init__(self, report_verbose):
        self.report_verbose = report_verbose
        self.table = []
        self.test = []

    def print_report(self):
        """ Print the report into table view.
        """
        # Return directly when the test is empty.
        if not self.test:
            print(RED + "[ERROR] " + NC + "failed in report stage.")
            print(
                "There was no any result to report. Did you set the `Inputs` correctly?")
            print("Please check `judge.conf` first.")
            exit(1)

        # Get the window size of the current terminal.
        _, columns = subprocess.check_output(['stty', 'size']).split()

        test_len = max(len(max(self.test, key=len)), len("Sample"))
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
        correct = [row['accept'] for row in self.table].count(True)
        score = int(100*correct/len(self.test))
        print("Total score: " + str(score))
        if score < 100 and int(self.report_verbose) < 1:
            print(BLUE + "\n[INFO]" + NC + " set `-v 1` to get diff result.")
            print("For example: `python3 judge/judge.py -v 1`")


if __name__ == '__main__':
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)

    # Check if the config file is empty or not exist.
    if config.sections() == []:
        print(RED + "[ERROR] " + NC + "failed in config stage.")
        raise FileNotFoundError(args.config)

    # Assign specific input for this judgement
    if not args.input == None:
        if os.path.isfile(args.input):
            config['Config']['Inputs'] = args.input
        else:
            parent = os.path.split(config['Config']['Inputs'])[0]
            ext = os.path.splitext(config['Config']['Inputs'])[1]
            config['Config']['Inputs'] = parent+os.sep+args.input+ext
        args.verbose = True
    judge = LocalJudge(config)
    judge.build()

    report = Report(args.verbose)
    for test in judge.io_map:
        output = judge.run(judge.io_map[test][0])
        accept, diff = judge.compare(output, judge.io_map[test][1])
        report.table.append({'test': test, 'accept': accept, 'diff': diff})
        report.test.append(test)
    report.print_report()
