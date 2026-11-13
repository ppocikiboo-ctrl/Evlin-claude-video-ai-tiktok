import sys, json
from faster_whisper import WhisperModel
import wave, numpy as np
def load(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0; return a
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
for name in sys.argv[2:]:
    segs, info = m.transcribe(load(f"{sys.argv[1]}/{name}.wav"), language="ms", word_timestamps=True, vad_filter=False, beam_size=5)
    out=[]
    for s in segs:
        out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"s":w.start,"e":w.end,"w":w.word} for w in s.words]})
        print(name, f"[{s.start:7.2f}-{s.end:7.2f}]{s.text}", flush=True)
    json.dump(out, open(f"{sys.argv[1]}/{name}.json","w"), ensure_ascii=False, indent=1)
