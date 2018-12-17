from IPython import embed
import re
import subprocess
import os
from shutil import copy2
import shlex

from utils import template_read_sub_write, parse_equation, parse_linear
from directories import sc_extensions_path, home_path, sources_path
from directories import ode_template_filename, sc_def_template_filename
from time import sleep

sleep_time = 0.01


class SynthDef():

    connect_group = None
    param_group = None
    gen_group = None
    output_group = None
    server = None

    @classmethod
    def set_server(cls, server):
        cls.server = server
        print(server)

    @classmethod
    def set_groups(cls, conn, param, gen, out):
        cls.connect_group = conn
        cls.param_group = param
        cls.gen_group = gen
        cls.output_group = out

    def __init__(self):
        self.node = None
        pass

    def new(self, name, group, args=[], action=0):
        if self.node is None:
            self.node = self.server.nextnodeID()
            self.server.send('/s_new', [name, self.node, action, group] + args)

    def set(self, args):
        if self.node is not None:
            self.server.send('/n_set', [self.node] + args)

    def free(self):
        if self.node is not None:
            self.server.send('/n_free', [self.node])


class Output(SynthDef):
    def __init__(self, bus):
        super().__init__()
        self.new('output', self.output_group, ['bus', bus], action=1)


class Connect(SynthDef):
    def __init__(self, from_, to, mul=1, add=0):
        super().__init__()
        self.new('connect', self.connect_group, ['from', from_, 'to', to, 'mul', mul, 'add', add], action=1)


class Parameter(SynthDef):
    def __init__(self, bus):
        super().__init__()
        self.new('param', self.param_group, ['bus', bus], action=1)
        self.bus = bus


