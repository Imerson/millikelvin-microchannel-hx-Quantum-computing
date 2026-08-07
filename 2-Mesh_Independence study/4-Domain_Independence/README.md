# Domain (Channel-Count) Independence Study

The factorial models a **five-channel unit cell** and scales its results to the full
channel array by N_ch/5. That scaling silently assumes the cell already behaves like a
slice of an infinite array — that the two outer walls don't distort the per-channel
answer. Symmetry makes this plausible; this study demonstrates it numerically: the
Cu / D_h = 1.0 mm model rebuilt with **5, 7 and 9 channels**, everything else identical,
every channel individually instrumented.

**Verdict: per-channel pressure drop is identical to six significant figures in all
21 channels across the three cases; per-channel interface temperature agrees within
5×10⁻⁶ (relative). The N_ch/5 unit-cell scaling is numerically validated.**

## Results

| Case | Cells | Per-channel ΔP (mPa) | Edge-channel T_int (mK) | Center-channel T_int (mK) |
|---|---|---|---|---|
| `N5` | 208,320 | 2.922878 | 24.99678 | 24.99677 |
| `N7` | 288,960 | 2.922878 | 24.99672 | 24.99670 |
| `N9` | 369,600 | 2.922878 | 24.99669 | 24.99666 |

- Maximum T_int spread over all 21 channels in the study: **1.2×10⁻⁴ mK** (4.8×10⁻⁶ relative).
- Edge effects are confined to the outermost channels, never exceed **3.5×10⁻⁵ mK**, and
  are symmetric about the center channel in every case (|ch_k − ch_{N+1−k}| ≤ 5×10⁻⁷ mK).
- Total chip load scales exactly with chip area (−110.96 / −152.57 / −194.18 nW for
  8 / 11 / 14 mm block widths) — the flux boundary condition behaves exactly.
- The N5 case reproduces the production Cu_1p0 values exactly (built-in consistency check).

## Methodology

One parameterized generator (`gen_domain_study.py`) builds all three cases with the
channel count as the only variable: production per-channel geometry (D_h = 1.0 mm square,
0.5 mm walls, 100 mm length), production cell density (20 cells across D_h — the mesh
verified by the parent [GCI study](../README.md)), identical hybrid boundary conditions
and numerics, all run to t = 6000. Every channel gets its own function objects
(ΔP, interface temperature, outlet temperature, mass flow), so edge-vs-interior variation
is measured rather than assumed. `domain_analysis.py` machine-generates every statistic
above from the three `metrics.txt` files — run `python3 domain_analysis.py` to reproduce.

## Assumptions

1. **One case, one diameter** (Cu, 1.0 mm): the edge-effect mechanism — heat spreading
   through the two outer solid strips — does not depend on D_h or wall material, so the
   conclusion transfers to the other five factorial cases.
2. **Width only**: the study varies spanwise extent (channel count). Channel length is
   common to every factorial case and cancels from comparisons.
3. **Same model idealisations as the parent cases** (effective-medium He-4, fixed-T inlet,
   analytic Kapitza) — inherited by construction, and irrelevant to a same-model
   comparison across N.

## Caveats

1. **Per-channel heat load falls ~2.8% from N5 to N9** (22.19 → 21.58 nW/channel). This is
   bookkeeping, not physics: the two fixed outer-wall strips are amortized over more
   channels as the block widens. The field response to it is <5×10⁻⁶ relative, and the
   factorial's per-channel load (Q_sys/N_ch) is width-independent by definition. Noted so
   a raw Q/N comparison isn't mistaken for an edge effect.
2. The temperature spreads quoted are at the numerical-noise floor of the converged
   solutions — they bound the edge effect, they don't resolve its structure.

## Conclusions

1. The five-channel unit cell is **domain-independent**: widening the array changes
   per-channel ΔP by less than the resolvable precision and per-channel interface
   temperature by <5×10⁻⁶ relative.
2. Edge effects exist, are symmetric, and are five orders of magnitude below the smallest
   Kapitza jump in the factorial (8.55 mK) — negligible by any standard.
3. Together with the parent GCI study, both verification questions are closed: cell size
   (grid convergence) and domain extent (this study).

## Files

- `domain_results.txt` — full per-channel table.
- `domain_analysis.py` — the analysis script (run: `python3 domain_analysis.py`).
- `gen_domain_study.py` — parameterized N-channel case generator + runner.
- `N5/ N7/ N9/` — per case: `metrics.txt`, `blockMeshDict`, per-channel `postProcessing/`
  time series, solver log tail, `.foam` file for ParaView.

## References
1. OpenCFD Ltd., *OpenFOAM v2412 User Guide* (2024).
