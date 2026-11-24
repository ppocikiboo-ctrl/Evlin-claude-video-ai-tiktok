"""Version 3 edit: "flash-forward" teaser + VHS rewind, then the full video
with one-word-at-a-time captions, checklist stamps, focus/scan HUD and a
lime/black colour theme.

Usage: python3 render_v3.py INPUT.mp4 OUTPUT.mp4
Reuses helpers from render.py (same folder).
"""
import math
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import render as R
from render import (BLACK, FONT_BLACK, FONT_BLACK_IT, WHITE, YELLOW, H, W, FPS,
                    ease_out, ease_out_back, emoji_img, is_emoji, pill, place,
                    pop, stack, star, text_img)

SRC, OUT = R.SRC, R.OUT
LIME = (198, 255, 0)
DARK = (12, 12, 12)
SR = 44100

# ---------------------------------------------------------------- timeline
TEASE_SRC = (12.2, 13.2)     # flash-forward: "ada 6 patches"
REW_SRC = 13.2               # rewind from here back to 0
MAIN_START = 0.55            # skip the silent first half-second
T_TEASE = 1.0
T_REW = 0.5
T_MAIN0 = T_TEASE + T_REW
OFFSET = T_MAIN0 - MAIN_START
T_MAIN1 = 19.0 + OFFSET
END_DUR = 1.8
TOTAL = T_MAIN1 + END_DUR
NF = int(round(TOTAL * FPS))
NSEQ = int(round(T_MAIN1 * FPS))


def src_of(t):
    if t < T_TEASE:
        return TEASE_SRC[0] + t
    if t < T_MAIN0:
        return None
    if t < T_MAIN1:
        return t - OFFSET
    return None


def in_rewind(t):
    return T_TEASE <= t < T_MAIN0


# ---------------------------------------------------------------- captions (one word at a time)
KEYWORDS = {"CURVE", "SCULPT", "MICRO-PATCH", "PUNGGUNG", "MICRONEEDLE", "LARUT", "6", "PATCHES",
            "3", "PASANG", "KIRI", "KANAN.", "CURIOUS", "BEG", "KUNING", "SEKARANG", "PATCH",
            "NAMPAK", "DETAIL", "LARUT."}
WORD_SIZE = 128


def word_tokens():
    """Flatten chunks into (t0, t1, word, emoji) using the per-chunk weights."""
    out = []
    for t0, t1, text in R.CHUNKS:
        words = text.split()
        ws = R.word_weights(words)
        tot = sum(ws)
        acc = 0.0
        for i, (wd, wg) in enumerate(zip(words, ws)):
            if not wg:
                if out:
                    a, b, w0, _ = out[-1]
                    out[-1] = (a, b, w0, wd)
                continue
            a = t0 + (t1 - t0) * acc / tot
            acc += wg
            b = t0 + (t1 - t0) * acc / tot
            out.append((a, b, wd, None))
    return out


TOKENS = word_tokens()
WORD_CACHE = {}


