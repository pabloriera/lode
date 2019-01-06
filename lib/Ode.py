from IPython import embed
import re
import subprocess
import os
from shutil import copy2
import shlex
import yaml
from utils import template_read_sub, template_read_sub_write, parse_equation, parse_linear
from directories import sc_extensions_path, home_path, sources_path
from directories import ode_template_filename, sc_def_template_filename, function_template_filename
from time import sleep
from collections import OrderedDict

sleep_time = 0.05
default_initial_condition = 0.001


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

    def set(self, **kwargs):
        if self.node is not None:
            args = [l for pair in kwargs.items() for l in pair]
            self.server.send('/n_set', [self.node] + args)

    def free(self):
        if self.node is not None:
            self.server.send('/n_free', [self.node])

    def __del__(self):
        self.free()


class Bus():
    def __init__(self):
        self.get_next_bus()

    @classmethod
    def get_next_bus(cls):
        cls.bus_id = cls.bus_counter
        cls.bus_counter += 1


class InputBus(Bus):
    bus_counter = 40

    def __init__(self):
        super().__init__()


class OutputBus(Bus):
    bus_counter = 10

    def __init__(self):
        super().__init__()


class OutputDef(SynthDef):
    def __init__(self, bus_id):
        super().__init__()
        self.new('output', self.output_group, ['bus', bus_id], action=1)
        self.bus_id = bus_id


class ConnectDef(SynthDef):
    def __init__(self, from_, to, mul=1, add=0):
        super().__init__()
        print('connection', ['from', from_, 'to', to, 'mul', mul, 'add', add])
        self.new('connection', self.connect_group, ['from', from_, 'to', to, 'mul', mul, 'add', add], action=1)


class ParameterDef(SynthDef):
    def __init__(self, bus_id):
        super().__init__()
        self.new('parameter', self.param_group, ['bus', bus_id], action=1)
        self.bus_id = bus_id


