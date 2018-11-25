# TODO
## Initial conditions:

It should be possible to set initial condition to the ode to start. And also it would be usefull a new command to restart the node, so the inital conditions take place again. In a more complex case initial conditions could be passed with a spetial type of input that triggers the system to go to that location and then continues. Example syntax:

```yaml
hopf:
  equation:
    x: '2*pi*y*w + (e*x-x*(x*x+y*y))*100.0'
    y: '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0'
  parameters:
    w: 440.0
    e: 1.0
  init:
    x: 0.5
    y: 0.5
```

## Time variable

It should be possible to add the time variable in the equations, this is rather strait fordward to do

```yaml
hopf:
  equation:
    x: '2*pi*y*w + sin(w*t) + (e*x-x*(x*x+y*y))*100.0'
    y: '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0'
```

## Output variables:

It shuld be possible to selec which are the output variables that will sound, and not the default all dynamic variables

```yaml
hopf:
  equation:
    x: '2*pi*y*w + sin(w*t) + (e*x-x*(x*x+y*y))*100.0'
    y: '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0'
  output:
    x:
      gain: 0.1
      channel: 1 
```

## Share variables:

This is already in the actual scope, because there is no distinction between a parameter and an 'external' input for a node.

```yaml
hopf:
  equation:
    x: '2*pi*y*w + (e*x-x*(x*x+y*y))*100.0'
    y: '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0+lorenz.x'

lorenz:
  equation:
    x: 'sigma*(y-x)*tau' 
    y: '(x*(rho-z)-y)*tau'
    z: '(x*y-beta*z)*tau'

```


## Delayed inputs:

It should be possible to delay an input signal, and also in the same node (feedback)

```yaml
hopf:
  equation:
    x: '2*pi*y*w + (e*x-x*(x*x+y*y))*100.0'
    y: '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0+x(-d)'
```

## Special inputs:

It could be a list of keywords that correspond to SC UGens, for example WhiteNoise  

```yaml
hopf:
  equation:
    x: '2*pi*y*w + (e*x-x*(x*x+y*y))*100.0'
    y: '-2*pi*x*w + (e*y-y*(x*x+y*y))*100.0 + WhiteNoise'
```


