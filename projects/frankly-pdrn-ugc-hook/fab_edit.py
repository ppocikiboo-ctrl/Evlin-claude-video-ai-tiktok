#!/usr/bin/env python3
"""Version 3 of the UGC selfie edit: curiosity hook + Feature/Advantage/Benefit + CTA formula.

  0.0–2.0   HOOK       punch-zoom on the bottle, glitch, a circle drawn around the orange ball
  2.0–5.0   FEATURE    what it is (polaroid of the product)
  5.0–9.3   ADVANTAGE  why the bounce ball matters (before/after shaking polaroid)
  9.3–12.0  BENEFIT    animated checklist
  12.0–14.3 ACTION     "Tekan BAKUL KUNING" over the talking close-up
  14.3–18.8 END CARD   CTA formula: Action, Benefit (untuk apa), Reason (kenapa sekarang),
                       consequence (kalau tak)

The source clip plays continuously, so the song and lip-sync stay intact. The
end card reuses an earlier slice of the song. Edits on cuts pulse on the beat.

Usage:
  python3 fab_edit.py --video /path/to/selfie.mp4 [--stills 0.4,3,7,10.5,13,16]
"""
import argparse
import math
import os
import subprocess
import tempfile
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import edit
from edit import FPS, H, SHADOW, SPARKS, W, audio, flash, grade, src_frame, zoom
from render import (BROWN, CTA_YELLOW, P02, SHAKE_L, SHAKE_R, SPARK, appear, burst, clamp,
                    ease_back, ease_io, ease_out, emoji, EMOJI, feathered, lerp, make_rays,
                    pill, place, prog, put, text_img)

MAIN_LEN = 14.3
END_LEN = 4.5
DURATION = MAIN_LEN + END_LEN
SECTIONS = [  # (start, end, tag, colour, emoji, text)
    (2.0, 5.0, "FEATURE", (240, 104, 32), "🧬", "Bola Salmon PDRN 100,000 ppm*\n+ ekstrak telur salmon"),
    (5.0, 9.3, "ADVANTAGE", (226, 64, 96), "🔥", "Goncang, bola pecah jadi\npartikel mikro & sebati dengan esen"),
    (9.3, 12.0, "BENEFIT", (34, 160, 104), "✨", None),
]
BENEFITS = ["Kulit rasa lembap", "Nampak segar & glowing", "Mudah masuk rutin harian"]
CTA_ROWS = [  # (label, colour, emoji, text)
    ("ACTION", (240, 104, 32), "🛒", "Tekan BAKUL KUNING sekarang"),
    ("BENEFIT", (34, 160, 104), "✨", "Dapatkan serum bola PDRN untuk\nkulit nampak lembap & glowing"),
    ("REASON", (60, 120, 220), "⏰", "Harga & voucher boleh berubah\nbila-bila masa — semak hari ini"),
    ("KALAU TAK", (200, 50, 60), "😩", "Kulit kusam & kering, rutin\nkau masih tak lengkap"),
]
# orange-ball position in the source frame (full-res px) during the hook
BALL_KEYS = [(0.0, 778, 1183), (0.5, 816, 1199), (1.0, 820, 1247), (1.5, 761, 1231), (2.0, 622, 1360)]
YELLOW = (255, 214, 50)
BEATS = []
RAYS = None
VIGNETTE = None
POLA_PROD = None
POLA_SHAKE = None
END_BG = None
PROD_END = feathered(P02, feather=70, radius=420)


# ------------------------------------------------------------------ helpers
def ball_pos(t):
    for (t0, x0, y0), (t1, x1, y1) in zip(BALL_KEYS, BALL_KEYS[1:]):
        if t <= t1:
            p = ease_io(clamp((t - t0) / (t1 - t0)))
            return lerp(x0, x1, p), lerp(y0, y1, p)
    return BALL_KEYS[-1][1:]


