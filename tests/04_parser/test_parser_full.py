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


def test_full(fort_mod):
    fort_mod.fdef("""\
! Resonant transport regimes in tokamaks
! in the action-angle formalism
! Christopher Albert, 2015-2017

module driftorbit
  use do_magfie_mod
  use do_magfie_pert_mod, only: do_magfie_pert_amp, mph
  !use do_magfie_neo_mod
  !use do_magfie_pert_neo_mod, only: do_magfie_pert_amp, mph
  use collis_alp
  use spline
  
  implicit none
  save

  integer :: nvar
end

    """)
    # assert fort_mod.csource
