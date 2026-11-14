"""Cut list for the retake (n1..n4): editorial sections -> tightened pieces on a 1/30 s grid.

Tighter than v1 for a fluent, firm delivery:
  * silences >= 0.25 s shrink to ~0.18 s
  * voiced stretches that no transcribed word covers (um/eh, false starts) are removed
  * explicit cuts (repeats, rambles) snap to the quietest 10 ms within +-0.2 s
Writes edl.json and words_out.json (words on the edited timeline).
"""
import json, wave, sys
import numpy as np

S = sys.argv[1]
RAW = f"{S}/raw2"
FPS = 30
MIN_SIL, KEEP_PRE, KEEP_POST = 0.25, 0.08, 0.10
FILLER_MIN = 0.30          # an unworded voiced run at least this long is cut

def q(t): return round(t * FPS) / FPS

def energy(v):
    w = wave.open(f"{RAW}/{v}.wav")
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    f = a[: len(a) // 160 * 160].reshape(-1, 160)
    return 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9)

SRC = ("n1", "n2", "n3", "n4")
DB = {v: energy(v) for v in SRC}
REF = {v: np.percentile(DB[v], 95) for v in SRC}
WORDS = {v: [w for s in json.load(open(f"{RAW}/{v}.json")) for w in s["words"]] for v in SRC}

def snap(v, t, win=0.2):
    i0, i1 = int((t - win) * 100), int((t + win) * 100)
    seg = DB[v][max(i0, 0):i1]
    return (max(i0, 0) + int(np.argmin(seg))) / 100 if len(seg) else t

def voiced(v, s, e):
    db = DB[v][int(s * 100): int(e * 100)]
    m = db > (REF[v] - 21)
    out = m.copy(); i = 0; n = len(m)
    while i < n:  # bridge dropouts < 80 ms inside words
        if not m[i]:
            j = i
            while j < n and not m[j]: j += 1
            if j - i < 8 and i > 0 and j < n: out[i:j] = True
            i = j
        else: i += 1
    return out

def runs(mask, val):
    i, n = 0, len(mask)
    while i < n:
        if mask[i] == val:
            j = i
            while j < n and mask[j] == val: j += 1
            yield i, j
            i = j
        else: i += 1

def subtract(pieces, cs, ce):
    out = []
    for a, b in pieces:
        if ce <= a or cs >= b: out.append([a, b]); continue
        if cs > a: out.append([a, cs])
        if ce < b: out.append([ce, b])
    return out

def tighten(v, s, e, cuts=()):
    m = voiced(v, s, e)
    pieces = [[s, e]]
    for i, j in runs(m, False):              # long silences
        if (j - i) / 100 >= MIN_SIL and i > 0 and j < len(m):
            a, b = s + i / 100 + KEEP_PRE, s + j / 100 - KEEP_POST
            if b > a: pieces = subtract(pieces, a, b)
    cover = np.zeros(len(m), bool)            # unworded voiced runs = fillers
    for w in WORDS[v]:
        a, b = int((w["s"] - s - 0.06) * 100), int((w["e"] - s + 0.06) * 100)
        cover[max(a, 0):max(b, 0)] = True
    for i, j in runs(m & ~cover, True):
        if (j - i) / 100 >= FILLER_MIN:
            pieces = subtract(pieces, s + i / 100 - 0.03, s + j / 100 + 0.03)
    for cs, ce in cuts:                       # editorial removals
        pieces = subtract(pieces, snap(v, cs), snap(v, ce))
    out = []
    for a, b in pieces:
        a, b = q(a), q(b)
        if b - a >= 3 / FPS: out.append([a, b])
    return out

SECTIONS = [
    # id, src, start, end, cuts            (source seconds)
    ("hook1", "n2", 24.20, 39.88, []),               # tanpa cek CTOS ... jumlah yang sangat besar
    ("hook2", "n2", 311.95, 316.86, []),             # mana-mana pinjaman ... adalah penipuan.
    ("intro", "n1", 0.00, 30.50, [(4.70, 9.62)]),    # drop the first "Saya Evelyn Sofidu" take
    ("data1", "n1", 30.60, 57.25, []),
    ("data2", "n2", 0.00, 16.95, []),
    ("umpan", "n2", 17.05, 54.40, []),
    ("jerat", "n2", 56.10, 156.10, [(89.24, 128.92)]),   # KPKT ramble + repeated ad claims
    ("modus", "n2", 157.48, 244.30, []),
    ("psiko", "n2", 244.30, 290.42, [(263.84, 278.74)]),  # repeated pay/don't-pay loop
    ("keldai", "n2", 291.15, 316.86, []),
    ("kesan", "n3", 1.40, 71.62, [(49.72, 59.66)]),      # "mengugut dan mengugut ... sangat-sangat"
    ("etika", "n3", 71.50, 163.88, []),                 # whisper's phantom "Terima kasih" dropped
    ("undang", "n4", 0.00, 72.55, [(60.86, 62.48)]),     # "Mangsa yang sama,"
    ("literasi", "n4", 72.85, 152.42, [(89.02, 102.36)]),  # repeated "tidak akan minta yuran"
    ("integriti", "n4", 152.42, 214.48, []),
    ("penutup", "n4", 216.80, 265.85, []),
]

pieces, sections, t = [], [], 0.0
for sid, v, s, e, cuts in SECTIONS:
    ps = tighten(v, s, e, cuts)
    st = t
    for a, b in ps:
        pieces.append({"src": v, "in": a, "out": b, "at": round(t, 4), "sec": sid})
        t = round(t + (b - a), 4)
    sections.append({"id": sid, "src": v, "start": round(st, 3), "end": round(t, 3)})

words_out = []
for v in SRC:
    for w in WORDS[v]:
        for p in pieces:
            if p["src"] != v: continue
            s_, e_ = max(w["s"], p["in"]), min(w["e"], p["out"])
            if e_ - s_ >= 0.5 * (w["e"] - w["s"]) or (p["in"] <= w["s"] < p["out"]):
                words_out.append({"text": w["w"].strip(), "start": round(p["at"] + s_ - p["in"], 3),
                                  "end": round(p["at"] + e_ - p["in"], 3), "src": v, "sec": p["sec"], "srcT": round(w["s"], 2)})
                break
words_out.sort(key=lambda w: w["start"])
json.dump({"fps": FPS, "duration": t, "pieces": pieces, "sections": sections}, open(f"{S}/work/edl.json", "w"), indent=1)
json.dump(words_out, open(f"{S}/work/words_out.json", "w"), ensure_ascii=False, indent=0)
raw = sum(e - s for _, _, s, e, _ in SECTIONS)
print(f"pieces {len(pieces)}  edited {t:.1f}s  (sections {raw:.1f}s, sources 838.3s)")
for s in sections: print(f"  {s['id']:10s} {s['start']:7.2f} -> {s['end']:7.2f}")
