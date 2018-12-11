from IPython import embed
import re
import subprocess
import os
import pathlib
from shutil import copy2
import shlex

from utils import template_read_sub_write, parameters_from_eq
from directories import sc_extensions_path, home_path, sources_path
from directories import ode_template_filename, sc_def_template_filename


class Ode():

    bus_counter = 10
    output_group = 1001
    gen_group = 1000
    server = None

    @classmethod
    def set_server(cls, server):
        cls.server = server
        print(server)

    @classmethod
    def set_groups(cls, gen, out):
        cls.gen_group = gen
        cls.output_group = out

    def __init__(self, name):
        self.equation = None
        self.parameters = None
        self.name = name
        self.Name = self.name.title()
        self.build_path = '{}/{}'.format(sources_path, self.Name)
        self.ode_source_filename = '{source_path}/{ode_name}/{ode_name}.cpp'.format(
            source_path=sources_path, ode_name=self.Name)
        self.sc_def_filename = '{home}/{sc_extensions_path}/{Ode_name}.scd'.format(
            home=home_path, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

        self.sc_def_filename = '{}/{}.scd'.format(sources_path, self.Name)
        self.output_node = {}


        # self.plugins_destination = '{home}/{sc_extensions_path}/Oderk4/plugins/'.format(
        # home=home_path, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

    def set_equation(self, equation):
        if isinstance(equation, dict):
            self.equation = equation
            self.variables = list(self.equation.keys())
            self.buses = list(range(Ode.bus_counter, Ode.bus_counter + len(self.variables)))
            Ode.bus_counter += len(self.variables)

            inputs = []
            for k, v in self.equation.items():
                inputs += parameters_from_eq(v)

            inputs = set(inputs)
            parameters_ = []
            no_parameters = [ov.upper() for ov in self.variables]
            no_parameters.append('PI')
            for i in inputs:
                if i not in no_parameters:
                    parameters_.append(i.lower())

            parameters_ = sorted(parameters_)
            if self.parameters == parameters_:
                print('Param in eq no change')
            else:
                print('Param in eq change')
                print(self.parameters)
                self.parameters = parameters_
                if 't' in self.parameters:
                    self.parameters.pop(self.parameters.index('t'))
                self.default_parameters = {k: 0 for k in self.parameters}

    def set_default_parameters(self, parameters):
        if isinstance(parameters, dict):
            self.default_parameters = parameters
            self.parameter_values = parameters

    def create_outputs(self, output):
        if isinstance(output, dict):
            for k, v in output.items():
                if k in self.variables:
                    bus = self.buses[self.variables.index(k)]
                    node_ = self.server.nextnodeID()
                    self.output_node[k] = node_
                    self.server.send('/s_new', ['output', node_, 1, self.output_group])
                    self.server.send('/n_set', [node_, 'bus', bus])

    def setup(self):
        if self.equation is not None:
            self.do_source_code()
            self.do_sc_def()
            self.build()

    def do_source_code(self):
        equation_str = []
        for j, (k, eq) in enumerate(self.equation.items()):
            for i, p in enumerate(self.parameters):
                eq = re.sub(r'\b' + p + r'\b', 'param[{}]'.format(i), eq, flags=re.IGNORECASE)
            for i, x in enumerate(self.variables):
                eq = re.sub(r'\b' + x + r'\b', '#[{}]'.format(i), eq, flags=re.IGNORECASE)
            eq = eq.replace('#', 'X')
            eq = 'dX[{}]='.format(j) + eq
            equation_str.append(eq)

        self.equation_str = ';\n    '.join(equation_str) + ';'

        # add more constants
        self.equation_str = self.equation_str.replace('pi', 'PI')
        subs = {'N_EQ': len(self.variables), 'N_PARAMETERS': len(self.parameters), 'EQUATION': self.equation_str}
        template_read_sub_write(ode_template_filename, self.ode_source_filename, subs)

    def do_sc_def(self):
        # ode_arg_list = ', '.join(self.parameters)
        def_arg_list = ', '.join(['{}={}'.format(p, self.default_parameters.get(p, 0.0)) for p in self.parameters])
        ode_arg_list = ', '.join(['DC.ar(1)*{}'.format(p) for p in self.parameters])
        outputs = '\n\t'.join(['OffsetOut.ar({},osc[{}]);'.format(b, i) for i, b in enumerate(self.buses)])
        inputs = ''
        # subs = {'Ode_name': self.Name, 'ode_class_args': ode_class_args,
        # 'ode_arg_list': ode_arg_list, 'ode_n_equations': len(self.equation)}
        # template_read_sub_write(self.sc_class_template_filename, self.sc_class_filename, subs)

        subs = {'Ode_name': self.Name, 'def_arg_list': def_arg_list, 'ode_arg_list': ode_arg_list,
                'inputs': inputs, 'outputs': outputs}
        # template_read_sub_write(self.sc_def_template_filename, self.sc_def_filename, subs)
        template_read_sub_write(sc_def_template_filename, self.sc_def_filename, subs)

    def build(self):
        os.chdir(self.build_path)
        command1 = 'g++ -fpic -c {Ode_name}.cpp -o {Ode_name}.o -Ofast'.format(Ode_name=self.Name)
        command2 = 'gcc -fpic -shared {Ode_name}.o -lm -o lib{Ode_name}.so -Ofast'.format(Ode_name=self.Name)

        subprocess.call(shlex.split(command1))
        subprocess.call(shlex.split(command2))
        # pathlib.Path(self.plugins_destination).mkdir(parents=True, exist_ok=True)
        # copy2('{path}/lib{Ode_name}.so'.format(path=os.getcwd(), Ode_name=self.Name), '{}/lib{}.so'.format(self.plugins_destination, self.Name))
        copy2('{path}/lib{Ode_name}.so'.format(path=os.getcwd(), Ode_name=self.Name), '{path}/..'.format(path=os.getcwd()))

    def load_synth(self):
        self.server.loadSynthDef(self.sc_def_filename)

    def create_synth(self):
        self.synth_node = self.server.nextnodeID()
        self.server.send('/s_new', [self.Name, self.synth_node, 0, self.gen_group])

    def update_outputs(self, output):
        if isinstance(output, dict):
            self.output = output
            for k, v in self.output.items():
                if k in self.variables:
                    if k not in self.output_node:
                        self.create_outputs({k: v})
                    if 'gain' in v:
                        self.server.send('/n_set', [self.output_node[k], 'amp', v['gain']])
                    if 'pan' in v:
                        self.server.send('/n_set', [self.output_node[k], 'pan', v['pan']])

    def update_parameters_value(self, parameters_values):
        if isinstance(parameters_values, dict):
            self.parameters_values = parameters_values
            for k, v in parameters_values.items():
                self.server.send('/n_set', [self.synth_node, k, v])
