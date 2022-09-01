g++ -c dbpf.cpp
g++ -static -shared -o dbpf32.dll dbpf.o

x86_64-w64-mingw32-g++ -c dbpf.cpp
x86_64-w64-mingw32-g++ -static -shared -o dbpf64.dll dbpf.o

py -3-64 setup.py build_ext --inplace
py -3-32 setup.py build_ext --inplace

del dbpf.o
del dbpf.c
@RD /S /Q build

mkdir build
mkdir build\64bit
mkdir build\32bit

move dbpf64.dll build\64bit\dbpf.dll
move dbpf32.dll build\32bit\dbpf.dll

move dbpf.cp310-win_amd64.pyd build\64bit\dbpf.cp310-win_amd64.pyd
move dbpf.cp310-win32.pyd build\32bit\dbpf.cp310-win32.pyd

pause