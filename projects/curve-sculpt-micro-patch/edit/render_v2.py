"""Version 2 edit: "barang FYP / unboxing" style with pink-white captions,
light-leak transitions, a retention progress bar, a "kenapa ramai checkout"
card, a count-up sticker, a shining CTA button and a product-card end screen.

Usage: python3 render_v2.py INPUT.mp4 OUTPUT.mp4
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
SRC_DUR = 19.0
END_DUR = 2.0
TOTAL = SRC_DUR + END_DUR
NF = int(round(TOTAL * FPS))
NSRC = int(round(SRC_DUR * FPS))
SR = 44100

PINK = (255, 46, 122)
SOFT_PINK = (255, 214, 230)
DEEP = (40, 10, 30)

# ---------------------------------------------------------------- captions
CHUNKS = R.CHUNKS
CAP_SIZE = 74
CAP_Y = 1345


def build_caption(words, active):
    toks = []
    for i, wd in enumerate(words):
        if any(is_emoji(c) for c in wd):
            toks.append(text_img(wd, int(CAP_SIZE * 1.0)))
        else:
            toks.append(text_img(wd, CAP_SIZE, fill=PINK if i == active else BLACK))
    lines, cur, cw = [], [], 0
    for im in toks:
        add = im.width + (16 if cur else 0)
        if cur and cw + add > 860:
            lines.append(cur)
            cur, cw = [], 0
            add = im.width
        cur.append(im)
        cw += add
    lines.append(cur)
    rows = []
    for ln in lines:
        lh = max(i.height for i in ln)
        lw = sum(i.width for i in ln) + 16 * (len(ln) - 1)
        L = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        x = 0
        for im in ln:
            L.alpha_composite(im, (x, (lh - im.height) // 2))
            x += im.width + 16
        rows.append(pill(L, (255, 255, 255, 245), pad_x=30, pad_y=10, radius=26))
    return stack(rows, gap=-14)


CAP_CACHE = {}


def caption_frame(t):
    exact = [c for c in CHUNKS if c[0] <= t < c[1]]
    linger = [c for c in CHUNKS if c[1] <= t < c[1] + 0.2]
    for idx, (t0, t1, text) in enumerate((exact or linger)[:1]):
        words = text.split()
        ws = R.word_weights(words)
        tot = sum(ws)
        rel = (min(t, t1) - t0) / (t1 - t0) * tot
        acc, active = 0.0, None
        for i, wgt in enumerate(ws):
            if wgt and acc <= rel < acc + wgt:
                active = i
            acc += wgt
        if active is None:
            active = max(i for i, wgt in enumerate(ws) if wgt)
        key = (text, active)
        if key not in CAP_CACHE:
            CAP_CACHE[key] = build_caption(words, active)
        p = ease_out((t - t0) / 0.16)
        a = p if t < t1 else max(0.0, 1 - (t - t1) / 0.2)
        rot = 2.0 if CHUNKS.index((t0, t1, text)) % 2 == 0 else -2.0
        return CAP_CACHE[key], (1 - p) * 40, a, rot
    return None


# ---------------------------------------------------------------- overlays
def shine(im, t, period=1.3):
    """Diagonal light sweep across an RGBA pill."""
    ph = (t % period) / period
    w, h = im.size
    band = Image.new("L", (w, h), 0)
    cx = -200 + ph * (w + 400)
    ImageDraw.Draw(band).polygon([(cx - 60, h), (cx + 10, 0), (cx + 70, 0), (cx, h)], fill=150)
    band = band.filter(ImageFilter.GaussianBlur(6))
    band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(im.getchannel("A"))))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    white.putalpha(band)
    out = im.copy()
    out.alpha_composite(white)
    return out


def build_overlays():
    o = {}
    o["tag"] = pill(text_img("📦 REAL UNBOXING", 40, fill=WHITE), (0, 0, 0, 170), pad_x=22, pad_y=10)
    a = text_img("BARANG YANG ASYIK", 78, fill=WHITE, stroke=9, path=FONT_BLACK_IT)
    b = text_img("LALU FYP KORANG 👀", 78, fill=WHITE, stroke=9, path=FONT_BLACK_IT)
    o["hook1"] = stack([a, b], gap=-6)
    o["hook2"] = pill(text_img("AKHIRNYA SAMPAI TANGAN! 😍", 56, fill=WHITE), PINK, border=WHITE)
    o["name"] = pill(text_img("CURVE SCULPT MICRO-PATCH 🍑", 46, fill=PINK), (255, 255, 255, 240),
                     border=PINK)
    o["needle"] = pill(text_img("💧 MICRONEEDLE LARUT", 44, fill=WHITE), (0, 0, 0, 180))

    o["why"] = pill(text_img("KENAPA RAMAI CHECKOUT? 🛒", 54, fill=WHITE), PINK, pad_x=30, pad_y=14,
                    radius=24)
    items = ["ENHANCE • LIFT • VOLUME", "MICRONEEDLE BOLEH LARUT 💧", "6 PATCH = 3 PASANG ✨"]
    rows = []
    for i, s in enumerate(items):
        num = pill(text_img(str(i + 1), 46, fill=WHITE), PINK, pad_x=18, pad_y=4, shadow=False)
        txt = text_img(s, 44, fill=BLACK)
        row = Image.new("RGBA", (num.width + 14 + txt.width, max(num.height, txt.height)), (0, 0, 0, 0))
        row.alpha_composite(num, (0, (row.height - num.height) // 2))
        row.alpha_composite(txt, (num.width + 14, (row.height - txt.height) // 2))
        rows.append(pill(row, (255, 255, 255, 245), pad_x=18, pad_y=8, radius=28))
    o["why_rows"] = rows

    o["count"] = {n: text_img(str(n), 230, fill=WHITE, stroke=14, stroke_fill=PINK, path=FONT_BLACK_IT)
                  for n in range(1, 7)}
    o["count_lbl"] = pill(text_img("PATCH DALAM 1 KOTAK", 44, fill=WHITE), PINK, pad_x=24, pad_y=10)

    o["cta"] = pill(text_img("🛒 CHECKOUT KAT BEG KUNING", 54, fill=BLACK), YELLOW,
                    pad_x=40, pad_y=26, border=WHITE)
    o["cta_top"] = pill(text_img("💛 Klik beg kuning bawah ni", 44, fill=WHITE), (0, 0, 0, 180),
                        pad_x=24, pad_y=10)
    o["finger"] = emoji_img("👇", 130)

    o["end_head"] = text_img("PATCH FYP NI 👀", 96, fill=WHITE, stroke=10, path=FONT_BLACK_IT)
    o["end_sub"] = pill(text_img("ENHANCE • LIFT • VOLUME", 44, fill=PINK), WHITE, pad_x=26, pad_y=10)
    o["end_cta"] = pill(text_img("🛒 CHECKOUT SEKARANG", 66, fill=BLACK), YELLOW,
                        pad_x=46, pad_y=30, border=WHITE)
    o["end_note"] = text_img("Harga & stok terkini dalam beg kuning 💛", 40, fill=WHITE, stroke=6)
    return o


# ---------------------------------------------------------------- base FX
PUNCHES = [(0.0, 0.08), (2.45, 0.10), (8.40, 0.06), (12.20, 0.10), (16.70, 0.08)]
LEAKS = [0.0, 2.45, 8.40, 12.20, 16.70]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = np.clip(1.0 - 0.22 * np.clip(_r - 0.6, 0, None) ** 1.5, 0.7, 1.0)[..., None]


def zoom_at(t):
    z = 1.03 + 0.015 * math.sin(t * 0.9)
    for p, a in PUNCHES:
        dt = t - p
        if 0 <= dt < 0.6:
            z += a * math.exp(-dt * 6.0)
    return z


def crop_zoom(img, z, dx=0.0, dy=0.0):
    cw, ch = W / z, H / z
    x0 = min(max((W - cw) / 2 + dx, 0), W - cw)
    y0 = min(max((H - ch) / 2 + dy, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def transform(img, t):
    z = zoom_at(t)
    drift = (6 * math.sin(t * 1.3), 5 * math.cos(t * 1.1))
    out = crop_zoom(img, z, *drift)
    for p, _ in PUNCHES:
        dt = t - p
        if 0 <= dt < 0.12:  # zoom blur on the punch
            k = 1 - dt / 0.12
            layers = [np.asarray(crop_zoom(img, z * (1 + 0.035 * k * j), *drift), np.float32)
                      for j in range(1, 4)]
            arr = (np.asarray(out, np.float32) + sum(layers)) / 4
            out = Image.fromarray(arr.astype(np.uint8))
    return out


def light_leak(a, t):
    for t0 in LEAKS:
        dt = t - t0
        if 0 <= dt < 0.55:
            p = dt / 0.55
            cx = -300 + p * (W + 600)
            cy = 500 + 500 * p
            d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 0.6) ** 2)
            g = np.clip(1 - d / 700, 0, 1) ** 2 * math.sin(p * math.pi) * 0.85
            col = np.array([255, 120, 160], np.float32)
            a = 255 - (255 - a) * (1 - g[..., None] * col / 255)  # screen blend
    return a


def grade(arr, t):
    a = arr.astype(np.float32)
    a = a * 0.94 + 12          # lifted, softer blacks
    a[..., 0] *= 1.04
    a[..., 2] *= 1.02
    a *= VIG
    a = light_leak(a, t)
    return a.clip(0, 255).astype(np.uint8)


def progress_bar(canvas, t):
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 0, W, 12), fill=(255, 255, 255, 90))
    d.rectangle((0, 0, int(W * min(1, t / SRC_DUR)), 12), fill=PINK)


# ---------------------------------------------------------------- overlays per frame
def draw_overlays(canvas, t, O):
    if t < 8.4:
        place(canvas, O["tag"], 40 + O["tag"].width / 2, 120, 1.0, min(1, t / 0.2, (8.4 - t) / 0.2))

    # Hook
    if t < 2.45:
        a = min(1.0, (2.45 - t) / 0.12)
        p = ease_out(t / 0.25)
        place(canvas, O["hook1"], W / 2, 330 - (1 - p) * 60, 1.0, a * p)
        s, a2 = pop(t, 0.75, 2.45)
        if a2:
            place(canvas, O["hook2"], W / 2, 520, s, a2, rot=-3)

    # Product name and microneedle chip
    if 2.45 <= t < 8.4:
        p = ease_out((t - 2.45) / 0.35)
        a = min(1.0, (8.4 - t) / 0.2)
        place(canvas, O["name"], W + 400 - p * (W / 2 + 400), 230, 1.0, a)
    s, a = pop(t, 6.65, 8.4)
    if a:
        place(canvas, O["needle"], W / 2, 1060, s, a)

    # "Kenapa ramai checkout" card
    if 8.4 <= t < 10.95:
        s, a = pop(t, 8.4, 10.95)
        place(canvas, O["why"], W / 2, 280, s, a)
        for i, row in enumerate(O["why_rows"]):
            t0 = 8.8 + i * 0.5
            if t >= t0:
                p = ease_out_back((t - t0) / 0.3)
                a2 = min(1.0, (10.95 - t) / 0.15)
                place(canvas, row, W + 500 - p * (W / 2 + 500), 410 + i * 120, 1.0, a2)

    # Count-up 1..6
    if 12.2 <= t < 14.7:
        n = min(6, 1 + int((t - 12.2) / 0.07))
        s = 1.0 + (0.25 * math.exp(-(t - 12.62) * 8) if t >= 12.62 else 0)
        a = min(1.0, (14.7 - t) / 0.15)
        place(canvas, O["count"][n], W / 2, 330, s, a, rot=-4)
        place(canvas, O["count_lbl"], W / 2, 520, 1.0, a, rot=-4)
        d = ImageDraw.Draw(canvas)
        for (x, y, r, ph) in R.SPARKLES:
            tw = 0.5 + 0.5 * math.sin(t * 6 + ph * 6.28)
            star(d, x, y * 0.6 + 120, r * (0.4 + 0.8 * tw), 0.8 * tw * a)

    # CTA
    s, a = pop(t, 16.45, SRC_DUR + 0.01)
    if a:
        place(canvas, O["cta_top"], W / 2, 250, s, a)
    s, a = pop(t, 16.7, SRC_DUR + 0.01)
    if a:
        btn = shine(O["cta"], t - 16.7)
        place(canvas, btn, W / 2, 1040, s * (1 + 0.04 * math.sin((t - 16.7) * 8)), a)
        place(canvas, O["finger"], 200, 1690 + 22 * abs(math.sin((t - 16.7) * 6)), 1.0, a)


def rounded_card(img, radius=46, border=10):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius, fill=255)
    card = Image.new("RGBA", (w + border * 2, h + border * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, w + border * 2, h + border * 2), radius + border,
                                           fill=WHITE)
    im = img.convert("RGBA")
    im.putalpha(mask)
    card.alpha_composite(im, (border, border))
    sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    sh_mask = Image.new("L", sh.size, 0)
    ImageDraw.Draw(sh_mask).rounded_rectangle((40, 55, 40 + card.width, 55 + card.height), radius, fill=140)
    sh.putalpha(sh_mask.filter(ImageFilter.GaussianBlur(18)))
    sh.alpha_composite(card, (40, 40))
    return sh


def end_card(bg_frame, product, t, O):
    dt = t - SRC_DUR
    bg = bg_frame.filter(ImageFilter.GaussianBlur(min(26, 4 + dt * 70)))
    arr = np.asarray(bg).astype(np.float32)
    k = min(1.0, dt * 4)
    arr = arr * (1 - 0.45 * k) + np.array(PINK, np.float32) * 0.18 * k
    canvas = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
    place(canvas, O["end_head"], W / 2, 330, ease_out_back(dt / 0.25), 1.0, rot=-3)
    p = ease_out_back((dt - 0.1) / 0.35)
    place(canvas, product, W / 2, 800 + (1 - min(p, 1)) * 300, 0.62 * max(p, 0.01) + 0.0,
          min(1, dt / 0.2), rot=-4 + 2 * math.sin(dt * 2))
    if dt > 0.35:
        place(canvas, O["end_sub"], W / 2, 1170, ease_out_back((dt - 0.35) / 0.25), 1.0)
    if dt > 0.5:
        btn = shine(O["end_cta"], dt - 0.5)
        place(canvas, btn, W / 2, 1330, ease_out_back((dt - 0.5) / 0.25) * (1 + 0.05 * math.sin(dt * 9)), 1.0)
    if dt > 0.7:
        place(canvas, O["end_note"], W / 2, 1470, 1.0, min(1, (dt - 0.7) / 0.15))
        place(canvas, O["finger"], 200, 1690 + 24 * abs(math.sin(dt * 6)), 1.0, 1.0)
    d = ImageDraw.Draw(canvas)
    for (x, y, r, ph) in R.SPARKLES:
        tw = 0.5 + 0.5 * math.sin(t * 5 + ph * 6.28)
        star(d, x, y + 200, r * (0.4 + 0.8 * tw), 0.8 * tw)
    progress_bar(canvas, SRC_DUR)
    return canvas


# ---------------------------------------------------------------- audio
def build_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-f", "s16le", "-ac", "2",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    voice = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
    n = int(TOTAL * SR)
    mix = np.zeros((n, 2), np.float32)
    mix[:len(voice)] += voice[:n]
    rng = np.random.default_rng(3)

    def add(sig, t, gain):
        i = int(t * SR)
        j = min(n, i + len(sig))
        mix[i:j] += (sig[:j - i] * gain)[:, None]

    def tone(f0, d, decay):
        tt = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * decay)

    def shutter():
        m = int(0.12 * SR)
        x = rng.standard_normal(m).astype(np.float32)
        env = np.concatenate([np.exp(-np.arange(m // 2) / SR * 90), np.exp(-np.arange(m - m // 2) / SR * 60)])
        return x * env * 0.8

    def riser(d=0.5):
        m = int(d * SR)
        x = rng.standard_normal(m).astype(np.float32)
        x = np.convolve(x, np.ones(15) / 15, mode="same")
        return x * np.linspace(0, 1, m) ** 2 * np.linspace(1, 0, m) ** 0.3 * 3

    def chaching():
        s = tone(2093, 0.6, 7) + 0.6 * tone(2637, 0.6, 7)
        out = np.zeros(int(0.75 * SR), np.float32)
        out[:len(s)] += s
        out[int(0.09 * SR):int(0.09 * SR) + len(s)] += 0.8 * s[: len(out) - int(0.09 * SR)]
        return out * 0.5

    add(shutter(), 0.0, 0.5)
    add(tone(880, 0.12, 30), 0.75, 0.3)
    for t in (2.0, 7.95, 11.75, 16.25):
        add(riser(), t, 0.16)
    for i in range(3):
        add(tone(990 + 150 * i, 0.12, 28), 8.8 + i * 0.5, 0.3)
    for i in range(6):
        add(tone(700 + 90 * i, 0.06, 45), 12.2 + i * 0.07, 0.22)
    add(chaching(), 16.7, 0.35)
    add(chaching(), 19.5, 0.4)
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


def grab_product():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.4", "-i", SRC, "-frames:v", "1", "-vf",
                          "scale=1080:1920:flags=lanczos,eq=saturation=1.1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    img = Image.frombuffer("RGB", (W, H), raw)
    return rounded_card(img.crop((40, 260, 1040, 1000)))


def main():
    audio_path = OUT + ".audio.wav"
    build_audio(audio_path)
    O = build_overlays()
    product = grab_product()
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", SRC, "-vf",
         "scale=1080:1920:flags=lanczos,eq=saturation=1.12", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
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
        if i < NSRC:
            buf = dec.stdout.read(fsz)
            if len(buf) == fsz:
                last = Image.frombuffer("RGB", (W, H), buf)
            base = transform(R.hide_old_subs(last), t)
            if i == NSRC - 1:
                last_clean = base
            frame = Image.fromarray(grade(np.asarray(base), t)).convert("RGBA")
            cap = caption_frame(t)
            if cap:
                im, dy, a, rot = cap
                place(frame, im, W / 2, CAP_Y + dy, 1.0, a, rot=rot)
            draw_overlays(frame, t, O)
            progress_bar(frame, t)
        else:
            frame = end_card(last_clean, product, t, O)
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
