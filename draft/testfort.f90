module testfort
  implicit none
  
contains
  
  subroutine test_vector(vec)
    real(8), intent(inout) :: vec(:)
    integer :: k, n
    
    n = size(vec)
    
    do k = 1, n
      vec(k) = vec(k)*k
    end do
  end subroutine test_vector

  function test_alloc_vector() result(y)
    real(8), allocatable :: y(:)
    allocate(y(20))
    y = 2.0d0
  end function test_alloc_vector

end module testfort