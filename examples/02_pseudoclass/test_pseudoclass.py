from fffi import FortranLibrary, FortranModule

lib = FortranLibrary('pseudoclass')
classmod = FortranModule(lib, 'class_circle')

classmod.fdef("""
type Circle
  double precision :: radius
end type

subroutine circle_print(self)
  type(Circle), intent(in) :: self
end
""")

lib.compile()
classmod.load()

cir = classmod.new('Circle')
cir.radius = 3.0

print('Radius: {}'.format(cir.radius))
print('Fortran output:')
classmod.circle_print(cir)

#
# To print Fortran stdout in Jupyter/IPython REPL:
#
# from wurlitzer import sys_pipes()
# with sys_pipes():  # required to print Fortran stdout in Jupyter
#     classmod.circle_print(cir)
#