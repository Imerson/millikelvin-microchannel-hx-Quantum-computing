"""Fig. 2.x pair - boundary-condition schematic and domain-independence plot.

- fig_bc_schematic.png: single-channel side view annotating each boundary
  condition and its physical rationale (chip fixed flux, 10 mK inlet as the
  only sink, adiabatic outer faces, interface continuity with the Kapitza
  jump applied analytically).
- fig_domain_indep.png: per-channel conjugate interface temperature for the
  5/7/9-channel unit cells (Cu, D_h = 1.0 mm), from
  S4_Domain_Independence/N*/metrics.txt; deviations plotted in nK.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from common import THESIS

C_CU, NAVY, ICE = '#B85042', '#1E2761', '#CADCFC'

# ---------------- BC schematic ----------------
fig, ax = plt.subplots(figsize=(8.8, 3.6)); ax.axis('off')
ax.add_patch(Rectangle((0, 0), 100, 20, fc='#D9D2C5', ec='k', lw=1.2))
ax.add_patch(Rectangle((0, 7), 100, 6, fc=ICE, ec='#50708E', lw=0.8))
ax.add_patch(Rectangle((0, 20), 100, 2.2, fc=C_CU, ec='k', lw=0.8))
for x in np.linspace(8, 92, 8):
    ax.add_patch(FancyArrow(x, 27, 0, -3.4, width=0.7, head_width=2.2,
                            head_length=1.4, color=C_CU))
ax.text(50, 30.5, r"chip face: uniform, temperature-independent flux  "
        r"$q''=Q_\mathrm{model}/A_\mathrm{chipFace}$  (fixedGradient; verified by Gate 1)",
        ha='center', fontsize=9, color='#7A3020')
ax.add_patch(FancyArrow(-9, 10, 6, 0, width=1.1, head_width=3.2, head_length=2.2, color=NAVY))
ax.text(-26.4, 13.5, 'He-II inlet\n$T=10$ mK\n$U=1$ mm s$^{-1}$\nideal bath reservoir,\nthe only heat sink',
        fontsize=8, ha='left', va='top', color=NAVY)
ax.add_patch(FancyArrow(102, 10, 6, 0, width=1.1, head_width=3.2, head_length=2.2, color=NAVY))
ax.text(103, 15, 'outlet\n$p_\\mathrm{rgh}=0$', fontsize=8, color=NAVY)
ax.add_patch(Rectangle((0, -2.2), 100, 2.2, fc='none', ec='k', hatch='///', lw=0.6))
ax.text(50, -4.6, 'all other external solid faces adiabatic (zeroGradient): vacuum-isolated hardware;\n'
        'the entire load is forced across the studied interface', ha='center', va='top', fontsize=8.5)
ax.annotate('fluid--solid interface: $T$ and $q$ continuity, no contact resistance;\n'
            'Kapitza jump $\\Delta T_\\mathrm{K}$ added analytically (Eq. 2.7)',
            xy=(78, 13), xytext=(62, -15.5), fontsize=8.5, color='#50708E',
            arrowprops=dict(arrowstyle='->', color='#50708E', lw=1))
ax.text(2, 16.2, 'solid (Cu / Ag)', fontsize=8.5)
ax.text(2, 9.6, 'He-II channel', fontsize=8.5, color=NAVY)
ax.set_xlim(-28, 126); ax.set_ylim(-20, 34)
fig.savefig(f"{THESIS}/Chapter2/Figs/fig_bc_schematic.png")
print("wrote fig_bc_schematic.png")

# ---------------- domain independence (values from N*/metrics.txt) ----------------
N5 = [2.49967765e-2, 2.49967725e-2, 2.49967712e-2, 2.49967724e-2, 2.49967763e-2]
N7 = [2.49967175e-2, 2.49967109e-2, 2.49967061e-2, 2.49967043e-2, 2.49967060e-2,
      2.49967106e-2, 2.49967171e-2]
N9 = [2.49966923e-2, 2.49966813e-2, 2.49966696e-2, 2.49966605e-2, 2.49966571e-2,
      2.49966604e-2, 2.49966693e-2, 2.49966809e-2, 2.49966918e-2]
fig, ax = plt.subplots(figsize=(6.6, 3.6))
for d, c, lab, mk in [(N5, NAVY, 'N5 (production cell)', 'o'),
                      (N7, '#5D7B99', 'N7', 's'), (N9, '#8CA8C6', 'N9', '^')]:
    d = np.array(d); dev = (d - d.min())*1e9   # K -> nK... (values in K: 2.4996e-2)
    x = np.arange(len(d)) - (len(d)-1)/2
    ax.plot(x, dev, mk+'-', color=c, lw=1.4, ms=6, label=lab)
ax.set_xlabel('Channel position relative to cell centre')
ax.set_ylabel(r'$T_\mathrm{int}$ deviation from channel minimum [nK]')
ax.legend(fontsize=9, loc='upper center')
ax.text(0, -5.4, r'$\Delta P = 2.922878$ mPa in all 21 channels of all three cases',
        ha='center', fontsize=8.5, color=C_CU)
ax.set_ylim(-8, 52)
fig.savefig(f"{THESIS}/Chapter2/Figs/fig_domain_indep.png")
print("wrote fig_domain_indep.png")
