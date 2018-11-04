import formulas
from string import Template
import pathlib


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
