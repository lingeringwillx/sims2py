g++ -c dbpf.cpp
g++ -static -shared -o dbpf32.dll dbpf.o

x86_64-w64-mingw32-g++ -c dbpf.cpp
x86_64-w64-mingw32-g++ -static -shared -o dbpf64.dll dbpf.o

del dbpf.o

pause