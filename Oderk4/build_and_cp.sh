#!/bin/bash
export SC_PATH=/usr/local/include/SuperCollider/
ODERK4_CLASS_PATH=$HOME'/.local/share/SuperCollider/Extensions/Oderk4/classes/'
ODERK4_PLUGIN_PATH=$HOME'/.local/share/SuperCollider/Extensions/Oderk4/plugins/'
rm -rf build
mkdir build
cd build
cmake ..
make clean
make
mkdir -p $ODERK4_PLUGIN_PATH
echo "Coping Oderk4.so to $ODERK4_PLUGIN_PATH"
cp -v Oderk4.so $ODERK4_PLUGIN_PATH
cd ..
mkdir -p $ODERK4_CLASS_PATH
echo "Coping Oderk4.scd to $ODERK4_CLASS_PATH"
cp -v Oderk4.sc $ODERK4_CLASS_PATH
