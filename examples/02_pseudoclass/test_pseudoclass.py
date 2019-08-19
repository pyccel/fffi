from fffi import fortran_library, fortran_module

lib = fortran_library('pseudoclass')
classmod = fortran_module(lib, 'class_circle')

# member variable and subroutine definition stub
# TODO: parse fortmod.f90 automatically and strip away implementation
classmod.fdef("""
type Circle
  double precision :: radius
end type

subroutine circle_print(self)
  type(Circle), intent(in) :: self
end
""")

lib.compile()  # only required when Fortran library has changed
classmod.load()

cir = classmod.new('Circle')
cir.radius = 3.0
classmod.circle_print(cir)
