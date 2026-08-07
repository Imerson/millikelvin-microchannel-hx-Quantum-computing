import subprocess, os, glob, re, shutil
OF="source /usr/lib/openfoam/openfoam2412/etc/bashrc 2>/dev/null"
BASE="/home/ubuntu/cases"; SRC=f"{BASE}/S4_MC_Cu_0p5_hyb"; OUT=f"{BASE}/S4_Mesh_Independence"
LEVELS=[("coarse",0.7),("medium",1.0),("fine",1.2)]   # PCG-tractable; medium=production mesh
KAPPA=13.08; QPP=6.675e-5
def sh(cmd,cwd): return subprocess.run(f'bash -c "{OF}; cd {cwd}; {cmd}"',shell=True,capture_output=True,text=True)
def scale_bmd(txt,f):
    def repl(m):
        nums=[max(1,round(int(n)*f)) for n in m.group(2).split()]
        return m.group(1)+f"({nums[0]} {nums[1]} {nums[2]})"
    return re.sub(r'(\)\s+(?:solid_wall|domain\d)\s+)\(([\d ]+)\)', repl, txt)
PCG='''p_rgh
    {
        solver PCG; preconditioner DIC;
        tolerance 1e-8; relTol 0.01; maxIter 1500;
    }'''
os.makedirs(OUT, exist_ok=True)
print("=== MESH INDEPENDENCE v2 (PCG, maxIter 1500) ===",flush=True)
for name,f in LEVELS:
    d=f"{OUT}/{name}"; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    shutil.copytree(f"{SRC}/system", f"{d}/system"); os.makedirs(f"{d}/constant",exist_ok=True)
    open(f"{d}/system/blockMeshDict","w").write(scale_bmd(open(f"{SRC}/system/blockMeshDict").read(),f))
    for i in range(1,6):
        fp=f"{d}/system/domain{i}/fvSolution"; t=open(fp).read()
        t=re.sub(r'p_rgh\s*\{[^}]*\}', PCG, t, count=1); open(fp,'w').write(t)
    sh("blockMesh > log.blockMesh 2>&1", d)
    ncells=int(re.search(r'nCells:(\d+)', open(f"{d}/constant/polyMesh/owner").read()).group(1))
    sh("splitMeshRegions -cellZonesOnly -overwrite > log.split 2>&1", d)
    subprocess.run(f"python3 {BASE}/apply_hybrid.py S4_Mesh_Independence/{name} Cu {KAPPA} {QPP}",shell=True,capture_output=True)
    for i in range(1,6):
        fp=f"{d}/constant/domain{i}/thermophysicalProperties"
        if os.path.exists(fp):
            t=open(fp).read().replace('mu 1e-7','mu 1e-6').replace('Pr 5.000e-04','Pr 5.000e-03'); open(fp,'w').write(t)
    shutil.copy(f"{SRC}/constant/regionProperties", f"{d}/constant/regionProperties")
    shutil.copy(f"{SRC}/constant/g", f"{d}/constant/g")
    for i in range(1,6): shutil.copy(f"{SRC}/constant/domain{i}/turbulenceProperties", f"{d}/constant/domain{i}/turbulenceProperties")
    print(f"  {name}: meshed {ncells} cells, running...",flush=True)
    sh("foamDictionary system/controlDict -entry startFrom -set startTime >/dev/null; "
       "foamDictionary system/controlDict -entry endTime -set 6000 >/dev/null; "
       "chtMultiRegionSimpleFoam > log.hybrid 2>&1", d)
    def gg(nm):
        fs=sorted(glob.glob(f"{d}/postProcessing/*/{nm}/*/*.dat"),key=lambda x:int(x.split('/')[-2]))
        return float([l for l in open(fs[-1]) if l.strip() and not l.startswith('#')][-1].split()[1])
    try:
        QC=gg("Q_chipFace"); TS=gg("T_int_solid"); TO=gg("T_outlet_fluid"); MD=abs(gg("massFlowInlet"))
        dP=gg("p_inlet")-gg("p_outlet"); nC=re.search(r'domain1\s+\((\d+)', open(f"{d}/system/blockMeshDict").read()).group(1)
        open(f"{d}/metrics.txt","w").write(f"NCELLS {ncells}\nNC_DH {nC}\nT_INT_SOLID {TS}\nDP {dP}\nGATE1 {QC}\nTOUT {TO}\nMDOT {MD}\n")
        print(f"  {name}: N={ncells} nC={nC} Gate1={QC*1e9:.3f}nW T_int_solid={TS*1e3:.5f}mK dP={dP:.6e}Pa",flush=True)
    except Exception as e:
        print(f"  {name}: FAIL {e}",flush=True)
print("=== DONE ===",flush=True)
