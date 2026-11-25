import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
import numpy as np
segs,info=m.transcribe(np.fromfile(sys.argv[1],dtype=np.float32),word_timestamps=True,beam_size=5,language="hi",initial_prompt="नमस्ते, यह हिंदी पॉडकास्ट है। Diabetes, depression, obesity, Alzheimer.")
print(info.language,info.language_probability)
out=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append(dict(w=w.word,s=w.start,e=w.end))
json.dump(out,open("words.json","w"),ensure_ascii=False,indent=0)
