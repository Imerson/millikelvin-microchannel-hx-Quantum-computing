"""Fig 1.x (sec:mxc-sota) - the sintering route to surface area.

(a) loose fine silver powder (~0.1 um grains);
(b) cold-pressed compact (~50% porosity);
(c) sintered: grains fuse at contact necks into a rigid open-pored sponge
    with 0.5-1 m^2/g of internal surface, process-dependent pore network.
Writes ../Chapter1/Figs/fig_sinter_process.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

plt.rcParams.update({'font.size': 10, 'font.family': 'DejaVu Serif',
                     'axes.grid': False, 'figure.dpi': 300, 'savefig.bbox': 'tight'})

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'Chapter1', 'Figs', 'fig_sinter_process.png'))

fig, axs = plt.subplots(1, 3, figsize=(9.0, 3.0))
rng = np.random.default_rng(4)

ax = axs[0]
for _ in range(55):
    x, y = rng.uniform(0.15, 1.85), rng.uniform(0.15, 1.85)
    ax.add_patch(Circle((x, y), rng.uniform(0.055, 0.08), facecolor='#b9b2a7', edgecolor='0.35', lw=0.5))
ax.set_title('(a) loose silver powder\n(grains ${\\sim}0.1\\,\\mu$m)', fontsize=9.5)

ax = axs[1]
for i in range(9):
    for j in range(9):
        x = 0.22 + i*0.195 + rng.uniform(-0.02, 0.02)
        y = 0.22 + j*0.195 + rng.uniform(-0.02, 0.02)
        ax.add_patch(Circle((x, y), 0.088, facecolor='#a8a196', edgecolor='0.35', lw=0.5))
ax.add_patch(Rectangle((0.08, 0.08), 1.84, 1.84, fill=False, edgecolor='k', lw=1.4))
ax.annotate('press', xy=(1.0, 2.12), xytext=(1.0, 2.45), ha='center', fontsize=9,
            arrowprops=dict(arrowstyle='->', color='k'))
ax.set_title('(b) cold-pressed compact\n(porosity ${\\sim}50\\%$)', fontsize=9.5)

ax = axs[2]
centers = []
for i in range(9):
    for j in range(9):
        x = 0.22 + i*0.195 + rng.uniform(-0.015, 0.015)
        y = 0.22 + j*0.195 + rng.uniform(-0.015, 0.015)
        centers.append((x, y))
for (x1, y1) in centers:
    for (x2, y2) in centers:
        d = np.hypot(x2-x1, y2-y1)
        if 0.01 < d < 0.24:
            ax.plot([x1, x2], [y1, y2], color='#8d857a', lw=4.5, solid_capstyle='round', zorder=1)
for (x, y) in centers:
    ax.add_patch(Circle((x, y), 0.085, facecolor='#9a938a', edgecolor='0.3', lw=0.5, zorder=2))
ax.add_patch(Rectangle((0.08, 0.08), 1.84, 1.84, fill=False, edgecolor='k', lw=1.4))
ax.set_title('(c) sintered: grains fuse at necks,\nrigid sponge, huge internal surface', fontsize=9.5)

for ax in axs:
    ax.set_xlim(0, 2); ax.set_ylim(0, 2.7 if ax is axs[1] else 2.15)
    ax.set_aspect('equal'); ax.axis('off')
fig.tight_layout()
fig.savefig(OUT)
print('wrote', OUT)
