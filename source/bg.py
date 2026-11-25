import subprocess
# src, start, x-frac, duration, zoom-from, zoom-to
S=[("41037",1.0,0.70,1.06,1.18,1.08),
   ("34900",0.5,0.62,1.54,1.05,1.16),
   ("45396",0.5,0.50,1.82,1.20,1.06),
   ("106",  2.0,0.45,2.78,1.04,1.18),
   ("45286",0.3,0.66,1.92,1.18,1.05),
   ("110",  3.0,0.50,1.78,1.05,1.15)]
grade="eq=contrast=1.12:saturation=0.82:brightness=-0.04,curves=r='0/0 0.5/0.47 1/0.98':g='0/0.01 0.5/0.49 1/0.97':b='0/0.06 0.5/0.52 1/0.93',vignette=PI/4.2"
parts=[]
for k,(i,ss,xf,d,z0,z1) in enumerate(S):
    src=f"clips/{i}.mp4"
    h=int(subprocess.check_output(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=height","-of","csv=p=0",src]))
    cw=int(h*9/16)//2*2
    vf=(f"fps=30,crop={cw}:{h}:(iw-{cw})*{xf}:0,scale=1080:1920:flags=lanczos,"
        f"scale=w='trunc(1080*({z0}+({z1}-{z0})*t/{d})/2)*2':h=-2:eval=frame:flags=bicubic,"
        f"crop=1080:1920:(iw-1080)/2:(ih-1920)/2,"+grade+",format=yuv420p")
    if i=="110": vf=vf.replace("eq=contrast=1.12","eq=contrast=1.5:gamma=0.6")+",colorbalance=bs=0.25:bm=0.15:rs=-0.1"
    out=f"s{k}.mp4"; parts.append(out)
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(ss),"-i",src,"-t",str(d),"-vf",vf,"-an","-c:v","libx264","-crf","14","-preset","fast",out],check=True)
    print(out)
open("list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","list.txt","-c","copy","bg.mp4"],check=True)
