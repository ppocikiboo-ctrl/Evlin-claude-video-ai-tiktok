#!/usr/bin/env python3
"""Version 3: v2 script (no voice, layered wording) with full motion graphics.

Base video (ffmpeg): slow push-in per shot, camera shake + RGB glitch + flash on
each cut, warm pink grade.  Motion layer (Pillow, rendered per frame and piped
to ffmpeg): light leaks, sparkles, bounce-in text, checklist with animated
ticks, pulsing CTA button with shine sweep and bouncing arrow, gradient
progress bar.  Audio: generated beat + whooshes on cuts + ding on CTA.

Usage: python3 edit_v3.py <input.mp4> <out-without-.mp4>
Writes <out>.mp4 (with music) and <out>-nosound.mp4.
"""
import math
import os
import random
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

from edit import (DEEP, FONT_BLACK, FONT_BOLD, FPS, H, PINK, W, WHITE, YELLOW,
                  font, text_card)
from edit_v2 import music

SPEED = 1.10
SEGMENTS = [(0.43, 7.00), (7.00, 14.40), (14.40, 17.10), (17.10, 20.30),
            (20.30, 23.20), (23.20, 29.60), (29.60, 33.60), (33.60, 35.55)]
ZOOM0 = [1.00, 1.06, 1.00, 1.08, 1.02, 1.06, 1.00, 1.04]
GREEN = (22, 163, 74)
DARK = (20, 20, 20)
random.seed(7)


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


