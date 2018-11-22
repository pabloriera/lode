from __future__ import absolute_import, division, print_function

import sys
import re
from traceback import format_exc as error_stack
from types import CodeType, FunctionType

try:

    from types import TypeType

except ImportError:

    TypeType = type
    
from ..Settings import *


class CodeString:
    def __init__(self, raw):
        self.raw = raw
        self.iter = -1
        self.lines = [s + "\n" for s in self.raw.split("\n")] + ['']
    def readline(self):
        self.iter += 1
        return self.lines[self.iter]
    def __str__(self):
        return self.raw

if sys.version_info[0] > 2:

    def clean(string):
        string = string.replace("\u03BB", "lambda")
        return string

else:

    def clean(string):
        """ Removes non-ascii characters from a string """
        string = string.replace(u"\u03BB", "lambda")
        return string.encode("ascii", "replace")
        

def stdout(code):
    """ Shell-based output """
    console_text = code.strip().split("\n")
    return ">>> {}".format("\n... ".join(console_text))

def debug_stdout(*args):
    """ Forces prints to server-side """
    sys.__stdout__.write(" ".join([str(s) for s in args]) + "\n")

def WarningMsg(*text):
    print("Warning: {}".format( " ".join(str(s) for s in text) ))

def write_to_file(fn, text):
    try:
        with open(fn, "w") as f:
            f.write(clean(text))
    except IOError:
        print("Unable to write to {}".format(fn))
    return

# These functions return information about an imported module

# Should use insepct module

def classes(module):
    """ Returns a list of class names defined in module """
    return [name for name, data in vars(module).items() if type(data) == TypeType]

def instances(module, cls):
    """ Returns a list of instances of cls from module """
    return [name for name, data in vars(module).items() if isinstance(data, cls)]

def functions(module):
    """ Returns a list of function names defined in module """
    return [name for name, data in vars(module).items() if type(data) == FunctionType]
