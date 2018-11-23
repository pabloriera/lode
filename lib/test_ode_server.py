from .ServerManager import DefaultServer
from IPython import embed
from lib.Ode import Ode


ode_config = {'hopf': {'parameters':
                       {'w': 440, 'e': 1.0},
                       'equation': {'x': '2*pi*y*w + (e*x-x*(x*x+y*y))*100.0',
                                    'y': '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0'}},
              'lorenz': {'parameters': {'beta': 2.6666, 'sigma': 10, 'rho': 28, 'tau': 50.0},
                         'equation': {'x': 'sigma*(y-x)*tau', 'z': '(x*y-beta*z)*tau',
                                      'y': '(x*(rho-z)-y)*tau'}}}

k = 'hopf'
o = Ode({k: ode_config[k]})
o.set_server(DefaultServer)
o.load_synth()
n = o.server.nextnodeID()
o.server.send('/s_new', ['Hopf', n])

embed()
