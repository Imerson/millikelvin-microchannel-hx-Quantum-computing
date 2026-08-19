#!/usr/bin/env python3
# 1 uW load-envelope table — SAME hybrid closure as generate_comparison.py (R_K = C_K/T_int^3,
# dT_K = (Q_model/A_wet) R_K, T_chip = T_int + dT_K), applied at Q_sys = 1 uW.
#
# T_int source: at 1 uW the two-seed CFD bracket (S4_1uW/*_s10p5, *_s12p5) shows the conjugate
# field's temperature LEVEL is undetermined (T_int stays at whichever seed it is given, moving
# < 1 uK in 2000 iterations), while the CFD still verifies the load (Gate 1) and hydraulics (dP).
# The closure therefore takes T_int from the fluid ENERGY BALANCE that anchors it at 15 uW:
#     T_int = T_bath + f_adv * Q_model / (5 * mdot * c_p)
# with f_adv the advected fraction of the load measured in the converged 15 uW case of the same
# geometry (Gate 2: ~0.5, the fixed-T-inlet back-conduction). Everything else is the 15 uW model.
import glob
BASE="/home/ubuntu/cases"; TBATH=0.010; CP=5.0; QSYS_1UW=1.0e-6; QSYS_15=15.0e-6
CASES=[  # dir15uW, label, mat, Dh, Nch, A_wet(m2), C_K
  ("S4_MC_Cu_0p5_hyb","Cu_0p5","Cu",0.5,2809,1.0e-3,0.020),
  ("S4_MC_Cu_1p0",    "Cu_1p0","Cu",1.0, 676,2.0e-3,0.020),
  ("S4_MC_Cu_2p0",    "Cu_2p0","Cu",2.0, 169,4.0e-3,0.020),
  ("S4_MC_Ag_0p5",    "Ag_0p5","Ag",0.5,2809,1.0e-3,0.005),
  ("S4_MC_Ag_1p0",    "Ag_1p0","Ag",1.0, 676,2.0e-3,0.005),
  ("S4_MC_Ag_2p0",    "Ag_2p0","Ag",2.0, 169,4.0e-3,0.005),
]
def gg(d,name):
    fs=sorted(glob.glob(f"{d}/postProcessing/*/{name}/*/*.dat"),key=lambda f:int(f.split('/')[-2]))
    return float([l for l in open(fs[-1]) if l.strip() and not l.startswith('#')][-1].split()[1])
def metrics(d):
    m={}
    for l in open(f"{d}/metrics.txt"):
        k,v=l.split(); m[k]=float(v)
    return m

rows=[]; ev=[]
for d15,lab,mat,Dh,Nch,Aw,CK in CASES:
    Qm=QSYS_1UW*5/Nch
    # --- 15 uW case: measured advected fraction (Gate 2) and mass flow ---
    p=f"{BASE}/{d15}"
    MD=abs(gg(p,"massFlowInlet")); TO15=gg(p,"T_outlet_fluid"); QC15=abs(gg(p,"Q_chipFace"))
    f_adv=5*MD*CP*(TO15-TBATH)/QC15
    # --- 1 uW CFD bracket: what the CFD verified, and the level degeneracy ---
    b1=metrics(f"{BASE}/S4_1uW/{lab}_s10p5"); b2=metrics(f"{BASE}/S4_1uW/{lab}_s12p5")
    QC1=abs(b1["QCHIP"]); dP1=b1["DP"]; dP15=gg(p,"p_inlet")-gg(p,"p_outlet")
    # --- energy-balance interface temperature (the closure input) ---
    TS=TBATH + f_adv*Qm/(5*MD*CP)
    RK=CK/TS**3; dTK=(Qm/Aw)*RK; Tphys=TS+dTK
    Rtot=(Tphys-TBATH)/Qm; kfrac=dTK/(Tphys-TBATH)*100
    rows.append((lab,mat,Dh,Nch,Qm,QC1,f_adv,TS,RK,dTK,Tphys,Rtot,kfrac,dP1))
    ev.append((lab,QC1,QC15,dP1,dP15,b1,b2))