# ---------- assets ----------
def soft_blob(size, color):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse((size * 0.2, size * 0.2, size * 0.8, size * 0.8), fill=color + (90,))
    return img.filter(ImageFilter.GaussianBlur(size // 8))


def sparkle_img(r, color=(255, 255, 255)):
    s = r * 2 + 8
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2
    pts = []
    for k in range(8):
        a = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.22
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=color + (255,))
    glow = img.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(glow, img)


def check_row(num, text, done, active, size=50):
    f = font(FONT_BLACK, size)
    tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f)
    r, pad = int(size * 0.75), 22
    cw, ch = int(tw + r * 2 + pad * 3), int(size * 1.6)
    img = Image.new("RGBA", (cw + 28, ch + 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if active:
        d.rounded_rectangle((4, 4, cw + 24, ch + 24), ch // 2 + 8, fill=YELLOW + (255,))
    d.rounded_rectangle((14, 14, cw + 14, ch + 14), ch // 2, fill=WHITE + (245,))
    cx, cy = 14 + pad + r, 14 + ch // 2
    if done:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)
        d.line([(cx - r * 0.45, cy + 2), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.38)],
               fill=WHITE, width=max(6, size // 7), joint="curve")
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PINK)
        d.text((cx, cy), str(num), font=font(FONT_BLACK, int(size * 0.85)), fill=WHITE, anchor="mm")
    d.text((cx + r + pad, cy), text, font=f, fill=DEEP, anchor="lm")
    return img


def arrow_img(size=120):
    img = Image.new("RGBA", (size, int(size * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    poly = [(s * .35, 0), (s * .65, 0), (s * .65, s * .7), (s * .95, s * .7), (s * .5, s * 1.25),
            (s * .05, s * .7), (s * .35, s * .7)]
    d.polygon(poly, fill=YELLOW + (255,), outline=(30, 30, 30), width=6)
    return img


def paste(canvas, img, x, y):
    """alpha_composite that tolerates negative / overflowing positions."""
    x, y = int(x), int(y)
    l, t = max(0, -x), max(0, -y)
    r, b = min(img.width, W - x), min(img.height, H - y)
    if r > l and b > t:
        canvas.alpha_composite(img.crop((l, t, r, b)), (x + l, y + t))


# ---------- elements ----------
class Card:
    """Pre-rendered image with an entrance animation and fade-out."""

    def __init__(self, img, t0, t1, y, x=None, anim="pop", pulse=False, shine=False):
        self.img, self.t0, self.t1, self.y, self.anim = img, t0, t1, y, anim
        self.x = (W - img.width) // 2 if x is None else x
        self.pulse, self.shine = pulse, shine
        self.cache = {}

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        lt = t - self.t0
        p = clamp(lt / 0.35)
        out = clamp((self.t1 - t) / 0.18)
        img, x, y = self.img, self.x, self.y
        scale = 1.0
        if self.anim == "pop":
            scale = 0.3 + 0.7 * ease_out_back(p)
        elif self.anim == "left":
            x = int(self.x - (W * 0.8) * (1 - ease_out_back(p)))
        elif self.anim == "up":
            y = int(self.y + 160 * (1 - ease_out_cubic(p)))
        if self.pulse and p >= 1:
            scale = 1 + 0.045 * math.sin(2 * math.pi * 1.6 * lt)
        if self.shine and p >= 1:
            img = self._shine(img, (lt * 0.7) % 1.0)
        if abs(scale - 1) > 1e-3:
            key = round(scale, 3)
            if key not in self.cache or self.shine:
                nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
                self.cache[key] = img.resize((nw, nh), Image.BILINEAR)
            sc = self.cache[key]
            x += (img.width - sc.width) // 2
            y += (img.height - sc.height) // 2
            img = sc
        alpha = min(clamp(lt / 0.12), out)
        if alpha < 1:
            img = img.copy()
            img.putalpha(img.getchannel("A").point(lambda a: int(a * alpha)))
        paste(canvas, img, x, y)

    @staticmethod
    def _shine(img, ph):
        band = Image.new("L", img.size, 0)
        d = ImageDraw.Draw(band)
        cx = -200 + ph * (img.width + 600)
        d.polygon([(cx, 0), (cx + 70, 0), (cx - 60, img.height), (cx - 130, img.height)], fill=150)
        band = band.filter(ImageFilter.GaussianBlur(12))
        mask = Image.composite(band, Image.new("L", img.size, 0), img.getchannel("A"))
        white = Image.new("RGBA", img.size, (255, 255, 255, 0))
        white.putalpha(mask)
        return Image.alpha_composite(img, white)


class Checklist:
    def __init__(self, items, t_end, x=60, y0=300, gap=122):
        self.items, self.t_end, self.x, self.y0, self.gap = items, t_end, x, y0, gap
        n = len(items)
        self.imgs = {}
        for i, (txt, _) in enumerate(items):
            for done in (False, True):
                for active in (False, True):
                    self.imgs[(i, done, active)] = check_row(i + 1, txt, done, active)

    def draw(self, canvas, t):
        if t >= self.t_end:
            return
        for i, (txt, t0) in enumerate(self.items):
            if t < t0:
                continue
            nxt = self.items[i + 1][1] if i + 1 < len(self.items) else self.t_end - 1.2
            done = t >= t0 + 0.9
            active = t0 <= t < nxt
            img = self.imgs[(i, done, active)]
            p = clamp((t - t0) / 0.4)
            x = int(self.x - W * (1 - ease_out_back(p)))
            # tick "pop" when it turns done
            tp = (t - t0 - 0.9) / 0.25
            if 0 <= tp < 1:
                s = 1 + 0.08 * math.sin(math.pi * tp)
                img = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
            out = clamp((self.t_end - t) / 0.2)
            if out < 1:
                img = img.copy()
                img.putalpha(img.getchannel("A").point(lambda a: int(a * out)))
            y = self.y0 + i * self.gap
            paste(canvas, img, x, y)


class Sparkles:
    def __init__(self, windows, per_sec=9):
        self.parts = []
        self.imgs = [sparkle_img(r, c) for r in (10, 16, 24)
                     for c in ((255, 255, 255), (255, 230, 120), (255, 180, 210))]
        for a, b in windows:
            n = int((b - a) * per_sec)
            for _ in range(n):
                self.parts.append((random.uniform(a, b), random.uniform(0.5, 1.0),
                                   random.randint(40, W - 80), random.randint(500, 1500),
                                   random.randrange(len(self.imgs))))

    def draw(self, canvas, t):
        for t0, life, x, y, k in self.parts:
            lt = t - t0
            if 0 <= lt < life:
                a = math.sin(math.pi * lt / life)
                img = self.imgs[k]
                s = 0.4 + 0.8 * a
                im = img.resize((max(1, int(img.width * s)),) * 2, Image.BILINEAR)
                im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
                paste(canvas, im, x, y - 40 * lt)


class Leaks:
    def __init__(self):
        self.b1 = soft_blob(1100, (255, 120, 170))
        self.b2 = soft_blob(900, (255, 200, 120))

    def draw(self, canvas, t):
        x1 = int(-500 + 380 * math.sin(t * 0.45))
        y1 = int(-350 + 260 * math.cos(t * 0.33))
        x2 = int(W - 450 + 300 * math.cos(t * 0.38))
        y2 = int(H - 650 + 240 * math.sin(t * 0.52))
        paste(canvas, self.b1, x1, y1)
        paste(canvas, self.b2, x2, y2)


class Arrow:
    def __init__(self, t0, x, y):
        self.img, self.t0, self.x, self.y = arrow_img(), t0, x, y

    def draw(self, canvas, t):
        if t < self.t0:
            return
        lt = t - self.t0
        a = clamp(lt / 0.2)
        dy = int(28 * abs(math.sin(math.pi * 2.0 * lt)))
        im = self.img
        if a < 1:
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        paste(canvas, im, self.x, self.y + dy)


class Progress:
    def __init__(self, total):
        self.total = total
        g = Image.new("RGBA", (W, 16))
        d = ImageDraw.Draw(g)
        for x in range(W):
            k = x / W
            c = tuple(int(PINK[i] * (1 - k) + YELLOW[i] * k) for i in range(3))
            d.line([(x, 0), (x, 16)], fill=c + (255,))
        self.bar = g

    def draw(self, canvas, t):
        w = int(W * clamp(t / self.total))
        if w > 0:
            canvas.alpha_composite(self.bar.crop((0, 0, w, 16)), (0, H - 16))


def build(total):
    els = [Leaks(), Sparkles([(0.0, 1.6), (22.8, total)], per_sec=10)]
    C = lambda *a, **k: els.append(Card(*a, **k))
    # HOOK — two lines bounce in one after the other
    C(text_card(["Baju impian masih"], size=86, highlight="Baju impian"), 0.05, 3.3, 230)
    C(text_card(["tergantung dalam almari?"], size=72, bg=DEEP), 0.45, 3.3, 400)
    C(text_card(["Dah tiba masa dia"], size=86), 3.3, 6.4, 230)
    C(text_card(["'keluar' dari almari..."], size=80, bg=DEEP, highlight="'keluar'"), 3.65, 6.4, 400)
    C(text_card(["Ini rahsia saya..."], size=52, bg=None), 0.9, 6.4, 1560, anim="up")
    # PRODUCT
    C(text_card(["SCC White Kidney Bean", "+ L-Carnitine Candy"], size=60, fg=DEEP, bg=WHITE),
      6.4, 8.8, 230, shine=True)
    C(text_card(["NEW ROUTINE"], size=40, bg=PINK, pad=(30, 12)), 6.6, 8.8, 150, anim="pop")
    # CHECKLIST
    C(text_card(["CARA MAKAN"], size=62, bg=PINK, pad=(40, 16)), 8.8, 17.8, 150)
    els.append(Checklist([("1 pack = 5 biji", 9.1), ("Belah 2 - 1/2 biji sehari", 11.0),
                          ("Makan selepas sarapan", 12.9), ("Minum air 3 liter sehari", 14.8)],
                         17.8))
    # ROUTINE
    C(text_card(["Rutin kecil,"], size=90), 17.8, 20.4, 230)
    C(text_card(["langkah besar"], size=90, bg=DEEP, fg=YELLOW), 18.15, 20.4, 410)
    C(text_card(["Simple, comel,"], size=80), 20.4, 22.8, 230)
    C(text_card(["muat dalam beg tangan"], size=70, bg=DEEP, highlight="muat"), 20.75, 22.8, 400)
    # BENEFIT
    C(text_card(["Baju lama pun mula"], size=78), 22.8, 25.4, 230)
    C(text_card(["'senyum' balik..."], size=86, bg=DEEP, highlight="'senyum'"), 23.15, 25.4, 405)
    C(text_card(["Tak perlu tunggu tahun depan,"], size=60), 25.4, 27.6, 230)
    C(text_card(["biar baju impian", "yang tunggu awak"], size=72, bg=DEEP, highlight="baju impian"),
      25.75, 27.6, 380)
    # CTA
    C(text_card(["KLIK BEG KUNING", "SEKARANG"], size=92, fg=(30, 30, 30), bg=YELLOW),
      27.6, 99, 200, pulse=True, shine=True)
    C(text_card(["Kenapa sekarang?", "Mula hari ini, esok selangkah", "lebih dekat"], size=46,
                bg=GREEN, highlight="Kenapa sekarang?"), 28.3, 99, 1060, anim="up")
    C(text_card(["Tangguh lagi?", "Baju impian terus berhabuk dalam almari"], size=40, bg=DARK,
                highlight="Tangguh lagi?"), 29.4, 99, 1310, anim="up")
    els.append(Arrow(28.0, 70, 1520))
    C(text_card(["Hasil berbeza mengikut individu.",
                 "Amalkan pemakanan seimbang & minum air secukupnya."],
                size=28, bg=(0, 0, 0), fpath=FONT_BOLD, pad=(22, 10), radius=16),
      22.8, 99, 1730, anim="none")
    els.append(Progress(total))
    return els


def sfx(path, dur, cuts, ding_t):
    w = "+".join(f"exp(-pow((t-{c:.3f})/0.09,2))" for c in cuts)
    expr = (f"0.35*(random(0)*2-1)*({w})"
            f"+0.25*sin(2*PI*1318*t)*exp(-5*(t-{ding_t}))*gte(t,{ding_t})"
            f"+0.18*sin(2*PI*1975*t)*exp(-6*(t-{ding_t}-0.12))*gte(t,{ding_t}+0.12)")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    f"aevalsrc='{expr}':s=44100:d={dur}", "-af", "bandpass=f=2500:width_type=o:w=3,"
                    "volume=2.0", "-ac", "2", path], check=True)


def main(src, out):
    tmp = tempfile.mkdtemp()
    total = sum(b - a for a, b in SEGMENTS) / SPEED
    nframes = int(round(total * FPS))
    cuts, acc = [], 0.0
    fc = []
    for i, ((a, b), z) in enumerate(zip(SEGMENTS, ZOOM0)):
        d = b - a
        zx = f"({z}+0.07*t/{d:.3f})"
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,"
                  f"scale=w='trunc({W}*{zx}/2)*2':h='trunc({H}*{zx}/2)*2':eval=frame,"
                  f"crop={W}:{H}:x='(iw-{W})/2+16*sin(90*t)*exp(-14*t)':"
                  f"y='(ih-{H})/2+16*cos(70*t)*exp(-14*t)',setsar=1[v{i}]")
        cuts.append(acc / SPEED)
        acc += d
    n = len(SEGMENTS)
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vc]")
    flash = "+".join(f"between(t,{t:.3f},{t + 0.07:.3f})" for t in cuts[1:])
    glitch = "+".join(f"between(t,{t:.3f},{t + 0.12:.3f})" for t in cuts)
    fc.append(f"[vc]setpts=PTS/{SPEED},fps={FPS},"
              f"eq=contrast=1.08:saturation=1.22:brightness=0.02:gamma=0.97,"
              f"colorbalance=rs=0.04:gs=-0.01:bs=0.03:rh=0.03,unsharp=5:5:0.7,vignette=PI/5,"
              f"rgbashift=rh=-14:bh=14:enable='{glitch}',"
              f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.6:t=fill:enable='{flash}',format=yuv420p[base]")
    fc.append("[1:v]format=rgba[ov]")
    fc.append("[base][ov]overlay=0:0:format=auto,format=yuv420p[vout]")
    silent = out + "-nosound.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src,
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-filter_complex", ";".join(fc), "-map", "[vout]", "-an", "-frames:v", str(nframes),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
           "-movflags", "+faststart", silent]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    els = build(total)
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
    sfx(fx, total + 0.5, cuts[1:], 27.6)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", mus, "-i", fx,
                    "-filter_complex", "[1:a][2:a]amix=inputs=2:normalize=0,alimiter=limit=0.9[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out + ".mp4"], check=True)
    print(f"done: {out}.mp4 + {silent} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
