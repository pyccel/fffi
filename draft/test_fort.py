"""
Created: Mon Mar 18 08:59:15 2019
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import numpy as np
from cffi import FFI
from fffi import numpy2fortran, arraydims, arraydescr

docompile = True

if (docompile):
    structdef = arraydims + arraydescr.format(1) + arraydescr.format(2)

    ffi = FFI()
    ffi.cdef(structdef + """
      void __testfort_MOD_test_vector(array_1d *vec);
      void __testfort_MOD_test_array_2d(array_2d *arr);
      void __testfort_MOD_ones_1d(array_1d *vec, int *n);
      void __testfort_MOD_ones_2d(array_2d *arr, int *m, int *n);
    """)

    ffi.set_source('_testfort',
                   structdef,
                   libraries=['testfort'],
                   library_dirs=['.'],
                   extra_link_args=['-Wl,-rpath=.','-lgfortran'])

    ffi.compile(verbose=True)

#%%

import _testfort

testfort = _testfort.lib
ffi = _testfort.ffi

#%%
print('')
print('----------------------------------------------------------------------')
print('Test 1: Allocate vector in numpy, apply Fortran routine')
print('----------------------------------------------------------------------')

vec = np.ones(10)
vecdata = numpy2fortran(ffi, vec)
testfort.__testfort_MOD_test_vector(vecdata)
print(vec)

#%%
print('')
print('----------------------------------------------------------------------')
print('Test 2: Allocate vector in Fortran, apply Fortran routine')
print('----------------------------------------------------------------------')

vecdata2 = ffi.new('array_1d*')
intdata = ffi.new('int*', 15)

testfort.__testfort_MOD_ones_1d(vecdata2, intdata)
buf = ffi.buffer(vecdata2.base_addr, 8*vecdata2.dim[0].upper_bound)
testfort.__testfort_MOD_test_vector(vecdata2)
vec2 = np.frombuffer(buf, np.float64)

print(vec2)

#%%
print('')
print('----------------------------------------------------------------------')
print('Test 3: Allocate 2D array in numpy, apply Fortran routine')
print('----------------------------------------------------------------------')

m = 3
n = 2

arr = np.ones((m,n), order='F')
arrdata = numpy2fortran(ffi, arr)
testfort.__testfort_MOD_test_array_2d(arrdata)
print(arr)

#%%
print('')
print('----------------------------------------------------------------------')
print('Test 4: Allocate 2D array in Fortran, apply Fortran routine')
print('----------------------------------------------------------------------')

arrdata = ffi.new('array_2d*')
mdata = ffi.new('int*', 3)
ndata = ffi.new('int*', 2)
testfort.__testfort_MOD_ones_2d(arrdata, mdata, ndata)
testfort.__testfort_MOD_test_array_2d(arrdata)
m = arrdata.dim[0].upper_bound
n = arrdata.dim[1].upper_bound
buf = ffi.buffer(arrdata.base_addr, 8*m*n)

addr = int(ffi.cast('int', arrdata.base_addr))
arrvec = np.frombuffer(buf, np.float64)
assert(addr == arrvec.ctypes.data)
arr = arrvec.view()
assert(addr == arr.ctypes.data)
arr.shape = (n,m)
arr = arr.T
assert(addr == arr.ctypes.data)
print('Flat data:\n', arrvec)
print('Array data:\n', arr)
