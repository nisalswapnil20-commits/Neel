import numpy as np, unicodedata, subprocess, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
DUR=16.90; N=int(DUR*FPS)+1
U="/root/.claude/uploads/cb453c9f-ae83-5c8c-b882-f17b1329f722/"
F="/root/.fonts/"
ORANGE=(255,106,31); CREAM=(245,240,228)
fHi=ImageFont.truetype(F+"TiroDevanagariHindi-Regular.ttf",86)
fHiS=ImageFont.truetype(F+"Hind-SemiBold.ttf",38)
fAnton=ImageFont.truetype(F+"Anton-Regular.ttf",170)
fAntonM=ImageFont.truetype(F+"Anton-Regular.ttf",58)
fAntonS=ImageFont.truetype(F+"Anton-Regular.ttf",44)
fMono=ImageFont.truetype(F+"CourierPrime-Bold.ttf",30)

def ease(x): x=min(max(x,0),1); return 1-(1-x)**3
def back(x):
    x=min(max(x,0),1); c=1.9; return 1+(c+1)*(x-1)**3+c*(x-1)**2

# ---- segments: (start,end,[(word,s,e)], stat)
S=[
 (0.0,2.70,[("If",0.0,0.16),("you",0.16,0.3),("want",0.3,0.66),("to",0.66,0.92),("achieve",0.92,1.28),("something",1.28,1.76),("really",1.76,2.2),("big,",2.2,2.6)],("SOMETHING","REALLY BIG",1.28)),
 (2.70,6.55,[("you",2.76,3.46),("need",3.46,3.76),("to",3.76,3.96),("be",3.96,4.1),("ready",4.1,4.52),("to",4.52,4.76),("have",4.76,5.0),("really",5.0,5.44),("big",5.44,5.76),("sacrifices.",5.76,6.4)],("BIG","SACRIFICES",5.44)),
 (6.55,8.20,[("Yes,",6.62,7.2),("absolutely.",7.36,8.0)],("YES.","ABSOLUTELY",6.62)),
 (8.20,11.50,[("तुम",8.28,8.58),("कितना",8.58,8.9),("बड़ा",8.9,9.1),("game",9.1,9.24),("खेल",9.24,9.42),("सकते",9.42,9.62),("हो,",9.62,9.68),("depend",9.68,10.0),("करता",10.0,10.22),("है",10.22,10.3),("तुम",10.3,10.42),("कितना",10.42,10.7),("बड़ा",10.7,10.84),("sacrifice",10.84,11.04),("करते",11.04,11.3),("हो।",11.3,11.46)],("GAME","= SACRIFICE",9.1)),
 (11.50,12.78,[("चाहता",11.52,11.82),("तो",11.82,11.96),("हर",11.96,12.16),("कोई",12.16,12.28),("सब",12.28,12.48),("कुछ",12.48,12.66),("है…",12.66,12.76)],("EVERYONE","WANTS EVERYTHING",11.96)),
 (12.78,14.50,[("पर",12.82,12.9),("कितनी",12.9,13.2),("बुरी",13.2,13.38),("तरह",13.38,13.62),("से",13.62,13.7),("चाहते",13.7,13.92),("हो,",13.92,14.0),("वो",14.0,14.06),("difference",14.06,14.32),("करता",14.32,14.4),("है।",14.4,14.48)],("HOW BADLY","DO YOU WANT IT?",13.2)),
 (14.50,DUR,[("Yes.",14.5,14.9)],("WANT IT","BADLY.",14.6)),
]
HL={"really","big,","big","sacrifices.","absolutely.","game","sacrifice","बड़ा","हर","सब","कुछ","बुरी","तरह","difference"}
def isnum(w): return w in HL

def clusters(w):
    out=[]
    for i,c in enumerate(w):
        if out and (unicodedata.category(c).startswith("M") or (i>0 and w[i-1]=="्") or c=="‍"):
            out[-1]+=c
        else: out.append(c)
    return out

