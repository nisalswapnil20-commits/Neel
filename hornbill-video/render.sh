#!/bin/bash
# usage: render.sh out.mp4 [extra ffmpeg args e.g. -t 12]
S=$(dirname $(dirname $0)); OUT=$1; shift
A=/root/.claude/uploads/83dbac44-6974-5160-83d7-f3c9b996b88f/70126f31-________________.mp3
D=181.6
ffmpeg -v error -y -i $S/fg.mp4 -i "$A" -i $S/music2.wav -f lavfi -i "color=c=0xFFC400:s=1080x10:r=30" \
-filter_complex "
[0:v]fps=30,split[a][b];
[a]scale=-2:1920:flags=bicubic,crop=1080:1920,boxblur=28:2,eq=brightness=-0.22:saturation=0.75,vignette=PI/3.2[bg];
[b]scale=1080:824:flags=lanczos,unsharp=5:5:0.9:3:3:0.0,eq=contrast=1.06:saturation=1.15:gamma=0.98,vignette=PI/5[fg];
[bg][fg]overlay=0:520,format=yuv420p,
drawbox=x=0:y=518:w=1080:h=2:color=white@0.35:t=fill,drawbox=x=0:y=1344:w=1080:h=2:color=white@0.35:t=fill[v1];
[3:v]format=rgba[bar];
[v1][bar]overlay=x='-W+W*t/$D':y=H-10:eval=frame:shortest=0[v2];
[v2]ass=$S/subs.ass,fade=t=in:st=0:d=0.8,fade=t=out:st=$(echo "$D-0.7"|bc):d=0.7,format=yuv420p[v];
[1:a]aresample=48000,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,asplit[voice][sc];
[2:a]aresample=48000,volume=0.55[mus];
[mus][sc]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=500[duck];
[voice][duck]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=$(echo "$D-1.2"|bc):d=1.2,loudnorm=I=-14:TP=-1.0:LRA=11[aout]
" -map "[v]" -map "[aout]" -c:v libx264 -preset medium -crf 18 -profile:v high -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t $D "$@" "$OUT"
