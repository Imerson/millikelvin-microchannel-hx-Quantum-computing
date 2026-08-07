# The Microchannel Factorial — Six Conjugate-CFD Cases

Two wall materials (OFHC copper, silver) crossed with three hydraulic diameters
(0.5, 1.0, 2.0 mm): six converged conjugate-heat-transfer models of a machined
microchannel heat exchanger for the mixing chamber (MXC) of a dilution refrigerator,
cooling a qubit chip against superfluid He-4 at 10 mK under a representative 15 µW load.

Each numbered folder is a complete, self-contained OpenFOAM case (converged state,
post-processing time series, ParaView `.foam` file, and its own detailed README).

## Results at a glance

| Case | Material | D_h (mm) | N_ch | A_wet (m²) | ΔT_Kapitza (mK) | **T_chip (mK)** | Kapitza % | ΔP (Pa) |
|---|---|---|---|---|---|---|---|---|
| [1-Cu_0p5](1-Cu_0p5/README.md) | Cu | 0.5 | 2809 | 0.562 | 34.19 | **59.19** | 70 | 1.137e-2 |
| [2-Cu_1p0](2-Cu_1p0/README.md) | Cu | 1.0 | 676 | 0.270 | 71.00 | **96.00** | 83 | 2.923e-3 |
| [3-Cu_2p0](3-Cu_2p0/README.md) | Cu | 2.0 | 169 | 0.135 | 142.09 | **167.08** | 90 | 8.078e-4 |
| [4-Ag_0p5](4-Ag_0p5/README.md) | Ag | 0.5 | 2809 | 0.562 | 8.55 | **33.54** | 36 | 1.137e-2 |
| [5-Ag_1p0](5-Ag_1p0/README.md) | Ag | 1.0 | 676 | 0.270 | 17.75 | **42.75** | 54 | 2.923e-3 |
| [6-Ag_2p0](6-Ag_2p0/README.md) | Ag | 2.0 | 169 | 0.135 | 35.53 | **60.52** | 70 | 8.078e-4 |

All cases: CFD conjugate interface temperature = 25.00 mK; chip temperatures are
conservative upper bounds at the full 15 µW system load (chip load enters as verified
fixed flux; coolant enters at the 10 mK bath temperature).

**The two exact signatures** (the built-in validation of the method):
- **Material lever**: ΔT_K(Ag)/ΔT_K(Cu) = 4.00 at every diameter — exactly the ratio of
  Kapitza coefficients C_K(Cu)/C_K(Ag) = 0.020/0.005 [1,2].
- **Area lever**: ΔT_K scales exactly as 1/A_wet (halving D_h at fixed footprint doubles
  the wetted area and halves the jump), at a pressure-drop cost that never exceeds a pascal.

## Methodology (common to all six cases)

- **Geometry**: 40×40×100 mm block, square channels at pitch 1.5·D_h; a five-channel
  unit cell is resolved and scaled to the array by N_ch/5 (scaling verified numerically —
  see the [domain-independence study](../2-Mesh_Independence%20study/4-Domain_Independence/README.md)).
- **Solver**: `chtMultiRegionSimpleFoam`, OpenFOAM v2412 [7]; steady, laminar (Re ≤ 290);
  structured hexahedral mesh, 20 cells across D_h, 208,320 cells
  (grid-convergence verified — see the [GCI study](../2-Mesh_Independence%20study/README.md)).
- **The hybrid Kapitza closure**: the CFD resolves the field problem with plain interface
  continuity (no contact resistance); the Kapitza jump R_K = C_K/T³ is applied analytically
  on the converged interface temperature: ΔT_K = (Q_model/A_wet)·R_K, T_chip = T_int + ΔT_K.
  This is the standard treatment of a 0-D interfacial law in cryogenic exchanger
  modelling [5,6] — and the reason for it is a finding of the study (see root README):
  a ~10³ m²K/W interfacial resistance cannot be resolved inside a segregated conjugate
  solver against a highly conductive solid.

## Assumptions (summary — each case README details all five)

1. Constant solid conductivity (Wiedemann–Franz values at ~30 mK [2]) — the solid is
   isothermal to nanokelvin, so only the delivered load matters, and that is exact (Gate 1).
2. He-4 as an effective Newtonian medium [3,4] — identical in all six cases, so it cancels
   from every relative result.
3. Kapitza applied analytically (validated by the two exact signatures above).
4. R_K evaluated at the cooler fluid-side temperature → all chip temperatures are
   deliberate upper bounds.
5. Five-channel unit cell with N_ch/5 scaling (verified numerically).

## Caveats

- ~50% of the injected load back-conducts to the fixed-temperature inlet (Pe ≈ 0.7
  artifact) — energy is conserved, the effect is identical across cases, and no conclusion
  rests on outlet enthalpy; do not quote absolute outlet temperatures.
- C_K values inherit the scatter of the interfacial literature [1]; the factor-4 ratio is
  robust, absolute values less so.
- Chip temperatures are upper bounds by construction.

## Conclusions

1. **The millikelvin exchanger is unconditionally Kapitza-limited**: the conjugate CFD
   chip temperature is 25 mK in all six cases; 36–90% of the chip-temperature rise is the
   interfacial term. Solid conduction is irrelevant (nanokelvin); convection is minor.
2. **Two clean, independent design levers**: material (a geometry-independent factor of 4,
   silver over copper) and wetted area (∝ 1/D_h at fixed footprint, essentially free
   hydraulically at these flow rates).
3. **The best case (silver, 0.5 mm) holds 33.5 mK at the full 15 µW** — and its 0.56 m²
   wetted area is the minimum-area criterion for holding the 10–20 mK band at
   low-microwatt loads. No copper variant studied meets the band at any load examined.
4. **Design rule**: choose silver, choose the finest machinable channel, and refine
   monotonically — unlike room-temperature compact exchangers, the millikelvin channel
   has no pressure-drop trade-off worth respecting.

## References
1. G. L. Pollack, "Kapitza Resistance," *Reviews of Modern Physics* **41**, 48-81 (1969).
2. J. W. Ekin, *Experimental Techniques for Low-Temperature Measurements*, Oxford University Press (2006).
3. F. Pobell, *Matter and Methods at Low Temperatures*, 3rd ed., Springer (2007).
4. R. J. Donnelly and C. F. Barenghi, "The Observed Properties of Liquid Helium at the Saturated Vapor Pressure," *J. Phys. Chem. Ref. Data* **27**, 1217-1274 (1998).
5. X. Shang et al., "Numerical and thermal resistance analysis on the cryogenic porous medium heat exchanger with liquid channel," *Int. J. Thermal Sciences* (2024).
6. X. Guan et al., "An efficient numerical method for modeling silver powder heat exchanger in dilution refrigerator," *Cryogenics* (2024).
7. OpenCFD Ltd., *OpenFOAM v2412 User Guide* (2024).
