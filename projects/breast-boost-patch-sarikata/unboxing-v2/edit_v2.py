"""Video unboxing VERSI 2: gaya edit lain dari versi 1.
- Visual: gred warna hangat + grain filem + vignette, glitch RGB pada hook,
  whip-slide (kabur gerakan) semasa tukar babak, Ken Burns push-in/pull-out perlahan,
  progress bar pink di atas, sticker teks miring masuk dari tepi.
- Sarikata: font Anton (tinggi, huruf besar), perkataan muncul satu demi satu,
  perkataan terbaru hijau lime, kata kunci coral, atas jalur "frosted glass"
  (jalur ini juga menutup sarikata lama dari app).
- Bunyi: impact boom, swish pendek, bubble "bloop", sparkle, riser, coin ding.
- Hook: FLASH-FORWARD (babak "orang tak nampak" ditunjuk dulu + teks soalan cop),
  kemudian efek pita REWIND ke awal cerita.
- Penutup: kad CTA penuh (TEKAN BEG KUNING + anak panah ke link produk).
Guna: python3 edit_v2.py <klip1_hook.mp4> <klip2_cta.mp4>"""
import difflib, os, re, subprocess, sys, wave
import numpy as np

SR = 44100
SPEED = 1.10
rng = np.random.default_rng(21)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- Rancangan potongan: (input, mula, tamat, laju, zoom_mula, zoom_tamat, gaya) ----------
SEGS = [
 (1, 9.85, 11.32, 1.0, 1.12, 1.04, "teaser"),  # HOOK flash-forward: "pakai baju pun orang tak nampak"
 (1, 7.60, 11.30, 6.0, 1.04, 1.04, "rewind"),  # pita rewind (main terbalik, laju)
 (0, 0.25, 3.50, 1.0, 1.10, 1.00, "slide"),    # cerita bermula
 (0, 3.80, 7.25, 1.0, 1.12, 1.04, "slide"),    # patch 3 in 1
 (0, 7.25, 10.45, 2.2, 1.12, 1.06, "slide"),   # buka bungkusan (laju)
 (0, 10.45, 12.15, 1.0, 1.10, 1.04, ""),       # 7 keping
 (0, 12.50, 15.80, 1.0, 1.00, 1.07, ""),       # dada & punggung, kelebihan
 (0, 16.05, 18.25, 1.0, 1.12, 1.05, "slide"),  # hormone free
 (0, 18.50, 20.12, 1.0, 1.02, 1.08, ""),       # collagen, hyaluronic
 (1, 0.25, 0.92, 1.0, 1.08, 1.10, ""),         # centella
 (1, 1.20, 3.75, 1.0, 1.00, 1.06, ""),         # expiry 2029
 (1, 4.75, 7.28, 1.0, 1.12, 1.03, "slide"),    # cara guna
 (1, 7.50, 11.32, 1.0, 1.00, 1.08, ""),        # tampal 4-6 jam
 (1, 12.20, 16.00, 1.0, 1.12, 1.00, "glitch"), # CTA suara
 (1, 15.94, 16.00, 1.0, 1.00, 1.00, "endcard"), # kad CTA penutup (frame beku)
]
ENDCARD_DUR = 2.6

# ---------- Sarikata ("/" = baris baru, * = kata kunci) ----------
SCRIPT = """
Pakai baju pun / orang *tak *nampak?! /
Benda yang asyik lalu / dekat *FYP korang tu / dah sampai tangan saya! /
Ni dia, patch / *3 dalam 1! /
Satu kotak ni ada / *7 keping, / boleh guna untuk / dada dan punggung. /
Cerita pasal *kelebihannya, / dia adalah *hormone-free, / bahan dia *lembut, /
ada *collagen, / ada *hyaluronic acid / dan *centella. /
Expiry date pun masih lama, / dalam *2029! /
Cara nak guna ni / *senang saja, / bersihkan bahagian kulit, / kemudian *tampal /
*4 hingga *6 jam, / pakai baju pun / orang *tak nampak! /
Nak cuba ni? / Jangan tunggu lama, / tekan *beg *kuning sekarang! / Seller tengah buat / *harga *promo!
"""

# Sticker atas: (perkataan pencetus, teks, warna_bg BGR)
STICKERS = [("benda", "BARANG VIRAL FYP", "&H00141414"), ("hormone", "HORMONE-FREE", "&H00141414"),
            ("2029", "EXP 2029", "&H00141414"), ("tampal", "4-6 JAM SAJA", "&H00141414"),
            ("tekan", "KLIK BEG KUNING", "&H0000D7FF")]

