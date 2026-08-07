#!/usr/bin/env python3
# Channel-count (domain) independence study — Cu_1p0 hybrid config, N = 5 / 7 / 9 channels.
# One parameterized generator builds all three; N=5 must reproduce production S4_MC_Cu_1p0.
import subprocess, os, glob, re, shutil
OF="source /usr/lib/openfoam/openfoam2412/etc/bashrc 2>/dev/null"
BASE="/home/ubuntu/cases"; SRC=f"{BASE}/S4_MC_Cu_1p0"; OUT=f"{BASE}/S4_Domain_Independence"
Dh=1.0e-3; TW=0.5e-3; L=0.1                       # Cu_1p0 geometry, exactly as production
NCH=20; NW=4; NAX=60                              # production cell counts (20/Dh, 4/wall, 60 axial)
KS=13.08; GRAD=-1.060398e-05                      # exact production chipFace gradient (Cu_1p0)
def sh(cmd,cwd): return subprocess.run(f'bash -c "{OF}; cd {cwd}; {cmd}"',shell=True,capture_output=True,text=True)
def H(cls,obj,loc):
    return ("FoamFile\n{\n    version 2.0; format ascii;\n"
            f"    class {cls}; location \"{loc}\"; object {obj};\n}}\n")

def build_blockmesh(d,N):
    ys=[0.0]
    for _ in range(N): ys+=[ys[-1]+TW, ys[-1]+TW+Dh]
    ys.append(ys[-1]+TW)
    zs=[0.0, TW, TW+Dh, 2*TW+Dh]
    V=[]; idx={}
    def v(x,y,z):
        k=(round(x,12),round(y,12),round(z,12))
        if k not in idx: idx[k]=len(V); V.append((x,y,z))
        return idx[k]
    blocks=[]; F={'inlet':[],'outlet':[],'chipFace':[],'hotPlate':[],'outerY0':[],'outerY3':[]}
    nyb=2*N+1
    for iy in range(nyb):
        ya,yb=ys[iy],ys[iy+1]
        for iz in range(3):
            za,zb=zs[iz],zs[iz+1]
            p0=v(0,ya,za); p1=v(0,yb,za); p2=v(0,yb,zb); p3=v(0,ya,zb)
            p4=v(L,ya,za); p5=v(L,yb,za); p6=v(L,yb,zb); p7=v(L,ya,zb)
            isch=(iy%2==1 and iz==1)
            zone=f"domain{(iy+1)//2}" if isch else "solid_wall"
            ny=NCH if iy%2==1 else NW; nz=NCH if iz==1 else NW
            blocks.append(f"    hex ({p0} {p1} {p2} {p3} {p4} {p5} {p6} {p7}) {zone} ({ny} {nz} {NAX}) simpleGrading (1 1 1)")
            F['inlet'].append(f"({p0} {p3} {p2} {p1})")
            F['outlet'].append(f"({p4} {p5} {p6} {p7})")
            if iz==0: F['chipFace'].append(f"({p0} {p1} {p5} {p4})")
            if iz==2: F['hotPlate'].append(f"({p3} {p7} {p6} {p2})")
            if iy==0: F['outerY0'].append(f"({p0} {p4} {p7} {p3})")
            if iy==nyb-1: F['outerY3'].append(f"({p1} {p2} {p6} {p5})")
    with open(f"{d}/system/blockMeshDict","w") as fo:
        fo.write(H("dictionary","blockMeshDict","system"))
        fo.write(f"// Domain-independence variant: N={N} channels, Cu_1p0 geometry (Dh=1mm, tw=0.5mm, L=100mm)\n")
        fo.write("convertToMeters 1;\nvertices\n(\n")
        for (x,y,z) in V: fo.write(f"    ({x:.7e} {y:.7e} {z:.7e})\n")
        fo.write(");\nblocks\n(\n"+"\n".join(blocks)+"\n);\nedges();\nboundary\n(\n")
        for nm,typ in [("inlet","patch"),("outlet","patch"),("chipFace","wall"),
                       ("hotPlate","wall"),("outerY0","wall"),("outerY3","wall")]:
            fo.write(f"    {nm} {{ type {typ}; faces (\n        "+"\n        ".join(F[nm])+"\n    ); }\n")
        fo.write(");\nmergePatchPairs ();\n")

