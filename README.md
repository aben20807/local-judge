# Local Judge

[![Python version](https://img.shields.io/badge/python-%3E=_3.6-blue.svg)](https://www.python.org/downloads/)
[![GitHub license](https://img.shields.io/github/license/aben20807/local-judge?color=blue)](LICENSE)
[![GitHub release](https://img.shields.io/github/release/aben20807/local-judge.svg)](https://github.com/aben20807/local-judge/releases)
[![PyPI](https://img.shields.io/pypi/v/local-judge?color=blue&style=flat&logo=pypi)](https://pypi.org/project/local-judge/)
[![Downloads](https://pepy.tech/badge/local-judge)](https://pepy.tech/project/local-judge)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/aben20807/local-judge.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/aben20807/local-judge/context:python)

Given source code, Makefile (or build commands), input files, and answer files then judge the program locally.

## Workflow

```
+-------------------------------------------------------------------------------------+
| # TA (ta_judge.py):                                                                 |
|              +------------------------------[unzip]---------------------------+++++ |
|              | # Student (judge.py):                                          ||||| |
|              | source code ---+                                               ||||| |
|              |                | [build]                                       ||||| |
|              |                v                                               ||||| |
| hidden inp. --> input ---> program ---> output                                ||||| |
|              |              [run]         |                                   ||||| |
|              |                            v                                   ||||| |
| hidden ans. --> answer -------------> [compare] ---> correctness, diff result ||||| |
|              +-----------------------------------------|----------------------+++++ |
|                                                        ||||| [collect]              |
|                                                        vvvvv                        |
|                                                     score table                     |
+-------------------------------------------------------------------------------------+
```

## Screenshot

![screenshot](https://raw.githubusercontent.com/aben20807/local-judge/master/images/screenshot.png)

## Installation

```bash
$ virtualenv -p python3.6 venv
$ source venv/bin/activate
$ pip install local-judge
```

## Features

+ Both
  + Automatically build the source code into executable
  + Automatically run the executable for each input and compare output with answer
  + Customization friendly
  + Able to leverage git diff tool to compare the result with the answer
+ Student (`judge.py`)
  + Without any dependencies but standard build-in python packages
+ TA (`ta_judge.py`)
  + Support different zip type (`.zip`, `.rar`)
  + When error is occurred, not interrupt or exit but just log it 
  + Output to excel table
  + Multiprocessing

## Environment (Recommended)

+ Ubuntu 18.04
+ python 3.6
+ git 2.17.1

## Examples (with DEMO)

+ [student](examples/student/)
+ [TA](examples/ta/)

## Usage (Student)

### Configuration

+ `judge.conf`: be placed in the root of your program
  + `BuildCommand`: how to build the executable
  + `Executable`: the name of the executable
  + `RunCommand`: how to run the executable with input and output
  + `Inputs`: input files (can use wildcard)
  + `TempOutputDir`: the temporary directory to place output files
  + `DiffCommand`: how to find differences between output and answer
  + `DeleteTempOutput`: whether to delete the temporary output after finding the differences (true or false)
  + `AnswerDir`: the directory where contains the answer files corresponding to the input files
  + `AnswerExtension`: the extension of the answer files
  + `ExitOrLog`: exit when any error occurred or just log the error
  + `ScoreDict`: the dictionary for the mapping of correctness and score
  + `TotalScore`: used if the number of tests is more than `ScoreDict`
  + `Timeout`: execution timeout for each test case

## Usage (TA)

### Dependencies

+ `openpyxl`, `rarfile`

### Configuration

+ `ta_judge.config`:
  + First part is `judge.conf`
  + `StudentList`: the execl file which contains student name and id
  + `StudentsZipContainer`: the directory where contains students' submit homeworks
  + `StudentsPattern`: used to match zip files
  + `UpdateStudentPattern`: used for update score of single student
  + `StudentsExtractDir`: the directory where contains extracted homeworks
  + `ScoreOutput`: the output excel file
  + `ExtractAfresh`: true: re-extract zipped file for each judge time; false: use pre-extracted files (under `StudentsExtractDir`) to judge