"""
Created: 2020-02
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import os
import subprocess
from shutil import copy

import pytest
from fffi import FortranLibrary

m = 3
n = 2


@pytest.fixture(scope='module')
def tmp(tmp_path_factory):
    return tmp_path_factory.mktemp('strings')

@pytest.fixture(scope='module')
def refout(tmp):
    os.chdir(tmp)
    out = subprocess.check_output('./test_strings.x')
    return out

@pytest.fixture(scope='module')
def lib(tmp):
    cwd = os.path.dirname(__file__)

    copy(os.path.join(cwd, 'Makefile'), tmp)
    copy(os.path.join(cwd, 'test_strings.f90'), tmp)

    os.chdir(tmp)
    os.system('make')

    fort_lib = FortranLibrary('test_strings', path=tmp)

    fort_lib.fdef("""
        subroutine test_string(s)
            character(len=*), intent(in) :: s
        end subroutine test_string
        """)

    fort_lib.compile()
    fort_lib.load()
    return fort_lib


def test_string(lib, refout):
    """
    Call subroutine with string argument
    """

    lib.test_string('Hello, Fortran!')
