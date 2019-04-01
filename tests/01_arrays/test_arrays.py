"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import numpy as np
import subprocess
import sys

import gc
import tracemalloc

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

# Reference output for vector
refspl = ref_out.split(b'\n\n\n')
refvec = np.fromstring(refspl[0], sep='\n')

# Reference output for 2D array
m = 3  # rows
n = 2  # columns
refarrspl = refspl[1].split(b'\n\n') # single column output from Fortran
refarr = np.empty((m,n))

for kcol in range(n):
    refarr[:,kcol] = np.fromstring(refarrspl[kcol], sep='\n')
#%%

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# Load module
mod_arrays.load()

print('')
print('Test 1: Allocate vector in numpy, apply Fortran routine')

vec = np.ones(15)
mod_arrays.test_vector(vec)
print(vec)
np.testing.assert_almost_equal(vec, refvec)


print('')
print('Test 2: Allocate 2D array in numpy, apply Fortran routine')

arr = np.ones((m,n), order='F') # important: array order 'F' for Fortran
mod_arrays.test_array_2d(arr)
print(arr)
np.testing.assert_almost_equal(arr, refarr)


print('')
print('Test 3: Allocate 2D array in numpy, apply Fortran routine 1e5 times')

arr = np.ones((m,n), order='F') # important: array order 'F' for Fortran

for k in range(10000):
    arr[:,:] = 1.0
    mod_arrays.test_array_2d(arr)
    np.testing.assert_almost_equal(arr, refarr)
    
gc.collect()
snapshot2 = tracemalloc.take_snapshot()

top_stats = snapshot2.compare_to(snapshot1, 'lineno')

print('[ Tracemalloc top 10 differences ]')
for stat in top_stats[:10]:
    print(stat)
