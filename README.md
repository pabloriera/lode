## Live coding with Ordinary Differential Equations

Go to Oderk4 folder and execute build_and_cp.sh. This will copy the Supercollider Extension (.so file) into default user's Supercollider extension directory. Also it uses default include directory, change directories if needed.

Then go to lib folder and run:

```
python yaml2so.py -w ../odes.yaml
```

Then open odes.yaml in an editor and save it. This will compile the odes in the yaml.


Then run: (this must be done in the lib folder)

```
sclang -D ../autotest_oderk4.sc
```

A pure tone should sound. Now you can edit the hopf equation in the odes.yaml file and it will automaticaly updated. For example, we could jump an octave if we multiply w by 2:

```
equation:
  x: '4*pi*y*w + (e*x-x*(x*x+y*y))*100.0'
  y: '-4*pi*x*w + (e*y-y*(x*x+y*y))*100.0'
```

### Live code scenario

Start Supercollider from lib folder and run lode.sc code. Then run  python3 -m lib.lode.py -w odes.yaml (from parten folder). Now open the odes.yaml file and save it, sound should appear automatically.

