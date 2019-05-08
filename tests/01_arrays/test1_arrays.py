"""
Created: 2019-04-01
@author: Christopher Albert <albert@alumni.tugraz.at>

Supposes that test_arrays_compile has already been run
to generate CFFI API interface as a Python extension module
"""

import numpy as np
import gc
import os
import subprocess
import tracemalloc

from unittest import TestCase

from fffi import fortran_module


class TestArrays(TestCase):
    m = 3
    n = 2

    @classmethod
    def setUpClass(cls):
        # Working directory
        cls.origcwd = os.getcwd()
        cls.cwd = os.path.dirname(__file__)
        os.chdir(cls.cwd)

        try:
            os.system('make clean && make')
            
            # Reference output
            ref_out = subprocess.check_output('./test_arrays.x')

            # Reference output for vector
            refspl = ref_out.replace(b' ',b'').split(b'\n\n\n')
            cls.refvec = np.fromstring(refspl[0], sep='\n')

            # Reference output for 2D array
            refarrspl = refspl[1].split(b'\n\n')  # Fortran column outputs
            cls.refarr = np.empty((cls.m, cls.n))

            for kcol in range(cls.n):
                cls.refarr[:, kcol] = np.fromstring(refarrspl[kcol], sep='\n')

            mod_arrays = fortran_module('test_arrays', 'mod_arrays',
                                        path=cls.cwd)
            mod_arrays.cdef("""
              void {mod}_test_vector_(array_1d *vec);
              void {mod}_test_array_2d_(array_2d *arr);
            """)
            mod_arrays.compile()

            # recreate module to check if it works independently now
            cls.mod_arrays = fortran_module('test_arrays', 'mod_arrays',
                                            path=cls.cwd)
            cls.mod_arrays.load()
        except BaseException:
            os.chdir(cls.origcwd)
            raise

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.origcwd)

    def test_vector(self):
        """
        Allocate vector in numpy, apply Fortran routine
        """

        vec = np.ones(15)
        print(vec)
        self.mod_arrays.test_vector(vec)
        print(vec)
        np.testing.assert_almost_equal(vec, self.refvec)

    def test_array_2d(self):
        """
        Allocate 2D array in numpy, apply Fortran routine
        """

        arr = np.ones((self.m, self.n), order='F')  # correct array order
        self.mod_arrays.test_array_2d(arr)
        np.testing.assert_almost_equal(arr, self.refarr)

    def test_array_2d_wrongorder(self):
        """
        Allocate 2D array in numpy in wrong order, apply Fortran routine
        check if correct exception is thrown
        """

        arr = np.ones((self.m, self.n), order='C')  # incorrect array order
        with self.assertRaises(TypeError) as context:
            self.mod_arrays.test_array_2d(arr)
        self.assertTrue('needs Fortran order' in str(context.exception))

    def test_array_2d_multi(self):
        """
        Allocate 2D array in numpy, apply Fortran routine first 10 times
        then 1000 times. Check for memory leaks via tracemalloc
        """

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        arr = np.ones((self.m, self.n), order='F')  # correct array order

        for k in range(10):
            arr[:, :] = 1.0
            self.mod_arrays.test_array_2d(arr)
            np.testing.assert_almost_equal(arr, self.refarr)

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()

        stats = snapshot2.compare_to(snapshot1, 'filename')
        statsum = sum(stat.count_diff for stat in stats)

        snapshot1 = tracemalloc.take_snapshot()
        for k in range(1000):
            arr[:, :] = 1.0
            self.mod_arrays.test_array_2d(arr)
            np.testing.assert_almost_equal(arr, self.refarr)

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()

        stats = snapshot2.compare_to(snapshot1, 'filename')
        self.assertLessEqual(sum(stat.count_diff for stat in stats), statsum)


if __name__ == "__main__":
    test = TestArrays()
    test.setUpClass()