BAND_Y, BAND_H = 1200, 300   # jalur frosted glass (tutup sarikata lama)
CAP_Y = BAND_Y + BAND_H // 2

# ---------------- Bunyi efek ----------------
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def onepole(x, fc):
    y, s, a = np.zeros_like(x), 0.0, 1 - np.exp(-2 * np.pi * fc / SR)
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y

def st(x, pan=0.5): return np.stack([x * (1 - pan) * 2 ** .5, x * pan * 2 ** .5], 1) / 1.4

def impact():
    n = int(0.7 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(np.geomspace(120, 42, n)) / SR) * env(n, 0.003, 0.22)
    m = int(0.03 * SR); crack = np.zeros(n); crack[:m] = rng.standard_normal(m) * env(m, 0.0005, 0.006)
    x = boom + 0.5 * crack; return st(x / np.abs(x).max())

def swish(d=0.2):
    n = int(d * SR); x = rng.standard_normal(n)
    x = x - onepole(x, 2500)                         # high-pass: lebih "tajam" dari whoosh v1
    e = np.linspace(0, 1, n) ** 2 * np.exp(-np.linspace(0, 1, n) * 0) ; e = e * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5
    x = x * e; x /= np.abs(x).max()
    pan = np.linspace(0.85, 0.15, n)                 # kanan -> kiri (v1 kiri -> kanan)
    return np.stack([x * (1 - pan), x * pan], 1) * 1.4

def bloop():
    n = int(0.11 * SR)
    ph = 2 * np.pi * np.cumsum(np.geomspace(260, 950, n)) / SR   # naik (v1 pop turun)
    x = np.sin(ph) * env(n, 0.004, 0.04); return st(x / np.abs(x).max())

def sparkle():
    out = np.zeros(int(0.6 * SR))
    for k, f in enumerate([2349, 2794, 3520, 4186]):
        n = int(0.35 * SR); t = np.arange(n) / SR
        i = int(k * 0.055 * SR); out[i:i + n] += np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.08) * (1 - k * 0.12)
    return st(out / np.abs(out).max(), 0.6)

def woodtick():
    n = int(0.05 * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1750 * t) * env(n, 0.0005, 0.008); return st(x / np.abs(x).max())

def riser(d=0.9):
    n = int(d * SR); x = rng.standard_normal(n)
    x = x - onepole(x, 800); e = np.linspace(0, 1, n) ** 2.5
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(300, 1400, n)) / SR) * 0.3
    x = (x / np.abs(x).max() + tone) * e; return st(x / np.abs(x).max())

def coin():
    out = np.zeros(int(0.7 * SR))
    for i0, f, d in [(0, 988, 0.08), (0.08, 1319, 0.5)]:
        n = int((d + 0.3) * SR); t = np.arange(n) / SR
        sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t) * 0.5
        sq = onepole(sq, 5000) * env(n, 0.001, d)
        i = int(i0 * SR); out[i:i + n] += sq[:len(out) - i]
    return st(out / np.abs(out).max())

def rewind_snd(d=0.62):
    n = int(d * SR); t = np.arange(n) / SR
    f = 900 + 600 * np.sin(2 * np.pi * 13 * t) + np.linspace(0, 900, n)   # pita berputar laju
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    x = onepole(saw, 3500) * 0.6 + rng.standard_normal(n) * 0.15
    x *= np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.04)
    return st(x / np.abs(x).max())

