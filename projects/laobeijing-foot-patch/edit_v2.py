#!/usr/bin/env python3
"""Version 2 of the Laobeijing foot patch edit, with a different visual style.

Usage:  python3 edit_v2.py SOURCE.mp4 OUTPUT.mp4
        python3 edit_v2.py SOURCE.mp4 PREVIEW_DIR --preview

Differences from edit.py (v1):
  * Hook: cold open on the result (both feet with patches) while the voice
    asks "siapa-siapa yang rasa lenguh-lenguh kaki", a RM0.20/keping stamp,
    then a whip-pan into the unboxing.
  * Red-gold look that matches the box, warm colour grade, vignette and a
    progress bar along the top.
  * One-word-at-a-time captions, with key words bigger and in gold.
  * Whip-pan transitions, camera shake and RGB-split glitch on stamps.
  * Rolling price counter (RM36.00 -> RM9.99), 0 -> 50 counter, filling stars
    and a sold counter, a TikTok-comment style review bubble.
  * Big outlined step numbers, guide image dropped in like a swinging photo,
    a checklist that ticks itself, CTA with a light sweep and confetti.
  * Synthesised sound effects (whoosh, pop, cha-ching), mixed under the voice.

Helpers, timeline mapping and the narration (PHRASES) come from edit.py.
"""
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import edit as v1
from edit import (FONT_BLACK, FONT_BOLD, PHRASES, PRICE, PRICE_OLD, DISCOUNT, RATING, REVIEWS,
                  card, ease_out, ease_out_back, emoji, font, panel, paste_center, pill, pop_scale,
                  stack_h, stack_v, strike, text_img)

W, H, FPS = v1.W, v1.H, v1.FPS
SP = v1.SP
ASSETS = v1.ASSETS

RED = (200, 16, 30)
DEEP = (110, 6, 14)
GOLD = (255, 196, 46)
CREAM = (255, 246, 225)
WHITE = (255, 255, 255)
INK = (25, 18, 15)

SOLD_N = 44300
PER_PIECE = f"RM{float(PRICE[2:]) / 50:.2f}"  # 50 pieces per box

TALK_A, TALK_B = 0.45, 25.45
HOOK_LEN = 1.8                       # output seconds of cold open
HOOK_SRC = (24.35, 0.6)              # feet clip: src start, speed
WHY_LEN, CTA_LEN = 2.35, 4.6
TALK_LEN = (TALK_B - TALK_A) / SP
TOTAL = TALK_LEN + WHY_LEN + CTA_LEN


def o(ts):
    return (min(max(ts, TALK_A), TALK_B) - TALK_A) / SP


T_WHY = TALK_LEN
T_CTA = TALK_LEN + WHY_LEN

GRADE = ("eq=contrast=1.10:saturation=1.30:brightness=0.015:gamma_r=1.04:gamma_b=0.95,"
         "colorbalance=rm=0.04:gm=0.0:bm=-0.04")


# ---------------------------------------------------------------- base video + audio
def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def render_base(src, dst):
    """Main talk part, cold-open clip and the slow tail, all graded, plus the voice track."""
    vf = lambda sp: f"setpts=(PTS-STARTPTS)/{sp},scale={W}:{H},fps={FPS},setsar=1,{GRADE}"
    n_talk = int(round(TALK_LEN * FPS))
    ff("-ss", str(TALK_A), "-t", str(TALK_B - TALK_A), "-i", src, "-vf", vf(SP), "-frames:v", str(n_talk),
       "-an", "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", dst + ".talk.mp4")
    ff("-ss", str(HOOK_SRC[0]), "-t", str(HOOK_LEN * HOOK_SRC[1] + 0.2), "-i", src, "-vf", vf(HOOK_SRC[1]),
       "-frames:v", str(int(HOOK_LEN * FPS)), "-an", "-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
       dst + ".hook.mp4")
    n_tail = int(round((WHY_LEN + CTA_LEN) * FPS))
    ff("-ss", "24.70", "-t", "0.8", "-i", src, "-vf", vf(0.3) + ",tpad=stop_mode=clone:stop=-1",
       "-frames:v", str(n_tail), "-an", "-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
       dst + ".tail.mp4")
    d = TALK_LEN
    ff("-ss", str(TALK_A), "-t", str(TALK_B - TALK_A), "-i", src, "-vn",
       "-af", f"atempo={SP},afade=t=in:d=0.04,afade=t=out:st={d - 0.1}:d=0.1,apad,atrim=0:{TOTAL}",
       "-ar", "44100", "-ac", "2", dst + ".voice.wav")


# ---------------------------------------------------------------- sound effects
SR = 44100


