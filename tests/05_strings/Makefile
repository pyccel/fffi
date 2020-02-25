FC := gfortran

all: test_strings.x libtest_strings.so

test_strings.x: test_strings.f90
	$(FC) test_strings.f90 -o test_strings.x

libtest_strings.so: test_strings.f90
	$(FC) -fPIC -shared test_strings.f90 -o libtest_strings.so

clean:
	rm -f static/* shared/* *.o *.mod *.a *.so *.x _*.c
