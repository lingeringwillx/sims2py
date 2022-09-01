g++ -c dbpf.cpp
g++ -static -shared -o dbpf32.dll dbpf.o

x86_64-w64-mingw32-g++ -c dbpf.cpp
x86_64-w64-mingw32-g++ -static -shared -o dbpf64.dll dbpf.o

copy dbpf.pyx dbpf64.pyx
copy dbpf.pyx dbpf32.pyx

py -3-64 setup64.py build_ext --inplace
py -3-32 setup32.py build_ext --inplace

del dbpf64.pyx
del dbpf32.pyx
del dbpf.o
del dbpf64.c
del dbpf32.c
@RD /S /Q build

mkdir build

move dbpf64.dll build\dbpf64.dll
move dbpf32.dll build\dbpf32.dll
move dbpf64.cp310-win_amd64.pyd build\dbpf64.cp310-win_amd64.pyd
move dbpf32.cp310-win32.pyd build\dbpf32.cp310-win32.pyd
copy dbpf.py build\dbpf.py

pause