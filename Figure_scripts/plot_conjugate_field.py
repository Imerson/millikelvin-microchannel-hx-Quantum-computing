"""Fig. 3.x - conjugate temperature field on a mid-channel x-z slice (Cu_1p0).

Reconstructs the 2-D slice directly from the converged OpenFOAM case:
parses polyMesh (points/faces/owner/neighbour) to compute cell centres,
reads the 6000/T fields of the solid and the centre channel (domain3),
selects the mesh layer nearest the channel centreline, and renders a
structured pivot as a pcolormesh.
"""
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from common import THESIS, MODEL

CASE = f"{MODEL}/Cu_1p0"


# ---------------- OpenFOAM ASCII parsers ----------------
def read_of_field(path):
    t = open(path, errors='ignore').read()
    m = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(', t)
    n = int(m.group(1))
    s = t.index('(', m.end()-1)+1
    vals = np.fromstring(t[s:t.index(')', s)], sep='\n')
    assert len(vals) == n
    return vals


def read_points(path):
    t = open(path, errors='ignore').read()
    m = re.search(r'\n(\d+)\s*\n\(', t); n = int(m.group(1))
    body = t[m.end():]; body = body[:body.rindex(')')]
    arr = np.fromstring(body.replace('(', ' ').replace(')', ' '), sep=' ')
    return arr.reshape(-1, 3)[:n]


def read_faces(path):
    t = open(path, errors='ignore').read()
    m = re.search(r'\n(\d+)\s*\n\(', t); n = int(m.group(1))
    body = t[m.end():]; body = body[:body.rindex(')')]
    return [np.fromstring(mm.group(2), sep=' ', dtype=int)
            for mm in re.finditer(r'(\d+)\(([^)]*)\)', body)][:n]


def read_labels(path):
    t = open(path, errors='ignore').read()
    m = re.search(r'\n(\d+)\s*\n\(', t); n = int(m.group(1))
    body = t[m.end():]; body = body[:body.rindex(')')]
    return np.fromstring(body, sep='\n', dtype=int)[:n]


def cell_centres(region):
    base = f"{CASE}/constant/{region}/polyMesh"
    pts = read_points(f"{base}/points")
    faces = read_faces(f"{base}/faces")
    own = read_labels(f"{base}/owner")
    nei = read_labels(f"{base}/neighbour")
    ncell = max(own.max(), nei.max())+1
    fc = np.array([pts[f].mean(axis=0) for f in faces])
    csum = np.zeros((ncell, 3)); cnt = np.zeros(ncell)
    np.add.at(csum, own, fc); np.add.at(cnt, own, 1)
    np.add.at(csum, nei, fc[:len(nei)]); np.add.at(cnt, nei, 1)
    return csum/cnt[:, None]


# ---------------- slice selection and rendering ----------------
cs = cell_centres('solid_wall'); Ts = read_of_field(f"{CASE}/6000/solid_wall/T")
cf = cell_centres('domain3');    Tf = read_of_field(f"{CASE}/6000/domain3/T")

yf = np.unique(np.round(cf[:, 1], 6))
yc = yf[np.argmin(np.abs(yf - cf[:, 1].mean()))]          # fluid layer at centreline
sel_f = np.isclose(cf[:, 1], yc, atol=1e-6)
ys = np.unique(np.round(cs[:, 1], 6))
ysc = ys[np.argmin(np.abs(ys - yc))]                       # nearest solid layer
sel_s = np.isclose(cs[:, 1], ysc, atol=1e-6)

X = np.concatenate([cs[sel_s, 0], cf[sel_f, 0]])*1e3       # [mm]
Z = np.concatenate([cs[sel_s, 2], cf[sel_f, 2]])*1e3
Tmk = np.concatenate([Ts[sel_s], Tf[sel_f]])*1e3           # [mK]

dfp = pd.DataFrame({'x': np.round(X, 4), 'z': np.round(Z, 4), 'T': Tmk})
piv = dfp.pivot_table(index='z', columns='x', values='T', aggfunc='mean')
piv = piv.sort_index().sort_index(axis=1).ffill(axis=1).bfill(axis=1)
XI, ZI = np.meshgrid(piv.columns.values, piv.index.values)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.1),
                             gridspec_kw={'width_ratios': [2.2, 1]})
vmin, vmax = 23.4, 25.05
a1.pcolormesh(XI, ZI, piv.values, cmap='inferno', vmin=vmin, vmax=vmax, shading='auto')
a1.axhline(0.5, color='w', lw=0.8, ls='--'); a1.axhline(1.5, color='w', lw=0.8, ls='--')
a1.text(50, 1.72, 'solid (Cu)', color='w', ha='center', fontsize=9)
a1.text(50, 0.97, 'He-4 channel', color='w', ha='center', fontsize=9)
a1.text(50, 0.22, 'solid (Cu)', color='w', ha='center', fontsize=9)
a1.set_xlabel('x (flow direction) [mm]'); a1.set_ylabel('z [mm]')
a1.set_title('(a) Mid-channel slice, full length', fontsize=9); a1.grid(False)
im2 = a2.pcolormesh(XI, ZI, piv.values, cmap='inferno', vmin=vmin, vmax=vmax, shading='auto')
a2.set_xlim(0, 8)
a2.axhline(0.5, color='w', lw=0.8, ls='--'); a2.axhline(1.5, color='w', lw=0.8, ls='--')
a2.set_xlabel('x [mm]')
a2.set_title('(b) Inlet development region', fontsize=9); a2.grid(False)
cb = fig.colorbar(im2, ax=a2, pad=0.03); cb.set_label('T [mK]')
fig.savefig(f"{THESIS}/Chapter3/Figs/fig_field.png")
print("wrote fig_field.png")
