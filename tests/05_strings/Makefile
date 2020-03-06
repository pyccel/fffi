FC := gfortran

ifeq ($(OS), Windows_NT)
    LIBEXT := dll
else
	LIBEXT := so
endif

all: test_strings.x libtest_strings.so

test_strings.x: test_strings.f90
	$(FC) test_strings.f90 -o test_strings.x

libtest_strings.$(LIBEXT): test_strings.f90
	$(FC) -fPIC -shared test_strings.f90 -o libtest_strings.$(LIBEXT)

clean:
	rm -f static/* shared/* *.o *.mod *.a *.$(LIBEXT) *.x _*.c
