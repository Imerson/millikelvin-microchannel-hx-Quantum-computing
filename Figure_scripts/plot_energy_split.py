"""Appendix fig. - fluid-side energy split (inlet back-conduction artefact)."""
import matplotlib.pyplot as plt
from common import THESIS, C_CU, C_AG, load_factorial

df = load_factorial()
share = df.Q_fluid_nW/df.Q_model_nW*100
cols = [C_CU]*3 + [C_AG]*3

fig, ax = plt.subplots(figsize=(5.8, 3.0))
ax.bar(df.case, share, color=cols, width=0.6)
ax.axhline(50, ls='--', color='k', lw=1)
ax.set_ylabel('Outlet enthalpy share [%]')
ax.set_ylim(0, 62)
ax.tick_params(axis='x', labelsize=8)
ax.text(-0.35, 54,
        r'$\approx$50%: remainder back-conducts to the fixed-$T$ inlet ($Pe\approx0.7$)',
        fontsize=8)
fig.savefig(f"{THESIS}/Appendix2/Figs/fig_energy_split.png")
print("wrote fig_energy_split.png")
