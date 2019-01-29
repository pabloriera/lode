from IPython import embed
import re
import subprocess
import os
from shutil import copy2
import shlex
from utils import template_read_sub, template_read_sub_write, parse_equation
from directories import sc_extensions_path, home_path, sources_path
from directories import ode_template_filename, sc_def_template_filename, function_template_filename
from time import sleep
from collections import OrderedDict
from utils import parse_parameter_formula
from dictdiffer import diff

sleep_time = 0.05
default_initial_condition = 0.001
scope_n = 6
scope_i = 2
scope_j = 3
external_input_list = ['sine', 'sine1', 'tri', 'tri1', 'noise']
input_bus_offset = 30
output_bus_offset = 80
default_lag = 0.05


class SynthDef():
    connect_group = None
    param_group = None
    gen_group = None
    output_group = None
    server = None

    @classmethod
    def set_server(cls, server):
        cls.server = server
        print('Server: ', server)

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
        # print('Freeing', self.node)
        if self.node is not None:
            self.server.send('/n_free', [self.node])

    def __del__(self):
        self.free()


class OutputDef(SynthDef):
    def __init__(self, bus_id):
        super().__init__()
        self.new('output', self.output_group, ['bus', bus_id], action=1)
        self.bus_id = bus_id


class ConnectDef(SynthDef):
    def __init__(self, from_, to, mul=1, add=0, delay_time=0):
        super().__init__()
        self.new('connection', self.connect_group, ['from', from_, 'to', to, 'mul', mul, 'add', add, 'del', delay_time], action=1)


class ValueDef(SynthDef):
    def __init__(self, bus_id):
        super().__init__()
        self.new('value', self.param_group, ['bus', bus_id], action=1)
        self.bus_id = bus_id


class SCInputDef(SynthDef):
    def __init__(self, bus_id, sc_input):
        super().__init__()
        self.new(sc_input, self.param_group, ['bus', bus_id], action=1)
        self.bus_id = bus_id


class ScopeDef(SynthDef):
    scope_ix = 0

    def __init__(self, bus_id, channels):
        super().__init__()
        self.bus_id = bus_id
        self.bufnum = ScopeDef.scope_ix
        self.new('scope', self.output_group, ['bus', bus_id, 'bufnum', self.bufnum, 'channels', channels], action=1)
        ScopeDef.scope_ix += 1
        ScopeDef.scope_ix = ScopeDef.scope_ix % scope_n
        print('scope_ix', ScopeDef.scope_ix)


class Bus():
    def __init__(self):
        self.get_next_bus(self)
        # if DEBUG:
        # print('New class', self, 'bus id:',
        # self.bus_id, 'bus_counter:', self.bus_counter)

    @classmethod
    def get_next_bus(cls, instance):
        instance.bus_id = cls.bus_counter
        cls.bus_counter += 1


class InputBus(Bus):
    bus_counter = input_bus_offset

    def __init__(self):
        super().__init__()


class OutputBus(Bus):
    bus_counter = output_bus_offset

    def __init__(self):
        super().__init__()


class Parameter():
    def __init__(self, name, bus_id, ode):
        self.ode = ode
        self.name = name
        self.bus_id = bus_id
        # self.formula = None
        self.prev_external_inputs = {}
        self.external_inputs_conn = OrderedDict()
        self.value = ValueDef(bus_id)

    def update(self, value_or_formula, lag=default_lag):
        if isinstance(value_or_formula, str):
            parsed = parse_parameter_formula(value_or_formula)
            if parsed is not None:
                add, self.external_inputs = parsed
                if add != 0:
                    self.value.set(val=add, lag=lag)
                self.do_connections(lag=lag)
        else:
            self.value.set(val=value_or_formula, lag=lag)
            self.prev_external_inputs = {}
            self.external_inputs_conn.clear()
            # [v.free() for k, v in self.external_inputs_conn.items()]

    def do_connections(self, lag=default_lag):
        try:
            # print(self.prev_external_inputs, '\n', self.external_inputs)
            diffs = list(diff(self.prev_external_inputs, self.external_inputs))
            print(diffs)
            for d in diffs:
                update_ts = {}
                if d[0] == 'change':
                    external_input = d[1].split('.')[0]
                    update_ts[external_input] = self.external_inputs[external_input]

                elif d[0] == 'add':
                    for external_input, t in d[2]:
                        if 'var' in t:
                            if external_input in self.ode.ode_network:
                                update_ts[external_input] = t
                                self.external_inputs_conn[external_input] = Connection(self.ode.ode_network[external_input],
                                                                                       t['var'], self.ode, self.name, mul=t['mul'])
                            else:
                                self.external_inputs.pop(external_input)
                        else:
                            if external_input in external_input_list:
                                update_ts[external_input] = t
                                self.external_inputs_conn[external_input] = SCInputDef(self.bus_id, external_input)

                            if external_input == 'value':
                                update_ts[external_input] = t
                                self.external_inputs_conn[external_input] = self.value

                elif d[0] == 'remove':
                    for external_input, t_ in d[2]:
                        if external_input in self.external_inputs_conn:
                            self.external_inputs_conn[external_input].free()

                for external_input, t in update_ts.items():
                    # print(external_input, t)

                    if external_input in external_input_list or external_input in self.ode.ode_network or external_input == 'value':
                        self.external_inputs_conn[external_input].set(lag=lag, mul=t['mul'])
                        if t.get('args', None):
                            args = {arg: float(val) for arg, val in t['args'].items()}
                            self.external_inputs_conn[external_input].set(lag=lag, **args)
                        if t.get('midi', None):
                            node = self.external_inputs_conn[external_input].node
                            self.assign_midi(node, t['midi'])

            self.prev_external_inputs = self.external_inputs

        except Exception as e:
            print(e)
            embed()

    def assign_midi(self, node, args):
        for k, v in args.items():
            cc = int(v.args[0])
            min_ = float(v.args[1])
            max_ = float(v.args[2])

            command = """
            MIDIdef(\\cc{cc}).free;
            MIDIdef.cc(\\cc{cc}, {{arg val, chan, arg2, arg3;
                s.sendMsg("/n_set",{node},"{arg}",val/127.0*({max} - {min}) + {min});}}, {cc});
            """.format(node=node, cc=cc, arg=k, min=min_, max=max_)

            self.ode.server.loadSynthDef(command, address='/lode/interpret')


