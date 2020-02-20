FC := gfortran

all: libpseudoclass.so

libpseudoclass.so: pseudoclass.o
	$(FC) -shared pseudoclass.o -o libpseudoclass.so

pseudoclass.o: ex02_pseudoclass.f90
	$(FC) -fPIC -c ex02_pseudoclass.f90 -o pseudoclass.o

clean:
	rm -f *.o *.mod *.a *.so *.x _*.c
