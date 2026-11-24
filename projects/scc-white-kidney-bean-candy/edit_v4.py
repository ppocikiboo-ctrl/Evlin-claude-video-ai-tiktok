#!/usr/bin/env python3
"""Version 4: "almari" (wardrobe) concept, aesthetic pastel style.

Same agreed wording as v2/v3 (no voice, no "craving", no reviews, layered lines),
different look:
  * wardrobe doors closed on the hook, swing open to reveal the video,
    and close again on the CTA at the end (seamless TikTok loop)
  * word-by-word kinetic captions
  * product freeze-frame dropped in as a tilted polaroid with tape
  * CARA MAKAN as a 2x2 grid of drawn icons (water drop fills up)
  * varied xfade transitions between shots, dreamy glow + lilac grade
  * bouncing yellow shopping-bag CTA

Usage: python3 edit_v4.py <input.mp4> <out-without-.mp4>
Writes <out>.mp4 (music + sfx) and <out>-nosound.mp4.
"""
import math
import os
import random
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from edit import DEEP, FONT_BLACK, FONT_BOLD, FPS, H, PINK, W, WHITE, YELLOW, font, text_card
from edit_v2 import music
from edit_v3 import (Card, Leaks, Sparkles, clamp, ease_out_back, ease_out_cubic,
                     paste, sfx)

SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
SPEED = 1.10
XF = 0.35  # crossfade length
SEGMENTS = [(0.43, 7.00), (7.00, 14.40), (14.40, 17.10), (17.10, 20.30),
            (20.30, 23.20), (23.20, 29.60), (29.60, 33.60), (33.60, 35.55)]
ZOOM0 = [1.00, 1.05, 1.00, 1.06, 1.02, 1.05, 1.00, 1.04]
TRANS = ["circleopen", "smoothleft", "radial", "smoothup", "zoomin", "slideleft", "fadewhite"]
LILAC = (196, 160, 230)
BLUSH = (255, 214, 228)
CREAM = (255, 248, 240)
DOOR = (246, 196, 214)
DOOR_IN = (250, 214, 228)
GOLD = (214, 170, 80)
random.seed(11)


