# Original background score + typewriter SFX, synthesised in code (no third-party audio).
import numpy as np, json, wave, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SR=48000; DUR=26.2; N=int(SR*DUR); rng=np.random.default_rng(7)
t=np.arange(N)/SR
def mtof(m): return 440*2**((m-69)/12)
def env_ad(n,a,d):
    e=np.ones(n); na=max(1,int(a*SR)); e[:na]=np.linspace(0,1,na)
    e[na:]=np.exp(-np.arange(n-na)/(d*SR)); return e
def add(buf,sig,at,gain=1.0,pan=0.0):
    i=int(at*SR);
    if i>=len(buf): return
    sig=sig[:len(buf)-i]; l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    buf[i:i+len(sig),0]+=sig*gain*l*1.41; buf[i:i+len(sig),1]+=sig*gain*r*1.41
def lowpass(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def lp_fft(x,fc,order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X/= (1+(f/fc)**(2*order))**0.5
    return np.fft.irfft(X,len(x))
def hp_fft(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*= 1/(1+(fc/np.maximum(f,1))**4)**0.5
    return np.fft.irfft(X,len(x))

def piano(m,dur=2.4,vel=1.0):
    n=int(dur*SR); tt=np.arange(n)/SR; f=mtof(m); s=np.zeros(n)
    for h,amp in [(1,1),(2,0.42),(3,0.18),(4,0.09),(5,0.04)]:
        s+=amp*np.sin(2*np.pi*f*h*tt*(1+0.0004*h*h))*np.exp(-tt*(0.9+0.9*h))
    s*=env_ad(n,0.004,10); s+=0.02*rng.standard_normal(n)*np.exp(-tt*80)  # hammer
    return s*vel*0.22
def pad(ms,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        for d in (-0.08,0.0,0.08):
            ph=rng.random()*6.28; f=mtof(m)*2**(d/12)
            s+=np.sin(2*np.pi*f*tt+ph)+0.25*np.sin(4*np.pi*f*tt+ph)
    a=int(0.9*SR); r=int(0.9*SR); e=np.ones(n); e[:a]=np.linspace(0,1,a)**2; e[-r:]*=np.linspace(1,0,r)
    return lp_fft(s*e,1400)*0.022

mus=np.zeros((N,2))
BEAT=60/78; BAR=4*BEAT
prog=[(48,[55,60,64]),(55,[55,59,62]),(57,[57,60,64]),(53,[53,57,60])]  # C G Am F (warm, hopeful)
arp=[0,2,1,2, 0,2,1,2]
bar=0; tb=0.0
while tb<DUR:
    root,ch=prog[bar%4]
    add(mus,pad([n-12 for n in ch]+[ch[0]],BAR+0.9),tb,1.0)
    add(mus,np.sin(2*np.pi*mtof(root-24)*np.arange(int(BAR*SR))/SR)*env_ad(int(BAR*SR),0.02,2.5)*0.09,tb)
    for k,ix in enumerate(arp):
        note=ch[ix]+(12 if k in (2,6) else 0)
        add(mus,piano(note+12,2.2,0.75 if k%2 else 1.0),tb+k*BEAT/2,1.0,pan=(-0.3 if k%2 else 0.3))
    # melody fragment on bars 2..
    if bar>=1:
        mel={1:[(0,72),(1.5,69),(3,67)],2:[(0,67),(1,69),(2,72),(3,74)],3:[(0,74),(1.5,71)],
             4:[(0,76),(1.5,74),(2.5,72)],5:[(0,69),(2,72)],6:[(0,72),(1,71),(2,67)],7:[(0,69)]}
        for b,m in mel.get(bar,[]): add(mus,piano(m+12,3.0,0.9),tb+b*BEAT,0.8)
    # soft beat from bar 1
    if bar>=1 and tb<24.9:
        for b in range(4):
            kt=tb+b*BEAT
            if b in (0,2):
                n=int(0.35*SR); tt=np.arange(n)/SR
                kick=np.sin(2*np.pi*(48+70*np.exp(-tt*28))*tt)*np.exp(-tt*9); add(mus,kick*0.28,kt)
            if b in (1,3):
                n=int(0.18*SR); sn=hp_fft(rng.standard_normal(n),1800)*np.exp(-np.arange(n)/SR*28)
                add(mus,sn*0.035,kt)
            for h in (0.5,):
                n=int(0.06*SR); hh=hp_fft(rng.standard_normal(n),7000)*np.exp(-np.arange(n)/SR*90)
                add(mus,hh*0.02,kt+h*BEAT,pan=0.4)
    bar+=1; tb+=BAR
# vinyl crackle bed
cr=np.zeros(N); idx=rng.integers(0,N,900); cr[idx]=rng.standard_normal(900)*0.25
cr=hp_fft(cr,1500)+lp_fft(rng.standard_normal(N),900)*0.004
mus[:,0]+=cr*0.5; mus[:,1]+=np.roll(cr,311)*0.5
# simple reverb on music
ir_n=int(2.2*SR); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.6); ir=lp_fft(ir,3500); ir/=np.abs(ir).sum()**0.5*30
for c in range(2):
    wet=np.fft.irfft(np.fft.rfft(mus[:,c],N+ir_n)*np.fft.rfft(np.roll(ir,c*97),N+ir_n),N+ir_n)[:N]
    mus[:,c]=mus[:,c]*0.8+wet*0.9
# fade in/out
fi=int(0.4*SR); mus[:fi]*=np.linspace(0,1,fi)[:,None]; fo=int(1.0*SR); mus[-fo:]*=np.linspace(1,0,fo)[:,None]

# ---------- SFX ----------
sfx=np.zeros((N,2)); ev=json.load(open('events.json'))
def key():
    n=int(0.07*SR); tt=np.arange(n)/SR
    clk=hp_fft(rng.standard_normal(n),2500)*np.exp(-tt*420)
    thunk=np.sin(2*np.pi*(170+rng.random()*60)*tt)*np.exp(-tt*70)*0.6
    return (clk*1.2+thunk)*(0.75+0.5*rng.random())
def ding():
    n=int(1.6*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for f,a,d in [(2093,1,1.6),(4186*1.01,0.35,3.5),(2637,0.25,2.2),(6280,0.1,8)]: s+=a*np.sin(2*np.pi*f*tt)*np.exp(-tt*d)
    return s*0.22
def whoosh(d=0.45):
    n=int(d*SR); x=rng.standard_normal(n); e=np.sin(np.linspace(0,np.pi,n))**2
    return lp_fft(x*e,1800)*0.5
def boom():
    n=int(1.4*SR); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*(42+40*np.exp(-tt*6))*tt)*np.exp(-tt*3.2)+lp_fft(rng.standard_normal(n),300)*np.exp(-tt*8)*0.6)*0.55
for e in ev:
    if e['t']<0: e['t']=0
    if e['k']=='key': add(sfx,key(),e['t'],0.30,pan=(rng.random()-0.5)*0.4)
    elif e['k']=='ding': add(sfx,ding(),e['t'],1.0,pan=0.2)
for c in [2.16,4.62,6.74,9.14,11.38,12.78,14.26,17.05,22.60]: add(sfx,whoosh(),c-0.25,0.20)
for c in [10.32,16.58,20.20]: add(sfx,boom(),c,0.8)
add(sfx,boom(),24.86,0.5)

def save(name,x):
    x=x/ max(1e-9,np.abs(x).max())*0.89
    with wave.open(name,'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype('<i2').tobytes())
save('music.wav',mus); save('sfx.wav',sfx); print('ok')
