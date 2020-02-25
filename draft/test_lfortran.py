from lfortran.ast import src_to_ast, print_tree
from lfortran.ast.ast_to_src import ast_to_src
from lfortran.semantic.ast_to_asr import ast_to_asr
from lfortran.asr.pprint import pprint_asr

src = """\
integer function f(a, b) result(r)
integer(kind=dp), intent(in) :: a, b
r = a + b
end function
"""

ast = src_to_ast(src, translation_unit=False)
asr = ast_to_asr(ast)

print_tree(ast)
pprint_asr(asr)