hdr="case   mat  Dh   N_ch   Q_mod   Gate1_1uW  f_adv  T_int(EB)  R_K        dT_K    T_chip  R_total    Kap%   dP"
units="              mm          nW      nW              mK         m2K/W      mK      mK      K/W             Pa"
L=["S4 Stage-4 Microchannel HX — 1 uW LOAD ENVELOPE (hybrid closure, same as 15 uW: R_K=C_K/T^3)",
   "Q_sys = 1 uW; Q_model = Q_sys*5/N_ch verified by CFD at chipFace (Gate 1). T_int from fluid energy balance",
   "(T_bath + f_adv*Q_model/(5 mdot c_p), f_adv = advected fraction measured in the 15 uW case, Gate 2).","",hdr,units,"-"*len(hdr)]
csv=["case,material,Dh_mm,N_ch,Q_model_nW,Gate1_1uW_nW,f_adv,T_int_EB_mK,R_K_m2KW,dT_K_mK,T_chip_mK,R_total_KW,Kapitza_pct,dP_Pa"]
for lab,mat,Dh,Nch,Qm,QC1,fa,TS,RK,dTK,Tp,Rt,kf,dP in rows:
    L.append(f"{lab:6} {mat:3}  {Dh:<3} {Nch:5}  {Qm*1e9:6.2f}  {QC1*1e9:8.3f}  {fa:5.3f}  {TS*1e3:8.3f}  {RK:9.1f}  {dTK*1e3:6.2f}  {Tp*1e3:6.2f}  {Rt:.3e}  {kf:4.0f}  {dP:.3e}")
    csv.append(f"{lab},{mat},{Dh},{Nch},{Qm*1e9:.3f},{QC1*1e9:.4f},{fa:.4f},{TS*1e3:.4f},{RK:.1f},{dTK*1e3:.3f},{Tp*1e3:.3f},{Rt:.4e},{kf:.1f},{dP:.4e}")
L+=["","CFD BRACKET EVIDENCE (two solid seeds, 2000 iterations each):",
    "case    Gate1: 1uW/15uW ratio   dP: 1uW vs 15uW        T_int seed 10.5 -> end   seed 12.5 -> end   (level undetermined)"]
for lab,QC1,QC15,dP1,dP15,b1,b2 in ev:
    L.append(f"{lab:6}  {QC1/QC15:.5f} (=1/15)      {dP1:.4e} / {dP15:.4e}   "
             f"{b1['TINT_FIRST']*1e3:.4f}->{b1['TINT_LAST']*1e3:.4f} mK   {b2['TINT_FIRST']*1e3:.4f}->{b2['TINT_LAST']*1e3:.4f} mK")
L+=["","READING:",
    " - CFD at 1 uW verifies the load (Gate 1 = exactly 1/15 of the 15 uW value) and the hydraulics (dP unchanged:",
    "   the flow does not see the load). Interface remains coupled and isothermal (solid = fluid side).",
    " - The conjugate temperature LEVEL is undetermined at 1 uW: T_int stays at whichever seed it is given",
    "   (moves < 1 uK in 2000 it, both seeds). At 15 uW the ~15 mK fluid warming anchors the level; at 1 uW the",
    "   ~1 mK warming cannot, against a 13 W/mK solid coupled through a 1e-3 W/mK fluid. This is the same",
    "   level-mode degeneracy identified for the meshed-Kapitza case, reappearing at weak load.",
    " - The closure therefore uses the energy-balance T_int (the quantity that anchors the level at 15 uW),",
    "   which is a physics statement, not a CFD output; the CFD run is what justifies using it.",
    " - Steep R_K ~ T^-3 at the colder interface makes the low-load regime unforgiving: only Ag_0p5 sits in the",
    "   10-20 mK band; Ag_1p0 marginal; every Cu case exceeds it."]
open(f"{BASE}/comparison_1uW.txt","w").write("\n".join(L)+"\n")
open(f"{BASE}/comparison_1uW.csv","w").write("\n".join(csv)+"\n")
print("\n".join(L))
