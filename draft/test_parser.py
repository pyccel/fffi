# -*- coding: utf-8 -*-

from fffi.parser import parse

if __name__ == '__main__':
    ast = parse('INTEGER :: x')
    ast = parse('integer :: x')
    ast = parse('INTEGER  x')
    ast = parse('INTEGER, PARAMETER ::  x')
    ast = parse('DOUBLE PRECISION :: y')
    ast = parse('INTEGER, DIMENSION(:) :: x')
    ast = parse('INTEGER, DIMENSION(:10) :: x')
    ast = parse('INTEGER, DIMENSION(10:) :: x')
    ast = parse('INTEGER, DIMENSION(10) :: x')
    ast = parse('INTEGER, DIMENSION(10:20) :: x')
    ast = parse('INTEGER, DIMENSION(10:20) :: x, y, z')
    ast = parse('''
                subroutine test(x, y)
                  integer, dimension(:), intent(out) :: x
                  integer :: y(:,:), z(:)
                end

                SUBROUTINE tes
                  integer, intent(out) :: a
                  integer :: b
                end
                ''')
    print(ast.subprograms['test'].namespace['x'].rank)
    print(ast.subprograms['test'].namespace['y'].rank)