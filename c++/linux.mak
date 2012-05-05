CC=gcc
CXX=g++ -std=gnu++0x
CFLAGS=-I/usr/include/python2.7
CXXFLAGS=-DBUILD_PYTHON $(CFLAGS)
LIBS=-lpython2.7 -lboost_python -lboost_regex

all: HALnative.so ../HALnative.so hunspell.so ../hunspell.so

clean:
	del *.lib
	del *.obj
	del *.exp

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $*.cpp

console.cpp: console.h stdafx.h
HALBot.cpp: HALBot.h stdafx.h

HALnative.so: HALBot.o HALnative.o
	$(CXX) $(CXXFLAGS) -shared -Wl,-soname,HALnative.so -o HALnative.so HALBot.o HALnative.o $(LIBS)

hunspell.so: hunspell.c
	$(CC) $(CFLAGS) -shared -Wl,-soname,hunspell.so -o hunspell.so hunspell.c -lhunspell -I/usr/include/hunspell

../hunspell.so: hunspell.so
	cp hunspell.so ..

../HALnative.so: HALnative.so
	cp HALnative.so ..
