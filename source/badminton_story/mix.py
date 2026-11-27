import subprocess
T=175.94
voice="sep/htdemucs/orig44/vocals.wav"
sfx=[ # file, time, gain(dB), trim_dur
 ("sfx/deep.mp3",0.0,-6,4),
 ("sfx/alarm.mp3",8.3,-14,1.9),
 ("sfx/whoosh.mp3",10.2,-12,1.2),
 ("sfx/impact.mp3",19.5,-16,2.5),
 ("sfx/trailer.mp3",36.68,-8,0.5),
 ("sfx/whoosh.mp3",36.4,-12,1.2),
 ("sfx/moto.mp3",51.0,-10,2.4),
 ("sfx/crash.mp3",53.2,-9,3.5),
 ("sfx/hb.mp3",57.5,-10,8),
 ("BEEP",59.3,-22,0), ("BEEP",60.3,-22,0), ("BEEP",61.3,-22,0), ("BEEP",62.3,-22,0),
 ("sfx/stadium.mp3",76.5,-16,3.5),
 ("sfx/whoosh2.mp3",91.6,-12,2.0),
 ("sfx/impact.mp3",92.0,-12,3.0),
 ("sfx/shutter.mp3",95.6,-12,1),("sfx/shutter2.mp3",96.2,-12,1),("sfx/shutter.mp3",96.9,-14,1),("sfx/shutter2.mp3",97.6,-12,1),
 ("sfx/impact.mp3",112.6,-8,3),
 ("sfx/riser.mp3",139.3,-14,3.6),
 ("sfx/trailer.mp3",142.88,-8,0.5),
 ("sfx/deep.mp3",155.5,-10,3),
 ("sfx/hb.mp3",157.6,-12,3.8),
 ("sfx/whoosh.mp3",164.9,-10,1.2),
 ("sfx/impact.mp3",165.5,-6,4),
 ("sfx/loudcheer.mp3",165.8,-12,7.5),
 ("sfx/whoosh2.mp3",172.9,-12,2),
 ("sfx/deep.mp3",173.2,-8,3),
]
inp=['-i',voice,'-i','music/601.mp3','-i','music/188.mp3']
fc=[]
fc.append("[0:a]aresample=48000,highpass=f=75,rubberband=pitch=1.035:formant=preserved:pitchq=quality,"
          "equalizer=f=180:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=1.5,"
          "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,aecho=0.8:0.5:28:0.06,atrim=0:%.2f[v]"%T)
fc.append("[v]asplit=2[vm][vk]")
# music A: 0..129 , B from t=125 (offset 28s)
fc.append("[1:a]aresample=48000,atrim=0:129,afade=t=in:st=0:d=1.5,afade=t=out:st=125:d=4,"
          "volume='if(between(t,52.9,58),0.25,if(between(t,58,62.8),0.55,1))':eval=frame,volume=-2dB[mA]")
fc.append("[2:a]aresample=48000,atrim=28:%.2f,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=3,afade=t=out:st=%.2f:d=2.5,volume=-1dB,adelay=125000|125000[mB]"%(28+T-125, T-125-2.5))
fc.append("[mA][mB]amix=inputs=2:normalize=0[m]")
fc.append("[m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[md]")
labels=[]
for n,(f,t,g,d) in enumerate(sfx):
    lab=f"s{n}"
    if f=="BEEP":
        fc.append(f"aevalsrc='0.6*sin(2*PI*1000*t)':d=0.13:s=48000,afade=t=out:st=0.08:d=0.05,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(t*1000)}|{int(t*1000)}[{lab}]")
    else:
        idx=len(inp)//2; inp+=['-i',f]
        fc.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{d},afade=t=out:st={max(0,d-0.4)}:d=0.4,volume={g}dB,adelay={int(t*1000)}|{int(t*1000)}[{lab}]")
    labels.append(f"[{lab}]")
fc.append("[md]volume=-7dB[mdd]")
fc.append("[vm][mdd]"+''.join(labels)+f"amix=inputs={2+len(labels)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]")
cmd=['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fc),'-map','[out]','-t',str(T),'-c:a','pcm_s16le','final_audio.wav']
subprocess.run(cmd,check=True)
