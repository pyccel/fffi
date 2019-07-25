"""
Created: Thu Jul 25 12:29:27 2019
@author: Christopher Albert <albert@alumni.tugraz.at>
"""

#%% Import, compile and load
from numpy import array, linspace
from fffi import fortran_library, fortran_module

libfortmod = fortran_library('fortmod')
fortmod = fortran_module(libfortmod, 'fortmod')

# member variable and subroutine definition stub
# TODO: parse fortmod.f90 automatically and strip away implementation
fortmod.fdef("""
   double precision :: member
   double precision, dimension(3) :: member_array
   
   subroutine modify_vector(z, k)
     double precision, dimension(:), intent(inout) :: z
     integer, intent(in) :: k
   end
   
   subroutine modify_matrix(A, x)
     double precision, dimension(:,:), intent(inout) :: A
     double precision, intent(in) :: x
   end
   
   subroutine init()
   end
   
   subroutine side_effects()
   end 
""")

libfortmod.compile()  # only required when Fortran library has changed
fortmod.load()

#%% Try some stuff

print('Before init(): member = {}'.format(fortmod.member))
fortmod.init()
print('After init(): member = {}'.format(fortmod.member))

a = fortmod.member_array  # this is a mutable reference
print('Before side_effects(): member_array = {}'.format(a))
fortmod.side_effects()
print('After side_effects(): member_array = {}'.format(a))

z = linspace(1, 10, 4)
print('Before modify_vector(z, 4): z = {}'.format(z))
fortmod.modify_vector(z, 4)
print('After modify_vector(z, 4): z = {}'.format(z))

A = array([[1,2],[3,4]], order='F')
print('Before modify_matrix(A, 1): z = {}'.format(A))
fortmod.modify_matrix(A, 1.0)
print('After modify_matrix(A, 1): z = {}'.format(A))
