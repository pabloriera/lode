from __future__ import absolute_import, division, print_function

import os
import sys

# Anything that needs to be updated

PY_VERSION = sys.version_info[0]

# Any Py2to3

if PY_VERSION == 2:

    range = xrange
    input = raw_input

else:

    from importlib import reload

# Check for OS -> mac, linux, win

SYSTEM = 0
WINDOWS = 0
LINUX = 1
MAC_OS = 2

if sys.platform.startswith('darwin'):

    SYSTEM = MAC_OS

    # Attempted fix for some Mac OS users

    try:
        import matplotlib
        matplotlib.use('TkAgg')
    except ImportError:
        pass

elif sys.platform.startswith('win'):

    SYSTEM = WINDOWS

elif sys.platform.startswith('linux'):

    SYSTEM = LINUX

# Directory informations

USER_CWD = os.path.realpath(".")
LODE_ROOT = os.path.realpath(__file__ + "/../../")
LODE_ICON = os.path.realpath(LODE_ROOT + "/lib/Workspace/img/icon.ico")
LODE_ICON_GIF = os.path.realpath(LODE_ROOT + "/lib/Workspace/img/icon.gif")
LODE_HELLO = os.path.realpath(LODE_ROOT + "/lib/Workspace/img/hello.txt")
LODE_SND = os.path.realpath(LODE_ROOT + "/snd/")
LODE_LOOP = os.path.realpath(LODE_ROOT + "/snd/_loop_/")

SCLANG_EXEC = 'sclang.exe' if SYSTEM == WINDOWS else 'sclang'
SYNTHDEF_DIR = os.path.realpath(LODE_ROOT + "/sclang_comm/scsyndef/")
EFFECTS_DIR = os.path.realpath(LODE_ROOT + "/sclang_comm/sceffects/")
ENVELOPE_DIR = os.path.realpath(LODE_ROOT + "/sclang_comm/scenvelopes/")
TUTORIAL_DIR = os.path.realpath(LODE_ROOT + "/demo/")
RECORDING_DIR = os.path.realpath(LODE_ROOT + "/rec/")

LODE_OSC_FUNC = os.path.realpath(LODE_ROOT + "/sclang_comm/OSCFunc.scd")
LODE_STARTUP_FILE = os.path.realpath(LODE_ROOT + "/sclang_comm/Startup.scd")
LODE_BUFFERS_FILE = os.path.realpath(LODE_ROOT + "/sclang_comm/Buffers.scd")
LODE_EFFECTS_FILE = os.path.realpath(LODE_ROOT + "/sclang_comm/Effects.scd")
LODE_INFO_FILE = os.path.realpath(LODE_ROOT + "/sclang_comm/Info.scd")
LODE_RECORD_FILE = os.path.realpath(LODE_ROOT + "/sclang_comm/Record.scd")
LODE_TEMP_FILE = os.path.realpath(LODE_ROOT + "/lib/Workspace/tmp/tempfile.txt")

# If the tempfile doesn't exist, create it

if not os.path.isfile(LODE_TEMP_FILE):
    try:
        with open(LODE_TEMP_FILE, "w") as f:
            pass
    except FileNotFoundError:
        pass


def GET_SYNTHDEF_FILES():
    return [os.path.realpath(SYNTHDEF_DIR + "/" + path) for path in os.listdir(SYNTHDEF_DIR)]


def GET_FX_FILES():
    return [os.path.realpath(EFFECTS_DIR + "/" + path) for path in os.listdir(EFFECTS_DIR)]


def GET_TUTORIAL_FILES():
    return [os.path.realpath(TUTORIAL_DIR + "/" + path) for path in sorted(os.listdir(TUTORIAL_DIR))]

# Set Environment Variables


from . import conf

reload(conf)  # incase of a reload

LODE_CONFIG_FILE = conf.filename

ADDRESS = conf.ADDRESS
PORT = conf.PORT
PORT2 = conf.PORT2
FONT = conf.FONT
SC3_PLUGINS = conf.SC3_PLUGINS
MAX_CHANNELS = conf.MAX_CHANNELS
GET_SC_INFO = conf.GET_SC_INFO
USE_ALPHA = conf.USE_ALPHA
ALPHA_VALUE = conf.ALPHA_VALUE
MENU_ON_STARTUP = conf.MENU_ON_STARTUP
TRANSPARENT_ON_STARTUP = conf.TRANSPARENT_ON_STARTUP
RECOVER_WORK = conf.RECOVER_WORK
LINE_NUMBER_MARKER_OFFSET = conf.LINE_NUMBER_MARKER_OFFSET
CPU_USAGE = conf.CPU_USAGE
CLOCK_LATENCY = conf.CLOCK_LATENCY

if conf.SAMPLES_DIR is not None and conf.SAMPLES_DIR != "":

    LODE_SND = os.path.realpath(conf.SAMPLES_DIR)


def get_timestamp():
    import time
    return time.strftime("%Y%m%d-%H%M%S")

# Name of SamplePlayer and LoopPlayer SynthDef


class _SamplePlayer:
    names = ('play1', 'play2')

    def __eq__(self, other):
        return other in self.names

    def __ne__(self, other):
        return other not in self.names


class _LoopPlayer:
    names = ("loop", "gsynth")

    def __eq__(self, other):
        return other in self.names

    def __ne__(self, other):
        return other not in self.names


class _MidiPlayer:
    name = "MidiOut"

    def __eq__(self, other):
        return other == self.name

    def __ne__(self, other):
        return other != self.name


SamplePlayer = _SamplePlayer()
LoopPlayer = _LoopPlayer()
MidiPlayer = _MidiPlayer()


# OSC Information

OSC_MIDI_ADDRESS = "/foxdot_midi"

# Colours


class COLOURS:
    plaintext = conf.plaintext
    background = conf.background
    functions = conf.functions
    key_types = conf.key_types
    user_defn = conf.user_defn
    other_kws = conf.other_kws
    comments = conf.comments
    numbers = conf.numbers
    strings = conf.strings
    dollar = conf.dollar
    arrow = conf.arrow
    players = conf.players
