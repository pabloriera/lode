from time import sleep
from IPython import embed
import yaml
from collections import OrderedDict
from SynthDefs import Ode


class OdeNetwork(OrderedDict):

    def __init__(self):
        pass

    def add_ode(self, name, config):
        ode = Ode(name, self)
        ode.setup(config)
        self[name] = ode

    def read_yaml(self, filename, first=False):
        try:
            with open(filename, 'r') as fp:
                ode_config = yaml.load(fp, Loader=yaml.Loader)
        except Exception as e:
            print(e)
            ode_config = None

        if ode_config is not None:
            for ode_name, v in ode_config.items():
                sleep(0.1)
                if ode_name not in self.keys():
                    if 'equation' in ode_config[ode_name]:
                        self.add_ode(ode_name, ode_config[ode_name])                        
                else:
                    self[ode_name].update(ode_config[ode_name])

            if first:
                 for ode_name, v in ode_config.items():
                    if 'equation' in ode_config[ode_name]:
                        self[ode_name].update(ode_config[ode_name], force=True)

            if len(self.keys()) > len(ode_config.keys()):
                for ode_name in set(self.keys()) - set(ode_config.keys()):
                    self.remove_ode(ode_name)

     
        else:
            print('clear')
            self.remove_all()

    def remove_ode(self, name):
        self[name].remove()
        del self[name]

    def __del__(self):
        self.remove_all()

    def remove_all(self):
        for ode_name in self:
            self[ode_name].remove()
        self.clear()