def word_img(wd, emo):
    key = (wd, emo)
    if key not in WORD_CACHE:
        col = LIME if wd.strip(",.?") in KEYWORDS or wd in KEYWORDS else WHITE
        size = WORD_SIZE if len(wd) < 10 else int(WORD_SIZE * 10 / len(wd) * 0.95) + 10
        im = text_img(wd, size, fill=col, stroke=13, path=FONT_BLACK_IT)
        if emo:
            e = emoji_img(emo, int(size * 0.9))
            both = Image.new("RGBA", (im.width + 12 + e.width, max(im.height, e.height)), (0, 0, 0, 0))
            both.alpha_composite(im, (0, (both.height - im.height) // 2))
            both.alpha_composite(e, (im.width + 12, (both.height - e.height) // 2))
            im = both
        if im.width > 1000:
            s = 1000 / im.width
            im = im.resize((1000, int(im.height * s)), Image.LANCZOS)
        WORD_CACHE[key] = im
    return WORD_CACHE[key]


def caption_at(src_t):
    for a, b, wd, emo in TOKENS:
        if a <= src_t < b + 0.12:
            nxt = [x for x in TOKENS if a < x[0] <= src_t]
            if nxt:
                continue
            k = (src_t - a) / 0.12
            s = 1.35 - 0.35 * ease_out(k)
            return word_img(wd, emo), s
    return None


# ---------------------------------------------------------------- overlays
def lime_pill(text, size=50, fg=BLACK, bg=LIME, **kw):
    return pill(text_img(text, size, fill=fg), bg, **kw)


def build_overlays():
    o = {}
    o["tease"] = lime_pill("INI DIA ISI DALAM KOTAK 😳", 54)
    o["wait"] = text_img("TUNGGU SAMPAI HABIS 👀", 56, fill=WHITE, stroke=7)
    o["rew"] = text_img("◀◀ REWIND", 60, fill=WHITE, stroke=6, path=FONT_BLACK_IT)
    o["hook"] = stack([text_img("KORANG DAH", 96, fill=WHITE, stroke=11, path=FONT_BLACK_IT),
                       text_img("TRY BELUM? 🍑", 110, fill=LIME, stroke=12, path=FONT_BLACK_IT)], gap=-8)
    o["name"] = lime_pill("CURVE SCULPT MICRO-PATCH", 40, pad_x=22, pad_y=8)
    o["scan"] = lime_pill("🔍 DETAIL CHECK", 50, fg=LIME, bg=(0, 0, 0, 200), border=LIME)
    o["scan_lines"] = [text_img(s, 46, fill=WHITE, stroke=7) for s in
                       ("ENHANCE", "LIFT", "VOLUME")]
    stamps = [(5.95, "✔ MICRONEEDLE"), (7.70, "✔ BOLEH LARUT"), (12.20, "✔ 6 PATCH"),
              (13.90, "✔ 3 PASANG"), (15.72, "✔ KIRI & KANAN")]
    o["stamps"] = [(t, pill(text_img(s, 40, fill=LIME), (0, 0, 0, 210), pad_x=22, pad_y=10,
                            radius=14, border=LIME)) for t, s in stamps]
    o["social"] = lime_pill("🔥 RAMAI DAH CHECKOUT", 50, fg=WHITE, bg=(0, 0, 0, 200), border=LIME)
    o["cta"] = pill(text_img("🛒 GRAB KAT BEG KUNING", 58, fill=BLACK), YELLOW, pad_x=44, pad_y=26,
                    border=BLACK)
    o["finger"] = emoji_img("👇", 130)
    o["end1"] = text_img("SAVE DULU VIDEO NI 📌", 76, fill=WHITE, stroke=10, path=FONT_BLACK_IT)
    o["end2"] = text_img("CURVE SCULPT", 120, fill=LIME, stroke=12, path=FONT_BLACK_IT)
    o["end3"] = text_img("MICRO-PATCH", 120, fill=WHITE, stroke=12, path=FONT_BLACK_IT)
    o["end_cta"] = pill(text_img("🛒 TEKAN BEG KUNING", 68, fill=BLACK), YELLOW, pad_x=48, pad_y=30,
                        border=LIME)
    o["end_note"] = text_img("Harga & stok terkini dalam beg kuning 💛", 40, fill=WHITE, stroke=6)
    return o


def brackets(canvas, box, t, col=LIME, label=None):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(canvas)
    L, th = 70, 10
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(x, y), (x + sx * L, y)], fill=col, width=th)
        d.line([(x, y), (x, y + sy * L)], fill=col, width=th)
    if label is not None:
        place(canvas, label, (x0 + x1) / 2, y0 - 40)


# ---------------------------------------------------------------- base FX
PUNCH_SRC = [0.55, 2.45, 5.95, 7.70, 12.20, 13.90, 15.72, 16.70]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = np.clip(1.0 - 0.35 * np.clip(_r - 0.5, 0, None) ** 1.4, 0.55, 1.0)[..., None]
SCAN = (1 - 0.06 * (np.arange(H) % 4 < 2)).astype(np.float32)[:, None, None]
rng = np.random.default_rng(11)


def zoom_at(t, st):
    z = 1.02
    if st is None:
        return 1.08
    for p in PUNCH_SRC:
        dt = st - p
        if 0 <= dt < 0.5:
            z += 0.09 * math.exp(-dt * 8)
    if t < T_TEASE:
        z += 0.06 * t
    return z


def transform(img, t, st):
    z = zoom_at(t, st)
    cw, ch = W / z, H / z
    jx = jy = 0.0
    if t < T_TEASE or in_rewind(t):
        jx, jy = 10 * math.sin(t * 83), 8 * math.cos(t * 71)
    x0 = min(max((W - cw) / 2 + jx, 0), W - cw)
    y0 = min(max((H - ch) / 2 + jy, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def grade(arr, t, st):
    a = arr.astype(np.float32)
    a = (a - 128) * 1.12 + 128
    a[..., 2] *= 1.03
    a *= VIG
    if t < T_TEASE:   # teaser: warm high contrast + scanlines
        a = (a - 128) * 1.1 + 128
        a *= SCAN
    if in_rewind(t):  # VHS: channel split, tearing, noise, desat
        g = a.mean(axis=2, keepdims=True)
        a = g + (a - g) * 0.4
        off = 14
        a[..., 0] = np.roll(a[..., 0], off, axis=1)
        a[..., 2] = np.roll(a[..., 2], -off, axis=1)
        for _ in range(6):
            y = int(rng.integers(0, H - 60))
            h = int(rng.integers(10, 60))
            a[y:y + h] = np.roll(a[y:y + h], int(rng.integers(-80, 80)), axis=1)
        a += rng.normal(0, 18, a.shape[:2])[..., None]
        a *= SCAN
    if st is not None:
        for p in (0.55, 12.20, 16.70):   # quick lime flash
            dt = st - p
            if 0 <= dt < 0.15:
                k = 0.45 * (1 - dt / 0.15)
                a = a * (1 - k) + np.array(LIME, np.float32) * k
    return a.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- per-frame overlays
def draw_overlays(canvas, t, st, O):
    if t < T_TEASE:
        s, a = pop(t, 0.0, T_TEASE + 0.01)
        place(canvas, O["tease"], W / 2, 260, s, a, rot=-3)
        if t > 0.3:
            place(canvas, O["wait"], W / 2, 390, 1.0, 0.75 + 0.25 * math.sin(t * 20))
        return
    if in_rewind(t):
        if int(t * 8) % 2 == 0:
            place(canvas, O["rew"], 60 + O["rew"].width / 2, 150)
        return

    # Hook at start of main
    s, a = pop(st, 0.55, 2.45)
    if a:
        place(canvas, O["hook"], W / 2, 380, s, a, rot=-3)

    # Focus brackets + name while product is presented
    if 2.45 <= st < 5.2:
        k = ease_out((st - 2.45) / 0.3)
        m = 120 * (1 - k)
        brackets(canvas, (150 - m, 560 - m, 930 + m, 1080 + m), t,
                 label=O["name"] if k > 0.6 else None)

    # Detail check scan (silent part)
    if 8.4 <= st < 10.95:
        s, a = pop(st, 8.4, 10.95)
        place(canvas, O["scan"], 40 + O["scan"].width / 2, 260, s, a)
        brackets(canvas, (110, 380, 970, 1080), t)
        y = 380 + ((st - 8.4) / 1.1 % 1.0) * 700
        glow = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
        ImageDraw.Draw(glow).rectangle((110, 24, 970, 34), fill=LIME + (255,))
        canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)), (0, int(y) - 30))
        canvas.alpha_composite(glow, (0, int(y) - 30))
        shown = [im for i, im in enumerate(O["scan_lines"]) if st >= 8.9 + i * 0.5]
        if shown:
            row = Image.new("RGBA", (sum(i.width for i in shown) + 50 * (len(shown) - 1), shown[0].height),
                            (0, 0, 0, 0))
            x = 0
            for im in shown:
                row.alpha_composite(im, (x, 0))
                x += im.width + 50
            place(canvas, row, W / 2, 1170, 1.0, min(1, (10.95 - st) / 0.15))

    # Checklist stamps, stacked on the right
    shown = [(t0, im) for t0, im in O["stamps"] if st >= t0 and st < 16.45]
    for i, (t0, im) in enumerate(shown):
        p = min(1.0, (st - t0) / 0.18)
        s = 1.6 - 0.6 * ease_out(p)
        a = min(1.0, p * 2, (16.45 - st) / 0.15)
        place(canvas, im, W - 40 - im.width / 2, 220 + i * 92, s, a, rot=-4 * (1 - p))

    # CTA
    s, a = pop(st, 16.45, 19.01)
    if a:
        place(canvas, O["social"], W / 2, 250, s, a, rot=-2)
    s, a = pop(st, 16.7, 19.01)
    if a:
        bounce = 1 + 0.06 * abs(math.sin((st - 16.7) * 7))
        place(canvas, O["cta"], W / 2, 1020, s * bounce, a, rot=2 * math.sin(st * 5))
        place(canvas, O["finger"], 200, 1690 + 22 * abs(math.sin((st - 16.7) * 6)), 1.0, a)


def end_card(bg, t, O):
    dt = t - T_MAIN1
    b = bg.filter(ImageFilter.GaussianBlur(min(24, 4 + dt * 70)))
    arr = np.asarray(b).astype(np.float32) * (1 - min(0.6, dt * 3))
    canvas = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    for gx in range(0, W, 90):   # lime grid
        d.line([(gx, 0), (gx, H)], fill=LIME + (int(40 * min(1, dt * 3)),), width=2)
    for gy in range(0, H, 90):
        d.line([(0, gy), (W, gy)], fill=LIME + (int(40 * min(1, dt * 3)),), width=2)
    place(canvas, O["end1"], W / 2, 420, ease_out_back(dt / 0.25), 1.0, rot=-3)
    place(canvas, O["end2"], W / 2, 650, ease_out_back((dt - 0.1) / 0.25), 1.0, rot=-3)
    place(canvas, O["end3"], W / 2, 790, ease_out_back((dt - 0.18) / 0.25), 1.0, rot=-3)
    if dt > 0.4:
        place(canvas, O["end_cta"], W / 2, 1040,
              ease_out_back((dt - 0.4) / 0.25) * (1 + 0.05 * abs(math.sin(dt * 7))), 1.0)
    if dt > 0.6:
        place(canvas, O["end_note"], W / 2, 1190, 1.0, min(1, (dt - 0.6) / 0.15))
        place(canvas, O["finger"], 200, 1690 + 24 * abs(math.sin(dt * 6)), 1.0, 1.0)
    return canvas


# ---------------------------------------------------------------- audio
def build_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-f", "s16le", "-ac", "2",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    src = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
    n = int(TOTAL * SR)
    mix = np.zeros((n, 2), np.float32)
    a, b = int(TEASE_SRC[0] * SR), int(TEASE_SRC[1] * SR)
    tease = src[a:b].copy()
    tease[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
    mix[:len(tease)] += tease
    m0 = int(MAIN_START * SR)
    main = src[m0:]
    i0 = int(T_MAIN0 * SR)
    mix[i0:i0 + len(main)] += main[:n - i0]
    g = np.random.default_rng(5)

    def add(sig, t, gain):
        i = int(t * SR)
        j = min(n, i + len(sig))
        mix[i:j] += (sig[:j - i] * gain)[:, None]

    def tone(f0, d, decay):
        tt = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * decay)

    # Rewind: reversed, sped-up chunk of the voice + tape warble
    rw = src[:int(REW_SRC * SR)][::-1, 0]
    idx = np.linspace(0, len(rw) - 1, int(T_REW * SR)).astype(int)
    rew = rw[idx] * 0.5
    tt = np.arange(len(rew)) / SR
    rew += 0.25 * np.sin(2 * np.pi * (300 + 900 * tt / T_REW) * tt) * np.sin(np.pi * tt / T_REW)
    add(rew.astype(np.float32), T_TEASE, 0.7)

    def stamp():
        m = int(0.08 * SR)
        x = g.standard_normal(m).astype(np.float32) * np.exp(-np.arange(m) / SR * 60)
        return x * 0.6 + tone(140, 0.08, 40) * 0.8

    for p in (2.45, 5.95, 7.70, 12.20, 13.90, 15.72):
        add(stamp(), p + OFFSET, 0.4)
    add(tone(110, 0.25, 12), T_MAIN0, 0.5)        # bass hit after rewind
    for i in range(3):
        add(tone(1200 + 200 * i, 0.1, 30), 8.9 + i * 0.5 + OFFSET, 0.25)
    add(tone(1568, 0.6, 6) + 0.5 * tone(2093, 0.6, 6), 16.7 + OFFSET, 0.25)
    add(tone(1760, 0.8, 5) + 0.5 * tone(2349, 0.8, 5), T_MAIN1 + 0.4, 0.3)
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


def main():
    audio_path = OUT + ".audio.wav"
    build_audio(audio_path)
    O = build_overlays()
    speed = REW_SRC / T_REW
    fc = (f"[0:v]split=3[a][b][c];"
          f"[a]trim={TEASE_SRC[0]}:{TEASE_SRC[1]},setpts=PTS-STARTPTS[t];"
          f"[b]trim=0:{REW_SRC},setpts=PTS-STARTPTS,reverse,setpts=PTS/{speed},fps={FPS}[r];"
          f"[c]trim={MAIN_START}:19,setpts=PTS-STARTPTS[m];"
          f"[t][r][m]concat=n=3:v=1:a=0,fps={FPS},scale=1080:1920:flags=lanczos,"
          f"eq=saturation=1.12[v]")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-filter_complex", fc, "-map", "[v]",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", audio_path, "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
         "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    fsz = W * H * 3
    last = None
    last_clean = None
    for i in range(NF):
        t = i / FPS
        st = src_of(t)
        if i < NSEQ:
            buf = dec.stdout.read(fsz)
            if len(buf) == fsz:
                last = Image.frombuffer("RGB", (W, H), buf)
            base = transform(R.hide_old_subs(last), t, st)
            last_clean = base
            frame = Image.fromarray(grade(np.asarray(base), t, st)).convert("RGBA")
            if st is not None:
                cap = caption_at(st)
                if cap:
                    im, s = cap
                    place(frame, im, W / 2, 1350, s, 1.0)
            draw_overlays(frame, t, st, O)
        else:
            frame = end_card(last_clean, t, O)
        enc.stdin.write(frame.convert("RGB").tobytes())
        if i % 90 == 0:
            print(f"frame {i}/{NF}", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    subprocess.run(["rm", "-f", audio_path])


if __name__ == "__main__":
    main()
