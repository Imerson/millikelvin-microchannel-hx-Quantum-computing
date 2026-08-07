"""Fig. 2.2 - Gate-1 verified loads across the factorial."""
import numpy as np
import matplotlib.pyplot as plt
from common import THESIS, C_CU, C_AG, load_factorial

df = load_factorial()
err = np.abs((np.abs(df.Gate1_nW) - df.Q_model_nW)/df.Q_model_nW)*100
cols = [C_CU]*3 + [C_AG]*3

fig, ax = plt.subplots(figsize=(5.8, 3.0))
ax.bar(df.case, err, color=cols, width=0.6)
ax.axhline(0.1, ls='--', color='k', lw=1)
ax.text(3.3, 0.103, 'acceptance gate 0.1%', fontsize=8)
ax.set_ylabel('Gate-1 load error [%]')
ax.set_ylim(0, 0.12)
ax.tick_params(axis='x', labelsize=8)
fig.savefig(f"{THESIS}/Chapter2/Figs/fig_gate1.png")
print("wrote fig_gate1.png")
