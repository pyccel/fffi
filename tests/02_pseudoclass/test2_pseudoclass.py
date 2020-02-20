"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Supposes that test_arrays_compile has already been run
to generate CFFI API interface as a Python extension module
"""

import os

from unittest import TestCase

import numpy as np
from fffi import fortran_library, fortran_module


class TestPseudoClass(TestCase):

    @classmethod
    def setUpClass(cls):
        # Working directory
        cls.origcwd = os.getcwd()
        cls.cwd = os.path.dirname(__file__)
        os.chdir(cls.cwd)

        try:
            os.system('make clean && make')

            cls.lib = fortran_library('pseudoclass', path=cls.cwd)
            classmod = fortran_module(cls.lib, 'class_circle')

            classmod.fdef("""
            type Circle
            double precision :: radius
            end type

            subroutine circle_print(self)
            type(Circle), intent(in) :: self
            end
            """)

            cls.lib.compile()

            # recreate module to check if it works independently now
            cls.lib = fortran_library('pseudoclass', path=cls.cwd)
            cls.classmod = fortran_module(cls.lib, 'class_circle')
            cls.classmod.load()
        except BaseException:
            os.chdir(cls.origcwd)
            raise

    @classmethod
    def tearDownClass(cls):
        os.system('make clean')
        os.chdir(cls.origcwd)

    def test_new(self):
        cir = self.classmod.new('Circle')
        assert(self.lib._ffi.typeof(cir) ==
               self.lib._ffi.typeof('struct Circle *'))

    def test_set(self):
        cir = self.classmod.new('Circle')
        cir.radius = 5.0
        assert np.equal(cir.radius, 5.0)


if __name__ == "__main__":
    test = TestPseudoClass()
    test.setUpClass()
