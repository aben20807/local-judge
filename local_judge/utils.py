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
