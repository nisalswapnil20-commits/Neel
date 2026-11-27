import subprocess,sys,os,json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'.'); from edl import EDL
W,H,FPS=2160,3840,30
G={
 'warm':"eq=contrast=1.08:saturation=1.08:gamma=0.98,colorbalance=rs=0.04:gs=0.01:bs=-0.05:rh=0.03:bh=-0.04",
 'cool':"eq=contrast=1.12:saturation=0.95,colorbalance=rs=-0.03:bs=0.06:bm=0.03",
 'sad':"eq=contrast=1.05:saturation=0.55:brightness=-0.03,colorbalance=bs=0.06:bm=0.04:rh=-0.02",
 'night':"eq=contrast=1.1:saturation=0.8:brightness=-0.04,colorbalance=bs=0.08:bm=0.04",
 'gold':"eq=contrast=1.1:saturation=1.25,colorbalance=rs=0.06:bs=-0.08:rm=0.05:bm=-0.06",
 'silver':"hue=s=0,eq=contrast=1.15:brightness=-0.02,colorbalance=bs=0.05",
 'bronze':"hue=s=0,colorchannelmixer=rr=0.85:rg=0.25:gg=0.62:gr=0.12:bb=0.38:br=0.05,eq=contrast=1.15",
 'bw':"hue=s=0,eq=contrast=1.2",
 'red':"eq=contrast=1.15:saturation=0.85,colorbalance=rs=0.14:rm=0.08:bs=-0.04",
 'end':"gblur=sigma=30,eq=brightness=-0.22:saturation=0.6",
}
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
def job(k):
    s,e,clip,off,grade,fx=EDL[k]; fx=fx.split(',') if fx else []
    d=e-s; src=f'clips/{clip}.mp4'; avail=dur(src)-off-0.05
    sp=1.0
    if 'slow' in fx: sp=min(2.0,max(1.0,avail/d))
    if avail*1.0/sp < d: sp=avail/d  # must slow to fit (sp<1)
    if avail < d: sp=avail/d
    need=d*sp
    z0,z1=(1.0,1.0)
    if 'zi' in fx: z0,z1=1.0,1.07
    if 'zo' in fx: z0,z1=1.07,1.0
    vf=[f"setpts=(PTS-STARTPTS)/{sp:.5f}", f"fps={FPS}",
        f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}"]
    if z0!=z1:
        vf+= [f"scale=w='trunc({W}*({z0}+({z1}-{z0})*t/{d:.3f})/2)*2':h=-2:eval=frame:flags=bicubic", f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2"]
    vf.append(G[grade]); vf.append("vignette=angle=PI/5")
    if 'fw' in fx: vf.append("fade=t=in:st=0:d=0.22:color=white")
    if 'fb' in fx: vf.append("fade=t=in:st=0:d=0.5:color=black")
    vf.append("format=yuv420p")
    out=f'build/s{k:03d}.mp4'
    nf=round(e*FPS)-round(s*FPS)
    cmd=['ffmpeg','-v','error','-y','-ss',f'{off}','-t',f'{need+0.2:.3f}','-i',src,'-vf',','.join(vf),'-frames:v',str(nf),'-an',
         '-c:v','libx264','-preset','veryfast','-crf','14','-r',str(FPS),out]
    subprocess.run(cmd,check=True)
    return k,nf,sp
ids=[int(a) for a in sys.argv[1:]] or range(len(EDL))
with ThreadPoolExecutor(2) as ex:
    for r in ex.map(job,ids): print(*r,flush=True)
