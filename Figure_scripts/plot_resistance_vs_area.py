"""Fig. 3.x - system-level R_total vs wetted area (log-log, 1/A trend).

Note: comparison_hybrid.csv reports the five-channel MODEL-level resistance;
system level = model level * 5 / N_ch.
"""
import numpy as np
import matplotlib.pyplot as plt
from common import THESIS, C_CU, C_AG, AWET, load_factorial

df = load_factorial()
df['R_sys'] = df.R_total_KW*5/df.N_ch     # system-level [K/W]

fig, ax = plt.subplots(figsize=(5.8, 3.8))
for mat, c, m in [('Cu', C_CU, 'o'), ('Ag', C_AG, 's')]:
    d = df[df.material == mat].sort_values('Dh_mm')
    A = d.Dh_mm.map(AWET).values
    ax.loglog(A, d.R_sys/1e3, m+'-', color=c, lw=1.5, ms=6,
              label=('OFHC copper' if mat == 'Cu' else 'Silver'))
    for a_, r_, dh_ in zip(A, d.R_sys/1e3, d.Dh_mm):
        ax.annotate(f'{dh_:g} mm', (a_, r_), textcoords='offset points',
                    xytext=(5, 5), fontsize=7.5)
R0 = df[(df.material == 'Cu') & (df.Dh_mm == 0.5)].R_sys.iloc[0]/1e3
Aref = np.array([0.115, 0.68])
ax.loglog(Aref, R0*0.562/Aref, ':', color='grey', lw=1.4)
ax.text(0.19, 8.2, r'$R\propto A_\mathrm{wet}^{-1}$', fontsize=9, color='grey', rotation=-24)
ax.set_xlabel(r'System wetted area $A_\mathrm{wet}$ [m$^2$]')
ax.set_ylabel(r'$R_\mathrm{total}$ [$10^{3}$ K W$^{-1}$]')
ax.legend(fontsize=9, loc='lower left')
fig.savefig(f"{THESIS}/Chapter3/Figs/fig_R_vs_A.png")
print("wrote fig_R_vs_A.png")
