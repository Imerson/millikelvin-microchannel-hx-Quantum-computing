"""Fig 1.x (sec:kapitza) - where the thermal bottleneck sits.

(a) Ordinary temperatures: the temperature drop is concentrated in the
    convective film next to the wall; resistance 1/(hA), flow-controlled.
(b) Millikelvin: the film is transparent and the drop concentrates in a
    discontinuous Kapitza step at the solid-fluid interface itself,
    leaving material (C_K) and wetted area (A_wet) as the only levers.
Writes ../Chapter1/Figs/fig_kapitza_schematic.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

C_CU = '#B85042'
plt.rcParams.update({'font.size': 10, 'font.family': 'DejaVu Serif',
                     'axes.grid': False, 'figure.dpi': 300, 'savefig.bbox': 'tight'})

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'Chapter1', 'Figs', 'fig_kapitza_schematic.png'))

fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.6))
for ax, mode in zip(axs, ['normal', 'mk']):
    ax.add_patch(Rectangle((0, 0), 1.0, 2.4, facecolor='#d9d4cc', edgecolor='k', lw=1.2))
    ax.add_patch(Rectangle((1.0, 0), 1.6, 2.4, facecolor='#dce8f8', edgecolor='k', lw=1.2))
    ax.text(0.5, 2.55, 'solid wall', ha='center', fontsize=10)
    ax.text(1.8, 2.55, 'fluid', ha='center', fontsize=10)
    if mode == 'normal':
        x = np.array([0.05, 1.0, 1.0, 1.35, 2.55]); yT = np.array([2.0, 1.95, 1.95, 1.0, 0.9])
        ax.plot(x, yT, color=C_CU, lw=2.5)
        ax.annotate('convective film:\nresistance $1/(hA)$,\ncontrolled by the FLOW', xy=(1.18, 1.5),
                    xytext=(1.5, 1.85), fontsize=8.5, color=C_CU,
                    arrowprops=dict(arrowstyle='->', color=C_CU))
        ax.text(1.28, 0.32, 'levers: turbulence, fins,\nentrance effects, velocity', fontsize=8.5, color='0.3')
        ax.set_title('(a) ordinary temperatures:\nthe film is the bottleneck', fontsize=10)
    else:
        ax.plot([0.05, 1.0], [2.0, 2.0], color=C_CU, lw=2.5)
        ax.plot([1.0, 2.55], [0.85, 0.83], color=C_CU, lw=2.5)
        ax.plot([1.0, 1.0], [2.0, 0.85], color=C_CU, lw=2.5, ls=':')
        ax.annotate('Kapitza step $\\Delta T_\\mathrm{K}$:\nresistance $C_\\mathrm{K}/T^{3}$\nAT the interface itself',
                    xy=(1.02, 1.4), xytext=(1.35, 1.75), fontsize=8.5, color=C_CU,
                    arrowprops=dict(arrowstyle='->', color=C_CU))
        ax.text(1.22, 0.28, 'levers: interface material ($C_\\mathrm{K}$)\nand wetted area ($A_\\mathrm{wet}$) only', fontsize=8.2, color='0.3')
        ax.set_title('(b) millikelvin: the interface itself\nis the bottleneck', fontsize=10)
    ax.set_xlim(-0.1, 2.7); ax.set_ylim(-0.15, 2.95); ax.axis('off')
    ax.annotate('', xy=(2.5, -0.05), xytext=(0.1, -0.05), arrowprops=dict(arrowstyle='->', color='k', lw=1))
    ax.text(1.3, -0.28, 'position', ha='center', fontsize=8.5)
    ax.text(-0.08, 1.4, 'temperature', rotation=90, va='center', fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT)
print('wrote', OUT)
