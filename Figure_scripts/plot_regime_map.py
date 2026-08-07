#!/usr/bin/env python3
"""
Effective-area regime map (fig:ch4-regime), Chapter 4.

Phonon-effective wetted area per unit chip footprint vs operating temperature,
for the candidate exchanger technologies.

Curves
------
- Microchannel lines: geometric, temperature-independent (351x / 169x / 84x
  for D_h = 0.5 / 1.0 / 2.0 mm), plus the D_h = 10 um machinability floor.
- Sintered silver, nominal microscopic area (idealised upper bound, dashed).
- Sintered silver in He-II: schematic interpolation between the idealised
  microscopic area above T* and the ~1.5x-flat-plate effective area measured
  below T* ~ 700 mK, where the dominant phonon wavelength/mean free path
  exceeds the sinter structure scale (Nakagawa 2023).
- Sintered silver in dilute 3He-4He solution: same length-scale crossover,
  observed as a thickness-dependent T^-1.5 -> T^-3 transition between
  8 and 150 mK; drawn schematically with T* ~ 100 mK (Cousins et al. 1994).
- Pure superfluid 3He-B: ballistic quasiparticles exchange heat with the
  macroscopic geometric envelope only (~10^3 collisions to thermalise);
  the crossover lies in the sub-mK regime, below the plotted range
  (Autti et al. 2020).

The sigmoids are schematic interpolations between literature-grounded
limits, not fits.

Output: ../Chapter4/Figs/fig_regime_map.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- style (matches thesis figure set) ----------------
plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "stix",
    "font.size": 11,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "axes.linewidth": 0.9,
})

HERE   = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "Chapter4", "Figs"))
os.makedirs(OUTDIR, exist_ok=True)

# ---------------- data ----------------
T = np.logspace(np.log2(1e-2) / np.log2(10), np.log10(2.0), 600)

A_SINTER_NOM = 4.4e6     # idealised full-microscopic sinter area / footprint
A_FLOOR_HE2  = 1.5       # ~1.5x flat plate below crossover (Nakagawa 2023)
A_FLOOR_GEOM = 1.0       # macroscopic geometric envelope (Autti 2020)
A_MC         = {0.5: 351.0, 1.0: 169.0, 2.0: 84.0}   # microchannel ratios
A_MACH       = 1.8e4     # D_h = 10 um machinability floor

TSTAR_HE2 = 0.700        # He-II phonon crossover (Nakagawa 2023)
TSTAR_MIX = 0.100        # dilute 3He-4He crossover, schematic within the
                         # 8-150 mK window of Cousins et al. (1994)
W_DEX     = 0.10         # sigmoid width in decades of T


def sigmoid_area(T, Tstar, floor, top=A_SINTER_NOM, w=W_DEX):
    """Schematic log-log sigmoid between the two literature-grounded limits."""
    s = 1.0 / (1.0 + np.exp(-(np.log10(T) - np.log10(Tstar)) / w))
    return 10.0 ** (np.log10(floor) + (np.log10(top) - np.log10(floor)) * s)


A_he2 = sigmoid_area(T, TSTAR_HE2, A_FLOOR_HE2)
A_mix = sigmoid_area(T, TSTAR_MIX, A_FLOOR_HE2)
A_he3 = np.full_like(T, A_FLOOR_GEOM)   # ballistic 3He-B: crossover sub-mK

# ---------------- plot ----------------
NAVY   = "#1f3864"
BLUES  = {0.5: "#2e4d78", 1.0: "#4a6da3", 2.0: "#7d9cc4"}
RED    = "#c0504d"
PURPLE = "#7b5aa6"
GREEN  = "#3a7d44"
GREY   = "#808080"

fig, ax = plt.subplots(figsize=(9.0, 6.0))

# MXC operating range 10-100 mK
ax.axvspan(1e-2, 1e-1, color="#c9d9f0", alpha=0.55, zorder=0)
ax.text(1.35e-2, 1.5e7, "MXC exchanger\noperating range",
        color=NAVY, fontsize=12, ha="left", va="top")

# idealised sinter microscopic area
ax.axhline(A_SINTER_NOM, color=GREY, ls="--", lw=2.0, zorder=2)
ax.text(1.35e-2, 2.4e6, "sintered silver, nominal microscopic area (idealised)",
        color=GREY, fontsize=11, ha="left", va="top")

# machinability floor
ax.axhline(A_MACH, color=NAVY, ls="-.", lw=1.6, zorder=2)
ax.text(1.35e-2, 2.6e4,
        r"machinability floor $D_{\mathrm{h}}=10\,\mu$m ($\approx 1.8\times10^{4}\times$)",
        color=NAVY, fontsize=11, ha="left", va="bottom")

# microchannel geometric lines
mc_txt = {0.5: r"microchannel $D_{\mathrm{h}}=0.5$ mm ($351\times$)",
          1.0: r"microchannel $D_{\mathrm{h}}=1.0$ mm ($169\times$)",
          2.0: r"microchannel $D_{\mathrm{h}}=2.0$ mm ($84\times$)"}
for D, A in A_MC.items():
    ax.axhline(A, color=BLUES[D], lw=3.0, zorder=3)
    ax.text(1.35e-2, A * 1.18, mc_txt[D], color=BLUES[D], fontsize=11.5,
            ha="left", va="bottom")

# --- sintered silver, effective area in He-II (Nakagawa 2023) ---
ax.plot(T, A_he2, color=RED, lw=3.0, zorder=4)
ax.text(7.5e-2, 4.5,
        "sintered silver, effective area in He-II:\n"
        r"$\approx 1.5\times$ flat plate below $T^{*}$ where $\ell_{\mathrm{ph}}$"
        "\nexceeds the sinter structure scale (Nakagawa 2023)",
        color=RED, fontsize=11, ha="left", va="bottom")

# --- sintered silver in dilute 3He-4He solution (Cousins 1994) ---
ax.plot(T, A_mix, color=PURPLE, lw=2.6, ls=(0, (6, 2)), zorder=4)
ax.text(1.15e-2, 1.05e4,
        "sintered silver, effective area in dilute\n"
        r"$^{3}$He--$^{4}$He solution: same crossover at"
        "\n" r"$T^{*}\approx 100$ mK (Cousins 1994)",
        color=PURPLE, fontsize=10.5, ha="left", va="top")

# --- pure superfluid 3He-B, ballistic regime (Autti 2020) ---
ax.plot(T, A_he3, color=GREEN, lw=2.6, ls=(0, (2, 2)), zorder=4)
ax.text(3.5e-2, 0.92,
        r"pure $^{3}$He-B: geometric envelope only, ballistic quasiparticles"
        "\n(Autti 2020); crossover sub-mK, below plotted range",
        color=GREEN, fontsize=10.5, ha="left", va="top")

# ---------------- literature-anchored points ----------------
# Filled dots: measured/calculated anchors. Open dot: schematic placement
# of the mixture crossover within the 8-150 mK measured window of
# Cousins et al. (1994). Left arrow: Autti (2020) anchor lies sub-mK,
# off the plotted range.
def _on(curve_fn, x):
    return curve_fn(np.array([x]))[0]

he2 = lambda x: sigmoid_area(x, TSTAR_HE2, A_FLOOR_HE2)
mix = lambda x: sigmoid_area(x, TSTAR_MIX, A_FLOOR_HE2)

# He-II (Nakagawa 2023): measured floor, measured crossover, full-area side
for x in (0.20, TSTAR_HE2, 1.6):
    ax.plot(x, _on(he2, x), "o", ms=9, color=RED,
            markeredgecolor="white", markeredgewidth=1.2, zorder=6)

# dilute 3He-4He (Cousins 1994): floor anchors inside the 8-150 mK window
for x in (0.011, 0.03):
    ax.plot(x, _on(mix, x), "o", ms=9, color=PURPLE,
            markeredgecolor="white", markeredgewidth=1.2, zorder=6)
# schematic T* placement: open marker
ax.plot(TSTAR_MIX, _on(mix, TSTAR_MIX), "o", ms=9, markerfacecolor="white",
        markeredgecolor=PURPLE, markeredgewidth=2.0, zorder=6)

# pure 3He-B (Autti 2020): anchor lies sub-mK, off scale to the left
ax.plot(1.07e-2, A_FLOOR_GEOM, marker="<", ms=10, color=GREEN,
        markeredgecolor="white", markeredgewidth=1.0, zorder=6)

# He-II crossover marker
ax.axvline(TSTAR_HE2, color="k", ls=":", lw=1.4, zorder=2)
ax.text(TSTAR_HE2 * 0.88, 3.0e4, r"$T^{*}\approx 700$ mK",
        rotation=90, fontsize=11, ha="center", va="bottom")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1e-2, 2.0)
ax.set_ylim(0.24, 2e7)
ax.set_xlabel("Temperature [K]", fontsize=14)
ax.set_ylabel("Phonon-effective wetted area / chip footprint  [--]", fontsize=13)

fig.tight_layout()
out = os.path.join(OUTDIR, "fig_regime_map.png")
fig.savefig(out, dpi=300)
print("saved:", out)
