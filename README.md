# Local Judge

[![PyPI](https://img.shields.io/pypi/v/local-judge?color=blue&style=flat&logo=pypi)](https://pypi.org/project/local-judge/)
[![Downloads](https://pepy.tech/badge/local-judge)](https://pepy.tech/project/local-judge)
[![Python version](https://img.shields.io/badge/python-%3E=_3.6-blue.svg)](https://www.python.org/downloads/)
[![GitHub license](https://img.shields.io/github/license/aben20807/local-judge?color=blue)](LICENSE)
[![Coding style](https://img.shields.io/badge/code%20style-black-1183C3.svg)](https://github.com/psf/black)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/aben20807/local-judge.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/aben20807/local-judge/context:python)

Given source code, Makefile (or build commands), input files, and answer files then judge the program locally.

> NOTE: this package is not an "online judge" (UVa, LeetCode, etc.) that allows you to solve some algorithmic problems but a tool that can judge (or correct) the students' compiler assignments (included but not limited to) by themselves and by the teaching assistants. You can still use this package to help simulate "online judge", which is not the goal of this work.

## Workflow

![Workflow](https://raw.githubusercontent.com/aben20807/local-judge/master/images/workflow.png)<!--https://app.diagrams.net/#G1sHhxLAY34FpYWBGIHJirRF19tevzqwi0-->

## Screenshot

![screenshot](https://raw.githubusercontent.com/aben20807/local-judge/master/images/screenshot.png)

## Installation

+ For global usage:

  ```bash
  $ pip install local-judge
  ```

+ With virtualenv:

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
+ Student (`judge`)
  + Without any dependencies but standard build-in python packages
+ TA (`ta_judge`)
  + Two dependencies packages: `openpyxl`, `rarfile`
  + Support different zip type (`.zip`, `.rar`)
  + When error is occurred, not interrupt or exit but just log it 
  + Output to excel table
  + Multiprocessing

## Environment (Recommended)

+ Ubuntu 18.04
+ python 3.6
+ git 2.17.1 (Our default diff tool for comparing between output and answer is git. Please make sure that you have installed it.)

## Usage Examples

+ [judge](https://github.com/aben20807/local-judge/tree/master/examples/judge/)
+ [ta_judge](https://github.com/aben20807/local-judge/tree/master/examples/ta_judge/)

## Documentation of Configuration
### judge

+ `judge.conf`: be placed in the root of your program [[example]](https://github.com/aben20807/local-judge/tree/master/examples/judge/wrong/judge.conf)
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

### ta_judge

+ `ta_judge.config`: [[example]](https://github.com/aben20807/local-judge/tree/master/examples/ta_judge/ta_judge.conf)
  + First part is `judge.conf`
  + `StudentList`: the execl file which contains student name and id
  + `StudentsZipContainer`: the directory where contains students' submit homeworks
  + `StudentsPattern`: used to match zip files
  + `UpdateStudentPattern`: used for update score of single student
  + `StudentsExtractDir`: the directory where contains extracted homeworks
  + `ScoreOutput`: the output excel file
  + `ExtractAfresh`: true: re-extract zipped file for each judge time; false: use pre-extracted files (under `StudentsExtractDir`) to judge

## Contributing

Please make sure that you have installed [pre-commit](https://pre-commit.com/) for linting the code with the [black](https://github.com/psf/black) style.

## License

MIT