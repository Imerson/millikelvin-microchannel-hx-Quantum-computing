"""Fig. 2.x - analytic sintered-silver benchmark schematic (Part B).

Two panels: (a) the normalised block (same footprint/duty as the
microchannel) as a stochastic packed-grain pore network carrying the chip
load and driven by a Darcy pressure drop; (b) the pore-scale microstructure
defining porosity, permeability (Kozeny-Carman), pore diameter, and the
microscopic-vs-He-4-effective wetted-area distinction. Pure schematic - no
data file; parameter values annotated match Section 2 (Part B).
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Circle, ConnectionPatch
from common import THESIS

TAN, CHIP, NAVY, SIL = '#D9D2C5', '#B85042', '#1E2761', '#9AA0A6'

fig = plt.figure(figsize=(9.4, 4.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.16)
axA = fig.add_subplot(gs[0]); axB = fig.add_subplot(gs[1])
for a in (axA, axB):
    a.axis('off')

# ---------- (a) macroscopic block ----------
axA.add_patch(Rectangle((0, 0), 100, 20, fc=TAN, ec='k', lw=1.2))
rng = np.random.default_rng(3)
for _ in range(230):
    x = rng.uniform(1.5, 98.5); y = rng.uniform(1.5, 18.5); r = rng.uniform(0.7, 1.25)
    axA.add_patch(Circle((x, y), r, fc=SIL, ec='none', alpha=0.5))
axA.add_patch(Rectangle((0, 20), 100, 2.2, fc=CHIP, ec='k', lw=0.8))
for x in np.linspace(8, 92, 8):
    axA.add_patch(FancyArrow(x, 27, 0, -3.4, width=0.7, head_width=2.2, head_length=1.4, color=CHIP))
axA.text(50, 30.6, r"chip face: qubit load $Q_\mathrm{sys}$ over the $40\times40$ mm face",
         ha='center', fontsize=9, color='#7A3020')
axA.add_patch(FancyArrow(-8, 10, 6, 0, width=1.1, head_width=3.2, head_length=2.2, color=NAVY))
axA.text(-30, 17, 'He-II\nsuperficial\nvelocity $U_\\mathrm{s}$', fontsize=8, ha='left', va='top', color=NAVY)
axA.add_patch(FancyArrow(102, 10, 6, 0, width=1.1, head_width=3.2, head_length=2.2, color=NAVY))
axA.annotate('', xy=(100, -3.6), xytext=(0, -3.6), arrowprops=dict(arrowstyle='<->', color='k', lw=0.9))
axA.text(50, -6.2, r'length $L=100$ mm', ha='center', va='top', fontsize=8.5)
axA.set_xlim(-32, 124); axA.set_ylim(-10, 34)
axA.set_title('(a) Normalised block: same footprint\nand duty as the microchannel', fontsize=9)

# ---------- (b) pore-scale microstructure ----------
axB.add_patch(Rectangle((0, 0), 10, 10, fc='white', ec='k', lw=1.0))
R = 0.95
for j, y in enumerate(np.arange(0.9, 10, 1.75)):
    off = 0.9 if j % 2 else 0.0
    for x in np.arange(0.9+off, 10, 1.8):
        gx, gy = x+rng.uniform(-0.1, 0.1), y+rng.uniform(-0.1, 0.1)
        axB.add_patch(Circle((gx, gy), R, fc=SIL, ec='#6E7378', lw=0.5))
axB.text(3.0, 11.9, r'grains (silver)', fontsize=7.8, color='#5A5A5A', ha='center')
axB.annotate('pore, $d_p=0.07\\ \\mu$m', xy=(2.6, 4.35), xytext=(-0.3, -1.4),
             fontsize=8, color=NAVY, ha='left', arrowprops=dict(arrowstyle='->', color=NAVY, lw=0.9))
axB.text(12.4, 8.6, 'microscopic wetted area\n'+r'$\sim1\ \mathrm{m^2 g^{-1}}$ (all grain'+'\nsurfaces): idealised bound',
         fontsize=7.8, color='#5A5A5A', va='top')
axB.text(12.4, 3.9, 'He-4 effective area:\nonly the geometric\nenvelope (phonon mfp\n'+r'$\ell_\mathrm{ph}\!\gg d_p$ below $\sim$700 mK)',
         fontsize=7.8, color=CHIP, va='top')
axB.text(5.0, -3.4, r'porosity $\varphi=V_\mathrm{void}/V_\mathrm{total}=0.5$',
         ha='center', va='top', fontsize=8.5)
axB.set_xlim(-1, 23); axB.set_ylim(-7, 13.2)
axB.set_title('(b) Pore-scale microstructure\n(magnified)', fontsize=9)

for ya, yb in [(19, 10), (15, 0)]:
    con = ConnectionPatch(xyA=(100, ya), coordsA=axA.transData, xyB=(0, yb), coordsB=axB.transData,
                          arrowstyle='-', color='#B7BBC0', lw=0.9, ls=(0, (3, 2)))
    fig.add_artist(con)
fig.savefig(f"{THESIS}/Chapter2/Figs/fig_sinter_schematic.png")
print("wrote fig_sinter_schematic.png")
