"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Compiles CFF for test_arrays
"""

import os
from shutil import copy, rmtree
from tempfile import mkdtemp
from unittest import TestCase
from fffi import fortran_module


class TestArraysCompile(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.origcwd = os.getcwd()
        cls.cwd = os.path.dirname(__file__)
        cls.tmpdir = mkdtemp()

        copy(os.path.join(cls.cwd, 'Makefile'), cls.tmpdir)
        copy(os.path.join(cls.cwd, 'mod_arrays.f90'), cls.tmpdir)
        copy(os.path.join(cls.cwd, 'test_arrays.f90'), cls.tmpdir)
        os.mkdir(os.path.join(cls.tmpdir, 'static'))
        os.mkdir(os.path.join(cls.tmpdir, 'shared'))

        os.chdir(cls.tmpdir)

        try:
            os.system('make')
        except BaseException:
            os.chdir(cls.origcwd)
            raise

    @classmethod
    def tearDownClass(cls):
        os.system('make clean')
        os.chdir(cls.origcwd)
        rmtree(cls.tmpdir)

    def test_compile(self):
        # Initialize
        mod_arrays = fortran_module('test_arrays', 'mod_arrays',
                                    path=self.tmpdir)

        # This will use fortran_module.fdef instead of cdef in the future.
        # Ideally, the actual Fortran source file would be parsed as an
        # option instead of code containing only the signatures.

        mod_arrays.cdef("""
          void {mod}_test_vector(array_1d *vec);
          void {mod}_test_array_2d(array_2d *arr);
        """)

        mod_arrays.compile(tmpdir=self.tmpdir)

if __name__ == "__main__":
    test = TestArraysCompile()
    test.setUpClass()
    test.test_compile()
    test.tearDownClass()
