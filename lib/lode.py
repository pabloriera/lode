from ServerManager import DefaultServer
from IPython import embed
from SynthDefs import SynthDef
from OdeNetwork import OdeNetwork
import argparse
import pyinotify
import pathlib
import sys, os

odes = OdeNetwork()


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print('CLOSE_WRITE event', event.pathname, '\n')
        odes.read_yaml(event.pathname)


def groups_creation():
    SynthDef.set_server(DefaultServer)
    # Groups creation
    n_conn = DefaultServer.nextnodeID()
    DefaultServer.send('/g_new', [n_conn, 1])
    n_param = DefaultServer.nextnodeID()
    DefaultServer.send('/g_new', [n_param])
    n_gen = DefaultServer.nextnodeID()
    DefaultServer.send('/g_new', [n_gen, 1])
    n_out = DefaultServer.nextnodeID()
    DefaultServer.send('/g_new', [n_out, 1])
    SynthDef.set_groups(n_conn, n_param, n_gen, n_out)


# def scope_window_creation():
#     embed()
#     DefaultServer.sclang_send(6, 3, 2, address='/lode/scope')


def main(args):
    groups_creation()
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
    parser = argparse.ArgumentParser(description='Build so from yaml file with ode definitions')
    parser.add_argument('odes_yaml', nargs='+', help='yaml file with ode definitions')
    parser.add_argument('--watch', '-w', dest='watch', action='store_true', help='watch file')
    args = parser.parse_args()
    print(args)
    main(args)
