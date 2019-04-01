"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import numpy as np
import subprocess
import sys

try:
    from fffi import fortran_module
except:
    sys.path.append('../../')
    from fffi import fortran_module

docompile = True

# Initialize
mod_arrays = fortran_module('test_arrays', 'mod_arrays')

# Optionally compile module
if docompile:
    # This will use fortran_module.fdef instead of cdef in the future.
    # Ideally, the actual Fortran source file would be parsed as an option
    # instead of code containing only the signatures.

    mod_arrays.cdef("""
      void {mod}_test_vector(array_1d *vec);
      void {mod}_test_array_2d(array_2d *arr);
    """)

    mod_arrays.compile(verbose=True)

ref_out = subprocess.check_output('./test_arrays.x', shell=True)

# Load module
mod_arrays.load()

print('')
print('Test 1: Allocate vector in numpy, apply Fortran routine')

vec = np.ones(10)
mod_arrays.test_vector(vec)
print(vec)


print('')
print('Test 2: Allocate 2D array in numpy, apply Fortran routine')

m = 3
n = 2

arr = np.ones((m,n), order='F') # important: array order 'F' for Fortran
mod_arrays.test_array_2d(arr)
print(arr)
