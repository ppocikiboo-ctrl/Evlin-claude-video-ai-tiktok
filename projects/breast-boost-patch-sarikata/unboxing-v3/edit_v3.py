"""Video unboxing VERSI 3: gaya "Polaroid + listicle".
- Hook: janji listicle "3 SEBAB BARANG NI VIRAL" + snare roll; bingkai polaroid jatuh & melantun.
- Struktur bab: #1 / #2 / #3 dengan tab tajuk; setiap bab polaroid "ditukar" (naik dari bawah).
- Visual: video dalam bingkai polaroid miring atas latar gradien pastel bergerak + titik-titik;
  sarikata lama dari app dibuang dengan potongan (crop), bukan ditutup.
- Sarikata: font Lilita One dalam jalur putih polaroid, isi warna karaoke (pink, kata kunci oren).
- Penutup: skrin RECAP dengan tanda semak + butang "TEKAN BEG KUNING" dengan riak sentuhan.
- Bunyi: snare roll + hit, bonk, kertas "fwip", marimba, ding semak, kilauan kaca.
Guna: python3 edit_v3.py <klip1_hook.mp4> <klip2_cta.mp4>"""
import difflib, os, re, subprocess, sys, wave
import numpy as np

SR = 44100
SPEED = 1.10
rng = np.random.default_rng(33)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- Potongan: (input, mula, tamat, laju, zoom_mula, zoom_tamat, bab) ----------
SEGS = [
 (0, 0.25, 3.50, 1.0, 1.00, 1.05, "hook"),   # Benda yang asyik lalu FYP...
 (0, 3.80, 7.25, 1.0, 1.06, 1.00, "c1"),     # #1 patch 3 dalam 1
 (0, 7.25, 10.45, 2.2, 1.00, 1.06, ""),      # buka bungkusan (laju)
 (0, 10.45, 12.15, 1.0, 1.05, 1.00, ""),     # 7 keping
 (0, 12.50, 14.60, 1.0, 1.00, 1.04, ""),     # dada & punggung
 (0, 14.60, 15.80, 1.0, 1.05, 1.02, "c2"),   # #2 kelebihan
 (0, 16.05, 18.25, 1.0, 1.00, 1.05, ""),     # hormone free, lembut
 (0, 18.50, 20.12, 1.0, 1.05, 1.00, ""),     # collagen, hyaluronic
 (1, 0.25, 0.92, 1.0, 1.00, 1.02, ""),       # centella
 (1, 1.20, 3.75, 1.0, 1.02, 1.06, ""),       # expiry 2029
 (1, 4.75, 7.28, 1.0, 1.06, 1.00, "c3"),     # #3 cara guna
 (1, 7.50, 11.32, 1.0, 1.00, 1.05, ""),      # tampal, tak nampak
 (1, 12.20, 16.00, 1.0, 1.04, 1.00, "cta"),  # CTA suara
 (1, 15.94, 16.00, 1.0, 1.00, 1.00, "end"),  # skrin RECAP + butang CTA
]
END_DUR = 3.4

HEADERS = {
    "c1": ("#1", "3 DALAM 1 + 7 KEPING"),
    "c2": ("#2", "BAHAN LEMBUT & HORMONE-FREE"),
    "c3": ("#3", "PAKAI, ORANG TAK NAMPAK"),
    "cta": ("", "JOM CUBA!"),
}
RECAP = ["3 DALAM 1, 7 KEPING", "HORMONE-FREE, BAHAN LEMBUT", "PAKAI, ORANG TAK NAMPAK"]

SCRIPT = """
Benda yang asyik lalu / dekat *FYP korang tu / dah sampai tangan saya! /
Ni dia, patch / *3 dalam 1! /
Satu kotak ni ada / *7 keping, / boleh guna untuk / dada dan punggung. /
Cerita pasal *kelebihannya, / dia adalah *hormone-free, / bahan dia *lembut, /
ada *collagen, / ada *hyaluronic acid / dan *centella. /
Expiry date pun masih lama, / dalam *2029! /
Cara nak guna ni / *senang saja, / bersihkan bahagian kulit, / kemudian *tampal /
*4 hingga *6 jam, / pakai baju pun / orang *tak *nampak! /
Nak cuba ni? / Jangan tunggu lama, / tekan *beg *kuning sekarang! / Seller tengah buat / *harga *promo!
"""

