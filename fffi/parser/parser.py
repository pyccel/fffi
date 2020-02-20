# coding: utf-8

import os
from os.path import join, dirname

from textx.metamodel import metamodel_from_file

# ==============================================================================
# TODO: integrate again with pyccel
#from pyccel.ast import Variable
#from pyccel.ast.datatypes import dtype_and_precsision_registry as dtype_registry

# Here are replacements to be compatible with pyccel


class Variable():
    def __init__(self,
                 dtype,
                 name,
                 rank=0,
                 allocatable=False,
                 is_stack_array=False,
                 is_pointer=False,
                 is_target=False,
                 is_polymorphic=None,
                 is_optional=None,
                 shape=None,
                 cls_base=None,
                 cls_parameters=None,
                 order='C',
                 precision=0):
        self.dtype = dtype
        self.name = name
        self.rank = rank
        self.allocatable = allocatable
        self.is_pointer = is_pointer
        self.is_target = is_target
        self.shape = shape
        self.precision = precision


# TODO: integrate again with pyccel
dtype_registry = {'real': ('real', 8),
                  'double': ('real', 8),
                  'float': ('real', 8),
                  'float32': ('real', 4),
                  'float64': ('real', 8),
                  'complex': ('complex', 8),
                  'complex64': ('complex', 4),
                  'complex128': ('complex', 8),
                  'int8': ('int', 1),
                  'int16': ('int', 2),
                  'int32': ('int', 4),
                  'int64': ('int', 8),
                  'int': ('int', 4),
                  'integer': ('int', 4),
                  'logical': ('int', 1)}

# ==============================================================================


class Fortran(object):
    """Class for Fortran syntax."""

    def __init__(self, *args, **kwargs):
        self.statements = kwargs.pop('statements', [])
        self.modules = {}
        self.subprograms = {}
        self.namespace = {}
        self.types = {}

        for stmt in self.statements:
            if isinstance(stmt, Module):
                self.modules[stmt.name] = stmt
            elif isinstance(stmt, InternalSubprogram):
                self.subprograms[stmt.name] = stmt
            elif isinstance(stmt, Declaration):
                self.namespace = {**self.namespace, **stmt.namespace}
            elif isinstance(stmt, DerivedTypeDefinition):
                self.types[stmt.name] = stmt
            else:
                raise NotImplementedError('TODO {}'.format(type(stmt)))


class Module(object):
    """Class representing a Fortran module."""

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        self.declarations = kwargs.pop('declarations', [])  # optional
        self.subprograms = kwargs.pop('subprograms', [])  # optional

        self.namespace = {}

        for decl in self.declarations:
            self.namespace = {**self.namespace, **decl.namespace}


class InternalSubprogram(object):
    """Class representing a Fortran internal subprogram."""

    def __init__(self, **kwargs):
        self.heading = kwargs.pop('heading')
        self.declarations = kwargs.pop('declarations', [])  # optional
        self.ending = kwargs.pop('ending')

        self.name = self.heading.name
        self.args = self.heading.arguments
        self.namespace = {}

        for decl in self.declarations:
            self.namespace = {**self.namespace, **decl.namespace}


class SubprogramHeading(object):
    """Class representing a Fortran internal subprogram."""

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.arguments = kwargs.pop('arguments', [])  # optional


class SubprogramEnding(object):
    """Class representing a Fortran internal subprogram."""

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')


class InternalSubprogramHeading(object):
    """Class representing a Fortran internal subprogram."""

    def __init__(self, **kwargs):
        self.heading = kwargs.pop('heading')
        self.ending = kwargs.pop('ending')


