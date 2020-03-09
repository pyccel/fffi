# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 19:00:57 2018

@author: chral
"""

from ctypes import CDLL, byref, POINTER, c_double, c_int, c_long, c_short
import numpy as np


libpath = '/home/calbert/code/uqp/libuq.so'
lib = CDLL(libpath)
#%%
from fffi import FortranModule

modname = 'mod_index'

mod_index = FortranModule(lib, 'mod_index')


npoly = c_int(3)
nfterme = c_int(0)
npterme = c_int(0)
npar = c_int(2)
jterme = np.zeros(4, dtype=np.int32)

func_name = '__{}_MOD_{}'.format(modname, 'number_of_terms')
print(func_name)
func = getattr(lib, func_name)

func(byref(nfterme), byref(npterme), byref(npoly), byref(npar), jterme.ctypes.data_as(POINTER(c_int)))

print(jterme)
