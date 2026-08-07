"""Fig. 3.x - factorial chip temperatures with the MXC operating band."""
import numpy as np
import matplotlib.pyplot as plt
from common import THESIS, C_CU, C_AG, load_factorial

df = load_factorial()
cu = df[df.material == 'Cu'].sort_values('Dh_mm')
ag = df[df.material == 'Ag'].sort_values('Dh_mm')
x, w = np.arange(3), 0.36

fig, ax = plt.subplots(figsize=(6.2, 3.8))
b1 = ax.bar(x-w/2, cu.T_phys_mK, w, color=C_CU, label='OFHC copper')
b2 = ax.bar(x+w/2, ag.T_phys_mK, w, color=C_AG, label='Silver')
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+2,
            f'{b.get_height():.0f}', ha='center', fontsize=8)
ax.axhspan(10, 20, color='#CADCFC', alpha=0.7)
ax.axhline(10, color='#1E2761', lw=1)
ax.text(2.42, 12.5, 'MXC operating\nband 10-20 mK', fontsize=7.5, color='#1E2761')
ax.set_xticks(x)
ax.set_xticklabels([r'$D_\mathrm{h}=0.5$ mm', r'$D_\mathrm{h}=1.0$ mm', r'$D_\mathrm{h}=2.0$ mm'])
ax.set_ylabel(r'Chip temperature $T_\mathrm{chip}$ [mK]')
ax.set_ylim(0, 185)
ax.legend(loc='upper left', fontsize=9)
fig.savefig(f"{THESIS}/Chapter3/Figs/fig_chipT.png")
print("wrote fig_chipT.png")
