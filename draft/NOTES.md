gfortran 7.3.0 produces the following .so for the pseudoclass (tests/ex02):

0000000000201064 B __bss_start
0000000000000acc T __class_circle_MOD_circle_area
00000000000009e8 T __class_circle_MOD_circle_print
00000000000009ca T __class_circle_MOD___copy_class_circle_Circle
0000000000201068 B __class_circle_MOD___def_init_class_circle_Circle
0000000000200de0 D __class_circle_MOD___vtab_class_circle_Circle
                 w __cxa_finalize
0000000000201064 D _edata
0000000000201070 B _end
0000000000000b5c T _fini
                 U _gfortran_set_args@@GFORTRAN_7
                 U _gfortran_set_options@@GFORTRAN_7
                 U _gfortran_st_write_done@@GFORTRAN_7
                 U _gfortran_st_write@@GFORTRAN_7
                 U _gfortran_transfer_character_write@@GFORTRAN_7
                 U _gfortran_transfer_real_write@@GFORTRAN_7
                 w __gmon_start__
0000000000000830 T _init
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000000b1c T main

... and for the real class (tests/ex03):

000000000020105c B __bss_start
0000000000000afe T __class_circle_MOD_circle_area
0000000000000a08 T __class_circle_MOD_circle_print
00000000000009ea T __class_circle_MOD___copy_class_circle_Circle
0000000000201060 B __class_circle_MOD___def_init_class_circle_Circle
0000000000200dc0 D __class_circle_MOD___vtab_class_circle_Circle
                 w __cxa_finalize
000000000020105c D _edata
0000000000201068 B _end
0000000000000ba4 T _fini
                 U _gfortran_set_args@@GFORTRAN_7
                 U _gfortran_set_options@@GFORTRAN_7
                 U _gfortran_st_write_done@@GFORTRAN_7
                 U _gfortran_st_write@@GFORTRAN_7
                 U _gfortran_transfer_character_write@@GFORTRAN_7
                 U _gfortran_transfer_real_write@@GFORTRAN_7
                 w __gmon_start__
0000000000000860 T _init
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000000b64 T main



Intel Fortran 18.0.3 does the following for the pseudoclass (tests/ex02):

0000000000201058 B __bss_start
0000000000000ac0 T class_circle._
0000000000000aa0 T class_circle_mp_circle_area_
00000000000009d0 T class_circle_mp_circle_print_
0000000000201050 D class_circle_mp_pi_
                 w __cxa_finalize@@GLIBC_2.2.5
0000000000201058 D _edata
0000000000201070 B _end
0000000000000ad0 T _fini
                 U for_set_reentrancy
                 U for_write_seq_lis
                 U for_write_seq_lis_xmit
                 w __gmon_start__
00000000000007f8 T _init
                 U __intel_new_feature_proc_init
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000000970 T MAIN__

... and for the real class (tests/ex03):

0000000000201050 B __bss_start
0000000000000b20 T class_circle._
0000000000000b30 T class_circle_mp_circle_area_
0000000000000a50 T class_circle_mp_circle_print_
0000000000201048 D class_circle_mp_pi_
                 w __cxa_finalize@@GLIBC_2.2.5
0000000000201050 D _edata
0000000000201068 B _end
0000000000000b50 T _fini
                 U for_set_reentrancy
                 U for_write_seq_lis
                 U for_write_seq_lis_xmit
                 w __gmon_start__
0000000000000828 T _init
                 U __intel_new_feature_proc_init
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000000990 T MAIN__