# Susun atur
CW, CH = 860, 856              # isi video dalam polaroid
PW, PH = 912, 1112             # polaroid penuh (bingkai 26px, jalur bawah 230px)
STRIP_Y = 26 + CH              # mula jalur putih bawah
CARD_Y = 362                   # kedudukan polaroid atas kanvas
ANGLE = -0.026                 # sengetan polaroid (radian)
SRC_CY, SRC_H = 667, 1075      # tetingkap sumber (atas sarikata lama, y < 1215)

# ---------------- Bunyi efek ----------------
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def onepole(x, fc):
    y, s, a = np.zeros_like(x), 0.0, 1 - np.exp(-2 * np.pi * fc / SR)
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y

def st(x, pan=0.5):
    x = x / (np.abs(x).max() + 1e-9)
    return np.stack([x * (1 - pan) * 1.4, x * pan * 1.4], 1) / 1.4

def marimba(f, d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * env(n, 0.002, 0.16) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * env(n, 0.001, 0.03)
    return x

def snare_roll(d=0.5):
    n = int(d * SR); out = np.zeros(n); t = 0.0; gap = 0.07
    while t < d - 0.02:
        i = int(t * SR); m = int(0.04 * SR)
        hit = rng.standard_normal(m) * env(m, 0.0005, 0.012)
        hit = hit - onepole(hit, 900)
        out[i:i + m] += hit[:n - i] * (0.4 + 0.6 * t / d)
        t += gap; gap = max(0.022, gap * 0.82)
    return st(out)

def hit():
    n = int(0.6 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n); noise = noise - onepole(noise, 1200)
    x = noise * env(n, 0.001, 0.09) * 0.7 + np.sin(2 * np.pi * np.cumsum(np.geomspace(160, 60, n)) / SR) * env(n, 0.002, 0.12)
    return st(x)

def bonk():
    n = int(0.25 * SR)
    x = np.sin(2 * np.pi * np.cumsum(np.geomspace(240, 95, n)) / SR) * env(n, 0.002, 0.06)
    return st(x)

def fwip(d=0.22):
    n = int(d * SR); x = rng.standard_normal(n)
    x = onepole(x, 4000) - onepole(x, 900)          # jalur kertas
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 3
    x = x * e * (1 + 0.5 * np.sin(2 * np.pi * 38 * np.arange(n) / SR))  # geseran kertas
    return st(x, 0.4)

def chapter_jingle():
    out = np.zeros(int(0.8 * SR))
    for k, f in enumerate([1047, 1319, 1568]):
        x = marimba(f); i = int(k * 0.085 * SR); out[i:i + len(x)] += x[:len(out) - i]
    return st(out)

def ding(f=1568):
    n = int(0.8 * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)) * env(n, 0.001, 0.25)
    return st(x)

def glass():
    out = np.zeros(int(0.9 * SR))
    for k, f in enumerate([1568, 1976, 2349, 2637, 3136, 3951]):
        n = int(0.4 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.1)
        i = int(k * 0.04 * SR); out[i:i + n] += x * (1 - k * 0.08)
    return st(out, 0.6)

def chord():
    n = int(1.2 * SR); out = np.zeros(n)
    for f in (523, 659, 784, 1047):
        x = marimba(f, 1.2); out += x[:n]
    return st(out)

PENTA = [880, 988, 1109, 1319, 1480, 1760]
SFX = {"roll": (snare_roll(), .35), "hit": (hit(), .55), "bonk": (bonk(), .35), "fwip": (fwip(), .45),
       "jingle": (chapter_jingle(), .30), "ding": (ding(), .30), "ding2": (ding(1976), .30),
       "ding3": (ding(2349), .30), "glass": (glass(), .25), "chord": (chord(), .35)}
