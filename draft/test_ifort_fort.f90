subroutine test(x)
    double precision, intent(inout) :: x(:)
    integer :: k
    
    do k=1,size(x)
        x(k) = 1d0*k
    end do
end subroutine test