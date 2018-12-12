from ServerManager import DefaultServer
from IPython import embed
from lib.Ode import Ode, SynthDef, Connect
import yaml
import argparse
import pyinotify
import pathlib

odes = {}
connects = {}


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print('CLOSE_WRITE event', event.pathname, '\n')
        yaml_parse(event.pathname)


def yaml_parse(filename):
    with open(filename, 'r') as fp:
        ode_config = yaml.load(fp)

    if ode_config is not None:
        for k, v in ode_config.items():
            if k not in odes:
                if 'equation' in ode_config[k]:
                    ode = Ode(k)
                    res = ode.setup(ode_config[k])
                    odes[k] = ode
            else:
                res = odes[k].update(ode_config[k])

            if res != 'no change':
                if isinstance(res, dict):
                    keep = []
                    if res:
                        for param, value in res.items():
                            ode_name, ode_var = value[0].split('.')
                            if ode_name in odes:
                                if ode_var in odes[ode_name].variables:
                                    from_ = odes[ode_name].output_buses[odes[ode_name].variables.index(ode_var)]
                                    to = value[3]
                                    mul = value[1]
                                    add = value[2]
                                    keep.append((from_, to))
                                    if not (from_, to) in connects:
                                        connects[(from_, to)] = Connect(from_, to, mul, add)
                                        print('Connect', from_, to, mul, add)
                                    else:
                                        connects[(from_, to)].set(['mul', mul, 'add', add])
                                        print('Update Connect', from_, to, mul, add)

                    for ft, c in list(connects.items()):
                        if ft not in keep:
                            print('Free', ft)
                            c.free()
                            connects.pop(ft)

        if len(odes.keys()) > len(ode_config.keys()):
            for k in set(odes.keys()) - set(ode_config.keys()):
                odes[k].remove()
                odes.pop(k)
    else:
        for k in list(odes.keys()):
            odes[k].remove()
            odes.pop(k)


def main(args):

    odes_yaml = str(pathlib.Path(args.odes_yaml[0]).absolute())
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
