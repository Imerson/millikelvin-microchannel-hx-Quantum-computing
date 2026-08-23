"""Fig 3.x / 4.x - the machined-microchannel manufacturing route (standalone).

(a) open sub-millimetre grooves cut or etched along thin plates;
(b) plates stacked, each cap closing the grooves below;
(c) stack diffusion-bonded into a monolithic core whose every dimension is
    specified in advance (construction principle of compact heat exchangers;
    additive manufacturing offers a single-piece alternative).
Companion piece to Chapter 1's fig_sinter_process.png (same visual language).

Writes ../Chapter3/Figs/fig_microchannel_route.png at true printed size
(width = frac * 153.75 mm text block; placed at 0.95\\textwidth).
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({'font.size': 10, 'font.family': 'DejaVu Serif',
                     'axes.grid': False, 'figure.dpi': 300, 'savefig.bbox': 'tight'})

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'Chapter3', 'Figs', 'fig_microchannel_route.png'))

METAL, EDGE = '#b9b2a7', '0.35'
TEXTBLOCK_MM = 153.75


def figsize(frac, aspect):
    w = frac * TEXTBLOCK_MM / 25.4
    return (w, aspect * w)


fig, axs = plt.subplots(1, 3, figsize=figsize(0.95, 0.36))


def grooved_plate(ax, y0, h=0.42, ngr=5, edge='k'):
    """Plate cross-section with square grooves cut into its top face."""
    ax.add_patch(Rectangle((0.15, y0), 1.70, h, facecolor=METAL, edgecolor=edge, lw=1.0, zorder=2))
    gw = 0.20
    xs = np.linspace(0.34, 1.66 - gw, ngr)
    for x in xs:
        ax.add_patch(Rectangle((x, y0 + h - gw), gw, gw + 0.001,
                               facecolor='white', edgecolor=edge, lw=0.8, zorder=3))
    return xs, gw


ax = axs[0]
xs, gw = grooved_plate(ax, 0.85)
ax.annotate('cut / etch grooves', xy=(xs[2] + gw/2, 1.30), xytext=(1.0, 1.95),
            ha='center', fontsize=9, arrowprops=dict(arrowstyle='->', color='k'))
ax.text(1.0, 0.55, '$D_\\mathrm{h}$ set by the tool', ha='center', fontsize=8, color='0.25')
ax.set_title('(a) grooves cut or etched\nalong thin plates', fontsize=9)

ax = axs[1]
for y0 in [0.30, 0.95, 1.60]:
    grooved_plate(ax, y0)
ax.annotate('stack', xy=(2.02, 0.95), xytext=(2.02, 1.95), ha='center', fontsize=9,
            arrowprops=dict(arrowstyle='->', color='k'))
ax.set_title('(b) plates stacked: each cap\ncloses the grooves below', fontsize=9)

ax = axs[2]
ax.add_patch(Rectangle((0.25, 0.25), 1.50, 1.70, facecolor=METAL, edgecolor='k', lw=1.4, zorder=2))
gw = 0.18
for i in range(5):
    for j in range(5):
        x = 0.41 + i*0.24
        y = 0.42 + j*0.30
        ax.add_patch(Rectangle((x, y), gw, gw, facecolor='white', edgecolor=EDGE, lw=0.7, zorder=3))
ax.set_title('(c) diffusion-bonded\nmonolithic core', fontsize=9)

for ax in axs:
    ax.set_xlim(0, 2.15)
    ax.set_ylim(0, 2.35)
    ax.set_aspect('equal')
    ax.axis('off')

fig.tight_layout()
fig.savefig(OUT)
print('wrote', OUT)
