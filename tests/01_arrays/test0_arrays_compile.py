"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Compiles CFF for test_arrays
"""

import numpy as np
import inspect
import os

from unittest import TestCase

from fffi import fortran_module

class TestArraysCompile(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.origcwd = os.getcwd()
        cls.cwd = os.path.dirname(inspect.getfile(inspect.currentframe()))
        os.chdir(cls.cwd)

        try:
            os.system('make clean && make')
        except:
            os.chdir(cls.origcwd)
            raise


    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.origcwd)


    def test_compile(self):
        # Initialize
        mod_arrays = fortran_module('test_arrays', 'mod_arrays')

        # This will use fortran_module.fdef instead of cdef in the future.
        # Ideally, the actual Fortran source file would be parsed as an option
        # instead of code containing only the signatures.

        mod_arrays.cdef("""
          void {mod}_test_vector(array_1d *vec);
          void {mod}_test_array_2d(array_2d *arr);
        """)

        mod_arrays.compile(verbose=False)
