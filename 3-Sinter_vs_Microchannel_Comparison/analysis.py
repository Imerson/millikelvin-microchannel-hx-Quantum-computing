#!/usr/bin/env python3
"""
Sinter vs microchannel: analytic thermal-hydraulic comparison.
Figure of merit = thermal conductance / pumping power  (Q_removed per unit pump power).

Microchannel  : Delta P from the converged CFD cases (cross-checked vs Hagen-Poiseuille);
                Kapitza resistance over the exact geometric wetted area.
Sinter        : Delta P from Darcy's law with Kozeny-Carman permeability (Stokes regime,
                Re_pore << 1 so the Ergun inertial term is negligible); Kapitza resistance
                over the packed-sphere surface area. Idealised (full microscopic) area is the
                sinter's best case; the He-4 effective area is far smaller (Nakagawa 2023).

All cases compared on a normalised 40 x 40 x 100 mm block, same He-4 coolant, same
superficial velocity (hence same volumetric throughput). The FOM ratio is shown to be
independent of velocity and temperature.
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------- inputs -----------------------------
L, W, Hh = 0.100, 0.040, 0.040;  Aface = W*Hh           # block (m), face area
mu, rho  = 1.0e-6, 145.0                                 # He-4 effective medium
Tref     = 0.025                                         # interface temperature (K) = CFD value
CK       = {"Cu": 0.020, "Ag": 0.005}                    # Kapitza coeff (K^4 m^2 / W)
U_ch     = 1.0e-3                                         # microchannel per-channel velocity (m/s)
open_fr  = 1.0/1.5**2                                     # channel open-area fraction (pitch 1.5 Dh)
Us       = open_fr*U_ch                                   # common superficial velocity (m/s)
Vdot     = Us*Aface                                       # common volumetric flow (m^3/s)
dp, eps  = 0.07e-6, 0.50                                  # sinter particle (m), porosity (baseline)

def RK(Awet, mat, T=Tref): return CK[mat]/(T**3*Awet)     # system Kapitza resistance (K/W)

# ----------------------------- microchannel (CFD) -----------------------------
MC = [  # material, Dh_mm, N_ch, A_wet(m2), dP_CFD(Pa)
    ("Cu",0.5,2809,0.5618,1.137e-2), ("Cu",1.0,676,0.2704,2.923e-3), ("Cu",2.0,169,0.1352,8.078e-4),
    ("Ag",0.5,2809,0.5618,1.137e-2), ("Ag",1.0,676,0.2704,2.923e-3), ("Ag",2.0,169,0.1352,8.078e-4)]
mc_rows=[]
for mat,Dh,Nch,Awet,dPcfd in MC:
    Dhm=Dh*1e-3
    dP_HP=28.45*mu*U_ch*L/Dhm**2                          # square-duct Hagen-Poiseuille (Po~56.9)
    Rk=RK(Awet,mat); G=1/Rk; Wp=dPcfd*Vdot
    mc_rows.append(dict(geom="microchannel",mat=mat,Dh=Dh,Awet=Awet,dP=dPcfd,dP_HP=dP_HP,
                        Rk=Rk,G=G,Wp=Wp,FOM=G/Wp))

# ----------------------------- sinter (Darcy + Kozeny-Carman) -----------------------------
def kperm(eps,dp): return eps**3*dp**2/(180*(1-eps)**2)
def a_v(eps,dp):   return 6*(1-eps)/dp
k   = kperm(eps,dp)
av  = a_v(eps,dp)
A_ideal = av*Aface*L
dP_s    = mu*Us*L/k                                       # Darcy
Re_pore = rho*Us*dp/mu
sin_rows=[]
for mat in ("Cu","Ag"):
    Rk=RK(A_ideal,mat); G=1/Rk; Wp=dP_s*Vdot
    sin_rows.append(dict(geom="sinter_ideal",mat=mat,Dh=dp*1e6,Awet=A_ideal,dP=dP_s,
                         Rk=Rk,G=G,Wp=Wp,FOM=G/Wp))

# ----------------------------- sanity checks -----------------------------
print("="*70,"\nSANITY CHECKS\n","="*70)
print(f"microchannel dP CFD vs Hagen-Poiseuille (ratio should be ~1):")
for r in mc_rows[:3]:
    print(f"  Dh={r['Dh']}: CFD={r['dP']:.3e}  HP={r['dP_HP']:.3e}  ratio={r['dP']/r['dP_HP']:.2f}")
print(f"sinter Darcy validity: Re_pore = {Re_pore:.2e}  (<<1 -> Darcy ok, Ergun term negligible)")
print(f"sinter permeability k = {k:.3e} m^2 ; A_ideal = {A_ideal:.0f} m^2 ; Darcy dP = {dP_s:.3e} Pa")
# FOM ratio invariance to velocity and temperature
def fom_ratio(Uc,T):
    Us2=open_fr*Uc; Vd2=Us2*Aface
    G_mc=1/RK(0.5618,"Ag",T); Wp_mc=(1.137e-2*(Uc/U_ch))*Vd2
    G_s =1/RK(A_ideal,"Ag",T); Wp_s=(mu*Us2*L/k)*Vd2
    return (G_mc/Wp_mc)/(G_s/Wp_s)
r0=fom_ratio(U_ch,Tref)
print(f"FOM ratio (MC Ag0.5 / sinter Ag) invariance:")
for Uc in (0.1e-3,1e-3,10e-3):
    for T in (0.015,0.025): print(f"   U={Uc*1e3:4.1f} mm/s, T={T*1e3:.0f} mK -> ratio/baseline = {fom_ratio(Uc,T)/r0:.4f}")

# ----------------------------- plots -----------------------------
allr=mc_rows+sin_rows
labels=[f"{r['mat']}\n{('%.1fmm'%r['Dh']) if r['geom']=='microchannel' else 'sinter'}" for r in allr]
col=['#185FA5' if r['geom']=='microchannel' else '#993C1D' for r in allr]
def barplot(key,title,ylab,fname,logy=True):
    fig,ax=plt.subplots(figsize=(8,4.2))
    ax.bar(range(len(allr)),[r[key] for r in allr],color=col)
    ax.set_xticks(range(len(allr))); ax.set_xticklabels(labels,fontsize=8)
    if logy: ax.set_yscale('log')
    ax.set_ylabel(ylab); ax.set_title(title); ax.grid(axis='y',alpha=.3)
    fig.tight_layout(); fig.savefig(fname,dpi=160); plt.close(fig)
barplot('dP','Pressure drop (matched superficial velocity)','$\\Delta P$ (Pa)','fig_dP.png')
barplot('G','Thermal conductance','$G=1/R_{\\mathrm{total}}$ (W/K)','fig_conductance.png')
barplot('Wp','Pumping power','$\\dot W_{\\mathrm{pump}}$ (W)','fig_pumping.png')
barplot('FOM','Figure of merit: conductance per pumping power','$G/\\dot W_{\\mathrm{pump}}$ (1/K)','fig_FOM.png')

# FOM vs velocity (robustness)
Uc=np.logspace(-4.5,-2,40)
fig,ax=plt.subplots(figsize=(7.5,4.2))
for mat,c in (("Ag",'#185FA5'),):
    G_mc=1/RK(0.5618,mat); fom_mc=G_mc/((1.137e-2*(Uc/U_ch))*(open_fr*Uc*Aface))
    G_s=1/RK(A_ideal,mat); fom_s=G_s/((mu*open_fr*Uc*L/k)*(open_fr*Uc*Aface))
    ax.loglog(Uc*1e3,fom_mc,'-',color='#185FA5',label='microchannel Ag 0.5 mm')
    ax.loglog(Uc*1e3,fom_s,'-',color='#993C1D',label='sinter Ag (idealised)')
ax.set_xlabel('per-channel velocity (mm/s)'); ax.set_ylabel('$G/\\dot W_{\\mathrm{pump}}$ (1/K)')
ax.set_title('FOM vs flow: gap is velocity-independent'); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig_FOM_vs_velocity.png',dpi=160); plt.close(fig)

print("\nSaved: fig_dP, fig_conductance, fig_pumping, fig_FOM, fig_FOM_vs_velocity (.png)")
print(f"\nHEADLINE: microchannel beats idealised sinter on FOM by "
      f"{mc_rows[3]['FOM']/sin_rows[1]['FOM']:.0f}x (Ag 0.5mm vs Ag sinter).")
