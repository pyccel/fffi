import os
import pytest
from shutil import copy
from fffi import fortran_module

dtypes = ['logical', 'integer', 'real', 'complex']


@pytest.fixture(scope='module')
def cwd():
    return os.path.dirname(__file__)


@pytest.fixture
def fort_mod(tmp_path, cwd):
    copy(os.path.join(cwd, 'test_parser.f90'), tmp_path)
    copy(os.path.join(cwd, 'Makefile'), tmp_path)
    os.chdir(tmp_path)
    os.system('make')
    return fortran_module('test_parser', 'test_parser_mod', path=tmp_path)


def test_scalar_types(fort_mod):
    for dtype in dtypes:
        fort_mod.fdef("""\
            subroutine test_{0}(x)
                {0} :: x
            end
            """.format(dtype))

    assert fort_mod.csource


def test_scalar_types_kind(fort_mod):
    for dtype in dtypes:
        fort_mod.fdef("""\
            subroutine test_{0}(x)
                {0}(4) :: x
            end
            """.format(dtype))

    assert fort_mod.csource

    # This should throw a KeyError for logical(8) and pass otherwise
    with pytest.raises(KeyError, match=r"('logical', 8)"):
        for dtype in dtypes:
            fort_mod.fdef("""\
                subroutine test_{0}(x)
                    {0}(8) :: x
                end
                """.format(dtype))


def test_array_types(fort_mod):
    for dtype in dtypes:
        fort_mod.fdef("""\
            subroutine test_logical(x, y, z)
                {0} :: x(:)
                {0}, dimension(:) :: y, z
            end
            """.format(dtype))

    assert fort_mod.csource
