# Millikelvin Microchannel Heat Exchanger — Conjugate CFD for Quantum-Computing Cryostats

OpenFOAM models, verification studies, and analysis scripts from the Msc. dissertation
**"Design and CFD Assessment of a Microchannel Mixing-Chamber Heat Exchanger for
Millikelvin Quantum-Computing Cryostats"** (Imerson Joao, University of Oxford).

The energy cost of quantum computing is set not by the qubits but by the machinery that
keeps them cold — and at the coldest point of that machinery, the ~10 mK mixing chamber
of a dilution refrigerator, the entire cooling problem collapses onto a single interface:
the **Kapitza resistance** between the metal cold plate and superfluid helium, R_K = C_K/T³.
This repository asks whether a *machined, exactly-known* microchannel geometry can replace
the *sintered-silver powder* that is the commercial standard there — and answers with a
verified CFD factorial, two verification studies, and an analytic benchmark.

## Key results

| Finding | Number |
|---|---|
| The regime is **Kapitza-limited** | interfacial term = 36–90% of the chip-temperature rise; CFD conjugate interface at 25 mK in all six cases |
| Material lever (Ag vs Cu) | exact **factor 4.0** at every diameter (= C_K ratio) |
| Area lever | ΔT_K ∝ 1/A_wet, at sub-pascal hydraulic cost |
| Best case: **silver, D_h = 0.5 mm** | **chip at 33.5 mK** under the full 15 µW load (upper bound) |
| Sinter benchmark | microchannel wins conductance-per-pumping-power by **≈2.4×10⁴**; sinter keeps raw conductance |
| Low-load envelope (1 µW, CFD-verified) | Ag 0.5 mm at **≈17.7 mK**; Chapter 3 low-load table reproduced; conjugate level shown degenerate at weak load |
| Mesh verification (GCI) | ≈1.2% ΔP uncertainty on the production mesh, asymptotic range confirmed |
| Unit-cell verification | per-channel ΔP identical to 6 significant figures across 5/7/9-channel domains |

## Repository map

| Folder | Contents |
|---|---|
| [`1-Micro-channel heat exchanger/`](1-Micro-channel%20heat%20exchanger/README.md) | The six-case factorial (Cu/Ag × 0.5/1.0/2.0 mm): complete converged OpenFOAM cases, each with its own README (methodology, assumptions, verification gates, caveats, conclusions) |
| [`2-Mesh_Independence study/`](2-Mesh_Independence%20study/README.md) | Grid-convergence study (ASME/Celik GCI, three grids) + [domain-independence study](2-Mesh_Independence%20study/4-Domain_Independence/README.md) (5/7/9-channel unit cells) |
| [`3-Sinter_vs_Microchannel_Comparison/`](3-Sinter_vs_Microchannel_Comparison/README.md) | Analytic benchmark vs sintered silver: Darcy/Kozeny–Carman hydraulics, conductance-per-pumping-power figure of merit, charts + live Excel workbook; [`1uW_load_envelope/`](3-Sinter_vs_Microchannel_Comparison/1uW_load_envelope/README.md) — the CFD-verified 1 µW closure (12 cases) |
| [`Figure_scripts/`](Figure_scripts/README.md) | The Python/ParaView scripts that generate every data-driven figure of the dissertation, organised by chapter |

## The method in one paragraph

Each case is a conjugate heat-transfer model (`chtMultiRegionSimpleFoam`, OpenFOAM v2412)
of a five-channel unit cell: solid block + He-4 coolant entering at the 10 mK bath, chip
load imposed as a verified fixed flux. The Kapitza resistance is **deliberately not
resolved in the solver** — a ~10³ m²K/W interfacial resistance against a highly conductive
solid defeats segregated conjugate solvers (the implied interfacial conductance is ~9
orders of magnitude below the near-wall cell conductance; both the coupled-baffle BC and a
meshed resistive layer fail). It is instead applied **analytically on the converged
interface temperature**: ΔT_K = (Q/A_wet)·C_K/T³. The hybrid validates itself: the
factorial reproduces the exact factor-4 material ratio and the exact inverse-area scaling.
That finding — *resolve the field, apply the interface law analytically* — is itself one
of the study's transferable results for cryogenic CFD.

## Using this repository

**Requirements**: [OpenFOAM v2412](https://www.openfoam.com) (re-running cases),
[ParaView](https://www.paraview.org) (viewing results), Python 3 with NumPy/Matplotlib
(analysis scripts). Viewing and analysis need no OpenFOAM install.

- **Look at a result**: open any case's `.foam` file in ParaView (e.g.
  `1-Micro-channel heat exchanger/1-Cu_0p5/Cu_0p5.foam`), load all regions, select the
  last time step, colour by `T`.
- **Check the numbers**: every quoted figure is machine-generated — `results_hybrid.txt`
  per case, `gci.py` for the mesh study, `domain_analysis.py` for the unit-cell study,
  `analysis.py` for the sinter benchmark. Run them; nothing is hand-entered.
- **Re-run a case**: `chtMultiRegionSimpleFoam` in the case folder (mesh and dictionaries
  are shipped; cases resume from the converged state).

## Honest limitations (details in each folder's README)

- He-4 is modelled as an **effective Newtonian medium** — superfluid counterflow is not a
  continuum process; the idealisation is identical across cases and cancels from every
  relative result.
- Chip temperatures are **deliberate upper bounds** (R_K evaluated at the cooler
  fluid-side temperature).
- ~50% of the load back-conducts to the fixed-temperature inlet (a low-Péclet boundary
  artifact) — energy is conserved, and no conclusion rests on outlet enthalpy.
- The sinter comparison is **model-to-model**, on literature pore properties, with the
  sinter granted its idealised area.

## Citing

If you use these cases or scripts, please cite the dissertation:

> I. Joao, *Design and CFD Assessment of a Microchannel Mixing-Chamber Heat Exchanger for
> Millikelvin Quantum-Computing Cryostats*, MEng dissertation, University of Oxford.

## Key references

1. G. L. Pollack, "Kapitza Resistance," *Reviews of Modern Physics* **41**, 48-81 (1969).
2. F. Pobell, *Matter and Methods at Low Temperatures*, 3rd ed., Springer (2007).
3. J. W. Ekin, *Experimental Techniques for Low-Temperature Measurements*, Oxford University Press (2006).
4. H. Nakagawa, "Heat exchange performance of sintered fine silver powders in ultra-low temperature cooling of superfluid ⁴He," *Cryogenics* **132**, 103690 (2023).
5. I. B. Celik et al., "Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications," *J. Fluids Engineering* **130**, 078001 (2008).
6. OpenCFD Ltd., *OpenFOAM v2412 User Guide* (2024).

*License: to be added before publication.*