def _env(n, attack=0.005, decay=None):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    d = np.exp(-t / decay) if decay else 1
    return a * d


def sfx_whoosh(dur=0.38):
    n = int(dur * SR)
    noise = np.random.RandomState(1).randn(n)
    t = np.arange(n) / n
    cut = 0.02 + 0.25 * np.sin(np.pi * t) ** 2       # sweep cutoff up and down
    y, out = 0.0, np.zeros(n)
    for i in range(n):                                # one-pole low-pass with moving cutoff
        y += cut[i] * (noise[i] - y)
        out[i] = y
    return out * np.sin(np.pi * t) ** 1.5 * 2.2


def sfx_pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 250
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.03) * 0.7


def sfx_ding(f0=1568):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 2.01 * t) + 0.25 * np.sin(2 * np.pi * f0 * 3 * t)
    return s * _env(n, 0.002, 0.18) * 0.35


def sfx_cash():
    a, b = sfx_ding(1568), sfx_ding(2093)
    out = np.zeros(len(b) + int(0.09 * SR))
    out[:len(a)] += a
    out[int(0.09 * SR):int(0.09 * SR) + len(b)] += b
    return out


def sfx_hit():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 8) + 45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.16)
    click = np.random.RandomState(2).randn(n) * _env(n, 0.001, 0.008) * 0.4
    return (body + click) * 0.9


def sfx_tick():
    n = int(0.025 * SR)
    return np.random.RandomState(3).randn(n) * _env(n, 0.0005, 0.004) * 0.35


def sfx_sparkle():
    out = np.zeros(int(0.9 * SR))
    for i, f in enumerate([2093, 2637, 3136, 4186]):
        d = sfx_ding(f) * 0.5
        s = int(i * 0.07 * SR)
        out[s:s + len(d)] += d[:len(out) - s]
    return out


# ---------------------------------------------------------------- timed events
WHIPS = [HOOK_LEN, o(6.80), o(14.80), T_WHY, T_CTA]
STEP_T = [o(17.40), o(18.60), o(22.50), o(24.40)]
T50, TPRICE, TPROOF = o(8.0), o(9.3), o(12.0)
T_WAJIB = o(4.7)
T_GUIDE = (o(21.00), o(22.55))
STAMP_HOOK = 0.55
PRICE_ROLL = (TPRICE + 0.15, 1.1)    # start, duration of the rolling counter
T_DISC = PRICE_ROLL[0] + PRICE_ROLL[1] + 0.05
T_PER = T_DISC + 0.45
SHAKES = [STAMP_HOOK, T_WAJIB, T_DISC, T50 + 0.5, T_CTA + 0.9]


def build_sfx():
    out = np.zeros(int((TOTAL + 1) * SR))

    def add(t, s, g=1.0):
        i = int(t * SR)
        out[i:i + len(s)] += s[:len(out) - i] * g

    add(0.0, sfx_hit(), 0.9)
    for t in WHIPS:
        add(max(t - 0.2, 0), sfx_whoosh(), 0.55)
    for t in STEP_T:
        add(t - 0.15, sfx_whoosh(0.3), 0.4)
        add(t + 0.1, sfx_pop(), 0.5)
    for t in (STAMP_HOOK, T_WAJIB, T_DISC):
        add(t, sfx_hit(), 0.6)
    k = 0
    while k < 50:                       # ticks while 0 -> 50 counts up
        add(T50 + 0.5 * ease_out(k / 50), sfx_tick(), 0.5)
        k += 5
    for i in range(12):                  # price roll ticks
        add(PRICE_ROLL[0] + PRICE_ROLL[1] * ease_out(i / 12) ** 1.3, sfx_tick(), 0.5)
    add(T_DISC - 0.05, sfx_cash(), 0.8)
    add(T_PER, sfx_pop(), 0.6)
    add(TPROOF + 0.1, sfx_pop(), 0.5)
    add(T_GUIDE[0], sfx_pop(), 0.6)
    for i in range(4):
        add(T_WHY + 0.4 + 0.35 * i, sfx_pop(), 0.45)
    add(T_CTA + 0.05, sfx_sparkle(), 0.7)
    add(T_CTA + 0.9, sfx_cash(), 0.6)
    peak = np.abs(out).max()
    return out / max(peak, 1) * 0.6


