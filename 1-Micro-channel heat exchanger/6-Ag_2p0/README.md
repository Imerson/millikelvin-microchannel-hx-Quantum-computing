# 6-Ag_2p0 -- Silver, D_h = 2.0 mm

One of the six cases of the microchannel factorial (2 materials x 3 hydraulic diameters).
A silver cold plate at the mixing chamber of a dilution refrigerator holds a qubit chip
at millikelvin temperature; superfluid He-4 at 10 mK flows along 100 mm square channels.
This folder contains the **converged OpenFOAM case** (t = 6000, with the two prior
snapshots), its post-processing time series, and the machine-generated result summary.

**Headline result: physical chip temperature = 60.52 mK** at the full 15 uW system load
(conservative upper bound), of which **70%** is the Kapitza interfacial jump.

| Parameter | Value |
|---|---|
| Material / kappa_s | silver / 9.21 W/(m K) (constant, see Assumptions) |
| Kapitza coefficient C_K | 0.005 K^4 m^2/W |
| Hydraulic diameter / wall | 2.0 mm / 1.00 mm |
| Channels in full 40x40 mm block | N_ch = 169 (5-channel unit cell modelled, scaled by N_ch/5) |
| Load: system / modelled | 15 uW / Q_model = 443.80 nW |
| Flow | U = 1 mm/s, Re = 290 (laminar), inlet 10 mK |

## Results (converged, t = 6000)

| Quantity | Value |
|---|---|
| Gate-1 verified load | -443.84 nW (target -443.80, <0.1% error) |
| CFD conjugate interface temperature T_int | 25.00 mK |
| Kapitza resistance R_K = C_K/T_int^3 | 320.2 m^2 K/W |
| Kapitza jump dT_K = (Q_model/A_wet) R_K | 35.53 mK |
| **Physical chip temperature T_chip = T_int + dT_K** | **60.52 mK** |
| Total resistance (T_chip - 10 mK)/Q_model | 1.138e+05 K/W |
| Kapitza fraction of the total rise | 70% |
| Pressure drop | 8.078e-04 Pa |

## Methodology (the hybrid method)

The chip-to-coolant resistance decomposes as R_total = R_cond + R_Kapitza + R_conv and is
**Kapitza-dominated** at millikelvin temperature. The Kapitza resistance R_K = C_K/T^3 [1,2]
is a sub-nanometre interfacial phenomenon with no continuum structure to resolve, and its
~10^3 m^2K/W magnitude cannot be imposed inside a segregated conjugate solver (the implied
interfacial conductance is ~9 orders of magnitude below the near-wall cell conductance;
see the repository root README). The model is therefore a **hybrid**:

1. **CFD resolves the field problem** -- conjugate conduction, laminar flow, pressure drop,
   and the interface temperature T_int -- with `chtMultiRegionSimpleFoam` (OpenFOAM v2412 [7])
   on a structured hexahedral mesh (20 cells across D_h, 60 axial; 208,320 cells).
   The chip load enters as a `fixedGradient` flux on the chip face
   (grad = -3.0119e-05 K/m -> q'' = kappa x |grad| = 2.7740e-04 W/m^2, delivering exactly Q_model);
   the fluid-solid interface carries plain temperature/flux continuity with **no** contact
   resistance.
2. **The Kapitza jump is applied analytically** on the converged field:
   `R_K = C_K/T_int^3`, `dT_K = (Q_model/A_wet) x R_K`, `T_chip = T_int + dT_K`
   (A_wet = 4.000e-03 m^2 for the 5-channel cell). This is the standard treatment of a 0-D
   interfacial law in cryogenic heat-exchanger modelling [5,6].

The method validates itself in the factorial: the silver/copper temperature-jump ratio is
exactly 4.0 (the C_K ratio) at every diameter, and dT_K scales exactly inversely with
wetted area -- the two signatures an analytic Kapitza term must reproduce if no physics
has been lost.

## Assumptions

1. **Constant solid conductivity** (kappa = 9.21 W/(m K), the Wiedemann-Franz value at
   ~30 mK for this purity [2]). Justified: the resolved solid is isothermal to nanokelvin,
   so no measurable quantity depends on kappa(T); the imposed-gradient BC delivers the load
   exactly regardless (verified by Gate 1).
