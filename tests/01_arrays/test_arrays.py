"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import numpy as np
import subprocess

from fffi import fortran_module

docompile = False

mod_arrays = fortran_module('test_arrays', 'mod_arrays')

if docompile:
    # This will use fortran_module.fdef instead of cdef in the future.
    # Ideally, the actual Fortran source code will be parsed optionally
    # instead of code containing only the signatures.
    #
    # with open('mod_arrays_sig.f90') as sigfile:
    #     fsource = sigfile.read()
    # mod_arrays.fdef(fsource)

    with open('mod_arrays_sig.c') as sigfile:
        csource = sigfile.read()
    mod_arrays.cdef(csource)

    mod_arrays.compile(verbose=True)

ref_out = subprocess.check_output('./test_arrays.x', shell=True)

mod_arrays.load()


print('')
print('----------------------------------------------------------------------')
print('Test 1: Allocate vector in numpy, apply Fortran routine')
print('----------------------------------------------------------------------')

vec = np.ones(10)
mod_arrays.test_vector(vec)
print(vec)


print('')
print('----------------------------------------------------------------------')
print('Test 2: Allocate 2D array in numpy, apply Fortran routine')
print('----------------------------------------------------------------------')

m = 3
n = 2

arr = np.ones((m,n), order='F')
mod_arrays.test_array_2d(arr)
print(arr)
