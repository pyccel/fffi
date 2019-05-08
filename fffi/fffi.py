#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 14:32:32 2017

@author: Christopher Albert <albert@alumni.tugraz.at>
"""
import importlib
import inspect
import os
import re
import sys
import numpy as np
from cffi import FFI

from .parser import parse

log_warn = True
log_debug = True

def arraydims(compiler, compiler_version):
    if compiler == 'gnu':
        if compiler_version >= 8:
            return """
              typedef struct array_dims array_dims;
              struct array_dims {
                ptrdiff_t stride;
                ptrdiff_t lower_bound;
                ptrdiff_t upper_bound;
              };
              
              typedef struct datatype datatype;
              struct datatype {
                size_t len;
                int ver;
                signed char rank;
                signed char type;
                signed short attribute;
              };
            """
        else:
            return """
              typedef struct array_dims array_dims;
              struct array_dims {
                ptrdiff_t stride;
                ptrdiff_t lower_bound;
                ptrdiff_t upper_bound;
              };
            """
    elif compiler == 'intel':
            return """
              typedef struct array_dims array_dims;
              struct array_dims {
                uintptr_t upper_bound;
                uintptr_t stride;
                uintptr_t lower_bound;
              };
            """
    else:
        raise NotImplementedError(
                'Compiler {} not supported. Use gnu or intel'.format(compiler))
        
def arraydescr(compiler, compiler_version):
    if compiler == 'gnu':
        if compiler_version >= 8:
            return """
              typedef struct array_{0}d array_{0}d;
              struct array_{0}d {{
                void *base_addr;
                size_t offset;
                datatype dtype;
                ptrdiff_t span;
                struct array_dims dim[{0}];
              }};
            """
        else:
            return """     
              typedef struct array_{0}d array_{0}d;
              struct array_{0}d {{
                void *base_addr;
                size_t offset;
                ptrdiff_t dtype;
                struct array_dims dim[{0}];
              }};
            """
    elif compiler == 'intel':
            return """     
              typedef struct array_{0}d array_{0}d;
              struct array_{0}d {{
                void *base_addr;
                uintptr_t elem_size;
                uintptr_t reserved;
                uintptr_t info;
                uintptr_t rank;
                uintptr_t reserved2;
                struct array_dims dim[{0}];
              }};
            """
    else:
        raise NotImplementedError(
                'Compiler {} not supported. Use gnu or intel'.format(compiler))
    
    
ctypemap = {
            ('int', 1): 'int8_t',
            ('int', 2): 'int16_t',
            ('int', 4): 'int32_t',
            ('int', 8): 'int64_t',
            ('real', 4): 'float',
            ('real', 8): 'double'
        }

def ccodegen(subprogram):
    cargs = []
    for arg in subprogram.args:
        attrs = subprogram.namespace[arg]
        dtype = attrs.dtype
        rank = attrs.rank
        precision = attrs.precision
        debug('{} rank={} bytes={}'.format(dtype, rank, precision))
        
        ctypename = None
        
        if rank == 0:
            ctypename = ctypemap[(dtype, precision)]
        else:
            ctypename = 'array_{}d'.format(rank)
            
        if ctypename == None:
            raise NotImplementedError('{} rank={}'.format(dtype, rank))
            
        cargs.append('{} *{}'.format(ctypename, arg))
                
    csource = 'void {{mod}}_{}({});\n'.format(subprogram.name, ','.join(cargs))
    return csource


def numpy2fortran(ffi, arr, compiler, compiler_version):
    """
    Converts Fortran-contiguous NumPy array arr into an array descriptor
    compatible with gfortran to be passed to library routines via cffi.
    """
    if not arr.flags.f_contiguous:
        raise TypeError('needs Fortran order in NumPy arrays')

    ndims = len(arr.shape)
    arrdata = ffi.new('array_{}d*'.format(ndims))
    arrdata.base_addr = ffi.cast('void*', arr.ctypes.data)
    if compiler == 'gnu':
        arrdata.offset = 0
        if compiler_version >= 8:
            arrdata.span = np.size(arr)*arr.dtype.itemsize
            arrdata.dtype.len = arr.dtype.itemsize
            arrdata.dtype.rank = ndims
            arrdata.dtype.type = 3 # "3" for float, TODO:others
            arrdata.dtype.attribute = 0
        else:
            arrdata.dtype = ndims  # rank of the array
            arrdata.dtype = arrdata.dtype | (3 << 3)  # "3" for float, TODO:others
            arrdata.dtype = arrdata.dtype | (arr.dtype.itemsize << 6)  # no of bytes
    elif compiler == 'intel':
        #  TODO: doesn't work yet
        arrdata.elem_size = arr.dtype.itemsize
        arrdata.reserved = 0
        arrdata.info = int('10000111', 2)
        arrdata.rank = ndims
        arrdata.reserved2 = 0

    stride = 1
    for kd in range(ndims):
        arrdata.dim[kd].stride = stride
        arrdata.dim[kd].lower_bound = 1
        arrdata.dim[kd].upper_bound = arr.shape[kd]
        stride = stride*arr.shape[kd]

    return arrdata


def warn(output):
    caller_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, lines, index) = inspect.getframeinfo(caller_frame)
    filename = os.path.split(filename)[-1]
    print('')
    print('WARNING {}:{} {}():'.format(filename, line_number, function_name))
    print(output)


def debug(output):
    if not log_debug:
        return
    caller_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, lines, index) = inspect.getframeinfo(caller_frame)
    filename = os.path.split(filename)[-1]
    print('')
    print('DEBUG {}:{} {}():'.format(filename, line_number, function_name))
    print(output)


class fortran_module:
    def __init__(self, library, name, maxdim=7, path=None):
        self.library = library
        self.name = name
        self.methods = []
        self.maxdim = maxdim  # maximum dimension of arrays
        self.csource = ''
        self.loaded = False
        self.path = path

        # TODO: don't hardcode this
        self.compiler = 'gnu'
        self.compiler_version = 4

        # Manual path specification is required for tests via `setup.py test`
        # which would not find the extension module otherwise
        if self.path not in sys.path:
            sys.path.append(self.path)

    def __dir__(self):
        return self.methods

    def __getattr__(self, attr):
        # print(attr)
        def method(*args): return self.__call_fortran(attr, *args)
        return method

    def __call_fortran(self, function, *args):
        """
        Calls a Fortran module routine based on its name
        """
        cargs = []
        for arg in args:
            if isinstance(arg, int):
                cargs.append(self._ffi.new('int*', arg))
            elif isinstance(arg, float):
                cargs.append(self._ffi.new('double*', arg))
            elif isinstance(arg, np.ndarray):
                cargs.append(numpy2fortran(self._ffi, arg, self.compiler, self.compiler_version))
            else:  # TODO: add more basic types
                raise NotImplementedError('Argument type not understood')
        if self.compiler == 'gnu':
            funcname = '__'+self.name+'_MOD_'+function
        elif self.compiler == 'intel':
            funcname = self.name+'_mp_'+function+'_'
        else:
            raise NotImplementedError(
                    'Compiler {} not supported. Use gnu or intel'.format(self.compiler, self.compiler_version))
        func = getattr(self._lib, funcname)
        debug('Calling {}({})'.format(funcname, cargs))
        func(*cargs)

    def cdef(self, csource):  # TODO: replace this by implementing fdef
        """
        Specifies C source with some template replacements:
        {mod} -> compiler module prefix, e.g. for self.name == testmod for GCC:
          void {mod}_func() -> void __testmod_MOD_func()
        """
        # GNU specific
        if self.compiler == 'gnu':
            self.csource += csource.format(mod='__'+self.name+'_MOD')
        elif self.compiler == 'intel':
            self.csource += csource.format(mod=self.name+'_mp')
        else:
            raise NotImplementedError(
                    'Compiler {} not supported. Use gnu or intel'.format(self.compiler))
        debug('C signatures are\n' + self.csource)

    def fdef(self, fsource):
        ast = parse(fsource)
        
        csource = ''
        for subname, subp in ast.subprograms.items():
            debug('Adding subprogram {}({})'.format(subname, ','.join(subp.args)))
            csource += ccodegen(subp)
        
        self.cdef(csource)

    def compile(self, tmpdir='.', verbose=0, debugflag=None):
        """
        Compiles a Python extension as an interface for the Fortran module
        """
        ffi = FFI()

        structdef = arraydims(self.compiler, self.compiler_version)
        descr = arraydescr(self.compiler, self.compiler_version)
        for kdim in range(1, self.maxdim+1):
            structdef += descr.format(kdim)

        ffi.cdef(structdef+self.csource)

        extraargs = []
        if not verbose:
            extraargs.append('-Wno-implicit-function-declaration')

        if self.path:
            libpath = self.path
            target = os.path.join(self.path, '_'+self.name+'.so')
        else:
            libpath = '.'
            target = './_'+self.name+'.so'


        ffi.set_source('_'+self.name,
                       structdef,
                       libraries=[self.library],
                       library_dirs=['.'],
                       extra_compile_args=extraargs,
                       extra_link_args=['-Wl,-rpath,'+libpath, '-lgfortran'])


        debug('Compilation starting')
        ffi.compile(tmpdir, verbose, target, debugflag)

    def load(self):
        """
        Loads the Fortran module using the generated Python extension.
        Attention: module cannot be re-/unloaded unless Python is restarted.
        """
        if self.loaded:
            # TODO: add a check if the extension module itself is loaded.
            # Otherwise a new instance of a fortran_module makes you think
            # you can reload the extension module without warning.
            warn('Module cannot be re-/unloaded unless Python is restarted.')

        self._mod = importlib.import_module('_'+self.name)
        self._ffi = self._mod.ffi
        self._lib = self._mod.lib
        self.methods = []
        ext_methods = dir(self._lib)
        for m in ext_methods:
            if self.compiler == 'gnu':
                mname = re.sub('__.+_MOD_', '', m)  # GNU specific
            elif self.compiler == 'intel':
                mname = re.sub('__.+_mt_', '', m)
            else:
                raise NotImplementedError(
                        'Compiler {} not supported. Use gnu or intel'.format(self.compiler))
            self.methods.append(mname)
        self.loaded = True
