"""Fig 3.x (sec:hx-decomp) - conduction-Kapitza crossover (single panel).

Specific Kapitza resistance C_K/T^3 against the Wiedemann-Franz conduction
resistance L/kappa(T) (kappa = a*T) for Cu, Ag and stainless steel over a
representative L = 20 mm span. Crossover markers show T_x = sqrt(C_K*a/L):
~20 K for Cu/Ag (far above the operating range -> unconditionally
Kapitza-limited) and ~0.18 K for a stainless wall (illustrative poor
conductor). Single-panel version of panel (b) of plot_decomposition_crossover
(that two-panel figure remains the viva backup).

Writes ../Chapter3/Figs/fig_crossover.png at true printed size
(width = frac * 153.75 mm text block; placed at 0.75\\textwidth).
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

C_CU, C_AG = '#B85042', '#50708E'
plt.rcParams.update({'font.size': 10, 'font.family': 'DejaVu Serif',
                     'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 300,
                     'savefig.bbox': 'tight'})

TEXTBLOCK_MM = 153.75


def figsize(frac, aspect=0.72):
    """Convert a \\textwidth fraction into a (w, h) tuple in inches."""
    w = frac * TEXTBLOCK_MM / 25.4
    return (w, aspect * w)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'Chapter3', 'Figs', 'fig_crossover.png'))

fig, ax = plt.subplots(figsize=figsize(0.75))

T = np.logspace(np.log10(0.005), np.log10(40), 500)
L = 0.02
a_cu, a_ag, a_ss = 436.0, 1600.0, 0.033   # kappa = a*T from residual resistivity (WF)
for C, a, c, lab in [(0.020, a_cu, C_CU, 'copper'), (0.005, a_ag, C_AG, 'silver')]:
    ax.loglog(T, C / T**3, color=c, lw=1.8, label=f'$R_\\mathrm{{K}}$ ({lab})')
    ax.loglog(T, L / (a * T), color=c, lw=1.2, ls='--')
    Tx = np.sqrt(C * a / L)
    ax.plot(Tx, C / Tx**3, 'o', color=c, ms=5, zorder=5)
ax.loglog(T, L / (a_ss * T), color='0.35', lw=1.2, ls='--')
Tx_ss = np.sqrt(0.020 * a_ss / L)
ax.plot(Tx_ss, 0.020 / Tx_ss**3, 'o', color='0.35', ms=5, zorder=5)
ax.axvspan(0.010, 0.100, color='#CADCFC', alpha=0.6)
ax.text(0.031, 1e-5, 'operating\nrange', fontsize=8, ha='center', color='#1E2761')
ax.text(0.55, 8e-1, 'conduction,\nstainless steel', fontsize=7.5, color='0.35')
ax.text(0.9, 1.2e-6, 'conduction, Cu / Ag', fontsize=7.5, color=C_CU, rotation=-8)
ax.annotate('$T^{\\times}\\approx 20$ K', xy=(20, 0.020 / 20**3), xytext=(2.5, 4e-7),
            fontsize=8, arrowprops=dict(arrowstyle='->', color='k', lw=0.8))
ax.annotate('$T^{\\times}_\\mathrm{ss}\\approx0.18$ K',
            xy=(Tx_ss * 0.93, 0.020 / Tx_ss**3 * 0.75),
            xytext=(0.0062, 1.2), fontsize=8, color='0.35',
            arrowprops=dict(arrowstyle='->', color='0.35', lw=0.8,
                            connectionstyle='arc3,rad=-0.15'))
ax.set_xlabel('Temperature [K]')
ax.set_ylabel('specific resistance  [$\\mathrm{m^2\\,K\\,W^{-1}}$]')
ax.set_ylim(1e-8, 1e6)
ax.set_xlim(5e-3, 40)
ax.legend(fontsize=7.5, loc='upper right')

fig.tight_layout()
fig.savefig(OUT)
print('wrote', OUT)
