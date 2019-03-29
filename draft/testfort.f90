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

  subroutine ones_1d(vec, n)
    real(8), allocatable, intent(out) :: vec(:)
    integer, intent(in) :: n
    allocate(vec(n))
    vec = 1.0d0
  end subroutine ones_1d

  subroutine ones_2d(arr, m, n)
    real(8), allocatable, intent(out) :: arr(:,:)
    integer, intent(in) :: m, n
    allocate(arr(m,n))
    arr = 1.0d0
  end subroutine ones_2d
  
  subroutine test_array_2d(arr)
    real(8), intent(inout) :: arr(:,:)
    integer :: k, l, m, n

    m = size(arr, 1)
    n = size(arr, 2)

    do l = 1, n
      do k = 1, m
        arr(k,l) = arr(k,l)*k*l
      end do
    end do
  end subroutine test_array_2d
  
end module testfort

program main
  use testfort
  implicit none

  real(8), allocatable :: y(:)
  real(8), allocatable :: z(:,:)
  
  integer :: k, l, m, n

  call ones_1d(y, 15)
  print *, y
  call test_vector(y)
  print *, y

  call ones_2d(z, 3, 2)
  call test_array_2d(z)
  print *, z
  
  
  m = size(z, 1)
  n = size(z, 2)

  do k = 1, m
      print *, z(k, :)
  end do
  
  deallocate(z)
  deallocate(y)
end program main
