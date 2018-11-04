import yaml
from Ode import Ode
import argparse
import pyinotify
import pathlib
from IPython import embed

odes = {}


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print('CLOSE_WRITE event', event.pathname, '\n')
        yaml_parse(event.pathname)


def yaml_parse(filename):
    with open(filename, 'r') as fp:
        ode_config = yaml.load(fp)

    for k, v in ode_config.items():
        if k not in odes:
            ode = Ode({k: ode_config[k]})
            ode.setup()
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build so from yaml file with ode definitions')
    parser.add_argument('odes_yaml', nargs='+', help='yaml file with ode definitions')
    parser.add_argument('--watch', '-w', dest='watch', action='store_true', help='watch file')
    args = parser.parse_args()
    main(args)
