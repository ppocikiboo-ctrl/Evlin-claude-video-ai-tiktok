"""Render the VTLM self-care TikTok ad (30s, 1080x1920, 30 fps) as a 2.5D
motion-graphics cut that follows the timeline in ../PROMPT_PACK.md.

    python3 vtlm_render.py out.mp4 [--audio mix.wav] [--frames 0,90,300]

--frames writes those frames as PNGs next to out.mp4 instead of a video.
Every frame is a pure function of its time, so frames render in parallel.
"""
import argparse
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
BALOO = os.path.join(FONT_DIR, "Baloo2-ExtraBold.ttf")
POPPINS_SB = os.path.join(FONT_DIR, "Poppins-SemiBold.ttf")
POPPINS_B = os.path.join(FONT_DIR, "Poppins-Bold.ttf")
PLAYFAIR = os.path.join(FONT_DIR, "Playfair-Bold.ttf")
EMOJI_FONT = os.environ.get("EMOJI_FONT", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")

W, H, FPS, DUR = 1080, 1920, 30, 30.0
N_FRAMES = int(FPS * DUR)

# Music grid: bars land on the BOOM (3.2s) and the product reveal (17.0s).
BAR = 13.8 / 7
BEAT = BAR / 4
B0 = 3.2


def bt(k):
    return B0 + k * BAR


# Scene cuts (seconds)
T_BOOM = bt(0)            # 3.20
T_WHIP = 4.45
T_TOUCH = bt(1)           # 5.17
T_TITLE2 = bt(2)          # 7.14
T_MAP = bt(3)             # 9.11
T_FOCUS = [bt(4), bt(5), bt(6)]  # 11.09 13.06 15.03
T_RIBBON = bt(7)          # 17.00
T_POUCH = 18.40
T_BRAND = bt(8)           # 18.97
T_SUB = bt(9)             # 20.94
T_SHOP = bt(10)           # 22.91
T_END = bt(12)            # 26.86

# Palette
LAV = np.array([183, 156, 255]) / 255
BLUSH = np.array([247, 198, 217]) / 255
PEARL = np.array([255, 248, 251]) / 255
GOLD = np.array([230, 198, 135]) / 255
PEACH = np.array([255, 216, 194]) / 255
MOON = np.array([143, 168, 232]) / 255
PINK = np.array([255, 110, 170]) / 255


# ---------------------------------------------------------------- easing

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_in(x):
    return clamp(x) ** 3


def ease_back(x, s=1.9):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def elastic(x):
    x = clamp(x)
    if x in (0.0, 1.0):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * 2 * math.pi / 3) + 1


def lerp(a, b, t):
    return a + (b - a) * t


def window(t, t0, t1, fade_in=0.15, fade_out=0.15):
    """1 inside [t0, t1], ramping in and out."""
    if t < t0 or t > t1:
        return 0.0
    return min(smooth((t - t0) / fade_in) if fade_in else 1.0,
               smooth((t1 - t) / fade_out) if fade_out else 1.0)


# ---------------------------------------------------------- compositing

def np_rgba(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def _clip(dst, h, w, x, y):
    x0, y0 = int(round(x)), int(round(y))
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return None
    return dy0, dy1, dx0, dx1, dy0 - y0, dx0 - x0


def over(dst, src, x, y, op=1.0):
    """Alpha-composite RGBA float array src with its top-left at (x, y)."""
    c = _clip(dst, src.shape[0], src.shape[1], x, y)
    if c is None or op <= 0:
        return
    dy0, dy1, dx0, dx1, sy, sx = c
    s = src[sy:sy + dy1 - dy0, sx:sx + dx1 - dx0]
    a = s[..., 3:4] * op
    d = dst[dy0:dy1, dx0:dx1]
    d *= 1 - a
    d += s[..., :3] * a


def add(dst, src, x, y, k=1.0):
    """Additive blend (glows, particles)."""
    c = _clip(dst, src.shape[0], src.shape[1], x, y)
    if c is None or k <= 0:
        return
    dy0, dy1, dx0, dx1, sy, sx = c
    s = src[sy:sy + dy1 - dy0, sx:sx + dx1 - dx0]
    dst[dy0:dy1, dx0:dx1] += s[..., :3] * s[..., 3:4] * k


def place(dst, img, cx, cy, scale=1.0, rot=0.0, op=1.0, mode="over"):
    """Draw a PIL RGBA sprite centred at (cx, cy)."""
    if op <= 0.003 or scale <= 0.01:
        return
    if scale != 1.0:
        w, h = max(1, int(img.width * scale)), max(1, int(img.height * scale))
        img = img.resize((w, h), Image.BILINEAR)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    arr = np_rgba(img)
    x, y = cx - img.width / 2, cy - img.height / 2
    (over if mode == "over" else add)(dst, arr, x, y, op)


_GLOW = {}


def glow_sprite(size):
    size = max(3, int(size)) | 1
    if size not in _GLOW:
        r = np.linspace(-1, 1, size)
        g = np.exp(-(r[None, :] ** 2 + r[:, None] ** 2) * 6.0).astype(np.float32)
        _GLOW[size] = g
    return _GLOW[size]


def dot(dst, x, y, size, col, k=1.0):
    g = glow_sprite(size)
    s = g.shape[0]
    c = _clip(dst, s, s, x - s / 2, y - s / 2)
    if c is None:
        return
    dy0, dy1, dx0, dx1, sy, sx = c
    dst[dy0:dy1, dx0:dx1] += g[sy:sy + dy1 - dy0, sx:sx + dx1 - dx0, None] * (np.asarray(col) * k)


_STAR = {}


def star_sprite(size):
    size = max(5, int(size)) | 1
    if size not in _STAR:
        r = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(r, r)
        rays = np.exp(-(X / 0.035) ** 2) * np.exp(-np.abs(Y) * 3.2) + \
            np.exp(-(Y / 0.035) ** 2) * np.exp(-np.abs(X) * 3.2)
        core = np.exp(-(X ** 2 + Y ** 2) * 40)
        _STAR[size] = np.clip(rays * 0.9 + core, 0, 1).astype(np.float32)
    return _STAR[size]


def star(dst, x, y, size, col, k=1.0):
    g = star_sprite(size)
    s = g.shape[0]
    c = _clip(dst, s, s, x - s / 2, y - s / 2)
    if c is None:
        return
    dy0, dy1, dx0, dx1, sy, sx = c
    dst[dy0:dy1, dx0:dx1] += g[sy:sy + dy1 - dy0, sx:sx + dx1 - dx0, None] * (np.asarray(col) * k)


def frost(dst, sprite, cx, cy, radius=14):
    """Blur the frame under a sprite's alpha (glassmorphism)."""
    x0, y0 = int(cx - sprite.width / 2), int(cy - sprite.height / 2)
    c = _clip(dst, sprite.height, sprite.width, x0, y0)
    if c is None:
        return
    dy0, dy1, dx0, dx1, sy, sx = c
    region = dst[dy0:dy1, dx0:dx1]
    im = Image.fromarray((region.clip(0, 1) * 255).astype(np.uint8))
    bl = np_rgba(im.filter(ImageFilter.GaussianBlur(radius)))
    a = np_rgba(sprite.getchannel("A"))[sy:sy + dy1 - dy0, sx:sx + dx1 - dx0, None]
    region[:] = region * (1 - a) + bl * a


# ---------------------------------------------------------------- text

def split_runs(text):
    runs, cur, kind = [], "", None
    for ch in text.replace("️", ""):
        k = "e" if ord(ch) >= 0x2600 else "t"
        if k != kind and cur:
            runs.append((kind, cur))
            cur = ""
        kind = k
        cur += ch
    if cur:
        runs.append((kind, cur))
    return runs


_EMOJI = {}


def emoji_img(ch):
    if ch not in _EMOJI:
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 20), ch, font=f, embedded_color=True)
        _EMOJI[ch] = im.crop(im.getbbox())
    return _EMOJI[ch]


def emoji(ch, height):
    im = emoji_img(ch)
    return im.resize((max(1, int(im.width * height / im.height)), int(height)), Image.LANCZOS)


def shifted(mask, dx, dy):
    out = Image.new("L", mask.size, 0)
    out.paste(mask, (dx, dy))
    return out


def solid(size, col, mask, k=1.0):
    layer = Image.new("RGBA", size, tuple(int(c) for c in col) + (0,))
    layer.putalpha(mask.point(lambda v: int(v * k)) if k != 1.0 else mask)
    return layer


