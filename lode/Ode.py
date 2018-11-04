from IPython import embed
import re
import subprocess
import os
import pathlib
from shutil import copy2
import shlex

from utils import template_read_sub_write, parameters_from_eq
from directories import sc_extensions_path, home_path, module_directory


class Ode():

    def __init__(self, config):

        self.config = config
        self.name = list(config.keys())[0]
        self.Name = self.name.title()

        # Move all this to directories
        self.sources_path = '{}/odes'.format(module_directory)
        self.ode_template_filename = '{}/templates/ode_equation_template.cpp'.format(module_directory)
        self.sc_class_template_filename = '{}/templates/sc_class.sc'.format(module_directory)
        self.sc_def_template_filename = '{}/templates/sc_def.sc'.format(module_directory)

        self.build_path = '{}/{}'.format(self.sources_path, self.Name)
        self.ode_source_filename = '{source_path}/{ode_name}/{ode_name}.cpp'.format(
            source_path=self.sources_path, ode_name=self.Name)

        self.sc_class_filename = '{home}/{sc_extensions_path}/{Ode_name}/classes/{Ode_name}.sc'.format(
            home=home_path, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)
        self.sc_def_filename = '{home}/{sc_extensions_path}/{Ode_name}.scd'.format(
            home=home_path, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

        self.plugins_destination = '{home}/{sc_extensions_path}/Oderk4/plugins/'.format(
            home=home_path, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

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
        # print(self.parameters)
        if 'parameters' in config[self.name]:
            self.parameters_values = config[self.name]['parameters']

    def setup(self):
        print(self.Name, 'setup')
        self.do_source_code()
        self.do_sc_ndef()
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
        subs = {'N_EQ': len(self.variables), 'N_PARAMETERS': len(self.parameters), 'EQUATION': self.equation_str}
        template_read_sub_write(self.ode_template_filename, self.ode_source_filename, subs)

    def do_sc_ndef(self):
        ode_arg_list = ', '.join(self.parameters)
        # ode_class_args = ', '.join(['{} = DC.ar({})'.format(p, self.parameters_values[p]) for p in self.parameters])
        sc_vars = '\n    '.join(['var {p} = \\{p}.ar({v});'.format(p=p, v=self.parameters_values[p]) for p in self.parameters])
        output = ','.join(['osc[{}]'.format(i) for i in range(len(self.variables))])
        # subs = {'Ode_name': self.Name, 'ode_class_args': ode_class_args,
        # 'ode_arg_list': ode_arg_list, 'ode_n_equations': len(self.equation)}
        # template_read_sub_write(self.sc_class_template_filename, self.sc_class_filename, subs)

        subs = {'Ode_name': self.Name, 'ode_arg_list': ode_arg_list,
                'vars': sc_vars, 'output': output}
        template_read_sub_write(self.sc_def_template_filename, self.sc_def_filename, subs)
        template_read_sub_write(self.sc_def_template_filename, '{}/{}.scd'.format(self.sources_path, self.Name), subs)

    def build(self):
        os.chdir(self.build_path)
        command1 = 'g++ -c {Ode_name}.cpp -o {Ode_name}.o -Ofast'.format(Ode_name=self.Name)
        command2 = 'gcc -fpic -shared {Ode_name}.o -o lib{Ode_name}.so -Ofast'.format(Ode_name=self.Name)

        subprocess.call(shlex.split(command1))
        subprocess.call(shlex.split(command2))
        pathlib.Path(self.plugins_destination).mkdir(parents=True, exist_ok=True)
        # copy2('{path}/lib{Ode_name}.so'.format(path=os.getcwd(), Ode_name=self.Name), '{}/lib{}.so'.format(self.plugins_destination, self.Name))
        copy2('{path}/lib{Ode_name}.so'.format(path=os.getcwd(), Ode_name=self.Name), '{path}/..'.format(path=os.getcwd()))
