#!/usr/bin/env python3
# 1 uW load-envelope: TWO-SEED BRACKET. Each of the 6 factorial cases at Q_sys = 1 uW
# (chipFace gradient x 1/15, everything else byte-identical), from two solid initial guesses
# (10.5 and 12.5 mK). If T_int stays at each seed the conjugate level is undetermined at
# this load -> the closure's energy-balance T_int is the consistent estimate.
import subprocess, os, glob, re, shutil
OF="source /usr/lib/openfoam/openfoam2412/etc/bashrc 2>/dev/null"
BASE="/home/ubuntu/cases"; SCALE=1.0/15.0; END=2000
SRC=[("S4_MC_Cu_0p5_hyb","Cu_0p5"),("S4_MC_Cu_1p0","Cu_1p0"),("S4_MC_Cu_2p0","Cu_2p0"),
     ("S4_MC_Ag_0p5","Ag_0p5"),("S4_MC_Ag_1p0","Ag_1p0"),("S4_MC_Ag_2p0","Ag_2p0")]
SEEDS=[("s10p5",0.0105),("s12p5",0.0125)]
def sh(cmd,cwd): return subprocess.run(f'bash -c "{OF}; cd {cwd}; {cmd}"',shell=True,capture_output=True,text=True)
def gg(d,nm):
    fs=sorted(glob.glob(f"{d}/postProcessing/*/{nm}/*/*.dat"),key=lambda x:int(x.split('/')[-2]))
    rows=[l.split() for l in open(fs[-1]) if l.strip() and not l.startswith('#')]
    return rows
print(f"=== 1 uW TWO-SEED BRACKET (gradient x 1/15, seeds 10.5 / 12.5 mK, 0->{END}) ===",flush=True)
os.makedirs(f"{BASE}/S4_1uW",exist_ok=True)
for src,lab in SRC:
    for sname,seed in SEEDS:
        d=f"{BASE}/S4_1uW/{lab}_{sname}"; s=f"{BASE}/{src}"
        shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
        for sub in ("constant","system","0"): shutil.copytree(f"{s}/{sub}",f"{d}/{sub}")
        fp=f"{d}/0/solid_wall/T"; t=open(fp).read()
        m=re.search(r"gradient\s+uniform\s+([-0-9.eE+]+)",t); g0=float(m.group(1)); g1=g0*SCALE
        t=t.replace(m.group(0),f"gradient uniform {g1:.6e}")
        t=re.sub(r"internalField\s+uniform\s+[0-9.eE+-]+",f"internalField uniform {seed}",t)
        open(fp,"w").write(t)
        sh("foamDictionary system/controlDict -entry startFrom -set startTime >/dev/null; "
           "foamDictionary system/controlDict -entry startTime -set 0 >/dev/null; "
           f"foamDictionary system/controlDict -entry endTime -set {END} >/dev/null; "
           "foamDictionary system/controlDict -entry purgeWrite -set 1 >/dev/null; "
           "rm -rf postProcessing; chtMultiRegionSimpleFoam > log.hybrid 2>&1", d)
        try:
            ti=gg(d,"T_int_solid"); QC=float(gg(d,"Q_chipFace")[-1][1]); TO=float(gg(d,"T_outlet_fluid")[-1][1])
            pin=float(gg(d,"p_inlet")[-1][1]); pout=float(gg(d,"p_outlet")[-1][1])
            T_last=float(ti[-1][1]); T_first=float(ti[0][1]); drift=(float(ti[-1][1])-float(ti[-2][1]))*1e3
            line=(f"{lab} seed={seed*1e3:.1f}mK  Q_chip={QC*1e9:.4f}nW  T_int(t={ti[0][0]})={T_first*1e3:.5f}  "
                  f"T_int(t={ti[-1][0]})={T_last*1e3:.5f}mK  moved={(T_last-seed)*1e3:+.5f}mK  "
                  f"drift/200it={drift:+.2e}mK  T_out={TO*1e3:.4f}mK  dP={pin-pout:.4e}Pa")
            open(f"{d}/metrics.txt","w").write(f"SEED_MK {seed*1e3}\nQCHIP {QC}\nTINT_FIRST {T_first}\nTINT_LAST {T_last}\nDRIFT_MK {drift}\nTOUT {TO}\nDP {pin-pout}\n")
            print(line,flush=True)
        except Exception as e:
            print(f"{lab} {sname}: FAIL {e}",flush=True); print(sh("grep -iE 'FATAL|error' log.hybrid|tail -2",d).stdout)
print("=== DONE ===",flush=True)
