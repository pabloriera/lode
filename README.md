## Live coding with Ordinary Differential Equations

Install Python dependencies:

```
pip install -r requirements.txt
```

Go to Oderk4 folder and execute `build_and_cp.sh`. This will copy the
Supercollider Extension (`.so` file) into default user's Supercollider
extension directory. Also it uses default include directory, change directories
if needed.

Then run:

```
python3 lib/yaml2so.py -w odes.yaml
```

Then open `odes.yaml` in an editor and save it. This will compile the odes in
the yaml.

Then run on another terminal:

```
cd lib/ && sclang -D ../autotest_oderk4.sc
```

A pure tone should sound. Now you can edit the hopf equation in the `odes.yaml`
file and it will automaticaly updated. For example, we could jump an octave if
we multiply w by 2:

```yaml
equation:
  x: '4*pi*y*w + (e*x-x*(x*x+y*y))*100.0'
  y: '-4*pi*x*w + (e*y-y*(x*x+y*y))*100.0'
```

### Live code scenario

Start Supercollider with:

```
cd lib/ && sclang -D lode.sc
```

On another terminal run:

```
python3 lib/lode.py -w odes.yaml
```

Now open the `odes.yaml` file and save it, sound should appear automatically.
