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
import os, sys


def get_filename(path):
    """Get the filename without extension

    input/a.txt -> a
    """
    head, tail = os.path.split(path)
    return os.path.splitext(tail or os.path.basename(head))[0]


def expand_path(dir, filename, extension):
    """Expand a directory and extension for filename

    a -> answer/a.out
    """
    return os.path.abspath(os.path.join(dir, filename + extension))


def create_specific_input(input_name_or_path, config):
    if os.path.isfile(input_name_or_path):
        specific_input = input_name_or_path
    else:
        parent = os.path.split(config["Config"]["Inputs"])[0]
        ext = os.path.splitext(config["Config"]["Inputs"])[1]
        specific_input = parent + os.sep + input_name_or_path + ext
    specific_input = os.path.abspath(specific_input)
    if not os.path.isfile(specific_input):
        sys.stderr.write(specific_input + " not found for specific input.")
        sys.exit(1)
    return specific_input
