g++ -c -fPIC -O2 qfs.cpp
g++ -shared qfs.o -o qfs.dll
del qfs.o
pause