OBJS=glove.o
CC=gcc
CPP=g++

glove.o: glove.cpp
	$(CC) -c -fPIC glove.cpp -o glove.o

mac: $(OBJS)
	$(CPP) -dynamiclib $(OBJS) -L. fglove.dylib -o glove.so

linux: $(OBJS)
	$(CPP) -L. -shared -Wl,-soname,glove.so -o glove.so $(OBJS) -lfglove
