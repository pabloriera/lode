from sympy.parsing.sympy_parser import parse_expr
from string import Template
import pathlib
import sys
import re
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
    pathlib.Path(filename_out).parent.mkdir(parents=True, exist_ok=True)
    with open(filename_out, 'w') as fp:
        fp.write(template_read_sub(filename_in, dict_subs))


def template_read_sub(filename_in, dict_subs):
    with open(filename_in) as fp:
        template = Template(fp.read())

    return template.safe_substitute(dict_subs)


def parse_equation(eq):
    try:
        expr = parse_expr(eq)
        return expr
    except Exception as e:
        print('Syntax formula error')
        print(e)
        # embed()
        return None


def parse_parameter_formula(formula_string):
    try:
        formula_string = re.sub(r'\.([a-zA-Z]+)', r'_var_\1', formula_string)
        # embed()
        formula_string = re.sub(r'\[-(\d+)\.?(\d+)?\]', r'_del_\1_\2', formula_string)
        expr = parse_expr(formula_string)
        add, expr = expr.as_coeff_Add()
        terms, syms = expr.as_terms()
        external_inputs = {}
        for t in terms:
            if t[0] != 0:
                term_sym = syms[t[1][1].index(1)]
                term_var = str(term_sym)
                node = term_var.split('_')[0]
                if 'var' in term_var:
                    var = re.findall(r'var_([a-zA-Z]+)', term_var)[0]
                else:
                    var = None
                if 'del' in term_var:
                    delay_time = float('.'.join(re.findall(r'del_(\d+)_?(\d+)?', term_var)[0]))
                else:
                    delay_time = 0

                if var is not None:
                    external_inputs[node] = {'mul': t[1][0][0], 'var': var, 'delay_time': delay_time}
                else:
                    external_inputs[str(term_sym.func)] = {'mul': t[1][0][0]}
                    if len(term_sym.args) > 0:
                        external_inputs[str(term_sym.func)].update({'args': term_sym.args, })

        return float(add), external_inputs

    except Exception as e:
        print('Syntax formula error')
        print(e)
        embed()
        return None
