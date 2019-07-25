module fortmod
	
   implicit none
	
   ! parameters are not exported as shared library symbols
   ! TODO: automatically import by parsing and setting value
   double precision, parameter  :: twopi = 6.28318530717958d0 
  
   double precision :: member
   double precision, dimension(3) :: member_array
    
   ! TODO: allow handling of assumed size module members
   double precision, allocatable, dimension(:) :: alloc_member

contains
   
   subroutine modify_vector(z, k)
     double precision, dimension(:), intent(inout) :: z
     integer, intent(in) :: k
     
     z = sin(k*twopi*z)
   end subroutine modify_vector
   
   
   subroutine modify_matrix(A, x)
     double precision, dimension(:,:), intent(inout) :: A
     double precision, intent(in) :: x
     
     A = x*transpose(A)
   end subroutine modify_matrix
   
   subroutine init()
     member = 1.0
     member_array = 1.0
   end subroutine init
   
   subroutine side_effects()
     member = member + 1.0
     member_array = 2.0*member_array
   end subroutine side_effects
   
end module fortmod