def write_wav(path, mono):
    pcm = (np.clip(mono, -1, 1) * 32767).astype(np.int16)
    st = np.repeat(pcm[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


# ---------------------------------------------------------------- frame effects
def zoom(frame, s, cx=0.5, cy=0.5):
    return v1.zoom(frame, s, cx, cy)


def whip(frame, k, direction=1):
    """Horizontal motion blur + slide. k in 0..1, strongest at 0.5."""
    amt = math.sin(math.pi * k)
    if amt < 0.02:
        return frame
    blur = 1 + int(amt * 28)
    fr = frame.resize((max(8, W // blur), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    dx = int(direction * (k - 0.5) * -260 * amt)
    return ImageChops.offset(fr, dx, 0)


def shake(img, t):
    for t0 in SHAKES:
        if t0 <= t < t0 + 0.35:
            a = 22 * (1 - (t - t0) / 0.35)
            dx = int(a * math.sin(t * 95))
            dy = int(a * math.cos(t * 77))
            return ImageChops.offset(img, dx, dy)
    return img


def rgb_split(img, amt):
    if amt < 1:
        return img
    r, g, b, a = img.split()
    r = ImageChops.offset(r, int(amt), 0)
    b = ImageChops.offset(b, -int(amt), int(amt * 0.4))
    return Image.merge("RGBA", (r, g, b, a))


def vignette():
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
    a = (np.clip(d - 0.55, 0, 1) * 260).clip(0, 150).astype(np.uint8)
    im = Image.new("RGBA", (W, H), (20, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


VIGNETTE = vignette()


def progress_bar(base, t):
    k = t / TOTAL
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, W, 12), fill=(0, 0, 0, 120))
    d.rectangle((0, 0, int(W * k), 12), fill=GOLD)


# ---------------------------------------------------------------- graphics
def banner(txt, size, bg=RED, fg=WHITE, rot=0, emo=None, border=GOLD):
    t = text_img(txt, size, fg)
    e = emoji(emo, int(size * 1.0)) if emo else None
    ew = (e.width + 16) if e else 0
    w, h = t.width + ew + 70, t.height + 44
    im = Image.new("RGBA", (w + 30, h + 40))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rectangle((15, 26, 15 + w, 26 + h), fill=(0, 0, 0, 130))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rectangle((15, 15, 15 + w, 15 + h), fill=bg, outline=border, width=6)
    x = 15 + 35
    if e:
        im.alpha_composite(e, (x, 15 + (h - e.height) // 2))
        x += ew
    im.alpha_composite(t, (x, 15 + (h - t.height) // 2))
    return im.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else im


def stamp_circle(top, mid, bot, d=330, bg=GOLD, fg=DEEP):
    im = Image.new("RGBA", (d + 40, d + 40))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).ellipse((20, 30, 20 + d, 30 + d), fill=(0, 0, 0, 140))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(12)))
    dr = ImageDraw.Draw(im)
    # starburst
    cx = cy = 20 + d / 2
    pts = []
    for i in range(48):
        r = d / 2 if i % 2 == 0 else d / 2 - 18
        a = math.pi * 2 * i / 48
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    dr.polygon(pts, fill=bg)
    dr.ellipse((cx - d / 2 + 32, cy - d / 2 + 32, cx + d / 2 - 32, cy + d / 2 - 32), outline=fg, width=5)
    block = stack_v([text_img(top, 38, fg), text_img(mid, 92, fg), text_img(bot, 40, fg)], gap=8)
    im.alpha_composite(block, (int(cx - block.width / 2), int(cy - block.height / 2)))
    return im


def outline_num(txt, d=170):
    im = Image.new("RGBA", (d + 40, d + 40))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).ellipse((20, 30, 20 + d, 30 + d), fill=(0, 0, 0, 140))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).ellipse((20, 20, 20 + d, 20 + d), fill=DEEP, outline=GOLD, width=9)
    t = text_img(txt, 92, GOLD)
    im.alpha_composite(t, (20 + (d - t.width) // 2, 20 + (d - t.height) // 2))
    return im


def star_shape(size, fill):
    im = Image.new("RGBA", (size, size))
    c, r1, r2 = size / 2, size / 2, size / 2 * 0.45
    pts = []
    for i in range(10):
        r = r1 if i % 2 == 0 else r2
        a = -math.pi / 2 + math.pi * i / 5
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=fill)
    return im


STAR_GREY = star_shape(96, (255, 255, 255, 90))
STAR_GOLD = star_shape(96, GOLD)


def stars_fill(value):
    """value 0..5, drawn as 5 stars filled up to value."""
    im = Image.new("RGBA", (5 * 108, 96))
    for i in range(5):
        im.alpha_composite(STAR_GREY, (i * 108, 0))
        f = min(max(value - i, 0), 1)
        if f > 0:
            part = STAR_GOLD.crop((0, 0, int(96 * f), 96))
            im.alpha_composite(part, (i * 108, 0))
    return im


def comment_bubble():
    av = Image.new("RGBA", (96, 96))
    ImageDraw.Draw(av).ellipse((0, 0, 95, 95), fill=(235, 225, 210))
    e = emoji("👩", 60)
    av.alpha_composite(e, ((96 - e.width) // 2, (96 - e.height) // 2))
    name = text_img("Pembeli • ⭐⭐⭐⭐⭐".replace("⭐", "★"), 36, (120, 110, 100), path=FONT_BOLD)
    lines = [text_img(s, 46, INK, path=FONT_BOLD) for s in
             ("Pakai malam sebelum tidur…", "bangun tidur rasa ringan badan,", "tapak kaki kurang sakit 🥰".replace(" 🥰", ""))]
    body = stack_v([name] + lines, gap=10, align="left")
    w, h = 96 + 30 + body.width + 80, max(96, body.height) + 70
    im = panel(w, h, bg=(255, 255, 255, 250), radius=44)
    im.alpha_composite(av, (20 + 34, 20 + 35))
    im.alpha_composite(body, (20 + 34 + 96 + 26, 20 + 35))
    # tail
    ImageDraw.Draw(im).polygon([(110, 20 + h - 2), (150, 20 + h - 2), (100, 20 + h + 34)], fill=(255, 255, 255, 250))
    tag = pill("Review pembeli", 34, RED, pad=(22, 10), shadow=False)
    im.alpha_composite(tag, (im.width - tag.width - 30, 0))
    return im


def polaroid(img, width):
    im = img.convert("RGBA").resize((width, int(width * img.height / img.width)), Image.LANCZOS)
    pad, bot = 26, 90
    out = Image.new("RGBA", (width + 2 * pad + 40, im.height + pad + bot + 40))
    sh = Image.new("RGBA", out.size)
    ImageDraw.Draw(sh).rectangle((20, 34, 20 + width + 2 * pad, 34 + im.height + pad + bot), fill=(0, 0, 0, 150))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(out).rectangle((20, 20, 20 + width + 2 * pad, 20 + im.height + pad + bot), fill=CREAM)
    out.alpha_composite(im, (20 + pad, 20 + pad))
    cap = text_img("6 langkah mudah ✓".replace(" ✓", ""), 52, DEEP)
    out.alpha_composite(cap, (out.width // 2 - cap.width // 2, 20 + pad + im.height + (bot - cap.height) // 2))
    # tape
    tape = Image.new("RGBA", (200, 56), (255, 230, 150, 190)).rotate(-6, expand=True)
    out.alpha_composite(tape, (out.width // 2 - tape.width // 2, 0))
    return out


def checklist():
    items = ["Untuk kaki lenguh & lama berdiri", "Cuka buluh + arang buluh",
             "Bau herba, tak busuk", "Pakai malam, buka lepas 8 jam"]
    rows = [text_img(s, 46, INK, path=FONT_BOLD) for s in items]
    w = max(r.width for r in rows) + 170
    h = 140 + len(rows) * 110
    return items, rows, w, h


CL_ITEMS, CL_ROWS, CL_W, CL_H = checklist()
CL_PANEL = panel(CL_W, CL_H, bg=(255, 250, 240, 245), radius=36)
_cl_title = text_img("KENAPA RAMAI SUKA?", 58, RED)
CL_PANEL.alpha_composite(_cl_title, (20 + (CL_W - _cl_title.width) // 2, 20 + 40))


def draw_checklist(base, lt, cx, cy):
    k = ease_out_back(lt / 0.4)
    if k <= 0.01:
        return
    im = CL_PANEL.copy()
    d = ImageDraw.Draw(im)
    for i, row in enumerate(CL_ROWS):
        y = 20 + 140 + i * 110
        t0 = 0.4 + 0.35 * i
        if lt < t0:
            continue
        a = ease_out((lt - t0) / 0.25)
        bx, by = 20 + 44, y + 10
        d.rounded_rectangle((bx, by, bx + 64, by + 64), 14, outline=RED, width=6)
        # tick drawn progressively
        p = [(bx + 12, by + 34), (bx + 28, by + 50), (bx + 56, by + 14)]
        if a > 0:
            m = min(a * 2, 1)
            d.line([p[0], (p[0][0] + (p[1][0] - p[0][0]) * m, p[0][1] + (p[1][1] - p[0][1]) * m)],
                   fill=(20, 150, 70), width=10)
            if a > 0.5:
                m = (a - 0.5) * 2
                d.line([p[1], (p[1][0] + (p[2][0] - p[1][0]) * m, p[1][1] + (p[2][1] - p[1][1]) * m)],
                       fill=(20, 150, 70), width=10)
        r = row.copy()
        r.putalpha(r.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(r, (bx + 96 - int((1 - a) * 40), by + (64 - row.height) // 2))
    paste_center(base, im, cx, cy, k)


# ---------------------------------------------------------------- static graphics
FEET_CARD = card(Image.open(os.path.join(ASSETS, "feet.png")), 600, radius=12, border=12, border_col=GOLD)
BOX_CARD = card(Image.open(os.path.join(ASSETS, "box.png")), 440, radius=12, border=10, border_col=GOLD)
GUIDE = polaroid(Image.open(os.path.join(ASSETS, "caraguna.png")), 820)
BUBBLE = comment_bubble()

HOOK_A = banner("KAKI LENGUH?", 120, RED, WHITE, rot=-3)
HOOK_B = text_img("TAMPAL NI MASA TIDUR", 66, WHITE, 9)
HOOK_STAMP = stamp_circle("CUMA", PER_PIECE, "SEKEPING!")
TAG_TOP = banner("KAKI LENGUH?", 50, RED, WHITE, emo="😩")
HOOK_C = banner("KERJA LAMA BERDIRI?", 64, CREAM, DEEP, rot=2)
WAJIB = banner("WAJIB TRY!", 96, GOLD, DEEP, rot=-6, emo="🔥", border=WHITE)

DISC_STAMP = stamp_circle("JIMAT", DISCOUNT, "HARI NI", d=280, bg=RED, fg=WHITE)
PER_PIECE_PILL = banner(f"= {PER_PIECE} SEKEPING", 58, GOLD, DEEP)

STEPS = [("CARA PASANG", "SENANG JE!"), ("01", "KOYAK STICKER BESAR"), ("02", "LETAK PAD, BUNGA DI LUAR"),
         ("03", "TAMPAL DI TAPAK KAKI"), ("04", "PAKAI MASA TIDUR 😴".replace(" 😴", ""))]
STEP_NUMS = {n: outline_num(n) for n, _ in STEPS[1:]}
STEP_TXT = {b: banner(b, 50, WHITE, INK, border=RED) for _, b in STEPS}
STEP_TIMES = [o(14.8)] + STEP_T

C_TOP = text_img("TERUS CHECKOUT!", 80, WHITE, 10)
C_OLD = strike(text_img(PRICE_OLD, 64, (235, 225, 225), 6, path=FONT_BOLD), GOLD, 8)
C_PRICE = text_img(PRICE, 200, GOLD, 16, stroke_fill=DEEP)
C_SUB = text_img(f"50 keping • {PER_PIECE} sekeping", 50, WHITE, 7, path=FONT_BOLD)
C_SHIP = banner("FREE SHIPPING", 44, (20, 120, 65), WHITE, emo="🚚", border=WHITE)
C_BUY = banner("TEKAN BEG KUNING", 64, GOLD, DEEP, emo="🛒", border=WHITE)
ARROW = emoji("👇", 120)

random.seed(7)
CONFETTI = [dict(x=W / 2 + random.uniform(-80, 80), y=700, vx=random.uniform(-900, 900),
                 vy=random.uniform(-1700, -500), rot=random.uniform(0, 360), vr=random.uniform(-600, 600),
                 c=random.choice([GOLD, RED, WHITE, (255, 120, 140), (120, 220, 160)]),
                 w=random.randint(14, 26), h=random.randint(8, 14)) for _ in range(140)]


def draw_confetti(base, lt):
    if lt < 0 or lt > 3.0:
        return
    d = ImageDraw.Draw(base)
    for p in CONFETTI:
        x = p["x"] + p["vx"] * lt
        y = p["y"] + p["vy"] * lt + 0.5 * 2200 * lt * lt
        if y > H + 40:
            continue
        a = math.radians(p["rot"] + p["vr"] * lt)
        hw, hh = p["w"] / 2, p["h"] / 2 * abs(math.cos(a * 1.7))
        pts = [(x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a))
               for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
        d.polygon(pts, fill=p["c"])


def glint(img, k):
    """Diagonal light sweep across img (respecting its alpha); k 0..1 position."""
    if k <= 0 or k >= 1:
        return img
    band = Image.new("L", img.size)
    x = int(-img.width * 0.4 + k * img.width * 1.8)
    ImageDraw.Draw(band).polygon([(x, 0), (x + 90, 0), (x - img.height * 0.4 + 90, img.height),
                                  (x - img.height * 0.4, img.height)], fill=170)
    band = band.filter(ImageFilter.GaussianBlur(12))
    band = ImageChops.multiply(band, img.getchannel("A"))
    out = img.copy()
    out.alpha_composite(Image.merge("RGBA", (Image.new("L", img.size, 255),) * 3 + (band,)))
    return out


# ---------------------------------------------------------------- captions (one word at a time)
EMPH = {"LENGUH-LENGUH", "KAKI,", "BERDIRI,", "BELILAH", "50", "KEPING,", "MAHAL", "SELESA",
        "SENANG", "STICKER,", "BUNGA", "LUAR.", "TAMPAL", "YEAY!"}


def build_words():
    words = []
    for a, b, txt in PHRASES:
        toks = txt.split()
        oa, ob = o(a), o(b)
        lens = [len(x) + 3 for x in toks]
        tot = sum(lens)
        t = oa
        for tok, ln in zip(toks, lens):
            d = (ob - oa) * ln / tot
            words.append([t, t + d, tok.upper()])
            t += d
    for i in range(len(words) - 1):
        words[i][1] = min(max(words[i][1], words[i][0] + 0.12), words[i + 1][0])
    words[-1][1] = TALK_LEN
    return words


WORDS = build_words()
_wcache = {}


def word_img(tok):
    if tok not in _wcache:
        emph = tok in EMPH
        size = 132 if emph else 108
        col = GOLD if emph else WHITE
        im = text_img(tok, size, col, 13, stroke_fill=(10, 0, 0))
        if im.width > 980:
            im = im.resize((980, int(im.height * 980 / im.width)), Image.LANCZOS)
        _wcache[tok] = im
    return _wcache[tok]


def draw_word(base, t, cy=1360):
    w = next((w for w in WORDS if w[0] <= t < w[1]), None)
    if not w:
        return
    im = word_img(w[2])
    k = ease_out_back((t - w[0]) / 0.14)
    paste_center(base, im, W / 2, cy, 0.6 + 0.4 * k, rot=(-3 if w[2] in EMPH else 0))


# ---------------------------------------------------------------- frame
def render_frame(fr, t):
    """fr: graded source frame (RGB) for output time t."""
    # camera
    if t < HOOK_LEN:
        fr = zoom(fr, 1.22 - 0.14 * ease_out(t / HOOK_LEN), 0.5, 0.6)
    elif t < T_WHY:
        s = 1.04 + 0.03 * math.sin(t * 0.8)          # gentle drift so the single take feels alive
        for t0 in [T_WAJIB, T50, TPRICE] + STEP_T:
            if t0 <= t < t0 + 0.3:
                s += 0.08 * (1 - ease_out((t - t0) / 0.3))
        fr = zoom(fr, s, 0.5, 0.45)
    elif t < T_CTA:
        fr = zoom(fr, 1.05 + 0.06 * (t - T_WHY) / WHY_LEN, 0.5, 0.75).filter(ImageFilter.GaussianBlur(3))
    else:
        lt = t - T_CTA
        fr = zoom(fr, 1.15 + 0.03 * lt / CTA_LEN).filter(ImageFilter.GaussianBlur(18))
        fr = Image.blend(fr, Image.new("RGB", (W, H), DEEP), 0.55)

    # whip transitions
    for i, tw in enumerate(WHIPS):
        if tw - 0.18 <= t < tw + 0.18:
            fr = whip(fr, (t - tw + 0.18) / 0.36, 1 if i % 2 == 0 else -1)

    base = fr.convert("RGBA")
    base.alpha_composite(VIGNETTE)

    if t < 0.1:  # flash
        base = Image.blend(base, Image.new("RGBA", (W, H), WHITE + (255,)), 0.9 * (1 - t / 0.1))

    glitch = 0
    # ---------------- hook (cold open)
    if t < HOOK_LEN:
        paste_center(base, HOOK_A, W / 2, 330, pop_scale(t, 0.05, 0.3))
        paste_center(base, HOOK_B, W / 2, 490, pop_scale(t, 0.3, 0.3))
        sc = 1.8 - 0.8 * ease_out((t - STAMP_HOOK) / 0.2) if t >= STAMP_HOOK else 0
        paste_center(base, HOOK_STAMP, 740, 900, sc * (1 + 0.04 * math.sin(t * 10)), rot=14)
        if STAMP_HOOK <= t < STAMP_HOOK + 0.15:
            glitch = 18
    elif t < T_WHY:
        lt_talk = t
        # hook carry-over
        if t < o(6.8):
            paste_center(base, TAG_TOP, W / 2, 200, pop_scale(t, HOOK_LEN, 0.3))
            paste_center(base, HOOK_C, W / 2, 360, pop_scale(t, o(3.6), 0.3))
            if t >= T_WAJIB:
                sc = 1.9 - 0.9 * ease_out((t - T_WAJIB) / 0.2)
                paste_center(base, WAJIB, W / 2, 560, sc)
                paste_center(base, BOX_CARD, 780, 900, pop_scale(t, T_WAJIB + 0.2, 0.4) * 0.85,
                             rot=6 + 2 * math.sin(t * 4))
                if t < T_WAJIB + 0.12:
                    glitch = 16
        # 50 counter
        if T50 <= t < TPRICE:
            n = int(round(50 * ease_out((t - T50) / 0.5)))
            num = text_img(str(n), 300, GOLD, 18, stroke_fill=DEEP)
            paste_center(base, num, W / 2, 600, pop_scale(t, T50, 0.25), rot=-4)
            paste_center(base, banner("KEPING SEKOTAK", 60, RED, WHITE), W / 2, 820, pop_scale(t, T50 + 0.3))
        # rolling price
        if TPRICE <= t < TPROOF:
            pn = panel(800, 520, bg=(255, 248, 235, 248), radius=30, border=GOLD)
            k = ease_out(min(max((t - PRICE_ROLL[0]) / PRICE_ROLL[1], 0), 1)) ** 1.3
            hi, lo = float(PRICE_OLD[2:]), float(PRICE[2:])
            v = hi + (lo - hi) * k
            lab = text_img("HARGA SEKARANG", 46, DEEP)
            old = strike(text_img(PRICE_OLD, 64, (150, 140, 135), path=FONT_BOLD)) if k >= 1 else \
                text_img(" ", 64, (0, 0, 0, 0), path=FONT_BOLD)
            val = text_img(f"RM{v:.2f}", 180, RED if k >= 1 else INK)
            content = stack_v([lab, old, val], gap=14)
            paste_center(pn, content, pn.width / 2, pn.height / 2)
            paste_center(base, pn, W / 2, 720, pop_scale(t, TPRICE, 0.3), rot=-2)
            if t >= T_DISC:
                sc = 1.8 - 0.8 * ease_out((t - T_DISC) / 0.2)
                paste_center(base, DISC_STAMP, 880, 470, sc * (1 + 0.04 * math.sin(t * 11)), rot=-12)
                if t < T_DISC + 0.12:
                    glitch = 20
            if t >= T_PER:
                paste_center(base, PER_PIECE_PILL, W / 2, 1050, pop_scale(t, T_PER), rot=2)
        # social proof
        if TPROOF <= t < o(14.8):
            lt = t - TPROOF
            paste_center(base, BUBBLE, W / 2, 560, pop_scale(lt, 0.0, 0.35))
            val = min(float(RATING), 5 * ease_out((lt - 0.4) / 0.8))
            row = stack_h([stars_fill(max(val, 0)), text_img(f"{max(val, 0):.1f}", 80, WHITE, 9)], gap=20)
            paste_center(base, row, W / 2, 860, pop_scale(lt, 0.35))
            sold = int(SOLD_N * ease_out((lt - 0.5) / 1.0)) if lt > 0.5 else 0
            paste_center(base, banner(f"{sold:,}+ TERJUAL • {REVIEWS} REVIEW", 46, RED, WHITE, emo="🔥"),
                         W / 2, 1010, pop_scale(lt, 0.5))
        # steps
        if t >= STEP_TIMES[0] and not T_GUIDE[0] <= t < T_GUIDE[1]:
            i = [j for j, t0 in enumerate(STEP_TIMES) if t0 <= t][-1]
            t0 = STEP_TIMES[i]
            num, txt = STEPS[i]
            k = ease_out((t - t0) / 0.35)
            if num in STEP_NUMS:
                ni = STEP_NUMS[num]
                tx = STEP_TXT[txt]
                row_w = ni.width - 30 + tx.width
                x0 = (W - row_w) / 2
                paste_center(base, tx, x0 + ni.width - 30 + tx.width / 2 + (1 - k) * 900, 270)
                paste_center(base, ni, x0 + ni.width / 2 - (1 - k) * 700, 270, rot=-360 * (1 - k))
            else:
                paste_center(base, banner(num, 44, RED, WHITE), W / 2, 190, pop_scale(t, t0))
                paste_center(base, STEP_TXT[txt], W / 2, 290, pop_scale(t, t0 + 0.1))
        # guide photo drops in and swings
        if T_GUIDE[0] <= t < T_GUIDE[1]:
            lt = t - T_GUIDE[0]
            y = 820 - 1400 * (1 - ease_out(lt / 0.35))
            ang = 9 * math.exp(-lt * 3) * math.cos(lt * 11)
            fade = min(1.0, (T_GUIDE[1] - t) / 0.15)
            paste_center(base, GUIDE, W / 2, y, 1.0, rot=ang - 2, alpha=fade)
        draw_word(base, t)
    elif t < T_CTA:
        draw_checklist(base, t - T_WHY, W / 2, 760)
    else:
        lt = t - T_CTA
        paste_center(base, C_TOP, W / 2, 190, pop_scale(lt, 0.0))
        cardk = pop_scale(lt, 0.1, 0.45)
        fc = glint(FEET_CARD, ((lt - 0.6) % 1.6) / 0.9) if lt > 0.6 else FEET_CARD
        paste_center(base, fc, W / 2, 610, cardk, rot=-2 + 1.5 * math.sin(t * 3))
        paste_center(base, DISC_STAMP, 880, 340, 0.75 * pop_scale(lt, 0.7), rot=-12)
        paste_center(base, C_OLD, W / 2, 1015, pop_scale(lt, 0.8))
        if lt >= 0.9:
            sc = 1.7 - 0.7 * ease_out((lt - 0.9) / 0.2)
            paste_center(base, C_PRICE, W / 2, 1150, sc * (1 + 0.025 * math.sin(t * 8)))
        paste_center(base, C_SUB, W / 2, 1285, pop_scale(lt, 1.15))
        paste_center(base, C_SHIP, W / 2, 1385, pop_scale(lt, 1.3))
        btn = C_BUY if lt < 1.6 else glint(C_BUY, ((lt - 1.6) % 1.2) / 0.8)
        paste_center(base, btn, W / 2, 1540, pop_scale(lt, 1.5) * (1 + 0.05 * math.sin(t * 9)))
        if lt > 1.8:
            paste_center(base, ARROW, W / 2, 1700 + 25 * abs(math.sin(t * 6)))
        draw_confetti(base, lt - 0.9)

    progress_bar(base, t)
    base = shake(base, t)
    if glitch:
        base = rgb_split(base, glitch)
    return base


# ---------------------------------------------------------------- main
def frames(tmp):
    """Yield the graded source frame for each output frame."""
    def reader(path):
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             stdout=subprocess.PIPE)
        while True:
            b = p.stdout.read(W * H * 3)
            if len(b) < W * H * 3:
                break
            yield Image.frombuffer("RGB", (W, H), b)
        p.wait()

    hook = list(reader(tmp + ".hook.mp4"))
    talk = reader(tmp + ".talk.mp4")
    n_hook = int(HOOK_LEN * FPS)
    for i, f in enumerate(talk):
        yield hook[min(i, len(hook) - 1)] if i < n_hook else f
    yield from reader(tmp + ".tail.mp4")


def main(src, dst):
    tmp = dst + ".tmp"
    render_base(src, tmp)
    write_wav(tmp + ".sfx.wav", build_sfx())
    n = int(round(TOTAL * FPS))
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", tmp + ".voice.wav", "-i", tmp + ".sfx.wav",
                           "-filter_complex",
                           "[1:a]volume=1.0[v];[2:a]volume=0.55[s];[v][s]amix=inputs=2:normalize=0,"
                           "loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "160k",
                           "-movflags", "+faststart", "-t", f"{n / FPS:.3f}", dst], stdin=subprocess.PIPE)
    for i, fr in enumerate(frames(tmp)):
        if i >= n:
            break
        wr.stdin.write(render_frame(fr, i / FPS).convert("RGB").tobytes())
        if (i + 1) % 150 == 0:
            print(f"{i + 1}/{n} frames", flush=True)
    wr.stdin.close()
    wr.wait()
    for ext in (".talk.mp4", ".hook.mp4", ".tail.mp4", ".voice.wav", ".sfx.wav"):
        os.remove(tmp + ext)
    print("done", dst, f"{TOTAL:.1f}s")


def preview(src, outdir, times):
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "pv")
    render_base(src, tmp)
    want = {int(tt * FPS): tt for tt in times}
    tiles = []
    for i, fr in enumerate(frames(tmp)):
        if i not in want:
            continue
        tt = want[i]
        im = render_frame(fr, tt).convert("RGB").resize((270, 480))
        ImageDraw.Draw(im).text((6, 14), f"{tt:.1f}", fill=(0, 255, 0), font=font(FONT_BLACK, 28))
        tiles.append(im)
    cols = 6
    sheet = Image.new("RGB", (270 * cols, 480 * math.ceil(len(tiles) / cols)))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
    sheet.save(os.path.join(outdir, "preview_v2.jpg"), quality=85)
    for ext in (".talk.mp4", ".hook.mp4", ".tail.mp4", ".voice.wav"):
        os.remove(tmp + ext)
    print("total", TOTAL)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[3] == "--preview":
        preview(sys.argv[1], sys.argv[2],
                [0.05, 0.4, 0.75, 1.5, 1.85, 3.3, 4.3, 5.2, 6.9, 7.6, 8.6, 9.5,
                 10.3, 11.4, 12.5, 14.0, 15.3, 16.6, 19.2, 20.6, 22.0, 23.6, 25.6, 28.5])
    else:
        main(sys.argv[1], sys.argv[2])
