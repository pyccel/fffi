"""
Created: Mon Mar 18 08:59:15 2019
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

from cffi import FFI

ffi = FFI()

structdef = """
  struct descr_dims {
    ptrdiff_t stride;
    ptrdiff_t lower_bound;
    ptrdiff_t upper_bound;
  };

  struct descr {
    void *base_addr;
    size_t offset;
    ptrdiff_t dtype;
    struct descr_dims dim[1]; // TODO: make this dynamic
  };
"""

            
ffi.cdef(structdef + """
  void __testfort_MOD_test_vector(struct descr *vecdata);
  struct descr * __testfort_MOD_test_alloc_vector();
""")

ffi.set_source('_testfort',
               structdef,
               libraries=['testfort'],
               library_dirs=['.'],
               extra_link_args=['-Wl,-rpath=.','-lgfortran'])


ffi.compile(verbose=True)

from importlib import reload 
import numpy as np
import _testfort

_testfort = reload(_testfort)

testfort = _testfort.lib
ffi = _testfort.ffi

vec = np.ones(10)
print(vec)

vecdata = ffi.new('struct descr*')
vecdata.offset = 0
vecdata.dim[0].stride = 1
vecdata.dim[0].lower_bound = 1
vecdata.dim[0].upper_bound = len(vec)
vecdata.dtype = 2
vecdata.dtype = vecdata.dtype | (3 << 3)
vecdata.dtype = vecdata.dtype | (8 << 6)
vecdata.base_addr = ffi.cast('void*', vec.ctypes.data)
testfort.__testfort_MOD_test_vector(vecdata)

print(vec)
#testfort.__testfort_MOD_test_alloc_vector()
#vecdata2 = testfort.__testfort_MOD_test_alloc_vector()

#print(vecdata2)
