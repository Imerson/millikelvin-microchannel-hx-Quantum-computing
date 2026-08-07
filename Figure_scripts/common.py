"""Shared paths, style, and data loading for the dissertation figures."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# ---- edit these two paths if the folders move ------------------------------
BASE = ("/Users/imerson/Library/CloudStorage/OneDrive-Personal/Documents/"
        "Education Hub/15-Energy Systems/4-Year 3/4-Dissertation")
THESIS = BASE + "/6-Latex/638cc3cf5419cef31326d0ee copy/Masters-thesis"
MODEL = BASE + "/2-Model/3-4K Heat exchanger/Final models/S4_HX_Hybrid_Results"
# -----------------------------------------------------------------------------

C_CU, C_AG = '#B85042', '#50708E'      # copper / silver series colours
AWET = {0.5: 0.562, 1.0: 0.270, 2.0: 0.135}   # system wetted area [m^2]

plt.rcParams.update({'font.size': 10, 'font.family': 'DejaVu Serif',
                     'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 300,
                     'savefig.bbox': 'tight'})


def load_factorial():
    """Per-case results of the six-case factorial (model-level R_total)."""
    return pd.read_csv(f"{MODEL}/comparison_hybrid.csv")