for i, f in enumerate(PENTA): SFX[f"m{i}"] = (st(marimba(f, 0.3)), .16)

# ---------------- Utiliti ----------------
def seg_dur(seg): return END_DUR if seg[6] == "end" else (seg[2] - seg[1]) / (seg[3] * SPEED)
def seg_start(k): return sum(seg_dur(s) for s in SEGS[:k])
def total(): return seg_start(len(SEGS))
def chap_start(tag): return seg_start(next(i for i, s in enumerate(SEGS) if s[6] == tag))

def parse_script():
    lines = []
    for chunk in SCRIPT.split("/"):
        ws = [(w.lstrip("*"), w.startswith("*")) for w in chunk.split()]
        if ws: lines.append(ws)
    return lines

def norm(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return {"ni": "ini", "nih": "ini", "hormon": "hormone", "kolagen": "collagen", "sintela": "centella",
            "tiga": "3", "tujuh": "7", "empat": "4", "enam": "6"}.get(w, w)

def ass_t(t): return f"0:{int(t // 60):02d}:{max(t, 0) % 60:05.2f}"
def run(cmd): subprocess.run(cmd, check=True)

def save_png(arr, path):
    h, w, c = arr.shape
    fmt = {1: "gray", 4: "rgba"}[c]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", fmt, "-s", f"{w}x{h}",
                    "-i", "-", path], input=arr.astype(np.uint8).tobytes(), check=True)

def rrect_mask(w, h, r):
    y, x = np.mgrid[0:h, 0:w]
    cx = np.clip(x, r, w - 1 - r); cy = np.clip(y, r, h - 1 - r)
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    return np.clip(r - d + 0.5, 0, 1)

def box_blur(a, k):
    for axis in (0, 1):
        c = np.cumsum(np.pad(a, [(k, k) if i == axis else (0, 0) for i in range(2)], mode="edge"), axis=axis)
        a = (np.take(c, range(2 * k, c.shape[axis]), axis=axis) - np.take(c, range(0, c.shape[axis] - 2 * k), axis=axis)) / (2 * k)
    return a

def make_assets():
    m = rrect_mask(PW, PH, 22); save_png((m * 255)[..., None], "_mask.png")
    sw, sh = PW + 120, PH + 120
    s = np.zeros((sh, sw)); s[60:60 + PH, 60:60 + PW] = rrect_mask(PW, PH, 22)
    for _ in range(3): s = box_blur(s, 14)
    sh_img = np.zeros((sh, sw, 4)); sh_img[..., :3] = (60, 20, 50); sh_img[..., 3] = s * 255 * 0.38
    save_png(sh_img, "_shadow.png")
    W, H = 1200, 2040; dots = np.zeros((H, W, 4)); dots[..., :3] = 255
    y, x = np.mgrid[0:H, 0:W]; a = np.zeros((H, W))
    for _ in range(70):
        cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(8, 30)
        a = np.maximum(a, np.clip((r - np.sqrt((x - cx) ** 2 + (y - cy) ** 2)) / 3, 0, 1) * rng.uniform(0.25, 0.5))
    dots[..., 3] = a * 255; save_png(dots, "_dots.png")

