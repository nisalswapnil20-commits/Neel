# Builds the 9:16 background plate (clips + photo cards), 30 fps, no text.
import subprocess, os, math
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
os.chdir(os.path.dirname(os.path.abspath(__file__)))
FPS=30; W,H=1080,1920
GRADE=("eq=contrast=1.10:saturation=0.70:brightness=-0.06,"
       "curves=r='0/0.02 0.5/0.50 1/0.97':g='0/0.02 0.5/0.49 1/0.95':b='0/0.07 0.5/0.52 1/0.90',"
       "vignette=PI/4")
# (kind, source, start-in-source / crop, x-frac, t0, t1, zoom-from, zoom-to)
SEG=[("photo","u2",None,None,0.00,2.16,1.00,1.07),
     ("clip","39803",1.0,0.06,2.16,4.62,1.04,1.13),
     ("clip","16109",1.0,0.25,4.62,6.74,1.12,1.03),
     ("clip","1038",2.0,0.13,6.74,9.14,1.02,1.14),
     ("clip","16017",2.0,0.84,9.14,11.38,1.12,1.02),
     ("clip","39765",1.0,0.50,11.38,12.78,1.03,1.12),
     ("clip","24621",1.0,0.28,12.78,14.26,1.12,1.03),
     ("clip","32591",2.0,0.50,14.26,17.05,1.03,1.13),
     ("clip","7761",3.0,0.50,17.05,20.20,1.03,1.14),
     ("photo","u1",None,None,20.20,22.60,1.00,1.08),
     ("clip","7678",3.0,0.58,22.60,26.20,1.02,1.12)]
CROPS={"u2":("img/u2.jpg",(130,30,530,430)),
       "u1":("img/u1.jpg",(0,0,480,560))}

def frames(t0,t1): return round(t1*FPS)-round(t0*FPS)

def clip(k,src,ss,xf,t0,t1,z0,z1):
    f=f"clips/{src}.mp4"; d=frames(t0,t1)/FPS
    h=int(subprocess.check_output(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=height","-of","csv=p=0",f]))
    cw=int(h*9/16)//2*2
    vf=(f"fps={FPS},crop={cw}:{h}:(iw-{cw})*{xf}:0,scale=1080:1920:flags=lanczos,"
        f"scale=w='trunc(1080*({z0}+({z1}-{z0})*t/{d})/2)*2':h=-2:eval=frame:flags=bicubic,"
        f"crop=1080:1920:(iw-1080)/2:(ih-1920)/2,unsharp=5:5:0.6,{GRADE},format=yuv420p")
    out=f"seg/s{k:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(ss),"-i",f,"-frames:v",str(frames(t0,t1)),
                    "-vf",vf,"-an","-c:v","libx264","-crf","14","-preset","fast",out],check=True)
    return out

def photo(k,src,t0,t1,z0,z1):
    path,box=CROPS[src]; im=Image.open(path).convert("RGB").crop(box)
    # backdrop: blurred, darkened, warm
    bgw=im.resize((W, int(W*im.height/im.width)))
    bgf=Image.new("RGB",(W,H)); bg=im.resize((int(H*im.width/im.height),H)) if im.width/im.height<W/H else bgw
    bg=bg.resize((max(W,bg.width),max(H,bg.height)))
    bg=bg.crop(((bg.width-W)//2,(bg.height-H)//2,(bg.width-W)//2+W,(bg.height-H)//2+H))
    bg=bg.filter(ImageFilter.GaussianBlur(40)); bg=ImageEnhance.Brightness(bg).enhance(0.38)
    bg=ImageEnhance.Color(bg).enhance(0.6)
    # card: photo with paper border
    cw=min(820,int(900*im.width/im.height)); ch=int(cw*im.height/im.width)
    ph=im.resize((cw,int(cw*im.height/im.width)),Image.LANCZOS).crop((0,0,cw,ch))
    ph=ph.filter(ImageFilter.UnsharpMask(2,60,2)); ph=ImageEnhance.Contrast(ph).enhance(1.06)
    b=22; card=Image.new("RGBA",(cw+2*b,ch+2*b+70),(242,236,224,255)); card.paste(ph,(b,b))
    n=frames(t0,t1); os.makedirs(f"ph{k}",exist_ok=True)
    for i in range(n):
        u=i/max(1,n-1); e=1-(1-u)**3
        z=z0+(z1-z0)*e; rot=-3.0+1.5*u
        c=card.resize((int(card.width*z),int(card.height*z)),Image.BICUBIC).rotate(rot,Image.BICUBIC,expand=True)
        fr=bg.copy()
        sh=Image.new("RGBA",c.size,(0,0,0,0)); sh.putalpha(c.split()[3].point(lambda a:a*0.6))
        sh=Image.new("RGBA",c.size,(0,0,0,255)).copy(); sh.putalpha(c.split()[3].point(lambda a:int(a*0.55)))
        sh=sh.filter(ImageFilter.GaussianBlur(28))
        x=(W-c.width)//2; y=(H-c.height)//2-150
        fr.paste(sh,(x+18,y+30),sh); fr.paste(c,(x,y),c)
        fr.save(f"ph{k}/{i:04d}.png")
    out=f"seg/s{k:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-framerate",str(FPS),"-i",f"ph{k}/%04d.png",
                    "-vf","vignette=PI/4.5,format=yuv420p","-c:v","libx264","-crf","14","-preset","fast",out],check=True)
    return out

os.makedirs("seg",exist_ok=True); parts=[]
for k,(kind,src,ss,xf,t0,t1,z0,z1) in enumerate(SEG):
    parts.append(clip(k,src,ss,xf,t0,t1,z0,z1) if kind=="clip" else photo(k,src,t0,t1,z0,z1)); print(parts[-1])
open("seg/list.txt","w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","seg/list.txt","-c","copy","bg.mp4"],check=True)
print("bg.mp4", sum(frames(s[4],s[5]) for s in SEG),"frames")
