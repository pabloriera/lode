import formulas
from string import Template
import pathlib
import sys
from IPython import embed

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


def parse_equation(eq):
    eq.replace('**', '^')
    eq = '=' + eq
    try:
        compiled = formulas.Parser().ast(eq)[1].compile()
        return compiled
    except Exception:
        print('Syntax formula error')
        return None


def parse_linear(eq):
    eq = '=' + eq
    try:
        parts = [p.name for p in formulas.Parser().ast(eq)[0]]
        mul = 1.0
        add = 0

        if '*' in parts:
            imul = parts.index('*')
        else:
            imul = None

        for i, p in enumerate(parts):
            if p != '+' and p != '*' and not p.isdigit():
                connect = p.lower()
            elif p.isdigit():
                if imul is not None:
                    if abs(i - imul) == 1:
                        mul = float(p)
                        break

        if '+' in parts:
            for i, p in enumerate(parts):
                if p.isdigit():
                    if float(p) != mul:
                        add = float(p)

        return connect, mul, add

    except Exception:
        print('Syntax formula error')
        return None
