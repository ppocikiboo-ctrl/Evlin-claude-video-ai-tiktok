"""Step 3: motion graphics, sound design and final encode.

Reads build/base.mp4 + build/track.json, draws every overlay frame by frame
(kinetic type, glass info cards tracked to the bottle cap, particles, CTA),
synthesises the music bed + SFX, and writes output/ocheal_micellar_tiktok.mp4.

    python3 render.py            # full render
    python3 render.py --stills   # only write preview stills to build/stills/
"""
import argparse
import json
import math
import random
import re
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from edl import FPS, H, TOTAL, W, seg_end, seg_start, timeline

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "assets" / "fonts"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
OUT = ROOT / "output" / "ocheal_micellar_tiktok.mp4"

# Palette: baby pink, rose, pearl, champagne.
ROSE = (214, 58, 110)
DEEP_ROSE = (170, 34, 88)
BABY_PINK = (255, 200, 218)
PEARL = (255, 250, 248)
CHAMPAGNE = (247, 222, 190)
MAUVE = (110, 58, 80)

# TikTok safe area: keep text inside x 60..880 (right rail has the buttons)
# and y 220..1450 (top tabs, bottom caption + product link).
SAFE_L, SAFE_R = 60, 880
SAFE_W = SAFE_R - SAFE_L
# The top info zone (y < 900) is clear of the right-rail buttons, so it may
# use almost the full width.
TOP_L, TOP_R = 50, 1030
TOP_W = TOP_R - TOP_L
TOP_Y = 250


def wrap2(text, fits):
    """Return [text] if it fits, else the most balanced two-line split."""
    if fits(text):
        return [text]
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = abs(len(a) - len(b))
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1]


def font(name, size):
    return _font(name, int(size))


@lru_cache(maxsize=None)
def _font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


# ---------------------------------------------------------------- easing

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in_out(u):
    u = clamp(u)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def ease_out_back(u, s=1.9):
    u = clamp(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def env(t, t0, t1, fade_in=0.28, fade_out=0.22):
    """0..1 visibility of an element living in [t0, t1]."""
    if t < t0 or t > t1:
        return 0.0
    return clamp((t - t0) / fade_in) * clamp((t1 - t) / fade_out)


# ---------------------------------------------------------------- text

EMOJI_RE = re.compile("([\U0001F000-\U0001FFFF☀-➿][️]?)")


@lru_cache(maxsize=None)
def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    s = size / im.height
    return im.resize((max(1, round(im.width * s)), size), Image.LANCZOS)


@lru_cache(maxsize=None)
def text_img(text, fname, size, fill, stroke=0, stroke_fill=(255, 255, 255), tracking=0,
             shadow=0.0, glow=None):
    """Render a single line (text + colour emoji) to a tight RGBA sprite."""
    f = font(fname, size)
    asc, desc = f.getmetrics()
    pad = stroke + 30
    parts = [p for p in EMOJI_RE.split(text) if p]
    # Measure.
    widths = []
    for p in parts:
        if EMOJI_RE.fullmatch(p):
            widths.append(emoji_img(p, int(size * 1.0)).width + int(size * 0.12))
        elif tracking:
            widths.append(sum(f.getlength(c) + tracking for c in p))
        else:
            widths.append(f.getlength(p))
    w = int(sum(widths)) + 2 * pad
    h = asc + desc + 2 * pad
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    x = pad
    for p, pw in zip(parts, widths):
        if EMOJI_RE.fullmatch(p):
            e = emoji_img(p, int(size * 1.0))
            im.alpha_composite(e, (int(x + size * 0.06), pad + int(asc * 0.55 - e.height / 2) + int(size * 0.12)))
        elif tracking:
            cx = x
            for c in p:
                d.text((cx, pad), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
                cx += f.getlength(c) + tracking
        else:
            d.text((x, pad), p, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += pw
    base = im
    if shadow or glow:
        a = im.getchannel("A")
        out = Image.new("RGBA", im.size)
        if glow:
            g = Image.new("RGBA", im.size, glow + (0,))
            g.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, int(v * 1.6))))
            out.alpha_composite(g)
        if shadow:
            s = Image.new("RGBA", im.size, (120, 20, 60, 0))
            s.putalpha(a.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * shadow)))
            out.alpha_composite(s, (0, 6))
        out.alpha_composite(base)
        base = out
    return base.crop(base.getbbox())


def paste(canvas, sprite, x, y, alpha=1.0, scale=1.0, anchor="mm", rot=0.0):
    """Composite sprite onto canvas with alpha/scale/rotation around anchor."""
    if alpha <= 0.003 or sprite is None:
        return
    if scale != 1.0:
        sw, sh = max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))
        sprite = sprite.resize((sw, sh), Image.BICUBIC)
    if rot:
        sprite = sprite.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = sprite.getchannel("A").point(lambda v: int(v * alpha))
        sprite = sprite.copy()
        sprite.putalpha(a)
    ax = {"l": 0, "m": 0.5, "r": 1}[anchor[0]]
    ay = {"t": 0, "m": 0.5, "b": 1}[anchor[1]]
    px, py = int(x - sprite.width * ax), int(y - sprite.height * ay)
    # Clip to canvas.
    l, t = max(0, px), max(0, py)
    r, b = min(canvas.width, px + sprite.width), min(canvas.height, py + sprite.height)
    if r <= l or b <= t:
        return
    canvas.alpha_composite(sprite.crop((l - px, t - py, r - px, b - py)), (l, t))


# ---------------------------------------------------------------- sprites

def _aa(im):
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


@lru_cache(maxsize=None)
def sparkle_sprite(size, color=(255, 255, 255)):
    s = size * 2
    im = Image.new("RGBA", (s * 2, s * 2))
    d = ImageDraw.Draw(im)
    c = s
    pts = []
    for i in range(8):
        r = s * (0.95 if i % 2 == 0 else 0.16)
        a = math.pi / 4 * i - math.pi / 2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    glow = Image.new("RGBA", im.size)
    ImageDraw.Draw(glow).ellipse((c - s * 0.5, c - s * 0.5, c + s * 0.5, c + s * 0.5), fill=BABY_PINK + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(s * 0.25))
    im.alpha_composite(glow)
    d.polygon(pts, fill=color + (255,))
    return _aa(im)


