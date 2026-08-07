"""Fig. 2.3 - three-grid GCI study (values from S4_Mesh_Independence/gci_results.txt)."""
import numpy as np
import matplotlib.pyplot as plt
from common import THESIS, C_CU, C_AG

cells = np.array([73920, 208320, 367200])
dP    = np.array([11.2522, 11.3736, 11.4099])    # [mPa]
dPext = 11.48                                     # Richardson extrapolate
Tint  = np.array([24.99693, 24.99703, 24.99731])  # [mK]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.4), gridspec_kw={'wspace': 0.32})
h = cells**(-1/3)
a1.plot(h*1e2, dP, 'o-', color='#1E2761', lw=1.5)
a1.axhline(dPext, ls='--', color=C_CU, lw=1.2)
a1.text(1.42, dPext-0.018, r'Richardson $\Delta P_\mathrm{ext}=11.48$ mPa',
        fontsize=8, color=C_CU, va='top')
labs = ['fine (367k)', 'medium (208k, production)', 'coarse (74k)']
offs = [(8, -4), (8, -4), (-12, 8)]
for x, y, lab, off in zip(h*1e2, dP, labs, offs):
    a1.annotate(lab, (x, y), textcoords='offset points', xytext=off, fontsize=7.5,
                ha='left' if off[0] > 0 else 'right')
a1.set_xlabel(r'Representative cell size $h\propto N^{-1/3}$ [$\times10^{-2}$]')
a1.set_ylabel(r'$\Delta P$ [mPa]')
a1.set_ylim(11.20, 11.54)
a1.set_title('(a) Pressure drop: monotonic, $p=2.20$', fontsize=9)
a2.plot(cells/1e3, (Tint-25)*1e3, 's-', color=C_AG, lw=1.5)
a2.set_xlabel(r'Cells [$\times10^{3}$]')
a2.set_ylabel(r'$T_\mathrm{int}-25\,$mK  [$\mu$K]')
a2.set_title('(b) Interface temperature:\ngrid-independent (variation $<0.2\\,\\mu$K)', fontsize=9)
fig.savefig(f"{THESIS}/Chapter2/Figs/fig_gci.png")
print("wrote fig_gci.png")
