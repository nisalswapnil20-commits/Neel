import json,sys,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
segs,info=m.transcribe(np.fromfile("a16.raw",dtype=np.float32),word_timestamps=True,beam_size=5,language="hi",condition_on_previous_text=False)
out=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append(dict(w=w.word,s=round(w.start,2),e=round(w.end,2)))
json.dump(out,open("words.json","w"),ensure_ascii=False)
print(" ".join(f"{x['s']}:{x['w'].strip()}" for x in out))