def to_screen(x, y, z, cx, cy):
    """Map a source-frame point to the screen after zoom(im, z, cx, cy)."""
    cw, ch = W / z, H / z
    x0 = clamp(cx - cw / 2, 0, W - cw)
    y0 = clamp(cy - ch / 2, 0, H - ch)
    return (x - x0) * z, (y - y0) * z


def glitch(im, amount, seed):
    """RGB split + horizontal slice offsets."""
    if amount <= 0.02:
        return im
    rng = np.random.default_rng(seed)
    a = np.asarray(im.convert("RGB")).copy()
    d = int(24 * amount)
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], d, axis=1)
    out[..., 2] = np.roll(a[..., 2], -d, axis=1)
    for _ in range(int(8 * amount)):
        y = int(rng.integers(0, H - 80))
        h = int(rng.integers(12, 80))
        out[y:y + h] = np.roll(out[y:y + h], int(rng.integers(-90, 90) * amount), axis=1)
    return Image.fromarray(out).convert("RGBA")


def beat_pulse(t):
    z = 0.0
    for b in BEATS:
        if 0 <= t - b < 0.3:
            z = max(z, 0.035 * math.exp(-(t - b) / 0.09))
    return z


def polaroid(img, w):
    h = int(img.height * w / img.width)
    im = img.convert("RGB").resize((w, h), Image.LANCZOS)
    b = 14
    card = Image.new("RGBA", (w + 2 * b + 40, h + 2 * b + 50), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20, 30, 20 + w + 2 * b, 30 + h + 2 * b), 20, fill=(0, 0, 0, 110))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(card).rounded_rectangle((20, 20, 20 + w + 2 * b, 20 + h + 2 * b), 20, fill=(255, 255, 255, 255))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 12, fill=255)
    card.paste(im, (20 + b, 20 + b), m)
    return card