def write_functions(N):
    s="functions\n{\n"
    s+=("    wallHeatFlux_solid { type wallHeatFlux; libs (fieldFunctionObjects); region solid_wall;\n"
        "        patches (chipFace); writeControl timeStep; writeInterval 200; log true; }\n")
    s+=("    Q_chipFace { type surfaceFieldValue; libs (fieldFunctionObjects); region solid_wall;\n"
        "        regionType patch; name chipFace; operation areaIntegrate; fields (wallHeatFlux);\n"
        "        writeControl timeStep; writeInterval 200; log true; writeFields false; }\n")
    for k in range(1,N+1):
        s+=(f"    T_int_s_d{k} {{ type surfaceFieldValue; libs (fieldFunctionObjects); region solid_wall;\n"
            f"        regionType patch; name solid_wall_to_domain{k}; operation areaAverage; fields (T);\n"
            f"        writeControl timeStep; writeInterval 200; log true; writeFields false; }}\n")
        for nm,patch,op,fld in [("p_in","inlet","areaAverage","p_rgh"),("p_out","outlet","areaAverage","p_rgh"),
                                 ("mdot","inlet","sum","phi")]:
            s+=(f"    {nm}_d{k} {{ type surfaceFieldValue; libs (fieldFunctionObjects); region domain{k};\n"
                f"        regionType patch; name {patch}; operation {op}; fields ({fld});\n"
                f"        writeControl timeStep; writeInterval 200; log true; writeFields false; }}\n")
        s+=(f"    T_out_d{k} {{ type surfaceFieldValue; libs (fieldFunctionObjects); region domain{k};\n"
            f"        regionType patch; name outlet; operation weightedAverage; weightField phi; fields (T);\n"
            f"        writeControl timeStep; writeInterval 200; log true; writeFields false; }}\n")
    return s+"}\n"

def write_fields(d,N):
    def coupled(nbr,method,T0):
        return (f"    {nbr}\n    {{\n        type compressible::turbulentTemperatureCoupledBaffleMixed;\n"
                f"        Tnbr T; kappaMethod {method}; value uniform {T0};\n    }}\n")
    s=H("volScalarField","T","0/solid_wall")
    s+="dimensions [0 0 0 1 0 0 0];\ninternalField uniform 0.025;\nboundaryField\n{\n"
    s+=(f"    chipFace {{ type fixedGradient; gradient uniform {GRAD:.6e}; }}\n"
        "    hotPlate { type zeroGradient; }\n    outerY0 { type zeroGradient; }\n"
        "    outerY3 { type zeroGradient; }\n    inlet { type zeroGradient; }\n    outlet { type zeroGradient; }\n")
    for k in range(1,N+1): s+=coupled(f"solid_wall_to_domain{k}","solidThermo",0.020)
    open(f"{d}/0/solid_wall/T","w").write(s+"}\n")
    sp=H("volScalarField","p","0/solid_wall")+"dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\nboundaryField\n{\n"
    for p in ["chipFace","hotPlate","outerY0","outerY3","inlet","outlet"]+[f"solid_wall_to_domain{k}" for k in range(1,N+1)]:
        sp+=f"    {p} {{ type zeroGradient; }}\n"
    open(f"{d}/0/solid_wall/p","w").write(sp+"}\n")
    for k in range(1,N+1):
        P=f"domain{k}_to_solid_wall"; dk=f"{d}/0/domain{k}"
        t=H("volScalarField","T",f"0/domain{k}")+"dimensions [0 0 0 1 0 0 0];\ninternalField uniform 0.010;\nboundaryField\n{\n"
        t+=("    inlet { type fixedValue; value uniform 0.010; }\n"
            "    outlet { type inletOutlet; inletValue uniform 0.010; value uniform 0.010; }\n")
        open(f"{dk}/T","w").write(t+coupled(P,"fluidThermo",0.012)+"}\n")
        u=H("volVectorField","U",f"0/domain{k}")+"dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0.001 0 0);\nboundaryField\n{\n"
        u+=("    inlet { type fixedValue; value uniform (0.001 0 0); }\n    outlet { type zeroGradient; }\n"
            f"    {P} {{ type noSlip; }}\n}}\n")
        open(f"{dk}/U","w").write(u)
        for fld in ("p","p_rgh"):
            pp=H("volScalarField",fld,f"0/domain{k}")+"dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\nboundaryField\n{\n"
            pp+=("    inlet { type zeroGradient; }\n    outlet { type fixedValue; value uniform 0; }\n"
                 f"    {P} {{ type fixedFluxPressure; value uniform 0; }}\n}}\n")
            open(f"{dk}/{fld}","w").write(pp)
        a=H("volScalarField","alphat",f"0/domain{k}")+"dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\nboundaryField\n{\n"
        a+=("    inlet { type calculated; value uniform 0; }\n    outlet { type calculated; value uniform 0; }\n"
            f"    {P} {{ type compressible::alphatWallFunction; value uniform 0; }}\n}}\n")
        open(f"{dk}/alphat","w").write(a)

