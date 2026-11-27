import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m = WhisperModel(sys.argv[3], device="cpu", compute_type="int8")
segs, info = m.transcribe(a, language="hi", word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=True)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end} for w in s.words]})
    print(f"{s.start:.1f}-{s.end:.1f} {s.text}", flush=True)
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False)