class Ode(SynthDef):
    def __init__(self, name, ode_network):
        super().__init__()
        self.ode_network = ode_network
        self.discrete = False
        self.equation = None
        self.initial_condition = None
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
        self.input_bus = OrderedDict()
        self.output_bus = OrderedDict()
        self.outputs = OrderedDict()
        self.output_config = OrderedDict()
        self.parameters = OrderedDict()
        self.parameters_config = OrderedDict()
        self.connections = OrderedDict()

    def setup(self, config):

        function = config['functions'] if 'functions' in config else None
        self.set_equation(config['equation'], functions=function)
        self.set_initial_conditions(config.get('init', None))

        if 'discrete' in config.keys():
            self.discrete = config['discrete']
            equation_parameters_ = ['hz'] + self.equation_parameters
        else:
            equation_parameters_ = self.equation_parameters

        self.create_equation_parameters(equation_parameters_)

        if 'parameters' in config:
            self.update_parameters_values(config['parameters'])

        self.create_outputs(self.variables)
        if 'output' in config:
            self.update_outputs(config['output'])

        self.subsitute_and_build()
        self.load_synth()
        sleep(sleep_time)
        self.create_synth()
        # sleep(sleep_time)

    def update(self, config):
        if 'equation' in config:
            if config['equation'] == self.equation:
                print(self.Name, 'Eq no change')
            else:
                print(self.Name, 'Eq change')
                if self.variables == list(sorted(config['equation'].keys())):
                    print(self.Name, 'Eq same variables')
                    self.set_equation(config['equation'])
                    self.update_parameters_values(config['parameters'])
                    self.subsitute_and_build()
                else:
                    print(self.Name, 'Eq not same variables')
                    self.remove()
                    self.__init__(self.name)
                    self.setup(config)

        if 'output' in config:
            if config['output'] == self.output_config:
                print(self.Name, 'Output no change')
            else:
                print(self.Name, 'Output change')
                self.update_outputs(config['output'])

        if 'parameters' in config:
            if config['parameters'] == self.parameters_config:
                print(self.Name, 'Param Values no change')
                return 'no change'
            else:
                print(self.Name, 'Param Values change')
                self.update_parameters_values(config['parameters'])

    def set_equation(self, equation, functions=None):
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

                parameters_ = []
                no_parameters = [ov.upper() for ov in self.variables] + ['PI', 'T']

                compiled_inputs = []
                for k, v in equation.items():
                    compiled_inputs += list(compiled_equations[k].inputs)
                compiled_inputs = set(compiled_inputs)
                for i in compiled_inputs:
                    if i not in no_parameters:
                        parameters_.append(i.lower())

                if set(self.equation_parameters) == set(parameters_):
                    print(self.Name, 'Param in eq no change')
                else:
                    for p in parameters_:
                        if p not in self.equation_parameters:
                            self.equation_parameters.append(p)

                    print(self.Name, self.equation_parameters)
                    print(self.Name, 'Param in eq change')

                if functions is not None:
                    self.functions = []
                    for name, func in functions.items():
                        self.functions.append({'ARGUMENTS': ', '.join(['double {}'.format(arg) for arg in func['args']]),
                                               'FUNCTION': name,
                                               'FORMULA': func['formula'] + ';'
                                               })
                else:
                    self.functions = None

    def remove(self):
        for k in self.outputs:
            self.outputs[k].free()
        for k in self.parameters:
            self.parameters[k].free()
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

        if self.functions is not None:
            functions = []
            for func in self.functions:
                functions.append(template_read_sub(function_template_filename, func))

            functions = '\n     '.join(functions)
        else:
            functions = ''

        # add more constants
        self.equation_str = self.equation_str.replace('pi', 'PI')
        subs = {'N_EQ': len(self.variables), 'N_PARAMETERS': len(self.equation_parameters),
                'EQUATION': self.equation_str, 'FUNCTIONS': functions}
        template_read_sub_write(ode_template_filename, self.ode_source_filename, subs)

    def do_sc_def(self):
        if self.discrete:
            rk4_or_discrete = 'Odemap'
        else:
            rk4_or_discrete = 'Oderk4'

        outputs = '\n\t'.join(['OffsetOut.ar({},osc[{}]);'.format(o.bus_id, i) for i, (var, o) in enumerate(self.outputs.items())])
        inputs = 'inputs = [' + ','.join(['InFeedback.ar({})'.format(p.bus_id) for param, p in self.parameters.items()]) + '];'
        initial_conditions = ','.join([str(self.initial_conditions[var]) for var in self.variables])
        subs = {'rk4_or_discrete': rk4_or_discrete, 'Ode_name': self.Name, 'inputs': inputs, 'outputs': outputs,
                'initial_conditions': initial_conditions}
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

    def set_initial_conditions(self, config):
        if config is not None:
            self.initial_conditions = config
        else:
            self.initial_conditions = {k: default_initial_condition for k in self.variables}

    def create_output(self, output_var):
        self.output_bus[output_var] = OutputBus()
        return OutputDef(self.output_bus[output_var].bus_id)

    def create_outputs(self, variables):
        for output_var in variables:
            self.outputs[output_var] = self.create_output(output_var)

    def update_outputs(self, output_config):
        if isinstance(output_config, dict):
            self.output_config = output_config
            for k, v in self.output_config.items():
                if k in self.outputs.keys():
                    if 'gain' in v:
                        self.outputs[k].set(amp=v['gain'])
                    if 'pan' in v:
                        self.outputs[k].set(pan=v['pan'])

    def create_equation_parameter(self, param):
        self.input_bus[param] = InputBus()
        return ParameterDef(self.input_bus[param].bus_id)

    def create_equation_parameters(self, equation_parameters):
        for param in equation_parameters:
            self.parameters[param] = self.create_equation_parameter(param)

    def update_parameters_values(self, config):
        if config is not None:
            parameters_values = self.parse_parameters(config)
            self.parameters_config = parameters_values
            for param, value in self.parameters.items():
                if param in parameters_values:
                    value.set(val=parameters_values[param])

    def parse_parameters(self, parameters):
        values = {}
        for param, value in parameters.items():
            if isinstance(value, str):
                if param in self.connections:
                    self.connections[param].remove_all()
                add, terms = parse_linear(value)
                self.connections[param] = Connections()
                for t in terms:
                    if t['ode'] in self.ode_network.keys():
                        if t['var'] in self.ode_network[t['ode']].variables:
                            self.connections[param].add_connection(self.ode_network[t['ode']], t['var'], self, param, t['mul'])
                if add != 0:
                    values[param] = add
            else:
                values[param] = value
        return values