# ---- photos
def load(p): return Image.open(U+p).convert("RGB")
P=[load("88c7bc4f-image.png"),load("8d00d382-image.jpg"),load("403dd71e-image.jpg"),load("a9d26409-image.jpg"),load("ffd182d9-image.jpg"),load("e3b67a33-image.jpg")]
P=[ImageEnhance.Contrast(im).enhance(1.06) for im in P]
# shots: (photo, center(x,y frac), zoom0, zoom1) -- zoom = crop fraction of width
SH=[(5,(.5,.45),1.0,.85),(0,(.45,.40),.95,.75),(1,(.5,.42),.90,.75),(2,(.5,.40),.95,.80),(4,(.48,.45),.80,.65),(0,(.44,.35),.60,.50),(3,(.55,.5),.60,.75)]
PH=1240  # photo area height
blurs=[]
for im in P:
    b=im.resize((W,H) if im.width/im.height<W/H else (int(H*im.width/im.height),H)).filter(ImageFilter.GaussianBlur(40))
    b=ImageEnhance.Brightness(b).enhance(.35); blurs.append(b.crop(((b.width-W)//2,0,(b.width-W)//2+W,H)))
def shot(i,t):
    pi,(cx,cy),z0,z1=SH[i]; s0,s1=S[i][0],S[i][1]
    p=min(max((t-s0)/(s1-s0+0.3),0),1); p=p*p*(3-2*p)
    im=P[pi]; z=z0+(z1-z0)*p
    ar=W/PH; cw=im.width*z; ch=cw/ar
    if ch>im.height: ch=im.height; cw=ch*ar
    x=cx*im.width-cw/2; y=cy*im.height-ch/2
    x=min(max(x,0),im.width-cw); y=min(max(y,0),im.height-ch)
    fr=im.resize((W,PH),Image.LANCZOS,box=(x,y,x+cw,y+ch))
    return fr, pi
# gradient mask for photo bottom fade
g=np.ones((PH,W),np.float32); ramp=np.linspace(1,0,420)**1.4; g[PH-420:]=ramp[:,None]
gmask=Image.fromarray((g*255).astype(np.uint8))
# vignette + grain
yy,xx=np.mgrid[0:H,0:W]; vig=1-0.55*np.clip(((xx-W/2)/(W*.75))**2+((yy-H*.4)/(H*.62))**2,0,1)
vig=vig[...,None].astype(np.float32)
rng=np.random.default_rng(1); grains=[rng.normal(0,7,(H//2,W//2,1)).astype(np.float32) for _ in range(6)]

def seg_at(t):
    for i,s in enumerate(S):
        if s[0]<=t<s[1]: return i
    return len(S)-1

def frame(n):
    t=n/FPS; i=seg_at(t)
    base=Image.new("RGB",(W,H),(10,10,12))
    fr,pi=shot(i,t)
    base.paste(blurs[pi],(0,0))
    # punch zoom at cut
    dt=t-S[i][0]
    if i>0 and dt<0.35:
        k=1+0.06*(1-ease(dt/0.35)); fr=fr.resize((int(W*k),int(PH*k))).crop((int((W*k-W)/2),int((PH*k-PH)/2),int((W*k-W)/2)+W,int((PH*k-PH)/2)+PH))
    # crossfade from previous
    if i>0 and dt<0.25:
        pf,ppi=shot(i-1,t); fr=Image.blend(pf,fr,ease(dt/0.25))
    base.paste(fr,(0,0),gmask)
    d=ImageDraw.Draw(base,"RGBA")
    # top gradient for header legibility
    for y in range(0,260,4): d.rectangle([0,y,W,y+4],fill=(0,0,0,int(150*(1-y/260))))
    # progress bar
    d.rectangle([0,0,W,8],fill=(255,255,255,40)); d.rectangle([0,0,int(W*t/DUR),8],fill=ORANGE)
    # header pill
    hp=ease(t/0.6)
    txt="बड़ी सफलता = बड़ी कुर्बानी"; tw=d.textlength(txt,font=fHiS)
    x0=60; y0=70-int(30*(1-hp))
    d.rounded_rectangle([x0,y0,x0+tw+60,y0+70],35,fill=(0,0,0,int(140*hp)),outline=ORANGE+(int(255*hp),),width=3)
    d.text((x0+30,y0+8),txt,font=fHiS,fill=CREAM+(int(255*hp),))
    # REC dot + mono label
    if int(t*2)%2==0: d.ellipse([W-205,y0+26,W-187,y0+44],fill=(230,40,40,int(255*hp)))
    d.text((W-175,y0+18),"PODCAST",font=fMono,fill=(255,255,255,int(200*hp)))
    # speaker tag
    sp=ease((t-0.4)/0.7); sx=60-int(80*(1-sp))
    d.rectangle([sx,1150,sx+10,1250],fill=ORANGE+(int(255*sp),))
    d.text((sx+30,1140),"RAJ SHAMANI",font=fAntonM,fill=(255,255,255,int(255*sp)))
    d.text((sx+32,1214),"PODCASTER  •  ENTREPRENEUR",font=fMono,fill=(255,200,170,int(230*sp)))
    # stat badge (top-right over photo)
    st=S[i][3]
    if st and t>=st[2]:
        lab,sub,ts=st; p=(t-ts)
        sc=back(p/0.45)
        L=Image.new("RGBA",(1000,330),(0,0,0,0)); ld=ImageDraw.Draw(L)
        lw=ld.textlength(lab,font=fAnton); sw=ld.textlength(sub,font=fAntonS)
        bw=max(lw,sw)+70
        ld.rounded_rectangle([0,0,bw,300],26,fill=(12,12,14,200),outline=ORANGE,width=4)
        ld.text((35,-5),lab,font=fAnton,fill=ORANGE)
        ld.rectangle([35,222,35+sw,226],fill=(255,255,255,90))
        ld.text((35,232),sub,font=fAntonS,fill=(255,255,255))
        L=L.crop((0,0,int(bw)+2,302))
        s2=max(sc,0.01); L=L.resize((max(1,int(L.width*s2)),max(1,int(L.height*s2))))
        a=min(1,p/0.15); 
        if a<1: L.putalpha(L.getchannel("A").point(lambda v:int(v*a)))
        bx=W-60-L.width; by=820+ (151-L.height//2)
        base.paste(L,(bx,by),L)
    # typewriter card
    words=S[i][2]
    cy0=1300; d.rounded_rectangle([50,cy0,W-50,1790],30,fill=(16,16,18,235),outline=(255,255,255,30),width=2)
    d.rectangle([90,cy0+34,98,cy0+62],fill=ORANGE); d.text((110,cy0+28),f"{i+1:02d} / {len(S):02d}",font=fMono,fill=ORANGE)
    # build typed tokens
    toks=[]; typing=False
    for w,s,e in words:
        if t<s: break
        cl=clusters(w); k=len(cl) if t>=e else max(1,int(len(cl)*(t-s)/max(e-s,0.05))+1); k=min(k,len(cl))
        toks.append(("".join(cl[:k]),isnum(w)));
        if k<len(cl): typing=True
    # layout lines
    x,y=90,cy0+90; lh=122; maxx=W-90
    lines=[[]]; cx=x
    for w,num in toks:
        full=w; ww=d.textlength(full,font=fHi)
        if cx+ww>maxx and lines[-1]: lines.append([]); cx=x
        lines[-1].append((w,num,cx)); cx+=ww+d.textlength(" ",font=fHi)
    endx,endy=x,y
    for li,ln in enumerate(lines):
        for w,num,px in ln:
            col=ORANGE if num else CREAM
            if num:
                bb=d.textbbox((px,y+li*lh),w,font=fHi); d.rectangle([bb[0]-8,bb[1]-6,bb[2]+8,bb[3]+10],fill=(255,106,31,40))
            d.text((px,y+li*lh),w,font=fHi,fill=col)
            endx=px+d.textlength(w,font=fHi); endy=y+li*lh
    if typing or int(t*2.5)%2==0:
        d.rectangle([endx+8,endy+22,endx+44,endy+116],fill=ORANGE)
    # flash on cut
    arr=np.asarray(base).astype(np.float32)
    if i>0 and dt<0.18: arr=arr+ (1-dt/0.18)*np.array([255,170,110],np.float32)*0.35
    gr=grains[n%6]; gr=np.repeat(np.repeat(gr,2,0),2,1)
    arr=arr*vig+gr
    return np.clip(arr,0,255).astype(np.uint8)

if __name__=="__main__":
    if len(sys.argv)>1:
        for tt in sys.argv[1:]:
            Image.fromarray(frame(int(float(tt)*FPS))).save(f"prev_{tt}.png")
        sys.exit()
    p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","video.mp4"],stdin=subprocess.PIPE)
    for n in range(N):
        p.stdin.write(frame(n).tobytes())
        if n%90==0: print(n,flush=True)
    p.stdin.close(); p.wait()
