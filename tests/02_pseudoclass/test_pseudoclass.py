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
from fffi import fortran_library, fortran_module


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

    lib = fortran_library('pseudoclass', path=tmp)
    classmod = fortran_module(lib, 'class_circle')

    classmod.fdef("""
    type Circle
    double precision :: radius
    end type

    subroutine circle_print(self)
    type(Circle), intent(in) :: self
    end
    """)

    lib.compile()


@pytest.fixture(scope="module")
def lib(tmp):
    return fortran_library('pseudoclass', path=tmp)


@pytest.fixture(scope="module")
def classmod(lib):
    fortmod = fortran_module(lib, 'class_circle')
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
