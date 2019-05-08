module mod_arrays
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
