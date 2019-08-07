FC := gfortran

all: libpseudoclass.so

libpseudoclass.so: ../../tests/02_pseudoclass/ex02_pseudoclass.f90
	$(FC) -shared -fPIC -c -o libpseudoclass.so ../../tests/02_pseudoclass/ex02_pseudoclass.f90