# ---------------- Pass 1: isi video + suara ----------------
def render_base(inputs, out):
    parts, labels = [], ""
    for i, seg in enumerate(SEGS):
        inp, s, e, sp, z0, z1, tag = seg
        sp2 = sp * SPEED; d = seg_dur(seg)
        z = f"({z0}+({z1}-{z0})*t/{d:.3f})"
        crop = (f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame,"
                f"crop=1080:{SRC_H}:x='(iw-1080)/2':y='ih*{SRC_CY}/1920-{SRC_H / 2}',scale={CW}:{CH},setsar=1")
        if tag == "end":
            parts.append(f"[{inp}:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30,tpad=stop_mode=clone:stop_duration={d + 0.2},"
                         f"trim=0:{d:.3f},setpts=PTS-STARTPTS,{crop.replace(z, '1')}[v{i}]")
            parts.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{d:.3f}[a{i}]")
        else:
            parts.append(f"[{inp}:v]trim={s}:{e},setpts=(PTS-STARTPTS)/{sp2},fps=30,{crop}[v{i}]")
            f = min(0.015, d / 4)
            parts.append(f"[{inp}:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={sp2},"
                         f"aformat=sample_rates=44100:channel_layouts=stereo,"
                         f"afade=t=in:d={f:.3f},afade=t=out:st={d - f:.3f}:d={f:.3f}[a{i}]")
        labels += f"[v{i}][a{i}]"
    parts.append(f"{labels}concat=n={len(SEGS)}:v=1:a=1[cv][ca]")
    parts.append("[cv]eq=saturation=1.1:contrast=1.03:brightness=0.02,colorbalance=rs=0.03:bs=0.02[vout]")
    parts.append("[ca]loudnorm=I=-15:TP=-2:LRA=11,aresample=44100[aout]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in inputs: cmd += ["-i", p]
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", out]
    run(cmd)

# ---------------- Penyelarasan perkataan (Whisper) ----------------
def align(video, lines):
    from faster_whisper import WhisperModel
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio, language="ms", word_timestamps=True, beam_size=5)
    heard = [(norm(w.word), w.start, w.end) for s in segs for w in s.words]
    words = [w for l in lines for w in l]
    mine = [(i, norm(t)) for i, (w, _) in enumerate(words) for t in w.split("-") if norm(t)]
    sm = difflib.SequenceMatcher(a=[m[1] for m in mine], b=[h[0] for h in heard], autojunk=False)
    times = [[None, None] for _ in words]
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            i = mine[a + k][0]
            if times[i][0] is None: times[i][0] = heard[b + k][1]
            times[i][1] = heard[b + k][2]
    known = [i for i, t in enumerate(times) if t[0] is not None]
    for i, t in enumerate(times):
        if t[0] is None:
            p = max([j for j in known if j < i], default=None); q = min([j for j in known if j > i], default=None)
            a = times[p][1] if p is not None else 0.0
            b = times[q][0] if q is not None else chap_start("end")
            gap = [j for j in range(len(times)) if (p is None or j > p) and (q is None or j < q)]
            k = gap.index(i); step = (b - a) / len(gap)
            t[0], t[1] = a + k * step, a + (k + 1) * step
    print(f"  padanan {sum(n for *_, n in sm.get_matching_blocks())}/{len(mine)} token")
    return times

# ---------------- ASS: sarikata dalam polaroid ----------------
POL_HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PW}
PlayResY: {PH}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Lilita One,74,&H008A3EFF,&H002E1B2B,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,50,50,0,1
Style: Tag,Lilita One,30,&H00A89BA6,&H00A89BA6,&H00FFFFFF,&H00000000,0,0,0,0,100,100,2,0,1,0,0,3,0,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def build_polaroid_ass(lines, times, path):
    ev = []; words = [w for l in lines for w in l]; idx = 0
    end0 = chap_start("end"); cy = STRIP_Y + (PH - STRIP_Y) // 2 - 8
    for line in lines:
        first, last = idx, idx + len(line) - 1
        line_end = times[last + 1][0] if last + 1 < len(words) else end0
        line_end = min(line_end, times[last][1] + 0.7, end0)
        s = times[first][0]
        txt = ""
        for k, (w, key) in enumerate(line):
            nxt = times[first + k + 1][0] if k < len(line) - 1 else min(times[last][1], line_end)
            cs = max(1, int(round((nxt - times[first + k][0]) * 100)))
            col = r"\1c&H00007AFF&" if key else r"\1c&H008A3EFF&"
            txt += "{" + col + rf"\kf{cs}" + "}" + w.upper() + " "
        squash = rf"{{\pos({PW // 2},{cy})\fscx125\fscy70\t(0,90,\fscx94\fscy110)\t(90,190,\fscx100\fscy100)}}"
        ev.append(f"Dialogue: 1,{ass_t(s)},{ass_t(line_end)},Cap,,0,0,0,,{squash}{txt.strip()}")
        idx = last + 1
    ev.append(f"Dialogue: 0,{ass_t(0)},{ass_t(total())},Tag,,0,0,0,,{{\\pos({PW - 36},{PH - 18})}}#racuntiktok")
    open(path, "w").write(POL_HEAD + "\n".join(ev) + "\n")

