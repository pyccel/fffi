program test_arrays
  use mod_arrays
  implicit none

  real(8), allocatable :: y(:)
  real(8), allocatable :: z(:,:)

  integer :: k, l, m, n

  ! Test 1
  m = 15
  call ones_1d(y, m)
  m = size(y, 1)
  call test_vector(y)
  do k = 1, m
    write(*, '(Es11.5)') y(k)
  end do

  print *
  print *

  call ones_2d(z, 3, 2)
  call test_array_2d(z)

  m = size(z, 1)
  n = size(z, 2)

  ! printing columns of z
  do l = 1, n
    do k = 1, m
      write(*, '(Es11.5)') z(k, l)
    end do
    print *
  end do


  deallocate(z)
  deallocate(y)

contains

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
  
end program test_arrays
