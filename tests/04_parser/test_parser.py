import os
import pytest
from shutil import copy
from fffi import FortranModule

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
    return FortranModule('test_parser', 'test_parser_mod', path=tmp_path)


def test_subroutine(fort_mod):
    fort_mod.fdef("""\
        subroutine test(x)
            real :: x
        end

        subroutine test2(x)
            real :: x
        end subroutine

        subroutine test3(x)
            real :: x
        end subroutine test4

        subroutine test4(x)
            real :: x
        end subroutine

        subroutine test5(x)
            real :: x
        end
    """)
    assert fort_mod.csource


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


def test_comment(fort_mod):
    fort_mod.fdef("""\
        ! Resonant transport regimes in tokamaks
        ! in the action-angle formalism
        ! Christopher Albert, 2015-2017

        integer :: i  ! This is an integer
        """)

    assert fort_mod.csource


def test_use(fort_mod):
    fort_mod.fdef("""\
        subroutine a
            use mod_tets
        end subroutine a
        """)

    assert fort_mod.csource