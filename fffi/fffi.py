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
import subprocess
from cffi import FFI

from .parser import parse

log_warn = True
log_debug = False


def arraydims(compiler):
    if compiler['name'] == 'gfortran':
        if compiler['version'] >= 8:
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
    elif compiler['name'] == 'ifort':
            return """
              typedef struct array_dims array_dims;
              struct array_dims {
                uintptr_t upper_bound;
                uintptr_t stride;
                uintptr_t lower_bound;
              };
            """
    else:
        raise NotImplementedError('''Compiler {} not supported.
                                     Use gfortran or ifort'''.format(compiler))


def arraydescr(compiler):
    if compiler['name'] == 'gfortran':
        if compiler['version'] >= 8:
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
    elif compiler['name'] == 'ifort':
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
        raise NotImplementedError('''Compiler {} not supported.
                                     Use gfortran or ifort'''.format(compiler))


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
        # TODO: add handling of fixed size array arguments
        attrs = subprogram.namespace[arg]
        dtype = attrs.dtype
        rank = attrs.rank
        precision = attrs.precision
        debug('{} rank={} bytes={}'.format(dtype, rank, precision))

        if dtype.startswith('type'): 
            typename = dtype.split(' ')[1]
            ctypename = 'struct {}'.format(typename)
        elif rank == 0:
            ctypename = ctypemap[(dtype, precision)]
        else:
            ctypename = 'array_{}d'.format(rank)

        if ctypename is None:
            raise NotImplementedError('{} rank={}'.format(dtype, rank))

        cargs.append('{} *{}'.format(ctypename, arg))

    csource = 'extern void {{mod}}_{}{{suffix}}({});\n'.format(
        subprogram.name, ','.join(cargs))
    return csource

def c_declaration(var):
    # TODO: add support for derived types also here
    ctype = ctypemap[(var.dtype, var.precision)]
    
    # Scalars
    if var.rank == 0:
        debug('Adding scalar {} ({})'.format(var.name, ctype))
        return ctype, var.name
    
    if not(var.shape):
        # TODO: add support for assumed size and/or allocatable arrays
        # csource += 'extern struct array_{}d {{mod}}_{};\n'.format(var.rank, varname)
        raise NotImplementedError('''
            Declaration of assumed size and/or allocatable arrays
            not yet supported.
            ''')
    
    # Fixed size arrays
    
    if var.rank == 1:
        debug('Adding rank {} array {} ({})'.format(var.rank, var.name, ctype))
        length = var.shape[0][1]
        return ctype, '{}[{}]'.format(var.name, length)
    elif var.rank > 1:
        raise NotImplementedError(
        '''Fixed size arrays with rank > 1 not yet supported 
           as module variables''')
    else:
        ctype = 'array_{}d'.format(var.rank)
        return (ctype + '*'), var.name


def numpy2fortran(ffi, arr, compiler):
    """
    Converts Fortran-contiguous NumPy array arr into an array descriptor
    compatible with gfortran to be passed to library routines via cffi.
    """
    if not arr.flags.f_contiguous:
        raise TypeError('needs Fortran order in NumPy arrays')

    ndims = len(arr.shape)
    arrdata = ffi.new('array_{}d*'.format(ndims))
    arrdata.base_addr = ffi.cast('void*', arr.ctypes.data)
    if compiler['name'] == 'gfortran':
        arrdata.offset = 0
        if compiler['version'] >= 8:
            arrdata.span = np.size(arr)*arr.dtype.itemsize
            arrdata.dtype.len = arr.dtype.itemsize
            arrdata.dtype.ver = 0
            arrdata.dtype.rank = ndims
            arrdata.dtype.type = 3  # "3" for float, TODO:others
            arrdata.dtype.attribute = 0
        else:
            arrdata.dtype = ndims  # rank of the array
            arrdata.dtype = arrdata.dtype | (3 << 3)  # float: "3" TODO:others
            arrdata.dtype = arrdata.dtype | (arr.dtype.itemsize << 6)
    elif compiler['name'] == 'ifort':
        # TODO: doesn't work yet
        # see https://software.intel.com/en-us/
        #     fortran-compiler-developer-guide-and-reference-handling
        #     -fortran-array-descriptors
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

def fortran2numpy(ffi, data):
    # See https://gist.github.com/yig/77667e676163bbfc6c44af02657618a6
    # TODO: add support for more types than real(8) and also assumed size
    ptr = ffi.addressof(data)
    return np.frombuffer(ffi.buffer(ptr, 8*len(data)), 'f8' )


