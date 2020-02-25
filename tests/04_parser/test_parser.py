import os
import pytest
from shutil import copy
from fffi import fortran_module


@pytest.fixture(scope='module')
def tmp(tmp_path_factory):
    return tmp_path_factory.mktemp('parser')


@pytest.fixture(scope='module')
def fort_mod(tmp):
    cwd = os.path.dirname(__file__)
    copy(os.path.join(cwd, 'test_parser.f90'), tmp)
    copy(os.path.join(cwd, 'Makefile'), tmp)
    os.chdir(tmp)
    os.system('make')
    return fortran_module('test_parser', 'test_parser_mod', path=tmp)


def test_scalar_types(fort_mod):
    fort_mod.fdef("""\
        subroutine test_logical(x)
            logical :: x
        end

        subroutine test_integer(x)
            integer :: x
        end

        subroutine test_real(x)
            real :: x
        end

        subroutine test_complex(x)
            complex :: x
        end
        """)

    assert fort_mod.csource