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
        """
        """
        self.dtype     = kwargs.pop('dtype')
        self.attributs = kwargs.pop('attributs', []) # this is optional
        self.entities  = kwargs.pop('entities')

class DeclarationEntityObject(object):
    """Class representing an entity object ."""
    def __init__(self, **kwargs):
        """
        """
        self.name = kwargs.pop('name')
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
               DeclarationEntityObject]

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
            dtype = stmt.dtype.kind
            if dtype.upper() == 'DOUBLE PRECISION':
                dtype = 'DOUBLE'
            dtype, precision = dtype_registry[dtype.lower()]
            attributs = [i.lower() for i in stmt.attributs]
            entities = stmt.entities
            names = [i.name for i in entities]
#            print(dtype, attributs, names)

            rank = 0

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
#                                shape=None,
#                                cls_base=None,
#                                cls_parameters=None,
#                                order=,
                                precision=precision,
                              )

                namespace[name] = var

        else:
            raise NotImplementedError('TODO {}'.format(type(stmt)))


    print(namespace)


####################################
if __name__ == '__main__':
    ast = parse('INTEGER :: x')
    ast = parse('DOUBLE PRECISION :: y')