def warn(output):
    caller_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, _, _) = inspect.getframeinfo(caller_frame)
    filename = os.path.split(filename)[-1]
    print('')
    print('WARNING {}:{} {}():'.format(filename, line_number, function_name))
    print(output)


def debug(output):
    if not log_debug:
        return
    caller_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, _, _) = inspect.getframeinfo(caller_frame)
    filename = os.path.split(filename)[-1]
    print('')
    print('DEBUG {}:{} {}():'.format(filename, line_number, function_name))
    print(output)

class fortran_library:
    def __init__(self, name, maxdim=7, path=None, compiler=None):
        self.name = name
        self.maxdim = maxdim  # maximum dimension of arrays
        self.csource = ''
        self.loaded = False
        self.compiler = compiler
        self.path = path
        
        if self.path:
            self.libpath = self.path
        else:
            self.libpath = '.'

        if self.compiler is None:
            libstrings = subprocess.check_output(
                ['strings', os.path.join(self.libpath, 'lib'+name+'.so')]
            )
            libstrings = libstrings.decode('utf-8').split('\n')
            for line in libstrings:
                if line.startswith('GCC:') or line.startswith('@GCC:'):
                    debug(line)
                    major = int(line.split(')')[-1].split('.')[0])
                    self.compiler = {'name': 'gfortran', 'version': major}
                    debug(self.compiler)
                    break
                

        # Manual path specification is required for tests via `setup.py test`
        # which would not find the extension module otherwise
        if self.path not in sys.path:
            sys.path.append(self.path)
    

    def compile(self, tmpdir='.', verbose=0, debugflag=None):
        """
        Compiles a Python extension as an interface for the Fortran module
        """
        ffi = FFI()

        extraargs = []
        if not verbose:
            extraargs.append('-Wno-implicit-function-declaration')

        if self.path:
            target = os.path.join(self.path, '_'+self.name+'.so')
        else:
            target = './_'+self.name+'.so'

        structdef = arraydims(self.compiler)
        descr = arraydescr(self.compiler)
        for kdim in range(1, self.maxdim+1):
            structdef += descr.format(kdim)

        ffi.cdef(structdef+self.csource)

        ffi.set_source('_'+self.name,
                       structdef+self.csource,
                       libraries=[self.name],
                       library_dirs=['.', self.libpath],
                       extra_compile_args=extraargs,
                       extra_link_args=['-Wl,-rpath,'+self.libpath,
                                        '-lgfortran'])

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
            warn('Library cannot be re-/unloaded unless Python is restarted.')

        self._mod = importlib.import_module('_'+self.name)
        self._ffi = self._mod.ffi
        self._lib = self._mod.lib
        self.loaded = True
        

