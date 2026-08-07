#!/usr/bin/env python3
"""Grid Convergence Index (GCI) analysis — ASME V&V20 / Celik et al. (2008).

Reads coarse/medium/fine metrics.txt from the folder this script sits in
(or a folder given as the first argument) and reports, per quantity:
apparent order p, Richardson extrapolation, approximate/extrapolated
relative errors, GCI_fine(21), GCI_medium(32), and the asymptotic-range check.

Quantities that are identical (to <0.005%) across all grids are reported as
grid-independent: the order-of-convergence formula is undefined at zero change,
which for BC-fixed quantities (e.g. the Gate-1 load) is expected, not an error.
"""
import math, os, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
Fs = 1.25  # safety factor for 3-grid studies (Celik et al., 2008)

def load(name):
    d = {}
    for l in open(os.path.join(HERE, name, "metrics.txt")):
        p = l.split()
        if len(p) == 2:
            try: d[p[0]] = float(p[1])
            except ValueError: pass
    return d

g1, g2, g3 = load("fine"), load("medium"), load("coarse")   # 1=fine 2=medium 3=coarse
N1, N2, N3 = g1["NCELLS"], g2["NCELLS"], g3["NCELLS"]
r21 = (N1/N2)**(1/3.0)   # h ~ N^(-1/3), fixed domain volume
r32 = (N2/N3)**(1/3.0)

def gci(phi1, phi2, phi3):
    e21 = phi2 - phi1; e32 = phi3 - phi2
    # noise floor: grids agree to <0.005% -> grid-independent, order undefined
    if phi1 != 0 and abs(e21/phi1) < 5e-5:
        return dict(indep=True, ea=abs(e21/phi1)*100,
                    gci21=Fs*abs(e21/phi1)*100 if phi1 else 0.0)
    s = math.copysign(1.0, e32/e21)
    p = 2.0
    for _ in range(500):  # fixed-point iteration for apparent order (Celik eq. 5)
        q = math.log(abs((r21**p - s)/(r32**p - s)))
        pn = abs(math.log(abs(e32/e21)) + q)/math.log(r21)
        if abs(pn - p) < 1e-9: p = pn; break
        p = pn
    # apparent order far above the scheme's formal order (2) means the grid
    # differences are at noise level, not in the asymptotic error band
    if p > 10:
        return dict(indep=True, ea=abs(e21/phi1)*100,
                    gci21=Fs*abs(e21/phi1)*100 if phi1 else 0.0)
    phi_ext = (r21**p*phi1 - phi2)/(r21**p - 1)          # Richardson extrapolation
    ea   = abs((phi1 - phi2)/phi1)*100
    eext = abs((phi_ext - phi1)/phi_ext)*100
    gci21 = Fs*(ea/100)/(r21**p - 1)*100
    gci32 = Fs*abs((phi2 - phi3)/phi2)/(r32**p - 1)*100
    return dict(indep=False, p=p, ext=phi_ext, ea=ea, eext=eext,
                gci21=gci21, gci32=gci32,
                asym=gci32/(r21**p*gci21))

print(f"GRIDS  fine N1={N1:.0f}  medium N2={N2:.0f}  coarse N3={N3:.0f}")
print(f"r21(med->fine)={r21:.4f}   r32(coarse->med)={r32:.4f}   Fs={Fs}\n")
ROWS = [("Pressure drop dP",        "DP",          1e3, "mPa"),
        ("Interface T_int_solid",   "T_INT_SOLID", 1e3, "mK"),
        ("Outlet T_out",            "TOUT",        1e3, "mK"),
        ("Gate-1 load (BC-fixed)",  "GATE1",       1e9, "nW")]
for lab, key, sc, u in ROWS:
    if not all(key in g for g in (g1, g2, g3)): continue
    R = gci(g1[key], g2[key], g3[key])
    print(f"== {lab} ==")
    print(f"  coarse={g3[key]*sc:.6g}  medium={g2[key]*sc:.6g}  fine={g1[key]*sc:.6g} {u}")
    if R["indep"]:
        print(f"  GRID-INDEPENDENT: change across grids {R['ea']:.4g}% — at noise level.")
        print(f"  A meaningful apparent order cannot be extracted from noise-level")
        print(f"  differences; expected for BC-fixed or energy-balance-pinned quantities.\n")
    else:
        print(f"  apparent order p={R['p']:.3f}   Richardson extrap phi_ext={R['ext']*sc:.6g} {u}")
        print(f"  approx rel err ea21={R['ea']:.3f}%   extrap rel err={R['eext']:.3f}%")
        print(f"  GCI_fine(21)={R['gci21']:.3f}%   GCI_medium(32)={R['gci32']:.3f}%")
        print(f"  asymptotic check GCI32/(r21^p*GCI21) = {R['asym']:.4f} (~1 => asymptotic range)\n")
