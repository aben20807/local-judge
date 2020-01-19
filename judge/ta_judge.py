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

__version__ = '1.0.0'

import argparse
import configparser
import os
from openpyxl import Workbook
from zipfile import ZipFile
import rarfile
from glob import glob as globbing
import re
from collections import namedtuple
import logging

from judge import LocalJudge

GREEN = '\033[32m'
RED = '\033[31m'
BLUE = '\033[34m'
NC = '\033[0m'


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename='ta_judge.log', filemode='a', format=FORMAT)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--config",
    help="the config file",
    type=str,
    default=os.getcwd()+os.sep+"judge.conf")
parser.add_argument(
    "-t", "--ta-config",
    help="the config file",
    type=str,
    default=os.getcwd()+os.sep+"ta_judge.conf")
parser.add_argument(
    "-s", "--student",
    help="judge only one student",
    type=str,
    default=None)


class TaJudge:
    def __init__(self, ta_config):
        try:
            self._config = ta_config['TaConfig']
            self.students_zip_container = self._config['StudentsZipContainer']
            self.students_pattern = self._config['StudentsPattern']
            self.students_extract_dir = self._config['StudentsExtractDir']
            self.students_zips = globbing(
                self.students_zip_container+os.sep+"*")

            # Parse the students' id and sort them
            self.students = self._parse_students()
            self.students.sort(key=lambda x: x.id)
        except KeyError as e:
            print(RED + "[ERROR] " + NC + str(e) +
                  " field was not found in config file.")
            print("Please check `judge.conf` first.")
            exit(1)
        try:
            # Create the temporary directory for output
            # Suppress the error when the directory already exists
            os.makedirs(self.students_extract_dir)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                print(RED + "[ERROR] " + NC + str(e))
                exit(1)

    def _parse_students(self):
        """ Used to parse student by the zip filename.

        The filename will be split into two parts: student id and the type of zip file (zip or rar).
        """
        Student = namedtuple(
            'Student', ('id', 'zip_type', 'zip_path', 'extract_path'))
        regex = re.compile(self.students_pattern)
        students = []
        for student_zip_path in self.students_zips:
            match = regex.search(student_zip_path)
            students.append(Student(
                match.group(1),
                match.group(3),
                os.path.abspath(student_zip_path),
                os.path.abspath(self.students_extract_dir+os.sep+match.group(1)+'_'+match.group(2))))
        return students

    def extract_student(self, student):
        """ Used to extract students' zip file.
        """
        try:
            if student.zip_type == 'zip':
                z = ZipFile(student.zip_path, 'r')
            elif student.zip_type == 'rar':
                z = rarfile.RarFile(student.zip_path)
            else:
                logging.error("[ERROR] " + student.id +
                              " failed in extract stage with unknown zip type.")
                return
            z.extractall(self.students_extract_dir)
            z.close()
        except Exception as e:
            logging.error("[ERROR] " + student.id +
                          " failed in extract stage." + str(e))


def specific_cases(args_student):
    """ Handle the case that judge only one student.
    """
    # Find the student
    student = [s for s in tj.students if s.id == args_student][0]
    tj.extract_student(student)
    wd = os.getcwd()
    try:
        os.chdir(student.extract_path)
    except FileNotFoundError as e:
        logging.error("[ERROR] " + student.id + str(e))
        exit(1)
    judge.build()
    from judge import Report
    report = Report(report_verbose=True)
    for test in judge.io_map:
        output = judge.run(judge.io_map[test][0])
        accept, diff = judge.compare(output, judge.io_map[test][1])
        report.table.append({'test': test, 'accept': accept, 'diff': diff})
        report.test.append(test)
    report.print_report()
    os.chdir(wd)
    exit(0)

def cd_student_path(student):
    try:
        os.chdir(student.extract_path)
    except FileNotFoundError as e:
        logging.error("[ERROR] " + student.id + str(e))
        return False
    return True

if __name__ == '__main__':
    args = parser.parse_args()
    config = configparser.ConfigParser()
    ta_config = configparser.ConfigParser()
    config.read(args.config)
    ta_config.read(args.ta_config)

    # Check if the config file is empty or not exist.
    if config.sections() == [] or ta_config.sections() == []:
        print(RED + "[ERROR] " + NC + "failed in config stage.")
        raise FileNotFoundError(
            args.config if config.sections() == [] else args.ta_config)

    tj = TaJudge(ta_config)
    judge = LocalJudge(config)

    # Assign specific student for this judgement
    if not args.student == None:
        specific_cases(args.student)

    # Init the table with the title
    wb = Workbook()
    ws = wb.active
    title = list(judge.io_map.keys())
    title.insert(0, "student id")
    ws.append(title)

    for student in tj.students:
        tj.extract_student(student)
        wd = os.getcwd()
        if not cd_student_path(student):
            continue

        judge.build()
        row = []
        row.append(student.id)
        for test in judge.io_map:
            output = judge.run(judge.io_map[test][0])
            accept, diff = judge.compare(output, judge.io_map[test][1])
            row.append(1 if accept else 0)

        ws.append(row)
        # Restore the path
        os.chdir(wd)

    wb.save(ta_config['TaConfig']['ScoreOutput'])
    print("Finished")
