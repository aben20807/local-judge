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

from .version import __version__

import sys

if sys.version_info < (3,):
    raise ImportError(
        "You are running local-judge {} on Python 2\n".format(__version__)
        + "Please use Python 3"
    )

import re
import time
from subprocess import PIPE, Popen, TimeoutExpired
import os
from glob import glob as globbing
from collections import namedtuple
import configparser
import argparse
import errno
from shutil import copyfile, copymode
import signal
import json

from . import utils
from .error_handler import ErrorHandler
from .report import Report


Test = namedtuple("Test", ("test_name", "input_filepath", "answer_filepath"))


class LocalJudge:
    def __init__(self, config, error_handler: ErrorHandler):
        """Set the member from the config file."""
        self.error_handler = error_handler
        self._config = config
        try:
            self.build_command = self._config["BuildCommand"]
            self.executable = self._config["Executable"]
            self.run_command = self._config["RunCommand"]
            self.temp_output_dir = self._config["TempOutputDir"]
            self.diff_command = self._config["DiffCommand"]
            self.delete_temp_output = self._config["DeleteTempOutput"]
            self._ans_dir = self._config["AnswerDir"]
            self._ans_ext = self._config["AnswerExtension"]
            self.score_dict = self._config["ScoreDict"]
            self.timeout = self._config["Timeout"]
            # tests contains corresponding input and answer path
            self.tests = self.inputs_to_tests(self._config["Inputs"])
        except KeyError as e:
            self.error_handler.handle(
                str(e)
                + " field was not found in config file. "
                + "Please check `judge.conf` first.",
                exit_or_log="exit",
            )
        try:
            # Create the temporary directory for output
            # Suppress the error when the directory already exists
            os.makedirs(self.temp_output_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                self.error_handler.handle(str(e))

    def inputs_to_tests(self, inputs):
        inputs_path = [os.path.abspath(path) for path in globbing(inputs)]

        ret = [
            Test(
                utils.get_filename(path),
                path,
                utils.expand_path(
                    self._ans_dir, utils.get_filename(path), self._ans_ext
                ),
            )
            for path in inputs_path
        ]
        ret.sort(key=lambda t: t.test_name)
        return ret

    def build(self, student_id="local", cwd="./"):
        """Build the executable which needs to be judged."""
        err = ""
        process = Popen(
            self.build_command,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            executable="bash",
            cwd=cwd,
            start_new_session=True,
        )
        try:
            _, err = process.communicate(timeout=float(self.timeout))
        except TimeoutExpired:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            # Ref: https://stackoverflow.com/a/44705997
            self.error_handler.handle(
                f"TLE at build stage; kill `{self.build_command}`",
                student_id=student_id,
            )
        except KeyboardInterrupt:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            raise KeyboardInterrupt from None
        if process.returncode != 0:
            self.error_handler.handle(
                "Failed in build stage. Error message:\n\n"
                + str(err, encoding="utf8")
                + "\n"
                + "Please check `Makefile`, your file architecture, or your program.",
                student_id=student_id,
            )
        if not os.path.isfile(cwd + self.executable):
            self.error_handler.handle(
                "Failed in build stage. "
                + "executable `"
                + self.executable
                + "` not found."
                + "\n"
                + "Please check `Makefile` first.",
                student_id=student_id,
            )

    def run(self, input_filepath, student_id="local", with_timestamp=True, cwd="./"):
        """Run the executable with input.

        The output will be temporarily placed in specific location,
        and the path will be returned for the validation.
        """
        if not os.path.isfile(cwd + self.executable):
            return 1, "no_executable_to_run"
        output_filepath = os.path.join(
            self.temp_output_dir, utils.get_filename(input_filepath)
        )
        if with_timestamp:
            output_filepath += student_id + "_" + str(int(time.time()))
        output_filepath += self._ans_ext
        cmd = self.run_command
        cmd = re.sub(r"{input}", input_filepath, cmd)
        cmd = re.sub(r"{output}", output_filepath, cmd)
        process = Popen(
            cmd,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            executable="bash",
            cwd=cwd,
            start_new_session=True,
        )
        try:
            _, err = process.communicate(timeout=float(self.timeout))
        except TimeoutExpired:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            # Ref: https://stackoverflow.com/a/44705997
            self.error_handler.handle(
                f"TLE at {utils.get_filename(input_filepath)}; kill `{cmd}`",
                student_id=student_id,
            )
            process.returncode = 124
            return process.returncode, output_filepath
        except KeyboardInterrupt:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            raise KeyboardInterrupt from None
        if process.returncode != 0:
            self.error_handler.handle(
                "Failed in run stage. Error message:\n\n"
                + str(err, encoding="utf8")
                + "\n"
                + "Please check `your program` first.",
                student_id=student_id,
            )
        return process.returncode, output_filepath

    def compare(
        self,
        output_filepath,
        answer_filepath,
        run_returncode,
        student_id="local",
        cwd="./",
    ):
        """Verify the differences between output and answer.

        If the files are identical, the accept will be set to True.
        Another return value is the diff result.
        """
        if run_returncode != 0:
            return False, ""
        if output_filepath == "no_executable_to_run":
            return False, output_filepath
        if not os.path.isfile(output_filepath):
            self.error_handler.handle(
                "There was no any output from your program to compare with `"
                + answer_filepath
                + "`. Please check `your program` first.",
                student_id=student_id,
            )
            return False, "no_output_file"
        if not os.path.isfile(answer_filepath):
            self.error_handler.handle(
                "There was no any corresponding answer `"
                + answer_filepath
                + "`. Did you set the `AnswerDir` correctly? "
                + "Please check `judge.conf` first.",
                student_id=student_id,
            )
            return False, "no_answer_file"
        # Sync the file mode
        copymode(answer_filepath, output_filepath)
        cmd = re.sub(r"{output}", output_filepath, self.diff_command)
        cmd = re.sub(r"{answer}", answer_filepath, cmd)
        process = Popen(
            cmd,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            executable="bash",
            cwd=cwd,
        )
        try:
            out, err = process.communicate()
        except KeyboardInterrupt:
            process.kill()
            raise KeyboardInterrupt from None
        # If there is difference between two files, the return code is not 0
        if str(err, encoding="utf8").strip() != "":
            self.error_handler.handle(
                "Failed in compare stage. Error message:\n\n"
                + str(err, encoding="utf8"),
                student_id=student_id,
            )
        if self.delete_temp_output == "true":
            os.remove(output_filepath)
        accept = process.returncode == 0
        return accept, str(out, encoding="utf8", errors="ignore")


def get_args():
    """Init argparser and return the args from cli."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="the config file",
        type=str,
        default=os.getcwd() + os.sep + "judge.conf",
    )
    parser.add_argument(
        "-v", "--verbose", help="the verbose level", type=int, default=0
    )
    parser.add_argument(
        "-i",
        "--input",
        help="judge only one input with showing diff result",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="used to save outputs to a given directory without judgement",
        type=str,
        default=None,
    )
    return parser.parse_args()


def judge_all_tests(judge: LocalJudge, verbose_level, score_dict, total_score):
    """Judge all tests for given program.

    If `--input` is set, there is only one input in this judgement.
    """

    judge.build()

    report = Report(
        report_verbose=verbose_level, score_dict=score_dict, total_score=total_score
    )
    for test in judge.tests:
        returncode, output_filepath = judge.run(test.input_filepath)
        accept, diff = judge.compare(output_filepath, test.answer_filepath, returncode)
        report.table.append({"test": test.test_name, "accept": accept, "diff": diff})
    return report.print_report()


def copy_output_to_dir(judge: LocalJudge, output_dir, delete_temp_output, ans_ext):
    """Copy output files into given directory without judgement.

    Usually used to create answer files or save the outputs for debugging.
    """
    try:
        # Create the temporary directory for output
        # Suppress the error when the directory already exists
        os.makedirs(output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            judge.error_handler.handle(
                str(e),
                exit_or_log="exit",
            )
    judge.build()

    for test in judge.tests:
        _, output_filepath = judge.run(test.input_filepath, with_timestamp=False)
        copyfile(
            output_filepath,
            utils.expand_path(output_dir, utils.get_filename(output_filepath), ans_ext),
        )
        if delete_temp_output == "true":
            os.remove(output_filepath)


def main() -> int:
    print(f"local-judge: v{__version__}")
    args = get_args()
    if not os.path.isfile(args.config):
        print(f"Config file `{args.config}` not found.")
        return 1

    config = configparser.RawConfigParser()
    config.read(args.config)

    judge = LocalJudge(config["Config"], ErrorHandler(config["Config"]["ExitOrLog"]))
    returncode = 0

    # Check if the config file is empty or not exist.
    if config.sections() == []:
        judge.error_handler.handle(
            f"Failed in config stage. `{str(args.config)}` not found.",
            exit_or_log="exit",
        )

    # Assign specific input for this judgement
    if not args.input is None:
        args.verbose = True
        judge.tests = judge.inputs_to_tests(
            utils.create_specific_input(args.input, config)
        )

    # Copy output files into given directory without judgement
    if not args.output is None:
        copy_output_to_dir(
            judge,
            args.output,
            config["Config"]["DeleteTempOutput"],
            config["Config"]["AnswerExtension"],
        )

    score_dict = json.loads(config["Config"]["ScoreDict"])
    # total_score will be used when the number of tests out of score_dict
    total_score = json.loads(config["Config"]["TotalScore"])
    returncode = judge_all_tests(judge, args.verbose, score_dict, total_score)
    return returncode


if __name__ == "__main__":
    returncode = main()
    sys.exit(returncode)
