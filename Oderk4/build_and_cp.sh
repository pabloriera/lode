#!/bin/bash
export SC_PATH=/usr/local/include/SuperCollider/
mkdir build
cd build
cmake ..
make clean
make
mkdir -p ~/.local/share/SuperCollider/Extensions/Oderk4/plugins/ 
cp Oderk4.so  ~/.local/share/SuperCollider/Extensions/Oderk4/plugins/
cd ..
mkdir -p ~/.local/share/SuperCollider/Extensions/Oderk4/classes/
cp Oderk4.sc  ~/.local/share/SuperCollider/Extensions/Oderk4/classes/
