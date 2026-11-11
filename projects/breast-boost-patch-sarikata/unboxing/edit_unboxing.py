"""Suntingan video unboxing: gabung 2 klip, buang jeda, zoom/flash/bounce + bunyi efek.
Guna: python3 edit_unboxing.py <klip1_hook.mp4> <klip2_cta.mp4>
Sarikata sudah ada dalam video asal (dari app), jadi tiada sarikata ditambah."""
import subprocess, sys, wave
import numpy as np

SR = 44100
SPEED = 1.08          # sedikit lebih laju supaya lebih bertenaga
rng = np.random.default_rng(7)

# ---------------- Bunyi efek (dijana, bebas hak cipta) ----------------
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def lowpass_sweep(x, f0, f1):
    y, s = np.zeros_like(x), 0.0
    fs = np.geomspace(f0, f1, len(x))
    for i, v in enumerate(x):
        a = 1 - np.exp(-2 * np.pi * fs[i] / SR); s += a * (v - s); y[i] = s
    return y

def whoosh(d=0.38):
    n = int(d * SR); t = np.arange(n) / n
    x = lowpass_sweep(rng.standard_normal(n), 400, 6000)
    x -= lowpass_sweep(x, 150, 150)
    e = np.sin(np.pi * t) ** 1.5
    x = x * e / (np.abs(x).max() + 1e-9)
    pan = np.linspace(0.2, 0.8, n)          # bergerak kiri -> kanan
    return np.stack([x * (1 - pan), x * pan], 1) * 1.6

def pop(f0=1100, f1=320, d=0.09):
    n = int(d * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(np.geomspace(f0, f1, n)) / SR
    x = np.sin(ph) * env(n, 0.002, 0.03)
    return np.stack([x, x], 1)

def tick(count=2, gap=0.07):
    n = int(0.012 * SR); click = rng.standard_normal(n) * env(n, 0.0005, 0.002)
    click = np.diff(np.concatenate([[0], click]))     # high-pass ringkas
    click = click + 0.6 * np.sin(2 * np.pi * 3200 * np.arange(n) / SR) * env(n, 0.0005, 0.003)
    out = np.zeros(int((gap * count + 0.02) * SR))
    for k in range(count):
        i = int(k * gap * SR); out[i:i + n] += click * (1 if k == 0 else 0.8)
    out /= np.abs(out).max()
    return np.stack([out, out], 1) * 0.8

def wup(f0=280, f1=1300, d=0.16):
    n = int(d * SR)
    ph = 2 * np.pi * np.cumsum(np.geomspace(f0, f1, n)) / SR
    x = np.sin(ph) * np.sin(np.pi * np.arange(n) / n)
    return np.stack([x, x], 1) * 0.6

def kaching():
    n = int(0.9 * SR); t = np.arange(n) / SR
    ka = np.zeros(n); m = int(0.04 * SR)
    ka[:m] = rng.standard_normal(m) * env(m, 0.001, 0.01)
    bell = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(2093, 1), (2637, .7), (3136, .5), (4186, .3)])
    d = int(0.07 * SR); bell[:d] = 0
    bell[d:] *= env(n - d, 0.002, 0.25)
    x = 0.5 * ka + 0.5 * bell
    x /= np.abs(x).max()
    return np.stack([x, x], 1) * 0.8

SFX = {"whoosh": whoosh(), "pop": pop(), "tick": tick(), "wup": wup(), "kaching": kaching(),
       "pop_hi": pop(1600, 600, 0.07)}
GAIN = {"whoosh": 0.45, "pop": 0.35, "pop_hi": 0.3, "tick": 0.4, "wup": 0.3, "kaching": 0.5}

# ---------------- Rancangan suntingan ----------------
# (input, mula, tamat, laju, zoom, gaya, [(masa_sumber, sfx), ...])
# gaya: "bounce" = zoom masuk melantun, "flash" = kilat putih, "push" = zoom perlahan
SEGS = [
 (0, 0.25, 3.50, 1.0, 1.00, "bounce", [(1.40, "pop"), (2.90, "pop_hi")]),                 # HOOK: FYP, tangan
 (0, 3.80, 7.25, 1.0, 1.12, "flash",  [(4.25, "pop")]),                                   # patch 3 in 1
 (0, 7.25, 10.45, 2.0, 1.00, "push",  [(7.6, "tick"), (8.6, "tick"), (9.6, "wup")]),      # unboxing (2x laju)
 (0, 10.45, 12.15, 1.0, 1.12, "",     [(11.28, "pop")]),                                  # 7 keping
 (0, 12.50, 15.80, 1.0, 1.00, "",     [(15.10, "pop_hi")]),                               # dada & punggung, kelebihan
 (0, 16.05, 18.25, 1.0, 1.12, "",     [(16.30, "pop")]),                                  # hormone free
 (0, 18.50, 20.12, 1.0, 1.00, "",     [(18.55, "pop"), (19.30, "pop")]),                  # collagen, hyaluronic
 (1, 0.25, 0.92, 1.0, 1.12, "",       [(0.40, "pop")]),                                   # centella
 (1, 1.20, 3.75, 1.0, 1.00, "",       [(2.62, "tick")]),                                  # expiry 2029
 (1, 4.75, 7.28, 1.0, 1.12, "flash",  []),                                                # cara guna
 (1, 7.50, 11.32, 1.0, 1.00, "",      [(7.95, "pop"), (8.70, "tick"), (10.95, "pop_hi")]),# tampal 4-6 jam, tak nampak
 (1, 12.20, 15.70, 1.0, 1.06, "bounce", [(13.58, "pop"), (15.12, "kaching")]),            # CTA
]

