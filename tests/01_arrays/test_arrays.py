"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Supposes that test_arrays_compile has already been run
to generate CFFI API interface as a Python extension module
"""

import gc
import os
import subprocess
import tracemalloc
from shutil import copy

import pytest
import numpy as np
from fffi import fortran_module

m = 3
n = 2


@pytest.fixture(scope='module')
def tmp(tmp_path_factory):
    return tmp_path_factory.mktemp('arrays')


@pytest.fixture(scope='module')
def refout(tmp):
    os.chdir(tmp)
    out = subprocess.check_output('./test_arrays.x')
    return out.replace(b' ', b'').split(b'\n\n\n')


@pytest.fixture(scope='module')
def refvec(refout):
    return np.fromstring(refout[0], sep='\n')


@pytest.fixture(scope='module')
def refarr(refout):
    # Reference output for 2D array
    refarrspl = refout[1].split(b'\n\n')  # Fortran column outputs
    ret = np.empty((m, n))

    for kcol in range(n):
        ret[:, kcol] = np.fromstring(refarrspl[kcol], sep='\n')

    return ret


@pytest.fixture(scope='module')
def mod_arrays(tmp):
    # Working directory
    cwd = os.path.dirname(__file__)

    copy(os.path.join(cwd, 'Makefile'), tmp)
    copy(os.path.join(cwd, 'mod_arrays.f90'), tmp)
    copy(os.path.join(cwd, 'test_arrays.f90'), tmp)
    os.mkdir(os.path.join(tmp, 'static'))
    os.mkdir(os.path.join(tmp, 'shared'))

    os.chdir(tmp)
    os.system('make')

    fort_mod = fortran_module('test_arrays', 'mod_arrays', path=tmp)

    fort_mod.fdef("""
        subroutine test_vector(vec)
        double precision, dimension(:) :: vec
        end

        subroutine test_array_2d(arr)
        double precision, dimension(:,:) :: arr
        end
        """)

    fort_mod.compile()

    # recreate module to check if it works independently now
    fort_mod = fortran_module('test_arrays', 'mod_arrays', path=tmp)
    fort_mod.load()
    return fort_mod


def test_vector(mod_arrays, refvec):
    """
    Allocate vector in numpy, apply Fortran routine
    """

    vec = np.ones(15)
    print(vec)
    mod_arrays.test_vector(vec)
    print(vec)
    np.testing.assert_almost_equal(vec, refvec)


def test_array_2d(mod_arrays, refarr):
    """
    Allocate 2D array in numpy, apply Fortran routine
    """

    arr = np.ones((m, n), order='F')  # correct array order
    mod_arrays.test_array_2d(arr)
    np.testing.assert_almost_equal(arr, refarr)


# def test_array_2d_wrongorder(mod_arrays):
#     """
#     Allocate 2D array in numpy in wrong order, apply Fortran routine
#     check if correct exception is thrown
#     """

#     arr = np.ones((m, n), order='C')  # incorrect array order
#     with self.assertRaises(TypeError) as context:
#         self.mod_arrays.test_array_2d(arr)
#     self.assertTrue('needs Fortran order' in str(context.exception))


def test_array_2d_multi(mod_arrays, refarr):
    """
    Allocate 2D array in numpy, apply Fortran routine first 10 times
    then 1000 times. Check for memory leaks via tracemalloc
    """

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    arr = np.ones((m, n), order='F')  # correct array order

    for _ in range(10):
        arr[:, :] = 1.0
        mod_arrays.test_array_2d(arr)
        np.testing.assert_almost_equal(arr, refarr)

    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()

    stats = snapshot2.compare_to(snapshot1, 'filename')
    statsum = sum(stat.count_diff for stat in stats)

    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(1000):
        arr[:, :] = 1.0
        mod_arrays.test_array_2d(arr)
        np.testing.assert_almost_equal(arr, refarr)

    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()

    stats = snapshot2.compare_to(snapshot1, 'filename')
    assert sum(stat.count_diff for stat in stats) <= statsum
