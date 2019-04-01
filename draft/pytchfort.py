#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 14:32:32 2017

@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import numpy as np
from ctypes import POINTER, c_double, c_int, byref
# from _ctypes import _SimpleCData


class fortran_module:
    def __init__(self, library, name):
        self.library = library
        self.name = name

    def __getattr__(self, attr):
        # print(attr)
        def method(*args): return self.__call_fortran(attr, *args)
        return method

    def __call_fortran(self, function, *args):
        func_name = '__{}_MOD_{}'.format(self.name, function)
        # print(routine_name)
        func = getattr(self.library, func_name)
        if(len(args) == 0):
            return func()

        fort_args = list()
        ka = 0
        for arg in args:
            # print(type(arg))
            if (ka == 0 and isinstance(arg, object)
                    and arg.__class__.__name__ == 'PyCSimpleType'):
                return self.__var_fortran(function, *args)
            if isinstance(arg, int):
                fort_arg = byref(c_int(arg))
            elif isinstance(arg, float):
                fort_arg = byref(c_double(arg))
            else:
                print(type(arg))
                print(arg.__class__.__name__)
                print(arg.__name__)
                raise NotImplementedError
            fort_args.append(fort_arg)
            ka = ka+1

        if (len(args) == 1):
            return func(fort_args[0])

    def __var_fortran(self, function, *args):
        if(len(args) > 2):
            raise RuntimeError

        dtype = args[0]

        if(len(args) == 1):
            return dtype.in_dll(self.library, '__{}_MOD_{}'.format(self.name,
                                function))

        if(isinstance(args[1], int)):
            shape = (args[1], 1)
        elif(isinstance(args[1], list)):
            shape = args[1]
        else:
            raise RuntimeError

        return np.ctypeslib.as_array(POINTER(dtype).in_dll(
                self.library, '__{}_MOD_{}'.format(
                    self.name, function)), shape)[:, 0]
