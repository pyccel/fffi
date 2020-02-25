FC := gfortran

all: libtest_parser.so

libtest_parser.so: test_parser.o
	$(FC) -shared test_parser.o -o libtest_parser.so

test_parser.o: test_parser.f90
	$(FC) -fPIC -c test_parser.f90 -o test_parser.o

clean:
	rm -f *.o *.mod *.a *.so *.x _*.c
