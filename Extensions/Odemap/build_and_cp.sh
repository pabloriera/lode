#!/bin/bash
export SC_PATH=/usr/local/include/SuperCollider/
ODEMAP_CLASS_PATH=$HOME'/.local/share/SuperCollider/Extensions/Odemap/classes/'
ODEMAP_PLUGIN_PATH=$HOME'/.local/share/SuperCollider/Extensions/Odemap/plugins/'
rm -rf build
mkdir build
cd build
cmake ..
make clean
make
mkdir -p $ODEMAP_PLUGIN_PATH
echo "Coping Odemap.so to $ODEMAP_PLUGIN_PATH"
cp -v Odemap.so $ODEMAP_PLUGIN_PATH
cd ..
mkdir -p $ODEMAP_CLASS_PATH
echo "Coping Odemap.scd to $ODEMAP_CLASS_PATH"
cp -v Odemap.sc $ODEMAP_CLASS_PATH
