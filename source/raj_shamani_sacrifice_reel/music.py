import numpy as np, wave, unicodedata, importlib.util
SR=48000; D=16.90; n=int(SR*D); t=np.arange(n)/SR
rng=np.random.default_rng(3)
def note(f): return 440*2**((f-69)/12)
mus=np.zeros((n,2))
# chord pad: Am - F - C - G, 2 bars each @ 90bpm (bar=2.667s)
bar=60/90*4; chords=[[57,60,64,69],[53,57,60,65],[48,55,60,64],[55,59,62,67]]
for k in range(int(D/bar)+1):
    c=chords[k%4]; s=int(k*bar*SR); e=min(n,int((k+1)*bar*SR)+SR//2)
    if s>=n: break
    tt=np.arange(e-s)/SR; env=np.minimum(1,tt/0.8)*np.exp(-np.maximum(0,tt-bar)*4)
    for i,m in enumerate(c):
        for det,pan in ((-0.08,0.3),(0.08,0.7)):
            w=np.sin(2*np.pi*note(m+det)*tt+ i)*0.5+0.18*np.sin(2*np.pi*2*note(m+det)*tt)
            mus[s:e,0]+=w*env*(1-pan)*0.05; mus[s:e,1]+=w*env*pan*0.05
    # bass
    tt2=np.arange(e-s)/SR; mus[s:e]+= (np.sin(2*np.pi*note(c[0]-12)*tt2)*np.minimum(1,tt2/0.05)*np.exp(-np.maximum(0,tt2-bar)*4)*0.12)[:,None]
# soft beat: kick on 1,3; hat on 8ths
beat=60/90
for b in np.arange(0,D,beat):
    s=int(b*SR); L=min(int(0.35*SR),n-s); tt=np.arange(L)/SR
    if round(b/beat)%2==0:
        k=np.sin(2*np.pi*(50+90*np.exp(-tt*30))*tt)*np.exp(-tt*9)*0.32; mus[s:s+L]+=k[:,None]
    for h in (0,beat/2):
        s2=int((b+h)*SR); L2=min(int(0.05*SR),n-s2)
        if L2>0: mus[s2:s2+L2]+=(np.diff(rng.normal(0,1,L2+1))*np.exp(-np.arange(L2)/SR*80)*0.025)[:,None]
# riser + impact on stat moments
spec=importlib.util.spec_from_file_location("r","render.py")
# fade in/out
fade=np.minimum(1,t/1.5)*np.minimum(1,(D-t)/1.5); mus*=fade[:,None]
# typing clicks
import json
src=open("render.py").read(); S=eval(src[src.index("S=["):src.index("]\nHL=")+1][2:].replace("DUR","16.90"))
clk=np.zeros(n)
for s,e,words,st in S:
    for w,ws,we in words:
        cl=[c for c in w if not unicodedata.category(c).startswith("M") and c!="्"]
        for j in range(len(cl)):
            p=int((ws+(we-ws)*j/max(len(cl),1))*SR); L=min(int(0.03*SR),n-p)
            if L<=0: continue
            x=rng.normal(0,1,L)*np.exp(-np.arange(L)/SR*260); x=np.diff(np.r_[0,x])
            clk[p:p+L]+=x*0.10*rng.uniform(.6,1)
    if st:  # whoosh impact at stat
        p=int(st[2]*SR); L=min(int(0.5*SR),n-p); tt=np.arange(L)/SR
        mus[p:p+L]+=(np.sin(2*np.pi*(60*np.exp(-tt*6)+40)*tt)*np.exp(-tt*7)*0.35)[:,None]
    p=int(s*SR); L=min(int(0.4*SR),n-p)
    if s>0:
        x=np.cumsum(rng.normal(0,1,L)); x-=np.linspace(x[0],x[-1],L); x/=np.abs(x).max()+1e-9
        env=np.sin(np.pi*np.arange(L)/L); mus[p:p+L]+=(x*env*0.06)[:,None]
mus[:,0]+=clk; mus[:,1]+=clk
mus/=np.abs(mus).max(); mus*=0.9
with wave.open("music.wav","wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mus*32767).astype(np.int16).tobytes())
