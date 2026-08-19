# Sinter vs Microchannel — The Thermal-Hydraulic Benchmark

The machined microchannel (this repository's CFD cases) benchmarked against the commercial
standard it must displace: the **sintered-silver powder heat exchanger**. The sinter cannot
be meshed — its pore geometry is process-dependent and unknown a priori — so it is
represented by an analytic, literature-based model, and the two concepts meet on a common
basis: the same normalised 40×40×100 mm block, the same He-4 coolant, the same superficial
velocity (hence the same volumetric throughput).

**Verdict: the sinter wins raw conductance (its enormous internal area is unmatchable),
but the microchannel wins conductance-per-unit-pumping-power by ≈2.4×10⁴** (silver
0.5 mm channels vs the *idealised* silver sinter) — open channels cost a sub-pascal
pressure drop where the sinter's nanometre pores impose ≈3 MPa. The FOM ratio is
independent of both flow velocity and operating temperature, so this is a structural
verdict, not an operating-point artifact.

## The figure of merit

```
FOM = G / W_pump          G = 1/R_K = T³·A_wet/C_K       W_pump = ΔP·V̇
```

Raw thermal resistance ignores what it costs to force coolant through the exchanger; the
FOM prices it in. Two structural properties make it robust: ΔP is linear in velocity in
both Darcy and Hagen–Poiseuille flow, so both pumping powers scale as U² and the ratio
cancels velocity; and G ∝ T³ for both technologies while pumping power is
temperature-independent, so the ratio cancels temperature too.

## Methodology

- **Microchannel side**: ΔP taken from the converged CFD cases in
  [`../1-Micro-channel heat exchanger/`](../1-Micro-channel%20heat%20exchanger/README.md)
  (cross-checked against the square-duct Hagen–Poiseuille value: ratio 1.00–1.14);
  Kapitza resistance over the exact geometric wetted area.
- **Sinter side**: ΔP from **Darcy's law with Kozeny–Carman permeability**
  K = φ³d_p²/[180(1−φ)²] = 1.4×10⁻¹⁷ m². The pore Reynolds number
  Re_p ≈ 4.5×10⁻³ ≪ 1 puts the flow deep in the creeping regime, so Darcy is the correct
  reduction and the Ergun inertial term is negligible. Kapitza resistance over the
  packed-sphere surface area.
- Run `python3 analysis.py` to reproduce every number and figure; the Excel workbook
  contains the same computation as live formulas (Inputs / Microchannel / Sinter /
  Comparison / Charts).

## Assumptions

1. **Sinter pore diameter d_p = 0.07 µm** — the measured fine-silver-sinter pore scale of
   Nakagawa [1]; **porosity φ = 0.5** — the standard pressed-silver value [3].
2. **The sinter is granted its full idealised (microscopic) area** — its absolute best
   case. The measured reality is far less favourable: below T* ≈ 700 mK the phonon mean
   free path in He-II exceeds the sinter's sub-micron structure, and measurements find
   only ≈1.5× the flat-plate area thermally effective [1], with the quasiparticle
   argument of Autti et al. [2] reaching the equivalent conclusion. Granting the ideal
   area means every conclusion drawn against the sinter is conservative.
3. **Common effective-medium He-4 properties** on both sides of the comparison
   (ρ = 145 kg/m³, μ = 1×10⁻⁶ Pa·s) — identical on both sides, so idealisations cancel
   from the ratio.
4. **Same interface physics on both sides**: R_K = C_K/T³ with literature C_K [4,5].

## Caveats

1. **Model-to-model, not model-to-measurement**: the microchannel side is converged CFD,
   the sinter side is analytic porous-media theory on literature inputs. No new experiment
   is reported.
2. **Porosity sensitivity**: sweeping φ = 0.4–0.6 moves the sinter ΔP by roughly an order
   of magnitude — bounded in the dissertation appendix, and small against a 4-order FOM
   gap. The verdict survives any plausible porosity.
3. **The comparison inherits the microchannel model's caveats** (upper-bound chip
   temperatures, effective-medium coolant) — see the factorial README.
