subroutine test_string(s)
    character(len=*), intent(in) :: s

    print *, s
end subroutine test_string

program main_test_str
    call test_string("Hello, Fortran!")
end program main_test_str
