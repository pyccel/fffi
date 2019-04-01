# coding: utf-8

import os
from os.path import join, dirname
from textx.metamodel import metamodel_from_str

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

    from textx.metamodel import metamodel_from_file
    meta = metamodel_from_file(grammar, debug=debug) # TODO add classes

    # Instantiate model
    if os.path.isfile(inputs):
        ast = meta.model_from_file(inputs)

    else:
        ast = meta.model_from_str(inputs)

    for token in ast.statements:
        print(token)

#    stmts = []
#    for stmt in model.statements:
#        if isinstance(stmt, OpenmpStmt):
#            e = stmt.stmt.expr
#            stmts.append(e)
#
#    if len(stmts) == 1:
#        return stmts[0]
#    else:
#        return stmts


####################################
if __name__ == '__main__':
    ast = parse('INTEGER :: x')
