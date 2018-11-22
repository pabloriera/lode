import formulas
from string import Template
import pathlib
import sys

if sys.version_info[0] > 2:

    def clean(string):
        string = string.replace("\u03BB", "lambda")
        return string

else:

    def clean(string):
        """ Removes non-ascii characters from a string """
        string = string.replace(u"\u03BB", "lambda")
        return string.encode("ascii", "replace")


def debug_stdout(*args):
    """ Forces prints to server-side """
    sys.__stdout__.write(" ".join([str(s) for s in args]) + "\n")


def WarningMsg(*text):
    print("Warning: {}".format(" ".join(str(s) for s in text)))


def write_to_file(fn, text):
    try:
        with open(fn, "w") as f:
            f.write(clean(text))
    except IOError:
        print("Unable to write to {}".format(fn))
    return


def template_read_sub_write(filename_in, filename_out, dict_subs):
    with open(filename_in) as fp:
        template = Template(fp.read())

    pathlib.Path(filename_out).parent.mkdir(parents=True, exist_ok=True)

    with open(filename_out, 'w') as fp:
        fp.write(template.safe_substitute(dict_subs))


def parameters_from_eq(eq):
    eq.replace('**', '^')
    eq = '=' + eq
    compiled = formulas.Parser().ast(eq)[1].compile()
    inputs = list(compiled.inputs)
    return inputs
