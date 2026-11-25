import numpy as np, unicodedata, subprocess, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
DUR=29.86; N=int(DUR*FPS)+1
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
 (0.0,4.70,[("आप",0.0,1.18),("रोज़",1.18,1.88),("रात",1.88,2.04),("6",2.04,2.38),("घंटे",2.38,3.08),("से",3.08,3.3),("कम",3.3,3.54),("सोते",3.54,3.94),("हो,",3.94,4.1),("then",4.1,4.4),("as an individual…",4.4,4.7)],("< 6","HOURS OF SLEEP",2.04,None)),
 (4.70,9.90,[("आपके",4.7,5.0),("डायबिटीज़",5.0,7.06),("होने",7.06,7.36),("के",7.36,7.56),("chances",7.56,7.9),("28–58%",7.9,9.22),("बढ़",9.22,9.5),("जाते हैं",9.5,9.9)],("+28–58%","DIABETES RISK",7.9,(28,58))),
 (9.90,12.74,[("आपके",9.9,10.56),("डिप्रेशन",10.56,11.02),("के",11.02,11.2),("chances",11.2,11.46),("3X",11.46,12.0),("ज़्यादा",12.0,12.26),("हो",12.26,12.4),("जाते हैं",12.4,12.74)],("3X","DEPRESSION RISK",11.46,(3,))),
 (12.74,15.90,[("ओबेसिटी",12.74,13.66),("के",13.66,13.82),("chances",13.82,14.16),("55%",14.16,14.88),("बढ़",14.88,15.22),("जाते",15.22,15.42),("हैं",15.42,15.9)],("+55%","OBESITY RISK",14.16,(55,))),
 (15.90,19.24,[("अल्ज़ाइमर्स",15.9,16.76),("के",16.76,16.92),("chances",16.92,17.34),("68%",17.34,18.14),("बढ़",18.14,18.52),("जाते",18.52,18.72),("हैं",18.72,19.24)],("+68%","ALZHEIMER'S RISK",17.34,(68,))),
 (19.24,21.74,[("हार्ट",19.24,19.54),("अटैक",19.54,19.8),("के",19.8,20.0),("chances",20.0,20.3),("48%",20.3,21.04),("बढ़",21.04,21.38),("जाते",21.38,21.56),("हैं,",21.56,21.74)],("+48%","HEART ATTACK RISK",20.3,(48,))),
 (21.74,26.46,[("then",21.74,22.24),("memory",22.24,22.46),("loss",22.46,22.98),("40%",22.98,24.72),("से",24.72,25.52),("ज़्यादा",25.52,25.78),("होने",25.78,25.92),("लग",25.92,26.1),("जाता",26.1,26.36),("है",26.36,26.46)],("40%+","MEMORY LOSS",22.98,(40,))),
 (26.46,DUR,[("तुम्हें",26.46,26.86),("comparatively",26.86,27.38),("दूसरों",27.38,27.86),("से…",27.86,28.1)],None),
]
def isnum(w): return any(c.isdigit() for c in w)

def clusters(w):
    out=[]
    for i,c in enumerate(w):
        if out and (unicodedata.category(c).startswith("M") or (i>0 and w[i-1]=="्") or c=="‍"):
            out[-1]+=c
        else: out.append(c)
    return out

# ---- photos
def load(p): return Image.open(U+p).convert("RGB")
P=[load("084fc966-image.png"),load("4a11528e-image.jpg"),load("bd6101de-image.jpg")]
P=[ImageEnhance.Contrast(im).enhance(1.06) for im in P]
# shots: (photo, center(x,y frac), zoom0, zoom1) -- zoom = crop fraction of width
SH=[(0,(.47,.42),1.0,.80),(1,(.5,.40),.95,.80),(2,(.48,.45),.95,.78),(0,(.44,.36),.62,.52),
    (1,(.5,.32),.70,.58),(2,(.52,.46),.70,.60),(0,(.62,.62),.70,.82),(1,(.5,.45),.80,1.0)]
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
    txt="कम नींद = बड़ा खतरा"; tw=d.textlength(txt,font=fHiS)
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
        lab,sub,ts,vals=st; p=(t-ts)
        sc=back(p/0.45)
        if vals:
            c=ease(p/0.8)
            if len(vals)==2: lab=f"+{round(vals[0]*c)}–{round(vals[1]*c)}%"
            elif lab.endswith("X"): lab=f"{max(1,round(vals[0]*c))}X"
            elif lab.endswith("+"): lab=f"{round(vals[0]*c)}%+"
            else: lab=f"+{round(vals[0]*c)}%"
        L=Image.new("RGBA",(900,330),(0,0,0,0)); ld=ImageDraw.Draw(L)
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
    d.rectangle([90,cy0+34,98,cy0+62],fill=ORANGE); d.text((110,cy0+28),["01","02","03","04","05","06","07","08"][i]+" / 08",font=fMono,fill=ORANGE)
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
