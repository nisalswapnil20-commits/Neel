import json, sys, difflib, re
S=sys.argv[1]
turbo=[w for s in json.load(open(S+'/trA.json')) for w in s['words']]
small=[w for s in json.load(open(S+'/tr.json')) for w in s['words']]
hyp=[w for w in turbo if not (31.9<w['s']<50.2)]+[w for w in small if 31.9<w['s']<50.2]
hyp.sort(key=lambda w:w['s'])
norm=lambda x: re.sub(r'[^ऀ-ॿ]','',x).replace('़','').replace('ँ','ं')
KEY=set()
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
ev=[]
for line in open(S+'/gen/script.txt',encoding='utf8'):
    a,b,txt=line.strip().split('|',2); a=float(a); b=float(b)
    words=txt.split()
    cand=[w for w in hyp if a-0.4<=w['s']<b+0.2]
    times=[None]*len(words)
    sm=difflib.SequenceMatcher(None,[norm(w) for w in words],[norm(w['w']) for w in cand],autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): times[blk.a+k]=max(a,min(b,cand[blk.b+k]['s']))
    # fill gaps by char-proportional interpolation
    known=[(-1,a)]+[(i,t) for i,t in enumerate(times) if t is not None]+[(len(words),b)]
    for (i0,t0),(i1,t1) in zip(known,known[1:]):
        L=sum(len(w) for w in words[i0+1:i1]) or 1; acc=0
        span=max(0,t1-t0)
        for j in range(i0+1,i1):
            times[j]=t0+span*(acc/(L+ (len(words[i0]) if i0>=0 else 0)))+ (0 if i0<0 else span*len(words[i0])/(L+len(words[i0])))
            acc+=len(words[j])
    for i in range(1,len(times)): times[i]=max(times[i],times[i-1]+0.05)
    # chunk: max 3 words / ~16 chars
    chunks=[];cur=[]
    for i,w in enumerate(words):
        cur.append(i)
        if len(cur)>=3 or sum(len(words[j]) for j in cur)>=15 or w.endswith(','):
            chunks.append(cur);cur=[]
    if cur:
        if len(cur)==1 and chunks and len(chunks[-1])<3: chunks[-1]+=cur
        else: chunks.append(cur)
    for ci,ch in enumerate(chunks):
        cs=times[ch[0]]; ce=times[chunks[ci+1][0]] if ci+1<len(chunks) else b+0.15
        for k,i in enumerate(ch):
            s0=cs if k==0 else times[i]; s1=times[ch[k+1]] if k+1<len(ch) else ce
            parts=[]
            for j in ch:
                wd=words[j].rstrip(',')
                if j==i: parts.append(r"{\c&H00D7FF&\3c&H000000&}"+wd+r"{\r}")
                elif norm(wd) in {norm(x) for x in KEY}: parts.append(r"{\c&H7FE3FF&}"+wd+r"{\r}")
                else: parts.append(wd)
            pop=r"{\fscx112\fscy112\t(0,90,\fscx100\fscy100)}" if k==0 else ""
            ev.append((s0,s1,'Cap',pop+' '.join(parts)))
hdr=r"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Noto Sans Devanagari,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,7,3,2,60,60,440,1
Style: Title,Noto Sans Devanagari,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,2,8,60,60,250,1
Style: Sub,Noto Sans Devanagari,40,&H0000D7FF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,8,60,60,350,1
Style: Btn,Noto Sans Devanagari,58,&H00FFFFFF,&H00FFFFFF,&H000000FF,&H00000000,1,0,0,0,100,100,0,0,3,22,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
out=[hdr]
# title (top bar)
out.append(f"Dialogue: 1,{ts(0.2)},{ts(181.6)},Title,,0,0,0,,{{\\fad(600,500)}}हॉर्नबिल की अनोखी प्रेम कहानी")
out.append(f"Dialogue: 1,{ts(0.8)},{ts(181.6)},Sub,,0,0,0,,{{\\fad(600,500)}}जिसकी जान दूसरे के हाथ में होती है")
# outro subscribe button
out.append(f"Dialogue: 3,{ts(174.6)},{ts(181.6)},Btn,,0,0,0,,{{\\an5\\pos(540,1610)\\fad(250,300)\\fscx40\\fscy40\\t(0,250,\\fscx108\\fscy108)\\t(250,400,\\fscx100\\fscy100)\\t(3200,3400,\\fscx92\\fscy92\\3c&H555555&)\\t(3400,3600,\\fscx100\\fscy100)}}  LIKE करें  ")
out.append(f"Dialogue: 3,{ts(177.4)},{ts(181.6)},Btn,,0,0,0,,{{\\an5\\pos(540,1745)\\fad(250,300)\\fscx40\\fscy40\\t(0,250,\\fscx108\\fscy108)\\t(250,400,\\fscx100\\fscy100)}}  SUBSCRIBE करें  ")
for s0,s1,st,tx in ev: out.append(f"Dialogue: 2,{ts(s0)},{ts(s1)},{st},,0,0,0,,{tx}")
open(sys.argv[2],'w',encoding='utf8').write('\n'.join(out)+'\n')
print(len(ev),'caption events')