class Connection():
    def __init__(self, from_ode, from_var, to_ode, to_parameter, mul=1, add=0):
        self.from_ode = from_ode
        self.from_var = from_var
        self.to_ode = to_ode
        self.to_parameter = to_parameter

        self.from_bus = from_ode.outputs[from_var].bus_id
        self.to_bus = to_ode.parameters[to_parameter].bus_id

        self.mul = mul
        self.add = add

    def connect(self):
        self.connect_def = ConnectDef(self.from_bus, self.to_bus, self.mul, self.add)

    def update(self, **kwargs):
        self.connect_def.set(**kwargs)

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        self.connect_def.free()


class Connections(OrderedDict):
    def __init__(self):
        pass

    def add_connection(self, from_ode, from_var, to_ode, to_parameter, mul=1, add=0):
        con = Connection(from_ode, from_var, to_ode, to_parameter, mul, add)
        con.connect()
        self[(from_ode, from_var, to_ode, to_parameter)] = con

    def remove_connection(self, from_ode, from_var, to_ode, to_parameter):
        del self[(from_ode, from_var, to_ode, to_parameter)]

    def remove_all(self):
        self.clear()

    def __del__(self):
        self.remove_all()


class OdeNetwork(OrderedDict):

    def __init__(self):
        pass

    def add_ode(self, name, config):
        ode = Ode(name, self)
        ode.setup(config)
        self[name] = ode

    def remove_ode(self, name):
        self[name].remove()
        del self[name]

    # def add_connection(self, from_ode, from_var, to_ode, to_parameter, mul, add):
    #     self.connections.add_connection(from_ode, from_var, to_ode, to_parameter, mul, add)

    # def remove_connection(self, from_ode, from_var, to_ode, to_parameter, mul, add):
    #     self.connections.remove_connection(from_ode, from_var, to_ode, to_parameter)

    def read_yaml(self, filename):
        try:
            with open(filename, 'r') as fp:
                ode_config = yaml.load(fp)
        except Exception:
            pass

        if ode_config is not None:
            for ode_name, v in ode_config.items():
                if ode_name not in self.keys():
                    if 'equation' in ode_config[ode_name]:
                        self.add_ode(ode_name, ode_config[ode_name])
                else:
                    self[ode_name].update(ode_config[ode_name])

            if len(self.keys()) > len(ode_config.keys()):
                for ode_name in set(self.keys()) - set(ode_config.keys()):
                    self.remove_ode(ode_name)
            # else:
            #     for ode_name in list(self.keys()):
            #         self.remove_ode(ode_name)

    # def update_connections(self):

    #     for ode_name, ode in self.items():

    #         for param, conn in ode.connections.items():

            # if res != 'no change':
            #     if isinstance(res, dict):
            #         keep = []
            #         if res:
            #             for param, value in res.items():
            #                 ode_name, ode_var = value[0].split('.')
            #                 if ode_name in odes:
            #                     if ode_var in odes[ode_name].variables:
            #                         from_ = odes[ode_name].output_buses[odes[ode_name].variables.index(ode_var)]
            #                         to = value[3]
            #                         mul = value[1]
            #                         add = value[2]
            #                         keep.append((from_, to))
            #                         if not (from_, to) in connects:
            #                             connects[(from_, to)] = Connect(from_, to, mul, add)
            #                             print('Connect', from_, to, mul, add)
            #                         else:
            #                             connects[(from_, to)].set(['mul', mul, 'add', add])
            #                             print('Update Connect', from_, to, mul, add)

            #         for ft, c in list(connects.items()):
            #             if ft not in keep:
            #                 print('Free', ft)
            #                 c.free()
            #                 connects.pop(ft)