def text_sprite(text, font, size, top=(255, 255, 255), bot=None, stroke=0,
                stroke_col=(255, 92, 154), extrude=0, ext_top=(236, 200, 120),
                ext_bot=(150, 110, 45), glow=0, glow_col=(255, 140, 190), glow_k=0.85,
                shadow=0.4, emoji_scale=1.0):
    f = ImageFont.truetype(font, size)
    asc, desc = f.getmetrics()
    cb = f.getbbox("H")
    cap_mid = (cb[1] + cb[3]) / 2
    items, x = [], 0.0
    for kind, s in split_runs(text):
        if kind == "t":
            items.append(("t", s, x))
            x += f.getlength(s)
        else:
            for ch in s:
                em = emoji(ch, size * 0.82 * emoji_scale)
                x += size * 0.06
                items.append(("e", em, x))
                x += em.width + size * 0.02
    pad = stroke + extrude + glow * 3 + 14
    size2 = (int(math.ceil(x + 2 * pad)), int(asc + desc + 2 * pad))
    face = Image.new("L", size2, 0)
    strk = Image.new("L", size2, 0)
    emm = Image.new("L", size2, 0)
    df, ds = ImageDraw.Draw(face), ImageDraw.Draw(strk)
    for kind, s, x0 in items:
        if kind == "t":
            df.text((pad + x0, pad), s, font=f, fill=255)
            ds.text((pad + x0, pad), s, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
        else:
            emm.paste(s.getchannel("A"), (int(pad + x0), int(pad + cap_mid - s.height / 2)))
    sil = ImageChops.lighter(strk, emm)
    out = Image.new("RGBA", size2, (0, 0, 0, 0))
    if glow:
        out.alpha_composite(solid(size2, glow_col, sil.filter(ImageFilter.GaussianBlur(glow)), glow_k))
    if shadow:
        sh = shifted(sil, 0, int(size * 0.05) + extrude).filter(ImageFilter.GaussianBlur(size * 0.05))
        out.alpha_composite(solid(size2, (30, 8, 50), sh, shadow))
    for d in range(extrude, 0, -1):
        t = d / extrude
        col = [lerp(a, b, t) for a, b in zip(ext_top, ext_bot)]
        out.alpha_composite(solid(size2, col, shifted(strk, 0, d)))
    if stroke:
        out.alpha_composite(solid(size2, stroke_col, strk))
    bot = bot or top
    grad = np.linspace(0, 1, size2[1])[:, None, None]
    g = (np.array(top)[None, None] * (1 - grad) + np.array(bot)[None, None] * grad)
    g = np.broadcast_to(g, (size2[1], size2[0], 3)).astype(np.uint8)
    fl = Image.fromarray(g).convert("RGBA")
    fl.putalpha(face)
    out.alpha_composite(fl)
    for kind, s, x0 in items:
        if kind == "e":
            out.alpha_composite(s, (int(pad + x0), int(pad + cap_mid - s.height / 2)))
    return out.crop(out.getbbox())


def pill_sprite(text_img, padx=40, pady=18, fill=(64, 36, 112, 165),
                border=(255, 255, 255, 170), glow_col=(190, 160, 255), radius=None):
    tw, th = text_img.size
    w, h = tw + 2 * padx, th + 2 * pady
    m = 26
    ss = 3
    radius = radius or h // 2
    base = Image.new("RGBA", ((w + 2 * m) * ss, (h + 2 * m) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    box = [m * ss, m * ss, (m + w) * ss, (m + h) * ss]
    d.rounded_rectangle(box, radius=radius * ss, fill=fill, outline=border, width=3 * ss)
    base = base.resize((w + 2 * m, h + 2 * m), Image.LANCZOS)
    ring = Image.new("L", base.size, 0)
    ImageDraw.Draw(ring).rounded_rectangle([m, m, m + w, m + h], radius=radius, outline=255, width=4)
    out = solid(base.size, glow_col, ring.filter(ImageFilter.GaussianBlur(9)), 0.9)
    out.alpha_composite(base)
    out.alpha_composite(text_img, (m + padx, m + pady))
    return out


# ------------------------------------------------------------- shapes

def heart_sprite(size, top=(255, 150, 195), bot=(255, 72, 140), glow=True):
    ss = 3
    S = size * ss
    t = np.linspace(0, 2 * math.pi, 200)
    x = 16 * np.sin(t) ** 3
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    pts = [(S / 2 + xi * S / 38, S / 2 + yi * S / 38 - S * 0.02) for xi, yi in zip(x, y)]
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    grad = np.linspace(0, 1, size)[:, None, None]
    g = np.array(top)[None, None] * (1 - grad) + np.array(bot)[None, None] * grad
    body = Image.fromarray(np.broadcast_to(g, (size, size, 3)).astype(np.uint8)).convert("RGBA")
    body.putalpha(mask)
    # gloss
    hl = Image.new("L", (size, size), 0)
    ImageDraw.Draw(hl).ellipse([size * 0.22, size * 0.2, size * 0.42, size * 0.34], fill=200)
    hl = ImageChops.multiply(hl.filter(ImageFilter.GaussianBlur(size * 0.03)), mask)
    body.alpha_composite(solid((size, size), (255, 255, 255), hl))
    if not glow:
        return body
    pad = size // 3
    out = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    gm = Image.new("L", out.size, 0)
    gm.paste(mask, (pad, pad))
    out.alpha_composite(solid(out.size, (255, 120, 180), gm.filter(ImageFilter.GaussianBlur(size * 0.12)), 0.8))
    out.alpha_composite(body, (pad, pad))
    return out


def vgrad(h, w, stops):
    """Vertical gradient from [(pos, rgb01), ...]."""
    ys = np.linspace(0, 1, h)
    out = np.zeros((h, 3), np.float32)
    pos = [p for p, _ in stops]
    for c in range(3):
        out[:, c] = np.interp(ys, pos, [col[c] for _, col in stops])
    return np.broadcast_to(out[:, None, :], (h, w, 3)).copy()


def hexc(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def radial(h, w, cx, cy, r):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / r


def to_img(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def blur_np(arr, r):
    return np_rgba(to_img(arr).filter(ImageFilter.GaussianBlur(r)))


# --------------------------------------------------------- backgrounds

BW, BH = 1242, 2208           # 1.15x canvases so the camera can move
OX, OY = (BW - W) // 2, (BH - H) // 2


class Cam:
    def __init__(self, z=1.0, cx=0.0, cy=0.0):
        self.z, self.cx, self.cy = z, cx, cy

    def view(self, img, par=1.0):
        bw, bh = img.size
        cx = bw / 2 + self.cx * par
        cy = bh / 2 + self.cy * par
        hw, hh = W / 2 / self.z, H / 2 / self.z
        return np_rgba(img.transform((W, H), Image.EXTENT, (cx - hw, cy - hh, cx + hw, cy + hh),
                                     Image.BILINEAR))

    def pt(self, x, y, par=1.0):
        return ((x - W / 2 - self.cx * par) * self.z + W / 2,
                (y - H / 2 - self.cy * par) * self.z + H / 2)


def build_bedroom():
    bg = vgrad(BH, BW, [(0, hexc("0c0a2a")), (0.45, hexc("24195a")), (1, hexc("3d2468"))])
    # window glass
    wx0, wx1, wtop, wbot = 241, 1001, 220 + OY - 20, 1300 + OY
    acx, acy, ar = 621, 600 + OY - 20, 380
    ys, xs = np.mgrid[0:BH, 0:BW].astype(np.float32)
    inside = ((xs >= wx0) & (xs <= wx1) & (ys >= acy) & (ys <= wbot)) | \
        (((xs - acx) ** 2 + (ys - acy) ** 2) <= ar ** 2) & (ys < acy)
    glass = vgrad(BH, BW, [(0, hexc("1b1f55")), (0.4, hexc("2e3480")), (0.7, hexc("4b3f96")), (1, hexc("4b3f96"))])
    bg = np.where(inside[..., None], glass, bg)
    rng = np.random.default_rng(3)
    for _ in range(140):
        x, y = rng.uniform(wx0, wx1), rng.uniform(acy - ar, wbot - 150)
        if inside[int(y), int(x)]:
            dot(bg, x, y, rng.uniform(4, 10), PEARL, rng.uniform(0.3, 0.9))
    # moon
    mx, my, mr = 621, 640 + OY, 205
    d = radial(BH, BW, mx, my, mr)
    halo = np.exp(-np.maximum(d - 1, 0) * 1.6) * (d > 1)
    bg += halo[..., None] * MOON * 0.55 * inside[..., None]
    bg += np.exp(-np.maximum(d - 1, 0) * 0.5)[..., None] * (d > 1)[..., None] * MOON * 0.18
    disc = np.clip((1 - d) * mr / 2.5, 0, 1)
    moon_col = vgrad(BH, BW, [(0, hexc("fff6e8")), (1, hexc("f1dcff"))])
    for cx_, cy_, cr in [(-60, -40, 50), (50, 60, 38), (70, -70, 26), (-30, 90, 30)]:
        cd = radial(BH, BW, mx + cx_, my + cy_, cr)
        moon_col = moon_col * (1 - 0.07 * np.exp(-cd ** 2 * 2)[..., None])
    bg = bg * (1 - disc[..., None]) + moon_col * disc[..., None]
    # window frame
    im = to_img(bg)
    d2 = ImageDraw.Draw(im)
    fc = (52, 36, 92)
    d2.arc([acx - ar, acy - ar, acx + ar, acy + ar], 180, 360, fill=fc, width=30)
    d2.line([wx0, acy, wx0, wbot], fill=fc, width=30)
    d2.line([wx1, acy, wx1, wbot], fill=fc, width=30)
    d2.line([acx, acy - ar, acx, wbot], fill=fc, width=16)
    d2.line([wx0, 900 + OY, wx1, 900 + OY], fill=fc, width=16)
    d2.rectangle([wx0 - 40, wbot - 10, wx1 + 40, wbot + 30], fill=(70, 50, 118))
    bg = np_rgba(im)
    # sheer curtains
    for x0, x1 in [(90, 330), (912, 1152)]:
        xx = np.arange(BW, dtype=np.float32)
        fold = 0.55 + 0.45 * np.sin((xx - x0) / 18.0)
        m = ((xx >= x0) & (xx <= x1)).astype(np.float32) * fold
        yy = np.arange(BH, dtype=np.float32)
        mv = ((yy > 160) & (yy < 1480 + OY)).astype(np.float32)
        a = (mv[:, None] * m[None, :] * 0.32)[..., None]
        bg = bg * (1 - a) + hexc("f3a6c8") * a
    # headboard + bed
    im = to_img(bg)
    d2 = ImageDraw.Draw(im)
    d2.rounded_rectangle([140, 1250 + OY, BW - 140, 1560 + OY], radius=70, fill=(186, 152, 226))
    for r in range(2):
        for c in range(7):
            x = 260 + c * 120
            y = 1330 + OY + r * 110
            d2.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(160, 124, 205))
    d2.rounded_rectangle([200, 1440 + OY, 600, 1580 + OY], radius=60, fill=(253, 231, 240))
    d2.rounded_rectangle([640, 1440 + OY, 1040, 1580 + OY], radius=60, fill=(253, 231, 240))
    d2.rounded_rectangle([60, 1540 + OY, BW - 60, BH + 60], radius=90, fill=(247, 184, 207))
    bg = np_rgba(im)
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    folds = (0.92 + 0.08 * np.sin(xx / 70 + yy / 140) * np.sin(yy / 90)) * (yy > 1560 + OY)
    bg = np.where((yy > 1560 + OY)[..., None], bg * folds[..., None], bg)
    # nightstand + clock
    im = to_img(bg)
    d2 = ImageDraw.Draw(im)
    d2.rounded_rectangle([OX + 110, 1360 + OY, OX + 400, 1760 + OY], radius=24, fill=(122, 96, 176))
    d2.rounded_rectangle([OX + 110, 1360 + OY, OX + 400, 1392 + OY], radius=14, fill=(160, 134, 214))
    d2.rounded_rectangle([OX + 140, 1250 + OY, OX + 370, 1360 + OY], radius=22, fill=(26, 18, 46),
                         outline=(255, 160, 205), width=4)
    bg = np_rgba(im).astype(np.float32)
    clock = text_sprite("12:00 AM", POPPINS_B, 50, top=(255, 150, 200), glow=8,
                        glow_col=(255, 90, 160), shadow=0)
    place(bg, clock, OX + 255, 1305 + OY)
    bg = blur_np(bg, 1.0)
    return to_img(bg)


def build_universe():
    PW = 2700
    sky = vgrad(BH, PW, [(0, hexc("3a2a80")), (0.28, hexc("7a5cc8")), (0.55, hexc("d9a0d2")),
                         (0.72, hexc("ffd5c4")), (1, hexc("f2bfe0"))])
    xs = np.arange(PW, dtype=np.float32)[None, :]
    ys = np.arange(BH, dtype=np.float32)[:, None]
    for y0, amp, k, ph, col, inten in [(520, 90, 1 / 380, 0.0, hexc("ffd88a"), 0.33),
                                       (690, 70, 1 / 300, 1.7, hexc("ff9ccf"), 0.35),
                                       (380, 60, 1 / 450, 3.1, hexc("9fd8ff"), 0.22)]:
        c = y0 + amp * np.sin(xs * k + ph)
        sky += (np.exp(-((ys - c) / 70) ** 2) * inten)[..., None] * col
    rng = np.random.default_rng(7)
    for _ in range(260):
        dot(sky, rng.uniform(0, PW), rng.uniform(0, 900), rng.uniform(4, 9), PEARL, rng.uniform(0.2, 0.7))
    # holographic rings in the sky
    im = to_img(sky)
    ring = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(ring)
    for cx, cy, rx, ry in [(500, 420, 260, 70), (1500, 300, 340, 90), (2300, 480, 220, 60)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=255, width=5)
    ring = ring.filter(ImageFilter.GaussianBlur(3))
    sky = np_rgba(im) + np_rgba(ring)[..., None] * hexc("ffe6f6") * 0.55
    # clouds near the horizon
    cl = Image.new("L", (PW, BH), 0)
    d = ImageDraw.Draw(cl)
    for _ in range(70):
        x, y = rng.uniform(-100, PW + 100), rng.uniform(1150, 1750)
        rx, ry = rng.uniform(120, 300), rng.uniform(40, 90)
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=int(rng.uniform(90, 170)))
    cl = np_rgba(cl.filter(ImageFilter.GaussianBlur(40)))[..., None]
    sky = sky * (1 - cl * 0.6) + PEARL * cl * 0.6
    far = to_img(sky)

    # mid layer: floating pearl platforms with crystal flowers
    mid = Image.new("RGBA", (PW, BH), (0, 0, 0, 0))
    for _ in range(16):
        cx, cy = rng.uniform(0, PW), rng.uniform(1500, 2150)
        rx = rng.uniform(110, 260)
        ry = rx * 0.22
        th = rx * 0.35
        lay = Image.new("RGBA", (PW, BH), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.ellipse([cx - rx * 1.2, cy + th - ry * 0.4, cx + rx * 1.2, cy + th + ry * 1.6], fill=(120, 80, 160, 60))
        dl.rectangle([cx - rx, cy, cx + rx, cy + th], fill=(214, 196, 236, 255))
        dl.ellipse([cx - rx, cy + th - ry, cx + rx, cy + th + ry], fill=(214, 196, 236, 255))
        dl.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(255, 246, 252, 255))
        for _ in range(int(rng.integers(1, 4))):
            fx, fh = cx + rng.uniform(-rx * 0.6, rx * 0.6), rng.uniform(40, 90)
            dl.polygon([(fx, cy - fh), (fx + fh * 0.28, cy - fh * 0.45), (fx, cy - 4),
                        (fx - fh * 0.28, cy - fh * 0.45)], fill=(206, 176, 255, 230))
        mid.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    return far, mid


def build_stage():
    bg = vgrad(BH, BW, [(0, hexc("1d1036")), (0.45, hexc("3e2470")), (0.66, hexc("5b3a95")),
                        (0.70, hexc("8a6cc8")), (1, hexc("2e1a52"))])
    d = radial(BH, BW, BW / 2, 980 + OY, 700)
    bg += np.exp(-d ** 2 * 1.4)[..., None] * hexc("8d62d6") * 0.45
    # spotlight cone
    cone = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(cone).polygon([(BW / 2 - 60, 0), (BW / 2 + 60, 0), (BW / 2 + 470, 1470 + OY),
                                  (BW / 2 - 470, 1470 + OY)], fill=120)
    cone = np_rgba(cone.filter(ImageFilter.GaussianBlur(50)))
    fade = np.linspace(1.0, 0.45, BH)[:, None]
    bg += (cone * fade)[..., None] * hexc("ffdf9e") * 0.55
    ys, xs = np.mgrid[0:BH, 0:BW].astype(np.float32)
    ell = np.sqrt(((xs - BW / 2) / 560) ** 2 + ((ys - 1450 - OY) / 120) ** 2)
    bg += np.exp(-ell ** 2 * 1.5)[..., None] * hexc("ffd9a0") * 0.35
    rng = np.random.default_rng(11)
    for _ in range(40):
        dot(bg, rng.uniform(0, BW), rng.uniform(0, 1300 + OY), rng.uniform(30, 90),
            hexc("c7a6ff"), rng.uniform(0.05, 0.18))
    return to_img(bg)


def build_pedestal(w=540):
    ss = 2
    W2, H2 = (w + 80) * ss, 260 * ss
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W2 / 2
    rx, ry = w / 2 * ss, 46 * ss
    top, bot = 60 * ss, 170 * ss
    rxb = rx * 0.86
    d.polygon([(cx - rx, top), (cx + rx, top), (cx + rxb, bot), (cx - rxb, bot)], fill=(225, 210, 255, 70))
    d.ellipse([cx - rxb, bot - ry * 0.86, cx + rxb, bot + ry * 0.86], fill=(225, 210, 255, 70),
              outline=(224, 186, 110, 255), width=5 * ss)
    d.ellipse([cx - rx, top - ry, cx + rx, top + ry], fill=(240, 230, 255, 120),
              outline=(246, 214, 140, 255), width=6 * ss)
    d.ellipse([cx - rx * 0.8, top - ry * 0.7, cx + rx * 0.8, top + ry * 0.7], outline=(255, 255, 255, 90),
              width=2 * ss)
    hl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dh = ImageDraw.Draw(hl)
    dh.polygon([(cx - rx * 0.75, top + 10 * ss), (cx - rx * 0.62, top + 10 * ss), (cx - rxb * 0.55, bot - 10 * ss),
                (cx - rxb * 0.68, bot - 10 * ss)], fill=(255, 255, 255, 150))
    dh.polygon([(cx + rx * 0.5, top + 10 * ss), (cx + rx * 0.56, top + 10 * ss), (cx + rxb * 0.5, bot - 10 * ss),
                (cx + rxb * 0.44, bot - 10 * ss)], fill=(255, 255, 255, 90))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(4 * ss)))
    return im.resize((W2 // ss, H2 // ss), Image.LANCZOS), 60  # sprite, y of the top surface


def build_boutique():
    bg = vgrad(BH, BW, [(0, hexc("f4c3d6")), (0.6, hexc("f9d9e4")), (0.7, hexc("fbe6ee")), (1, hexc("f7e9ef"))])
    im = to_img(bg)
    d = ImageDraw.Draw(im)
    floor_y = 1430 + OY
    for i, cx in enumerate([OX + 120, OX + 540, OX + 960]):
        aw, top = 300, 380 + OY
        d.rounded_rectangle([cx - aw / 2 - 18, top - 18, cx + aw / 2 + 18, floor_y], radius=aw / 2 + 18,
                            fill=(238, 176, 199))
        d.rounded_rectangle([cx - aw / 2, top, cx + aw / 2, floor_y], radius=aw / 2, fill=(253, 236, 242))
        for s in range(3):
            y = top + 330 + s * 230
            d.rectangle([cx - aw / 2 + 20, y, cx + aw / 2 - 20, y + 10], fill=(224, 190, 120))
            rng = np.random.default_rng(i * 10 + s)
            x = cx - aw / 2 + 40
            while x < cx + aw / 2 - 70:
                bw_, bh_ = rng.uniform(34, 60), rng.uniform(50, 120)
                col = [(255, 210, 225), (214, 190, 250), (255, 238, 200), (255, 255, 255)][int(rng.integers(4))]
                d.rounded_rectangle([x, y - bh_, x + bw_, y], radius=8, fill=col)
                x += bw_ + rng.uniform(10, 22)
    d.rectangle([0, floor_y, BW, BH], fill=(250, 240, 244))
    d.line([0, floor_y, BW, floor_y], fill=(224, 190, 120), width=6)
    bg = np_rgba(im)
    rng = np.random.default_rng(5)
    vein = Image.new("L", (BW, BH), 0)
    dv = ImageDraw.Draw(vein)
    for _ in range(18):
        x, y = rng.uniform(0, BW), rng.uniform(floor_y + 20, BH)
        pts = [(x + i * 30, y + 25 * math.sin(i * 0.7 + x)) for i in range(20)]
        dv.line(pts, fill=90, width=2)
    vein = np_rgba(vein.filter(ImageFilter.GaussianBlur(2)))[..., None]
    bg = bg * (1 - vein * 0.25) + hexc("d8c4dc") * vein * 0.25
    beams = Image.new("L", (BW, BH), 0)
    db = ImageDraw.Draw(beams)
    for x in (100, 420, 760):
        db.polygon([(x, 0), (x + 160, 0), (x + 620, BH), (x + 380, BH)], fill=70)
    beams = np_rgba(beams.filter(ImageFilter.GaussianBlur(60)))[..., None]
    bg += beams * hexc("fff3e0") * 0.35
    fg = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    df = ImageDraw.Draw(fg)
    for _ in range(14):
        x, y, r = rng.uniform(-80, 150), rng.uniform(1650 + OY, BH), rng.uniform(30, 60)
        col = [(255, 170, 200, 255), (255, 214, 228, 255), (220, 190, 255, 255)][int(rng.integers(3))]
        df.ellipse([x - r, y - r, x + r, y + r], fill=col)
    fg = fg.filter(ImageFilter.GaussianBlur(10))
    return to_img(bg), fg


def build_endcard():
    bg = vgrad(BH, BW, [(0, hexc("2f2068")), (0.35, hexc("6e4fbf")), (0.7, hexc("c99ae0")), (1, hexc("f4b4d0"))])
    rng = np.random.default_rng(21)
    for _ in range(45):
        dot(bg, rng.uniform(0, BW), rng.uniform(0, BH), rng.uniform(40, 140),
            [PEARL, BLUSH, LAV, GOLD][int(rng.integers(4))], rng.uniform(0.05, 0.2))
    ys, xs = np.mgrid[0:BH, 0:BW].astype(np.float32)
    ell = np.sqrt(((xs - BW / 2) / 520) ** 2 + ((ys - 1350 - OY) / 110) ** 2)
    bg += np.exp(-ell ** 2 * 1.5)[..., None] * hexc("ffe0b0") * 0.3
    return to_img(bg)


def build_bag(w=280):
    ss = 2
    hgt = int(w * 1.05)
    Wc, Hc = (w + 120) * ss, (hgt + 200) * ss
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = Wc / 2
    top = 170 * ss
    tw, bw_ = w * 0.92 * ss, w * ss
    # handles
    for off in (-0.22, 0.22):
        hx = cx + off * tw
        d.arc([hx - 46 * ss, top - 120 * ss, hx + 46 * ss, top + 40 * ss], 180, 360, fill=(250, 244, 230), width=9 * ss)
    body = [(cx - tw / 2, top), (cx + tw / 2, top), (cx + bw_ / 2, top + hgt * ss), (cx - bw_ / 2, top + hgt * ss)]
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(body, fill=255)
    grad = np.linspace(0, 1, Hc)[:, None, None]
    g = hexc("ffe36e") * 255 * (1 - grad) + hexc("f4ae1c") * 255 * grad
    fill = Image.fromarray(np.broadcast_to(g, (Hc, Wc, 3)).astype(np.uint8)).convert("RGBA")
    fill.putalpha(mask)
    im.alpha_composite(fill)
    d = ImageDraw.Draw(im)
    d.polygon([(cx + tw / 2 - 40 * ss, top), (cx + tw / 2, top), (cx + bw_ / 2, top + hgt * ss),
               (cx + bw_ / 2 - 46 * ss, top + hgt * ss)], fill=(226, 158, 20, 150))
    d.rectangle([cx - tw / 2, top, cx + tw / 2, top + 26 * ss], fill=(255, 241, 160, 255))
    for off in (-0.22, 0.22):
        hx = cx + off * tw
        d.ellipse([hx - 7 * ss, top + 6 * ss, hx + 7 * ss, top + 20 * ss], fill=(180, 120, 20))
    gl = Image.new("L", im.size, 0)
    ImageDraw.Draw(gl).polygon([(cx - tw * 0.4, top + 40 * ss), (cx - tw * 0.25, top + 40 * ss),
                                (cx - bw_ * 0.05, top + hgt * ss - 20 * ss), (cx - bw_ * 0.2, top + hgt * ss - 20 * ss)],
                               fill=110)
    gl = ImageChops.multiply(gl.filter(ImageFilter.GaussianBlur(14 * ss)), mask)
    im.alpha_composite(solid(im.size, (255, 255, 255), gl))
    return im.resize((Wc // ss, Hc // ss), Image.LANCZOS)


def build_arrow(length=230):
    ss = 3
    L, T = length * ss, 64 * ss
    pad = 50 * ss
    im = Image.new("L", (L + 2 * pad, T * 3 + 2 * pad), 0)
    cy = im.height / 2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, cy - T / 2, pad + L - T * 1.3, cy + T / 2], radius=T / 2, fill=255)
    d.polygon([(pad + L - T * 1.8, cy - T * 1.35), (pad + L, cy), (pad + L - T * 1.8, cy + T * 1.35)], fill=255)
    im = im.resize((im.width // ss, im.height // ss), Image.LANCZOS)
    h, w = im.height, im.width
    g = np.linspace(0, 1, h)[:, None, None]
    grad = hexc("fff2c4") * 255 * (1 - g) + hexc("d6a03c") * 255 * g
    body = Image.fromarray(np.broadcast_to(grad, (h, w, 3)).astype(np.uint8)).convert("RGBA")
    body.putalpha(im)
    out = solid(im.size, (255, 210, 110), im.filter(ImageFilter.GaussianBlur(14)), 0.95)
    edge = ImageChops.subtract(im, im.filter(ImageFilter.MinFilter(5)))
    out.alpha_composite(body)
    out.alpha_composite(solid(im.size, (255, 255, 255), edge, 0.7))
    return out


# ---------------------------------------------------------- assets

A = {}


def build_assets():
    pouch = Image.open(os.path.join(HERE, "assets", "vtlm_pouch.png")).convert("RGBA")
    A["pouch"] = pouch
    A["bedroom"] = build_bedroom()
    A["far"], A["mid"] = build_universe()
    A["stage"] = build_stage()
    A["pedestal"], A["ped_top"] = build_pedestal()
    A["boutique"], A["bout_fg"] = build_boutique()
    A["endcard"] = build_endcard()
    A["bag"] = build_bag()
    A["arrow"] = build_arrow()
    A["heart"] = heart_sprite(200)
    A["heart_s"] = heart_sprite(60)
    A["heart_t"] = heart_sprite(70, top=(255, 214, 235), bot=(255, 160, 200), glow=False)
    A["food"] = [emoji(c, 170) for c in "🍩🍪🍟🍰"]

    hook = dict(font=BALOO, size=150, top=(255, 255, 255), bot=(255, 228, 242), stroke=9,
                stroke_col=(255, 82, 150), extrude=12, glow=10, glow_col=(255, 110, 180))
    A["hook"] = [text_sprite(w, **hook) for w in ["SELALU", "LAPAR", "TENGAH", "MALAM?🌙"]]
    holo = dict(font=POPPINS_B, size=104, top=(255, 252, 255), bot=(240, 226, 255), glow=12,
                glow_col=(183, 156, 255), shadow=0.45)
    A["t2"] = [text_sprite("MASA UNTUK", **holo), text_sprite("JAGA DIRI! 💗", **holo)]
    A["map_title"] = pill_sprite(text_sprite("RUTIN JAGA DIRI ✨", POPPINS_B, 74, shadow=0.3),
                                 padx=48, pady=22, fill=(255, 255, 255, 60), radius=34)
    lab = dict(font=POPPINS_SB, size=52, shadow=0.25)
    A["labels"] = [pill_sprite(text_sprite(s, **lab)) for s in ["🌸 JAGA BADAN", "💖 JAGA DIRI", "✨ SAYANG DIRI"]]
    A["bubble_in"] = [
        [(emoji("👗", 170), 0, 0), (emoji("👠", 80), 70, 70), (emoji("👚", 86), -78, 46)],
        [(emoji("🛁", 150), 0, 10), (emoji("🕯", 70), -84, -50), (emoji("🍵", 70), 84, -50)],
        [(emoji("🪞", 160), 0, 0), (emoji("💐", 76), 78, 60), (emoji("😊", 60), -70, -64)],
    ]
    A["brand"] = text_sprite("VTLM 💜", PLAYFAIR, 190, top=(255, 243, 200), bot=(206, 156, 64),
                             glow=14, glow_col=(255, 214, 140), glow_k=0.55, shadow=0.5, emoji_scale=0.8)
    A["sub"] = text_sprite("RUTIN PENJAGAAN DIRI ✨", POPPINS_SB, 66, glow=10,
                           glow_col=(190, 160, 255), shadow=0.5)
    shop = dict(font=POPPINS_B, size=62, shadow=0.2)
    A["shop"] = [pill_sprite(text_sprite("JAGA BADAN 🌸", **shop), fill=(120, 60, 150, 170)),
                 pill_sprite(text_sprite("JAGA DIRI 💖", **shop), fill=(120, 60, 150, 170))]
    gold = dict(font=BALOO, size=96, top=(255, 246, 214), bot=(240, 196, 110), stroke=7,
                stroke_col=(150, 70, 140), extrude=7, glow=10, glow_col=(255, 180, 210))
    A["berharga"] = [text_sprite("KERANA DIRI ANDA", **gold), text_sprite("BERHARGA ✨", **gold)]
    cta = dict(font=BALOO, size=118, top=(255, 255, 255), bot=(255, 236, 246), stroke=8,
               stroke_col=(240, 70, 140), extrude=10, glow=0, shadow=0.35)
    A["cta"] = [text_sprite("KENALI VTLM", **cta), text_sprite("DI BEG KUNING 🛍", **cta)]
    A["vignette"] = np.clip(1.0 - 0.28 * radial(H, W, W / 2, H / 2, 1250) ** 2.2, 0.55, 1)[..., None].astype(np.float32)


# ----------------------------------------------------------- particles

def bursts(f, t, events, col, n=26, spread=520, life=0.9, size=26, seed=0):
    for i, (t0, x, y) in enumerate(events):
        dt = t - t0
        if dt < 0 or dt > life:
            continue
        rng = np.random.default_rng(seed + i * 101)
        ang = rng.uniform(0, 2 * math.pi, n)
        spd = rng.uniform(0.3, 1.0, n) * spread
        sz = rng.uniform(0.5, 1.2, n) * size
        k = (1 - dt / life) ** 1.5
        dist = spd * (dt - 0.5 * dt * dt / life)
        for j in range(n):
            px, py = x + math.cos(ang[j]) * dist[j], y + math.sin(ang[j]) * dist[j] + 60 * dt * dt
            (star if j % 3 == 0 else dot)(f, px, py, sz[j] * (1.4 if j % 3 == 0 else 1), col, k)


def ambient(f, t, n, col, seed, ymin=0, ymax=H, vy=40, size=(6, 16), k=0.6, cam=None):
    rng = np.random.default_rng(seed)
    xs, ys = rng.uniform(0, W, n), rng.uniform(ymin, ymax, n)
    ph, sz = rng.uniform(0, 6.28, n), rng.uniform(*size, n)
    for i in range(n):
        y = ymin + (ys[i] - ymin - vy * t * (0.6 + 0.4 * math.sin(ph[i]))) % (ymax - ymin)
        x = xs[i] + 14 * math.sin(t * 0.8 + ph[i])
        tw = 0.55 + 0.45 * math.sin(t * 3.1 + ph[i] * 5)
        dot(f, x, y, sz[i], col, k * tw)


def floating_hearts(f, t, n, seed, ymin=300, ymax=1700, op=0.6):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x0, y0 = rng.uniform(80, W - 80), rng.uniform(ymin, ymax)
        sp, ph, sc = rng.uniform(40, 90), rng.uniform(0, 6.28), rng.uniform(0.45, 1.0)
        y = ymin + (y0 - ymin - sp * t) % (ymax - ymin)
        x = x0 + 30 * math.sin(t * 1.3 + ph)
        place(f, A["heart_t"], x, y, sc, rot=15 * math.sin(t + ph), op=op * (0.6 + 0.4 * math.sin(t * 2 + ph)))


# ------------------------------------------------------------- scenes

WORD_POS = [(540, 380), (540, 545), (540, 720), (540, 885)]
WORD_T = [bt(-1) + i * BEAT for i in range(4)]
FOOD_T = [bt(-1) + i * BEAT + 0.1 for i in range(4)]


def bedroom_cam(t):
    if t < WORD_T[0]:
        return Cam(1.0 + 0.10 * smooth(t / WORD_T[0]), 0, -40 * (1 - smooth(t / WORD_T[0])))
    if t < T_BOOM:
        u = (t - WORD_T[0]) / (T_BOOM - WORD_T[0])
        return Cam(1.10 + 0.03 * u, 30 * math.sin(u * 1.6), 0)
    if t < T_WHIP:
        u = ease_out((t - T_BOOM) / 0.3)
        return Cam(1.13 + 0.32 * u, 30 * math.sin(1.6) * (1 - u), 40 * u)
    u = ease_out((t - T_WHIP) / 0.45)
    return Cam(lerp(1.45, 1.08, u), lerp(0, 0, u), lerp(40, 0, u))


def food_layer(f, t, cam):
    for i, img in enumerate(A["food"]):
        t0 = FOOD_T[i]
        if t < t0:
            continue
        ang = i * math.pi / 2 + 0.55 * (t - t0) + 0.4
        rx, ry = 330, 210
        if t > T_BOOM:
            rx += 900 * ease_in((t - T_BOOM) / 0.6)
            ry += 600 * ease_in((t - T_BOOM) / 0.6)
        wx = 540 + rx * math.cos(ang)
        wy = 1060 + ry * math.sin(ang) + 18 * math.sin(t * 3 + i)
        depth = 0.85 + 0.25 * math.sin(ang)
        sc = elastic((t - t0) / 0.6) * depth
        x, y = cam.pt(wx, wy)
        dot(f, x, y + 30, 210 * sc * cam.z, BLUSH, 0.25)
        place(f, img, x, y, sc * cam.z, rot=12 * math.sin(t * 4 + i))


def hook_text(f, t):
    if t > T_WHIP + 0.15:
        return
    out = ease_in((t - (T_WHIP - 0.12)) / 0.25)
    boom = 0.0
    if t >= T_BOOM:
        boom = 0.22 * math.exp(-(t - T_BOOM) * 9) * math.cos((t - T_BOOM) * 30)
    for i, img in enumerate(A["hook"]):
        t0 = WORD_T[i]
        if t < t0:
            continue
        sc = elastic((t - t0) / 0.5)
        if t >= T_BOOM:
            sc *= 1.0 + boom + 0.06 * ease_out((t - T_BOOM) / 0.2)
        sc *= 1 + 0.6 * out
        x, y = WORD_POS[i]
        y = 630 + (y - 630) * (1 + boom * 0.5)
        place(f, img, x, y - 200 * out, sc, rot=(4 if i % 2 else -4) * (1 - ease_out((t - t0) / 0.4)),
              op=1 - out)
    bursts(f, t, [(WORD_T[i], *WORD_POS[i]) for i in range(4)], hexc("ff7ab8"), n=22, spread=420,
           life=0.7, size=26, seed=5)
    bursts(f, t, [(T_BOOM, 540, 640)], hexc("ffb3d6"), n=70, spread=1300, life=1.0, size=38, seed=77)
    bursts(f, t, [(T_BOOM + 0.05, 540, 640)], GOLD, n=40, spread=900, life=1.0, size=30, seed=78)


def universe_cam(t):
    if t < T_MAP:
        u = smooth((t - T_TOUCH) / (T_MAP - T_TOUCH))
        return Cam(lerp(1.12, 1.03, u), lerp(-640, 380, u), 0)
    u = (t - T_MAP) / (T_RIBBON - T_MAP)
    return Cam(1.03 + 0.03 * u, 380 + 180 * u, -10 * u)


def universe(t):
    cam = universe_cam(t)
    f = cam.view(A["far"], par=0.45)
    midv = cam.view(A["mid"], par=1.0)
    over(f, midv, 0, 0)
    ambient(f, t, 60, PEARL, 9, vy=35, size=(6, 14), k=0.55)
    ambient(f, t, 30, hexc("ffd88a"), 10, vy=20, size=(10, 22), k=0.35)
    return f, cam


def heart_layer(f, t):
    # heart appears in the bedroom, becomes the hub of the mind map
    if t < 4.6:
        return
    s = ease_back((t - 4.6) / 0.45)
    pulse = 1 + 0.25 * math.exp(-max(0, t - T_TOUCH) * 6) * (t >= T_TOUCH)
    bob = 14 * math.sin(t * 2.2)
    if t < T_MAP:
        x, y, sc = 540, 1080 + bob, 1.0
    else:
        u = smooth((t - T_MAP) / 0.8)
        x, y, sc = 540, lerp(1080, 960, u) + bob * (1 - u) + 6 * math.sin(t * 2.2) * u, lerp(1.0, 0.62, u)
    dot(f, x, y, 520 * sc * s, hexc("ff8fc4"), 0.35 + 0.1 * math.sin(t * 4))
    place(f, A["heart"], x, y, s * sc * pulse)
    if t >= T_TOUCH and t < T_TOUCH + 0.8:
        u = (t - T_TOUCH) / 0.8
        r = 80 + 600 * ease_out(u)
        ring_glow(f, x, y, r, hexc("ffc0e0"), (1 - u) * 1.2, width=10)


_RING = {}


def ring_glow(f, cx, cy, r, col, k, width=12):
    ys, xs = np.ogrid[0:H, 0:W]
    y0, y1 = int(max(0, cy - r - 60)), int(min(H, cy + r + 60))
    x0, x1 = int(max(0, cx - r - 60)), int(min(W, cx + r + 60))
    if y1 <= y0 or x1 <= x0:
        return
    yy = np.arange(y0, y1, dtype=np.float32)[:, None]
    xx = np.arange(x0, x1, dtype=np.float32)[None, :]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - r
    f[y0:y1, x0:x1] += (np.exp(-(d / width) ** 2) * k)[..., None] * col


_POLAR = {}


def polar(cx, cy):
    key = (cx, cy)
    if key not in _POLAR:
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        _POLAR[key] = (np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2), np.arctan2(ys - cy, xs - cx))
    return _POLAR[key]


def scene_a(t):
    """0 -> T_RIBBON: bedroom hook, portal, universe, mind map."""
    if t < T_TOUCH + 1.4:
        cam = bedroom_cam(t)
        f = cam.view(A["bedroom"])
        # fairy lights on the headboard
        for i in range(14):
            wx = 190 + i * 54
            wy = 1250 + 26 * math.sin(i * 0.9) + 6
            x, y = cam.pt(wx, wy)
            tw = 0.55 + 0.45 * math.sin(t * 4 + i * 1.7)
            dot(f, x, y, 34 * cam.z, [hexc("ffd88a"), hexc("ff9ccf")][i % 2], 0.9 * tw)
        ambient(f, t, 30, MOON, 3, vy=12, size=(4, 10), k=0.5)
        food_layer(f, t, cam)
        if t >= T_BOOM:
            shake = 16 * math.exp(-(t - T_BOOM) * 12)
            f = np.roll(f, int(shake * math.sin((t - T_BOOM) * 90)), axis=1)
    else:
        f = None
    if t >= T_TOUCH:
        uni, _ = universe(t)
        R = 1600 * ease_in((t - T_TOUCH - 0.05) / 1.3)
        if R >= 1599 or f is None:
            f = uni
        else:
            d, th = polar(540, 1080)
            Rm = R + 45 * np.sin(th * 6 + t * 8) * min(1, R / 200)
            m = np.clip((Rm - d) / 30 + 0.5, 0, 1)[..., None]
            f = f * (1 - m) + uni * m
            ring = np.exp(-((d - Rm) / 26) ** 2)[..., None]
            f += ring * hexc("c9a8ff") * 0.9
            rng = np.random.default_rng(42)
            for i in range(90):
                a0, rr = rng.uniform(0, 6.28), rng.uniform(0.85, 1.12)
                a = a0 + (t - T_TOUCH) * 3.2 * (1.3 - rr)
                x, y = 540 + math.cos(a) * R * rr, 1080 + math.sin(a) * R * rr
                dot(f, x, y, rng.uniform(10, 26), [LAV, BLUSH, GOLD][i % 3], 0.9)
    if T_TOUCH - 0.1 <= t < T_MAP + 0.4:
        # swirl of particles around the heart during the orbit
        rng = np.random.default_rng(8)
        for i in range(120):
            a0, rr, sp = rng.uniform(0, 6.28), rng.uniform(120, 520), rng.uniform(0.6, 1.4)
            a = a0 + (t - T_TOUCH) * sp * 1.6
            y_up = (t - T_TOUCH) * 30 * sp
            k = window(t, T_TOUCH, T_MAP + 0.4, 0.4, 0.5) * 0.8
            dot(f, 540 + math.cos(a) * rr, 1080 + math.sin(a) * rr * 0.45 - y_up, rng.uniform(8, 20),
                [LAV, PEARL, BLUSH][i % 3], k)
    if t >= T_WHIP - 0.05 and t < T_WHIP + 0.4:
        k = math.sin(clamp((t - T_WHIP + 0.05) / 0.45) * math.pi)
        f = sum(np.roll(f, int(s * 40 * k), axis=1) for s in (-2, -1, 0, 1, 2)) / 5
    heart_layer(f, t)
    hook_text(f, t)
    if T_TITLE2 - 0.1 < t < T_MAP + 0.3:
        title2(f, t)
    if t >= T_MAP:
        mind_map(f, t)
    if T_BOOM <= t < T_BOOM + 0.1:
        k = 0.55 * (1 - (t - T_BOOM) / 0.1)
        f = f * (1 - k) + k
    return f


def title2(f, t):
    out = smooth((t - (T_MAP - 0.25)) / 0.35)
    for i, img in enumerate(A["t2"]):
        t0 = T_TITLE2 + i * 0.18
        if t < t0:
            continue
        u = clamp((t - t0) / 0.38)
        cy = [470, 610][i] + 6 * math.sin(t * 3.0) - 260 * ease_in(out)
        arr = np_rgba(img).copy()
        w = arr.shape[1]
        edge = u * (w + 120) - 60
        ramp = np.clip((edge - np.arange(w)) / 60, 0, 1)
        arr[..., 3] *= ramp[None, :]
        x0, y0 = 540 - w / 2, cy - arr.shape[0] / 2
        for dx, col in ((-4, (0.5, 0.95, 1.0)), (4, (1.0, 0.55, 0.85))):
            ghost = arr.copy()
            ghost[..., :3] = col
            ghost[..., 3] *= 0.28
            over(f, ghost, x0 + dx, y0, 1 - out)
        over(f, arr, x0, y0, 1 - out)
        if u < 1:
            dot(f, x0 + edge, cy, 160, PEARL, 0.8)
            add(f, np.dstack([np.ones((arr.shape[0], 8, 3), np.float32), np.ones((arr.shape[0], 8, 1), np.float32)]),
                x0 + edge, y0, 0.6)


BUB = [(300, 650), (780, 650), (540, 1250)]
BUB_R = 168
HUB = (540, 960)
BUB_T = [T_MAP + 0.35, T_MAP + 0.6, T_MAP + 0.85]


def bubble(f, t, i, cx, cy, r, lit, appear):
    if appear <= 0:
        return
    r = r * appear
    if r < 4:
        return
    # glass: blur + brighten what is behind
    size = int(r * 2 + 8)
    mask = Image.new("L", (size * 2, size * 2), 0)
    ImageDraw.Draw(mask).ellipse([8, 8, size * 2 - 8, size * 2 - 8], fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    spr = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    spr.putalpha(mask)
    frost(f, spr, cx, cy, radius=10)
    rr = radial(size, size, size / 2, size / 2, r)
    inner = np.clip(1 - rr, 0, 1)
    tint = np.dstack([np.broadcast_to(lerp(PEARL, LAV, 0.4), (size, size, 3)),
                      (0.10 + 0.32 * np.clip(rr, 0, 1) ** 3) * (rr <= 1)]).astype(np.float32)
    over(f, tint, cx - size / 2, cy - size / 2, 1.0)
    # contents
    sw = math.sin(t * 1.4 + i)
    for img, dx, dy in A["bubble_in"][i]:
        place(f, img, cx + (dx + 10 * sw) * appear, cy + (dy + 5 * math.sin(t * 2 + i + dx)) * appear,
              appear * (1.0 if lit else 0.92), op=0.97 if lit else 0.75)
    # specular highlights + neon outline
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) - size / 2
    ang = np.arctan2(yy, xx)
    hl = np.exp(-(((rr - 0.80) / 0.05) ** 2)) * np.clip(np.cos(ang + 2.36 + 0.3 * sw), 0, 1) ** 2
    add(f, np.dstack([np.ones((size, size, 3), np.float32), (hl * 0.7).astype(np.float32)]), cx - size / 2, cy - size / 2)
    ring_glow(f, cx, cy, r, LAV, 1.1 if lit else 0.55, width=5)
    ring_glow(f, cx, cy, r, hexc("e7d7ff"), 0.6 if lit else 0.3, width=16)
    a = t * 2.4 + i * 2
    for k in range(6):
        dot(f, cx + math.cos(a - k * 0.06) * r, cy + math.sin(a - k * 0.06) * r, 30 - k * 3, PEARL, (0.9 if lit else 0.4) * (1 - k / 6))


def bezier(p0, p1, p2, n=60):
    ts = np.linspace(0, 1, n)[:, None]
    return (1 - ts) ** 2 * np.array(p0) + 2 * (1 - ts) * ts * np.array(p1) + ts ** 2 * np.array(p2)


def mind_map(f, t):
    exit_u = ease_in((t - (T_RIBBON - 0.05)) / 0.3) if t > T_RIBBON - 0.05 else 0
    if exit_u >= 1:
        return
    # trails hub -> bubbles
    trail = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(trail)
    pulse = 1.0 + (0.6 * (0.5 + 0.5 * math.sin((t - 16.2) * 9)) if t > 16.2 else 0)
    curves = []
    for i, (bx, by) in enumerate(BUB):
        u = smooth((t - (BUB_T[i] + 0.25)) / 0.7)
        if u <= 0:
            continue
        ctrl = ((HUB[0] + bx) / 2 + (60 if i == 2 else 0), (HUB[1] + by) / 2 + (-80 if i < 2 else 0))
        pts = bezier(HUB, ctrl, (bx, by))
        pts = pts[: max(2, int(len(pts) * u))]
        d.line([tuple(p) for p in pts], fill=255, width=6)
        curves.append(pts)
    for i, j in ((0, 1), (1, 2), (2, 0)):
        u = smooth((t - (BUB_T[2] + 0.6)) / 0.7)
        if u <= 0:
            continue
        a, b = np.array(BUB[i]), np.array(BUB[j])
        mid = (a + b) / 2 + (np.array([0, -90]) if i == 0 else (np.array([140, 40]) if i == 1 else np.array([-140, 40])))
        pts = bezier(tuple(a), tuple(mid), tuple(b))
        pts = pts[: max(2, int(len(pts) * u))]
        d.line([tuple(p) for p in pts], fill=110, width=4)
    tr = np_rgba(trail)
    tb = np_rgba(trail.filter(ImageFilter.GaussianBlur(10)))
    k = (1 - exit_u)
    f += (tr * 0.7 + tb * 1.6 * pulse)[..., None] * LAV * k
    for c in curves:
        if len(c) > 4:
            q = (t * 0.6) % 1
            p = c[int(q * (len(c) - 1))]
            dot(f, p[0], p[1], 40, PEARL, 0.9 * k)
    # title panel
    tu = ease_back((t - (T_MAP + 0.1)) / 0.45)
    if tu > 0:
        y = 300 - 200 * exit_u
        frost(f, A["map_title"], 540, y, 12)
        place(f, A["map_title"], 540, y, tu, op=(1 - exit_u))
    # bubbles with rack focus
    focus = None
    for i, tf in enumerate(T_FOCUS):
        if t >= tf:
            focus = i
    if t >= 16.3:
        focus = None
    for i, (bx, by) in enumerate(BUB):
        ap = elastic((t - BUB_T[i]) / 0.7) * (1 - exit_u)
        lit = focus is None or focus == i
        r = BUB_R * (1.12 if focus == i else (0.94 if focus is not None else 1.0))
        bubble(f, t, i, bx, by + 8 * math.sin(t * 1.7 + i), r, lit, ap)
        lt = T_FOCUS[i] + 0.12
        if t >= lt:
            lu = ease_back((t - lt) / 0.35)
            ly = by + r * 0.95 + 8
            place(f, A["labels"][i], bx if i != 1 else bx - 10, ly, lu, op=1 - exit_u)
    if t > 16.2:
        bursts(f, t, [(16.25, 540, 960)], LAV, n=40, spread=700, life=0.9, size=24, seed=31)
    bursts(f, t, [(T_FOCUS[i] + 0.12, *BUB[i]) for i in range(3)], PEARL, n=18, spread=380, life=0.6,
           size=20, seed=40)


# --- ribbons (17.0 - 18.4)

RIB = [dict(yc=(i + 0.5) / 5 * H, th=H / 5 * 1.6, amp=60 + 20 * i, k=2 * math.pi / (1500 + 200 * i),
            ph=i * 1.3, tk=2 * math.pi / (1300 + 150 * i), tph=i * 0.9,
            col=[hexc("b79cff"), hexc("f3b4d2"), hexc("cdb6ff"), hexc("f7c6d9"), hexc("c3a4f2")][i]) for i in range(5)]


def ribbons(f, t):
    u = t - T_RIBBON
    cover = ease_out(u / 0.5)
    part = smooth((u - 0.55) / 0.9)
    xs = np.arange(W, dtype=np.float32)[None, :]
    ys = np.arange(H, dtype=np.float32)[:, None]
    for i, r in enumerate(RIB):
        off = (1 - cover) * (-(H * 1.4) - i * 160)
        sign = -1 if r["yc"] < H / 2 else 1
        off += sign * part * (H * 0.8 + abs(r["yc"] - H / 2))
        c = r["yc"] + off + r["amp"] * np.sin(xs * r["k"] + r["ph"] + u * 3)
        tw = np.cos(xs * r["tk"] + r["tph"] + u * 2.5)
        half = r["th"] / 2 * (0.6 + 0.4 * np.abs(tw))
        y0, y1 = int(max(0, (c - half).min() - 4)), int(min(H, (c + half).max() + 4))
        if y1 <= y0:
            continue
        yy = ys[y0:y1]
        dist = np.abs(yy - c) / half
        m = np.clip((1 - dist) * half / 1.5, 0, 1)
        across = (yy - c) / half  # -1 (top edge) .. 1 (bottom edge)
        shade = 0.82 + 0.18 * tw - 0.10 * across * tw + \
            0.45 * np.exp(-((across + 0.35 * tw) / 0.18) ** 2) * (0.5 + 0.5 * tw)
        col = r["col"][None, None, :] * shade[..., None]
        reg = f[y0:y1]
        reg[:] = reg * (1 - m[..., None]) + col * m[..., None]
    rng = np.random.default_rng(12)
    for i in range(40):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        star(f, x, y - part * 300 * (1 if y < H / 2 else -1), rng.uniform(20, 46), GOLD,
             0.8 * window(t, T_RIBBON + 0.1, T_RIBBON + 1.3, 0.2, 0.4))


def pouch_on(f, t, cam, cx, cy_bottom, width, appear, sweep_t=None, float_amp=6):
    pw = width * cam.z
    ph = pw * A["pouch"].height / A["pouch"].width
    x, yb = cam.pt(cx, cy_bottom)
    yb += float_amp * math.sin(t * 1.8)
    sc_in = lerp(0.9, 1.0, ease_out(appear))
    img = A["pouch"].resize((int(pw * sc_in), int(ph * sc_in)), Image.LANCZOS)
    y = yb - img.height / 2
    if appear < 1:
        dot(f, x, y, img.width * 2.2, PEARL, 0.6 * math.sin(appear * math.pi))
    dot(f, x, y, img.width * 1.9, hexc("d9b8ff"), 0.22 * appear)
    arr = np_rgba(img)
    over(f, arr, x - img.width / 2, y - img.height / 2, ease_out(appear))
    if sweep_t is not None and 0 <= sweep_t <= 1:
        h_, w_ = arr.shape[:2]
        yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
        pos = lerp(-0.4, 1.4, sweep_t) * (w_ + h_)
        band = np.exp(-(((xx + yy * 0.7) - pos) / (w_ * 0.12)) ** 2) * arr[..., 3]
        add(f, np.dstack([np.ones((h_, w_, 3), np.float32), band * 0.45]), x - w_ / 2, y - h_ / 2)
    return x, y, img.width, img.height


def scene_stage(t):
    u = (t - (T_RIBBON + 0.5)) / (T_SHOP - T_RIBBON - 0.5)
    cam = Cam(1.0 + 0.08 * smooth(u), lerp(30, -30, smooth(u)), 20 * smooth(u))
    f = cam.view(A["stage"])
    ap = clamp((t - T_POUCH) / 0.45)
    # particles behind
    rng = np.random.default_rng(3)
    orbit = []
    for i in range(46):
        a = rng.uniform(0, 6.28) + t * rng.uniform(0.4, 0.9)
        rx, ry = rng.uniform(300, 430), rng.uniform(60, 110)
        orbit.append((math.cos(a) * rx, math.sin(a) * ry - rng.uniform(100, 520), math.sin(a), rng.uniform(10, 24)))
    for ox, oy, z, s in orbit:
        if z < 0:
            x, y = cam.pt(540 + ox, 1040 + oy)
            dot(f, x, y, s * cam.z, LAV, 0.5)
    ped = A["pedestal"]
    px, py = cam.pt(540, 1400)
    bob = 6 * math.sin(t * 1.8)
    gx, gy = cam.pt(540, 1500)
    dot(f, gx, gy, 520 * cam.z, hexc("ffd9a0"), 0.25)
    place(f, ped, px, py + bob, cam.z)
    top_y = 1400 - ped.height / 2 + A["ped_top"]
    if ap > 0:
        sweep = (t - 19.5) / 0.6
        pouch_on(f, t, cam, 540, top_y + 4, 470, ap, sweep_t=sweep, float_amp=6)
        # floor reflection
        rimg = A["pouch"].transpose(Image.FLIP_TOP_BOTTOM).resize((int(470 * cam.z), int(470 * cam.z * 830 / 600)))
        ra = np_rgba(rimg)
        ra[..., 3] *= np.linspace(0.22, 0, ra.shape[0])[:, None] * ap
        rx, ry = cam.pt(540, 1530)
        over(f, ra, rx - ra.shape[1] / 2, ry, 1.0)
    for ox, oy, z, s in orbit:
        if z >= 0:
            x, y = cam.pt(540 + ox, 1040 + oy)
            dot(f, x, y, s * cam.z * 1.3, PEARL if s > 18 else LAV, 0.8)
    floating_hearts(f, t, 9, 55, ymin=200, ymax=1500, op=0.45)
    ambient(f, t, 30, GOLD, 15, ymin=0, ymax=1400, vy=25, size=(5, 12), k=0.6)
    # text
    if t >= T_BRAND:
        bu = clamp((t - T_BRAND) / 0.5)
        place(f, A["brand"], 540, 300, lerp(1.25, 1.0, ease_out(bu)), op=ease_out(bu))
        bursts(f, t, [(T_BRAND, 540, 300)], GOLD, n=30, spread=600, life=0.8, size=26, seed=61)
    if t >= T_SUB:
        su = ease_out((t - T_SUB) / 0.45)
        place(f, A["sub"], 540, 470 + 30 * (1 - su), 1.0, op=su)
    return f


def scene_shop(t):
    u = (t - T_SHOP) / (T_END - T_SHOP)
    cam = Cam(1.04, lerp(-60, 60, u), 0)
    f = cam.view(A["boutique"], par=0.6)
    # display stand + pouch
    stand_x, stand_y = 400, 1390
    x, y = cam.pt(stand_x, stand_y + 40)
    place(f, A["pedestal"], x, y, 0.8 * cam.z)
    pouch_on(f, t, cam, stand_x, stand_y + 40 - A["pedestal"].height * 0.8 / 2 + A["ped_top"] * 0.8 + 4,
             400, clamp((t - T_SHOP - 0.1) / 0.35), sweep_t=(t - 24.4) / 0.6, float_amp=4)
    # yellow bag, gently swinging
    bx, by = cam.pt(800, 1200, par=1.1)
    sw = 4 * math.sin(t * 2.6)
    place(f, A["bag"], bx, by, 1.0, rot=sw)
    rng = np.random.default_rng(91)
    for i in range(10):
        a = rng.uniform(0, 6.28)
        rr = rng.uniform(150, 230)
        tw = 0.5 + 0.5 * math.sin(t * 5 + i * 1.9)
        star(f, bx + math.cos(a) * rr, by + math.sin(a) * rr * 1.1, rng.uniform(24, 46), hexc("fff0a8"), tw)
    fg = cam.view(A["bout_fg"], par=1.6)
    over(f, fg, 0, 0)
    ambient(f, t, 20, PEARL, 23, vy=20, size=(6, 14), k=0.5)
    # text
    for i, img in enumerate(A["shop"]):
        t0 = T_SHOP + 0.3 + i * 2 * BEAT
        if t >= t0:
            place(f, img, 540, 270 + i * 135, ease_back((t - t0) / 0.35))
    for i, img in enumerate(A["berharga"]):
        t0 = bt(11) + i * 0.15
        if t >= t0:
            place(f, img, 540, 560 + i * 115, elastic((t - t0) / 0.6))
    bursts(f, t, [(bt(11), 540, 600)], GOLD, n=30, spread=600, life=0.8, size=26, seed=71)
    return f


def scene_end(t):
    u = (t - T_END) / (DUR - T_END)
    cam = Cam(1.0 + 0.02 * u, 0, 0)
    f = cam.view(A["endcard"])
    floating_hearts(f, t, 10, 81, ymin=150, ymax=1650, op=0.5)
    ambient(f, t, 40, GOLD, 31, vy=25, size=(5, 14), k=0.6)
    # bag behind
    bx, by = cam.pt(800, 1240)
    place(f, A["bag"], bx, by, 0.8, rot=6 + 2 * math.sin(t * 2))
    ped = A["pedestal"]
    px, py = cam.pt(540, 1420)
    place(f, ped, px, py, cam.z * 0.95)
    top_y = 1420 - ped.height * 0.95 / 2 + A["ped_top"] * 0.95
    pouch_on(f, t, cam, 540, top_y + 4, 430, 1.0, sweep_t=(t - 28.6) / 0.6, float_amp=5)
    # CTA
    cu = ease_back((t - (T_END + 0.1)) / 0.45)
    if cu > 0:
        pw, ph = 980, 300
        pill = Image.new("RGBA", (pw * 2, ph * 2), (0, 0, 0, 0))
        ImageDraw.Draw(pill).rounded_rectangle([6, 6, pw * 2 - 6, ph * 2 - 6], radius=120,
                                               fill=(255, 150, 196, 215), outline=(255, 226, 160, 255), width=10)
        pill = pill.resize((pw, ph), Image.LANCZOS)
        place(f, pill, 540, 470, cu)
        place(f, A["cta"][0], 540, 405, cu)
        place(f, A["cta"][1], 540, 545, cu)
        bursts(f, t, [(T_END + 0.1, 540, 470)], hexc("ffc6e0"), n=40, spread=800, life=0.9, size=28, seed=99)
    au = clamp((t - (T_END + 4 * BEAT)) / 0.3)
    if au > 0:
        pulse = 1 + 0.1 * (0.5 + 0.5 * math.sin((t - T_END) * 2 * math.pi / 0.6))
        shift = 14 * (0.5 + 0.5 * math.sin((t - T_END) * 2 * math.pi / 0.6))
        ang = math.radians(225)
        ax, ay = 230 + math.cos(ang) * shift, 1520 - math.sin(ang) * shift
        dot(f, ax, ay, 360, hexc("ffd27a"), 0.3 * pulse)
        place(f, A["arrow"], ax, ay, ease_back(au) * pulse, rot=225)
    return f


# ----------------------------------------------------------- frame

def grade(f, t):
    f = np.clip(f, 0, 4)
    small = to_img(np.clip(f - 0.8, 0, 1) * 2.5).resize((W // 4, H // 4), Image.BILINEAR)
    bloom = np_rgba(small.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR))
    f = f + bloom * 0.3
    f = f / (1 + np.maximum(f - 1, 0) * 0.6)      # soft roll-off of highlights
    f = f * A["vignette"]
    f = f * 0.96 + 0.025 * LAV * (1 - f)            # lavender lift in the shadows
    rng = np.random.default_rng(int(t * 1000))
    f += rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
    return np.clip(f, 0, 1)


def render(t):
    if t < T_RIBBON + 0.55:
        f = scene_a(t)
    elif t < T_SHOP:
        f = scene_stage(t)
    elif t < T_END:
        f = scene_shop(t)
    else:
        f = scene_end(t)
    if T_RIBBON <= t < T_RIBBON + 1.5:
        ribbons(f, t)
    # flash into the shop, zoom-through into the end card
    if T_SHOP - 0.12 <= t < T_SHOP:
        f = f * 0.5 + 0.5
    if T_SHOP <= t < T_SHOP + 0.3:
        k = 1 - (t - T_SHOP) / 0.3
        f = f * (1 - 0.6 * k) + 0.6 * k
    if T_END - 0.2 <= t < T_END:
        k = (t - (T_END - 0.2)) / 0.2
        img = to_img(f)
        z = 1 + 0.3 * k
        img = img.transform((W, H), Image.EXTENT, (W / 2 - W / 2 / z, H / 2 - H / 2 / z,
                                                   W / 2 + W / 2 / z, H / 2 + H / 2 / z), Image.BILINEAR)
        f = np_rgba(img) * (1 - k) + k * 0.95
    if T_END <= t < T_END + 0.25:
        k = 1 - (t - T_END) / 0.25
        f = f * (1 - k) + 0.95 * k
    return grade(f, t)


def frame_bytes(i):
    return (render(i / FPS) * 255 + 0.5).astype(np.uint8).tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--audio")
    ap.add_argument("--frames")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    a = ap.parse_args()
    build_assets()
    if a.frames:
        base = os.path.splitext(a.out)[0]
        for fr in [int(x) for x in a.frames.split(",")]:
            to_img(render(fr / FPS)).save(f"{base}_{fr:04d}.png")
        return
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if a.audio:
        cmd += ["-i", a.audio, "-c:a", "aac", "-b:a", "256k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-movflags", "+faststart", a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(a.jobs) as pool:
        for i, b in enumerate(pool.imap(frame_bytes, range(N_FRAMES), chunksize=2)):
            p.stdin.write(b)
            if i % 60 == 0:
                print(f"frame {i}/{N_FRAMES}", file=sys.stderr, flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