class Connection():
    def __init__(self, from_ode, from_var, to_ode, to_parameter, mul=1, add=0, delay_time=0):
        self.from_ode = from_ode
        self.from_var = from_var
        self.to_ode = to_ode
        self.to_parameter = to_parameter

        self.from_bus = from_ode.outputs[from_var].bus_id
        self.to_bus = to_ode.parameters[to_parameter].bus_id

        self.mul = mul
        self.add = add
        self.delay_time = delay_time
        print('Connecting', 'from', from_ode.Name, from_var, 'to', to_ode.Name, to_parameter, 'mul', mul, 'add', add, 'delay_time', delay_time)
        self.connect()
        self.node = self.connect_def.node

    def connect(self):
        self.connect_def = ConnectDef(self.from_bus, self.to_bus, self.mul, self.add, self.delay_time)

    def set(self, **kwargs):
        self.connect_def.set(**kwargs)

    def update(self, **kwargs):
        self.connect_def.set(**kwargs)

    def __del__(self):
        self.free()

    def free(self):
        self.connect_def.free()


class Ode(SynthDef):
    def __init__(self, name, ode_network):
        super().__init__()
        self.ode_network = ode_network
        self.discrete = False
        self.config = OrderedDict()
        self.initial_condition = None
        self.scope = None
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
        self.parameters = OrderedDict()
        self.parameters_formulas = OrderedDict()
        self.connections = OrderedDict()
        self.lag = default_lag

    def setup(self, config):

        if 'discrete' in config.keys():
            self.discrete = config['discrete']
        else:
            self.discrete = None

        self.set_equation(config['equation'], functions=config.get('functions', None))
        self.config['init'] = {k: default_initial_condition for k in self.variables}
        if 'init' in config:
            self.update_initial_conditions(config['init'])

        if self.discrete is not None:
            equation_parameters_ = ['hz'] + self.equation_parameters
        else:
            equation_parameters_ = self.equation_parameters

        self.create_parameters(equation_parameters_)

        if 'lag' in config:
            self.lag = config['lag']
        else:
            self.lag = default_lag

        if 'parameters' in config:
            self.update_parameters(config['parameters'])

        self.create_outputs(self.variables)
        if 'output' in config:
            self.update_outputs(config['output'])

        self.create_scope()
        if 'scope' in config:
            self.update_scope(config['scope'])

        self.subsitute_and_build()
        self.load_synth()
        sleep(sleep_time)
        self.create_synth()

        # sleep(sleep_time)

    def update(self, config):
        if 'equation' in config:
            if config['equation'] == self.config['equation']:
                print(self.Name, 'Eq no change')
            else:
                print(self.Name, 'Eq change')
                if self.variables == list(sorted(config['equation'].keys())):
                    embed()
                    print(self.Name, 'Eq same variables')
                    self.set_equation(config['equation'], functions=config.get('functions', None))
                    # Must check what parameters are new and add them

                    # self.update_parameters(config['parameters'])
                    # self.create_parameters(equation_parameters_)
                    self.subsitute_and_build()
                else:
                    print(self.Name, 'Eq not same variables')
                    embed()
                    self.remove()
                    self.__init__(self.name, self.ode_network)
                    self.setup(config)

        if 'init' in config:
            self.update_initial_conditions(config['init'])

        if 'output' in config:
            self.update_outputs(config['output'])

        if 'lag' in config:
            self.lag = config['lag']
        else:
            self.lag = default_lag

        if 'parameters' in config:
            self.update_parameters(config['parameters'])

        if 'scope' in config:
            self.update_scope(config['scope'])

    def set_equation(self, equation, functions=None):
        if isinstance(equation, dict):
            expresions = {}
            for k, v in equation.items():
                peq = parse_equation(v)
                if peq is not None:
                    expresions[k] = peq
                    valid = True
                else:
                    valid = False
                    break

            if valid:
                self.config['equation'] = equation
                self.variables = list(sorted(self.config['equation'].keys()))
                parameters_ = []
                no_parameters = self.variables + ['pi']
                if self.discrete is not None:
                    no_parameters += ['n']
                else:
                    no_parameters += ['t']

                free_symbols = set()
                for k, v in equation.items():
                    free_symbols = free_symbols.union(map(str, expresions[k].free_symbols))
                for s in free_symbols:
                    if s not in no_parameters:
                        parameters_.append(s)

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

    def __del__(self):
        self.remove()

    def remove(self):
        for k in self.outputs:
            self.outputs[k].free()
        for k in self.parameters:
            self.parameters[k].external_inputs_conn.clear()
            self.parameters[k].value.free()
        self.free()

    def subsitute_and_build(self):
        if self.config['equation'] is not None:
            self.do_source_code()
            self.do_sc_def()
            self.build()

    def do_source_code(self):
        equation_str = []
        for j, (k, eq) in enumerate(self.config['equation'].items()):
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

        if self.discrete:
            torn = 'int n'
        else:
            torn = 'double t'

        # add more constants
        self.equation_str = self.equation_str.replace('pi', 'PI')
        subs = {'N_EQ': len(self.variables), 'N_PARAMETERS': len(self.equation_parameters),
                'EQUATION': self.equation_str, 'FUNCTIONS': functions, 'TorN': torn}
        template_read_sub_write(ode_template_filename, self.ode_source_filename, subs)

    def do_sc_def(self):
        if self.discrete is not None:
            rk4_or_discrete = 'Odemap'
        else:
            rk4_or_discrete = 'Oderk4'

        outputs = '\n\t'.join(['OffsetOut.ar({},osc[{}]);'.format(o.bus_id, i) for i, (var, o) in enumerate(self.outputs.items())])
        inputs = 'inputs = [' + ','.join(['InFeedback.ar({})'.format(p.bus_id) for param, p in self.parameters.items()]) + '];'
        initial_conditions = ','.join(['init_{}'.format(i) for i, var in enumerate(self.variables)])
        initial_conditions_args = ','.join(['init_{}={}'.format(i, str(self.config['init'][var])) for i, var in enumerate(self.variables)])

        impulse = ''
        if self.discrete is not None:
            if self.discrete == 'impulse':
                impulse = '*Impulse.ar(inputs[0])'

        subs = {'rk4_or_discrete': rk4_or_discrete, 'Ode_name': self.Name, 'inputs': inputs, 'outputs': outputs,
                'initial_conditions': initial_conditions, 'initial_conditions_args': initial_conditions_args, 'impulse': impulse}
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

    def update_initial_conditions(self, config):
        if self.config.get('init', None) == config:
            print(self.Name, 'Init no change')
        else:
            print(self.Name, 'Init change')
            init_set_ = {'init_{}'.format(self.variables.index(v)): config[v] for v in config}
            print(init_set_)
            self.set(**init_set_)
            self.config['init'].update(config)

    def create_scope(self):
        if self.scope is not None:
            self.scope.free()

        bus_id = list(self.output_bus.values())[0].bus_id
        channels = len(self.output_bus)
        self.scope = ScopeDef(bus_id, channels)

    def update_scope(self, config):
        if self.config.get('scope', None) == config:
            print(self.Name, 'Scope no change')
        else:
            print(self.Name, 'Scope change')
            self.config['scope'] = config
            if 'channels' in config:
                self.scope.set(channels=config.pop('channels'))
            if 'offset' in config:
                self.scope.set(offset=config.pop('offset'))
            for k, v in config.items():
                command = 'AppClock.sched(0.1,{{c[{scope_ix}].{key}={value}; nil;}});'.format(scope_ix=self.scope.bufnum, key=k, value=v)
                self.server.loadSynthDef(command, address='/lode/interpret')

    def create_output(self, output_var):
        self.output_bus[output_var] = OutputBus()
        return OutputDef(self.output_bus[output_var].bus_id)

    def create_outputs(self, variables):
        for output_var in variables:
            self.outputs[output_var] = self.create_output(output_var)

    def update_outputs(self, config):
        if self.config.get('output', None) == config:
            print(self.Name, 'Output no change')
        else:
            print(self.Name, 'Output change')
            self.config['output'] = config
            for k, v in config.items():
                if k in self.outputs.keys():
                    if 'gain' in v:
                        self.outputs[k].set(amp=v['gain'])
                    if 'pan' in v:
                        self.outputs[k].set(pan=v['pan'])

    def create_parameters(self, equation_parameters):
        for param in equation_parameters:
            self.input_bus[param] = InputBus()
            self.parameters[param] = Parameter(param, self.input_bus[param].bus_id, self)

    def update_parameters(self, config):
        if self.config.get('parameters', None) == config:
            print(self.Name, 'Parameters no change')
        else:
            print(self.Name, 'Parameters change')
            self.config['parameters'] = config
            for name in config:
                if name in self.parameters:
                    self.parameters[name].update(config[name], lag=self.lag)
