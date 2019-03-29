#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 14:32:32 2017

@author: Christopher Albert <albert@alumni.tugraz.at>
"""

import numpy as np
from cffi import FFI
from fparser.two.parser import ParserFactory
from fparser.two.utils import walk_ast
from fparser.two.Fortran2003 import (
        Subroutine_Stmt, Dummy_Arg_List, Type_Declaration_Stmt,
        Entity_Decl, Name, Intrinsic_Type_Spec, Entity_Decl
        )
from fparser.common.readfortran import FortranStringReader
                                     
def debug(output):
    print(output)
    
f2003_parser = ParserFactory().create(std="f2003")

class fortran_module:
    def __init__(self, library, name):
        self.library = library
        self.name = name
        self.methods = dict()

    def __dir__(self):
        return self.methods
    
    def __getattr__(self, attr):
        # print(attr)
        def method(*args): return self.__call_fortran(attr, *args)
        return method

    def __call_fortran(self, function, *args):
        func_name = '__{}_MOD_{}'.format(self.name, function)
        debug('Calling {}{}'.format(func_name, args))

def fdef(fortmod, fcode):
    pass
   