def write_constant(d,N):
    shutil.copy(f"{SRC}/constant/g", f"{d}/constant/g")
    open(f"{d}/constant/regionProperties","w").write(
        H("dictionary","regionProperties","constant")+
        "regions ( fluid ( "+" ".join(f"domain{k}" for k in range(1,N+1))+" ) solid ( solid_wall ) );\n")
    os.makedirs(f"{d}/constant/solid_wall",exist_ok=True)
    open(f"{d}/constant/solid_wall/thermophysicalProperties","w").write(
        H("dictionary","thermophysicalProperties","constant/solid_wall")+
"""// Cu solid — HYBRID: constant kappa (near-isothermal solid; Kapitza applied analytically)
thermoType
{ type heSolidThermo; mixture pureMixture; transport constIso; thermo hConst;
  equationOfState rhoConst; specie specie; energy sensibleEnthalpy; }
mixture
{
    specie { molWeight 63.546; }
    equationOfState { rho 8960.0; }
    thermodynamics { Cp 0.40; Hf 0; }
    transport { kappa """+f"{KS:.4f}"+"""; }
}
""")
    ft=(H("dictionary","thermophysicalProperties","constant/fluid")+
"""// He-4 effective medium — mu=1e-6 (settled), Pr=5e-3 (kappa_eff=0.001 W/mK)
thermoType
{ type heRhoThermo; mixture pureMixture; transport const; thermo hConst;
  equationOfState rhoConst; specie specie; energy sensibleEnthalpy; }
mixture
{
    specie { molWeight 4.003; }
    equationOfState { rho 145.0; }
    thermodynamics { Cp 5.0; Hf 0; }
    transport { mu 1e-6; Pr 5.000e-03; }
}
""")
    for k in range(1,N+1):
        dk=f"{d}/constant/domain{k}"; os.makedirs(dk,exist_ok=True)
        open(f"{dk}/thermophysicalProperties","w").write(ft)
        shutil.copy(f"{SRC}/constant/domain1/turbulenceProperties", f"{dk}/turbulenceProperties")

def write_system(d,N):
    for f in ("fvSchemes","fvSolution"):
        shutil.copy(f"{SRC}/system/{f}", f"{d}/system/{f}")
    shutil.copytree(f"{SRC}/system/solid_wall", f"{d}/system/solid_wall")
    PCG=("p_rgh\n    {\n        solver PCG; preconditioner DIC;\n"
         "        tolerance 1e-8; relTol 0.01; maxIter 1500;\n    }")
    for k in range(1,N+1):
        dk=f"{d}/system/domain{k}"; shutil.copytree(f"{SRC}/system/domain1", dk)
        t=open(f"{dk}/fvSolution").read()
        open(f"{dk}/fvSolution","w").write(re.sub(r'p_rgh\s*\{[^}]*\}', PCG, t, count=1))
    cd=open(f"{SRC}/system/controlDict").read()
    cd=cd[:cd.index("functions")]+write_functions(N)
    cd=re.sub(r'purgeWrite\s+\d+;','purgeWrite 2;',cd)
    if 'purgeWrite' not in cd: cd=cd.replace("functions","purgeWrite 2;\n\nfunctions",1)
    open(f"{d}/system/controlDict","w").write(cd)

def run_case(N):
    d=f"{OUT}/N{N}"; shutil.rmtree(d,ignore_errors=True)
    for sub in ("system","constant","0"): os.makedirs(f"{d}/{sub}",exist_ok=True)
    build_blockmesh(d,N); write_system(d,N); write_constant(d,N)
    r=sh("blockMesh > log.blockMesh 2>&1 && echo OK",d)
    if "OK" not in r.stdout: print(f"N{N}: blockMesh FAILED",flush=True); print(sh("tail -5 log.blockMesh",d).stdout); return
    nc=int(re.search(r'nCells:(\d+)',open(f"{d}/constant/polyMesh/owner").read()).group(1))
    r=sh("checkMesh 2>&1 | grep -E 'Mesh OK|non-orthogonality|Failed' | head -3",d)
    print(f"N{N}: meshed {nc} cells | {r.stdout.strip()}",flush=True)
    sh("splitMeshRegions -cellZonesOnly -overwrite > log.split 2>&1",d)
    write_fields(d,N)
    sh("foamDictionary system/controlDict -entry startFrom -set startTime >/dev/null; "
       "foamDictionary system/controlDict -entry endTime -set 6000 >/dev/null; "
       "chtMultiRegionSimpleFoam > log.hybrid 2>&1",d)
    def gg(nm):
        fs=sorted(glob.glob(f"{d}/postProcessing/*/{nm}/*/*.dat"),key=lambda x:int(x.split('/')[-2]))
        if not fs: return float('nan')
        return float([l for l in open(fs[-1]) if l.strip() and not l.startswith('#')][-1].split()[1])
    try:
        QC=gg("Q_chipFace")
        out=[f"NCELLS {nc}",f"QCHIP {QC}"]
        print(f"N{N}: Q_chip={QC*1e9:.3f} nW",flush=True)
        for k in range(1,N+1):
            dP=gg(f"p_in_d{k}")-gg(f"p_out_d{k}"); Ti=gg(f"T_int_s_d{k}"); To=gg(f"T_out_d{k}"); md=abs(gg(f"mdot_d{k}"))
            out+=[f"CH{k} DP {dP:.6e} TINT {Ti:.8e} TOUT {To:.8e} MDOT {md:.4e}"]
            print(f"  ch{k}: dP={dP*1e3:.5f} mPa  T_int={Ti*1e3:.5f} mK  T_out={To*1e3:.4f} mK",flush=True)
        open(f"{d}/metrics.txt","w").write("\n".join(out)+"\n")
    except Exception as e:
        print(f"N{N}: extract FAIL {e}",flush=True)

os.makedirs(OUT,exist_ok=True)
print("=== DOMAIN (CHANNEL-COUNT) INDEPENDENCE — Cu_1p0 hybrid, N=5/7/9 ===",flush=True)
for N in (5,7,9): run_case(N)
print("=== DONE ===",flush=True)
