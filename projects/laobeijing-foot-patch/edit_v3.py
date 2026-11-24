#!/usr/bin/env python3
"""Version 3 of the Laobeijing foot patch edit: "3 SEBAB" listicle in a card frame.

Usage:  python3 edit_v3.py SOURCE.mp4 OUTPUT.mp4
        python3 edit_v3.py SOURCE.mp4 PREVIEW_DIR --preview

Look and structure (different from v1 and v2):
  * The video plays inside a rounded card on a soft cream background made
    from a blurred copy of itself, with a header strip above it.
  * Hook: a note card types itself out, "barang bawah RM10 paling berbaloi
    aku beli 😭", with keyboard clicks.
  * Sebab #1 / #2 / #3 headers. A camera-shutter "snap" freezes key moments
    into small photos that collect in the corner.
  * Price as a till receipt that prints line by line and gets a stamp.
  * Two buyer reviews swipe in as cards.
  * How-to as a checklist in the header that ticks itself.
  * CTA: a product card; a finger taps the buy button (ripple + cha-ching).
  * Captions in TikTok's own "white box" text style.

Narration (PHRASES), helpers and sound synthesis come from edit.py / edit_v2.py.
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import edit as v1
import edit_v2 as v2
from edit import (FONT_BLACK, FONT_BOLD, PHRASES, PRICE, PRICE_OLD, DISCOUNT, RATING, REVIEWS, SOLD,
                  ease_out, ease_out_back, emoji, font, paste_center, pop_scale, stack_h, stack_v, strike,
                  text_img)

W, H, FPS = v1.W, v1.H, v1.FPS
SP = v1.SP
ASSETS = v1.ASSETS
FONT_MED = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
FONT_MONO_X = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"

CREAM = (250, 241, 228)
PAPER = (255, 253, 247)
INK = (28, 24, 22)
GREY = (125, 118, 110)
RED = (222, 36, 52)
GREEN = (22, 140, 80)
YEL = (255, 214, 64)
NOTE_TOP = (255, 205, 60)

TALK_A, TALK_B = 0.45, 25.45
TALK_LEN = (TALK_B - TALK_A) / SP
CTA_LEN = 4.8
TOTAL = TALK_LEN + CTA_LEN
T_CTA = TALK_LEN
PER_PIECE = v2.PER_PIECE


def o(ts):
    return (min(max(ts, TALK_A), TALK_B) - TALK_A) / SP


GRADE = "eq=contrast=1.04:saturation=1.12:brightness=0.03:gamma=1.04"

# card that holds the video
SCALE = 0.80
CW, CH = int(W * SCALE), int(H * SCALE)          # 864 x 1536
CX, CY = (W - CW) // 2, 330                        # top-left of card
RADIUS = 46

# section times (output seconds)
T_S1, T_S2, T_S3, T_HOW = o(6.8), o(9.3), o(12.0), o(14.8)
STEP_T = [o(17.4), o(18.6), o(22.5), o(24.4)]
T_GUIDE = (o(21.0), o(22.55))
SNAPS = [o(8.3), o(16.3), o(24.7)]
SECTIONS = [T_S1, T_S2, T_S3, T_HOW]


# ---------------------------------------------------------------- base
def render_base(src, dst):
    n = int(round(TALK_LEN * FPS))
    v2.ff("-ss", str(TALK_A), "-t", str(TALK_B - TALK_A), "-i", src,
          "-vf", f"setpts=(PTS-STARTPTS)/{SP},scale={W}:{H},fps={FPS},setsar=1,{GRADE}",
          "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", dst + ".talk.mp4")
    v2.ff("-ss", str(TALK_A), "-t", str(TALK_B - TALK_A), "-i", src, "-vn",
          "-af", f"atempo={SP},afade=t=in:d=0.04,afade=t=out:st={TALK_LEN - 0.1}:d=0.1,apad,atrim=0:{TOTAL}",
          "-ar", "44100", "-ac", "2", dst + ".voice.wav")


def frames(tmp):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", tmp + ".talk.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-"], stdout=subprocess.PIPE)
    last = None
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        last = Image.frombuffer("RGB", (W, H), b)
        yield last
    p.wait()
    n_cta = int(round(CTA_LEN * FPS)) + 2
    for _ in range(n_cta):
        yield last


# ---------------------------------------------------------------- sound
SR = v2.SR
TYPE_TEXT = "barang bawah RM10 paling berbaloi aku beli 😭"
TYPE_T0, TYPE_CPS = 0.25, 26.0      # start, characters per second


def sfx_shutter():
    n = int(0.16 * SR)
    r = np.random.RandomState(5).randn(n)
    e = np.zeros(n)
    for s in (0, int(0.07 * SR)):
        k = np.arange(n - s) / SR
        e[s:] += np.exp(-k / 0.012)
    return r * e * 0.6


def sfx_key(seed):
    n = int(0.03 * SR)
    r = np.random.RandomState(seed).randn(n)
    return r * v2._env(n, 0.0005, 0.005) * 0.3


def sfx_printer(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 95 * t)) * 0.12 + np.random.RandomState(6).randn(n) * 0.05
    gate = (np.sin(2 * np.pi * 9 * t) > -0.3).astype(float)
    return buzz * gate * np.minimum(1, (dur - t) * 8)


def build_sfx():
    out = np.zeros(int((TOTAL + 1) * SR))

    def add(t, s, g=1.0):
        i = int(max(t, 0) * SR)
        out[i:i + len(s)] += s[:len(out) - i] * g

    for i, ch in enumerate(TYPE_TEXT):
        if ch != " ":
            add(TYPE_T0 + i / TYPE_CPS, sfx_key(i), 0.8)
    add(TYPE_T0 + len(TYPE_TEXT) / TYPE_CPS + 0.05, v2.sfx_pop(), 0.6)
    for t in SECTIONS:
        add(t - 0.12, v2.sfx_whoosh(0.3), 0.45)
    for t in SNAPS:
        add(t, sfx_shutter(), 0.9)
    add(T_S2 + 0.15, sfx_printer(1.0), 0.5)
    add(T_S2 + 1.35, v2.sfx_hit(), 0.5)
    add(T_S2 + 1.4, v2.sfx_cash(), 0.7)
    add(T_S3 + 0.05, v2.sfx_whoosh(0.3), 0.5)
    add(T_S3 + 0.85, v2.sfx_whoosh(0.3), 0.5)
    for t in STEP_T:
        add(t + 0.15, v2.sfx_pop(), 0.5)
    add(T_GUIDE[0], v2.sfx_whoosh(0.3), 0.5)
    add(T_CTA, v2.sfx_whoosh(), 0.5)
    add(T_CTA + 1.95, v2.sfx_pop(), 0.8)
    add(T_CTA + 2.0, v2.sfx_cash(), 0.8)
    add(T_CTA + 2.1, v2.sfx_sparkle(), 0.5)
    return out / max(np.abs(out).max(), 1) * 0.6


# ---------------------------------------------------------------- shared drawing
def rr_mask(w, h, r):
    m = Image.new("L", (w, h))
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


CARD_MASK = rr_mask(CW, CH, RADIUS)


def shadowed(w, h, r, fill, blur=16, off=14, alpha=110, outline=None, ow=0):
    im = Image.new("RGBA", (w + 60, h + 70))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((30, 30 + off, 30 + w, 30 + off + h), r, fill=(60, 30, 10, alpha))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).rounded_rectangle((30, 30, 30 + w, 30 + h), r, fill=fill, outline=outline, width=ow)
    return im, 30


def chip(txt, size, bg, fg=(255, 255, 255), pad=(22, 10), emo=None, path=FONT_BLACK):
    t = text_img(txt, size, fg, path=path)
    e = emoji(emo, size) if emo else None
    ew = e.width + 10 if e else 0
    w, h = t.width + ew + 2 * pad[0], max(t.height, e.height if e else 0) + 2 * pad[1]
    im = Image.new("RGBA", (w, h))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg)
    x = pad[0]
    if e:
        im.alpha_composite(e, (x, (h - e.height) // 2))
        x += ew
    im.alpha_composite(t, (x, (h - t.height) // 2))
    return im


def wrap(txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        s = (cur + " " + w).strip()
        if f.getbbox(s)[2] > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = s
    lines.append(cur)
    return lines


def rich_line(txt, size, col, path):
    """Text that may end with one emoji."""
    parts = txt.split(" ")
    if parts and parts[-1] and ord(parts[-1][0]) > 0x2000:
        t = text_img(" ".join(parts[:-1]), size, col, path=path) if len(parts) > 1 else None
        e = emoji(parts[-1], int(size * 1.05))
        return stack_h([x for x in (t, e) if x], gap=12)
    return text_img(txt, size, col, path=path)


# ---------------------------------------------------------------- background + card
def background(fr):
    bg = fr.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    return Image.blend(bg, Image.new("RGB", (W, H), CREAM), 0.62).convert("RGBA")


CARD_SHADOW = Image.new("RGBA", (W, H))
ImageDraw.Draw(CARD_SHADOW).rounded_rectangle((CX - 2, CY + 18, CX + CW + 2, CY + CH + 22), RADIUS + 8,
                                              fill=(70, 35, 10, 120))
CARD_SHADOW = CARD_SHADOW.filter(ImageFilter.GaussianBlur(22))
CARD_BORDER = Image.new("RGBA", (W, H))
ImageDraw.Draw(CARD_BORDER).rounded_rectangle((CX - 10, CY - 10, CX + CW + 10, CY + CH + 10), RADIUS + 10,
                                              fill=(255, 255, 255, 255))


def place_card(base, fr, t):
    # small bounce at each section change
    s = 1.0
    for ts in SECTIONS:
        if ts <= t < ts + 0.35:
            s = 0.965 + 0.035 * ease_out_back((t - ts) / 0.35)
    base.alpha_composite(CARD_SHADOW)
    inner = fr.resize((CW, CH), Image.BILINEAR).convert("RGBA")
    inner.putalpha(CARD_MASK)
    if s != 1.0:
        layer = Image.new("RGBA", (W, H))
        layer.alpha_composite(CARD_BORDER)
        layer.alpha_composite(inner, (CX, CY))
        lw, lh = int(W * s), int(H * s)
        layer = layer.resize((lw, lh), Image.BILINEAR)
        cy = CY + CH / 2
        base.alpha_composite(layer, (int((W - lw) / 2), int(cy - cy * s)))
    else:
        base.alpha_composite(CARD_BORDER)
        base.alpha_composite(inner, (CX, CY))


# ---------------------------------------------------------------- header strip
def header_img(kicker, title, kicker_bg=RED):
    k = chip(kicker, 34, kicker_bg, pad=(20, 8))
    t = rich_line(title, 66, INK, FONT_BLACK)
    return stack_v([k, t], gap=14, align="left")


HEADERS = [
    (T_S1, header_img("SEBAB #1", "50 keping sekotak 📦")),
    (T_S2, header_img("SEBAB #2", "Harga memang tak mahal 💸")),
    (T_S3, header_img("SEBAB #3", "Selesa + review padu ⭐")),
    (T_HOW, header_img("CARA PAKAI", "Senang je, 4 langkah 👣", GREEN)),
]
COUNTER = {T_S1: "1/3", T_S2: "2/3", T_S3: "3/3"}


def draw_header(base, t):
    cur = [h for h in HEADERS if h[0] <= t]
    if not cur:
        return
    t0, im = cur[-1]
    k = ease_out((t - t0) / 0.3)
    if len(cur) > 1 and t < t0 + 0.3:  # previous header slides up and out
        prev = cur[-2][1]
        paste_center(base, prev, 70 + prev.width / 2, 200 - 120 * k, alpha=1 - k)
    paste_center(base, im, 70 + im.width / 2, 200 + 120 * (1 - k), alpha=k)
    if t0 in COUNTER:
        c = chip(COUNTER[t0], 36, INK, pad=(20, 8))
        paste_center(base, c, W - 90 - c.width / 2 + 0, 140, pop_scale(t, t0 + 0.1, 0.3))


# ---------------------------------------------------------------- hook note (typewriter)
def note_card(n_chars, cursor):
    w = 900
    f = font(FONT_BOLD, 60)
    txt = TYPE_TEXT[:n_chars]
    lines = wrap(TYPE_TEXT, f, w - 100)
    # wrap the full text once so lines do not jump while typing
    shown, left = [], len(txt)
    for ln in lines:
        take = min(left, len(ln))
        shown.append(ln[:take])
        left -= take + 1 if take == len(ln) else take
        if left <= 0:
            break
    body_h = 74 * len(lines)
    h = 110 + body_h + 50
    im, m = shadowed(w, h, 34, PAPER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((m, m, m + w, m + 86), 34, fill=NOTE_TOP)
    d.rectangle((m, m + 50, m + w, m + 86), fill=NOTE_TOP)
    hdr = text_img("nota", 40, INK, path=FONT_BLACK)
    im.alpha_composite(emoji("📝", 44), (m + 32, m + 20))
    im.alpha_composite(hdr, (m + 92, m + 22))
    for i in range(3):
        d.ellipse((m + w - 150 + i * 40, m + 32, m + w - 126 + i * 40, m + 56), fill=(255, 255, 255, 170))
    y = m + 118
    for i, ln in enumerate(shown):
        if ln:
            li = rich_line(ln, 60, INK, FONT_BOLD) if ord(ln[-1]) > 0x2000 else text_img(ln, 60, INK, path=FONT_BOLD)
            im.alpha_composite(li, (m + 50, y + i * 74))
            if cursor and i == len(shown) - 1:
                d.rectangle((m + 50 + li.width + 6, y + i * 74, m + 50 + li.width + 12, y + i * 74 + 60), fill=RED)
        elif cursor:
            d.rectangle((m + 50, y + i * 74, m + 56, y + i * 74 + 60), fill=RED)
    return im


NOTE_DONE = None


def draw_hook(base, t):
    global NOTE_DONE
    if t >= T_S1:
        return
    n = int((t - TYPE_T0) * TYPE_CPS) if t > TYPE_T0 else 0
    done = n >= len(TYPE_TEXT)
    cursor = (int(t * 3) % 2 == 0) or not done
    if done and not cursor:
        if NOTE_DONE is None:
            NOTE_DONE = note_card(len(TYPE_TEXT), False)
        im = NOTE_DONE
    else:
        im = note_card(min(n, len(TYPE_TEXT)), cursor)
    k = ease_out_back(t / 0.3)
    fade = min(1, (T_S1 - t) / 0.2)
    paste_center(base, im, W / 2, 330, k, rot=-1.5, alpha=fade)
    if done:
        tdone = TYPE_T0 + len(TYPE_TEXT) / TYPE_CPS
        tag = chip(f"cuma {PRICE} • 50 keping", 46, RED, pad=(28, 14), emo="🔥")
        paste_center(base, tag, W / 2 + 120, 560, pop_scale(t, tdone + 0.05) * (1 + 0.03 * math.sin(t * 9)),
                     rot=3, alpha=fade)


# ---------------------------------------------------------------- snaps (polaroids collected in a corner)
def polaroid(fr, w=420):
    img = fr.resize((w, int(w * H / W)), Image.BILINEAR).crop((0, int(w * 0.25), w, int(w * 0.25) + w))
    pad, bot = 18, 60
    im, m = shadowed(w + 2 * pad, w + pad + bot, 8, (255, 255, 255), blur=10, off=10, alpha=120)
    im.paste(img, (m + pad, m + pad))
    return im


SNAP_POS = [(910, 1400, 8), (935, 1330, -6), (905, 1260, 5)]   # resting spots (bottom-right of card)


def draw_snaps(base, t, snaps):
    for i, ts in enumerate(SNAPS):
        if t < ts or i not in snaps:
            continue
        lt = t - ts
        pol = snaps[i]
        ex, ey, er = SNAP_POS[i]
        if lt < 0.12:   # flash
            a = 1 - lt / 0.12
            base.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * a))))
        k = ease_out((lt - 0.45) / 0.45)
        sc = 1.25 + (0.42 - 1.25) * k
        x = W / 2 + (ex - W / 2) * k
        y = CY + CH / 2 - 120 + (ey - (CY + CH / 2 - 120)) * k
        paste_center(base, pol, x, y, sc * min(1, ease_out_back(lt / 0.2)), rot=-4 + (er + 4) * k)


# ---------------------------------------------------------------- receipt
def receipt_full():
    w = 640
    mono = lambda s, sz=38, c=INK: text_img(s, sz, c, path=FONT_MONO)
    rows = []

    def row(l, r, sz=38, c=INK, path=FONT_MONO):
        li, ri = text_img(l, sz, c, path=path), text_img(r, sz, c, path=path)
        im = Image.new("RGBA", (w - 80, max(li.height, ri.height)))
        im.alpha_composite(li, (0, 0))
        im.alpha_composite(ri, (im.width - ri.width, 0))
        return im

    hi, lo = float(PRICE_OLD[2:]), float(PRICE[2:])
    rows += [text_img("RESIT BELIAN", 46, INK, path=FONT_MONO_X), mono("--------------------------", 34, GREY),
             row("Tampalan kaki", ""), row("  50 keping x1", PRICE_OLD),
             row(f"Diskaun {DISCOUNT}", f"-RM{hi - lo:.2f}", c=RED),
             row("Penghantaran", "PERCUMA", c=GREEN),
             mono("--------------------------", 34, GREY),
             row("JUMLAH", PRICE, 60, INK, FONT_MONO_X),
             mono(f"= {PER_PIECE} sekeping", 34, GREY), mono("terima kasih :)", 30, GREY)]
    hs = [r.height for r in rows]
    h = sum(hs) + 18 * len(rows) + 90
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    # paper with zigzag bottom
    d.rectangle((0, 0, w, h - 24), fill=PAPER)
    zz = [(0, h - 24)]
    for i in range(0, w + 1, 32):
        zz += [(i + 16, h - 4), (i + 32, h - 24)]
    d.polygon(zz + [(w, h - 24)], fill=PAPER)
    y = 50
    offs = []
    for r in rows:
        x = (w - r.width) // 2 if r.width < w - 80 else 40
        im.alpha_composite(r, (x, y))
        offs.append(y + r.height)
        y += r.height + 18
    return im, offs


RECEIPT, RECEIPT_ROWS = receipt_full()
STAMP = None


def make_stamp():
    t = text_img("BERBALOI!", 84, RED, path=FONT_BLACK)
    im = Image.new("RGBA", (t.width + 60, t.height + 50))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, im.width - 5, im.height - 5), 18, outline=RED, width=8)
    im.alpha_composite(t, (30, 25))
    im = im.rotate(-14, expand=True, resample=Image.BICUBIC)
    a = np.array(im)
    noise = np.random.RandomState(9).rand(*a.shape[:2]) > 0.12   # worn ink
    a[..., 3] = (a[..., 3] * noise * 0.9).astype(np.uint8)
    return Image.fromarray(a)


STAMP = make_stamp()


def draw_receipt(base, t):
    if not (T_S2 <= t < T_S3):
        return
    lt = t - T_S2
    k = min(1, max(0, (lt - 0.15) / 1.0))
    shown_h = int(RECEIPT.height * k)
    if shown_h < 4:
        return
    top = 470
    # printer slot
    slot = Image.new("RGBA", (720, 40))
    ImageDraw.Draw(slot).rounded_rectangle((0, 0, 719, 39), 20, fill=(45, 40, 38))
    paste_center(base, slot, W / 2, top - 10, pop_scale(lt, 0.0, 0.25))
    piece = RECEIPT.crop((0, RECEIPT.height - shown_h, RECEIPT.width, RECEIPT.height))
    sh = Image.new("RGBA", (piece.width + 60, piece.height + 60))
    ImageDraw.Draw(sh).rectangle((30, 40, 30 + piece.width, 30 + piece.height), fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    base.alpha_composite(sh, (int(W / 2 - piece.width / 2 - 30), top - 30))
    base.alpha_composite(piece, (int(W / 2 - piece.width / 2), top))
    if lt >= 1.35:
        s = 1.8 - 0.8 * ease_out((lt - 1.35) / 0.18)
        paste_center(base, STAMP, W / 2 + 210, top + RECEIPT.height - 20, s)


# ---------------------------------------------------------------- reviews (swipe cards)
def review(stars_n, text, who, w=820):
    f = font(FONT_BOLD, 46)
    lines = wrap(text, f, w - 100)
    body = [text_img(ln, 46, INK, path=FONT_BOLD) for ln in lines]
    st = stack_h([emoji("⭐", 42) for _ in range(stars_n)], gap=4)
    whoi = text_img(who, 32, GREY, path=FONT_MED)
    content = stack_v([st] + body + [whoi], gap=14, align="left")
    im, m = shadowed(w, content.height + 80, 32, (255, 255, 255))
    im.alpha_composite(content, (m + 50, m + 40))
    return im


REVIEW_A = review(5, "“Malam sebelum tidur pakai… bangun tidur rasa ringan badan dan tapak kaki kurang sakit”",
                  "pembeli • 50 keping")
REVIEW_B = review(5, "“Produk memang best, fast delivery, bau herba gitu”", "pembeli • review 5 bintang")
RATING_CHIP = chip(f"{RATING} • {REVIEWS} review • {SOLD} terjual", 42, INK, pad=(28, 14), emo="⭐")


def draw_reviews(base, t):
    if not (T_S3 <= t < T_HOW):
        return
    lt = t - T_S3
    for i, (im, t0, y, rot) in enumerate([(REVIEW_A, 0.05, 640, -3), (REVIEW_B, 0.85, 930, 2.5)]):
        if lt < t0:
            continue
        k = ease_out_back((lt - t0) / 0.4)
        paste_center(base, im, W / 2 + (1 - k) * 1100, y, 1.0, rot=rot * k)
    paste_center(base, RATING_CHIP, W / 2, 1160, pop_scale(lt, 1.4))


# ---------------------------------------------------------------- how-to checklist + guide
STEPS = ["Koyak sticker besar", "Letak pad, bunga di luar", "Tampal di tapak kaki", "Pakai masa tidur 😴"]


def checklist_img(n_done, tick_k):
    rows = []
    for i, s in enumerate(STEPS):
        done = i < n_done or (i == n_done and tick_k >= 1)
        active = i == n_done
        col = GREY if (i < n_done) else INK
        box = Image.new("RGBA", (52, 52))
        d = ImageDraw.Draw(box)
        if i < n_done or (active and tick_k > 0):
            d.rounded_rectangle((0, 0, 51, 51), 12, fill=GREEN)
            k = 1 if i < n_done else tick_k
            p = [(12, 27), (22, 38), (41, 14)]
            m1 = min(k * 2, 1)
            d.line([p[0], (p[0][0] + (p[1][0] - p[0][0]) * m1, p[0][1] + (p[1][1] - p[0][1]) * m1)], fill="white",
                   width=7)
            if k > 0.5:
                m2 = (k - 0.5) * 2
                d.line([p[1], (p[1][0] + (p[2][0] - p[1][0]) * m2, p[1][1] + (p[2][1] - p[1][1]) * m2)],
                       fill="white", width=7)
        else:
            d.rounded_rectangle((2, 2, 49, 49), 12, outline=(190, 180, 170), width=5)
        label = rich_line(f"{i + 1}. {s}", 42, col if not active else INK, FONT_BOLD if active else FONT_MED)
        if i < n_done:
            label = strike(label, (160, 150, 140), 4)
        rows.append(stack_h([box, label], gap=20))
        _ = done
    content = stack_v(rows, gap=16, align="left")
    w = content.width + 90
    im, m = shadowed(w, content.height + 60, 30, (255, 255, 255, 245))
    im.alpha_composite(content, (m + 45, m + 30))
    return im


_ck = {}


def draw_howto(base, t):
    if not (T_HOW <= t < T_CTA):
        return
    passed = [i for i, ts in enumerate(STEP_T) if ts <= t]
    n_done = len(passed) - 1 if passed else -1
    # active step is the latest started; it ticks during its first 0.4 s
    if passed:
        cur = passed[-1]
        tick = min(1, (t - STEP_T[cur]) / 0.4)
        key = (cur, round(tick, 2))
        if key not in _ck:
            _ck[key] = checklist_img(cur, tick)
        im = _ck[key]
    else:
        key = (-1, 0)
        if key not in _ck:
            _ck[key] = checklist_img(0, 0)
        im = _ck[key]
    _ = n_done
    k = ease_out_back((t - T_HOW) / 0.4)
    paste_center(base, im, W / 2, 640, k)
    if T_GUIDE[0] <= t < T_GUIDE[1]:
        lt = t - T_GUIDE[0]
        g = GUIDE_CARD
        kk = ease_out((lt) / 0.3)
        fade = min(1, (T_GUIDE[1] - t) / 0.15)
        paste_center(base, g, W / 2 - (1 - kk) * 1100, 1120, 1.0, rot=-2 * kk, alpha=fade)


def guide_card():
    img = Image.open(os.path.join(ASSETS, "caraguna.png")).convert("RGBA")
    w = 760
    img = img.resize((w, int(w * img.height / img.width)), Image.LANCZOS)
    img.putalpha(rr_mask(img.width, img.height, 24))
    im, m = shadowed(w + 24, img.height + 24, 30, (255, 255, 255))
    im.alpha_composite(img, (m + 12, m + 12))
    return im


GUIDE_CARD = guide_card()


# ---------------------------------------------------------------- captions (TikTok "white box" text)
def build_caps():
    caps = []
    for a, b, txt in PHRASES:
        caps.append([o(a), o(b), txt])
    for i in range(len(caps) - 1):
        caps[i][1] = caps[i + 1][0]
    caps[-1][1] = T_CTA
    return caps


CAPS = build_caps()
_cap = {}


def cap_img(txt):
    if txt not in _cap:
        t = text_img(txt, 54, INK, path=FONT_BOLD)
        if t.width > CW - 120:
            t = t.resize((CW - 120, int(t.height * (CW - 120) / t.width)), Image.LANCZOS)
        im = Image.new("RGBA", (t.width + 52, t.height + 34))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 16, fill=(255, 255, 255, 240))
        im.alpha_composite(t, (26, 17))
        _cap[txt] = im
    return _cap[txt]


def draw_caption(base, t):
    c = next((c for c in CAPS if c[0] <= t < c[1]), None)
    if c:
        paste_center(base, cap_img(c[2]), W / 2, CY + CH - 150, 0.85 + 0.15 * ease_out((t - c[0]) / 0.15))


# ---------------------------------------------------------------- CTA (product card + tap)
def product_card():
    w = 860
    img = Image.open(os.path.join(ASSETS, "feet.png")).convert("RGBA")
    img = img.resize((w - 240, int((w - 240) * img.height / img.width)), Image.LANCZOS)
    img.putalpha(rr_mask(img.width, img.height, 24))
    title1 = text_img("Tampalan Kaki Herba", 54, INK, path=FONT_BLACK)
    title2 = text_img("Laobeijing • 50 keping / kotak", 40, GREY, path=FONT_MED)
    rate = stack_h([emoji("⭐", 38), text_img(f"{RATING}  ({REVIEWS})  •  {SOLD} terjual", 38, INK, path=FONT_MED)],
                   gap=10)
    price = stack_h([text_img(PRICE, 96, RED, path=FONT_BLACK),
                     strike(text_img(PRICE_OLD, 44, GREY, path=FONT_MED), GREY, 4),
                     chip(DISCOUNT, 38, RED, pad=(16, 6))], gap=20)
    ship = chip("Free shipping", 36, (230, 246, 236), GREEN, pad=(18, 8), emo="🚚", path=FONT_BOLD)
    top = Image.new("RGBA", (w - 60, img.height))
    top.alpha_composite(img, ((w - 60 - img.width) // 2, 0))
    content = stack_v([top, title1, title2, rate, price, ship], gap=16, align="left")
    h = content.height + 60 + 150
    im, m = shadowed(w, h, 40, (255, 255, 255))
    im.alpha_composite(content, (m + 30, m + 30))
    btn_box = (m + 30, m + h - 140, m + w - 30, m + h - 30)
    return im, btn_box


PCARD, BTN = product_card()


def button(pressed, glow):
    w, h = BTN[2] - BTN[0], BTN[3] - BTN[1]
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    col = (190, 20, 35) if pressed else RED
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=col)
    t = stack_h([emoji("🛒", 50), text_img("Beli sekarang", 54, (255, 255, 255), path=FONT_BLACK)], gap=16)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    if glow > 0:
        r = int(glow * w * 0.6)
        g = Image.new("RGBA", (w, h))
        ImageDraw.Draw(g).ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                                  fill=(255, 255, 255, int(150 * (1 - glow))))
        g.putalpha(Image.fromarray(np.minimum(np.array(g.getchannel("A")), np.array(rr_mask(w, h, h // 2)))))
        im.alpha_composite(g)
    return im


HAND = emoji("👆", 130)
CTA_TOP = text_img("Nak cuba? Tekan beg kuning 👇".replace(" 👇", ""), 62, INK, path=FONT_BLACK)


def draw_cta(base, t):
    lt = t - T_CTA
    k = ease_out_back(lt / 0.45)
    tap = 1.95
    pressed = tap <= lt < tap + 0.15
    glow = (lt - tap) / 0.5 if tap <= lt < tap + 0.5 else 0
    card = PCARD.copy()
    bw = button(pressed, glow)
    s = 0.95 if pressed else 1.0 + (0.03 * math.sin(lt * 8) if lt > tap + 0.5 else 0)
    if s != 1.0:
        bw = bw.resize((int(bw.width * s), int(bw.height * s)), Image.BILINEAR)
    bx = (BTN[0] + BTN[2]) // 2 - bw.width // 2
    by = (BTN[1] + BTN[3]) // 2 - bw.height // 2
    card.alpha_composite(bw, (bx, by))
    cy = 950
    paste_center(base, card, W / 2, cy + (1 - min(k, 1)) * 600, 1.0)
    top_y = cy - card.height / 2 - 70
    head = stack_h([CTA_TOP, emoji("👇", 64)], gap=14)
    paste_center(base, head, W / 2, top_y, pop_scale(lt, 0.3))
    # finger moves in, taps, then rests
    btn_cx = W / 2 - card.width / 2 + (BTN[0] + BTN[2]) / 2
    btn_cy = cy - card.height / 2 + (BTN[1] + BTN[3]) / 2
    if lt > 1.0:
        m = ease_out((lt - 1.0) / 0.8)
        hx = btn_cx + 160 + (1 - m) * 250
        hy = btn_cy + 80 + (1 - m) * 500
        if tap - 0.1 <= lt < tap + 0.2:
            hy -= 14 * math.sin(math.pi * (lt - tap + 0.1) / 0.3)
        paste_center(base, HAND, hx, hy, 1.0, rot=10)
    if lt > tap + 0.4:
        tag = chip("Hantar dalam 24 jam", 42, GREEN, pad=(26, 12), emo="⚡")
        paste_center(base, tag, W / 2, cy + card.height / 2 + 30, pop_scale(lt, tap + 0.4))


# ---------------------------------------------------------------- frame
def render_frame(fr, t, snaps):
    if t < T_CTA:
        base = background(fr)
        place_card(base, fr, t)
        draw_header(base, t)
        draw_hook(base, t)
        draw_receipt(base, t)
        draw_reviews(base, t)
        draw_howto(base, t)
        draw_caption(base, t)
        draw_snaps(base, t, snaps)
    else:
        base = background(fr)
        base.alpha_composite(Image.new("RGBA", (W, H), CREAM + (120,)))
        if t < T_CTA + 0.3:  # card shrinks away
            k = ease_out((t - T_CTA) / 0.3)
            small = fr.resize((CW, CH), Image.BILINEAR).convert("RGBA")
            small.putalpha(CARD_MASK)
            paste_center(base, small, W / 2, CY + CH / 2, 1 - 0.9 * k, alpha=1 - k)
        draw_cta(base, t)
    if t < 0.08:
        base = Image.blend(base, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 1 - t / 0.08)
    return base


# ---------------------------------------------------------------- main
SNAP_FRAMES = [int(round(s * FPS)) for s in SNAPS]


def run(src, tmp, want, sink):
    snaps = {}
    n = int(round(TOTAL * FPS))
    for i, fr in enumerate(frames(tmp)):
        if i >= n:
            break
        if i in SNAP_FRAMES:
            snaps[SNAP_FRAMES.index(i)] = polaroid(fr)
        if want is None or i in want:
            sink(i, render_frame(fr, i / FPS, snaps))


def main(src, dst):
    tmp = dst + ".tmp"
    render_base(src, tmp)
    v2.write_wav(tmp + ".sfx.wav", build_sfx())
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

    def sink(i, im):
        wr.stdin.write(im.convert("RGB").tobytes())
        if (i + 1) % 150 == 0:
            print(f"{i + 1}/{n} frames", flush=True)

    run(src, tmp, None, sink)
    wr.stdin.close()
    wr.wait()
    for ext in (".talk.mp4", ".voice.wav", ".sfx.wav"):
        os.remove(tmp + ext)
    print("done", dst, f"{TOTAL:.1f}s")


def preview(src, outdir, times):
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "pv3")
    render_base(src, tmp)
    want = {int(tt * FPS): tt for tt in times}
    tiles = []

    def sink(i, im):
        im = im.convert("RGB").resize((270, 480))
        ImageDraw.Draw(im).text((6, 6), f"{i / FPS:.1f}", fill=(0, 160, 0), font=font(FONT_BLACK, 28))
        tiles.append(im)

    run(src, tmp, want, sink)
    cols = 6
    sheet = Image.new("RGB", (270 * cols, 480 * math.ceil(len(tiles) / cols)))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
    sheet.save(os.path.join(outdir, "preview_v3.jpg"), quality=85)
    for ext in (".talk.mp4", ".voice.wav"):
        os.remove(tmp + ext)
    print("total", TOTAL)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[3] == "--preview":
        preview(sys.argv[1], sys.argv[2],
                [0.1, 0.8, 1.6, 2.5, 4.5, 6.0, 7.3, 7.9, 8.6, 9.2, 10.0, 9.8,
                 12.0, 12.8, 14.2, 14.5, 17.0, 19.0, 21.0, 22.4, 23.6, 25.0, 25.8, 27.2])
    else:
        main(sys.argv[1], sys.argv[2])