# ---------------- ASS: kanvas (tajuk, recap, butang) ----------------
CAN_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,Lilita One,138,&H008A3EFF,&H00FFFFFF,&H00FFFFFF,&H502E1B2B,0,0,0,0,100,100,2,0,1,9,7,5,0,0,0,1
Style: Sub,Lilita One,62,&H002E1B2B,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,5,0,5,0,0,0,1
Style: Tab,Lilita One,58,&H00FFFFFF,&H00FFFFFF,&H002E1B2B,&H00000000,0,0,0,0,100,100,1,0,3,18,0,5,0,0,0,1
Style: Recap,Lilita One,60,&H002E1B2B,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,5,0,4,0,0,0,1
Style: Btn,Lilita One,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,0,0,0,1
Style: Draw,Lilita One,10,&H008A3EFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def rrect(w, h, r):
    k = r * 0.45
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
            f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0")

def circle(r):
    k = r * 0.552
    return (f"m 0 {-r} b {k} {-r} {r} {-k} {r} 0 b {r} {k} {k} {r} 0 {r} b {-k} {r} {-r} {k} {-r} 0 "
            f"b {-r} {-k} {-k} {-r} 0 {-r}")

CHECK = "m -20 2 l -7 15 l 20 -13 l 25 -8 l -7 24 l -25 7"
DROP = r"{\fscx70\fscy130\t(0,110,\fscx112\fscy90)\t(110,220,\fscx100\fscy100)"

