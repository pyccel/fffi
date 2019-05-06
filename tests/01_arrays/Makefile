FC := gfortran

all: test_arrays.x libtest_arrays.so libtest_arrays.a

test_arrays.x: test_arrays.f90 static/mod_arrays.o
	$(FC) -I static/ test_arrays.f90 static/mod_arrays.o -o test_arrays.x

libtest_arrays.so: shared/mod_arrays.o
	$(FC) -shared shared/mod_arrays.o -o libtest_arrays.so

libtest_arrays.a: static/mod_arrays.o
	ar rcs libtest_arrays.a static/mod_arrays.o

shared/mod_arrays.o: mod_arrays.f90
	$(FC) -fPIC -c -J shared/ -o shared/mod_arrays.o mod_arrays.f90

static/mod_arrays.o: mod_arrays.f90
	$(FC) -c -J static/ -o static/mod_arrays.o mod_arrays.f90

clean:
	rm -f static/* shared/* *.o *.a *.so *.x