def rich(parts, size, kind="xb"):
    """Horizontally join differently coloured runs: parts = [(text, colour), ...]."""
    ims = [text_img(t, size, c, kind, shadow=SHADOW) for t, c in parts]
    gap = int(size * 0.22)
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for i in ims:
        out.alpha_composite(i, (x, (h - i.height) // 2))
        x += i.width + gap
    return out


@lru_cache(None)
def solid_card(w, h, r, fill, border):
    """Like render.glass_card but without the gloss strip, so text stays crisp."""
    sp = 30
    im = Image.new("RGBA", (w + 2 * sp, h + 2 * sp), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((sp, sp + 12, sp + w, sp + h + 12), r, fill=(40, 20, 10, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).rounded_rectangle((sp, sp, sp + w, sp + h), r, fill=fill, outline=border, width=4)
    return im


def tag_chip(label, colour, size=34):
    t = text_img(label, size, (255, 255, 255), "xb")
    w, h = t.width + 40, t.height + 18
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=colour + (255,))
    im.alpha_composite(t, (20, 9))
    return im


def section_card(sec, t):
    t0, t1, tag, col, em, txt = sec
    rows = BENEFITS if txt is None else txt.split("\n")
    ch = 112 + 66 * len(rows) if txt is None else 200
    card = solid_card(720, ch, 34, fill=(255, 255, 255, 228), border=col + (255,)).copy()
    chip = tag_chip(f"{tag}", col)
    card.alpha_composite(chip, (30 + 26, 30 + 20))
    card.alpha_composite(emoji(EMOJI[em], 52), (30 + 26 + chip.width + 12, 30 + 14))
    if txt is not None:
        tx = text_img(txt, 42, BROWN, "sb", align="left", max_w=660, line_h=1.15)
        card.alpha_composite(tx, (30 + 28, 30 + 82))
    else:
        for k, line in enumerate(BENEFITS):
            tk = t0 + 0.35 + 0.55 * k
            p = prog(t, tk, tk + 0.3)
            if p <= 0:
                continue
            y = 30 + 100 + 66 * k
            ck = emoji(EMOJI["✅"], 48)
            s = 0.4 + 0.6 * ease_back(p)
            ck = ck.resize((max(1, int(48 * s)), max(1, int(48 * s))))
            card.alpha_composite(ck, (30 + 28 + (48 - ck.width) // 2, y + (48 - ck.height) // 2))
            tl = text_img(line, 42, BROWN, "sb")
            tl = tl.crop((0, 0, max(1, int(tl.width * ease_out(p))), tl.height))
            card.alpha_composite(tl, (30 + 92, y + (48 - tl.height) // 2))
    return card


def setup():
    global RAYS, VIGNETTE, POLA_PROD, POLA_SHAKE, END_BG
    RAYS = make_rays(color=(255, 210, 150), peak=70)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = ((xx / W - 0.5) ** 2 + ((yy / H - 0.5) * 1.2) ** 2)
    VIGNETTE = Image.fromarray((np.clip((d - 0.12) * 1.6, 0, 0.55) * 255).astype(np.uint8))
    POLA_PROD = polaroid(P02.crop((150, 60, 950, 1060)), 250)
    POLA_SHAKE = (polaroid(SHAKE_L, 220), polaroid(SHAKE_R, 220))
    last = grade(src_frame(MAIN_LEN - 0.05)).convert("RGB").filter(ImageFilter.GaussianBlur(28))
    arr = np.asarray(last, np.float32) * 0.55 + np.array([255, 214, 180], np.float32) * 0.45
    END_BG = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")


def vignette(base):
    dark = Image.new("RGBA", (W, H), (30, 15, 5, 255))
    dark.putalpha(VIGNETTE)
    base.alpha_composite(dark)


def progress_bar(base, t):
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, W, 9), fill=(255, 255, 255, 90))
    d.rectangle((0, 0, int(W * t / DURATION), 9), fill=(255, 140, 40, 255))


def fab_tracker(base, t, active):
    labels = ["F", "A", "B"]
    cols = [s[3] for s in SECTIONS]
    x0 = 540 - 1.5 * 86 + 43
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(3):
        x = x0 + 86 * k
        on = k <= active
        if k < 2:
            d.line((x + 30, 556, x + 56, 556), fill=(255, 255, 255, 200), width=4)
        d.ellipse((x - 28, 528, x + 28, 584), fill=(cols[k] + (255,)) if on else (255, 255, 255, 160),
                  outline=(255, 255, 255, 255), width=4)
    base.alpha_composite(layer)
    for k in range(3):
        c = (255, 255, 255) if k <= active else (150, 120, 100)
        place(base, text_img(labels[k], 30, c, "xb"), x0 + 86 * k, 557)


# ------------------------------------------------------------------- frames
def hook(t):
    bx, by = ball_pos(t)
    z = 1.5 - 0.3 * ease_out(prog(t, 0.0, 0.45)) + 0.02 * math.sin(t * 3)
    cx = bx + 20 * math.sin(t * 70) * (1 - prog(t, 0, 0.3))
    cy = by - 120
    base = zoom(grade(src_frame(t)), z, cx, cy)
    sx, sy = to_screen(bx, by, z, cx, cy)
    # drawn circle around the ball + curved arrow from the headline
    p = prog(t, 0.35, 0.75)
    if p > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        r = 175 + 6 * math.sin(t * 9)
        d.arc((sx - r, sy - r * 0.9, sx + r, sy + r * 0.9), -100, -100 + 360 * ease_out(p),
              fill=(255, 50, 60, 255), width=14)
        q = prog(t, 0.65, 0.95)
        if q > 0:
            pts = [(lerp(300, sx - r * 0.7, s), lerp(560, sy - r * 0.75, s) - 160 * math.sin(math.pi * s))
                   for s in np.linspace(0, ease_out(q), 20)]
            d.line(pts, fill=(255, 255, 255, 255), width=10, joint="curve")
            if q >= 0.99:
                ex, ey = pts[-1]
                d.polygon([(ex + 8, ey + 10), (ex - 34, ey - 6), (ex - 4, ey - 38)], fill=(255, 255, 255, 255))
        base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.6)))
    SPARKS.draw(base, t, 0.6)
    vignette(base)
    l1 = rich([("KENAPA ADA", (255, 255, 255)), ("BOLA", YELLOW)], 96)
    l2 = rich([("DALAM SERUM NI?! 😳", (255, 255, 255))], 82)
    s, a, dy = appear(t, 0.05, "pop", 0.35)
    place(base, l1, 540, 300 + dy, s, a)
    s, a, dy = appear(t, 0.2, "pop", 0.35)
    place(base, l2, 540, 410 + dy, s, a)
    burst(base, t, 0.1, 540, 330, seed=1, radius=480, n=12)
    s, a, dy = appear(t, 1.15, "up", 0.3)
    place(base, pill("Jawapan dia... 👇", 46), 540, 1580 + dy, s, a)
    base = glitch(base, 1 - prog(t, 0, 0.18), seed=int(t * 100))
    return flash(base, 0.8 * (1 - prog(t, 0, 0.1)))


def main_part(t):
    z = 1.0 + beat_pulse(t)
    base = zoom(grade(src_frame(t)), z, 540, 800)
    SPARKS.draw(base, t, 0.35)
    vignette(base)
    active = -1
    for k, sec in enumerate(SECTIONS):
        t0, t1 = sec[0], sec[1]
        if t >= t0:
            active = k
        if not (t0 - 0.05 <= t < t1 + 0.35):
            continue
        p_in = ease_out(prog(t, t0, t0 + 0.4))
        p_out = ease_io(prog(t, t1, t1 + 0.3))
        x = 50 + 390 - 900 * (1 - p_in) - 900 * p_out
        place(base, section_card(sec, t), x, 345, 1.0, 1.0)
        # polaroids
        if k in (0, 1):
            pp = prog(t, t0 + 0.35, t0 + 0.75)
            s = (0.5 + 0.5 * ease_back(pp)) * (1 - p_out)
            if k == 0:
                pol = POLA_PROD
            else:
                pol = POLA_SHAKE[0] if t < t0 + 2.0 else POLA_SHAKE[1]
                if abs(t - (t0 + 2.0)) < 0.15:
                    s *= 1 - 0.25 * math.sin(math.pi * (t - t0 - 1.85) / 0.3)
            place(base, pol, 870, 790 + 8 * math.sin(t * 2), s, clamp(pp * 3) * (1 - p_out), rot=-7 + 2 * math.sin(t * 1.5))
            if k == 1 and t >= t0 + 2.0:
                place(base, text_img("Lepas goncang ✨", 30, (255, 255, 255), "xb", shadow=SHADOW), 870, 1010,
                      1, clamp((t - t0 - 2.0) / 0.3) * (1 - p_out))
            elif k == 1:
                place(base, text_img("Sebelum goncang", 30, (255, 255, 255), "xb", shadow=SHADOW), 870, 1010,
                      1, clamp(pp * 3))
        if k == 0:
            place(base, text_img("*Angka dari bahan pemasaran jenama", 24, (255, 255, 255), "m", shadow=SHADOW),
                  330, 480, 1, p_in * (1 - p_out))
    if 2.0 <= t < 12.3:
        fab_tracker(base, t, active)
    # section-change glitch
    for sec in SECTIONS:
        if 0 <= t - sec[0] < 0.14:
            base = glitch(base, 1 - (t - sec[0]) / 0.14, seed=int(t * 100))
    # ACTION over the close-up
    if t >= 12.0:
        s, a, dy = appear(t, 12.0, "pop", 0.35)
        place(base, rich([("Nak cuba sendiri?", (255, 255, 255)), ("👀", (255, 255, 255))], 70), 540, 320 + dy, s, a)
        s, a, _ = appear(t, 12.3, "pop", 0.4)
        pulse = 1 + 0.05 * math.sin((t - 12.3) * 2 * math.pi * 1.8) * prog(t, 12.7, 12.9)
        place(base, pill("TEKAN BAKUL KUNING 🛒", 62, fg=BROWN, bg=CTA_YELLOW, bg2=(255, 178, 40)),
              540, 1575, s * pulse, a)
        put(base, emoji("1f447", 120), 170, 1440 + 22 * math.sin(t * 9), 110, a)
        burst(base, t, 12.35, 540, 1575, seed=20, radius=460, n=14)
    progress_bar(base, t)
    return flash(base, 0.0)


def end_card(u):
    base = END_BG.copy()
    place(base, RAYS.rotate(u * 10, Image.BILINEAR), 540, 700, 1.0, 0.9)
    pe = ease_back(prog(u, 0.0, 0.5))
    place(base, PROD_END, 540, 690 + 8 * math.sin(u * 2), 0.54 * (0.6 + 0.4 * pe), clamp(u / 0.25))
    s, a, dy = appear(u, 0.1, "pop", 0.35)
    place(base, rich([("🚨 JANGAN", (255, 255, 255)), ("TERLEPAS!", YELLOW)], 84), 540, 230 + dy, s, a)
    burst(base, u, 0.15, 540, 230, seed=40, radius=480, n=12)
    for k, (label, col, em, txt) in enumerate(CTA_ROWS):
        tk = 0.55 + 0.75 * k
        p = prog(u, tk, tk + 0.35)
        if p <= 0:
            continue
        rh = 118 if "\n" not in txt else 150
        hi = k == 0
        card = solid_card(900, rh, 30, fill=(255, 236, 140, 245) if hi else (255, 255, 255, 235),
                          border=col + (255,)).copy()
        chip = tag_chip(label, col, 26)
        card.alpha_composite(chip, (30 + 20, 30 + 14))
        card.alpha_composite(emoji(EMOJI[em], 50), (30 + 20 + (chip.width - 50) // 2, 30 + 14 + chip.height + 6)
                             if rh > 130 else (30 + 20 + chip.width + 10, 30 + 10))
        tx = text_img(txt, 40 if not hi else 46, BROWN, "xb" if hi else "sb", align="left", max_w=640, line_h=1.12)
        tx_x = 30 + 20 + max(chip.width, 50) + (20 if rh > 130 else 70)
        card.alpha_composite(tx, (tx_x, 30 + (rh - tx.height) // 2))
        y = 1060 + sum((118 if "\n" not in r[3] else 150) + 14 for r in CTA_ROWS[:k])
        pulse = 1 + (0.03 * math.sin((u - tk) * 2 * math.pi * 1.6) if hi and u > tk + 0.5 else 0)
        place(base, card, 510 - 600 * (1 - ease_out(p)), y + rh / 2, pulse, clamp(p * 2))
        burst(base, u, tk, 160, y + rh / 2, seed=50 + k, radius=200, n=6, size=50)
    put(base, emoji("1f447", 120), 120, 1700 + 20 * math.sin(u * 9), 100, clamp((u - 0.6) / 0.3))
    progress_bar(base, MAIN_LEN + u)
    base = glitch(base, 1 - prog(u, 0, 0.15), seed=int(u * 100) + 7)
    return flash(base, 0.7 * (1 - prog(u, 0, 0.12)))


def render_frame(i):
    t = i / FPS
    if t < 2.0:
        im = hook(t)
    elif t < MAIN_LEN:
        im = main_part(t)
    else:
        im = end_card(t - MAIN_LEN)
    return im.convert("RGB").tobytes()


# -------------------------------------------------------------------- audio
def load_orig(video, work):
    raw = os.path.join(work, "orig.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "2", "-ar", str(audio.SR), raw], check=True)
    with wave.open(raw) as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768


def find_beats(x, t0=2.0, t1=12.0):
    sr = audio.SR
    mono = x.mean(axis=1)
    low = audio.fft_band(mono, 40, 160)
    hop = int(0.02 * sr)
    e = np.array([np.sqrt(np.mean(low[i:i + hop] ** 2)) for i in range(0, len(low) - hop, hop)])
    on = np.maximum(0, np.diff(e, prepend=e[0]))
    thr = on.mean() + 2 * on.std()
    beats, last = [], -1
    for k, v in enumerate(on):
        tt = k * 0.02
        if v > thr and tt - last > 0.28 and t0 <= tt <= t1:
            beats.append(tt)
            last = tt
    return beats


def build_audio(x, path):
    sr = audio.SR

    def seg(a, b, fi=0.01, fo=0.06):
        s = x[int(a * sr):int(b * sr)].copy()
        e = np.ones(len(s))
        e[:int(fi * sr)] = np.linspace(0, 1, int(fi * sr))
        e[len(s) - int(fo * sr):] = np.linspace(1, 0, int(fo * sr))
        return s * e[:, None]

    song = np.concatenate([seg(0, MAIN_LEN, 0.005, 0.25), seg(0.3, 0.3 + END_LEN, 0.25, 0.8) * 0.7])
    fx = np.zeros_like(song)
    rng = np.random.default_rng(9)
    ev = [(0.0, "impact"), (0.0, "whoosh"), (0.08, "pop"), (0.25, "pop"), (0.4, "tik"), (0.7, "whoosh_soft"),
          (1.15, "pop"), (12.0, "pop"), (12.3, "pop"), (12.35, "sparkle"),
          (MAIN_LEN, "impact"), (MAIN_LEN + 0.1, "pop")]
    for sec in SECTIONS:
        ev += [(sec[0] - 0.05, "whoosh"), (sec[0] + 0.35, "pop")]
    ev += [(9.3 + 0.35 + 0.55 * k, "tik") for k in range(3)]
    ev += [(7.0, "ting")]
    ev += [(MAIN_LEN + 0.55 + 0.75 * k, "pop") for k in range(4)] + [(MAIN_LEN + 3.4, "ting")]
    for t0, kind in ev:
        audio.add(fx, audio.sfx(kind, rng), max(0.0, t0))
    mix = song + fx * 0.45
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix *= 0.93 / np.abs(mix).max()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


def main():
    global BEATS
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", default=os.path.join(edit.HERE, "output", "frankly-pdrn-ugc-fab-cta.mp4"))
    ap.add_argument("--stills")
    args = ap.parse_args()
    work = tempfile.mkdtemp(prefix="fab-")
    edit.FRAMES = os.path.join(work, "f")
    os.makedirs(edit.FRAMES)
    subprocess.run(["ffmpeg", "-v", "error", "-i", args.video, "-vf", f"fps={FPS}", "-q:v", "2",
                    os.path.join(edit.FRAMES, "f%04d.jpg")], check=True)
    x = load_orig(args.video, work)
    BEATS = find_beats(x)
    setup()
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    if args.stills:
        for s in args.stills.split(","):
            Image.frombytes("RGB", (W, H), render_frame(int(float(s) * FPS))).save(
                os.path.join(out_dir, f"fab_still_{float(s):05.2f}.jpg"), quality=90)
        return
    wav = os.path.join(work, "mix.wav")
    build_audio(x, wav)
    n = int(round(DURATION * FPS))
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", args.out], stdin=subprocess.PIPE)
    from multiprocessing import Pool
    with Pool(os.cpu_count()) as pool:
        for buf in pool.imap(render_frame, range(n), chunksize=4):
            enc.stdin.write(buf)
    enc.stdin.close()
    enc.wait()
    print("wrote", args.out, "beats:", len(BEATS))


if __name__ == "__main__":
    main()
