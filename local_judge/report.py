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
import sys
from itertools import repeat
from subprocess import check_output, CalledProcessError

GREEN = "\033[32m"
RED = "\033[31m"
NC = "\033[0m"


class Report:
    def __init__(self, report_verbose=0, score_dict=None, total_score=0):
        self.score_dict = score_dict
        self.total_score = total_score
        self.report_verbose = report_verbose
        self.table = []

    def get_score_by_correct_cnt(self, correct_cnt: int):
        return int(self.score_dict[str(correct_cnt)])

    def print_report(self) -> int:
        """Print the report into table view."""
        self.table.sort(key=lambda x: x["test"])
        tests = [x["test"] for x in self.table]

        # Return directly when the test is empty.
        if len(tests) == 0:
            sys.stderr.write(
                "Failed in report stage. "
                + "There was no any result to report. "
                + "Did you set the `Inputs` correctly? "
                + "Please check `judge.conf` first."
            )
            return 1

        # Get the window size of the current terminal.
        columns = 100
        try:
            _, columns = check_output(["stty", "size"]).split()
        except CalledProcessError as e:
            pass  # We cannot get the size of stty during testing.

        test_len = max(len(max(tests, key=len)), len("Sample"))
        doubledash = "".join(list(repeat("=", int(columns))))
        doubledash = doubledash[: test_len + 1] + "+" + doubledash[test_len + 2 :]
        dash = "".join(list(repeat("-", int(columns))))
        dash = dash[: test_len + 1] + "+" + dash[test_len + 2 :]

        print(doubledash)
        print("{:>{width}} | {}".format("Sample", "Accept", width=test_len))
        for row in self.table:
            print(doubledash)
            mark = GREEN + "✔" + NC if row["accept"] else RED + "✘" + NC
            print("{:>{width}} | {}".format(row["test"], mark, width=test_len))
            if not row["accept"] and int(self.report_verbose) > 0:
                print(dash)
                print(row["diff"])
        print(doubledash)

        # The test which ends with "hide" will not be count to calculate the score.
        correct_cnt = [
            row["accept"] for row in self.table if not row["test"].endswith("hide")
        ].count(True)
        valid_test_number = len(
            [test for test in tests if not test.endswith("hide")]
        )  # not to count hide test case
        total_score = 0
        obtained_score = 0
        try:  # try to use score_dict first
            total_score = int(self.score_dict[str(valid_test_number)])
            obtained_score = self.get_score_by_correct_cnt(correct_cnt)
        except KeyError:  # if the number of tests out of range, use total_score
            total_score = self.total_score
            obtained_score = int(correct_cnt / len(tests) * total_score)
        print(
            f"Correct/Total problems:\t{correct_cnt}/{valid_test_number}\n"
            f"Obtained/Total scores:\t{obtained_score}/{total_score}"
        )
        returncode = 0
        if obtained_score < total_score and int(self.report_verbose) < 1:
            print("\n[INFO] set `-v 1` to get diff result.")
            print("For example: `judge -v 1`")
            returncode = 1
        return returncode