def ease_in_out(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((70, 70), ch, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)


# ---------------- wardrobe doors ----------------
def door_img(left):
    w = W // 2
    im = Image.new("RGBA", (w, H), DOOR + (255,))
    d = ImageDraw.Draw(im)
    # wood-ish vertical grain
    for x in range(0, w, 6):
        c = 6 * math.sin(x * 0.07) + 4 * math.sin(x * 0.31)
        d.line([(x, 0), (x, H)], fill=tuple(int(v + c) for v in DOOR) + (255,), width=6)
    m = 60
    d.rounded_rectangle((m, 120, w - m, 900), 30, fill=DOOR_IN + (255,), outline=(232, 170, 196), width=8)
    d.rounded_rectangle((m, 980, w - m, H - 120), 30, fill=DOOR_IN + (255,), outline=(232, 170, 196), width=8)
    hx = w - 40 if left else 40
    d.rounded_rectangle((hx - 12, 860, hx + 12, 1060), 12, fill=GOLD + (255,), outline=(160, 120, 50), width=3)
    # seam shadow
    sh = Image.new("RGBA", (40, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(40):
        sd.line([(i, 0), (i, H)], fill=(120, 60, 90, int(90 * (1 - i / 40))))
    if left:
        sh = sh.transpose(Image.FLIP_LEFT_RIGHT)
        im.alpha_composite(sh, (w - 40, 0))
    else:
        im.alpha_composite(sh, (0, 0))
    return im


class Doors:
    """Closed until open_t, swing open over 0.8s; close again from close_t."""

    def __init__(self, open_t, close_t, total, text_open, text_close):
        self.L, self.R = door_img(True), door_img(False)
        self.open_t, self.close_t, self.total = open_t, close_t, total
        self.text_open, self.text_close = text_open, text_close

    def frac(self, t):  # 0 = closed, 1 = fully open
        if t < self.open_t:
            return 0.0
        if t < self.close_t:
            return ease_in_out(clamp((t - self.open_t) / 0.8))
        return 1 - ease_in_out(clamp((t - self.close_t) / 0.6))

    def draw(self, canvas, t):
        f = self.frac(t)
        if f >= 0.999:
            return
        w = W // 2
        # perspective-ish: door shrinks in width as it swings
        lw = max(1, int(w * (1 - f)))
        L = self.L.resize((lw, H), Image.BILINEAR)
        R = self.R.resize((lw, H), Image.BILINEAR)
        shade = int(120 * f)
        if shade:
            dark = Image.new("RGBA", (lw, H), (60, 20, 40, shade))
            L = Image.alpha_composite(L, dark)
            R = Image.alpha_composite(R, dark)
        paste(canvas, L, 0, 0)
        paste(canvas, R, W - lw, 0)
        if t < self.close_t:
            txt, a = self.text_open, clamp(1 - f * 3)
        else:
            txt, a = self.text_close, clamp((t - self.close_t - 0.35) / 0.25)
        if txt is not None and a > 0:
            im = txt
            if a < 1:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
            paste(canvas, im, (W - im.width) // 2, (H - im.height) // 2 - 80)


def door_text(lines, sub=None, emo=None, fill=DEEP):
    f = font(SERIF, 104)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lh = 128
    width = max(d.textlength(l, font=f) for l in lines)
    if sub:
        width = max(width, d.textlength(sub, font=font(FONT_BLACK, 52)))
    hgt = lh * len(lines) + (90 if sub else 0) + (170 if emo else 0)
    im = Image.new("RGBA", (int(width) + 120, hgt + 80), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 50, fill=CREAM + (235,))
    y = 40
    if emo:
        e = emoji(emo, 140)
        im.alpha_composite(e, ((im.width - e.width) // 2, y))
        y += 170
    for l in lines:
        dr.text((im.width // 2, y + lh // 2), l, font=f, fill=fill, anchor="mm")
        y += lh
    if sub:
        dr.text((im.width // 2, y + 40), sub, font=font(FONT_BLACK, 52), fill=PINK, anchor="mm")
    return im


# ---------------- kinetic words ----------------
class Words:
    """Words pop in one by one; `hl` words get a coloured highlight box."""

    def __init__(self, lines, t0, t1, y, step=0.16, size=96, hl=(), hl_color=PINK, serif=False):
        self.t0, self.t1, self.y = t0, t1, y
        f = font(SERIF if serif else FONT_BLACK, size)
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        self.words = []  # (img, x, y, t)
        k = 0
        lh = int(size * 1.35)
        for li, line in enumerate(lines):
            ws = line.split(" ")
            imgs = []
            for wd in ws:
                tw = int(d.textlength(wd, font=f))
                im = Image.new("RGBA", (tw + 40, lh + 10), (0, 0, 0, 0))
                dr = ImageDraw.Draw(im)
                is_hl = wd.strip(",.'?!") in hl or wd in hl
                if is_hl:
                    dr.rounded_rectangle((4, 8, tw + 36, lh), 18, fill=hl_color + (255,))
                    dr.text((20, lh // 2 + 4), wd, font=f, fill=WHITE, anchor="lm")
                else:
                    dr.text((20, lh // 2 + 4), wd, font=f, fill=WHITE, anchor="lm",
                            stroke_width=8, stroke_fill=(40, 10, 30))
                imgs.append(im)
            total_w = sum(i.width for i in imgs) - 16 * (len(imgs) - 1)
            x = (W - total_w) // 2
            for im in imgs:
                self.words.append((im, x, y + li * lh, t0 + k * step))
                x += im.width - 16
                k += 1

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        out = clamp((self.t1 - t) / 0.2)
        for im, x, y, tw in self.words:
            if t < tw:
                continue
            p = clamp((t - tw) / 0.28)
            s = 0.2 + 0.8 * ease_out_back(p)
            a = min(clamp((t - tw) / 0.1), out)
            img = im
            if abs(s - 1) > 1e-3:
                img = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
            if a < 1:
                img = img.copy()
                img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
            paste(canvas, img, x + (im.width - img.width) // 2, y + (im.height - img.height) // 2)


# ---------------- polaroid ----------------
class Polaroid:
    def __init__(self, photo, t0, t1, caption):
        pw = 640
        ph = int(photo.height * pw / photo.width)
        ph = min(ph, 760)
        photo = photo.resize((pw, int(photo.height * pw / photo.width)), Image.LANCZOS).crop((0, 0, pw, ph))
        card = Image.new("RGBA", (pw + 60, ph + 220), WHITE + (255,))
        card.paste(photo, (30, 30))
        d = ImageDraw.Draw(card)
        f = font(SERIF, 46)
        for i, ln in enumerate(caption):
            d.text((card.width // 2, ph + 85 + i * 58), ln, font=f, fill=DEEP, anchor="mm")
        # tape
        tape = Image.new("RGBA", (200, 60), (255, 230, 150, 190))
        tape = tape.rotate(-8, expand=True, resample=Image.BICUBIC)
        card.alpha_composite(tape, (card.width // 2 - tape.width // 2, 0))
        sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((40, 50, card.width + 40, card.height + 50), fill=(0, 0, 0, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        sh.alpha_composite(card, (40, 30))
        self.img, self.t0, self.t1 = sh, t0, t1

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        lt = t - self.t0
        p = clamp(lt / 0.55)
        ang = -24 + 18 * ease_out_back(p) + 1.2 * math.sin(lt * 2.2)
        y = int(-1300 + 1560 * ease_out_back(p))
        out = clamp((self.t1 - t) / 0.25)
        im = self.img.rotate(ang, expand=True, resample=Image.BICUBIC)
        if out < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * out)))
            y -= int(200 * (1 - out))
        paste(canvas, im, (W - im.width) // 2, y)


# ---------------- icon grid ----------------
def icon_tile(kind, l1, l2, fill_level=1.0):
    tw, th = 430, 330
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw - 1, th - 1), 40, fill=CREAM + (245,), outline=LILAC + (255,), width=6)
    cx, cy = tw // 2, 110
    if kind == "pack":
        d.rounded_rectangle((cx - 60, cy - 72, cx + 60, cy + 72), 18, fill=BLUSH, outline=PINK, width=6)
        d.polygon([(cx - 60, cy - 72), (cx - 20, cy - 72), (cx - 60, cy - 32)], fill=PINK)
        for i in range(5):
            x = cx - 44 + i * 22
            d.ellipse((x - 9, cy + 18, x + 9, cy + 36), fill=PINK)
        d.text((cx, cy - 18), "SCC", font=font(SERIF, 34), fill=DEEP, anchor="mm")
    elif kind == "split":
        r = 64
        d.pieslice((cx - r - 14, cy - r, cx + r - 14, cy + r), 90, 270, fill=(255, 170, 160))
        d.pieslice((cx - r + 14, cy - r, cx + r + 14, cy + r), 270, 90, fill=(255, 170, 160))
        d.text((cx + 6, cy), "½", font=font(FONT_BLACK, 70), fill=WHITE, anchor="mm")
    elif kind == "sun":
        r = 46
        for k in range(12):
            a = k * math.pi / 6
            d.line([(cx + (r + 12) * math.cos(a), cy + (r + 12) * math.sin(a)),
                    (cx + (r + 34) * math.cos(a), cy + (r + 34) * math.sin(a))], fill=(255, 170, 0), width=10)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 200, 40))
    elif kind == "drop":
        mask = Image.new("L", (tw, th), 0)
        md = ImageDraw.Draw(mask)
        r = 56
        md.ellipse((cx - r, cy - 20, cx + r, cy + 92), fill=255)
        md.polygon([(cx - r + 6, cy + 20), (cx, cy - 90), (cx + r - 6, cy + 20)], fill=255)
        top, bot = cy - 90, cy + 92
        lvl = int(bot - (bot - top) * fill_level)
        water = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        wd = ImageDraw.Draw(water)
        wd.rectangle((0, top, tw, bot), fill=(225, 240, 255, 255))
        wd.rectangle((0, lvl, tw, bot), fill=(60, 160, 240, 255))
        im.paste(water, (0, 0), mask)
        d.text((cx, cy + 40), "3L", font=font(FONT_BLACK, 40), fill=WHITE, anchor="mm")
    d.text((tw // 2, 240), l1, font=font(FONT_BLACK, 42), fill=DEEP, anchor="mm")
    d.text((tw // 2, 290), l2, font=font(FONT_BOLD, 34), fill=PINK, anchor="mm")
    return im


class IconGrid:
    def __init__(self, t0, t1, y0=1000):
        self.t0, self.t1, self.y0 = t0, t1, y0
        self.items = [("pack", "1 pack = 5 biji", "isi dalam satu pek", t0 + 0.5),
                      ("split", "Belah 2", "1/2 biji sehari", t0 + 2.3),
                      ("sun", "Selepas sarapan", "sekali sehari", t0 + 4.1),
                      ("drop", "Air 3 liter", "setiap hari", t0 + 5.9)]
        self.static = {k: icon_tile(k, a, b) for k, a, b, _ in self.items}
        self.head = text_card(["CARA MAKAN"], size=62, bg=PINK, pad=(44, 16))
        panel = Image.new("RGBA", (W, 960), (0, 0, 0, 0))
        ImageDraw.Draw(panel).rounded_rectangle((20, 0, W - 20, 960), 60, fill=LILAC + (170,))
        self.panel = panel.filter(ImageFilter.GaussianBlur(2))

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        lt = t - self.t0
        out = clamp((self.t1 - t) / 0.25)
        pp = ease_out_cubic(clamp(lt / 0.4))
        py = int(self.y0 - 60 + (H - self.y0) * (1 - pp) + 400 * (1 - out))
        paste(canvas, self.panel, 0, py)
        paste(canvas, self.head, (W - self.head.width) // 2, py - 60)
        for i, (k, a, b, ti) in enumerate(self.items):
            if t < ti:
                continue
            p = clamp((t - ti) / 0.35)
            img = self.static[k]
            if k == "drop":
                img = icon_tile(k, a, b, fill_level=ease_out_cubic(clamp((t - ti) / 1.4)))
            s = 0.3 + 0.7 * ease_out_back(p)
            if abs(s - 1) > 1e-3:
                img = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
            col, row = i % 2, i // 2
            cx = 60 + col * 500 + 215
            cy = py + 120 + row * 380 + 165
            paste(canvas, img, cx - img.width // 2, cy - img.height // 2)


# ---------------- CTA bag ----------------
def bag_img(size=230):
    im = Image.new("RGBA", (size, int(size * 1.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top = int(size * 0.32)
    d.arc((size * 0.28, size * 0.05, size * 0.72, size * 0.55), 180, 360, fill=(150, 100, 0), width=14)
    d.rounded_rectangle((size * 0.08, top, size * 0.92, size * 1.1), 30, fill=YELLOW, outline=(150, 100, 0), width=8)
    d.text((size / 2, top + (size * 1.1 - top) / 2), "BELI", font=font(FONT_BLACK, int(size * 0.2)),
           fill=(60, 40, 0), anchor="mm")
    return im


class Bag:
    def __init__(self, t0, t1, x, y):
        self.img, self.t0, self.t1, self.x, self.y = bag_img(), t0, t1, x, y

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        lt = t - self.t0
        p = clamp(lt / 0.4)
        s = (0.2 + 0.8 * ease_out_back(p)) * (1 + 0.06 * math.sin(lt * 2 * math.pi * 1.8))
        ang = 8 * math.sin(lt * 2 * math.pi * 0.9)
        im = self.img.resize((int(self.img.width * s), int(self.img.height * s)), Image.BILINEAR)
        im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
        out = clamp((self.t1 - t) / 0.2)
        if out < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * out)))
        bounce = int(-30 * abs(math.sin(lt * math.pi * 1.8)))
        paste(canvas, im, self.x - im.width // 2, self.y - im.height // 2 + bounce)


def grab(src, t):
    p = os.path.join(tempfile.mkdtemp(), "g.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", p], check=True)
    im = Image.open(p).convert("RGB")
    # crop the pack area (centre-upper) for the polaroid photo
    return im.crop((60, 380, 1020, 1520))


def build(total, src):
    T = total
    close_t = T - 1.6
    els = [Leaks(), Sparkles([(1.3, 3.2), (T - 6.5, T - 1.6)], per_sec=9)]
    els.append(Words(["Dah tiba masa dia", "'keluar'", "dari almari..."], 2.2, 5.2, 250,
                     hl=("'keluar'",), size=94))
    els.append(Polaroid(grab(src, 31.2), 5.2, 7.8, ["SCC White Kidney Bean", "+ L-Carnitine Candy"]))
    els.append(IconGrid(7.8, 15.6))
    els.append(Words(["Rutin kecil,", "langkah besar"], 15.6, 18.0, 260, hl=("besar",), size=100))
    els.append(Words(["Simple, comel,", "muat dalam", "beg tangan"], 18.0, 20.4, 260,
                     hl=("muat",), hl_color=(150, 90, 200), size=92))
    els.append(Words(["Baju lama pun", "mula 'senyum'", "balik..."], 20.4, 22.9, 260,
                     hl=("'senyum'",), size=92))
    els.append(Words(["Tak perlu tunggu", "tahun depan,", "biar baju impian", "yang tunggu awak"],
                     22.9, 25.4, 220, hl=("impian",), hl_color=(150, 90, 200), size=78, step=0.12))
    C = lambda *a, **k: els.append(Card(*a, **k))
    C(text_card(["KLIK BEG KUNING", "SEKARANG"], size=86, fg=(30, 30, 30), bg=YELLOW),
      25.4, close_t, 190, pulse=True, shine=True)
    C(text_card(["Kenapa sekarang?", "Mula hari ini, esok selangkah lebih dekat"], size=42,
                bg=(22, 163, 74), highlight="Kenapa sekarang?"), 25.9, close_t, 1040, anim="up")
    C(text_card(["Tangguh lagi?", "Baju impian terus berhabuk dalam almari"], size=40,
                bg=(20, 20, 20), highlight="Tangguh lagi?"), 26.6, close_t, 1225, anim="up")
    els.append(Bag(25.6, close_t, 190, 1590))
    els.append(Doors(1.2, close_t, T,
                     door_text(["Baju impian", "masih tergantung", "dalam almari?"], emo="👗"),
                     door_text(["Jom buka", "almari baru"], sub="KLIK BEG KUNING SEKARANG", emo="🛍️")))
    C(text_card(["Hasil berbeza mengikut individu.",
                 "Amalkan pemakanan seimbang & minum air secukupnya."],
                size=28, bg=(0, 0, 0), fpath=FONT_BOLD, pad=(22, 10), radius=16),
      20.4, 99, 1760, anim="none")
    return els


def main(src, out):
    tmp = tempfile.mkdtemp()
    durs = [(b - a) / SPEED for a, b in SEGMENTS]
    total = sum(durs) - XF * (len(durs) - 1)
    nframes = int(total * FPS)
    fc, offs, acc = [], [], 0.0
    for i, ((a, b), z) in enumerate(zip(SEGMENTS, ZOOM0)):
        d = b - a
        zx = f"({z}+0.06*t/{d:.3f})"
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,"
                  f"scale=w='trunc({W}*{zx}/2)*2':h='trunc({H}*{zx}/2)*2':eval=frame,"
                  f"crop={W}:{H},setsar=1,setpts=PTS/{SPEED},fps={FPS},format=yuv420p[s{i}]")
    last = "s0"
    acc = durs[0]
    for i in range(1, len(SEGMENTS)):
        off = acc - XF
        offs.append(off)
        fc.append(f"[{last}][s{i}]xfade=transition={TRANS[i - 1]}:duration={XF}:offset={off:.3f}[x{i}]")
        last = f"x{i}"
        acc = off + durs[i]
    fc.append(f"[{last}]eq=contrast=1.04:saturation=1.12:brightness=0.03,"
              f"colorbalance=rs=0.03:bs=0.06:rm=0.02:bm=0.04,split[g1][g2]")
    fc.append("[g2]gblur=sigma=28[gb]")
    fc.append("[g1][gb]blend=all_mode=screen:all_opacity=0.22,vignette=PI/6,format=yuv420p[base]")
    fc.append("[1:v]format=rgba[ov]")
    fc.append("[base][ov]overlay=0:0:format=auto,format=yuv420p[vout]")
    silent = out + "-nosound.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src,
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-filter_complex", ";".join(fc), "-map", "[vout]", "-an", "-frames:v", str(nframes),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
           "-movflags", "+faststart", silent]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    els = build(total, src)
    blank = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for f in range(nframes):
        t = f / FPS
        canvas = blank.copy()
        for e in els:
            e.draw(canvas, t)
        proc.stdin.write(canvas.tobytes())
        if f % 150 == 0:
            print(f"frame {f}/{nframes}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")

    mus, fx = os.path.join(tmp, "m.wav"), os.path.join(tmp, "fx.wav")
    music(mus, total)
    sfx(fx, total + 0.5, [1.5] + [o + XF / 2 for o in offs] + [total - 1.3], 25.4)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", mus, "-i", fx,
                    "-filter_complex", "[1:a][2:a]amix=inputs=2:normalize=0,alimiter=limit=0.9[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out + ".mp4"], check=True)
    print(f"done: {out}.mp4 + {silent} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