def out_time(idx, t_src):
    pos = sum((e - s) / (sp * SPEED) for _, s, e, sp, *_ in SEGS[:idx])
    _, s, _, sp, *_ = SEGS[idx]
    return pos + (t_src - s) / (sp * SPEED)

def build_sfx(total):
    track = np.zeros((int((total + 1) * SR), 2))
    def put(t, name):
        x = SFX[name] * GAIN[name]; i = max(0, int(t * SR)); track[i:i + len(x)] += x[:len(track) - i]
    for k, seg in enumerate(SEGS):
        start = out_time(k, seg[1])
        if k > 0 and seg[5] in ("flash", "bounce"): put(max(0, start - 0.18), "whoosh")
        elif k > 0: put(max(0, start - 0.03), "wup" if k % 2 else "pop_hi")
        for t, name in seg[6]: put(out_time(k, t) - 0.02, name)
    put(0, "whoosh")
    track = np.clip(track, -1, 1)
    with wave.open("sfx_track.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype("<i2").tobytes())

# ---------------- Teks overlay (ASS) ----------------
def ass_time(t):
    return f"0:{int(t // 60):02d}:{t % 60:05.2f}"

def build_overlay(total):
    cta = out_time(len(SEGS) - 1, 13.30); promo = out_time(len(SEGS) - 1, 15.05)
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pink,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00B469FF,&H00000000,-1,0,0,0,100,100,2,0,3,22,0,8,40,40,330,1
Style: Yellow,Inter Black,84,&H00141414,&H00FFFFFF,&H0000D7FF,&H00000000,-1,0,0,0,100,100,1,0,3,24,0,8,40,40,330,1
Style: Promo,Inter Black,70,&H00FFFFFF,&H00FFFFFF,&H00B469FF,&H00000000,-1,0,0,0,100,100,1,0,3,18,0,8,40,40,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    pop_in = r"{\fscx30\fscy30\t(0,140,\fscx115\fscy115)\t(140,240,\fscx100\fscy100)"
    ev = [
        f"Dialogue: 1,{ass_time(0.05)},{ass_time(2.6)},Pink,,0,0,0,,{pop_in}\\frz-4}}VIRAL DI FYP!",
    ]
    # TEKAN BEG KUNING: muncul + berdenyut setiap 0.5s
    t = cta; k = 0
    while t < total:
        e = min(t + 0.5, total)
        anim = pop_in + "}" if k == 0 else r"{\t(0,120,\fscx108\fscy108)\t(120,300,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 1,{ass_time(t)},{ass_time(e)},Yellow,,0,0,0,,{anim}TEKAN BEG KUNING ↓")
        t = e; k += 1
    ev.append(f"Dialogue: 1,{ass_time(promo)},{ass_time(total)},Promo,,0,0,0,,{pop_in}\\frz3}}HARGA PROMO!")
    open("overlay.ass", "w").write(head + "\n".join(ev) + "\n")

# ---------------- Render ----------------
def render(inputs, out):
    parts, labels = [], ""
    for i, (inp, s, e, sp, z, style, _) in enumerate(SEGS):
        sp2 = sp * SPEED; d = (e - s) / sp2
        if style == "bounce":   zexpr = f"{z}+0.30*exp(-t*9)*cos(t*18)"
        elif style == "push":   zexpr = f"{z}+0.10*t/{d:.3f}"
        else:                   zexpr = f"{z}"
        v = (f"[{inp}:v]trim={s}:{e},setpts=(PTS-STARTPTS)/{sp2},fps=30,"
             f"scale=w='trunc(1080*({zexpr})/2)*2':h='trunc(1920*({zexpr})/2)*2':eval=frame,"
             f"crop=1080:1920:(iw-1080)/2:(ih-1920)/2,setsar=1")
        if style == "flash": v += ",fade=t=in:st=0:d=0.18:color=white"
        parts.append(v + f"[v{i}]")
        f = min(0.015, d / 4)
        parts.append(f"[{inp}:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={sp2},aformat=sample_rates=44100:channel_layouts=stereo,"
                     f"afade=t=in:d={f:.3f},afade=t=out:st={d - f:.3f}:d={f:.3f}[a{i}]")
        labels += f"[v{i}][a{i}]"
    parts.append(f"{labels}concat=n={len(SEGS)}:v=1:a=1[cv][ca]")
    parts.append("[cv]eq=saturation=1.12:contrast=1.04,ass=overlay.ass[vout]")
    parts.append("[ca]loudnorm=I=-15:TP=-2:LRA=11,aresample=44100[voice]")
    parts.append("[voice][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in inputs: cmd += ["-i", p]
    cmd += ["-i", "sfx_track.wav", "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    total = sum((e - s) / (sp * SPEED) for _, s, e, sp, *_ in SEGS)
    build_sfx(total); build_overlay(total)
    import os; os.makedirs("output", exist_ok=True)
    render(sys.argv[1:3], "output/unboxing-efek.mp4")
    print(f"siap: {total:.1f}s")
