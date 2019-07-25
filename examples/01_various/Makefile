FC := gfortran

all: libfortmod.so

libfortmod.so: fortmod.f90
	$(FC) -shared -fPIC -c -o libfortmod.so fortmod.f90

