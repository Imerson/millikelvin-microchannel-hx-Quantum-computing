# =====================================================================
# Build the 3-D conjugate temperature-field figure (fig:hx-field3d)
# for the Cu, D_h = 1 mm, five-channel unit cell (Cu_1p0, time 6000).
#
# HOW TO RUN (recommended):
#   1. In ParaView, File > Open  ->  Cu_1p0.foam
#      In the Properties panel tick ALL Mesh Regions
#      (solid_wall + domain1..domain5) and the 'T' cell array, then Apply.
#      Set the time to the last step (6000).
#   2. View > Python Shell, then:
#         exec(open('<path-to-this-file>').read())
#      (or paste the whole file into the shell).
#
# It operates on the ACTIVE SOURCE, so whatever you have loaded/selected
# is what it renders. It saves both a PNG and a .pvsm next to the figure.
#
# Tunables are at the top. EXAGG stretches the two transverse directions
# so the slender 100 mm x ~7.5 x ~2 mm cell is legible; set EXAGG = 1.0
# for true scale (then add "transverse dimensions exaggerated" to the
# caption if you keep EXAGG > 1).
# =====================================================================
from paraview.simple import *
import os

# ---------------- tunables ----------------
OUTDIR = ("/Users/imerson/Library/CloudStorage/OneDrive-Personal/Documents/"
          "Education Hub/15-Energy Systems/4-Year 3/4-Dissertation/6-Latex/"
          "638cc3cf5419cef31326d0ee copy/Masters-thesis/Chapter3/Figs")
FOAM = ("/Users/imerson/Library/CloudStorage/OneDrive-Personal/Documents/"
        "Education Hub/15-Energy Systems/4-Year 3/4-Dissertation/2-Model/"
        "3-4K Heat exchanger/Final models/S4_HX_Hybrid_Results/Cu_1p0/Cu_1p0.foam")
EXAGG   = 5.0        # transverse (y,z) exaggeration; 1.0 = true scale
TMIN, TMAX = 10.0, 26.0   # colour range in mK
INLET_FRAC = 0.03   # transverse slice position, as a fraction of the length from the inlet
# ------------------------------------------

paraview.simple._DisableFirstRenderCameraReset()

# --- get the loaded case, or open it if nothing is active ---
src = GetActiveSource()
if src is None:
    print("No active source: opening the .foam (multi-region may need manual region ticking).")
    src = OpenDataFile(FOAM)
    try:
        src.CaseType = 'Reconstructed Case'
        src.CellArrays = ['T']
    except Exception as e:
        print("Reader auto-config skipped:", e)
    Show(src)

# --- go to the last time step (6000) ---
tk = GetTimeKeeper()
times = list(tk.TimestepValues) if tk.TimestepValues else []
view = GetActiveViewOrCreate('RenderView')
if times:
    view.ViewTime = max(times)
UpdatePipeline(max(times) if times else 0.0, src)

# --- optional transverse exaggeration (keeps flow axis x true) ---
base = src
if EXAGG != 1.0:
    base = Transform(Input=src)
    base.Transform.Scale = [1.0, EXAGG, EXAGG]
    UpdatePipeline(max(times) if times else 0.0, base)

# --- convert K -> mK so the legend reads in mK ---
calc = Calculator(Input=base)
calc.AttributeType   = 'Cell Data'
calc.ResultArrayName = 'T_mK'
calc.Function        = 'T*1000'
UpdatePipeline(max(times) if times else 0.0, calc)

# --- geometry bounds (after exaggeration) to place clips relative to data ---
b = calc.GetDataInformation().GetBounds()   # xmin,xmax,ymin,ymax,zmin,zmax
xmin, xmax, ymin, ymax, zmin, zmax = b
cx = 0.5 * (xmin + xmax)
cy = 0.5 * (ymin + ymax)
cz = 0.5 * (zmin + zmax)

# --- (1) axial clip: horizontal plane at channel mid-height, keep lower half.
#     This opens the volume along the flow axis and exposes all five channels. ---
clip = Clip(Input=calc)
clip.ClipType = 'Plane'
clip.ClipType.Origin = [cx, cy, cz]
clip.ClipType.Normal = [0.0, 0.0, 1.0]
clip.Invert = 1

# --- (2) transverse slice near the inlet: shows the 5-channel cross-section
#     and the thermal development region ---
sl = Slice(Input=calc)
sl.SliceType = 'Plane'
sl.SliceType.Origin = [xmin + INLET_FRAC * (xmax - xmin), cy, cz]
sl.SliceType.Normal = [1.0, 0.0, 0.0]

# --- render setup ---
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 1

d1 = Show(clip, view)
d2 = Show(sl, view)
Hide(calc, view)
ColorBy(d1, ('CELLS', 'T_mK'))
ColorBy(d2, ('CELLS', 'T_mK'))

# --- Inferno colormap, fixed 10-26 mK range ---
lut = GetColorTransferFunction('T_mK')
try:
    lut.ApplyPreset('Inferno (matplotlib)', True)
except Exception:
    lut.ApplyPreset('Black-Body Radiation', True)
lut.RescaleTransferFunction(TMIN, TMAX)

d1.SetScalarBarVisibility(view, True)
sb = GetScalarBar(lut, view)
sb.Title = 'T [mK]'
sb.ComponentTitle = ''

# --- camera: shallow isometric ---
view.ResetCamera()
cam = GetActiveCamera()
cam.Azimuth(35)
cam.Elevation(22)
view.ResetCamera()
Render()

# --- save PNG + state ---
if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR, exist_ok=True)
png  = os.path.join(OUTDIR, 'fig_field3d.png')
pvsm = os.path.join(OUTDIR, 'fig_field3d.pvsm')
SaveScreenshot(png, view, ImageResolution=[2400, 1200])
servermanager.SaveState(pvsm)
print("Saved:\n  ", png, "\n  ", pvsm)
