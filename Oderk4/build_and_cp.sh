cd build
cmake ..
make clean
make 
cp Oderk4.so  ~/.local/share/SuperCollider/Extensions/Oderk4/plugins/
cd ..
cp Oderk4.sc  ~/.local/share/SuperCollider/Extensions/Oderk4/classes/
