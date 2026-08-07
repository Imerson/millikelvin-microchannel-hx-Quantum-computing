# Grid-Convergence (Mesh-Independence) Study

The standard CFD verification question: *is the reported result a property of the physics,
or an artefact of the mesh?* Three systematically refined grids of the most demanding
factorial case (Cu, D_h = 0.5 mm — the finest features and highest cell aspect ratio),
processed with the ASME/Celik Grid Convergence Index procedure [1]. Because all six
factorial cases share the same topology and per-channel cell density, grid independence
here justifies the matched resolution used throughout.

**Verdict: the production mesh carries ≈1.2% discretisation uncertainty on pressure drop
and <0.01% on every temperature. The solution is monotonically convergent and in the
asymptotic range. The mesh is fit for purpose.**

## The three grids

| Folder | Grid | Cells across D_h | Total cells |
|---|---|---|---|
| [`1-coarse`](1-coarse/) | coarse | 14 | 73,920 |
| [`2-medium`](2-medium/) | **medium (production)** | 20 | 208,320 |
| [`3-fine`](3-fine/) | fine | 24 | 367,200 |

Refinement ratios r₃₂ = 1.413, r₂₁ = 1.208 (representative cell size h ∝ N^(−1/3)).
All grids are built by uniform integer scaling of the same `blockMeshDict` with identical
numerics — the only thing that changes is cell size. The medium grid reproduces the
production factorial result exactly (built-in consistency check).

## Results

**Pressure drop** (the grid-sensitive metric):

| Grid | ΔP (mPa) |
|---|---|
| coarse | 11.2522 |
| medium | 11.3736 |
| fine | 11.4099 |

| GCI quantity | Value |
|---|---|
| Apparent order of convergence p | **2.20** (≈ theoretical 2nd order) |
| Richardson extrapolation (h→0) | 11.48 mPa |
| GCI, fine grid | **0.77%** |
| GCI, medium (production) grid | 1.18% |
| Asymptotic-range check GCI₃₂/(r₂₁^p·GCI₂₁) | **1.003 ≈ 1 → confirmed** |

**Temperatures**: interface and outlet temperatures vary by <2e-4 and <3e-3 mK across a
five-fold change in cell count — grid-independent.

## Methodology

The GCI procedure [1] turns three grid solutions into a quantified numerical-uncertainty
band: (i) the apparent order p from the ratio of solution changes between grids (with the
q(p) correction for unequal refinement ratios); (ii) Richardson extrapolation to the
zero-cell-size value; (iii) GCI = 1.25·|e|/(r^p − 1), the safety-factored uncertainty of
each grid; (iv) the asymptotic-range check, which validates the whole procedure.
Run `python3 gci.py` in this folder — it reads each grid's `metrics.txt` and machine-
generates every number above (`gci_results.txt` is its output; `mesh_indep_v2.py` built
and ran the grids).

## Assumptions

1. **One representative case covers the factorial** — all six cases share mesh topology
   and per-channel cell density; the study uses the most demanding geometry.
2. **h ∝ N^(−1/3)** as the representative cell size (fixed domain volume, ASME standard).
3. **ΔP is the operative metric**: temperatures are set by the fluid energy balance
   (fixed inlet + fixed load), not local resolution — and the factorial's headline chip
   temperature is dominated by the *analytic* Kapitza term, which no mesh can affect.
   A chip-temperature-vs-mesh plot would be trivially flat and prove nothing; the honest
   verification is the ΔP convergence.

## Caveats

1. **Non-uniform refinement ratio** (1.41 / 1.21): the extreme channel aspect ratio
   (100 mm × 0.5 mm ≈ 66:1) makes the pressure-Poisson equation stiff, and a 1.4× fine
   mesh stalled against the linear-solver iteration cap (see below). The ASME q(p) term
   handles unequal ratios explicitly, and the asymptotic check (1.003) confirms the grid
   set is valid; r₂₁ = 1.21 sits marginally below the 1.3 guideline of [1].
2. **Fine grid stopped at flow convergence** (t ≈ 1050, ΔP constant to 6 significant
   figures since t = 600) rather than run to t = 6000; coarse/medium ran to 6000.
3. **Temperature grid-independence partly reflects the model**, not only the mesh — the
   fixed-inlet/fixed-load setup pins the energy balance (see Assumption 3).

**Practical solver note** (the reusable lesson): on high-aspect-ratio channel meshes the
p_rgh (pressure) solve can silently hit OpenFOAM's default 1000-iteration cap and stall —
the run looks "slow" but is actually not converging its pressure equation. Fix: raise
`maxIter` (1500 here) and check the iteration count in the log before trusting any
large-mesh run.

## Conclusions

1. Pressure drop converges monotonically at the theoretical order (p = 2.20); the
   production mesh's discretisation uncertainty is ≈1.2% on ΔP.
2. All temperatures are grid-independent to <0.01%.
3. The asymptotic-range check passes (1.003 ≈ 1) — the grids are a valid GCI set.
4. The unit-cell abstraction itself is verified separately: see
   [`4-Domain_Independence/`](4-Domain_Independence/README.md) (5 vs 7 vs 9 channels —
   per-channel results identical to 6 significant figures).

## Files

- `gci.py` — the GCI calculator (run it: `python3 gci.py`; no arguments, no hand-entered values).
- `gci_results.txt` — its output: the numbers quoted above.
- `mesh_indep_v2.py` — builds and runs the three grids (full reproducibility).
- `GCI to understand.docx` — a plain-language explainer of the GCI method.
- `1-coarse/ 2-medium/ 3-fine/` — per grid: `blockMeshDict`, `metrics.txt`, `postProcessing/`
  time series, solver log tail, and a `.foam` file for ParaView.
- `4-Domain_Independence/` — the companion channel-count study.

## References
1. I. B. Celik, U. Ghia, P. J. Roache, C. J. Freitas, H. Coleman and P. E. Raad,
   "Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD
   Applications," *Journal of Fluids Engineering* **130**, 078001 (2008).
2. OpenCFD Ltd., *OpenFOAM v2412 User Guide* (2024).
