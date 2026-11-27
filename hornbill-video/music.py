import numpy as np, wave, sys
SR=44100; DUR=float(sys.argv[2]); N=int(SR*DUR)
rng=np.random.default_rng(7)
def midi(m): return 440*2**((m-69)/12)
L=np.zeros(N); R=np.zeros(N)
bpm=68; beat=60/bpm; bar=4*beat
# Am - F - C - G  / Am - F - Dm - E
prog=[[57,60,64],[53,57,60],[48,52,55],[55,59,62],[57,60,64],[53,57,60],[50,53,57],[52,56,59]]
bass=[45,41,48,43,45,41,38,40]
t_bar=np.arange(int(bar*SR))/SR
def pad_note(f,n):
    t=np.arange(n)/SR
    s=sum(np.sin(2*np.pi*f*d*t+rng.random()*6) for d in (0.997,1.0,1.004))/3
    s+=0.25*np.sin(2*np.pi*2*f*t)
    env=np.minimum(1,t/1.2)*np.minimum(1,(n/SR-t)/1.2)
    return s*env
def piano(f,n):
    t=np.arange(n)/SR
    s=np.zeros(n)
    for k,a in enumerate([1,0.45,0.25,0.12,0.06],1):
        s+=a*np.sin(2*np.pi*f*k*t*(1+0.0004*k*k))*np.exp(-t*(1.6+0.9*k))
    att=np.minimum(1,t/0.004)
    return s*att
nb=int(DUR/bar)+2
for b in range(nb):
    st=int(b*bar*SR); ch=prog[b%8]
    n=int(bar*SR*1.25)
    for m in ch:
        x=pad_note(midi(m),n)*0.06
        e=min(N,st+n)-st
        if e<=0: continue
        L[st:st+e]+=x[:e]*(0.8 if m%2 else 1); R[st:st+e]+=x[:e]*(1 if m%2 else 0.8)
    x=pad_note(midi(bass[b%8]),n)*0.09; e=min(N,st+n)-st
    if e>0: L[st:st+e]+=x[:e]; R[st:st+e]+=x[:e]
    # piano arpeggio (enters after bar 2)
    if b>=2:
        notes=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+12,ch[0]+24,ch[2]+12,ch[1]+12,ch[2]+12]
        for i,m in enumerate(notes):
            if b%4==3 and i>=6: break
            p=st+int(i*beat/2*SR); n2=int(3*SR); e=min(N,p+n2)-p
            if e<=0: continue
            vel=0.10*(1 if i%4==0 else 0.7)*(0.9+0.2*rng.random())
            x=piano(midi(m),n2)*vel; pan=0.35+0.3*(i%3)/2
            L[p:p+e]+=x[:e]*(1-pan); R[p:p+e]+=x[:e]*pan
# simple reverb (feedback delays)
def rev(x):
    y=x.copy()
    for d,g in [(0.029,0.5),(0.037,0.45),(0.041,0.4),(0.053,0.35),(0.11,0.3),(0.17,0.25)]:
        k=int(d*SR); z=np.zeros_like(x)
        for r in range(1,8):
            if k*r<len(x): z[k*r:]+=x[:-k*r]*(g**r)
        y+=z*0.5
    return y
L=rev(L); R=rev(R)
# soft forest wind: lowpassed noise
nz=rng.standard_normal(N); 
from numpy.fft import rfft,irfft
F=rfft(nz); fr=np.fft.rfftfreq(N,1/SR); F*=1/(1+(fr/400)**2); w=irfft(F,N); w/=np.abs(w).max()
mod=0.6+0.4*np.sin(2*np.pi*np.arange(N)/SR/9)
L+=w*0.025*mod; R+=np.roll(w,4000)*0.025*mod
fade=np.ones(N); fi=int(2*SR); fo=int(4*SR); fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)
st=np.stack([L,R],1)*fade[:,None]; st/=np.abs(st).max()*1.12
wv=wave.open(sys.argv[1],'w'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes((st*32767).astype(np.int16).tobytes())
