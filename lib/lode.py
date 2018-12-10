from ServerManager import DefaultServer
from IPython import embed
from lib.Ode import Ode
import yaml
import argparse
import pyinotify
import pathlib
from time import sleep

odes = {}
groups = {}


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print('CLOSE_WRITE event', event.pathname, '\n')
        yaml_parse(event.pathname)


def yaml_parse(filename):
    with open(filename, 'r') as fp:
        ode_config = yaml.load(fp)

    print(ode_config)

    for k, v in ode_config.items():
        if k not in odes:
            ode = Ode(k)
            if 'equation' in ode_config[k]:
                ode.set_equation(ode_config[k]['equation'])
                ode.set_default_parameters(ode_config[k]['parameters'])
                ode.setup()
                ode.load_synth()
                sleep(1)
                ode.create_synth()
                ode.create_outputs(ode_config[k]['output'])
                odes[ode.name] = ode
        else:
            if 'equation' in ode_config[k]:
                if ode_config[k]['equation'] == odes[k].equation:
                    print('Eq no change')
                else:
                    print('Eq change')
                    odes[k].set_equation(ode_config[k]['equation'])
                    odes[k].set_default_parameters(ode_config[k]['parameters'])
                    odes[k].setup()

            if 'output' in ode_config[k]:
                if ode_config[k]['output'] == odes[k].output:
                    print('Output no change')
                else:
                    odes[k].update_outputs(ode_config[k]['output'])

            if 'parameters' in ode_config[k]:
                if ode_config[k]['parameters'] == odes[k].parameter_values:
                    print('Param no change')
                else:
                    print('Param change')
                    odes[k].update_parameters_value(ode_config[k]['parameters'])


def main(args):

    odes_yaml = str(pathlib.Path(args.odes_yaml[0]).absolute())
    Ode.set_server(DefaultServer)

    # Groups creation
    n_gen = DefaultServer.nextnodeID()
    DefaultServer.send('/g_new', [n_gen])
    groups['gen'] = n_gen
    n_out = DefaultServer.nextnodeID()
    DefaultServer.send('/g_new', [n_out, 1])
    groups['out'] = n_out

    Ode.set_groups(n_gen, n_out)

    if args.watch:
        wm = pyinotify.WatchManager()
        wm.add_watch(odes_yaml, pyinotify.ALL_EVENTS, rec=True)

        # event handler
        eh = MyEventHandler()

        # notifier
        notifier = pyinotify.Notifier(wm, eh)
        notifier.loop()
    else:
        yaml_parse(odes_yaml)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build so from yaml file with ode definitions')
    parser.add_argument('odes_yaml', nargs='+', help='yaml file with ode definitions')
    parser.add_argument('--watch', '-w', dest='watch', action='store_true', help='watch file')
    args = parser.parse_args()
    print(args)
    main(args)
