import numpy as np, json, wave
SR=48000; T=31.0; N=int(SR*T); rng=np.random.default_rng(7)
t=np.arange(N)/SR
def lp(x,a):  # one-pole lowpass, a in (0,1)
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def lpf(x,fc): # fft lowpass
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=1/(1+(f/fc)**4); return np.fft.irfft(X,len(x))
def hpf(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=1/(1+(fc/np.maximum(f,1))**4); return np.fft.irfft(X,len(x))
def bpf(x,lo,hi): return hpf(lpf(x,hi),lo)
mus=np.zeros((N,2)); sfx=np.zeros((N,2))
def add(buf,sig,at,gain=1.0,pan=0.0):
    i=int(at*SR); n=min(len(sig),N-i)
    if n<=0:return
    buf[i:i+n,0]+=sig[:n]*gain*(1-pan)/1; buf[i:i+n,1]+=sig[:n]*gain*(1+pan)/1
# ---- music: D minor, 96bpm
bpm=96; beat=60/bpm; bar=4*beat
def n2f(n): return 440*2**((n-69)/12)
chords=[[50,57,62,65],[46,53,58,62],[53,57,60,65],[48,55,60,64]]  # Dm Bb F C
pad=np.zeros(N)
for ci in range(int(T/(2*bar))+1):
    ch=chords[ci%4]; a=ci*2*bar; L=int(2*bar*SR)+SR
    tt=np.arange(L)/SR; env=np.minimum(1,tt/0.8)*np.minimum(1,np.maximum(0,(2*bar+0.9-tt)/0.9))
    s=sum(np.sin(2*np.pi*n2f(n)*tt*d+rng.random()*6) for n in ch for d in (0.997,1.0,1.004))
    s+= 0.5*sum(np.sign(np.sin(2*np.pi*n2f(n)*tt))*0.3 for n in ch[:1])
    i=int(a*SR); m=min(L,N-i)
    if m>0: pad[i:i+m]+=(s*env)[:m]
pad=lpf(pad,1400)*0.05
sub=np.zeros(N)
def kick():
    tt=np.arange(int(0.45*SR))/SR; f=45+110*np.exp(-tt*28); ph=2*np.cumsum(np.pi*f)/SR
    return np.sin(ph)*np.exp(-tt*7)
def hat():
    tt=np.arange(int(0.06*SR))/SR; return hpf(rng.standard_normal(len(tt)),7000)*np.exp(-tt*70)
def snare():
    tt=np.arange(int(0.25*SR))/SR; return (bpf(rng.standard_normal(len(tt)),1200,6000)*0.7+np.sin(2*np.pi*190*tt)*0.5)*np.exp(-tt*18)
K,Hh,Sn=kick(),hat(),snare()
nb=int(T/beat)+1
for b in range(nb):
    tb=b*beat
    if tb>29.4: break
    inten=0.55 if tb<4.96 else 1.0
    if b%4 in(0,2) or (tb>13 and b%8==7): add(mus,K,tb,0.42*inten)
    if tb>=4.96 and b%4 in (1,3): add(mus,Sn,tb,0.10)
    if tb>=4.96:
        add(mus,Hh,tb+beat/2,0.05,0.3); 
        if tb>13: add(mus,Hh,tb,0.03,-0.3)
# bass pulse on 8ths
for b in range(int(29.4/(beat/2))):
    tb=b*beat/2; ci=int(tb/(2*bar))%4; f=n2f(chords[ci][0]-12)
    tt=np.arange(int(beat/2*SR))/SR; s=np.tanh(2*np.sin(2*np.pi*f*tt))*np.exp(-tt*6)
    add(mus,lpf(s,500) if False else s,tb,0.06 if tb>4.96 else 0.03)
mus[:,0]+=pad; mus[:,1]+=np.roll(pad,240)
# riser into finale + impact
rs,re=26.9,29.55; L=int((re-rs)*SR); tt=np.arange(L)/SR
riser=hpf(rng.standard_normal(L),800)*(tt/(re-rs))**2*0.18+np.sin(2*np.pi*np.cumsum(200+900*(tt/(re-rs))**2)/SR)*(tt/(re-rs))**2*0.05
add(mus,riser,rs)
tt=np.arange(int(2.5*SR))/SR
boom=(np.sin(2*np.pi*np.cumsum(40+80*np.exp(-tt*8))/SR)*np.exp(-tt*1.6)*0.9+lpf(rng.standard_normal(len(tt)),2500)*np.exp(-tt*5)*0.4)
add(sfx,boom,29.55,0.55)
# stamp thunk
add(sfx,kick()*1.2,29.6,0.5)
# ---- typewriter clicks
meta=json.load(open('meta.json')); last=-1
def click(seed):
    r=np.random.default_rng(seed); L=int(0.07*SR); tt=np.arange(L)/SR
    c=bpf(r.standard_normal(L),1800,9000)*np.exp(-tt*160)
    c+=np.sin(2*np.pi*(150+r.random()*60)*tt)*np.exp(-tt*60)*0.6
    c[int(0.012*SR):]+=bpf(r.standard_normal(L-int(0.012*SR)),2500,8000)*np.exp(-tt[:L-int(0.012*SR)]*220)*0.5
    return c
for i,k in enumerate(meta['keys']):
    if k-last<0.055: continue
    last=k; add(sfx,click(i),k,0.065*(0.75+0.5*rng.random()),(rng.random()-.5)*0.5)
# carriage return zip at each new line (except first) + soft bell at line end
def zipr():
    L=int(0.22*SR);tt=np.arange(L)/SR; z=bpf(rng.standard_normal(L),1500,6000)*(np.sin(np.pi*tt/0.22))*(1+0.6*np.sign(np.sin(2*np.pi*55*tt)))
    return z
def bell():
    tt=np.arange(int(1.2*SR))/SR; return (np.sin(2*np.pi*2350*tt)+0.4*np.sin(2*np.pi*4720*tt))*np.exp(-tt*4.5)
starts=[0,2.56,4.96,6.72,9.44,13.22,17.08,19.44,22.66,25.06,27.9]
for s in starts[1:]: add(sfx,zipr(),s-0.05,0.035)
for d in [2.5,16.7,30.6]: add(sfx,bell(),d+0.05,0.025)
# whooshes at cuts
def whoosh(d=0.5):
    L=int(d*SR);tt=np.arange(L)/SR;env=np.sin(np.pi*tt/d)**2
    n=rng.standard_normal(L);return bpf(n,300,3000)*env
for c in [4.96,9.44,13.22,19.44,25.06,27.9]: add(sfx,whoosh(),c-0.3,0.09,(rng.random()-.5))
def wr(name,x):
    x=np.clip(x,-1,1);w=wave.open(name,'wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype('<i2').tobytes());w.close()
print('mus peak',np.abs(mus).max(),'sfx peak',np.abs(sfx).max())
wr('music.wav',mus/np.abs(mus).max()*0.7); wr('sfx.wav',sfx/max(1,np.abs(sfx).max()))
