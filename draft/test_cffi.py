# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 19:00:57 2018

@author: chral
"""

from cffi import FFI
import numpy as np
from fparser.two.parser import ParserFactory
from fparser.two.utils import walk_ast
from fparser.two.Fortran2003 import (
        Subroutine_Stmt, Dummy_Arg_List, Type_Declaration_Stmt,
        Entity_Decl, Name, Intrinsic_Type_Spec, Entity_Decl,
        Explicit_Shape_Spec
        )

ffi = FFI()
libuq = ffi.dlopen('/home/calbert/code/uqp/libuq.so')
#libuq = ffi.dlopen('/Users/ert/code/uqp/libuq.so')

#%%
from fffi import fortran_module, fdef, f2003_parser, debug
from fparser.common.readfortran import FortranStringReader

mod_index = fortran_module(libuq, 'mod_index')

code = """
subroutine test(nfterme, npterme, np, mmax)
      integer, dimension(0:np) :: jterme, jtermo
      integer :: jterme2(0:np), jterme3(4)
      integer nfterme, npterme, mmax
      integer np
end subroutine
"""

fortmod = mod_index
fcode = code

tree = f2003_parser(FortranStringReader(fcode))
func = walk_ast(tree.content, [Subroutine_Stmt])[0]
arglist = walk_ast(func.items, [Dummy_Arg_List])[0]
args = [a.string for a in arglist.items]

"""
Possiblilities:
  * dtype :: varname
  * dtype :: varname(dim)
  * dtype :: var1name(dim1), var2name(dim2)
  * dtype, dimension(dim) :: varname
  * dtype, dimension(dim) :: var1name, var2name
"""


typelist = walk_ast(tree.content, [Type_Declaration_Stmt])
for typestmt in typelist:
    entlist = walk_ast(typestmt.items, [Entity_Decl])
    ents = [n.items[0].string for n in entlist]
    dtype = walk_ast(typestmt.items,  [Intrinsic_Type_Spec])[0].string
    shapelist = walk_ast(typestmt.items, [Explicit_Shape_Spec])
    if shapelist:
        # do array processing...
        debug('---------------')
        debug('ARRAY:')
        debug('---------------')
        debug(shapelist)
    else:
        # do scalar processing...
        debug('---------------')
        debug('SCALAR:')
        debug('---------------')
    
    debug(ents)
        
    debug(dtype)
    #debug(typestmt.items)
    
    debug('')
    debug('')
    
fortmod.methods[func.get_name().string] = args

#%%

ffi.cdef("""
void __mod_index_MOD_number_of_terms(
  int *nfterme, int *npterme, int *npoly, int *npar, int *jterme);
void __mod_index_MOD_test(
  int *nfterme, int *npterme, int *npoly, int *npar);
""")

#%%

npoly = np.array(3)
nfterme = np.array(1)
npterme = np.array(1)
npar = np.array(2)
jterme = np.zeros(npoly+1, dtype=np.int32)

libuq.__mod_index_MOD_number_of_terms(ffi.cast('int*', nfterme.ctypes.data),
                                  ffi.cast('int*', npterme.ctypes.data), 
                                  ffi.cast('int*', npoly.ctypes.data), 
                                  ffi.cast('int*', npar.ctypes.data), 
                                  ffi.cast('int*', jterme.ctypes.data))

print(jterme)

#%%
ffi.dlclose(libuq)
