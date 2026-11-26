import numpy as np, json, subprocess
SR=48000; T=21.6; N=int(SR*T); rng=np.random.default_rng(3)
t=np.arange(N)/SR
def nf(m): return 440*2**((m-69)/12)
def env(n,a,d): x=np.arange(n)/SR; return np.minimum(x/a,1)*np.exp(-x/d)
def lp(x,a): # one-pole
    from scipy.signal import lfilter; return lfilter([1-a],[1,-a],x)
from scipy.signal import lfilter, butter, sosfilt, fftconvolve
mus=np.zeros((N,2))
def add(sig,start,pan=0.0,buf=mus):
    i=int(start*SR)
    if i<0: sig=sig[-i:]; i=0
    n=min(len(sig),N-i)
    if n<=0: return
    buf[i:i+n,0]+=sig[:n]*(1-pan)*0.5*2**.5; buf[i:i+n,1]+=sig[:n]*(1+pan)*0.5*2**.5
def piano(m,dur=2.5,v=0.25):
    n=int(dur*SR); x=np.arange(n)/SR; f=nf(m); s=np.zeros(n)
    for h,a in [(1,1),(2,.45),(3,.18),(4,.08),(5,.04)]:
        s+=a*np.sin(2*np.pi*f*h*x*(1+0.0004*h))*np.exp(-x*(1.2+h*0.9))
    return v*s*np.minimum(x/0.004,1)
def pad(ms,dur,v=0.05):
    n=int(dur*SR); x=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        for d in (-0.08,0,0.08):
            f=nf(m+d/1); s+=np.sin(2*np.pi*f*x+rng.random()*6)+0.3*np.sin(4*np.pi*f*x)
    e=np.minimum(x/0.8,1)*np.minimum((dur-x)/0.8,1)
    return v*s*e/len(ms)
BAR=3.0
chords=[[48,55,64,67],[43,55,59,62],[45,57,60,64],[41,53,57,60]]  # C G Am F
for b in range(8):
    st=b*BAR; c=chords[b%4]
    add(pad([m+12 for m in c[1:]],BAR+0.9,0.045),st-0.3)
    add(0.16*np.sin(2*np.pi*nf(c[0]-12)*np.arange(int(2.9*SR))/SR)*env(int(2.9*SR),0.01,1.6),st)
    arp=[c[0]+12,c[1]+12,c[2]+12,c[3]+12,c[2]+24,c[3]+12,c[2]+12,c[1]+12]
    for k,m in enumerate(arp):
        add(piano(m,2.2,0.16 if k%2 else 0.21),st+k*0.375,pan=(-0.3 if k%2 else 0.3))
    if b in (1,3,5,6): add(piano(c[3]+24,3,0.09),st+0.75,pan=0.1)
# soft heartbeat kick on beats 1&3 from bar 3
for b in range(3,7):
    for k in (0,1.5):
        n=int(0.4*SR); x=np.arange(n)/SR
        add(0.35*np.sin(2*np.pi*(50+70*np.exp(-x*30))*x)*np.exp(-x*9),b*BAR+k)
# reverb
ir=rng.standard_normal((int(2.2*SR),2))*np.exp(-np.arange(int(2.2*SR))/SR*3.2)[:,None]*0.02
mus=mus+np.stack([fftconvolve(mus[:,i],ir[:,i])[:N] for i in range(2)],1)*0.9
mus=sosfilt(butter(2,7000,'lp',fs=SR,output='sos'),mus,axis=0)
# --- voice ---
v=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','/root/.claude/uploads/bfcc3182-4a87-5583-abf1-415b6323d4f2/2b70a085-Samay_Raina_YT_04.mp3','-af','highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5:LRA=9','-ar','48000','-ac','2','-f','f32le','-'],capture_output=True).stdout,dtype=np.float32).reshape(-1,2)
voice=np.zeros((N,2)); voice[:min(len(v),N)]=v[:N]
ve=np.abs(voice).mean(1); ve=lfilter([1-0.9995],[1,-0.9995],ve); ve=ve/ve.max()
duck=1-0.55*np.clip(ve*4,0,1)
mus*=duck[:,None]
# fades for music
mus*=np.clip(t/1.0,0,1)[:,None]*np.clip((T-t)/1.6,0,1)[:,None]
mus=mus/np.abs(mus).max()*0.32
# --- fx ---
fx=np.zeros((N,2))
hp=butter(2,1800,'hp',fs=SR,output='sos')
for c in json.load(open('clicks.json')):
    n=int(0.03*SR); x=np.arange(n)/SR
    s=sosfilt(hp,rng.standard_normal(n))*np.exp(-x*260)*0.5+np.sin(2*np.pi*(180+rng.random()*60)*x)*np.exp(-x*120)*0.35
    add(s*(0.05+0.03*rng.random()),c,pan=rng.uniform(-.25,.25),buf=fx)
for c in [4.04,10.22,14.12]:
    n=int(0.8*SR); x=np.arange(n)/SR; w=rng.standard_normal(n)
    out=np.zeros(n)
    for k in range(0,n,1200):
        fc=300+5000*(k/n); sos=butter(2,[fc,fc*1.6],'bp',fs=SR,output='sos'); out[k:k+1200]=sosfilt(sos,w[k:k+1200])
    add(out*np.sin(np.pi*x/0.8)**2*0.5,c-0.55,buf=fx)
    n=int(1.2*SR); x=np.arange(n)/SR
    add(0.28*np.sin(2*np.pi*(45+40*np.exp(-x*20))*x)*np.exp(-x*3.5),c,buf=fx)
# typewriter bell at end of outro signature
n=int(2*SR); x=np.arange(n)/SR
bell=sum(a*np.sin(2*np.pi*f*x)*np.exp(-x*d) for f,a,d in [(2093,1,2.5),(4186*1.01,.4,5),(5250,.25,6)])
add(bell*0.07,19.45+1.18,buf=fx)
# outro clicks
for k in range(13): add(sosfilt(hp,rng.standard_normal(1400))*np.exp(-np.arange(1400)/SR*260)*0.04,19.8+k*0.8/13,buf=fx)
mix=voice*1.0+mus+fx
mix=np.tanh(mix*1.1)/np.tanh(1.1)
mix/=max(1,np.abs(mix).max()/0.97)
from scipy.io import wavfile; wavfile.write('mix.wav',SR,(mix*32767).astype(np.int16))
print('ok',np.abs(mix).max())
