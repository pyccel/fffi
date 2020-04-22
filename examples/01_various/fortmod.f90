module fortmod
	
   implicit none
	
   ! parameters are not exported as shared library symbols
   ! TODO: automatically import by parsing and setting value
   double precision, parameter  :: twopi = 6.28318530717958d0 
  
   double precision :: member
   double precision, dimension(3) :: member_array
   complex(8), dimension(:), allocatable :: alloc_array

contains
   
  subroutine modify_vector(z, k)
    double precision, dimension(:), intent(inout) :: z
    integer, intent(in) :: k
    
    z = sin(k*twopi*z)
  end subroutine
  
  
  subroutine modify_matrix(A, x)
    double precision, dimension(:,:), intent(inout) :: A
    double precision, intent(in) :: x
    
    A = x*transpose(A)
  end subroutine
  
  subroutine init()
    member = 1.0
    member_array = 1.0
  end subroutine
  
  subroutine side_effects()
    member = member + 1.0
    member_array = 2.0*member_array
  end subroutine

  subroutine alloc_member()
    allocate(alloc_array(5)) 
    alloc_array = (1d0, 2d0)
  end subroutine
   
end module fortmod
