# Local Judge

Given source code, Makefile (or build commands), input files, and answer files then judge the program locally.

```
source code --------+
                    | [build]
                    v
[run] input ---> program ---> output
                                |
                                v
answer -------------------> [compare] ---> correctness, diff result
```

## Features

+ Automatically build the source code into executable
+ Automatically run the executable for each input and compare output with answer
+ Customization friendly
+ Without any dependencies but standard build-in python packages

## Environment (Recommended)

+ Ubuntu 18.04
+ python 3.6

## Usage (Student)

### Configuration

+ `judge.conf`: be placed in the root of your program
  + Content:
    + `BuildCommand`: how to build the executable
    + `Executable`: the name of the executable
    + `Inputs`: input files (can use wildcard)
    + `TempOutputDir`: the temporary directory to place output files
    + `DiffCommand`: how to find differences between output and answer
    + `DeleteTempOutput`: whether to delete the temporary output after finding the differences (true or false)
    + `AnswerDir`: the directory where contains the answer files corresponding to the input files
    + `AnswerExtension`: the extension of the answer files
  + Example config file:
    ```conf
    [Config]
    BuildCommand = make clean && make
    Executable = scanner
    Inputs = input/*.txt
    TempOutputDir = /tmp/output
    DiffCommand = git diff --no-index --color-words
    DeleteTempOutput = true
    AnswerDir = answer
    AnswerExtension = .out
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
```

### Examples

```bash
$ cd examples/wrong/
$ python3 ../../judge/judge.py 
=======+========================================================================
Sample | Accept
=======+========================================================================
  xxxx | ✘
=======+========================================================================
    gg | ✔
=======+========================================================================
     a | ✔
=======+========================================================================
     b | ✔
=======+========================================================================
Total score: 75

[INFO] set `-v 1` to get diff result.
For example: `python3 judge/judge.py -v 1`



$ python3 ../../judge/judge.py -v 1
=======+========================================================================
Sample | Accept
=======+========================================================================
  xxxx | ✘
-------+------------------------------------------------------------------------
diff --git a/tmp/output/xxxx_1579351349.out b/../answer/xxxx.out
index 4f6ff86..3a2e3f4 100644
--- a/tmp/output/xxxx_1579351349.out
+++ b/../answer/xxxx.out
@@ -1 +1 @@
4294967295-1

=======+========================================================================
    gg | ✔
=======+========================================================================
     a | ✔
=======+========================================================================
     b | ✔
=======+========================================================================
Total score: 75



$ python3 ../../judge/judge.py -i xxxx
=======+========================================================================
Sample | Accept
=======+========================================================================
  xxxx | ✘
-------+------------------------------------------------------------------------
diff --git a/tmp/output/xxxx_1579357598.out b/../answer/xxxx.out
index 4f6ff86..3a2e3f4 100644
--- a/tmp/output/xxxx_1579357598.out
+++ b/../answer/xxxx.out
@@ -1 +1 @@
4294967295-1

=======+========================================================================
Total score: 0
```

## Usage (TA)

### Configuration

+ `judge.conf`: (Same as student)
+ `ta_judge.config`
  + Content:
    + `StudentsZipContainer`: the directory where contains students' submit homeworks
    + `StudentsPattern`: used to match zip files
    + `StudentsExtractDir`: the directory where contains extracted homeworks
    + `ScoreOutput`: the output excel file
  + Example config file:
      ```conf
      [TaConfig]
      StudentsZipContainer = ./zip
      StudentsPattern = (\w*)_(HW1)\.(.*)
      StudentsExtractDir = ./extract
      ScoreOutput = hw1.xlsx
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
```

### File architecture

```text
.
├── judge.conf
├── judge_resources/
│   ├── answer/
│   │   ├── hide1.out
│   │   └── hide2.out
│   └── input
│       ├── hide1.txt
│       └── hide2.txt
├── ta_judge.conf
└── zip/
    ├── F12345678_HW1.zip
    ├── OU2345678_HW1.rar
    └── OU2345999_HW1.zip
```