class Declaration(object):
    """Class representing a Fortran declaration."""

    def __init__(self, **kwargs):
        self.dtype = kwargs.pop('dtype')
        self.attributes = kwargs.pop('attributes', [])  # this is optional
        self.entities = kwargs.pop('entities')
        self._build_namespace()

    def _build_namespace(self):
        self.namespace = {}
        # ...
        dtype = self.dtype.kind
        if dtype.upper() == 'DOUBLE PRECISION':
            dtype = 'DOUBLE'

        if dtype.upper() == 'TYPE':
            dtype = 'type ' + self.dtype.name
            precision = None
        else:
            dtype, precision = dtype_registry[dtype.lower()]

        rank = 0
        shape = None
        attributes = []
        for i in self.attributes:
            key = i.key.lower()
            value = i.value

            if key == 'dimension':
                d_infos = value.expr
                shape = d_infos['shape']
                rank = len(shape)

            attributes.append(key)

        is_allocatable = ('allocatable' in attributes)
        is_pointer = ('pointer' in attributes)
        is_target = ('target' in attributes)

        for ent in self.entities:
            localrank = rank
            arrayspec = ent.arrayspec
            if rank == 0 and (arrayspec is not None):
                localrank = len(arrayspec.expr['shape'])

            var = Variable(dtype,
                           ent.name,
                           rank=localrank,
                           allocatable=is_allocatable,
                           #                                is_stack_array = ,
                           is_pointer=is_pointer,
                           is_target=is_target,
                           #                                is_polymorphic=,
                           #                                is_optional=,
                           shape=shape,
                           #                                cls_base=None,
                           #                                cls_parameters=None,
                           #                                order=,
                           precision=precision
                           )
            self.namespace[ent.name] = var


class DeclarationAttribute(object):
    """Class representing a Fortran declaration attribute."""

    def __init__(self, **kwargs):
        self.key = kwargs.pop('key')
        self.value = kwargs.pop('value', None)  # this is optional


class DeclarationEntityObject(object):
    """Class representing an entity object ."""

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.arrayspec = kwargs.pop('arrayspec')


class DeclarationEntityFunction(object):
    """Class representing an entity function."""

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.charlen = kwargs.pop('charlen', None)
        raise NotImplementedError('')


class ArraySpec(object):
    """Class representing array spec."""

    def __init__(self, **kwargs):
        self.value = kwargs.pop('value')

    @property
    def expr(self):
        d_infos = {}

        shapes = []
        if isinstance(self.value, (list, tuple)):
            for i in self.value:
                if isinstance(i, ArrayExplicitShapeSpec):
                    lower = i.lower_bound
                    upper = i.upper_bound
                    shapes.append([lower, upper])

        else:
            raise NotImplementedError('')

        d_infos['shape'] = shapes
        return d_infos


class ArrayExplicitShapeSpec(object):
    """Class representing explicit array shape."""

    def __init__(self, **kwargs):
        self.upper_bound = kwargs.pop('upper_bound', None)
        self.lower_bound = kwargs.pop('lower_bound', 1)


class DerivedTypeDefinition(object):
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.declarations = kwargs.pop('declarations', [])

# ==============================================================================

# ==============================================================================


def get_by_name(ast, name):
    """
    Returns an object from the AST by giving its name.
    """
    for token in ast.declarations:
        if token.name == name:
            return token
    return None

# ==============================================================================


def ast_to_dict(ast):
    """
    Returns an object from the AST by giving its name.
    """
    tokens = {}
    for token in ast.declarations:
        tokens[token.name] = token
    return tokens

# ==============================================================================


def parse(inputs, debug=False):
    this_folder = dirname(__file__)

    # Get meta-model from language description
    grammar = join(this_folder, 'grammar.tx')

    classes = [Fortran,
               Module,
               InternalSubprogram,
               Declaration,
               DeclarationAttribute,
               DeclarationEntityObject,
               DeclarationEntityFunction,
               ArraySpec,
               ArrayExplicitShapeSpec,
               DerivedTypeDefinition]

    meta = metamodel_from_file(
        grammar, debug=debug, classes=classes, ignore_case=True)

    # Instantiate model
    if os.path.isfile(inputs):
        ast = meta.model_from_file(inputs)

    else:
        ast = meta.model_from_str(inputs)

#    print(namespace)
#    for k,v in namespace.items():
#        v.inspect()

    # this is usefull for testing
#    if len(namespace) == 1:
#        return list(namespace.values())[0]
    return ast