def tape_stop(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    f = np.geomspace(700, 40, n); saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    x = onepole(saw, 1800) * (1 - t / d); return st(x / np.abs(x).max())

SFX = {"rewind": (rewind_snd(), .30), "tapestop": (tape_stop(), .30), "impact": (impact(), .55), "swish": (swish(), .40), "bloop": (bloop(), .30),
       "sparkle": (sparkle(), .22), "tick": (woodtick(), .22), "riser": (riser(), .25), "coin": (coin(), .40)}

# ---------------- Utiliti ----------------
def seg_dur(seg):
    if seg[6] == "endcard": return ENDCARD_DUR
    return (seg[2] - seg[1]) / (seg[3] * SPEED)
def seg_start(k): return sum(seg_dur(s) for s in SEGS[:k])
def total(): return seg_start(len(SEGS))

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

def ass_t(t): return f"0:{int(t // 60):02d}:{t % 60:05.2f}"

def run(cmd): subprocess.run(cmd, check=True)

# ---------------- Pass 1: visual + suara ----------------
def render_base(inputs, out):
    parts, labels = [], ""
    for i, seg in enumerate(SEGS):
        inp, s, e, sp, z0, z1, style = seg
        sp2 = sp * SPEED; d = seg_dur(seg)
        silent = f"anullsrc=r=44100:cl=stereo,atrim=0:{d:.3f}[a{i}]"
        if style == "endcard":
            parts.append(f"[{inp}:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30,"
                         f"tpad=stop_mode=clone:stop_duration={d + 0.2},trim=0:{d:.3f},setpts=PTS-STARTPTS,"
                         f"gblur=sigma=16,eq=brightness=-0.22:saturation=0.8,setsar=1[v{i}]")
            parts.append(silent); labels += f"[v{i}][a{i}]"; continue
        if style == "rewind":
            parts.append(f"[{inp}:v]trim={s}:{e},setpts=PTS-STARTPTS,reverse,setpts=PTS/{sp2},fps=30,"
                         f"scale=1210:2150,crop=1080:1920:'65+40*sin(t*60)':115,hue=s=0.35,"
                         f"rgbashift=rh=-18:bh=18,noise=alls=35:allf=t,setsar=1[v{i}]")
            parts.append(silent); labels += f"[v{i}][a{i}]"; continue
        z = f"({z0}+({z1}-{z0})*t/{d:.3f})"
        xoff = "0"
        if style == "slide":  xoff = "70*exp(-t*16)"                       # whip masuk dari kanan
        if style in ("glitch", "teaser"): xoff = "-12*sin(t*90)*lt(t\\,0.35)"  # gegar
        v = (f"[{inp}:v]trim={s}:{e},setpts=(PTS-STARTPTS)/{sp2},fps=30,"
             f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame,"
             f"crop=1080:1920:x='max(0\\,(iw-1080)/2-({xoff}))':y='(ih-1920)/2',setsar=1")
        if style == "slide":
            v += ",gblur=sigma=30:sigmaV=0.5:enable='lt(t,0.12)'"
        if style in ("glitch", "teaser"):
            v += ",rgbashift=rh=-14:bh=14:gv=6:enable='lt(t,0.35)'"
        parts.append(v + f"[v{i}]")
        f = min(0.015, d / 4)
        parts.append(f"[{inp}:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={sp2},"
                     f"aformat=sample_rates=44100:channel_layouts=stereo,"
                     f"afade=t=in:d={f:.3f},afade=t=out:st={d - f:.3f}:d={f:.3f}[a{i}]")
        labels += f"[v{i}][a{i}]"
    parts.append(f"{labels}concat=n={len(SEGS)}:v=1:a=1[cv][ca]")
    # gred hangat + vignette + grain
    parts.append("[cv]colorbalance=rs=0.05:gs=0.01:bs=-0.04:rm=0.03:bm=-0.02,"
                 "eq=saturation=1.08:contrast=1.06:gamma=1.02,vignette=angle=PI/8,"
                 "noise=alls=4:allf=t,split[g1][g2]")
    # jalur frosted glass
    parts.append(f"[g2]crop=1080:{BAND_H}:0:{BAND_Y},gblur=sigma=38,eq=brightness=-0.16:saturation=0.7[band]")
    parts.append(f"[g1][band]overlay=0:{BAND_Y},"
                 f"drawbox=x=0:y={BAND_Y}:w=1080:h=4:color=0xFF69B4@0.9:t=fill,"
                 f"drawbox=x=0:y={BAND_Y + BAND_H - 4}:w=1080:h=4:color=0xFF69B4@0.9:t=fill[vout]")
    parts.append("[ca]loudnorm=I=-15:TP=-2:LRA=11,aresample=44100[aout]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in inputs: cmd += ["-i", p]
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", out]
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
    # isi yang tidak dikesan dengan interpolasi
    known = [i for i, t in enumerate(times) if t[0] is not None]
    for i, t in enumerate(times):
        if t[0] is None:
            p = max([j for j in known if j < i], default=None); q = min([j for j in known if j > i], default=None)
            a = times[p][1] if p is not None else 0.0
            b = times[q][0] if q is not None else total()
            gap = [j for j in range(len(times)) if (p is None or j > p) and (q is None or j < q)]
            k = gap.index(i); step = (b - a) / len(gap)
            t[0], t[1] = a + k * step, a + (k + 1) * step
    print(f"  padanan {sum(n for *_, n in sm.get_matching_blocks())}/{len(mine)} token")
    return times

# ---------------- Sarikata + overlay (ASS) ----------------
HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1.5,0,1,3,5,5,40,40,0,1
Style: Stk,Poppins ExtraBold,58,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,-1,0,0,100,100,1,0,3,20,0,5,40,40,0,1
Style: Hook,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00B469FF,&H00000000,0,0,0,0,100,100,1,0,3,22,0,5,40,40,0,1
Style: Vhs,JetBrains Mono ExtraBold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,3,0,7,0,0,0,1
Style: End1,Poppins ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,-1,0,0,100,100,1,0,1,4,4,5,40,40,0,1
Style: End2,Anton,132,&H00141414,&H00FFFFFF,&H0000D7FF,&H00000000,0,0,0,0,100,100,1,0,3,30,0,5,40,40,0,1
Style: End3,Anton,70,&H00FFFFFF,&H00FFFFFF,&H00B469FF,&H00000000,0,0,0,0,100,100,1,0,3,18,0,5,40,40,0,1
Style: Arrow,Anton,10,&H0000D7FF,&H00FFFFFF,&H00141414,&H00000000,0,0,0,0,100,100,0,0,1,6,0,7,0,0,0,1
Style: Bar,Anton,10,&H00B469FF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
LIME, CORAL, WHITE = r"\c&H3BFFB6&", r"\c&H5B5EFF&", r"\c&HFFFFFF&"

def build_ass(lines, times, path):
    ev = []
    end0 = seg_start(len(SEGS) - 1)                    # mula kad CTA
    teaser_end = seg_start(1); rew_end = seg_start(2)
    # HOOK: teks soalan "cop" (masuk besar + kabur -> tepat), 2 baris
    stamp = r"{\fscx260\fscy260\blur12\alpha&H60&\t(0,140,\fscx100\fscy100\blur0\alpha&H00&)\t(140,220,\fscx108\fscy108)\t(220,300,\fscx100\fscy100)"
    ev.append(f"Dialogue: 5,{ass_t(0.0)},{ass_t(teaser_end)},Hook,,0,0,0,,{stamp}\\frz-3\\pos(540,430)}}TAMPAL 4-6 JAM...")
    ev.append(f"Dialogue: 5,{ass_t(0.35)},{ass_t(teaser_end)},Hook,,0,0,0,,{stamp}\\frz2\\3c&H141414&\\pos(540,590)}}TAPI ORANG TAK NAMPAK?")
    # REWIND: label pita berkelip
    t = teaser_end
    while t < rew_end:
        ev.append(f"Dialogue: 5,{ass_t(t)},{ass_t(min(t + 0.15, rew_end))},Vhs,,0,0,0,,{{\\pos(70,170)}}<< REWIND")
        t += 0.3
    ev.append(f"Dialogue: 5,{ass_t(rew_end)},{ass_t(rew_end + 0.9)},Vhs,,0,0,0,,{{\\pos(70,170)\\fad(0,250)}}PLAY >  MULA DARI AWAL")
    words = [w for l in lines for w in l]
    idx = 0
    for li, line in enumerate(lines):
        first = idx; last = idx + len(line) - 1
        line_end = times[last + 1][0] if last + 1 < len(words) else end0
        if last + 1 < len(words): line_end = min(line_end, times[last][1] + 0.6)
        if times[last][0] < teaser_end: line_end = min(line_end, teaser_end)   # tiada sarikata semasa rewind
        for k in range(len(line)):
            s = times[first + k][0]
            e = times[first + k + 1][0] if k < len(line) - 1 else line_end
            if e <= s: continue
            parts = []
            for j, (w, key) in enumerate(line):
                if j < k:   parts.append("{" + (CORAL if key else WHITE) + r"\alpha&H00&}" + w.upper())
                elif j == k: parts.append("{" + LIME + r"\alpha&H90&\t(0,90,\alpha&H00&)}" + w.upper())
                else:       parts.append(r"{\alpha&HFF&}" + w.upper())
            pos = (rf"{{\move(540,{CAP_Y + 34},540,{CAP_Y},0,110)}}" if k == 0 else rf"{{\pos(540,{CAP_Y})}}")
            ev.append(f"Dialogue: 2,{ass_t(s)},{ass_t(e)},Cap,,0,0,0,,{pos}" + " ".join(parts))
        idx = last + 1
    # sticker: masuk dari kanan, miring, keluar ke kiri
    for trig, text, bg in STICKERS:
        i = next(i for i, (w, _) in enumerate(words) if norm(w).startswith(trig))
        s = times[i][0]; e = min(s + 2.2, total())
        if trig == "tekan": e = end0
        col = r"\c&H141414&" if bg == "&H0000D7FF" else ""
        ev.append(f"Dialogue: 3,{ass_t(s)},{ass_t(e)},Stk,,0,0,0,,"
                  rf"{{\3c{bg}{col}\frz6\move(1300,330,540,330,0,180)\t(0,180,\frz-3)\fad(0,150)}}{text}")
    # KAD CTA PENUTUP
    T = total(); fly = r"{\fad(120,0)\move(540,%d,540,%d,0,200)}"
    ev.append(f"Dialogue: 6,{ass_t(end0)},{ass_t(T)},End1,,0,0,0,,{fly % (560, 600)}MAHU CUBA?")
    k = 0; t = end0 + 0.15
    while t < T:
        e = min(t + 0.45, T)
        a = (r"{\pos(540,790)\fscx40\fscy40\t(0,150,\fscx112\fscy112)\t(150,260,\fscx100\fscy100)}" if k == 0
             else r"{\pos(540,790)\t(0,120,\fscx107\fscy107)\t(120,280,\fscx100\fscy100)}")
        ev.append(f"Dialogue: 6,{ass_t(t)},{ass_t(e)},End2,,0,0,0,,{a}TEKAN BEG KUNING")
        t = e; k += 1
    ev.append(f"Dialogue: 6,{ass_t(end0 + 0.45)},{ass_t(T)},End3,,0,0,0,,{{\\fad(100,0)\\frz-2\\pos(540,975)}}HARGA PROMO SEKARANG!")
    # anak panah kuning melantun ke arah link produk (kiri bawah)
    arrow = "m -28 0 l 28 0 l 28 90 l 70 90 l 0 170 l -70 90 l -28 90"
    t = end0 + 0.6
    while t < T:
        e = min(t + 0.5, T)
        ev.append(f"Dialogue: 6,{ass_t(t)},{ass_t(e)},Arrow,,0,0,0,,"
                  rf"{{\move(250,1080,215,1160,0,250)\frz-20\p1}}{arrow}{{\p0}}")
        t = e
    # progress bar pink di atas
    ms = int(T * 1000)
    ev.append(f"Dialogue: 4,{ass_t(0)},{ass_t(T)},Bar,,0,0,0,,"
              rf"{{\pos(0,0)\clip(0,0,0,12)\t(0,{ms},\clip(0,0,1080,12))\p1}}m 0 0 l 1080 0 1080 12 0 12{{\p0}}")
    open(path, "w").write(HEAD + "\n".join(ev) + "\n")

def build_sfx(lines, times, path):
    track = np.zeros((int((total() + 1.5) * SR), 2))
    def put(t, name):
        x, g = SFX[name]; i = max(0, int(t * SR)); track[i:i + len(x)] += (x * g)[:len(track) - i]
    words = [w for l in lines for w in l]
    put(0, "impact")
    for k, seg in enumerate(SEGS[1:], 1):
        t0 = seg_start(k)
        if seg[6] == "rewind": put(t0 - 0.1, "tapestop"); put(t0 + 0.05, "rewind")
        elif seg[6] == "endcard": put(t0 - 0.08, "swish"); put(t0 + 0.12, "impact"); put(t0 + 0.6, "sparkle")
        elif seg[6] == "slide": put(t0 - 0.08, "swish")
        elif seg[6] == "glitch": put(t0 - 0.9, "riser"); put(t0, "impact")
    idx = 0                      # 'tick' kayu lembut setiap baris sarikata baru
    for line in lines:
        put(times[idx][0] - 0.01, "tick"); idx += len(line)
    for i, (w, key) in enumerate(words):
        n = norm(w)
        if n in ("hormone", "collagen", "2029", "nampak"): put(times[i][0], "sparkle")
        elif n == "promo": put(times[i][0], "coin")
        elif key and n not in ("harga", "kuning", "beg"): put(times[i][0], "bloop")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype("<i2").tobytes())

def final(base, ass, sfx, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", base, "-i", sfx, "-filter_complex",
         f"[0:v]ass={ass}:fontsdir={HERE}/fonts[v];"
         "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
         "-maxrate", "14M", "-bufsize", "28M",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])

if __name__ == "__main__":
    os.chdir(HERE); os.makedirs("output", exist_ok=True)
    lines = parse_script()
    render_base(sys.argv[1:3], "_base.mkv")
    times = align("_base.mkv", lines)
    build_ass(lines, times, "captions_v2.ass")
    build_sfx(lines, times, "_sfx.wav")
    final("_base.mkv", "captions_v2.ass", "_sfx.wav", "output/unboxing-v2.mp4")
    os.remove("_base.mkv"); os.remove("_sfx.wav")
    print(f"siap: {total():.1f}s")
