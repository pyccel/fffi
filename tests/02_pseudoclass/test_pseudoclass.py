"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Supposes that test_arrays_compile has already been run
to generate CFFI API interface as a Python extension module
"""

import os
from shutil import copy

import pytest
import numpy as np
from fffi import FortranLibrary, FortranModule
from fffi.fortran_wrapper import fortran2numpy


@pytest.fixture(scope='module')
def tmp(tmp_path_factory):
    return tmp_path_factory.mktemp('pseudoclass')


@pytest.fixture(scope='module', autouse=True)
def setup(tmp):
    # Working directory
    cwd = os.path.dirname(__file__)

    copy(os.path.join(cwd, 'Makefile'), tmp)
    copy(os.path.join(cwd, 'ex02_pseudoclass.f90'), tmp)

    os.chdir(tmp)
    os.system('make')

    lib = FortranLibrary('pseudoclass', path=tmp)
    classmod = FortranModule(lib, 'class_circle')

    classmod.fdef("""
    type Circle
      double precision :: radius
      complex(8), dimension(:), allocatable :: alloc_array
    end type

    subroutine circle_print(self)
      type(Circle), intent(in) :: self
    end subroutine

    subroutine circle_alloc_member(self)
      type(Circle), intent(inout) :: self
    end subroutine
    """)

    lib.compile()


@pytest.fixture(scope="module")
def lib(tmp):
    return FortranLibrary('pseudoclass', path=tmp)


@pytest.fixture(scope="module")
def classmod(lib):
    fortmod = FortranModule(lib, 'class_circle')
    fortmod.load()
    return fortmod


def test_new(classmod, lib):
    cir = classmod.new('Circle')
    assert(lib._ffi.typeof(cir) ==
           lib._ffi.typeof('struct Circle *'))


def test_set(classmod):
    cir = classmod.new('Circle')
    cir.radius = 5.0
    assert np.equal(cir.radius, 5.0)


def test_alloc(classmod):
    cir = classmod.new('Circle')
    # TODO: cir.alloc_member() should work
    classmod.circle_alloc_member(cir)
    ref = (1.0+2.0j)*np.ones(5, dtype='c16')
    # TODO: cir.alloc_array should directly give np.array
    test = fortran2numpy(classmod.lib._ffi, cir.alloc_array)
    assert np.allclose(test, ref)
