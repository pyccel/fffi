The goal of fffi is to be able to transparently use shared libraries generated
by Fortran within Python.

First tests can be made based on the `tests/01_arrays` directory:

1. Possibly add new testing routines to `mod_arrays.f90` and `test_arrays.f90`
2. Run `make`. This should generate a shared library `libtest_arrays.so` and
   a Fortran executable `test_arrays.x` for reference output
3. Edit and run `test_arrays.py` which uses the (faster) API mode of CFFI to
   generate a Python extension module

Current status:

* Code generation and invocation is transparent by encapsulation in Python class
* Subroutine signatures are right now defined via C equivalent in CFFI cdef
* Array descriptor structs are working with gfortran 7.3
* First tests to define signatures directly in Fortran syntax via Fortran parser

Next steps:

* Check synergies with https://github.com/DLR-SC/F2x
* Simplify / auto-import subroutine signature generation
* Allow for ABI mode in addition to API mode
* Test in real world applications