def build_canvas_ass(path):
    ev = []; T = total(); end0 = chap_start("end")
    tags = [(seg_start(i), s[6]) for i, s in enumerate(SEGS) if s[6]]
    # HOOK: "3 SEBAB" + "BARANG NI VIRAL!"
    c1 = chap_start("c1")
    ev.append(f"Dialogue: 3,{ass_t(0.5)},{ass_t(c1)},Big,,0,0,0,,{{\\pos(540,220)\\fscx260\\fscy260\\alpha&H80&"
              r"\t(0,120,\fscx92\fscy92\alpha&H00&)\t(120,220,\fscx100\fscy100)\frz-3}3 SEBAB")
    ev.append(f"Dialogue: 3,{ass_t(0.75)},{ass_t(c1)},Sub,,0,0,0,,{{\\pos(540,318)\\fad(120,0)}}BARANG NI VIRAL!")
    # Tab bab
    for k, (t0, tag) in enumerate(tags):
        if tag not in HEADERS: continue
        t1 = next((t for t, g in tags[k + 1:] if g in HEADERS or g == "end"), end0)
        num, text = HEADERS[tag]
        label = (r"{\1c&H008A3EFF&}" + num + r"{\1c&H00FFFFFF&}  " + text) if num else text
        ev.append(f"Dialogue: 3,{ass_t(t0 + 0.12)},{ass_t(t1)},Tab,,0,0,0,,{{\\pos(540,282)}}{DROP}}}{label}")
    # RECAP
    ev.append(f"Dialogue: 3,{ass_t(end0 + 0.2)},{ass_t(T)},Big,,0,0,0,,{{\\pos(540,330)\\frz-3}}{DROP}}}RECAP!")
    for k, txt in enumerate(RECAP):
        t0 = end0 + 0.45 + k * 0.38; y = 560 + k * 150
        ev.append(f"Dialogue: 2,{ass_t(t0)},{ass_t(T)},Draw,,0,0,0,,{{\\pos(170,{y})\\1c&H008A3EFF&{DROP[1:]}\\p1}}{circle(42)}{{\\p0}}")
        ev.append(f"Dialogue: 3,{ass_t(t0 + 0.08)},{ass_t(T)},Draw,,0,0,0,,{{\\pos(170,{y})\\1c&HFFFFFF&\\fscx0\\fscy0\\t(0,120,\\fscx100\\fscy100)\\p1}}{CHECK}{{\\p0}}")
        ev.append(f"Dialogue: 3,{ass_t(t0)},{ass_t(T)},Recap,,0,0,0,,{{\\pos(240,{y})\\fad(100,0)\\move(280,{y},240,{y},0,150)}}{txt}")
    # BUTANG CTA + riak sentuhan + teks promo
    tb = end0 + 1.55; bw, bh = 820, 180; bx, by = 540 - bw // 2, 1080
    ev.append(f"Dialogue: 2,{ass_t(tb)},{ass_t(T)},Draw,,0,0,0,,{{\\pos({bx},{by + 14})\\1c&H2E1B2B&\\alpha&H70&\\fad(150,0)\\p1}}{rrect(bw, bh, 70)}{{\\p0}}")
    t = tb; k = 0
    while t < T:
        e = min(t + 0.5, T)
        a = (r"\fscx40\fscy40\t(0,160,\fscx108\fscy108)\t(160,280,\fscx100\fscy100)" if k == 0
             else r"\t(0,90,\fscx96\fscy96)\t(90,260,\fscx100\fscy100)")
        ev.append(f"Dialogue: 3,{ass_t(t)},{ass_t(e)},Draw,,0,0,0,,{{\\an7\\pos({bx},{by})\\org(540,{by + bh // 2})\\1c&H008A3EFF&{a}\\p1}}{rrect(bw, bh, 70)}{{\\p0}}")
        ev.append(f"Dialogue: 4,{ass_t(t)},{ass_t(e)},Btn,,0,0,0,,{{\\pos(540,{by + bh // 2})\\org(540,{by + bh // 2}){a}}}TEKAN BEG KUNING")
        ev.append(f"Dialogue: 5,{ass_t(t + 0.1)},{ass_t(min(t + 0.5, T))},Draw,,0,0,0,,{{\\pos(840,{by + 120})\\1c&HFFFFFF&"
                  rf"\alpha&H40&\fscx20\fscy20\t(0,400,\fscx160\fscy160\alpha&HFF&)\p1}}{circle(40)}{{\\p0}}")
        t = e; k += 1
    ev.append(f"Dialogue: 3,{ass_t(tb + 0.35)},{ass_t(T)},Sub,,0,0,0,,{{\\pos(540,{by + bh + 90})\\fad(150,0)}}SELLER TENGAH BUAT HARGA PROMO!")
    arrow = "m -26 0 l 26 0 l 26 80 l 62 80 l 0 150 l -62 80 l -26 80"
    t = tb + 0.5
    while t < T:
        e = min(t + 0.5, T)
        ev.append(f"Dialogue: 4,{ass_t(t)},{ass_t(e)},Draw,,0,0,0,,{{\\move(230,{by + bh + 160},200,{by + bh + 230},0,250)"
                  rf"\frz-22\1c&H00D7FF&\3c&H2E1B2B&\bord5\p1}}{arrow}{{\p0}}")
        t = e
    open(path, "w").write(CAN_HEAD + "\n".join(ev) + "\n")

