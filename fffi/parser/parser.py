# coding: utf-8

import os
from os.path import join, dirname

from textx.metamodel import metamodel_from_str

from pyccel.ast import Variable
from pyccel.ast.datatypes import dtype_and_precsision_registry as dtype_registry

#==============================================================================
class Fortran(object):
    """Class for Fortran syntax."""
    def __init__(self, *args, **kwargs):
        self.statements = kwargs.pop('statements', [])

class Declaration(object):
    """Class representing a Fortran declaration."""
    def __init__(self, **kwargs):
        self.dtype     = kwargs.pop('dtype')
        self.attributs = kwargs.pop('attributs', []) # this is optional
        self.entities  = kwargs.pop('entities')

class DeclarationAttribut(object):
    """Class representing a Fortran declaration attribut."""
    def __init__(self, **kwargs):
        self.key   = kwargs.pop('key')
        self.value = kwargs.pop('value', None) # this is optional

class DeclarationEntityObject(object):
    """Class representing an entity object ."""
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')

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
        self.upper_bound = kwargs.pop('upper_bound')
        self.lower_bound = kwargs.pop('lower_bound', None)

#==============================================================================

#==============================================================================
def get_by_name(ast, name):
    """
    Returns an object from the AST by giving its name.
    """
    for token in ast.declarations:
        if token.name == name:
            return token
    return None

#==============================================================================
def ast_to_dict(ast):
    """
    Returns an object from the AST by giving its name.
    """
    tokens = {}
    for token in ast.declarations:
        tokens[token.name] = token
    return tokens

#==============================================================================
def parse(inputs, debug=False):
    this_folder = dirname(__file__)

    # Get meta-model from language description
    grammar = join(this_folder, 'grammar.tx')

    classes = [Fortran,
               Declaration,
               DeclarationAttribut,
               DeclarationEntityObject,
               DeclarationEntityFunction,
               ArraySpec,
               ArrayExplicitShapeSpec]

    from textx.metamodel import metamodel_from_file
    meta = metamodel_from_file(grammar, debug=debug, classes=classes)

    # Instantiate model
    if os.path.isfile(inputs):
        ast = meta.model_from_file(inputs)

    else:
        ast = meta.model_from_str(inputs)

    namespace = {}
    stmts = []
    for stmt in ast.statements:
        if isinstance(stmt, Declaration):
            # ...
            dtype = stmt.dtype.kind
            if dtype.upper() == 'DOUBLE PRECISION':
                dtype = 'DOUBLE'
            dtype, precision = dtype_registry[dtype.lower()]
            # ...

            # ...
            entities = stmt.entities
            names = [i.name for i in entities]
            # ...

            # ...
            rank = 0
            attributs = []
            for i in stmt.attributs:
                key   = i.key.lower()
                value = i.value
                d_infos = value.expr

                if key == 'dimension':
                    shape = d_infos['shape']
                    rank = len(shape)

                attributs.append(key)
            # ...

#            print(dtype, attributs, names)

            is_allocatable = ('allocatable' in attributs)
            is_pointer     = ('pointer' in attributs)
            is_target      = ('target' in attributs)

            for name in names:
                var = Variable( dtype,
                                name,
                                rank           = rank,
                                allocatable    = is_allocatable,
#                                is_stack_array = ,
                                is_pointer     = is_pointer,
                                is_target      = is_target,
#                                is_polymorphic=,
#                                is_optional=,
                                shape=shape,
#                                cls_base=None,
#                                cls_parameters=None,
#                                order=,
                                precision=precision,
                              )

                namespace[name] = var

        else:
            raise NotImplementedError('TODO {}'.format(type(stmt)))


#    print(namespace)
    for k,v in namespace.items():
        v.inspect()


####################################
if __name__ == '__main__':
#    ast = parse('INTEGER :: x')
#    ast = parse('INTEGER  x')
#    ast = parse('INTEGER, PARAMETER ::  x')
#    ast = parse('DOUBLE PRECISION :: y')
    ast = parse('INTEGER, DIMENSION(10) :: x')
