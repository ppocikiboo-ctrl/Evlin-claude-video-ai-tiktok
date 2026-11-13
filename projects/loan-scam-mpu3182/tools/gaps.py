import json, wave, numpy as np, sys
for v in sys.argv[1:]:
    w=wave.open(f"{v}.wav"); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    def db(s,e):
        seg=a[int(s*16000):int(e*16000)]
        if len(seg)<160: return -99
        # 50ms frames, report loudest frame
        n=len(seg)//800; f=seg[:n*800].reshape(n,800); r=np.sqrt((f**2).mean(1))+1e-9
        return 20*np.log10(np.percentile(r,90))
    words=[x for s in json.load(open(f"{v}.json")) for x in s['words']]
    print("==",v, "speech dB ~", round(db(10,20),1))
    for i in range(1,len(words)):
        p,c=words[i-1],words[i]
        g=c['s']-p['e']
        # also flag long words (whisper stretches over pauses)
        if g>0.4: print(f"GAP {p['e']:.2f}->{c['s']:.2f} ({g:.2f}s) {db(p['e'],c['s']):.0f}dB  ..{p['w'].strip()} | {c['w'].strip()}..")
        dur=c['e']-c['s']
        if dur>1.2: print(f"LONGWORD {c['s']:.2f}-{c['e']:.2f} {c['w'].strip()}")