# ---------------- Bunyi ----------------
def build_sfx(lines, times, path):
    track = np.zeros((int((total() + 1.5) * SR), 2))
    def put(t, name):
        x, g = SFX[name]; i = max(0, int(t * SR)); track[i:i + len(x)] += (x * g)[:len(track) - i]
    words = [w for l in lines for w in l]
    put(0.0, "roll"); put(0.5, "hit"); put(0.42, "bonk")
    for i, s in enumerate(SEGS):
        t0 = seg_start(i)
        if s[6] in ("c1", "c2", "c3", "cta"): put(t0 - 0.06, "fwip"); put(t0 + 0.15, "jingle")
        if s[6] == "end":
            put(t0 - 0.02, "fwip")
            for k, n in enumerate(["ding", "ding2", "ding3"]): put(t0 + 0.45 + k * 0.38, n)
            put(t0 + 1.55, "chord")
    idx = 0
    for li, line in enumerate(lines):                     # marimba setiap baris sarikata
        put(times[idx][0] - 0.01, f"m{li % len(PENTA)}"); idx += len(line)
    for i, (w, key) in enumerate(words):
        if norm(w) in ("hormone", "collagen", "2029", "nampak", "promo"): put(times[i][0], "glass")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype("<i2").tobytes())

# ---------------- Pass 2: komposit ----------------
def card_y():
    y = f"{CARD_Y}+5*sin(t*1.7)-1500*exp(-t*6)*abs(cos(t*7))"           # jatuh & melantun
    for i, s in enumerate(SEGS):
        if s[6] in ("c1", "c2", "c3", "cta"):
            t0 = seg_start(i); y += f"+1500*exp(-(t-{t0:.3f})*11)*gte(t\\,{t0:.3f})"   # naik dari bawah
    te = chap_start("end")
    y += f"+1800*(1-exp(-(t-{te:.3f})*7))*gte(t\\,{te:.3f})"                         # keluar ke bawah
    return y

def final(base, out):
    T = total(); Y = card_y(); fd = f"fontsdir={HERE}/fonts"
    g = (f"[0:v]pad={PW}:{PH}:26:26:white,ass=_pol.ass:{fd},format=rgba[p0];"
         f"[1:v]format=gray,loop=-1:size=1:start=0,trim=0:{T:.3f},setpts=N/30/TB[m];"
         f"[p0][m]alphamerge,rotate=a={ANGLE}:c=none:ow=rotw({ANGLE}):oh=roth({ANGLE})[pol];"
         f"[2:v]format=rgba,rotate=a={ANGLE}:c=none:ow=rotw({ANGLE}):oh=roth({ANGLE}),loop=-1:size=1:start=0,"
         f"trim=0:{T:.3f},setpts=N/30/TB[sh];"
         f"[3:v]format=rgba,loop=-1:size=1:start=0,trim=0:{T:.3f},setpts=N/30/TB[dots];"
         f"gradients=s=1080x1920:r=30:d={T:.3f}:c0=0xFFD1DC:c1=0xFFE5CC:c2=0xE8D5FF:c3=0xFFF0F5:"
         f"nb_colors=4:speed=0.012:seed=5[bg0];"
         f"[bg0][dots]overlay=x='-60+40*sin(t*0.3)':y='-60+30*cos(t*0.25)'[bg1];"
         f"[bg1][sh]overlay=x='(W-w)/2+14':y='{Y}-60+20'[bg2];"
         f"[bg2][pol]overlay=x='(W-w)/2':y='{Y}':eof_action=pass,format=yuv420p,ass=_canvas.ass:{fd}[v];"
         f"[0:a][4:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", base, "-i", "_mask.png", "-i", "_shadow.png", "-i", "_dots.png",
         "-i", "_sfx.wav", "-filter_complex", g, "-map", "[v]", "-map", "[a]", "-t", f"{T:.3f}",
         "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-maxrate", "12M", "-bufsize", "24M",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])

if __name__ == "__main__":
    os.chdir(HERE); os.makedirs("output", exist_ok=True)
    lines = parse_script()
    make_assets()
    render_base(sys.argv[1:3], "_base.mkv")
    times = align("_base.mkv", lines)
    build_polaroid_ass(lines, times, "_pol.ass")
    build_canvas_ass("_canvas.ass")
    build_sfx(lines, times, "_sfx.wav")
    final("_base.mkv", "output/unboxing-v3.mp4")
    for f in ("_base.mkv", "_sfx.wav", "_mask.png", "_shadow.png", "_dots.png"): os.remove(f)
    print(f"siap: {total():.1f}s")
