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
import logging


class ErrorHandler:
    def __init__(self, exit_or_log, **logging_config):
        self.exit_or_log = exit_or_log
        self.database = {}
        if logging_config == {}:
            logging_config["format"] = "%(asctime)-15s [%(levelname)s] %(message)s"
        logging.basicConfig(**logging_config)

    def init_student(self, student_id: str):
        self.database[student_id] = ""

    def get_error(self, student_id):
        if not student_id in self.database.keys():
            return ""
        return self.database[student_id]

    def handle(self, msg="", exit_or_log=None, student_id="", max_len=200):
        action = self.exit_or_log if exit_or_log is None else exit_or_log

        if action == "exit":
            print(student_id + " " + msg)
            sys.exit(1)
        elif action == "log":
            if not student_id in self.database.keys():
                self.init_student(student_id)
            self.database[student_id] += str(msg) + str("\n")
            logging.error(
                student_id + " " + msg[:max_len] if len(msg) > max_len else msg
            )
        else:
            print("Cannot handle `" + action + "`. Check ErrorHandler setting.")
            sys.exit(1)

        if len(self.database[student_id]) > max_len:
            self.database[student_id] = self.database[student_id][:max_len]
