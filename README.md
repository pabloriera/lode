# lode: Live coding with Ordinary Differential Equations

## Dependencies

* Supercollider 3.7+
* Python 3+

## Install

First, clone the repository.  You will also need cmake to compile the SC
extensions and SC source code (dev packages).

```
sudo apt-get install build-essential cmake supercollider-dev
```

Then, install Python dependencies:

```
pip install -r --user requirements.txt
```

Go to Extensions/{Oderk4,Odemap} folder and execute `build_and_cp.sh`.  This will copy the
Supercollider Extension (`.so` file) into default user's Supercollider
extension directory.  Also it uses default include directory, change
directories if needed.

## Usage

Start Supercollider with:

```
cd lib/ && sclang -D lode.scd
```

On another terminal run:

```
python3 lib/lode.py -w odes.yaml
```

Now open the `odes.yaml` file and save it, sound should appear automatically.
