"""Build the cut list: editorial sections -> VAD-tightened pieces on a 1/30 s grid.
Writes edl.json (pieces + section map) and words_out.json (words mapped to output time)."""
import json, wave, sys
import numpy as np

S = sys.argv[1]
FPS = 30
MIN_SIL = 0.30      # silences at least this long get tightened
KEEP_PRE = 0.10     # room kept after the last word before a cut
KEEP_POST = 0.12    # room kept before the next word after a cut

def q(t):  # snap to frame grid
    return round(t * FPS) / FPS

def energy(v):
    w = wave.open(f"{S}/raw/{v}.wav")
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    f = a[: len(a) // 160 * 160].reshape(-1, 160)  # 10 ms frames
    return 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9)

DB = {v: energy(v) for v in ("v1", "v2", "v3")}
REF = {v: np.percentile(DB[v], 95) for v in DB}

def speech_mask(v, s, e):
    db = DB[v][int(s * 100): int(e * 100)]
    m = db > (REF[v] - 21)
    # bridge tiny dropouts (<80 ms) inside words
    out = m.copy(); i = 0; n = len(m)
    while i < n:
        if not m[i]:
            j = i
            while j < n and not m[j]: j += 1
            if j - i < 8 and i > 0 and j < n: out[i:j] = True
            i = j
        else: i += 1
    return out

def tighten(v, s, e, cuts=()):
    """Return keep pieces inside [s,e], removing silences >= MIN_SIL and explicit cuts."""
    m = speech_mask(v, s, e)
    pieces = []; i = 0; n = len(m)
    # find silence runs
    keep_start = s
    while i < n:
        if not m[i]:
            j = i
            while j < n and not m[j]: j += 1
            if (j - i) / 100 >= MIN_SIL and i > 0 and j < n:
                a = s + i / 100 + KEEP_PRE
                b = s + j / 100 - KEEP_POST
                if b > a:
                    pieces.append([keep_start, a]); keep_start = b
            i = j
        else: i += 1
    pieces.append([keep_start, e])
    # explicit removals
    for cs, ce in cuts:
        nxt = []
        for a, b in pieces:
            if ce <= a or cs >= b: nxt.append([a, b]); continue
            if cs > a: nxt.append([a, cs])
            if ce < b: nxt.append([ce, b])
        pieces = nxt
    out = []
    for a, b in pieces:
        a, b = q(a), q(b)
        if b - a >= 2 / FPS: out.append([a, b])
    return out

# ---- editorial sections (source times) ----
SECTIONS = [
    # id, src, start, end, explicit cuts
    ("hook1", "v3", 10.50, 17.42, []),          # Pada Mei 2026 ... RM167,050
    ("hook2", "v3", 56.10, 58.48, []),          # ada rumah mangsa yang dibaling bom petrol
    ("hook3", "v3", 1.95, 4.15, []),            # Ini bukanlah cerita rekaan.
    ("intro", "v1", 0.45, 22.40, []),           # salam, nama, topik
    ("data", "v1", 22.40, 67.20, [(22.34, 24.42)]),   # drop "Oke," before "firstly"
    ("jerat", "v1", 67.40, 118.60, [(93.70, 94.46)]), # drop doubled "logo,"
    ("modus", "v1", 118.70, 194.45, [(119.15, 119.93)]),  # drop "Oke,"
    ("kes", "v3", 8.60, 59.00, []),             # second take of the case stories
    ("kesan", "v3", 71.20, 103.40, []),
    ("etika", "v3", 122.30, 245.30, []),
    ("undang", "v2", 0.50, 80.00, []),
    ("literasi", "v2", 83.90, 138.60, []),
    ("integriti", "v2", 143.60, 195.90, []),
    ("penutup", "v2", 203.30, 240.90, []),      # drop whisper's phantom "Terima kasih kerana menonton"
]

GAP_BETWEEN_SECTIONS = {"hook3": 0.0}

pieces, sections, t = [], [], 0.0
for sid, v, s, e, cuts in SECTIONS:
    ps = tighten(v, s, e, cuts)
    sec_start = t
    for a, b in ps:
        pieces.append({"src": v, "in": a, "out": b, "at": round(t, 4), "sec": sid})
        t = round(t + (b - a), 4)
    sections.append({"id": sid, "src": v, "start": round(sec_start, 3), "end": round(t, 3)})

# map words to output time
words_out = []
for v in ("v1", "v2", "v3"):
    for seg in json.load(open(f"{S}/raw/{v}.json")):
        for w in seg["words"]:
            mid = (w["s"] + w["e"]) / 2
            for p in pieces:
                if p["src"] == v and p["in"] <= mid < p["out"]:
                    s_ = max(w["s"], p["in"]); e_ = min(w["e"], p["out"])
                    words_out.append({"text": w["w"].strip(), "start": round(p["at"] + s_ - p["in"], 3),
                                      "end": round(p["at"] + e_ - p["in"], 3), "src": v, "sec": p["sec"], "srcT": round(w["s"], 2)})
words_out.sort(key=lambda w: w["start"])

json.dump({"fps": FPS, "duration": t, "pieces": pieces, "sections": sections}, open(f"{S}/work/edl.json", "w"), indent=1)
json.dump(words_out, open(f"{S}/work/words_out.json", "w"), ensure_ascii=False, indent=0)
raw = sum(e - s for _, _, s, e, _ in SECTIONS)
print(f"pieces {len(pieces)}  edited {t:.1f}s  (sections raw {raw:.1f}s, sources 685.7s)")
for s in sections: print(f"  {s['id']:10s} {s['start']:7.2f} -> {s['end']:7.2f}")
