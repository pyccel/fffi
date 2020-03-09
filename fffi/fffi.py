#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 14:32:32 2017

@author: Christopher Albert <albert@alumni.tugraz.at>
"""
import importlib
import os
import re
import sys
import subprocess
from pathlib import Path

from cffi import FFI
import numpy as np

from .common import libext, debug, warn
from .parser import parse
from .fortran_wrapper import (
    arraydescr, arraydims, c_declaration, call_fortran,
    numpy2fortran, fortran2numpy, fdef
)


class FortranLibrary:
    def __init__(self, name, maxdim=7, path=None, compiler=None):
        self.name = name
        self.maxdim = maxdim  # maximum dimension of arrays
        self.csource = ''
        self.loaded = False
        self.compiler = compiler
        self.methods = set()

        if isinstance(path, Path):
            self.path = path.__str__()
        else:
            self.path = path

        if self.path:
            self.libpath = self.path
        else:
            self.libpath = '.'

        if self.compiler is None:
            libstrings = subprocess.check_output(
                ['strings', os.path.join(self.libpath, 'lib'+name+libext)]
            )
            libstrings = libstrings.decode('utf-8').split('\n')
            for line in libstrings:
                if line.startswith('GCC:') or line.startswith('@GCC:'):
                    debug(line)
                    major = int(line.split(')')[-1].split('.')[0])
                    self.compiler = {'name': 'gfortran', 'version': major}
                    debug(self.compiler)
                    break

        if self.compiler is None:  # fallback to recent gfortran
            self.compiler = {'name': 'gfortran', 'version': 9}

        # Manual path specification is required for tests via `setup.py test`
        # which would not find the extension module otherwise
        if self.path not in sys.path:
            sys.path.append(self.path)

    def __dir__(self):
        return sorted(self.methods)

    def __getattr__(self, attr):
        if ('methods' in self.__dict__) and (attr in self.methods):
            def method(*args):
                return call_fortran(
                    self._ffi, self._lib, attr, self.compiler, *args)
            return method
        raise AttributeError('''Fortran library \'{}\' has no routine
                                \'{}\'.'''.format(self.name, attr))


    def compile(self, tmpdir='.', verbose=0, debugflag=None):
        """
        Compiles a Python extension as an interface for the Fortran module
        """
        ffi = FFI()

        extraargs = []
        if not verbose:
            extraargs.append('-Wno-implicit-function-declaration')

        extralinkargs = []
        if self.compiler['name'] in ('gfortran', 'ifort'):
            extralinkargs.append('-Wl,-rpath,'+self.libpath)
        if self.compiler['name'] == 'gfortran' and 'darwin' not in sys.platform:
            extralinkargs.append('-lgfortran')

        if self.path:
            target = os.path.join(self.path, '_'+self.name+libext)
        else:
            target = './_'+self.name+libext

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
                       extra_link_args=extralinkargs)

        debug('Compilation starting')
        ffi.compile(tmpdir, verbose, target, debugflag)

    def load(self):
        """
        Loads the Fortran module using the generated Python extension.
        Attention: module cannot be re-/unloaded unless Python is restarted.
        """
        if self.loaded:
            # TODO: add a check if the extension module itself is loaded.
            # Otherwise a new instance of a FortranModule makes you think
            # you can reload the extension module without warning.
            warn('Library cannot be re-/unloaded unless Python is restarted.')

        self._mod = importlib.import_module('_'+self.name)
        self._ffi = self._mod.ffi
        self._lib = self._mod.lib

        self.methods = set()
        ext_methods = dir(self._lib)
        for m in ext_methods:
            if not m.endswith('_'):
                continue
            mname = m.strip('_')
            attr = getattr(self._lib, m)
            debug('Name: {}, Type: {}, Callable: {}'.format(
                mname, type(attr), callable(attr)))
            if callable(attr):  # subroutine or function
                self.methods.add(mname)

        self.loaded = True

    def cdef(self, csource):
        """
        Specifies C source with suffix template replacements
        """
        self.csource += csource
        debug('C signatures are\n' + self.csource)

    def fdef(self, fsource):
        csource = fdef(fsource, module=False)
        self.cdef(csource)

    def new(self, typename, value=None):
        typelow = typename.lower()  # Case-insensitive Fortran

        # Basic types
        if typelow in ['integer', 'int', 'int32']:
            return self._ffi.new('int32_t*', value)
        if typelow in ['integer(8)', 'int64']:
            return self._ffi.new('int64_t*', value)
        if typelow in ['real', 'real(4)', 'float']:
            return self._ffi.new('float*', value)
        if typelow in ['real(8)', 'double']:
            return self._ffi.new('double*', value)

        # User-defined types
        if value is None:
            return self._ffi.new('struct {} *'.format(typename))
        raise NotImplementedError(
            'Cannot assign value to type {}'.format(typename))


class FortranModule:
    def __init__(self, library, name, maxdim=7, path=None, compiler=None):
        if isinstance(library, str):
            self.lib = FortranLibrary(library, maxdim, path, compiler)
        else:
            self.lib = library
        self.name = name
        self.methods = set()
        self.variables = set()
        self.csource = ''
        self.loaded = False

    def __dir__(self):
        return sorted(self.methods | self.variables)

    def __getattr__(self, attr):
        if ('methods' in self.__dict__) and (attr in self.methods):
            def method(*args):
                return self.__call_fortran(attr, *args)
            return method
        if ('variables' in self.__dict__) and (attr in self.variables):
            return self.__get_var_fortran(attr)
        raise AttributeError('''Fortran module \'{}\' has no attribute
                                \'{}\'.'''.format(self.name, attr))

    def __setattr__(self, attr, value):
        if ('variables' in self.__dict__) and (attr in self.variables):
            if self.lib.compiler['name'] == 'gfortran':
                varname = '__'+self.name+'_MOD_'+attr
            elif self.lib.compiler['name'] == 'ifort':
                varname = self.name+'_mp_'+attr+'_'
            else:
                raise NotImplementedError(
                    '''Compiler {} not supported. Use gfortran or ifort
                    '''.format(self.compiler))
            setattr(self.lib._lib, varname, value)
        else:
            super(FortranModule, self).__setattr__(attr, value)

    def __call_fortran(self, function, *args):
        """
        Calls a Fortran module routine based on its name
        """
        # TODO: scalars should be able to be either mutable 0d numpy arrays
        # for in/out, or immutable Python types for pure input
        # TODO: should be able to cast variables e.g. int/float if needed
        cargs = []
        cextraargs = []
        for arg in args:
            if isinstance(arg, str):
                cargs.append(self._ffi.new("char[]", arg.encode('ascii')))
                cextraargs.append(len(arg))
            if isinstance(arg, int):
                cargs.append(self.lib._ffi.new('int32_t*', arg))
            elif isinstance(arg, float):
                cargs.append(self.lib._ffi.new('double*', arg))
            elif isinstance(arg, np.ndarray):
                cargs.append(numpy2fortran(self.lib._ffi, arg,
                                           self.lib.compiler))
            else:  # TODO: add more basic types
                cargs.append(arg)
        if self.lib.compiler['name'] == 'gfortran':
            funcname = '__'+self.name+'_MOD_'+function
        elif self.lib.compiler['name'] == 'ifort':
            funcname = self.name+'_mp_'+function+'_'
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(self.lib.compiler))
        func = getattr(self.lib._lib, funcname)
        debug('Calling {}({})'.format(funcname, cargs))
        func(*(cargs + cextraargs))

    def __get_var_fortran(self, var):
        """
        Returns a Fortran variable based on its name
        """
        if self.lib.compiler['name'] == 'gfortran':
            varname = '__'+self.name+'_MOD_'+var
        elif self.lib.compiler['name'] == 'ifort':
            varname = self.name+'_mp_'+var+'_'
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(self.lib.compiler))
        var = getattr(self.lib._lib, varname)

        if isinstance(var, self.lib._ffi.CData):  # array
            return fortran2numpy(self.lib._ffi, var)

        return var

    def cdef(self, csource):
        """
        Specifies C source with some template replacements:
        {mod} -> compiler module prefix, e.g. for self.name == testmod for GCC:
          void {mod}_func() -> void __testmod_MOD_func()
        """
        # GNU specific
        if self.lib.compiler['name'] == 'gfortran':
            self.csource += csource.format(mod='__'+self.name+'_MOD',
                                           suffix='')
        elif self.lib.compiler['name'] == 'ifort':
            self.csource += csource.format(mod=self.name+'_mp',
                                           suffix='_')
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(self.lib.compiler))
        debug('C signatures are\n' + self.csource)
        self.lib.csource = self.lib.csource + self.csource

    def fdef(self, fsource):
        csource = fdef(fsource, module=True)

        self.cdef(csource)

    def load(self):
        if not self.lib.loaded:
            self.lib.load()
        self.methods = set()
        ext_methods = dir(self.lib._lib)
        for m in ext_methods:
            if self.lib.compiler['name'] == 'gfortran':
                mod_sym = '__{}_MOD_'.format(self.name)
            elif self.lib.compiler['name'] == 'ifort':
                mod_sym = '{}_mp_'.format(self.name)
            else:
                raise NotImplementedError(
                    '''Compiler {} not supported. Use gfortran or ifort
                    '''.format(self.compiler))
            if not mod_sym in m:
                continue
            mname = re.sub(mod_sym, '', m)
            if self.lib.compiler['name'] == 'ifort':
                mname = mname.strip('_')
            attr = getattr(self.lib._lib, m)
            debug('Name: {}, Type: {}, Callable: {}'.format(
                mname, type(attr), callable(attr)))
            if isinstance(attr, self.lib._ffi.CData):  # array variable
                self.variables.add(mname)
            elif callable(attr):  # subroutine or function
                self.methods.add(mname)
            else:  # scalar variable
                self.variables.add(mname)

    def compile(self, tmpdir='.', verbose=0, debugflag=None):
        self.lib.compile(tmpdir, verbose, debugflag)

    def new(self, typename):
        return self.lib.new(typename)
