g++ -c dbpf.cpp
g++ -shared dbpf.o -o dbpf32.dll

x86_64-w64-mingw32-g++ -c dbpf.cpp
x86_64-w64-mingw32-g++ -shared dbpf.o -o dbpf64.dll

del dbpf.o

pause