2. **He-4 as an effective Newtonian medium** (rho = 145 kg/m^3 [4], mu = 1e-6 Pa s,
   c_p = 5 J/(kg K), kappa_eff = 0.001 W/(m K)). Superfluid counterflow is a quantum,
   phonon-mediated process no standard solver represents [3,4]; the effective medium
   reproduces the one property the comparison needs -- a fluid-side resistance negligible
   against the interfacial one -- and is identical in all six cases, so it cancels from
   every relative result.
3. **Kapitza applied analytically, not resolved** (see Methodology).
4. **R_K evaluated at the fluid-side interface temperature** (~25 mK), the cooler side, so
   the reported dT_K and T_chip are deliberate **upper bounds**.
5. **Five-channel unit cell** with symmetry sides, scaled by N_ch/5 -- verified numerically
   in [`../../2-Mesh_Independence study/4-Domain_Independence/`](../../2-Mesh_Independence%20study/4-Domain_Independence/README.md).

## Verification

| Gate | Test | Result |
|---|---|---|
| 1 -- load | integral of wall heat flux over chip face = Q_model | pass (-443.84 nW, <0.1%) |
| 2 -- energy balance | fluid enthalpy rise + inlet conduction = Q_model | closes when both fluid boundaries counted (see Caveats) |
| 3 -- Kapitza self-consistency | dT_K = (Q_model/A_wet) R_K at T_int | applied analytically |
| 4 -- flow | laminar (Re = 290); dP = 8.078e-04 Pa | pass |

Mesh: grid-convergence (GCI) study in [`../../2-Mesh_Independence study/`](../../2-Mesh_Independence%20study/README.md)
(~1.2% discretisation uncertainty on dP on this mesh class, temperatures grid-independent).

## Caveats

1. **The reported chip temperature is an upper bound** (Assumption 4): the full
   self-consistent closure would evaluate R_K at the hotter solid-side temperature, giving
   a smaller jump.
2. **~50% of the load back-conducts to the fixed-temperature inlet** at Pe ~ 0.7. Energy is
   conserved (the inlet conduction returns to the bath), the artifact is identical across
   all six cases, and no conclusion rests on the outlet enthalpy -- but absolute outlet
   temperatures should not be quoted from this model.
3. **C_K values carry the experimental scatter of the interfacial literature** [1,2]; the
   factor-4 Cu/Ag ratio is robust, the absolute values less so.
4. **Effective-medium fluid**: absolute fluid-side quantities inherit the idealisation
   (Assumption 2); relative results do not.

## Conclusions

This case is the coarsest silver geometry. At 60.5 mK it lands within a millikelvin of the *finest copper* case (59.2 mK) despite having four times less wetted area -- the cleanest single illustration that the factor-4 material lever and the factor-4 area lever (0.5 mm vs 2.0 mm) are worth the same amount, exactly as R_K = C_K/T^3 predicts.

## How to open / re-run

- **ParaView**: open `Ag_2p0.foam`, load all regions (`solid_wall`, `domain1-5`), time 6000.
- **Re-run**: with OpenFOAM v2412: `chtMultiRegionSimpleFoam` in this folder re-converges
  from the shipped state (the mesh and all dictionaries are included; runs from t = 6000).
- `postProcessing/` holds the function-object time series (chip-face load, interface and
  outlet temperatures, mass flow, inlet/outlet pressure); `results_hybrid.txt` is the
  machine-generated summary; `log.hybrid` is the solver log tail.

## References
1. G. L. Pollack, "Kapitza Resistance," *Reviews of Modern Physics* **41**, 48-81 (1969).
2. J. W. Ekin, *Experimental Techniques for Low-Temperature Measurements*, Oxford University Press (2006).
3. F. Pobell, *Matter and Methods at Low Temperatures*, 3rd ed., Springer (2007).
4. R. J. Donnelly and C. F. Barenghi, "The Observed Properties of Liquid Helium at the Saturated Vapor Pressure," *J. Phys. Chem. Ref. Data* **27**, 1217-1274 (1998).
5. X. Shang et al., "Numerical and thermal resistance analysis on the cryogenic porous medium heat exchanger with liquid channel," *Int. J. Thermal Sciences* (2024).
6. X. Guan et al., "An efficient numerical method for modeling silver powder heat exchanger in dilution refrigerator," *Cryogenics* (2024).
7. OpenCFD Ltd., *OpenFOAM v2412 User Guide* (2024).
