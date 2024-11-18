from ServerManager import DefaultServer
from IPython import embed
from OdeNetwork import OdeNetwork
import argparse
import pyinotify
import pathlib
from utils import groups_creation

odes = OdeNetwork()


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print('CLOSE_WRITE event', event.pathname, '\n')
        odes.read_yaml(event.pathname)


# def scope_window_creation():
#     embed()
#     DefaultServer.sclang_send(6, 3, 2, address='/lode/scope')


def main(args):
    groups_creation(DefaultServer)
    # scope_window_creation()

    odes_yaml = str(pathlib.Path(args.odes_yaml[0]).absolute())

    if args.watch:
        odes.read_yaml(odes_yaml)
        # odes.read_yaml(odes_yaml)

        wm = pyinotify.WatchManager()
        wm.add_watch(odes_yaml, pyinotify.ALL_EVENTS, rec=True)
        # event handler
        eh = MyEventHandler()
        # notifier
        notifier = pyinotify.Notifier(wm, eh)
        notifier.loop()
        print('\nGood Bye')
        odes.remove_all()
    else:
        odes.read_yaml(odes_yaml)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Build so from yaml file with ode definitions')
    parser.add_argument('odes_yaml', nargs='+',
                        help='yaml file with ode definitions')
    parser.add_argument('--watch', '-w', dest='watch',
                        action='store_true', help='watch file')
    args = parser.parse_args()
    print(args)
    main(args)
