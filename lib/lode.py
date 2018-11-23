from .ServerManager import DefaultServer
from IPython import embed
from lib.Ode import Ode
import yaml
import argparse
import pyinotify
import pathlib
from time import sleep

odes = {}


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
            ode = Ode({k: ode_config[k]})
            ode.setup()
            ode.set_server(DefaultServer)
            ode.load_synth()
            sleep(1)
            n = ode.server.nextnodeID()
            print('Node:', n)
            ode.server.send('/s_new', [ode.Name, n])
            odes[ode.name] = ode
        else:
            if ode_config[k]['equation'] == odes[k].config[k]['equation']:
                print('No change')
            else:
                odes[k] = Ode({k: ode_config[k]})
                odes[k].setup()


def main(args):

    odes_yaml = str(pathlib.Path(args.odes_yaml[0]).absolute())

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


if __name__ == 'lib.lode':
    parser = argparse.ArgumentParser(description='Build so from yaml file with ode definitions')
    parser.add_argument('odes_yaml', nargs='+', help='yaml file with ode definitions')
    parser.add_argument('--watch', '-w', dest='watch', action='store_true', help='watch file')
    args = parser.parse_args()
    print(args)
    main(args)
