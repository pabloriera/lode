import yaml
from IPython import embed
import formulas
import re
import subprocess
import os
from string import Template
import pathlib
from shutil import copy2


sc_extensions_path = '.local/share/SuperCollider/Extensions'
home = pathlib.Path.home()


def template_read_sub(filename_in, filename_out, dict_subs):

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


current_directory = os.getcwd()


class Ode():

    def __init__(self, config):

        self.name = list(config.keys())[0]
        self.Name = self.name.title()

        self.sources_path = '{}/ode_sources'.format(current_directory)
        self.ode_template_filename = '{}/templates/oderk4_template.cpp'.format(current_directory)
        self.cmake_template_filename = '{}/templates/CMakeLists.txt'.format(current_directory)
        self.sc_class_template_filename = '{}/templates/sc_class.sc'.format(current_directory)
        self.sc_def_template_filename = '{}/templates/sc_def.sc'.format(current_directory)

        self.build_path = '{}/{}'.format(self.sources_path, self.Name)

        self.cmake_filename = '{source_path}/{ode_name}/CMakeLists.txt'.format(
            source_path=self.sources_path, ode_name=self.Name)

        self.ode_source_filename = '{source_path}/{ode_name}/{ode_name}.cpp'.format(
            source_path=self.sources_path, ode_name=self.Name)

        self.sc_class_filename = '{home}/{sc_extensions_path}/{Ode_name}/classes/{Ode_name}.sc'.format(
            home=home, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)
        self.sc_def_filename = '{home}/{sc_extensions_path}/{Ode_name}.scd'.format(
            home=home, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

        self.plugins_destination = '{home}/{sc_extensions_path}/{Ode_name}/plugins/'.format(
            home=home, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

        self.equation = config[self.name]['equation']
        self.variables = list(self.equation.keys())

        inputs = []
        for k, v in self.equation.items():
            inputs += parameters_from_eq(v)

        inputs = set(inputs)
        self.parameters = []
        no_parameters = [ov.upper() for ov in self.variables]
        no_parameters.append('PI')
        for i in inputs:
            if i not in no_parameters:
                self.parameters.append(i.lower())

        self.parameters = sorted(self.parameters)

        if 'parameters' in config[self.name]:
            self.parameters_values = config[self.name]['parameters']

        self.setup()

    def setup(self):
        self.do_source_code()
        self.do_sc_class()
        self.do_cmake()
        self.build()

    def do_source_code(self):
        equation_str = []
        for j, (k, eq) in enumerate(self.equation.items()):
            for i, p in enumerate(self.parameters):
                eq = re.sub(p, 'param[{}]'.format(i), eq, flags=re.IGNORECASE)
            for i, x in enumerate(self.variables):
                eq = re.sub(x, '#[{}]'.format(i), eq, flags=re.IGNORECASE)
            eq = eq.replace('#', 'X')
            eq = 'dX[{}]='.format(j) + eq
            equation_str.append(eq)

        self.equation_str = ';\n    '.join(equation_str) + ';'

        # add more constants
        self.equation_str = self.equation_str.replace('pi', 'PI')
        subs = {'Ode_name': self.Name, 'N_EQ': len(self.variables), 'N_PARAMETERS': len(self.parameters), 'EQUATION': self.equation_str}
        template_read_sub(self.ode_template_filename, self.ode_source_filename, subs)

    def do_sc_class(self):
        ode_arg_list = ', '.join(self.parameters)
        ode_class_args = ', '.join(['{} = DC.ar({})'.format(p, self.parameters_values[p]) for p in self.parameters])
        sc_vars = '\n    '.join(['var {p} = \\{p}.ar({v});'.format(p=p, v=self.parameters_values[p]) for p in self.parameters])

        subs = {'Ode_name': self.Name, 'ode_class_args': ode_class_args,
                'ode_arg_list': ode_arg_list, 'ode_n_equations': len(self.equation)}
        template_read_sub(self.sc_class_template_filename, self.sc_class_filename, subs)

        subs = {'Ode_name': self.Name, 'ode_arg_list': ode_arg_list,
                'vars': sc_vars}
        template_read_sub(self.sc_def_template_filename, self.sc_def_filename, subs)

    def do_cmake(self):
        subs = {'ODE_NAME': self.Name}
        template_read_sub(self.cmake_template_filename, self.cmake_filename, subs)

    def build(self):
        os.chdir(self.build_path)
        subprocess.call(['cmake', '.'])
        subprocess.call(['make'])
        pathlib.Path(self.plugins_destination).mkdir(parents=True, exist_ok=True)
        copy2('{path}/{Ode_name}.so'.format(path=os.getcwd(), Ode_name=self.Name), '{}/{}.so'.format(self.plugins_destination, self.Name))


def parse(filename):
    with open(filename, 'r') as fp:
        ode_config = yaml.load(fp)

    odes = []
    for k, v in ode_config.items():
        odes.append(Ode({k: ode_config[k]}))


if __name__ == '__main__':
    parse('odes.yaml')
