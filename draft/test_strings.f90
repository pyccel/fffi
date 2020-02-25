subroutine test0
    print *, "TEST0"
end subroutine test0

subroutine test_string(s)
    character(len=*), intent(in) :: s

    print *, s
end subroutine test_string

program main_test_str
    call test_string("TEEEEST")
end program main_test_str
