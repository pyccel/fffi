src = """
  subroutine init_field(ans_s, ans_tp, amultharm, aintegmode)
    integer :: ans_s, ans_tp, amultharm, aintegmode
  end subroutine init_field

  subroutine init_params(Z_charge, m_mass, E_kin, adtau, adtaumax, arelerr)
    integer :: Z_charge, m_mass
    real :: E_kin, adtau, adtaumax
    real :: arelerr
  end subroutine init_params

  subroutine init_integrator(z0)
    real, intent(in) :: z0(:)
  end subroutine init_integrator

  subroutine timestep_z(z, ierr)
    real :: z(:)
    integer :: ierr
  end subroutine timestep_z

  subroutine timestep_sympl_z(z, ierr)
    real :: z(:)
    integer :: ierr
  end subroutine timestep_sympl_z

  subroutine spline_vmec(s, theta, varphi, A_phi, A_theta, dA_phi_ds, dA_theta_ds, aiota, R, Z, alam, dR_ds, dR_dt, dR_dp, dZ_ds, dZ_dt, dZ_dp, dl_ds, dl_dt, dl_dp)
    real, intent(in) :: s, theta, varphi
    real, intent(out) :: A_phi,A_theta,dA_phi_ds,dA_theta_ds,aiota,R,Z,alam,dR_ds,dR_dt,dR_dp,dZ_ds,dZ_dt,dZ_dp,dl_ds,dl_dt,dl_dp
  end subroutine spline_vmec

  subroutine field_vmec(s,theta,varphi,A_theta,A_phi,dA_theta_ds,dA_phi_ds, aiota, sqg,alam,dl_ds,dl_dt,dl_dp,Bctrvr_vartheta,Bctrvr_varphi, Bcovar_r,Bcovar_vartheta,Bcovar_varphi)
    real :: s,theta,varphi,A_phi,A_theta,dA_phi_ds,dA_theta_ds,aiota, R,Z,alam,dR_ds,dR_dt,dR_dp,dZ_ds,dZ_dt,dZ_dp,dl_ds,dl_dt,dl_dp
    real :: Bctrvr_vartheta,Bctrvr_varphi,Bcovar_r,Bcovar_vartheta,Bcovar_varphi,sqg
  end subroutine field_vmec
"""

src2 = """
subroutine init_field(ans_s, ans_tp, amultharm, aintegmode)
  integer :: ans_s, ans_tp, amultharm, aintegmode
end
"""
#ast = src_to_ast(src, translation_unit=False)
#print_tree(ast[2])

#%%
from fffi.parser import parse

ast = parse(src2)

# %%