class fortran_module:
    def __init__(self, library, name, maxdim=7, path=None, compiler=None):
        if isinstance(library, str):
            self.library = fortran_library(library, maxdim, path, compiler=None)
        else:
            self.library = library
        self.name = name
        self.methods = set()
        self.variables = set()
        self.csource = ''
        self.loaded = False

    def __dir__(self):
        return sorted(self.methods | self.variables)

    def __getattr__(self, attr):
        if ('methods' in self.__dict__)  and (attr in self.methods):
            def method(*args): return self.__call_fortran(attr, *args)
            return method
        if ('variables' in self.__dict__) and (attr in self.variables):
            return self.__get_var_fortran(attr)
        else:
            raise AttributeError('''Fortran module \'{}\' has no attribute
                                    \'{}\'.'''.format(self.name, attr))

    def __setattr__(self, attr, value):
        if ('variables' in self.__dict__) and (attr in self.variables):
            if self.library.compiler['name'] == 'gfortran':
                varname = '__'+self.name+'_MOD_'+attr
            elif self.library.compiler['name'] == 'ifort':
                varname = self.name+'_mp_'+attr+'_'
            else:
                raise NotImplementedError(
                    '''Compiler {} not supported. Use gfortran or ifort
                    '''.format(self.compiler))
            setattr(self.library._lib, varname, value)
        else:
            super(fortran_module, self).__setattr__(attr, value)


    def __call_fortran(self, function, *args):
        """
        Calls a Fortran module routine based on its name
        """
        # TODO: scalars should be able to be either mutable 0d numpy arrays
        # for in/out, or immutable Python types for pure input
        # TODO: should be able to cast variables e.g. int/float if needed
        cargs = []
        for arg in args:
            if isinstance(arg, int):
                cargs.append(self.library._ffi.new('int32_t*', arg))
            elif isinstance(arg, float):
                cargs.append(self.library._ffi.new('double*', arg))
            elif isinstance(arg, np.ndarray):
                cargs.append(numpy2fortran(self.library._ffi, arg, 
                                           self.library.compiler))
            else:  # TODO: add more basic types
                cargs.append(arg)
        if self.library.compiler['name'] == 'gfortran':
            funcname = '__'+self.name+'_MOD_'+function
        elif self.library.compiler['name'] == 'ifort':
            funcname = self.name+'_mp_'+function+'_'
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(self.library.compiler))
        func = getattr(self.library._lib, funcname)
        debug('Calling {}({})'.format(funcname, cargs))
        func(*cargs)

    def __get_var_fortran(self, var):
        """
        Returns a Fortran variable based on its name
        """
        if self.library.compiler['name'] == 'gfortran':
            varname = '__'+self.name+'_MOD_'+var
        elif self.library.compiler['name'] == 'ifort':
            varname = self.name+'_mp_'+var+'_'
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(self.library.compiler))
        var = getattr(self.library._lib, varname)
        
        if isinstance(var, self.library._ffi.CData):  # array
            return fortran2numpy(self.library._ffi, var)
        
        return var

    def cdef(self, csource):
        """
        Specifies C source with some template replacements:
        {mod} -> compiler module prefix, e.g. for self.name == testmod for GCC:
          void {mod}_func() -> void __testmod_MOD_func()
        """
        # GNU specific
        if self.library.compiler['name'] == 'gfortran':
            self.csource += csource.format(mod='__'+self.name+'_MOD',
                                           suffix='')
        elif self.library.compiler['name'] == 'ifort':
            self.csource += csource.format(mod=self.name+'_mp',
                                           suffix='_')
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(self.library.compiler))
        debug('C signatures are\n' + self.csource)
        self.library.csource = self.library.csource + self.csource
        

    def fdef(self, fsource):
        ast = parse(fsource)

        csource = ''
        for typename, typedef in ast.types.items():
            debug('Adding type {}'.format(typename))
            csource += 'struct {} {{{{\n'.format(typename)
            for decl in typedef.declarations:
                for varname, var in decl.namespace.items():
                    ctype, cdecl = c_declaration(var)
                    debug('{} {}'.format(ctype, cdecl))
                    csource += '{} {};\n'.format(ctype, cdecl)
            csource += '}};\n'
           # csource += ccodegen(subp)
        for subname, subp in ast.subprograms.items():
            debug('Adding subprogram {}({})'.format(
                    subname, ','.join(subp.args)))
            csource += ccodegen(subp)

        for varname, var in ast.namespace.items():
            ctype, cdecl = c_declaration(var)
            csource += 'extern {} {{mod}}_{}{{suffix}};\n'.format(ctype, cdecl)

        self.cdef(csource)
    
    def load(self):
        if not self.library.loaded:
            self.library.load()
        self.methods = set()
        ext_methods = dir(self.library._lib)
        for m in ext_methods:
            if self.library.compiler['name'] == 'gfortran':
                mod_sym = '__{}_MOD_'.format(self.name)
            elif self.library.compiler['name'] == 'ifort':
                mod_sym = '{}_mp_'.format(self.name)
            else:
                raise NotImplementedError(
                    '''Compiler {} not supported. Use gfortran or ifort
                    '''.format(self.compiler))
            if not mod_sym in m: 
                continue
            mname = re.sub(mod_sym, '', m)
            if self.library.compiler['name'] == 'ifort':
                mname = mname.strip('_')
            attr = getattr(self.library._lib, m)
            debug('Name: {}, Type: {}, Callable: {}'.format(
                    mname, type(attr), callable(attr)))
            if isinstance(attr, self.library._ffi.CData):  # array variable
                self.variables.add(mname)
            elif callable(attr):  # subroutine or function
                self.methods.add(mname)
            else:  # scalar variable
                self.variables.add(mname)

    def compile(self, tmpdir='.', verbose=0, debugflag=None):
        self.library.compile(tmpdir, verbose, debugflag)
        
    def new(self, typename):
        return self.library._ffi.new('struct {} *'.format(typename))