class Ode(SynthDef):
    output_bus_counter = 10
    input_bus_counter = 40

    def __init__(self, name):
        super().__init__()
        self.equation = None
        self.variables = []
        self.equation_parameters = []
        self.equation_inputs = []
        self.name = name
        self.Name = self.name.title()
        self.build_path = '{}/{}'.format(sources_path, self.Name)
        self.ode_source_filename = '{source_path}/{ode_name}/{ode_name}.cpp'.format(
            source_path=sources_path, ode_name=self.Name)
        self.sc_def_filename = '{home}/{sc_extensions_path}/{Ode_name}.scd'.format(
            home=home_path, sc_extensions_path=sc_extensions_path, Ode_name=self.Name)

        self.sc_def_filename = '{}/{}.scd'.format(sources_path, self.Name)
        self.outputs = {}
        self.output_dict = {}
        self.parameters_dict = {}
        self.parameters = {}
        self.first_time = True

    def setup(self, config):
        self.set_equation(config['equation'])
        # sleep(sleep_time)
        self.create_equation_parameters()
        # sleep(sleep_time)
        values, connect = self.parse_parameters(config['parameters'])
        self.update_parameters_values(values)
        # sleep(sleep_time)
        self.subsitute_and_build()
        # sleep(sleep_time)
        self.load_synth()
        sleep(sleep_time)
        self.create_synth()
        # sleep(sleep_time)
        self.create_outputs(config['output'])
        # sleep(sleep_time)
        self.update_outputs(config['output'])
        return connect

    def update(self, config):
        if 'equation' in config:
            if config['equation'] == self.equation:
                print(self.Name, 'Eq no change')
            else:
                print(self.Name, 'Eq change')
                if self.variables == list(sorted(config['equation'].keys())):
                    print(self.Name, 'Eq same variables')
                    self.set_equation(config['equation'])
                    values, connect = self.parse_parameters(config['parameters'])
                    self.update_parameters_values(values)
                    self.subsitute_and_build()
                    return connect
                else:
                    print(self.Name, 'Eq not same variables')
                    self.remove()
                    self.__init__(self.name)
                    self.setup(config)

        if 'output' in config:
            if config['output'] == self.output_dict:
                print(self.Name, 'Output no change')
            else:
                print(self.Name, 'Output change')
                self.update_outputs(config['output'])

        if 'parameters' in config:
            if config['parameters'] == self.parameters_dict:
                print(self.Name, 'Param Values no change')
                return 'no change'
            else:
                print(self.Name, 'Param Values change')
                values, connect = self.parse_parameters(config['parameters'])
                self.update_parameters_values(values)
                return connect

    def set_equation(self, equation):
        if isinstance(equation, dict):
            compiled_equations = {}
            for k, v in equation.items():
                compiled = parse_equation(v)
                if compiled is not None:
                    compiled_equations[k] = compiled
                    valid = True
                else:
                    valid = False
                    break

            if valid:
                self.equation = equation
                self.variables = list(sorted(self.equation.keys()))
                if self.first_time:
                    self.set_output_buses(len(self.variables))

                parameters_ = []
                no_parameters = [ov.upper() for ov in self.variables]
                no_parameters.append('PI')

                compiled_inputs = []
                for k, v in equation.items():
                    compiled_inputs += list(compiled_equations[k].inputs)
                compiled_inputs = set(compiled_inputs)
                for i in compiled_inputs:
                    if i not in no_parameters:
                        parameters_.append(i.lower())

                parameters_ = sorted(parameters_)
                if self.equation_parameters == parameters_:
                    print(self.Name, 'Param in eq no change')
                else:
                    if self.first_time:
                        self.equation_parameters = parameters_
                        print(self.Name, self.equation_parameters)
                        if 't' in self.equation_parameters:
                            self.equation_parameters.pop(self.equation_parameters.index('t'))

                        self.n_inputs = len(self.equation_parameters) + len(self.equation_inputs)
                        self.set_input_buses(self.n_inputs)
                    else:
                        print(self.Name, 'Param in eq change')

    def set_output_buses(self, num):
        self.output_buses = list(range(Ode.output_bus_counter, Ode.output_bus_counter + num))
        Ode.output_bus_counter += num

    def set_input_buses(self, num):
        self.input_buses = list(range(Ode.input_bus_counter, Ode.input_bus_counter + num))
        Ode.input_bus_counter += num

    def remove(self):
        for k in self.outputs:
            self.outputs[k].free()
            # sleep(sleep_time)
        for p in self.parameters:
            self.parameters[p].free()
            # sleep(sleep_time)
        self.free()

    def subsitute_and_build(self):
        if self.equation is not None:
            self.do_source_code()
            self.do_sc_def()
            self.build()

    def do_source_code(self):
        equation_str = []
        for j, (k, eq) in enumerate(self.equation.items()):
            for i, p in enumerate(self.equation_parameters):
                eq = re.sub(r'\b' + p + r'\b', 'param[{}]'.format(i), eq, flags=re.IGNORECASE)
            for i, x in enumerate(self.variables):
                eq = re.sub(r'\b' + x + r'\b', '#[{}]'.format(i), eq, flags=re.IGNORECASE)
            eq = eq.replace('#', 'X')
            eq = 'dX[{}]='.format(self.variables.index(k)) + eq
            equation_str.append(eq)

        self.equation_str = ';\n    '.join(equation_str) + ';'

        # add more constants
        self.equation_str = self.equation_str.replace('pi', 'PI')
        subs = {'N_EQ': len(self.variables), 'N_PARAMETERS': len(self.equation_parameters), 'EQUATION': self.equation_str}
        template_read_sub_write(ode_template_filename, self.ode_source_filename, subs)

    def do_sc_def(self):
        outputs = '\n\t'.join(['OffsetOut.ar({},osc[{}]);'.format(b, i) for i, b in enumerate(self.output_buses)])
        inputs = 'inputs = [' + ','.join(['InFeedback.ar({})'.format(i) for i in self.input_buses]) + '];'
        subs = {'Ode_name': self.Name, 'inputs': inputs, 'outputs': outputs}

        template_read_sub_write(sc_def_template_filename, self.sc_def_filename, subs)

    def build(self):
        os.chdir(self.build_path)
        command1 = 'g++ -fpic -c {Ode_name}.cpp -o {Ode_name}.o -Ofast'.format(Ode_name=self.Name)
        command2 = 'gcc -fpic -shared {Ode_name}.o -lm -o lib{Ode_name}.so -Ofast'.format(Ode_name=self.Name)

        subprocess.call(shlex.split(command1))
        subprocess.call(shlex.split(command2))

        copy2('{path}/lib{Ode_name}.so'.format(path=os.getcwd(), Ode_name=self.Name), '{path}/..'.format(path=os.getcwd()))

    def load_synth(self):
        self.server.loadSynthDef(self.sc_def_filename)

    def create_synth(self):
        self.new(self.Name, self.gen_group)

    def create_outputs(self, output):
        if isinstance(output, dict):
            for k, v in output.items():
                if k in self.variables:
                    bus = self.output_buses[self.variables.index(k)]
                    self.outputs[k] = Output(bus)

    def update_outputs(self, output):
        if isinstance(output, dict):
            self.output_dict = output
            for k, v in self.output_dict.items():
                if k in self.variables:
                    if k not in self.outputs:
                        self.create_outputs({k: v})
                    if 'gain' in v:
                        self.outputs[k].set(['amp', v['gain']])
                    if 'pan' in v:
                        self.outputs[k].set(['pan', v['pan']])

    def create_equation_parameters(self):
        for param, ibus in zip(self.equation_parameters, self.input_buses):
            self.parameters[param] = Parameter(ibus)

    def update_parameters_values(self, parameters_values):
        if isinstance(parameters_values, dict):
            self.parameters_dict = parameters_values
            for param, value in self.parameters.items():
                if param in parameters_values:
                    if isinstance(parameters_values[param], str):
                        value.set(['val', 0])
                    else:
                        value.set(['val', parameters_values[param]])

    def parse_parameters(self, parameters):
        values = {}
        connect = {}
        for param, value in parameters.items():
            if isinstance(value, str):
                connect[param] = parse_linear(value) + (self.parameters[param].bus,)
            else:
                values[param] = value

        return values, connect
