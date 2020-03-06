FC := gfortran

ifeq ($(OS), Windows_NT)
    LIBEXT := dll
else
	LIBEXT := so
endif

all: libtest_parser.$(LIBEXT)

libtest_parser.$(LIBEXT): test_parser.o
	$(FC) -shared test_parser.o -o libtest_parser.$(LIBEXT)

test_parser.o: test_parser.f90
	$(FC) -fPIC -c test_parser.f90 -o test_parser.o

clean:
	rm -f *.o *.mod *.a *.$(LIBEXT) *.x _*.c
