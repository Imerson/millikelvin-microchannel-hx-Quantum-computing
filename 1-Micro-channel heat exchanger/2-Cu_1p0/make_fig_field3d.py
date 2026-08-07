# pvbatch script — fig:hx-field3d  (v2)
# 3-D conjugate T field, Cu_1p0 (5-channel unit cell), t=6000.
# Cutaway: lower half exposed from inlet to x0 (axial cut at channel mid-height,
# showing the development region in all five channels), full-height block beyond x0
# whose upstream face is the transverse cross-section. Common 10-26 mK scale.
# Transverse dimensions exaggerated 5x (consistent with fig:meth-domain3d).
from paraview.simple import *

CASE = "/Users/imerson/Library/CloudStorage/OneDrive-Personal/Documents/Education Hub/15-Energy Systems/4-Year 3/4-Dissertation/2-Model/3-4K Heat exchanger/Final models/S4_HX_Hybrid_Results/Cu_1p0/Cu_1p0.foam"
OUT  = "/tmp/fig_field3d.png"

r = OpenFOAMReader(FileName=CASE)
r.UpdatePipelineInformation()
avail = list(r.MeshRegions.Available)
regions = [x for x in avail if "internalMesh" in x and "/" in x]
regions += [x for x in avail if x.startswith("/domain") and x.endswith("patch/inlet")]
r.MeshRegions = regions
r.CellArrays = ["T"]
t = list(r.TimestepValues)[-1]

view = GetActiveViewOrCreate("RenderView")
scene = GetAnimationScene()
scene.UpdateAnimationUsingDataTimeSteps()
scene.AnimationTime = t

calc = Calculator(Input=r)
calc.AttributeType = "Cell Data"
calc.ResultArrayName = "T_mK"
calc.Function = "T*1000"

c2p = CellDatatoPointData(Input=calc)

tr = Transform(Input=c2p)
tr.Transform.Scale = [1.0, 5.0, 5.0]

ZMID = 0.005    # channel mid-height (1.0 mm, x5)
X0   = 0.020    # transverse cut 35 mm from inlet

# A: development window — lower half, inlet..X0 (axial cut visible from above)
cA = Clip(Input=tr);  cA.ClipType.Origin = [0, 0, ZMID];  cA.ClipType.Normal = [0, 0, 1]; cA.Invert = 1
cA2 = Clip(Input=cA); cA2.ClipType.Origin = [X0, 0, 0];   cA2.ClipType.Normal = [1, 0, 0]; cA2.Invert = 1
cC = Clip(Input=tr); cC.ClipType.Origin = [0.0005, 0, 0]; cC.ClipType.Normal = [1, 0, 0]; cC.Invert = 1
cA3 = Clip(Input=cA2); cA3.ClipType.Origin = [0.0008, 0, 0]; cA3.ClipType.Normal = [1, 0, 0]; cA3.Invert = 0
# B: full-height block downstream of X0 (tiny offset kills z-fighting on the shared plane)
cB = Clip(Input=tr);  cB.ClipType.Origin = [X0 + 3e-4, 0, 0]; cB.ClipType.Normal = [1, 0, 0]; cB.Invert = 0

lut = GetColorTransferFunction("T_mK")
lut.AutomaticRescaleRangeMode = "Never"
lut.ApplyPreset("Turbo", True)

for src, rep in ((cA3, "Surface With Edges"), (cB, "Surface"), (cC, "Surface With Edges")):
    d = Show(src, view)
    d.Representation = rep
    ColorBy(d, ("POINTS", "T_mK"))
    d.LookupTable = lut
    if rep == "Surface With Edges":
        d.EdgeColor = [0.25, 0.25, 0.25]
        d.LineWidth = 1.0

lut.RescaleTransferFunction(10.0, 26.0)

bar = GetScalarBar(lut, view)
bar.Title = "T (mK)"
bar.ComponentTitle = ""
bar.TitleColor = [0, 0, 0]
bar.LabelColor = [0, 0, 0]
bar.TitleFontSize = 16
bar.LabelFontSize = 14
bar.ScalarBarLength = 0.40
bar.WindowLocation = "Any Location"
bar.Position = [0.78, 0.13]
bar.AutomaticLabelFormat = 1
bar.AddRangeLabels = 0
bar.UseCustomLabels = 1
bar.CustomLabels = [10, 14, 18, 22, 26]
bar.Visibility = 1

view.UseColorPaletteForBackground = 0
view.Background = [1, 1, 1]
view.OrientationAxesVisibility = 0

# camera upstream-above-left: inlet face, axial cut window, and the x0 face all visible
view.CameraPosition   = [-0.085, -0.058, 0.050]
view.CameraFocalPoint = [0.030, 0.020, 0.004]
view.CameraViewUp     = [0, 0, 1]
ResetCamera(view)
GetActiveCamera().Dolly(1.45)
lut.RescaleTransferFunction(10.0, 26.0)
Render()
SaveScreenshot(OUT, view, ImageResolution=[2600, 1600])
SaveState("/tmp/fig_field3d.pvsm")
print("STATE SAVED")
print("SAVED:", OUT)
