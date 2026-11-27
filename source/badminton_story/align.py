import json,re,difflib
d=json.load(open('tr.json'))
W=[(w[0],w[1],w[2].strip()) for s in d for w in s['w'] if not (54<=w[0]<62.9)]
for t in open('gapw.txt').read().split():
    w,ts=t.rsplit('@',1); W.append((float(ts),float(ts)+0.2,w))
W.sort()
def norm(x): return re.sub(r'[़ँं\s.,।?!\-"\']','',x).replace('ॉ','ा')
sents=[l.strip() for l in open('script.txt') if l.strip()]
toks=[];  # (sent_idx, word)
for i,s in enumerate(sents):
    for w in s.split(): toks.append([i,w,None])
a=[norm(t[1]) for t in toks]; b=[norm(w[2]) for w in W]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size): toks[blk.a+k][2]=W[blk.b+k][0]
# fuzzy fill for replace ops
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op=='replace' and (i2-i1)==(j2-j1):
        for k in range(i2-i1): toks[i1+k][2]=W[j1+k][0]
# interpolate
known=[i for i,t in enumerate(toks) if t[2] is not None]
print('matched',len(known),'of',len(toks))
toks[0][2]=toks[0][2] if toks[0][2] is not None else 0.0
if toks[-1][2] is None: toks[-1][2]=175.3
known=[i for i,t in enumerate(toks) if t[2] is not None]
for x,y in zip(known,known[1:]):
    for k in range(x+1,y): toks[k][2]=toks[x][2]+(toks[y][2]-toks[x][2])*(k-x)/(y-x)
# enforce monotonic
for k in range(1,len(toks)):
    if toks[k][2]<toks[k-1][2]: toks[k][2]=toks[k-1][2]
# chunk
caps=[];cur=[]
def flush():
    global cur
    if cur: caps.append({'t':' '.join(c[1] for c in cur),'s':cur[0][2],'ws':[round(c[2],2) for c in cur]}); cur=[]
for k,t in enumerate(toks):
    cur.append(t)
    end_sent = k+1==len(toks) or toks[k+1][0]!=t[0]
    if end_sent or (t[1][-1] in ',' and len(cur)>=3) or len(cur)>=6: flush()
for i,c in enumerate(caps):
    c['e']=round(min(caps[i+1]['s'] if i+1<len(caps) else 175.9, c['ws'][-1]+1.2),2); c['s']=round(c['s'],2)
json.dump(caps,open('caps.json','w'),ensure_ascii=False,indent=0)
json.dump([{'i':t[0],'w':t[1],'t':round(t[2],2)} for t in toks],open('words.json','w'),ensure_ascii=False)
for c in caps: print(c['s'],c['e'],c['t'])
