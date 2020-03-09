"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Compiles CFF for test_arrays
"""

import os
from shutil import copy
from fffi import FortranModule

def test_compile(tmp_path):
    cwd = os.path.dirname(__file__)

    copy(os.path.join(cwd, 'Makefile'), tmp_path)
    copy(os.path.join(cwd, 'mod_arrays.f90'), tmp_path)
    copy(os.path.join(cwd, 'test_arrays.f90'), tmp_path)
    os.mkdir(os.path.join(tmp_path, 'static'))
    os.mkdir(os.path.join(tmp_path, 'shared'))

    os.chdir(tmp_path)
    os.system('make')

    # Initialize
    mod_arrays = FortranModule('test_arrays', 'mod_arrays', path=tmp_path)

    # This will use fortran_module.fdef instead of cdef in the future.
    # Ideally, the actual Fortran source file would be parsed as an
    # option instead of code containing only the signatures.

    mod_arrays.cdef("""
        void {mod}_test_vector(array_1d *vec);
        void {mod}_test_array_2d(array_2d *arr);
    """)

    mod_arrays.compile(tmpdir=tmp_path)
