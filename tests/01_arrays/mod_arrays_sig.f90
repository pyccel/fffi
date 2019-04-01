subroutine ones_1d(vec, n)
  real(8), allocatable, intent(out) :: vec(:)
  integer, intent(in) :: n
end subroutine ones_1d

subroutine ones_2d(arr, m, n)
  real(8), allocatable, intent(out) :: arr(:,:)
  integer, intent(in) :: m, n
end subroutine ones_2d

subroutine test_vector(vec)
  real(8), intent(inout) :: vec(:)
end subroutine test_vector

subroutine test_array_2d(arr)
  real(8), intent(inout) :: arr(:,:)
end subroutine test_array_2d
