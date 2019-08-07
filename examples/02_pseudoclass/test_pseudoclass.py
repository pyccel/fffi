from fffi import fortran_library, fortran_module

lib = fortran_library('pseudoclass')
classmod = fortran_module(lib, 'class_Circle')

# member variable and subroutine definition stub
# TODO: parse fortmod.f90 automatically and strip away implementation
classmod.fdef("""
type Circle
end type
""")

lib.compile()  # only required when Fortran library has changed
classmod.load()