@lru_cache(maxsize=None)
def droplet_sprite(size):
    s = size * 2
    im = Image.new("RGBA", (s, int(s * 1.4)))
    d = ImageDraw.Draw(im)
    r = s * 0.42
    cx, cy = s / 2, im.height - r - 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 235, 242, 150), outline=(255, 255, 255, 230), width=max(2, s // 18))
    d.polygon([(cx, 2), (cx - r * 0.86, cy - r * 0.45), (cx + r * 0.86, cy - r * 0.45)], fill=(255, 235, 242, 150))
    d.line([(cx, 2), (cx - r * 0.9, cy - r * 0.42)], fill=(255, 255, 255, 230), width=max(2, s // 18))
    d.line([(cx, 2), (cx + r * 0.9, cy - r * 0.42)], fill=(255, 255, 255, 230), width=max(2, s // 18))
    d.ellipse((cx - r * 0.5, cy - r * 0.35, cx - r * 0.12, cy + r * 0.1), fill=(255, 255, 255, 235))
    return _aa(im)


@lru_cache(maxsize=None)
def bubble_sprite(size):
    s = size * 2
    im = Image.new("RGBA", (s, s))
    d = ImageDraw.Draw(im)
    d.ellipse((2, 2, s - 3, s - 3), fill=(255, 220, 232, 45), outline=(255, 255, 255, 210), width=max(2, s // 20))
    d.arc((s * 0.18, s * 0.18, s * 0.82, s * 0.82), 200, 260, fill=(255, 255, 255, 240), width=max(2, s // 12))
    return _aa(im)


@lru_cache(maxsize=None)
def petal_sprite(size, shade=0):
    s = size * 2
    im = Image.new("RGBA", (s, int(s * 1.25)))
    d = ImageDraw.Draw(im)
    cols = [(255, 182, 203), (250, 160, 188), (255, 205, 220)]
    c = cols[shade % 3]
    d.ellipse((0, 0, s, im.height), fill=c + (235,))
    d.pieslice((s * 0.3, -s * 0.25, s * 0.7, s * 0.18), 0, 180, fill=(0, 0, 0, 0))
    hl = Image.new("RGBA", im.size)
    ImageDraw.Draw(hl).ellipse((s * 0.2, s * 0.25, s * 0.55, im.height * 0.8), fill=(255, 255, 255, 90))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(s * 0.08)))
    # keep the notch transparent
    a = im.getchannel("A")
    ImageDraw.Draw(a).pieslice((s * 0.3, -s * 0.25, s * 0.7, s * 0.18), 0, 180, fill=0)
    im.putalpha(a)
    return _aa(im)


@lru_cache(maxsize=None)
def heart_sprite(size):
    s = size * 2
    im = Image.new("RGBA", (s, s))
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((s / 2 + x * s / 36, s / 2 - y * s / 36))
    ImageDraw.Draw(im).polygon(pts, fill=(255, 112, 160, 240))
    hl = Image.new("RGBA", im.size)
    ImageDraw.Draw(hl).ellipse((s * 0.22, s * 0.2, s * 0.42, s * 0.38), fill=(255, 255, 255, 170))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(2)))
    return _aa(im)


@lru_cache(maxsize=None)
def dust_sprite(size, color):
    s = size * 2
    im = Image.new("RGBA", (s * 2, s * 2))
    ImageDraw.Draw(im).ellipse((s * 0.5, s * 0.5, s * 1.5, s * 1.5), fill=color + (220,))
    return _aa(im.filter(ImageFilter.GaussianBlur(s * 0.18)))


@lru_cache(maxsize=None)
def cotton_pad_sprite(size, wet=0.0):
    """Premium cotton pad: soft white disc, quilted dots, optional pink wet zone."""
    s = size * 2
    im = Image.new("RGBA", (s + 40, s + 40))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).ellipse((24, 30, s + 24, s + 30), fill=(150, 60, 90, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.ellipse((20, 20, s + 20, s + 20), fill=(255, 255, 255, 255), outline=(240, 220, 228, 255), width=4)
    if wet > 0:
        wz = Image.new("RGBA", im.size)
        r = s * 0.36 * wet
        c = 20 + s / 2
        ImageDraw.Draw(wz).ellipse((c - r, c - r, c + r, c + r), fill=(255, 190, 210, 170))
        im.alpha_composite(wz.filter(ImageFilter.GaussianBlur(8)))
    step = s / 7
    for i in range(1, 7):
        for j in range(1, 7):
            x, y = 20 + i * step, 20 + j * step
            if (x - 20 - s / 2) ** 2 + (y - 20 - s / 2) ** 2 < (s * 0.42) ** 2:
                d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(236, 214, 222, 255))
    return _aa(im)


@lru_cache(maxsize=None)
def rose_sprite(size):
    im = Image.open(ROOT / "assets" / "graphics" / "rose.png").convert("RGBA")
    s = size / im.width
    return im.resize((size, int(im.height * s)), Image.LANCZOS)


@lru_cache(maxsize=None)
def badge_sprite(kind, size=92):
    """Round rose-gradient badge with a white glyph."""
    s = size * 2
    im = Image.new("RGBA", (s, s))
    grad = Image.linear_gradient("L").resize((s, s)).rotate(45)
    a = Image.new("L", (s, s))
    ImageDraw.Draw(a).ellipse((4, 4, s - 4, s - 4), fill=255)
    top = Image.new("RGBA", (s, s), (255, 120, 165, 255))
    bot = Image.new("RGBA", (s, s), DEEP_ROSE + (255,))
    disc = Image.composite(bot, top, grad)
    disc.putalpha(a)
    im.alpha_composite(disc)
    d = ImageDraw.Draw(im)
    ImageDraw.Draw(im).ellipse((10, 10, s - 10, s - 10), outline=(255, 255, 255, 140), width=4)
    c = s / 2
    if kind == "sparkle":
        g = sparkle_sprite(int(s * 0.32))
        im.alpha_composite(g, (int(c - g.width / 2), int(c - g.height / 2)))
    elif kind == "bubbles":
        for (x, y, r) in [(0.42, 0.56, 0.2), (0.64, 0.38, 0.13), (0.66, 0.66, 0.09)]:
            d.ellipse((s * (x - r), s * (y - r), s * (x + r), s * (y + r)), outline="white", width=7)
    elif kind == "drop":
        g = droplet_sprite(int(s * 0.26)).copy()
        im.alpha_composite(g, (int(c - g.width / 2), int(c - g.height / 2)))
    elif kind == "wave":
        for k, yy in enumerate((0.42, 0.56, 0.70)):
            pts = [(s * (0.24 + 0.52 * i / 30), s * yy + math.sin(i / 30 * 2 * math.pi) * s * 0.045) for i in range(31)]
            d.line(pts, fill="white", width=8, joint="curve")
    elif kind == "heart":
        g = heart_sprite(int(s * 0.25))
        wh = Image.new("RGBA", g.size, (255, 255, 255, 255))
        wh.putalpha(g.getchannel("A"))
        im.alpha_composite(wh, (int(c - g.width / 2), int(c - g.height / 2 + 4)))
    return _aa(im)


def rounded_mask(w, h, r):
    m = Image.new("L", (w * 2, h * 2))
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def glass_panel(frame, box, radius=38, tint=(255, 244, 248), opacity=0.62, border=True):
    """Frosted-glass panel sampled from the current video frame."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    region = frame.crop((x0, y0, x1, y1)).convert("RGB")
    small = region.resize((max(1, w // 6), max(1, h // 6)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    blur = small.resize((w, h), Image.BILINEAR)
    panel = Image.blend(blur, Image.new("RGB", (w, h), tint), opacity).convert("RGBA")
    # soft top sheen
    sheen = Image.linear_gradient("L").rotate(180).resize((w, h)).point(lambda v: int(v * 0.35))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    white.putalpha(sheen)
    panel.alpha_composite(white)
    mask = rounded_mask(w, h, radius)
    panel.putalpha(mask)
    out = Image.new("RGBA", (w + 60, h + 70))
    sh = Image.new("RGBA", out.size)
    ImageDraw.Draw(sh).rounded_rectangle((30, 42, w + 30, h + 42), radius, fill=(150, 40, 85, 70))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(panel, (30, 30))
    if border:
        ImageDraw.Draw(out).rounded_rectangle((30, 30, w + 29, h + 29), radius, outline=(255, 255, 255, 200), width=3)
    return out, 30


# ---------------------------------------------------------------- tracking

TRACK = {}


def load_track():
    p = ROOT / "build" / "track.json"
    if p.exists():
        TRACK.update({int(k): v for k, v in json.loads(p.read_text()).items()})


def cap_at(fi):
    return TRACK.get(fi)


# ---------------------------------------------------------------- camera

SEG_BY_NAME = {n: (s, e, seg) for n, s, e, seg in timeline()}


def camera(fi):
    """Zoom + centre for frame fi (Ken Burns per segment + punch at cuts)."""
    t = fi / FPS
    for n, s, e, seg in timeline():
        if s <= t < e or n == "hero":
            if s <= t < e:
                break
    z0, z1 = seg[4]
    u = (t - s) / (e - s)
    z = z0 + (z1 - z0) * (ease_out_cubic(u * 2.2) if n == "hook" else ease_in_out(u))
    # punch-in transition: first frames of every cut settle from +5 %
    z *= 1 + 0.05 * (1 - ease_out_cubic((t - s) / 0.22))
    cx, cy = W / 2, H * 0.47
    tr = cap_at(fi)
    if tr and tr[2] > 0.5:
        cx = cx * 0.7 + tr[0] * 0.3
        cy = cy * 0.75 + tr[1] * 0.25
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(cx, hw, W - hw)
    cy = clamp(cy, hh, H - hh)
    return z, cx, cy, n, s, e


def apply_camera(img, z, cx, cy):
    hw, hh = W / (2 * z), H / (2 * z)
    return img.resize((W, H), Image.BICUBIC, box=(cx - hw, cy - hh, cx + hw, cy + hh))


def to_screen(pt, z, cx, cy):
    return ((pt[0] - cx) * z + W / 2, (pt[1] - cy) * z + H / 2)


def bloom(img, strength=0.11):
    a = np.asarray(img, dtype=np.float32) / 255.0
    small = img.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(10))
    b = np.asarray(small.resize((W, H), Image.BILINEAR), dtype=np.float32) / 255.0
    b = np.clip((b - 0.55) / 0.45, 0, 1)  # highlights only
    out = 1 - (1 - a) * (1 - b * strength)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8))


# ---------------------------------------------------------------- elements

class Ctx:
    def __init__(self, fi, frame, overlay, cam):
        self.fi, self.t = fi, fi / FPS
        self.frame, self.ov = frame, overlay
        self.z, self.cx, self.cy = cam[:3]

    def cap(self):
        tr = cap_at(self.fi)
        if not tr or tr[2] < 0.45:
            return None
        return to_screen(tr, self.z, self.cx, self.cy)


class Headline:
    """Kinetic two-line headline, words pop in one by one."""

    def __init__(self, t0, t1, lines, y=TOP_Y + 20, size=104, stagger=0.07):
        self.t0, self.t1, self.y, self.stagger = t0, t1, y, stagger
        styles = [
            dict(fill=(255, 255, 255), stroke=9, stroke_fill=ROSE),
            dict(fill=(255, 92, 147), stroke=9, stroke_fill=(255, 255, 255)),
        ]
        self.rows = []
        for li, line in enumerate(lines):
            st = styles[li % 2]
            sz = size
            words = line.split(" ")
            imgs = [text_img(w_, "Montserrat-ExtraBold.ttf", sz, st["fill"], st["stroke"], st["stroke_fill"], shadow=0.55)
                    for w_ in words]
            gap = -int(sz * 0.08)
            total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
            while total > TOP_W:
                sz -= 4
                imgs = [text_img(w_, "Montserrat-ExtraBold.ttf", sz, st["fill"], st["stroke"], st["stroke_fill"], shadow=0.55)
                        for w_ in words]
                gap = -int(sz * 0.08)
                total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
            self.rows.append((imgs, gap, total, sz))
        self.word_times = []
        k = 0
        for imgs, *_ in self.rows:
            self.word_times.append([t0 + 0.05 + (k + i) * stagger for i in range(len(imgs))])
            k += len(imgs)

    def sfx(self):
        return [("pop", wt) for row in self.word_times for wt in row[::2]] + [("sparkle", self.t0 + 0.05)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        out = clamp((self.t1 - c.t) / 0.2)
        y = self.y
        for (imgs, gap, total, sz), times in zip(self.rows, self.word_times):
            x = TOP_L + (TOP_W - total) / 2
            rh = max(i.height for i in imgs)
            for im, wt in zip(imgs, times):
                u = (c.t - wt) / 0.28
                if u > 0:
                    sc = 0.4 + 0.6 * ease_out_back(u)
                    paste(c.ov, im, x + im.width / 2, y + rh / 2 + (1 - ease_out_cubic(u)) * 24,
                          alpha=clamp(u * 2.5) * out, scale=sc * (0.96 + 0.04 * out))
                x += im.width + gap
            y += rh - int(sz * 0.12)


class InfoCard:
    """Glassmorphism card: title + subtitle, optional icon, optional leader to the cap."""

    def __init__(self, t0, t1, title, subtitle, y=TOP_Y, icon=None, rose=False, leader=False,
                 title_font="Playfair-ExtraBold.ttf", title_size=72, sub_size=42, sfx="ting"):
        self.t0, self.t1, self.y, self.icon, self.rose, self.leader, self.sfx_kind = t0, t1, y, icon, rose, leader, sfx
        avail = TOP_W - 90 - (110 if icon else 0)
        lines = wrap2(title, lambda tx: text_img(tx, title_font, title_size, DEEP_ROSE).width <= avail)
        ts = title_size
        while max(text_img(l, title_font, ts, DEEP_ROSE).width for l in lines) > avail:
            ts -= 3
        imgs = [text_img(l, title_font, ts, DEEP_ROSE) for l in lines]
        tw, th = max(i.width for i in imgs), sum(i.height for i in imgs) + int(ts * 0.2) * (len(imgs) - 1)
        self.title = Image.new("RGBA", (tw, th))
        yy = 0
        for i in imgs:
            self.title.alpha_composite(i, (0, yy))
            yy += i.height + int(ts * 0.2)
        ss = sub_size
        while True:
            self.sub = text_img(subtitle, "Montserrat-Bold.ttf", ss, MAUVE, tracking=1)
            if self.sub.width <= avail:
                break
            ss -= 2
        inner_w = max(self.title.width, self.sub.width) + (110 if icon else 0)
        self.w = min(TOP_W, inner_w + 90)
        self.h = self.title.height + self.sub.height + 84
        self.x0 = TOP_L + (TOP_W - self.w) / 2

    def sfx(self):
        return [(self.sfx_kind, self.t0 + 0.05), ("click", self.t0 + 0.22)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.32, 0.22)
        if v <= 0:
            return
        u = (c.t - self.t0) / 0.42
        sc = 0.82 + 0.18 * ease_out_back(u, 1.4)
        lift = (1 - ease_out_cubic(u)) * 40
        x0, y0 = self.x0, self.y + lift
        cap = c.cap() if self.leader else None
        if cap and cap[1] > y0 + self.h + 60:
            # leader line from card to the tracked cap, with a pulsing ring
            a = int(200 * v)
            d = ImageDraw.Draw(c.ov)
            sx, sy = x0 + self.w * 0.5, y0 + self.h + 8
            ex, ey = cap[0], cap[1] - 30
            prog = ease_out_cubic((c.t - self.t0 - 0.2) / 0.35)
            mx, my = sx + (ex - sx) * prog, sy + (ey - sy) * prog
            d.line([(sx, sy), (mx, my)], fill=(255, 255, 255, a), width=4)
            if prog > 0.95:
                pr = 22 + 10 * math.sin(c.t * 7)
                d.ellipse((ex - pr, ey - pr, ex + pr, ey + pr), outline=(255, 255, 255, a), width=4)
                d.ellipse((ex - 8, ey - 8, ex + 8, ey + 8), fill=(255, 120, 165, a))
        panel, m = glass_panel(c.frame, (x0, y0, x0 + self.w, y0 + self.h))
        tx = m + 45 + (110 if self.icon else 0)
        panel.alpha_composite(self.title, (int(tx), m + 30))
        panel.alpha_composite(self.sub, (int(tx), m + 30 + self.title.height + 18))
        if self.icon:
            b = badge_sprite(self.icon, 92)
            panel.alpha_composite(b, (m + 34, int(m + self.h / 2 - b.height / 2)))
        # thin champagne accent line
        ImageDraw.Draw(panel).rounded_rectangle((tx, m + 30 + self.title.height + 6, tx + 90, m + 30 + self.title.height + 10), 2,
                                                fill=CHAMPAGNE + (255,))
        paste(c.ov, panel, x0 + self.w / 2, y0 + self.h / 2 + 5, alpha=v, scale=sc)
        if self.rose:
            ru = ease_out_back((c.t - self.t0 - 0.12) / 0.5, 1.2)
            r = rose_sprite(300)
            paste(c.ov, r, x0 + self.w - 90, y0 + self.h + 90, alpha=v * clamp(ru), scale=0.5 + 0.5 * ru,
                  rot=-8 + 6 * math.sin(c.t * 1.3))


class Steps:
    """'CARA PENGGUNAAN' panel with three steps, the active one synced to the footage."""

    LABELS = ["1. Basahkan kapas", "2. Tekap seketika", "3. Lap perlahan-lahan"]

    def __init__(self, t0, t1, step_times, y=TOP_Y):
        self.t0, self.t1, self.y, self.step_times = t0, t1, y, step_times
        self.header = text_img("CARA PENGGUNAAN 🌸", "Montserrat-ExtraBold.ttf", 72, (255, 255, 255), 9, ROSE, shadow=0.5)
        self.col_w = TOP_W // 3
        self.labels = []

        def fit(tx, fn, size, col):
            while text_img(tx, fn, size, col).width > self.col_w - 24:
                size -= 2
            return text_img(tx, fn, size, col)

        for lab in self.LABELS:
            num, rest = lab.split(" ", 1)
            words = rest.split(" ")
            self.labels.append([fit(num + " " + words[0], "Montserrat-ExtraBold.ttf", 44, DEEP_ROSE),
                                fit(" ".join(words[1:]), "Montserrat-Bold.ttf", 40, MAUVE)])

    def active(self, t):
        k = -1
        for i, st in enumerate(self.step_times):
            if t >= st:
                k = i
        return k

    def sfx(self):
        return [("whoosh", self.t0), ("pop", self.t0 + 0.1)] + [("ting", st + 0.05) for st in self.step_times]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.3, 0.25)
        if v <= 0:
            return
        u = (c.t - self.t0) / 0.4
        paste(c.ov, self.header, W / 2, self.y + 40 + (1 - ease_out_cubic(u)) * 30, alpha=v,
              scale=0.7 + 0.3 * ease_out_back(u))
        ph = 340
        py = self.y + 110
        k = self.active(c.t)
        panel, m = glass_panel(c.frame, (TOP_L, py, TOP_R, py + ph), radius=40)
        for i in range(3):
            colx = m + i * self.col_w
            on = i == k
            ku = clamp((c.t - self.step_times[i]) / 0.3) if on else 0
            if on:
                hl = Image.new("RGBA", panel.size)
                ImageDraw.Draw(hl).rounded_rectangle((colx + 10, m + 12, colx + self.col_w - 10, m + ph - 12), 30,
                                                     fill=(255, 214, 228, int(220 * ku)), outline=(255, 140, 180, int(255 * ku)), width=4)
                panel.alpha_composite(hl)
            alpha = 1.0 if on else (0.55 if i < k else 0.42)
            cx = colx + self.col_w / 2
            # illustration
            ill = Image.new("RGBA", (self.col_w, 150))
            pad_s = 74
            if i == 0:
                wet = clamp((c.t - self.step_times[0]) / 1.2) if on else 1.0
                pad = cotton_pad_sprite(pad_s, wet)
                ill.alpha_composite(pad, (int(self.col_w / 2 - pad.width / 2), 150 - pad.height))
                if on:
                    dy = ((c.t - self.step_times[0]) * 1.6) % 1.0
                    dr = droplet_sprite(26)
                    paste(ill, dr, self.col_w / 2 + 6, 10 + dy * 60, alpha=1 - dy)
            elif i == 1:
                pad = cotton_pad_sprite(pad_s, 1.0)
                press = 1 - 0.08 * (0.5 + 0.5 * math.sin(c.t * 6)) if on else 1
                paste(ill, pad, self.col_w / 2, 150 - pad.height / 2, scale=press)
                # timer ring = hold
                if on:
                    p = clamp((c.t - self.step_times[1]) / 1.6)
                    ImageDraw.Draw(ill).arc((self.col_w / 2 - 62, 150 - pad.height / 2 - 62, self.col_w / 2 + 62, 150 - pad.height / 2 + 62),
                                            -90, -90 + 360 * p, fill=ROSE + (255,), width=7)
            else:
                pad = cotton_pad_sprite(pad_s, 1.0)
                sw = math.sin(c.t * 5) * 34 if on else 0
                paste(ill, pad, self.col_w / 2 + sw, 150 - pad.height / 2, rot=sw * 0.4)
                d = ImageDraw.Draw(ill)
                for j in range(3):
                    yy = 40 + j * 22
                    d.line([(20, yy), (48, yy)], fill=(255, 150, 185, 200), width=5)
            if alpha < 1:
                ill.putalpha(ill.getchannel("A").point(lambda vv: int(vv * alpha)))
            sc = 1 + 0.06 * ease_out_back(ku) if on else 1
            paste(panel, ill, cx, m + 20 + 75, scale=sc)
            ly = m + 190
            for lab in self.labels[i]:
                paste(panel, lab, cx, ly + lab.height / 2, alpha=alpha)
                ly += lab.height + 2
        pu = (c.t - self.t0 - 0.12) / 0.4
        paste(c.ov, panel, W / 2 - 0, py + ph / 2 + (1 - ease_out_cubic(pu)) * 40, alpha=v * clamp(pu * 2))


class Benefit:
    """One benefit at a time: rose badge + kinetic headline on a pearl pill."""

    def __init__(self, t0, t1, text, icon, y=TOP_Y + 20):
        self.t0, self.t1, self.y, self.icon = t0, t1, y, icon
        avail = TOP_W - 190
        size = 62
        lines = wrap2(text, lambda tx: text_img(tx, "Montserrat-ExtraBold.ttf", size, DEEP_ROSE).width <= avail)
        while max(text_img(l, "Montserrat-ExtraBold.ttf", size, DEEP_ROSE).width for l in lines) > avail:
            size -= 2
        imgs = [text_img(l, "Montserrat-ExtraBold.ttf", size, DEEP_ROSE) for l in lines]
        self.txt = Image.new("RGBA", (max(i.width for i in imgs), sum(i.height for i in imgs) + int(size * 0.2) * (len(imgs) - 1)))
        yy = 0
        for i in imgs:
            self.txt.alpha_composite(i, (0, yy))
            yy += i.height + int(size * 0.2)
        self.w = self.txt.width + 190
        self.h = max(140, self.txt.height + 56)

    def sfx(self):
        return [("ting", self.t0 + 0.04), ("pop", self.t0 + 0.14)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.25, 0.2)
        if v <= 0:
            return
        u = (c.t - self.t0) / 0.38
        x0 = TOP_L + (TOP_W - self.w) / 2 + (1 - ease_out_cubic(u)) * -60
        panel, m = glass_panel(c.frame, (x0, self.y, x0 + self.w, self.y + self.h), radius=70, opacity=0.72)
        b = badge_sprite(self.icon, 108)
        bu = ease_out_back((c.t - self.t0 - 0.06) / 0.35)
        paste(panel, b, m + 16 + b.width / 2, m + self.h / 2, scale=clamp(bu, 0.01, 2), rot=(1 - clamp(bu)) * 90)
        # wipe-reveal of the text
        reveal = ease_out_cubic((c.t - self.t0 - 0.1) / 0.35)
        txt = self.txt.crop((0, 0, max(1, int(self.txt.width * reveal)), self.txt.height))
        panel.alpha_composite(txt, (m + 156, int(m + self.h / 2 - self.txt.height / 2)))
        paste(c.ov, panel, x0 + self.w / 2, self.y + self.h / 2 + 5, alpha=v)


class CTA:
    def __init__(self, t0, t1, line1, line2, y=1300):
        self.t0, self.t1, self.y = t0, t1, y
        size = 64
        while text_img(line2, "Montserrat-ExtraBold.ttf", size, (255, 255, 255), shadow=0.35).width > SAFE_W - 100:
            size -= 2
        l1 = text_img(line1, "Montserrat-Bold.ttf", int(size * 0.72), (255, 236, 244), tracking=3)
        l2 = text_img(line2, "Montserrat-ExtraBold.ttf", size, (255, 255, 255), shadow=0.35)
        gap = int(size * 0.18)
        self.txt = Image.new("RGBA", (max(l1.width, l2.width), l1.height + gap + l2.height))
        self.txt.alpha_composite(l1, ((self.txt.width - l1.width) // 2, 0))
        self.txt.alpha_composite(l2, ((self.txt.width - l2.width) // 2, l1.height + gap))
        self.w, self.h = min(SAFE_W, self.txt.width + 110), self.txt.height + 64
        g = Image.linear_gradient("L").rotate(90).resize((self.w, self.h))
        btn = Image.composite(Image.new("RGBA", (self.w, self.h), (255, 120, 165, 255)),
                              Image.new("RGBA", (self.w, self.h), DEEP_ROSE + (255,)), g)
        btn.putalpha(rounded_mask(self.w, self.h, self.h // 2))
        ImageDraw.Draw(btn).rounded_rectangle((3, 3, self.w - 4, self.h - 4), self.h // 2, outline=(255, 255, 255, 230), width=4)
        btn.alpha_composite(self.txt, ((self.w - self.txt.width) // 2, (self.h - self.txt.height) // 2))
        glow = Image.new("RGBA", (self.w + 120, self.h + 120))
        ImageDraw.Draw(glow).rounded_rectangle((60, 60, self.w + 60, self.h + 60), self.h // 2, fill=(255, 110, 160, 210))
        self.glow = glow.filter(ImageFilter.GaussianBlur(26))
        self.btn = btn

    def sfx(self):
        return [("chime", self.t0), ("sparkle", self.t0 + 0.1)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1 + 1, 0.3, 0.3)
        if v <= 0:
            return
        u = (c.t - self.t0) / 0.5
        pulse = 1 + 0.035 * math.sin((c.t - self.t0) * 6.5) * clamp(u - 1)
        cx = SAFE_L + SAFE_W / 2
        paste(c.ov, self.glow, cx, self.y, alpha=v * (0.55 + 0.35 * math.sin(c.t * 6.5) ** 2), scale=pulse)
        paste(c.ov, self.btn, cx, self.y, alpha=v, scale=(0.6 + 0.4 * ease_out_back(u)) * pulse)
        # light sweep across the button
        sweep = ((c.t - self.t0 - 0.6) % 1.6) / 0.6
        if 0 < sweep < 1:
            band = Image.new("RGBA", (self.w, self.h))
            bx = int(-80 + sweep * (self.w + 160))
            ImageDraw.Draw(band).polygon([(bx, 0), (bx + 50, 0), (bx + 10, self.h), (bx - 40, self.h)], fill=(255, 255, 255, 110))
            band.putalpha(ImageChops.multiply(band.getchannel("A"), rounded_mask(self.w, self.h, self.h // 2)))
            paste(c.ov, band, cx, self.y, alpha=v * pulse)


class Particles:
    """Deterministic particle emitter. kind: sparkle/petal/droplet/bubble/heart/dust."""

    def __init__(self, t0, t1, kind, area, rate, life=(1.2, 2.2), size=(18, 34), vel=((-30, 30), (-80, -20)),
                 follow_cap=False, seed=1, colors=None, gravity=0.0):
        rng = random.Random(seed)
        self.kind, self.follow_cap = kind, follow_cap
        self.t0, self.t1 = t0, t1
        self.ps = []
        n = int((t1 - t0) * rate)
        for i in range(n):
            st = t0 + (t1 - t0) * i / max(1, n) + rng.uniform(0, 1 / rate)
            self.ps.append(dict(
                st=st, life=rng.uniform(*life),
                x=rng.uniform(area[0], area[2]), y=rng.uniform(area[1], area[3]),
                vx=rng.uniform(*vel[0]), vy=rng.uniform(*vel[1]),
                size=rng.randint(*size), rot=rng.uniform(0, 360), vr=rng.uniform(-120, 120),
                shade=rng.randint(0, 2), color=rng.choice(colors) if colors else None,
                ph=rng.uniform(0, 6.28)))
        self.gravity = gravity

    def draw(self, c):
        if c.t < self.t0 - 0.1 or c.t > self.t1 + 3:
            return
        off = (0, 0)
        if self.follow_cap:
            cap = c.cap()
            if cap is None:
                return
            off = (cap[0], cap[1])
        for p in self.ps:
            a = c.t - p["st"]
            if a < 0 or a > p["life"]:
                continue
            u = a / p["life"]
            x = off[0] + p["x"] + p["vx"] * a + math.sin(p["ph"] + a * 2.2) * 14
            y = off[1] + p["y"] + p["vy"] * a + 0.5 * self.gravity * a * a
            fade = clamp(u / 0.15) * clamp((1 - u) / 0.35)
            k = self.kind
            if k == "sparkle":
                tw = 0.6 + 0.4 * math.sin(p["ph"] + a * 9)
                paste(c.ov, sparkle_sprite(p["size"]), x, y, alpha=fade * tw, scale=0.6 + 0.6 * tw)
            elif k == "petal":
                paste(c.ov, petal_sprite(p["size"], p["shade"]), x, y, alpha=fade * 0.95,
                      rot=p["rot"] + p["vr"] * a, scale=0.7 + 0.3 * abs(math.sin(p["ph"] + a * 2.5)))
            elif k == "droplet":
                paste(c.ov, droplet_sprite(p["size"]), x, y, alpha=fade)
            elif k == "bubble":
                paste(c.ov, bubble_sprite(p["size"]), x, y, alpha=fade, scale=0.8 + 0.4 * u)
            elif k == "heart":
                paste(c.ov, heart_sprite(p["size"]), x, y, alpha=fade, scale=0.7 + 0.4 * ease_out_back(u * 3),
                      rot=math.sin(p["ph"] + a * 3) * 15)
            elif k == "dust":
                # makeup particles that dissolve as they are "cleansed"
                paste(c.ov, dust_sprite(p["size"], p["color"]), x, y, alpha=fade * (1 - u) ** 0.5, scale=0.8 + u)


class Ripples:
    def __init__(self, t0, t1, period=0.55):
        self.t0, self.t1, self.period = t0, t1, period

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        cap = c.cap()
        if cap is None:
            return
        d = ImageDraw.Draw(c.ov)
        v = env(c.t, self.t0, self.t1, 0.3, 0.3)
        for k in range(3):
            ph = ((c.t - self.t0) / self.period + k / 3) % 1.0
            r = 40 + ph * 220
            a = int(170 * (1 - ph) * v)
            d.ellipse((cap[0] - r, cap[1] - r * 0.45, cap[0] + r, cap[1] + r * 0.45), outline=(255, 255, 255, a), width=4)


class Flash:
    """Soft pink light-leak on a cut."""

    def __init__(self, t, strength=0.32, dur=0.22):
        self.t, self.s, self.dur = t, strength, dur
        g = Image.radial_gradient("L").resize((W, H)).point(lambda v: 255 - v)
        self.img = Image.new("RGBA", (W, H), (255, 228, 238, 255))
        self.img.putalpha(g)

    def draw(self, c):
        u = (c.t - self.t) / self.dur
        if 0 <= u <= 1:
            paste(c.ov, self.img, W / 2, H / 2, alpha=self.s * (1 - ease_out_cubic(u)))


class Vignette:
    """Pearl-pink top gradient so the info zone always reads."""

    def __init__(self):
        g = Image.linear_gradient("L").resize((W, 700)).point(lambda v: int((255 - v) * 0.30))
        self.top = Image.new("RGBA", (W, 700), (255, 236, 243, 255))
        self.top.putalpha(g)

    def draw(self, c):
        c.ov.alpha_composite(self.top, (0, 0))


# ---------------------------------------------------------------- the script

def build_elements():
    S, E = seg_start, seg_end
    els = [Vignette()]
    cuts = [s for _, s, _, _ in timeline()][1:]
    els += [Flash(t) for t in cuts]

    # 1. HOOK (0-2 s)
    els.append(Headline(0.0, S("intro") - 0.02, ["MASIH TIDUR DENGAN", "SISA MAKEUP? 😳"]))
    els.append(Particles(0.05, 0.6, "sparkle", (150, 230, 930, 560), 30, life=(0.4, 0.9), size=(16, 30), vel=((-160, 160), (-120, 80)), seed=2))

    # 2. PRODUCT INTRO
    t = S("intro")
    els.append(Headline(t, t + 1.25, ["JOM KENAL", "MICELLAR WATER INI! 🌸"]))
    els.append(Particles(t, t + 0.5, "sparkle", (200, 260, 880, 520), 24, life=(0.4, 0.8), size=(14, 26), vel=((-140, 140), (-100, 60)), seed=3))
    els.append(InfoCard(t + 1.2, E("intro") - 0.05, "O’CHEAL MICELLAR WATER", "300ML | PENCUCI SOLEKAN", leader=True, title_size=74))
    els.append(Particles(t + 1.2, E("intro"), "petal", (60, 120, 1000, 300), 7, life=(2.0, 2.8), size=(20, 32), vel=((-40, 40), (140, 260)), seed=4))
    els.append(Particles(t + 1.3, E("intro"), "sparkle", (-120, -160, 120, 160), 14, life=(0.5, 1.0), size=(12, 22), vel=((-40, 40), (-60, 20)), follow_cap=True, seed=5))

    # 3. LIFT / ROTATE -> cleansing
    t, e = S("lift"), E("lift")
    els.append(InfoCard(t + 0.05, e - 0.03, "✨ BANTU TANGGALKAN SOLEKAN", "Membersihkan sisa makeup & kotoran", leader=True,
                        title_font="Montserrat-ExtraBold.ttf", title_size=58, sfx="swish"))
    els.append(Particles(t + 0.1, e, "dust", (-150, 80, 150, 420), 40, life=(0.7, 1.2), size=(8, 16), vel=((-60, 60), (-260, -120)),
                         follow_cap=True, seed=6, colors=[(224, 122, 139), (139, 90, 74), (201, 77, 92), (230, 170, 150)]))
    els.append(Particles(t + 0.3, e, "droplet", (-160, 0, 160, 300), 9, life=(0.8, 1.3), size=(14, 22), vel=((-30, 30), (-160, -80)), follow_cap=True, seed=7))

    # 4. FRONT LABEL -> ingredients
    t, e = S("label"), E("label")
    els.append(InfoCard(t + 0.03, e - 0.03, "🌹 HYALURONIC ACID + ROSE", "Membantu mengekalkan kelembapan kulit", rose=True,
                        title_font="Montserrat-ExtraBold.ttf", title_size=58, sfx="sparkle"))
    els.append(Particles(t, e, "bubble", (150, 900, 950, 1450), 12, life=(1.2, 1.8), size=(18, 40), vel=((-20, 20), (-260, -150)), seed=8))
    els.append(Particles(t + 0.2, e, "sparkle", (-140, -120, 140, 260), 12, life=(0.5, 1.0), size=(12, 22), vel=((-20, 20), (-40, 20)), follow_cap=True, seed=9))

    # 5. BOTTLE CLOSER -> fresh feel
    t, e = S("closer"), E("closer")
    els.append(InfoCard(t + 0.05, e - 0.05, "💗 RASA SEGAR SELEPAS MEMBERSIH", "Rutin pembersihan wajah yang mudah", leader=True,
                        title_font="Montserrat-ExtraBold.ttf", title_size=58))
    els.append(Ripples(t + 0.3, e - 0.1))
    els.append(Particles(t + 0.2, e, "droplet", (-200, -260, 200, 60), 10, life=(0.9, 1.4), size=(14, 24), vel=((-40, 40), (-120, -60)), follow_cap=True, seed=10))

    # 6. HOW TO USE (pump -> eye press -> wipe)
    els.append(Steps(S("pump"), E("wipe") - 0.05, [S("pump") + 0.35, S("press"), S("wipe")]))
    els.append(Particles(S("pump") + 0.4, E("pump"), "droplet", (-60, -40, 60, 40), 4, life=(0.8, 1.0), size=(16, 22), vel=((-10, 10), (60, 120)), follow_cap=True, seed=11))
    els.append(Particles(S("press") + 0.2, E("press"), "sparkle", (220, 760, 860, 980), 10, life=(0.5, 1.0), size=(12, 22), vel=((-20, 20), (-40, 0)), seed=12))

    # 7. BENEFITS during the real wipe footage, one at a time
    bstart, bend = S("wipe2"), E("wipe3")
    bens = [("MEMBANTU MENANGGALKAN SOLEKAN", "sparkle"), ("MEMBERSIHKAN SISA KOTORAN", "bubbles"),
            ("DENGAN HYALURONIC ACID", "drop"), ("MEMBANTU KEKALKAN KELEMBAPAN", "wave")]
    step = (bend - bstart) / len(bens)
    for i, (txt, icon) in enumerate(bens):
        els.append(Benefit(bstart + i * step, bstart + (i + 1) * step - 0.04, txt, icon))
    els.append(Particles(bstart, bend, "bubble", (120, 1100, 960, 1450), 5, life=(1.5, 2.2), size=(16, 32), vel=((-20, 20), (-200, -120)), seed=13))

    # 8. CLEAN FACE -> payoff
    t, e = S("clean"), E("clean")
    els.append(Benefit(t + 0.05, t + 1.35, "RASA SEGAR & SELESA", "heart"))
    els.append(Particles(t, e, "sparkle", (260, 650, 820, 1150), 9, life=(0.6, 1.2), size=(14, 26), vel=((-10, 10), (-30, 0)), seed=14))
    els.append(Headline(t + 1.4, e - 0.02, ["MAKEUP DAH TANGGAL,", "BARU LEGA! 💗"], size=100))
    els.append(Particles(t + 1.4, e, "heart", (200, 1150, 880, 1350), 6, life=(1.2, 1.6), size=(22, 36), vel=((-30, 30), (-220, -140)), seed=15))

    # 9. HERO + CTA
    t, e = S("hero"), E("hero")
    els.append(InfoCard(t + 0.05, e + 1, "O’CHEAL MICELLAR WATER 300ML 🌸", "PENCUCI SOLEKAN HARIAN", title_size=58, leader=False,
                        title_font="Montserrat-ExtraBold.ttf", sfx="ting"))
    els.append(CTA(t + 0.7, e, "NAK CUBA?", "CHECK BEG KUNING 🛍️"))
    els.append(Particles(t, e + 1, "petal", (40, 60, 1040, 400), 9, life=(2.2, 3.0), size=(22, 36), vel=((-50, 50), (150, 260)), seed=16))
    els.append(Particles(t + 0.2, e + 1, "sparkle", (-170, -200, 170, 420), 16, life=(0.5, 1.1), size=(12, 26), vel=((-20, 20), (-40, 20)), follow_cap=True, seed=17))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    for n, s, e, seg in timeline()[1:]:
        cues.append(("whoosh" if n not in ("lift", "label") else "swish", s - 0.12))
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


# ---------------------------------------------------------------- audio

SR = 48000


def _t(d):
    return np.arange(int(d * SR)) / SR


def adsr(n, a=0.005, r=0.2):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (r * SR))
    return e


def bell(freq, d=0.8, decay=0.25):
    t = _t(d)
    s = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.76 * t) + 0.2 * np.sin(2 * np.pi * freq * 5.4 * t)
    return s * adsr(len(t), 0.002, decay)


def noise(d, seed=0):
    return np.random.default_rng(seed).standard_normal(int(d * SR))


def bandpass_sweep(x, f0, f1):
    """Crude time-varying band-pass via short FFT frames."""
    out = np.zeros_like(x)
    hop, n = 512, 2048
    win = np.hanning(n)
    frames = max(1, (len(x) - n) // hop)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    for i in range(frames):
        u = i / frames
        fc = f0 * (f1 / f0) ** u
        seg = x[i * hop:i * hop + n] * win
        spec = np.fft.rfft(seg)
        spec *= np.exp(-((np.log(freqs + 1) - np.log(fc)) ** 2) / 0.35)
        out[i * hop:i * hop + n] += np.fft.irfft(spec) * win
    return out / (np.abs(out).max() + 1e-9)


def make_sfx():
    fx = {}
    t = _t(0.09)
    f = np.linspace(900, 260, len(t))
    fx["pop"] = 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * adsr(len(t), 0.001, 0.03)
    fx["ting"] = 0.32 * (bell(2093, 0.9, 0.22) + 0.6 * bell(3136, 0.9, 0.16))
    w = noise(0.42, 1) * np.hanning(int(0.42 * SR))
    fx["whoosh"] = 0.30 * bandpass_sweep(w, 500, 5000) * np.hanning(int(0.42 * SR))
    s = noise(0.22, 2) * np.hanning(int(0.22 * SR))
    fx["swish"] = 0.26 * bandpass_sweep(s, 2500, 7000) * np.hanning(int(0.22 * SR))
    c = np.zeros(int(0.05 * SR))
    c[:int(0.004 * SR)] = noise(0.004, 3) * np.linspace(1, 0, int(0.004 * SR))
    c += 0.25 * np.sin(2 * np.pi * 3800 * _t(0.05)) * adsr(len(c), 0.0005, 0.006)
    fx["click"] = 0.45 * c
    sp = np.zeros(int(0.9 * SR))
    rng = np.random.default_rng(4)
    for k in range(9):
        st = int(k * 0.06 * SR)
        b = bell(rng.uniform(3000, 5600), 0.4, 0.07) * (1 - k / 11)
        sp[st:st + len(b)] += b[:len(sp) - st]
    fx["sparkle"] = 0.16 * sp
    ch = np.zeros(int(2.0 * SR))
    for k, fr in enumerate([1318.5, 1568, 1975.5, 2637]):
        b = bell(fr, 1.6, 0.5)
        st = int(k * 0.07 * SR)
        ch[st:st + len(b)] += b[:len(ch) - st]
    fx["chime"] = 0.2 * ch
    return fx


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(freq, d, seed=0):
    """Karplus-Strong pluck."""
    n = int(d * SR)
    p = max(2, int(SR / freq))
    buf = np.random.default_rng(seed).uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out


def make_music(dur):
    """Original 116 BPM K-beauty pop bed: pad, pluck arps, soft drums, sub bass."""
    bpm = 116
    beat = 60 / bpm
    n = int((dur + 2.5) * SR)
    mix = np.zeros((n, 2))
    # IV - V - iii - vi in D major, one bar each
    chords = [[55, 59, 62, 66], [57, 61, 64, 67], [54, 57, 61, 64], [59, 62, 66, 69]]
    bar = 4 * beat
    nbars = int(dur / bar) + 2
    pad_t = _t(bar)
    for b in range(nbars):
        ch = chords[b % 4]
        st = int(b * bar * SR)
        pad = np.zeros(len(pad_t))
        for m in ch:
            for det in (-0.08, 0.08):
                pad += np.sin(2 * np.pi * note(m) * (1 + det / 100) * pad_t + np.sin(2 * np.pi * 0.3 * pad_t))
        pad *= np.minimum(1, pad_t / 0.25) * np.minimum(1, (bar - pad_t) / 0.3) * 0.022
        seg = mix[st:st + len(pad)]
        seg[:, 0] += pad[:len(seg)]
        seg[:, 1] += pad[:len(seg)]
        # bass on beats 1 and 3
        for k in (0, 2):
            bt = _t(beat * 1.8)
            bs = np.sin(2 * np.pi * note(ch[0] - 24) * bt) * adsr(len(bt), 0.01, 0.35) * 0.16
            s2 = st + int(k * beat * SR)
            seg2 = mix[s2:s2 + len(bs)]
            seg2 += bs[:len(seg2), None]
        # pluck arpeggio in 8ths
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[3] + 12, ch[2] + 24]
        for k, m in enumerate(arp):
            pl = pluck(note(m), beat * 0.9, seed=b * 8 + k) * 0.07
            s2 = st + int(k * beat / 2 * SR)
            pan = 0.35 if k % 2 else -0.35
            seg2 = mix[s2:s2 + len(pl)]
            seg2[:, 0] += pl[:len(seg2)] * (1 - pan)
            seg2[:, 1] += pl[:len(seg2)] * (1 + pan)
    # drums
    total_beats = int(dur / beat) + 4
    kt = _t(0.3)
    kick = np.sin(2 * np.pi * np.cumsum(np.linspace(120, 45, len(kt))) / SR) * adsr(len(kt), 0.001, 0.12) * 0.42
    snap = noise(0.15, 9) * adsr(int(0.15 * SR), 0.001, 0.035) * 0.13
    hat = noise(0.05, 10)
    hat = np.diff(np.concatenate([[0], hat])) * adsr(len(hat), 0.0005, 0.012) * 0.05
    for k in range(total_beats):
        st = int(k * beat * SR)
        if k * beat > dur + 0.3:
            break
        for snd, off in [(kick, 0)] + ([(snap, 0)] if k % 2 else []) + [(hat, 0), (hat, beat / 2)]:
            s2 = st + int(off * SR)
            seg = mix[s2:s2 + len(snd)]
            seg += snd[:len(seg), None]
    return mix[:n]


def make_audio(cues, path):
    music = make_music(TOTAL)
    fx = make_sfx()
    n = int((TOTAL + 0.05) * SR)
    out = music[:n].copy()
    # fade the bed out with the final chime
    tail = int(1.2 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 1.5
    for kind, t in cues:
        s = fx[kind]
        st = int(t * SR)
        seg = out[st:st + len(s)]
        seg += s[:len(seg), None] * 0.9
    out /= np.abs(out).max() / 0.89
    pcm = (out * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- main

def frames_from(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1)
    p.wait()


def render_frame(fi, img, els):
    cam = camera(fi)
    img = apply_camera(img, *cam[:3])
    img = bloom(img)
    frame = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    c = Ctx(fi, frame, ov, cam)
    for el in els:
        el.draw(c)
    return Image.alpha_composite(frame, ov).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    load_track()
    els = build_elements()
    base = ROOT / "build" / "base.mp4"
    if args.stills:
        outdir = ROOT / "build" / "stills"
        outdir.mkdir(exist_ok=True)
        want = {round(t * FPS) for t in
                [0.5, 1.6, 2.6, 3.9, 5.6, 7.4, 9.4, 11.8, 14.2, 16.6, 18.6, 20.4, 22.0, 23.4, 24.7, 26.2, 27.6, 28.6, 29.5]}
        for fi, img in enumerate(frames_from(base)):
            if fi in want:
                render_frame(fi, img, els).save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
        return
    wav = ROOT / "build" / "audio.wav"
    make_audio(cue_list(els), wav)
    OUT.parent.mkdir(exist_ok=True)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(wav),
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)
    for fi, img in enumerate(frames_from(base)):
        enc.stdin.write(render_frame(fi, img, els).tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{round(TOTAL * FPS)}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
