"""
Generate Python wrapper for given object files in Fortran
"""

import numpy as np

from cffi import FFI
from .common import libexts, debug


def arraydims(compiler):
    if compiler['name'] == 'gfortran':
        if compiler['version'] >= 8:  # TODO: check versions
            return """
              typedef struct array_dims array_dims;
              struct array_dims {
                ptrdiff_t stride;
                ptrdiff_t lower_bound;
                ptrdiff_t extent;
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
        # gfortran version < 8
        return """
            typedef struct array_dims array_dims;
            struct array_dims {
            ptrdiff_t stride;
            ptrdiff_t lower_bound;
            ptrdiff_t upper_bound;
            };
        """
    if compiler['name'] == 'ifort':
        return """
              typedef struct array_dims array_dims;
              struct array_dims {
                uintptr_t extent;
                uintptr_t distance;
                uintptr_t lower_bound;
              };
            """
    else:
        raise NotImplementedError(
            "Compiler {} not supported. Use gfortran or ifort".format(compiler))


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
        return """
            typedef struct array_{0}d array_{0}d;
            struct array_{0}d {{
            void *base_addr;
            size_t offset;
            ptrdiff_t dtype;
            struct array_dims dim[{0}];
            }};
        """
    if compiler['name'] == 'ifort':
        return """
              typedef struct array_{0}d array_{0}d;
              struct array_{0}d {{
                void *base_addr;
                size_t elem_size;
                uintptr_t reserved;
                uintptr_t info;
                uintptr_t rank;
                uintptr_t reserved2;
                struct array_dims dim[{0}];
              }};
            """
    raise NotImplementedError(
        "Compiler {} not supported. Use gfortran or ifort".format(compiler))


ctypemap = {
    ('int', None): 'int32_t',
    ('real', None): 'float',
    ('complex', None): 'float _Complex',
    ('logical', None): '_Bool',
    ('str', None): 'char',
    ('int', 1): 'int8_t',
    ('int', 2): 'int16_t',
    ('int', 4): 'int32_t',
    ('int', 8): 'int64_t',
    ('real', 4): 'float',
    ('real', 8): 'double',
    ('complex', 4): 'float _Complex',
    ('complex', 8): 'double _Complex',
    ('logical', 4): '_Bool'
}

# Map for GCC datatypes
dtypemap = {
    1: 'integer',
    2: 'logical',
    3: 'real',
    4: 'complex'
}

def ccodegen(ast, module):
    """Generates C signature for Fortran subprogram.

    Parameters:
        ast: AST containing Fortran types, variables, subroutines and/or functions.
        module (bool): True if code is part of a module, False otherwise.

    Returns:
        str: C code for the according signature for type definitions and
             declaration of variables and functions.

    """
    csource = ''
    for typename, typedef in ast.types.items():  # types
        debug('Adding type {}'.format(typename))
        csource += 'struct {} {{{{\n'.format(typename)
        for decl in typedef.declarations:
            for var in decl.namespace.values():
                ctype, cdecl = c_declaration(var)
                debug('{} {}'.format(ctype, cdecl))
                csource += '{} {};\n'.format(ctype, cdecl)
        csource += '}};\n'

    for subname, subp in ast.subprograms.items():  # subprograms
        debug('Adding subprogram {}({})'.format(
            subname, ', '.join(subp.args)))
        csource += ccodegen_sub(subp, module)

    if module:  # module variables
        for var in ast.namespace.values():
            ctype, cdecl = c_declaration(var)
            csource += 'extern {} {{mod}}_{}{{suffix}};\n'.format(ctype, cdecl)

    return csource


def ccodegen_sub(subprogram, module=True):
    """Generates C function signature for Fortran subprogram.

    Parameters:
        subprogram: AST branch representing a Fortran subroutine or function.
        module (bool): True if subprogram is part of a module, False otherwise.

    Returns:
        str: C code for the according signature to call the subprogram.

    """
    cargs = []
    nstr = 0  # number of string arguments, for adding hidden length arguments
    for arg in subprogram.args:
        # TODO: add handling of more than 1D fixed size array arguments
        attrs = subprogram.namespace[arg]
        dtype = attrs.dtype
        rank = attrs.rank
        shape = attrs.shape
        precision = attrs.precision
        debug('{} rank={} bytes={}'.format(dtype, rank, precision))

        if dtype == 'str':
            nstr = nstr+1

        if dtype.startswith('type'):
            typename = dtype.split(' ')[1]
            ctypename = 'struct {}'.format(typename)
        elif rank == 0:
            ctypename = ctypemap[(dtype, precision)]
        else:
            if (shape is None
                or shape[0] is None
                    or shape[0][1] is None):  # Assumed size array
                ctypename = 'array_{}d'.format(rank)
            else:  # Fixed size array
                ctypename = ctypemap[(dtype, precision)]

        if ctypename is None:
            raise NotImplementedError('{} rank={}'.format(dtype, rank))

        cargs.append('{} *{}'.format(ctypename, arg))

    for kstr in range(nstr):
        cargs.append('size_t strlen{}'.format(kstr))

    if module:  # subroutine in module
        csource = 'extern void {{mod}}_{}{{suffix}}({});\n'.format(
            subprogram.name, ', '.join(cargs))
    else:  # global subroutine
        csource = 'extern void {}_({});\n'.format(
            subprogram.name, ', '.join(cargs))

    return csource


def c_declaration(var):
    # TODO: add support for derived types also here
    ctype = ctypemap[(var.dtype, var.precision)]

    # Scalars
    if var.rank == 0:
        debug('Adding scalar {} ({})'.format(var.name, ctype))
        return ctype, var.name.lower()

    # Assumed size arrays

    if var.shape is None or var.shape[0] is None or var.shape[0][1] is None:
        return 'array_{}d'.format(var.rank), var.name.lower()

    # Fixed size arrays

    if var.rank == 1:
        debug('Adding rank {} array {} ({})'.format(var.rank, var.name, ctype))
        length = var.shape[0][1]
        return ctype, '{}[{}]'.format(var.name.lower(), length)
    if var.rank > 1:
        raise NotImplementedError('''
           Fixed size arrays with rank > 1 not yet supported
           as module variables''')



def fortran2numpy(ffi, var):
    # See https://gist.github.com/yig/77667e676163bbfc6c44af02657618a6
    # TODO: add support for more types than real(8) and also assumed size

    vartype = ffi.typeof(var)

    # Fixed size array
    if vartype.kind == 'array':  # fixed size
        ctype = vartype.item.cname
        ptr = ffi.addressof(var)
        size = ffi.sizeof(var)
    elif vartype.kind == 'struct':
        ptr = var.base_addr
        dtype = dtypemap[var.dtype.type]
        if var.dtype.type == 4:  # complex has twice the bytes
            ctype = ctypemap[(dtype, var.dtype.len/2)]
        else:
            ctype = ctypemap[(dtype, var.dtype.len)]
        
        size = var.dtype.len*var.dim[0].extent # TODO: support >1D
        dtype = var.dtype.type
    else:
        raise NotImplementedError(f'''
        Array of kind {vartype.kind} not supported.
        ''')
    
    if ctype == 'double':
        return np.frombuffer(ffi.buffer(ptr, size), 'f8')
    elif ctype == 'double _Complex':
        return np.frombuffer(ffi.buffer(ptr, size), 'c16')
    raise NotImplementedError(f'''
        Array of type {ctype} not supported.
        ''')


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

        stride = 1
        for kd in range(ndims):
            arrdata.dim[kd].stride = stride
            arrdata.dim[kd].lower_bound = 1
            if compiler['version'] >= 8:
                arrdata.dim[kd].extent = arr.shape[kd]
            else:
                arrdata.dim[kd].upper_bound = arr.shape[kd]
            stride = stride*arr.shape[kd]
    elif compiler['name'] == 'ifort':
        arrdata.elem_size = arr.dtype.itemsize
        arrdata.reserved = 0
        arrdata.info = int('100001110', 2)
        arrdata.rank = ndims
        arrdata.reserved2 = 0
        distance = arr.dtype.itemsize
        for kd in range(ndims):
            arrdata.dim[kd].distance = distance
            arrdata.dim[kd].lower_bound = 1
            arrdata.dim[kd].extent = arr.shape[kd]
            distance = distance*arr.shape[kd]

    return arrdata


def call_fortran(ffi, lib, function, compiler, module, *args):
    """
    Calls a Fortran routine based on its name
    """
    # TODO: scalars should be able to be either mutable 0d numpy arrays
    # for in/out, or immutable Python types for pure input
    # TODO: should be able to cast variables e.g. int/float if needed
    cargs = []
    cextraargs = []
    for arg in args:
        if isinstance(arg, str):
            cargs.append(ffi.new("char[]", arg.encode('ascii')))
            cextraargs.append(len(arg))
        elif isinstance(arg, int):
            cargs.append(ffi.new('int32_t*', arg))
        elif isinstance(arg, float):
            cargs.append(ffi.new('double*', arg))
        elif isinstance(arg, np.ndarray):
            cargs.append(numpy2fortran(ffi, arg, compiler))
        else:  # TODO: add more basic types
            cargs.append(arg)

    if module is None:
        funcname = function + '_'
    else:
        if compiler['name'] == 'gfortran':
            funcname = '__'+module+'_MOD_'+function
        elif compiler['name'] == 'ifort':
            funcname = module+'_mp_'+function+'_'
        else:
            raise NotImplementedError(
                '''Compiler {} not supported. Use gfortran or ifort
                '''.format(compiler))
    func = getattr(lib, funcname)
    debug('Calling {}({})'.format(funcname, cargs))
    func(*(cargs + cextraargs))


class FortranWrapper:
    def __init__(self, name, csource, extra_objects):
        self.name = name
        self.target = './_' + self.name + libexts[0]
        self.ffi = FFI()
        self.ffi.set_source(name, csource, extra_objects=extra_objects)

    def compile(self, tmpdir='.', verbose=0, debugflag=None):
        self.ffi.compile(tmpdir, verbose, self.target, debugflag)

    def load(self):
        pass
