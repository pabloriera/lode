from sympy.parsing.sympy_parser import parse_expr
from sympy import sympify
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
        embed()
        return None


def parse_parameter_formula(formula_string):
    try:
        formula_string = re.sub(r'\.([a-zA-Z]+)', r'_var_\1', formula_string)
        expr = parse_expr(formula_string)
        add, expr = expr.as_coeff_Add()
        terms, syms = expr.as_terms()
        external_inputs = {}
        for t in terms:
            if t[0] != 0:
                d = {'mul': t[1][0][0]}

                if sum(t[1][1]) == 2:
                    k = [s for i, s in enumerate([syms[i] for i, v in enumerate(t[1][1]) if v == 1]) if 'midicc' in str(s.func)][0]
                    term_sym = t[0].replace(k, 1)
                    d['midi'] = {'mul': k}
                else:
                    term_sym = syms[t[1][1].index(1)]

                term_var = str(term_sym)
                func = str(term_sym.func)

                if func == 'midicc':
                    v = sympify('value(x)')
                    term_sym = v.replace(v.args[0], term_sym)
                    func = str(term_sym.func)

                if len(term_sym.args) > 0:
                    args = {}
                    midi = {}
                    for i, arg in enumerate(term_sym.args):
                        if 'midicc' in str(arg):
                            midi['arg{}'.format(i + 1)] = arg
                        else:
                            args['arg{}'.format(i + 1)] = arg

                    d['args'] = args
                    if 'midi' in d:
                        d['midi'].update(midi)
                    else:
                        d['midi'] = midi

                if 'var' in term_var:
                    var = re.findall(r'var_([a-zA-Z]+)', term_var)[0]
                    d.update({'var': var})
                    node = term_var.split('_')[0]
                    external_inputs[node] = d
                else:
                    external_inputs[func] = d

        return float(add), external_inputs

    except Exception as e:
        print('Syntax formula error')
        print(e)
        embed()
        return None
