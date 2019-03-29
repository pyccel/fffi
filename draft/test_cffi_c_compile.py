"""
Created: Mon Mar 18 08:59:15 2019
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

from cffi import FFI

ffi = FFI()
ffi.set_source('_testext',
                      r'',
                      libraries=['testlib'],
                      library_dirs=['.'],
                      extra_link_args=['-Wl,-rpath=.'])
                      

ffi.cdef("""
int libfunc(float f);
""")

ffi.compile(verbose=True)
