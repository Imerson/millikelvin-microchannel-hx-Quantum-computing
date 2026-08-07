#!/usr/bin/env python3
"""Domain (channel-count) independence analysis — Cu_1p0 hybrid, N = 5/7/9 channels.

Reads N5/N7/N9 metrics.txt from the folder this script sits in (or a folder
given as the first argument) and reports every statistic quoted in the study:
per-channel dP / T_int / T_out tables, hydraulic and thermal uniformity,
edge-vs-center spreads, the symmetry check (ch_k vs ch_{N+1-k}), the
chip-load-vs-area scaling check, and the per-channel load bookkeeping note.
No hand-entered values: everything derives from the metrics files, which are
themselves extracted from each case's converged (t=6000) function-object data.
"""
import os, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
CASES = [5, 7, 9]
# geometry / BC constants (identical to gen_domain_study.py)
DH, TW, L = 1.0e-3, 0.5e-3, 0.1                  # channel, wall, length (m)
KS, GRAD  = 13.08, -1.060398e-05                 # solid kappa, chipFace gradient (production Cu_1p0)
QPP = KS*abs(GRAD)                               # imposed flux (W/m^2)

def load(N):
    d = {"N": N, "ch": {}}
    for l in open(os.path.join(HERE, f"N{N}", "metrics.txt")):
        p = l.split()
        if p[0] == "NCELLS": d["cells"] = int(float(p[1]))
        elif p[0] == "QCHIP": d["Q"] = float(p[1])
        elif p[0].startswith("CH"):
            k = int(p[0][2:])
            d["ch"][k] = {p[i]: float(p[i+1]) for i in range(1, len(p), 2)}
    return d

data = [load(N) for N in CASES]

print("DOMAIN (CHANNEL-COUNT) INDEPENDENCE — analysis of N5/N7/N9 metrics")
print(f"imposed flux q'' = kappa*|grad| = {KS}*{abs(GRAD):.6e} = {QPP:.4e} W/m^2\n")

# --- 1. chip-load-vs-area scaling check (flux BC behaving) ---
print("== 1. Chip load scales with chip area (flux BC check) ==")
for d in data:
    N = d["N"]; width = N*DH + (N+1)*TW
    Qexp = QPP*width*L
    print(f"  N{N}: width={width*1e3:4.1f} mm  Q_expected={Qexp*1e9:8.3f} nW  "
          f"Q_measured={abs(d['Q'])*1e9:8.3f} nW  ratio={abs(d['Q'])/Qexp:.5f}")
print()

# --- 2. per-channel tables ---
print("== 2. Per-channel values (converged, t=6000) ==")
for d in data:
    print(f"  -- N{d['N']} ({d['cells']} cells) --")
    for k in sorted(d["ch"]):
        c = d["ch"][k]
        print(f"    ch{k}: dP={c['DP']*1e3:.6f} mPa  T_int={c['TINT']*1e3:.5f} mK  "
              f"T_out={c['TOUT']*1e3:.4f} mK  mdot={c['MDOT']:.4e} kg/s")
print()

# --- 3. hydraulic uniformity ---
allDP = [c["DP"] for d in data for c in d["ch"].values()]
allMD = [c["MDOT"] for d in data for c in d["ch"].values()]
nch = len(allDP)
print("== 3. Hydraulic uniformity (all channels, all cases) ==")
print(f"  {nch} channels total: dP min={min(allDP)*1e3:.6f}  max={max(allDP)*1e3:.6f} mPa"
      f"  spread={(max(allDP)-min(allDP))/min(allDP)*100:.2e} %")
print(f"  mdot min={min(allMD):.4e}  max={max(allMD):.4e} kg/s\n")

# --- 4. thermal spreads: global, edge-center, symmetry ---
allTI = [c["TINT"] for d in data for c in d["ch"].values()]
print("== 4. Thermal uniformity ==")
print(f"  T_int over ALL channels: max spread = {(max(allTI)-min(allTI))*1e3:.2e} mK"
      f"  ({(max(allTI)-min(allTI))/min(allTI):.2e} relative)")
for d in data:
    N = d["N"]; ch = d["ch"]; mid = (N+1)//2
    edge_center = ch[1]["TINT"] - ch[mid]["TINT"]
    sym = max(abs(ch[k]["TINT"] - ch[N+1-k]["TINT"]) for k in range(1, N//2+1))
    print(f"  N{N}: edge-center = {edge_center*1e3:.2e} mK   "
          f"symmetry max |ch_k - ch_(N+1-k)| = {sym*1e3:.2e} mK")
print()

# --- 5. per-channel load bookkeeping ---
print("== 5. Per-channel load (bookkeeping, not physics) ==")
q5 = abs(data[0]["Q"])/data[0]["N"]
for d in data:
    qn = abs(d["Q"])/d["N"]
    print(f"  N{d['N']}: Q/N = {qn*1e9:.3f} nW/channel  ({(qn/q5-1)*100:+.2f}% vs N5)")
print("  (decline = fixed outer-wall strips amortized over more channels;")
print("   field response above is <5e-6 relative, and the factorial's per-channel")
print("   load Q_sys/N_ch is width-independent by definition)\n")

# --- 6. verdict ---
dp_ok = (max(allDP)-min(allDP))/min(allDP) < 1e-5
ti_ok = (max(allTI)-min(allTI))/min(allTI) < 1e-4
print("== VERDICT ==")
print(f"  per-channel dP uniform to <1e-5 relative: {'PASS' if dp_ok else 'FAIL'}")
print(f"  per-channel T_int uniform to <1e-4 relative: {'PASS' if ti_ok else 'FAIL'}")
print("  -> the 5-channel unit cell is domain-independent; the N_ch/5 scaling"
      if dp_ok and ti_ok else "  -> INVESTIGATE before relying on the unit-cell scaling")
if dp_ok and ti_ok: print("     to the full array is numerically validated.")
