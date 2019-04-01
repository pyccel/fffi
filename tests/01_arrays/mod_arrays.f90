module mod_arrays
  implicit none

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

  subroutine test_vector(vec)
    real(8), intent(inout) :: vec(:)
    integer :: k, n

    n = size(vec)

    do k = 1, n
      vec(k) = vec(k)*k
    end do
  end subroutine test_vector

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

end module mod_arrays
