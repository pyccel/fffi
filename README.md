`fffi` is a tool to transparently use shared libraries generated by Fortran in
Python with NumPy arrays. It is based on CFFI and assumes the use of gfortran.

The philosophy of `fffi` differs from `F2PY` in the sense that no rewriting or
recompilation of Fortran code should be required. Practical and intuitive
usability with a minimum of effort by the user is the top priority. The common
case required by a majority of codes shall have the simplest possible usage.
The use of ISO-C bindings will remain optional if guaranteed safety is required.
Otherwise `fffi` relies on the convention that Fortran subroutines pass
arguments by reference as pointers, as realized at least by gfortran and Intel.


Basic usage using CFFI (fast) API mode with shared library
`libtest_arrays.so` containing module `mod_arrays`:
1. Import fffi and initialize `fortran_module` object `mod_arrays`
```
from fffi import fortran_module
mod_arrays = fortran_module('test_arrays', 'mod_arrays')
```

2. Define and generate Python extension
  (only on first run or if library routines have been added/changed)
```
mod_arrays.cdef("""
      void {mod}_test_vector(array_1d *vec);
      void {mod}_test_array_2d(array_2d *arr);
    """)
mod_arrays.compile()
```
Here `array_Nd` structs are defined as an ad-hoc representation for internal
array descriptors of Fortran compilers.
3. Load interface module to library
```
  mod_arrays.load()
```
4. Calling of a subroutine `test_vector` in `mod_arrays` is as simple as
```
  vec = np.ones(15)
  mod_arrays.test_vector(vec)
```

This example can be found and extended based on the `tests/01_arrays` directory.

1. Possibly add new testing routines to `mod_arrays.f90` and `test_arrays.f90`
2. Run `make`. This generates a shared library `libtest_arrays.so` and
   a Fortran executable `test_arrays.x` for reference output
3. Edit and run `test_arrays.py`

Current status:

* Code generation and invocation is transparent by encapsulation in Python class
* CFFI API mode is used (pre-generate C extension module as a wrapper)
* Subroutine signatures are defined via C equivalent in CFFI cdef
* Array descriptor structs are working with gfortran 7.3
* First tests to define signatures directly in Fortran syntax via Fortran parser

Next steps:

* Check synergies with https://github.com/DLR-SC/F2x
* Add flexibility with regard to types, floating-point precision, etc.
* Allow subroutine signature definition in Fortran (`fdef` instead of `cdef`)
* Allow for ABI mode in addition to API mode, and static library API mode
* Add support for Intel and PGI in addition to GNU Fortran compiler
* Test in real world applications
