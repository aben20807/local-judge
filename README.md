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
  + Content:
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
  + Example config file:
    ```conf
    [Config]
    BuildCommand = make clean && make
    Executable = scanner
    RunCommand = ./scanner < {input} > {output}
    Inputs = input/*.txt
    TempOutputDir = /tmp/output
    DiffCommand = git diff --no-index --color-words {answer} {output}
    DeleteTempOutput = true
    AnswerDir = answer
    AnswerExtension = .out
    ExitOrLog = exit
    ScoreDict = {"0":"0","1":"30","2":"60","3":"90","4":"100"}
    TotalScore = 100
    Timeout = 5
    ```

### Commands

```text
usage: judge.py [-h] [-c CONFIG] [-v VERBOSE]

optional arguments:
  -h, --help            show this help message and exit

  -c CONFIG, --config CONFIG
                        the config file, default: `judge.conf`

  -v VERBOSE, --verbose VERBOSE
                        the verbose level, default: `0`
                        `0`: suppress the diff results
                        `1`: show the diff results
  -i INPUT, --input INPUT
                        judge only one input with showing diff result
                        path or test name both work
                        for example: `-i xxxx` or `-i ../input/xxxx.txt`
  -o OUTPUT, --output OUTPUT
                        used to save outputs to a given directory without
                        judgement
```

## Usage (TA)

### Dependencies

+ `judge.py`
+ `openpyxl`: `pip3 install openpyxl`
+ `rarfile`: `pip3 install rarfile`

### Configuration

+ `ta_judge.config`
  + Content:
    + First part is `judge.conf`
    + `StudentList`: the execl file which contains student name and id
    + `StudentsZipContainer`: the directory where contains students' submit homeworks
    + `StudentsPattern`: used to match zip files
    + `UpdateStudentPattern`: used for update score of single student
    + `StudentsExtractDir`: the directory where contains extracted homeworks
    + `ScoreOutput`: the output excel file
    + `ExtractAfresh`: true: re-extract zipped file for each judge time; false: use pre-extracted files (under `StudentsExtractDir`) to judge
  + Example config file:
      ```conf
      [Config]
      BuildCommand = make clean && make
      Executable = scanner
      RunCommand = ./scanner < {input} > {output}
      Inputs = input/*.txt
      TempOutputDir = /tmp/output
      DiffCommand = git diff --no-index --color-words {answer} {output}
      DeleteTempOutput = true
      AnswerDir = answer
      AnswerExtension = .out
      ExitOrLog = exit
      ScoreDict = {"0":"0","1":"30","2":"60","3":"90","4":"100"}
      TotalScore = 100
      Timeout = 5

      [TaConfig]
      StudentList = student.xlsx
      StudentsZipContainer = ./zip
      StudentsPattern = ((\w*)_HW1)\.(.*)
      UpdateStudentPattern = Compiler_{student_id}_HW1
      StudentsExtractDir = ./extract
      ScoreOutput = hw1.xlsx
      ExtractAfresh = true
      ```

### Commands

```text
usage: ta_judge.py [-h] [-c CONFIG] [-t TA_CONFIG] [-s STUDENT]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        the config file, default: `judge.conf`
  -t TA_CONFIG, --ta-config TA_CONFIG
                        the config file, default: `ta_judge.conf`
  -s STUDENT, --student STUDENT
                        judge only one student
  -j JOBS, --jobs JOBS  number of jobs for multiprocessing
  -u UPDATE, --update UPDATE
                        update specific student's score by rejudgement
```
