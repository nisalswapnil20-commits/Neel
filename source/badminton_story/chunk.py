import json,math
W=json.load(open('words.json'))
sents={}
for k,w in enumerate(W): sents.setdefault(w['i'],[]).append(k)
caps=[]
for i,idx in sorted(sents.items()):
    clauses=[[]]
    for k in idx:
        clauses[-1].append(k)
        if W[k]['w'].endswith(',') or W[k]['w'].endswith('?'): clauses.append([])
    clauses=[c for c in clauses if c]
    merged=[]
    for c in clauses:
        if merged and (len(c)<3 or len(merged[-1])<3) and len(merged[-1])+len(c)<=7: merged[-1]+=c
        else: merged.append(c)
    for c in merged:
        n=math.ceil(len(c)/6); size=math.ceil(len(c)/n)
        for j in range(0,len(c),size):
            part=c[j:j+size]
            if len(part)<3 and caps and len(caps[-1])+len(part)<=7 and caps[-1][-1]+1==part[0] and W[caps[-1][0]]['i']==i: caps[-1]+=part
            else: caps.append(part)
out=[]
for n,c in enumerate(caps):
    out.append({'words':[W[k]['w'] for k in c],'t':[W[k]['t'] for k in c]})
for n,c in enumerate(out):
    nxt=out[n+1]['t'][0] if n+1<len(out) else 175.94
    c['end']=min(nxt, c['t'][-1]+1.5)
json.dump(out,open('caps2.json','w'),ensure_ascii=False)
for c in out: print(c['t'][0], c['end'], ' '.join(c['words']))
print(len(out), max(len(c['words']) for c in out))