4. The effective-area reduction (Assumption 2) is applied only as a bound, not claimed as
   a measured property of any particular sinter; real sinters vary by process.

## Conclusions

1. **Raw conductance**: the sinter wins at high loads and this study does not displace it
   there — square metres per gram of internal area is not matchable by machining.
2. **Thermal-hydraulic efficiency**: the microchannel wins by ≈2.4×10⁴ on
   conductance-per-pumping-power, independent of velocity and temperature.
3. **In superfluid He-II below T* ≈ 700 mK** — the entire 10–100 mK operating range of a
   mixing-chamber chip exchanger — the sinter's sole advantage (area) is largely inactive
   [1,2]: the machined channel's geometric surface stays fully phonon-effective while only
   the sinter's envelope does. On effective area the channel then leads by ~10², on top of
   the FOM verdict.
4. **The two technologies are complements with a load-set crossover, not competitors**:
   sinter where raw conductance at hundreds of microwatts is everything; microchannel for
   low-microwatt chip loads, where it offers exactly known, reproducible, simulatable
   geometry and four orders of magnitude better pumping economy. (For the ³He/dilute
   streams of the internal step exchangers, sinters remain the established solution — the
   He-II argument does not extend there without separate analysis.)

## 1 µW load envelope — CFD-verified low-load closure

The load-set crossover in Conclusion 4 rests on the microchannel holding the 10–20 mK band at
*low-microwatt* chip loads. That claim was originally an analytic extrapolation of the 15 µW
factorial; it is now **CFD-verified**. [`1uW_load_envelope/`](1uW_load_envelope/README.md)
holds the 12 OpenFOAM runs (six geometries × two cold seeds) at Q_sys = 1 µW, the
comparison table (`comparison_1uW.txt/.csv`), the generator script and the bracket runner.
Result: Ag 0.5 mm at ≈17.7 mK, Ag 1.0 mm marginal at ≈24.9 mK, every copper case above the
band — the Chapter 3 low-load table reproduced to the millikelvin. The two-seed bracket also
demonstrates that the conjugate temperature *level* is undetermined at 1 µW (segregated-solver
level degeneracy), so T_int there comes from the fluid energy balance (11.0 mK); load,
hydraulics and coupling come from the solver. Any earlier analytic-only 1 µW assessment is
superseded by that folder.

## Files

- `analysis.py` — full computation, sanity checks, and figure generation (run it).
- `Sinter_vs_Microchannel_comparison.xlsx` — the same model as a live workbook.
- `fig_dP.png` — pressure drop, microchannel vs sinter (the 5–6 order gap).
- `fig_conductance.png` — raw Kapitza conductance (the sinter's win).
- `fig_pumping.png` — pumping power at matched throughput.
- `fig_FOM.png` — the figure of merit (the microchannel's win).
- `fig_FOM_vs_velocity.png` — demonstration that the FOM ratio is velocity-independent.
- `1uW_load_envelope/` — CFD-verified 1 µW closure (12 cases, table, scripts, README).

## References
1. H. Nakagawa, "Heat exchange performance of sintered fine silver powders in ultra-low
   temperature cooling of superfluid ⁴He," *Cryogenics* **132**, 103690 (2023).
2. S. Autti et al., "Effect of the boundary condition on the Kapitza resistance between
   superfluid ³He-B and sintered metal," *Physical Review B* **102** (2020).
3. F. Pobell, *Matter and Methods at Low Temperatures*, 3rd ed., Springer (2007).
4. G. L. Pollack, "Kapitza Resistance," *Reviews of Modern Physics* **41**, 48-81 (1969).
5. J. W. Ekin, *Experimental Techniques for Low-Temperature Measurements*, Oxford
   University Press (2006).
6. X. Shang et al., "Numerical and thermal resistance analysis on the cryogenic porous
   medium heat exchanger with liquid channel," *Int. J. Thermal Sciences* (2024).
