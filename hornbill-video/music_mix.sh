#!/bin/bash
# story-based soundtrack from Kevin MacLeod (incompetech.com, CC BY 4.0)
D=$1; OUT=$2
ffmpeg -v error -y \
 -i "$D/Interloper.mp3" -i "$D/Long%20Note%20Four.mp3" -i "$D/Heartbreaking.mp3" -i "$D/Heartwarming.mp3" \
 -filter_complex "
 [0:a]atrim=0:71.7,asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-20:TP=-2,afade=t=in:d=1.5,afade=t=out:st=69.2:d=2.5[a0];
 [1:a]atrim=10:46,asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-20:TP=-2,afade=t=in:d=2.5,afade=t=out:st=33.5:d=2.5,adelay=67700|67700[a1];
 [2:a]atrim=0:49.8,asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-19:TP=-2,afade=t=in:d=2.5,afade=t=out:st=47.3:d=2.5,adelay=101300|101300[a2];
 [3:a]atrim=0:33.6,asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-20:TP=-2,afade=t=in:d=2.5,afade=t=out:st=29.6:d=4,adelay=148100|148100[a3];
 [a0][a1][a2][a3]amix=inputs=4:normalize=0:duration=longest,atrim=0:181.7[m]" \
 -map "[m]" -ac 2 -ar 48000 "$OUT"
