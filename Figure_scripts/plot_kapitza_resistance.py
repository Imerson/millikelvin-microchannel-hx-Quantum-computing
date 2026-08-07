"""Fig. 1.2 - Kapitza resistance R_K = C_K/T^3 for Cu and Ag (analytic)."""
import numpy as np
import matplotlib.pyplot as plt
from common import THESIS, C_CU, C_AG

T = np.logspace(np.log10(0.005), np.log10(1.0), 300)   # [K]

fig, ax = plt.subplots(figsize=(5.6, 3.6))
ax.loglog(T*1e3, 0.020/T**3, color=C_CU, lw=2,
          label=r'OFHC copper ($C_\mathrm{K}=0.020\ \mathrm{K^4 m^2 W^{-1}}$)')
ax.loglog(T*1e3, 0.005/T**3, color=C_AG, lw=2,
          label=r'Silver ($C_\mathrm{K}=0.005\ \mathrm{K^4 m^2 W^{-1}}$)')
ax.axvspan(10, 20, color='#CADCFC', alpha=0.6, label='MXC operating band (10-20 mK)')
ax.annotate('', xy=(11, 0.020/0.011**3), xytext=(11, 0.005/0.011**3),
            arrowprops=dict(arrowstyle='<->', color='k', lw=1))
ax.text(12.3, 6.5e3, r'$\times 4$', fontsize=11)
ax.set_xlabel('Temperature [mK]')
ax.set_ylabel(r'$R_\mathrm{K}=C_\mathrm{K}/T^{3}$  [$\mathrm{m^2\,K\,W^{-1}}$]')
ax.legend(fontsize=8, loc='upper right')
fig.savefig(f"{THESIS}/Chapter1/Figs/fig_RK_vs_T.png")
print("wrote fig_RK_vs_T.png")
