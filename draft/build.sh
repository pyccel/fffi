#!/bin/sh
#
# Create the object files for the static library (without -fPIC)
#
gcc -c       testlib.c    -o static/testlib.o
gfortran -c  testfort.f90 -o static/testfort.o
ar rcs libtestlib.a static/testlib.o
ar rcs libtestfort.a static/testfort.o

#
# object files for shared libraries need to be compiled as position independent
# code (-fPIC) because they are mapped to any position in the address space.
#
gcc -fPIC -c testlib.c    -o shared/testlib.o
gfortran -fPIC -c  testfort.f90 -o shared/testfort.o
gcc -shared shared/testlib.o -o libtestlib.so
gcc -shared shared/testfort.o -o libtestfort.so

