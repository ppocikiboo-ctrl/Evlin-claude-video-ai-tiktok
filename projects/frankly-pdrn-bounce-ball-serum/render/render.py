#!/usr/bin/env python3
"""Render the FRANKLY PDRN Bounce Ball Serum TikTok ad (1080x1920, 30 fps).

Every visual is built from the product reference panels in ../reference and
from the hands-on phone video of the real product. The music and sound effects
are synthesised in audio.py, so the output has no third-party audio.

Usage:
  python3 render.py --video /path/to/hands-on.mp4 --out ../output/frankly-pdrn.mp4
  python3 render.py --video ... --stills 1.0,6.0,12.0   # preview single frames
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import audio

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference")
ASSETS = os.path.join(HERE, "assets")
W, H, FPS = 1080, 1920, 30

BROWN = (58, 36, 24)
ORANGE = (240, 104, 32)
ORANGE2 = (255, 150, 70)
GOLD = (222, 178, 110)
PEACH = (255, 210, 186)
WHITE = (255, 255, 255)
CTA_YELLOW = (255, 204, 51)

CLIP_DIR = None  # set in main(); frames of the hands-on video from 5.0 s at 30 fps
CLIP_T0 = 5.0


# ---------------------------------------------------------------- math helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    return clamp((t - a) / (b - a))


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in(x):
    return x ** 3


def ease_io(x):
    return 3 * x * x - 2 * x * x * x


def ease_back(x, s=1.7):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def lerp(a, b, x):
    return a + (b - a) * x


# ------------------------------------------------------------- image helpers
def comp(base, im, x, y):
    x, y = int(round(x)), int(round(y))
    bw, bh = base.size
    w, h = im.size
    if x >= bw or y >= bh or x + w <= 0 or y + h <= 0:
        return
    cx0, cy0 = max(0, -x), max(0, -y)
    cx1, cy1 = min(w, bw - x), min(h, bh - y)
    if (cx0, cy0, cx1, cy1) != (0, 0, w, h):
        im = im.crop((cx0, cy0, cx1, cy1))
    base.alpha_composite(im, (x + cx0, y + cy0))


def with_alpha(im, a):
    if a >= 0.999:
        return im
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


def place(base, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.003 or scale <= 0.01:
        return
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    comp(base, with_alpha(im, alpha), cx - im.width / 2, cy - im.height / 2)


def rgba(arr_rgb, alpha):
    a = np.dstack([arr_rgb, alpha[..., None]]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def grid(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    return x / (n - 1) * 2 - 1, y / (n - 1) * 2 - 1


def rounded_mask(w, h, r, feather=0):
    m = Image.new("L", (w, h), 0)
    pad = feather * 2
    ImageDraw.Draw(m).rounded_rectangle((pad, pad, w - 1 - pad, h - 1 - pad), r, fill=255)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return m


def feathered(img, feather=40, radius=80):
    img = img.convert("RGBA")
    img.putalpha(rounded_mask(img.width, img.height, radius, feather))
    return img


def cover(img, w, h, fx=0.5, fy=0.5):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(math.ceil(img.width * s)), int(math.ceil(img.height * s))), Image.LANCZOS)
    x = int((im.width - w) * fx)
    y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def ref(name):
    return Image.open(os.path.join(REF, name)).convert("RGB")


# ------------------------------------------------------------------- sprites
def make_sphere(n=320, base=(255, 112, 34), core=(255, 196, 110), alpha=235):
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    z = np.sqrt(np.clip(1 - r * r, 0, 1))
    L = np.array([-0.45, -0.55, 0.7])
    L /= np.linalg.norm(L)
    diff = np.clip(x * L[0] + y * L[1] + z * L[2], 0, 1)
    base = np.array(base, np.float32)
    core = np.array(core, np.float32)
    sss = np.exp(-((x - 0.15) ** 2 + (y - 0.25) ** 2) * 2.2)[..., None]
    col = base * (0.62 + 0.38 * diff[..., None])
    col = col * (1 - sss * 0.6) + core * sss * 0.6
    spec = np.exp(-(((x + 0.38) / 0.22) ** 2 + ((y + 0.42) / 0.14) ** 2))
    spec2 = np.exp(-(((x - 0.35) / 0.25) ** 2 + ((y - 0.62) / 0.1) ** 2)) * 0.35
    rim = np.clip(r, 0, 1) ** 8 * 0.35
    col = col + (255 - col) * np.clip(spec + spec2 + rim, 0, 1)[..., None]
    a = np.clip((1 - r) * n / 2.5, 0, 1) * (alpha * (0.85 + 0.15 * r ** 3) + 255 * spec * 0.3)
    return rgba(col, np.clip(a, 0, 255))


def make_droplet(n=320):
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    col = np.zeros((n, n, 3), np.float32)
    col[:] = (236, 244, 252)
    dark = np.clip((x + y) * 0.5, 0, 1) * (r ** 4)
    col -= dark[..., None] * np.array([70, 55, 40])
    edge = 0.10 + 0.55 * r ** 7
    spec = np.exp(-(((x + 0.35) / 0.2) ** 2 + ((y + 0.4) / 0.13) ** 2))
    caustic = np.exp(-(((x - 0.15) / 0.45) ** 2 + ((y - 0.62) / 0.12) ** 2)) * 0.55
    a = (edge + spec + caustic) * np.clip((1 - r) * n / 2.5, 0, 1)
    col = col + (255 - col) * np.clip(spec + caustic, 0, 1)[..., None]
    return rgba(col, np.clip(a, 0, 1) * 255)


def make_bubble(n=200):
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    ring = np.exp(-(((r - 0.9) / 0.06) ** 2)) * 0.75
    spec = np.exp(-(((x + 0.4) / 0.18) ** 2 + ((y + 0.4) / 0.1) ** 2))
    a = np.clip(ring + spec + 0.06 * (r < 0.9), 0, 1)
    col = np.full((n, n, 3), 255, np.float32)
    col[..., 2] = 245
    return rgba(col, a * 255)


def make_soft(n, color, power=1.0, peak=1.0):
    x, y = grid(n)
    r2 = x * x + y * y
    a = np.exp(-r2 * 3.2) ** power * peak * (r2 < 1)
    col = np.zeros((n, n, 3), np.float32)
    col[:] = color
    return rgba(col, a * 255)


def make_bokeh(n, color, peak=0.45):
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    a = np.clip((1 - r) / 0.12, 0, 1) * (0.7 + 0.3 * r) * peak
    col = np.zeros((n, n, 3), np.float32)
    col[:] = color
    return rgba(col, a * 255)


def make_sparkle(n=160, color=(255, 246, 225)):
    x, y = grid(n)
    ax, ay = np.abs(x), np.abs(y)
    star = np.exp(-ax * 26) * np.exp(-ay * 2.6) + np.exp(-ay * 26) * np.exp(-ax * 2.6)
    glow = np.exp(-(x * x + y * y) * 14) * 0.8
    a = np.clip(star + glow, 0, 1)
    col = np.zeros((n, n, 3), np.float32)
    col[:] = color
    return rgba(col, a * 255)


def make_rays(n=1800, count=16, color=(255, 196, 150), peak=60):
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = n / 2
    for i in range(count):
        a0 = i * 2 * math.pi / count
        w = 0.07 + 0.05 * ((i * 7) % 3)
        pts = [(c, c)] + [(c + n * math.cos(a0 + s), c + n * math.sin(a0 + s)) for s in (-w / 2, w / 2)]
        d.polygon(pts, fill=color + (peak,))
    im = im.filter(ImageFilter.GaussianBlur(18))
    x, y = grid(n)
    fade = np.clip(1 - np.sqrt(x * x + y * y), 0, 1) ** 1.2
    a = np.asarray(im.getchannel("A"), np.float32) * fade
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def make_pedestal(w=780, top_h=150, body_h=190):
    h = top_h + body_h
    arr = np.zeros((h, w, 4), np.float32)
    xs = np.linspace(-1, 1, w)
    shade = 0.80 + 0.2 * np.cos(np.clip(xs + 0.25, -1.5, 1.5) * 1.3)
    body = np.zeros((body_h, w, 3), np.float32)
    body[:] = np.array([244, 232, 222]) * shade[:, None]
    yy = np.linspace(0, 1, body_h)[:, None]
    body = body * (1 - 0.12 * yy[..., None])
    arr[top_h // 2: top_h // 2 + body_h, :, :3] = body
    arr[top_h // 2: top_h // 2 + body_h, :, 3] = 255
    # bottom rounded edge (ellipse)
    ey, ex = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (ex - w / 2) / (w / 2)
    bottom_c = top_h // 2 + body_h
    ny = (ey - bottom_c) / (top_h / 2)
    below = ey > bottom_c
    inside_bottom = nx ** 2 + ny ** 2 <= 1
    arr[below & inside_bottom, :3] = (np.array([244, 232, 222]) * 0.82)
    arr[below & inside_bottom, 3] = 255
    arr[below & ~inside_bottom, 3] = 0
    # top ellipse
    ny2 = (ey - top_h / 2) / (top_h / 2)
    top = nx ** 2 + ny2 ** 2 <= 1
    hl = np.exp(-((nx + 0.2) ** 2 * 2 + (ny2 + 0.2) ** 2 * 3))
    topcol = np.array([250, 244, 238])[None, None, :] * (0.94 + 0.06 * hl[..., None]) + 10 * hl[..., None]
    arr[top, :3] = topcol[top]
    arr[top, 3] = 255
    rim = np.abs(nx ** 2 + ny2 ** 2 - 1) < 0.035
    arr[rim, :3] = (255, 236, 214)
    side = np.abs(np.abs(nx) - 1) < 0.004
    arr[side & (arr[..., 3] > 0), :3] *= 0.95
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    return im.filter(ImageFilter.GaussianBlur(0.8))


def vgrad(top, bottom, glow=None, glow_pos=(0.5, 0.42), glow_r=0.7):
    y = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(top, np.float32) * (1 - y) + np.array(bottom, np.float32) * y
    arr = np.broadcast_to(arr, (H, W, 3)).copy()
    if glow:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx / W - glow_pos[0]) ** 2 + ((yy / H - glow_pos[1]) * 1.78) ** 2) / glow_r ** 2
        g = np.exp(-d * 2.5)[..., None]
        arr = arr * (1 - g * 0.55) + np.array(glow, np.float32) * g * 0.55
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")


# --------------------------------------------------------------------- text
EMOJI = {"🧡": "1f9e1", "👀": "1f440", "💧": "1f4a7", "✨": "2728", "🌸": "1f338",
         "🧬": "1f9ec", "🛒": "1f6d2", "👋": "1f44b", "⭐": "2b50"}
FONT_FILES = {"xb": "Poppins-ExtraBold.ttf", "b": "Poppins-Bold.ttf", "sb": "Poppins-SemiBold.ttf",
              "m": "Poppins-Medium.ttf", "serif": "PlayfairDisplay-Italic.ttf"}


@lru_cache(None)
def font(kind, size):
    return ImageFont.truetype(os.path.join(ASSETS, "fonts", FONT_FILES[kind]), size)


@lru_cache(None)
def emoji(code, size):
    im = Image.open(os.path.join(ASSETS, "emoji", code + ".png")).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)


def _segments(line):
    segs, buf = [], ""
    for ch in line:
        if ch == "️":
            continue
        if ch in EMOJI:
            if buf:
                segs.append(("t", buf))
                buf = ""
            segs.append(("e", EMOJI[ch]))
        else:
            buf += ch
    if buf:
        segs.append(("t", buf))
    return segs


def _line_width(segs, f, size, track):
    w = 0
    for kind, v in segs:
        if kind == "e":
            w += int(size * 1.08) + int(size * 0.12)
        else:
            w += f.getlength(v) + track * len(v)
    return w


@lru_cache(None)
def text_img(text, size, color=BROWN, kind="xb", track=0, max_w=940, shadow=None, align="center",
             line_h=1.18):
    """Render text with inline emoji. shadow = (dy, blur, (r,g,b,a))."""
    lines = text.split("\n")
    while True:
        f = font(kind, size)
        segl = [_segments(l) for l in lines]
        widths = [_line_width(s, f, size, track) for s in segl]
        if max(widths) <= max_w or size <= 18:
            break
        size = int(size * 0.94)
    pad = int(size * 0.5)
    lh = int(size * line_h)
    cw = int(max(widths)) + pad * 2
    ch = lh * len(lines) + pad * 2
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill = tuple(color) + (255,) if len(color) == 3 else tuple(color)
    for i, (segs, w) in enumerate(zip(segl, widths)):
        x = pad + ((cw - 2 * pad - w) / 2 if align == "center" else 0)
        base = pad + i * lh + size * 0.98
        for kind_, v in segs:
            if kind_ == "e":
                es = int(size * 1.08)
                x += int(size * 0.06)
                im.alpha_composite(emoji(v, es), (int(x), int(base - size * 0.36 - es / 2)))
                x += es + int(size * 0.06)
            elif track:
                for c in v:
                    d.text((x, base), c, font=f, fill=fill, anchor="ls")
                    x += f.getlength(c) + track
            else:
                d.text((x, base), v, font=f, fill=fill, anchor="ls")
                x += f.getlength(v)
    if shadow:
        dy, blur, scol = shadow
        a = im.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
        sh = Image.new("RGBA", im.size, scol[:3] + (0,))
        sh.putalpha(a.point(lambda v: int(v * scol[3] / 255)))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        comp(out, sh, 0, dy)
        out.alpha_composite(im)
        im = out
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


@lru_cache(None)
def pill(text, size, fg=WHITE, bg=ORANGE, bg2=ORANGE2, kind="xb", padx=44, pady=22, max_w=900, border=None):
    t = text_img(text, size, fg, kind, max_w=max_w - 2 * padx)
    w, h = t.width + 2 * padx, t.height + 2 * pady
    sp = 30
    im = Image.new("RGBA", (w + 2 * sp, h + 2 * sp), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((sp, sp + 10, sp + w, sp + h + 10), h // 2, fill=(150, 60, 20, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    g = np.linspace(0, 1, w)[None, :, None]
    grad = np.array(bg, np.float32) * (1 - g) + np.array(bg2, np.float32) * g
    grad = np.broadcast_to(grad, (h, w, 3))
    body = rgba(grad, np.asarray(rounded_mask(w, h, h // 2), np.float32))
    gloss = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).rounded_rectangle((6, 4, w - 6, h // 2), h // 4, fill=(255, 255, 255, 50))
    body.alpha_composite(gloss)
    if border:
        ImageDraw.Draw(body).rounded_rectangle((1, 1, w - 2, h - 2), h // 2, outline=border, width=3)
    im.alpha_composite(body, (sp, sp))
    im.alpha_composite(t, (sp + padx, sp + (h - t.height) // 2))
    return im


@lru_cache(None)
def glass_card(w, h, r=36, fill=(255, 255, 255, 170), border=(255, 220, 196, 255)):
    sp = 30
    im = Image.new("RGBA", (w + 2 * sp, h + 2 * sp), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((sp, sp + 12, sp + w, sp + h + 12), r, fill=(160, 90, 50, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((sp, sp, sp + w, sp + h), r, fill=fill, outline=border, width=3)
    d.rounded_rectangle((sp + 8, sp + 6, sp + w - 8, sp + h * 0.42), r - 6, fill=(255, 255, 255, 45))
    return im


def appear(t, t0, kind="pop", dur=0.45, t_out=None, out_dur=0.3):
    """-> (scale, alpha, dy) for an element that appears at t0 (and leaves at t_out)."""
    p = prog(t, t0, t0 + dur)
    if kind == "pop":
        s, a, dy = 0.3 + 0.7 * ease_back(p), clamp(p * 2.5), 0
    elif kind == "up":
        s, a, dy = 1.0, clamp(p * 1.6), 70 * (1 - ease_out(p))
    else:
        s, a, dy = 1.0, p, 0
    if t_out is not None:
        q = prog(t, t_out, t_out + out_dur)
        a *= 1 - q
        dy -= 40 * ease_in(q)
    return s, a, dy


def draw_text(base, im, cx, cy, t, t0, kind="pop", t_out=None, dur=0.45):
    s, a, dy = appear(t, t0, kind, dur, t_out)
    place(base, im, cx, cy + dy, s, a)
    return a


# ------------------------------------------------------------ shared assets
SPHERE = make_sphere()
SPHERE_GOLD = make_sphere(base=(232, 176, 92), core=(255, 232, 170))
DROP = make_droplet()
BUBBLE = make_bubble()
SPARK = make_sparkle()
GLOW_OR = make_soft(400, (255, 150, 70), peak=0.8)
GLOW_WH = make_soft(400, (255, 248, 236), peak=0.9)
BOKEH_P = make_bokeh(120, (255, 196, 160))
BOKEH_G = make_bokeh(120, (255, 228, 180))
RAYS = make_rays()
PEDESTAL = make_pedestal()
BG_PEARL = vgrad((253, 250, 246), (250, 230, 214), glow=(255, 226, 205), glow_pos=(0.5, 0.45))
BG_CHAMP = vgrad((254, 246, 234), (246, 214, 178), glow=(255, 236, 205), glow_pos=(0.5, 0.38))
BG_EDU = vgrad((250, 247, 245), (243, 230, 222), glow=(255, 236, 222), glow_pos=(0.5, 0.47), glow_r=0.6)

P02 = ref("02-main-product.jpg")
PROD_MAIN = feathered(P02, feather=36, radius=120)
TITLE03 = feathered(ref("03-before-after.jpg").crop((165, 140, 935, 318)), feather=10, radius=30)
MODEL_BIG = None  # built lazily (needs LANCZOS upscale)
BALL05 = ref("05-salmon-pdrn-ball.jpg").crop((550, 257, 1100, 733))
P06 = ref("06-shake-to-activate.jpg")
SHAKE_L = feathered(P06.crop((60, 280, 545, 815)), feather=4, radius=34)
SHAKE_R = feathered(P06.crop((555, 280, 1040, 815)), feather=4, radius=34)
MACRO07 = feathered(ref("07-sensitive-skin.jpg").crop((690, 250, 1100, 560)), feather=30, radius=60)
HOWTO08 = feathered(ref("08-how-to-use.jpg").crop((50, 285, 1065, 810)), feather=26, radius=60)
PACK09 = feathered(ref("09-packaging-versions.jpg").crop((40, 350, 1060, 1099)), feather=34, radius=90)

_sprite_cache = {}


def sized(sprite, px):
    px = max(2, int(px) // 2 * 2)
    key = (id(sprite), px)
    if key not in _sprite_cache:
        _sprite_cache[key] = sprite.resize((px, int(px * sprite.height / sprite.width)), Image.BILINEAR)
    return _sprite_cache[key]


def put(base, sprite, cx, cy, px, alpha=1.0, rot=0):
    im = sized(sprite, px)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    comp(base, with_alpha(im, alpha), cx - im.width / 2, cy - im.height / 2)


def model_big():
    global MODEL_BIG
    if MODEL_BIG is None:
        m = ref("04-why-salmon-pdrn.jpg").crop((600, 330, 1100, 1099))
        m = cover(m, 1350, 2400, fx=0.45, fy=0.4).filter(ImageFilter.UnsharpMask(3, 60, 2))
        arr = np.asarray(m, np.float32)
        arr = arr * np.array([1.03, 1.0, 0.96]) + np.array([4, 2, 0])
        soft = np.asarray(Image.fromarray(arr.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)), np.float32)
        arr = 255 - (255 - arr) * (255 - soft * 0.35) / 255  # gentle bloom (screen)
        MODEL_BIG = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
    return MODEL_BIG


def zoom_view(big, z, fx, fy):
    cw, ch = big.width / z, big.height / z
    x = clamp(fx * big.width - cw / 2, 0, big.width - cw)
    y = clamp(fy * big.height - ch / 2, 0, big.height - ch)
    return big.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


def zoom_frame(im, z, cx, cy):
    if z <= 1.001:
        return im
    cw, ch = W / z, H / z
    x = clamp(cx - cw / 2, 0, W - cw)
    y = clamp(cy - ch / 2, 0, H - ch)
    return im.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


def yrot(img, ang, k=0.22):
    """Fake 3-D rotation about the vertical axis (perspective squeeze)."""
    if abs(ang) < 0.3:
        return img
    w, h = img.size
    a = math.radians(ang)
    c, s = abs(math.cos(a)), math.sin(a)
    nw = max(4, w * c)
    xl, xr = (w - nw) / 2, (w + nw) / 2
    hl = h * (1 - k * s) / (1 + k * abs(s))
    hr = h * (1 + k * s) / (1 + k * abs(s))
    dst = [(xl, (h - hl) / 2), (xr, (h - hr) / 2), (xr, (h + hr) / 2), (xl, (h + hl) / 2)]
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    A, B = [], []
    for (X, Y), (u, v) in zip(dst, src):
        A.append([X, Y, 1, 0, 0, 0, -u * X, -u * Y])
        A.append([0, 0, 0, X, Y, 1, -v * X, -v * Y])
        B += [u, v]
    coef = np.linalg.solve(np.array(A, float), np.array(B, float))
    return img.transform((w, h), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)


def gloss_sweep(img, p, width=0.18):
    """Diagonal light sweep across an RGBA image, p in 0..1."""
    if p <= 0 or p >= 1:
        return img
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx / w + yy / h * 0.45) / 1.45
    band = np.exp(-((u - (p * 1.4 - 0.2)) / width) ** 2) * 0.55
    arr = np.asarray(img, np.float32).copy()
    arr[..., :3] += (255 - arr[..., :3]) * band[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


# ------------------------------------------------------------ particle fields
class Field:
    def __init__(self, seed, n, sprite, size, xr=(0, W), yr=(0, H), vy=(-60, -20), vx=(-10, 10),
                 alpha=(0.4, 0.9), wob=30, twinkle=False):
        rng = np.random.default_rng(seed)
        self.sprite = sprite if isinstance(sprite, list) else [sprite]
        self.p = []
        for _ in range(n):
            self.p.append(dict(
                x=rng.uniform(*xr), y=rng.uniform(*yr), vx=rng.uniform(*vx), vy=rng.uniform(*vy),
                s=rng.uniform(*size), a=rng.uniform(*alpha), ph=rng.uniform(0, 6.28),
                f=rng.uniform(0.6, 1.6), k=int(rng.integers(len(self.sprite)))))
        self.xr, self.yr, self.wob, self.twinkle = xr, yr, wob, twinkle

    def draw(self, base, t, alpha=1.0):
        if alpha <= 0.01:
            return
        x0, x1 = self.xr
        y0, y1 = self.yr
        for q in self.p:
            x = x0 + (q["x"] - x0 + q["vx"] * t + self.wob * math.sin(t * q["f"] + q["ph"])) % (x1 - x0)
            y = y0 + (q["y"] - y0 + q["vy"] * t) % (y1 - y0)
            a = q["a"] * alpha
            s = q["s"]
            if self.twinkle:
                tw = 0.5 + 0.5 * math.sin(t * q["f"] * 4 + q["ph"])
                a *= tw
                s *= 0.6 + 0.4 * tw
            put(base, self.sprite[q["k"]], x, y, s, a)


def burst(base, t, t0, cx, cy, n=9, radius=180, seed=0, dur=0.9, size=70):
    p = prog(t, t0, t0 + dur)
    if p <= 0 or p >= 1:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        ang = i * 2 * math.pi / n + rng.uniform(-0.3, 0.3)
        r = radius * rng.uniform(0.6, 1.2) * ease_out(p)
        s = size * rng.uniform(0.5, 1.1) * math.sin(math.pi * p)
        put(base, SPARK, cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.7, s, 1 - p * 0.5)


def ribbon(base, t, y0, amp, color, phase=0.0, width=10, alpha=150, slope=-0.25):
    layer = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    for i in range(0, 61):
        x = -40 + i * (W // 2 + 80) / 60
        y = (y0 + slope * (x * 2 - W / 2) + amp * math.sin(x * 2 / 210 + t * 1.4 + phase)) / 2
        pts.append((x, y))
    d.line(pts, fill=color + (alpha,), width=width // 2, joint="curve")
    glow = layer.filter(ImageFilter.GaussianBlur(5))
    d2 = ImageDraw.Draw(glow)
    d2.line(pts, fill=(255, 250, 235, min(255, alpha + 60)), width=max(1, width // 6), joint="curve")
    base.alpha_composite(glow.resize((W, H), Image.BILINEAR))


def holo_rings(base, t, cx, cy, rx, ry, color=(255, 190, 140), alpha=1.0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, (sx, w_, sp) in enumerate(((1.0, 3, 0.9), (0.78, 2, -1.3), (1.22, 2, 0.6))):
        a, b = rx * sx, ry * sx
        d.ellipse((cx - a, cy - b, cx + a, cy + b), outline=color + (int(110 * alpha),), width=w_)
        for j in range(3):
            th = t * sp + j * 2.09 + i
            px, py = cx + a * math.cos(th), cy + b * math.sin(th)
            d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(255, 240, 220, int(230 * alpha)))
    base.alpha_composite(layer)


def rays(base, t, cx, cy, alpha=1.0, speed=6.0):
    im = RAYS.rotate(t * speed, Image.BILINEAR)
    place(base, im, cx, cy, 1.0, alpha)


# ---------------------------------------------------------------- footage
def clip_frame(T):
    idx = int(round((T - CLIP_T0) * FPS)) + 1
    idx = max(1, min(idx, len(os.listdir(CLIP_DIR))))
    im = Image.open(os.path.join(CLIP_DIR, f"f{idx:04d}.jpg")).convert("RGB")
    arr = np.asarray(im, np.float32) / 255
    lum = (arr @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    arr = lum + (arr - lum) * 0.62
    arr = arr * np.array([1.06, 1.0, 0.9], np.float32)
    arr = arr * 0.9 + 0.09
    return Image.fromarray((arr.clip(0, 1) * 255).astype(np.uint8))


@lru_cache(None)
def frame_chrome(w, h, r=48, border=10):
    sp = 40
    im = Image.new("RGBA", (w + 2 * sp, h + 2 * sp), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((sp, sp + 16, sp + w, sp + h + 16), r, fill=(140, 70, 40, 85))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    ImageDraw.Draw(im).rounded_rectangle((sp - border, sp - border, sp + w + border, sp + h + border),
                                         r + border, fill=(255, 251, 246, 255))
    return im


def framed_clip(base, T, src_box, w, h, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    im = clip_frame(T).crop(src_box)
    im = cover(im, w, h).convert("RGBA")
    im.putalpha(rounded_mask(w, h, 48))
    chrome = frame_chrome(w, h).copy()
    chrome.alpha_composite(im, (40, 40))
    place(base, chrome, cx, cy, scale, alpha, rot)


# ===================================================================== scenes
F1_BOKEH = Field(1, 12, [BOKEH_P, BOKEH_G], (60, 160), vy=(-40, -15))
F1_SPARK = Field(2, 14, SPARK, (40, 90), vy=(-20, 0), twinkle=True)
F1_DROPS = Field(3, 7, DROP, (40, 90), vy=(-25, -8), alpha=(0.7, 1.0))


def s_hook(t):
    z = 1.05 + 0.05 * t / 4.6 + 0.6 * ease_in(prog(t, 3.9, 4.6))
    base = zoom_view(model_big(), z, 0.55, 0.42)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = np.zeros((H, W), np.float32)
    a[:1050] = np.linspace(0.86, 0, 1050)[:, None]
    over = rgba(np.broadcast_to(np.array([255, 246, 238], np.float32), (H, W, 3)), a * 255)
    base.alpha_composite(over)
    # soft orange light sweep
    p = prog(t, 0.2, 2.4)
    if 0 < p < 1:
        put(base, GLOW_OR, lerp(-300, W + 300, ease_io(p)), 900, 1300, 0.55)
    F1_BOKEH.draw(base, t, 0.8)
    F1_DROPS.draw(base, t)
    # translucent droplet crossing the frame
    p = prog(t, 0.4, 3.4)
    if 0 < p < 1:
        e = ease_io(p)
        put(base, DROP, lerp(-120, W + 120, e), 1250 - 330 * e + 60 * math.sin(e * 6), 170)
    F1_SPARK.draw(base, t)
    draw_text(base, text_img("DAH MASUK 30-AN? 👀", 92, BROWN, "xb", shadow=(4, 10, (255, 255, 255, 230))),
              540, 420, t, 0.15, "pop")
    burst(base, t, 0.2, 540, 420, seed=1, radius=420)
    draw_text(base, text_img("Kulit nampak kusam &\nkurang lembap?", 62, (90, 54, 34), "sb",
                             shadow=(3, 8, (255, 255, 255, 220))), 540, 600, t, 1.4, "up")
    draw_text(base, pill("JOM KENAL PDRN SERUM! 🧡", 60), 540, 1360, t, 2.8, "pop")
    burst(base, t, 2.85, 540, 1360, seed=3, radius=440, n=12)
    return base


F2_BUB = Field(4, 14, BUBBLE, (26, 70), vy=(-90, -40), alpha=(0.6, 1.0))
F2_SPARK = Field(5, 16, SPARK, (30, 80), twinkle=True)
F2_BOKEH = Field(6, 10, [BOKEH_P, BOKEH_G], (80, 180), vy=(-30, -10))


def s_reveal(t):
    base = BG_PEARL.copy()
    rays(base, t, 540, 900, 0.9)
    F2_BOKEH.draw(base, t)
    ribbon(base, t, 760, 90, GOLD, 0.0, 14, 150)
    ribbon(base, t, 1120, 70, (255, 168, 110), 2.0, 10, 120, slope=0.18)
    holo_rings(base, t, 540, 1240, 430, 95, alpha=clamp(t / 0.8))
    put(base, GLOW_OR, 540, 1010, 900, 0.45 + 0.1 * math.sin(t * 3))
    orbit = []
    for i in range(7):
        th = t * 0.7 + i * 2 * math.pi / 7
        depth = math.sin(th)
        orbit.append((depth, 540 + 440 * math.cos(th), 930 + 140 * depth + 25 * math.sin(t * 2 + i),
                      60 + 34 * depth + 8 * (i % 3), SPHERE if i % 3 else SPHERE_GOLD))
    for o in orbit:
        if o[0] < 0:
            put(base, o[4], o[1], o[2], o[3], 0.9)
    pe = ease_out(prog(t, 0, 1.1))
    ang = 75 * (1 - pe) + 14 * math.sin(t * 1.3) * ease_io(prog(t, 0.7, 1.7))
    card = PROD_MAIN.resize((880, 880), Image.BICUBIC)
    card = gloss_sweep(card, prog(t, 1.3, 2.4))
    card = yrot(card, ang)
    place(base, card, 540, 900 + 8 * math.sin(t * 1.6), 0.7 + 0.3 * pe, clamp(t / 0.4))
    for o in orbit:
        if o[0] >= 0:
            put(base, o[4], o[1], o[2], o[3], 0.95)
    F2_BUB.draw(base, t)
    # macro push into the orange PDRN ball, then the label macro
    zp = ease_io(prog(t, 3.3, 4.7))
    base = zoom_frame(base, 1 + 1.9 * zp, 540, lerp(900, 1018, zp))
    if zp > 0:
        put(base, GLOW_OR, 540, 1150, 900, 0.5 * zp)
    mp = prog(t, 4.3, 4.8)
    if mp > 0:
        bg = BG_CHAMP.copy()
        rays(bg, t, 540, 960, 0.9)
        put(bg, GLOW_OR, 560, 1110, 1000, 0.55 + 0.15 * math.sin(t * 5))
        place(bg, MACRO07, 540, 960, 1.95 + 0.12 * prog(t, 4.3, 5.6))
        F2_SPARK.draw(bg, t)
        base = Image.blend(base, bg, ease_io(mp))
    else:
        F2_SPARK.draw(base, t)
    draw_text(base, text_img("FRANKLY PDRN", 104, BROWN, "xb", shadow=(4, 10, (255, 255, 255, 220))),
              540, 255, t, 0.5, "pop", t_out=3.3)
    draw_text(base, text_img("BOUNCE BALL SERUM", 54, ORANGE, "sb", track=6), 540, 360, t, 0.9, "up", t_out=3.3)
    draw_text(base, pill("SALMON DNA 🧡", 62), 540, 1500, t, 1.5, "pop")
    burst(base, t, 0.55, 540, 255, seed=4, radius=480)
    burst(base, t, 4.5, 560, 1110, seed=5, radius=380, n=12, size=90)
    return base


def helix(base, t, cx, y0, y1, amp, alpha=1.0):
    n = 15
    pts = []
    for i in range(n):
        y = y0 + (y1 - y0) * i / (n - 1)
        ph = i * 0.62 + t * 1.8
        for strand, off in ((0, 0.0), (1, math.pi)):
            x = cx + amp * math.sin(ph + off)
            z = math.cos(ph + off)
            pts.append((z, x, y, strand, i))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        a = [p for p in pts if p[4] == i]
        d.line((a[0][1], a[0][2], a[1][1], a[1][2]), fill=(255, 205, 170, int(150 * alpha)), width=5)
    for s in (0, 1):
        line = [(p[1], p[2]) for p in pts if p[3] == s]
        d.line(line, fill=(255, 186, 140, int(120 * alpha)), width=4, joint="curve")
    base.alpha_composite(layer)
    for z, x, y, s, i in sorted(pts):
        spr = SPHERE if s == 0 else SPHERE_GOLD
        put(base, spr, x, y, 34 + 18 * (z + 1), alpha * (0.55 + 0.45 * (z + 1) / 2))


F3_SPARK = Field(7, 18, SPARK, (28, 60), twinkle=True)
F3_BUB = Field(8, 12, [BUBBLE, DROP], (24, 60), vy=(-50, -20))
F3_GLOW = Field(9, 14, SPHERE, (10, 20), xr=(330, 750), yr=(520, 1280), vy=(-80, -40), wob=120, alpha=(0.6, 1))

BRANCHES = [
    ("🧡", "Bahan berasaskan\nDNA salmon", 255, 630),
    ("💧", "Penjagaan\nkelembapan kulit", 825, 630),
    ("✨", "Penampilan kulit\nlebih berseri", 255, 1200),
    ("🌸", "Rutin penjagaan\nkulit harian", 825, 1200),
]


def s_pdrn(t):
    base = BG_EDU.copy()
    rays(base, t, 540, 900, 0.5, speed=4)
    put(base, GLOW_WH, 540, 900, 1100, 0.7)
    panel = glass_card(960, 1220, 50, fill=(255, 255, 255, 80), border=(255, 255, 255, 200))
    place(base, panel, 540, 940, 1.0, clamp(t / 0.4))
    F3_BUB.draw(base, t)
    put(base, GLOW_OR, 540, 900, 700, 0.35)
    mm = prog(t, 1.0, 1.6)
    helix(base, t, 540, 470 + 90 * mm, 1330 - 90 * mm, 115, 1 - 0.45 * mm)
    F3_GLOW.draw(base, t)
    # mind-map branches
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k, (_, _, bx, by) in enumerate(BRANCHES):
        t0 = 1.5 + 0.7 * k
        lp = ease_out(prog(t, t0, t0 + 0.35))
        if lp <= 0:
            continue
        ex = lerp(540, bx + (150 if bx < 540 else -150), lp)
        ey = lerp(900, by + (60 if by < 900 else -60), lp)
        d.line((540, 900, ex, ey), fill=(255, 160, 100, 90), width=14)
        d.line((540, 900, ex, ey), fill=(255, 120, 50, 255), width=4)
        q = (t * 0.8 + k * 0.25) % 1
        d.ellipse((lerp(540, ex, q) - 7, lerp(900, ey, q) - 7, lerp(540, ex, q) + 7, lerp(900, ey, q) + 7),
                  fill=(255, 245, 225, 255))
    base.alpha_composite(layer)
    for k, (em, txt, bx, by) in enumerate(BRANCHES):
        t0 = 1.75 + 0.7 * k
        s, a, dy = appear(t, t0, "pop", 0.4)
        if a <= 0:
            continue
        card = glass_card(400, 170, 34).copy()
        e = emoji(EMOJI[em], 64)
        card.alpha_composite(e, (30 + 26, 30 + 53))
        tx = text_img(txt, 36, BROWN, "sb", align="left", max_w=280, line_h=1.12)
        card.alpha_composite(tx, (30 + 104, 30 + (170 - tx.height) // 2))
        place(base, card, bx, by + dy, s, a)
        burst(base, t, t0, bx, by, n=6, radius=200, seed=10 + k, size=50)
    s, a, _ = appear(t, 0.8, "pop", 0.45)
    place(base, pill("KENALI PDRN 🧬", 60, border=(255, 236, 214, 255)), 540, 900, s, a)
    burst(base, t, 0.85, 540, 900, seed=20, radius=360, n=12)
    place(base, TITLE03, 540, 205, 0.92, clamp(t / 0.5))
    F3_SPARK.draw(base, t)
    draw_text(base, text_img("PDRN di sini ialah bahan penjagaan kulit (kosmetik).", 30, (110, 80, 62), "m"),
              540, 1490, t, 4.4, "fade")
    return base


F4_SPARK_IN = Field(11, 22, SPARK, (18, 46), xr=(250, 830), yr=(380, 960), vy=(-30, 10), twinkle=True, wob=40)
F4_BOKEH = Field(12, 10, [BOKEH_P, BOKEH_G], (80, 180), vy=(-30, -10))
_BALL = None


def ball_img(d=640):
    global _BALL
    if _BALL is None:
        b = cover(BALL05, d, d).convert("RGBA")
        x, y = grid(d)
        r = np.sqrt(x * x + y * y)
        mask = np.clip((1 - r) * d / 4, 0, 1)
        arr = np.asarray(b, np.float32).copy()
        sp = np.asarray(make_sphere(d), np.float32)
        hl = np.clip(np.exp(-(((x + 0.38) / 0.22) ** 2 + ((y + 0.42) / 0.14) ** 2)) + np.clip(r, 0, 1) ** 10 * 0.6, 0, 1)
        arr[..., :3] = arr[..., :3] * (1 - hl[..., None]) + 255 * hl[..., None]
        arr[..., :3] = arr[..., :3] * 0.8 + sp[..., :3] * 0.2
        arr[..., 3] = mask * 255
        _BALL = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    return _BALL


def s_ingredient(t):
    base = BG_CHAMP.copy()
    rays(base, t, 540, 690, 1.0)
    F4_BOKEH.draw(base, t)
    put(base, GLOW_OR, 540, 690, 1000, 0.6 + 0.12 * math.sin(t * 2.4))
    s = (0.75 + 0.25 * ease_back(prog(t, 0, 0.7))) * (1 + 0.025 * math.sin(t * 2.2))
    place(base, ball_img(), 540, 690 + 12 * math.sin(t * 1.5), s, clamp(t / 0.3), rot=3 * math.sin(t * 0.9))
    F4_SPARK_IN.draw(base, t)
    for i in range(5):
        th = t * 0.9 + i * 1.256
        put(base, DROP if i % 2 else SPHERE, 540 + 390 * math.cos(th), 690 + 330 * math.sin(th) * 0.9,
            40 + 12 * math.sin(th), 0.9)
    draw_text(base, text_img("SALMON PDRN", 90, ORANGE, "xb", shadow=(4, 10, (255, 255, 255, 220))),
              540, 215, t, 0.25, "pop")
    draw_text(base, text_img("100,000 ppm*", 84, BROWN, "serif"), 540, 318, t, 0.65, "up")
    burst(base, t, 0.3, 540, 215, seed=30, radius=460)
    draw_text(base, pill("SALMON EGG EXTRACT", 46, bg=(255, 255, 255), bg2=(255, 240, 228), fg=ORANGE,
                         border=(255, 190, 150, 255)), 540, 1080, t, 1.2, "pop")
    draw_text(base, text_img("Untuk rutin penjagaan kulit\nyang lebih lengkap.", 44, BROWN, "sb"),
              540, 1200, t, 2.0, "up")
    for k, (em, label) in enumerate((("💧", "Kelembapan"), ("✨", "Seri kulit"), ("🧡", "Penjagaan\nkulit"))):
        t0 = 2.8 + 0.35 * k
        sc, a, dy = appear(t, t0, "up", 0.45)
        if a <= 0:
            continue
        card = glass_card(290, 150, 30).copy()
        card.alpha_composite(emoji(EMOJI[em], 52), (30 + 18, 30 + 49))
        tx = text_img(label, 34, BROWN, "sb", align="left", max_w=190, line_h=1.1)
        card.alpha_composite(tx, (30 + 82, 30 + (150 - tx.height) // 2))
        place(base, card, 225 + 305 * k, 1355 + dy, sc, a)
    draw_text(base, text_img("*Angka berdasarkan bahan pemasaran jenama.", 26, (120, 88, 66), "m"),
              540, 1475, t, 3.4, "fade")
    return base


F5_SPARK = Field(13, 14, SPARK, (30, 70), twinkle=True)
F5_BOKEH = Field(14, 10, [BOKEH_P, BOKEH_G], (80, 170), vy=(-30, -10))
SHAKE_SRC = (90, 300, 990, 1470)


def s_shake(t):
    base = BG_PEARL.copy()
    rays(base, t, 540, 900, 0.7)
    F5_BOKEH.draw(base, t)
    if t < 3.3:
        a = 1 - prog(t, 3.0, 3.3)
        framed_clip(base, 5.4 + t, SHAKE_SRC, 780, 1010, 540, 930, 0.92 + 0.08 * ease_out(prog(t, 0, 0.4)), a)
        hp = 1 - prog(t, 2.9, 3.2)
        put(base, emoji("1f44b", 150), 880, 520, 150, hp * clamp(t / 0.3), rot=28 * math.sin(t * 2 * math.pi * 3))
        for i in range(3):
            put(base, SPHERE, 200 + 40 * math.sin(t * 7 + i), 1350 - ((t * 260 + i * 140) % 500), 26, 0.8 * a)
    else:
        u = t - 3.3
        cx_l, cx_r, cy = 290, 790, 860
        sh = 1 - prog(u, 1.0, 1.2)
        rot = 7 * math.sin(u * 2 * math.pi * 5) * sh
        place(base, SHAKE_L, cx_l + 12 * math.sin(u * 2 * math.pi * 5) * sh, cy, 0.98, clamp(u / 0.25), rot)
        ap = prog(u, 1.2, 1.6)
        place(base, SHAKE_R, cx_r, cy, 0.85 + 0.13 * ease_back(ap), ap)
        bp = prog(u, 0.8, 1.9)
        if 0 < bp < 1:
            rng = np.random.default_rng(40)
            for i in range(26):
                d0 = rng.uniform(0, 0.35)
                q = clamp((bp - d0) / 0.65)
                if q <= 0 or q >= 1:
                    continue
                e = ease_io(q)
                x = lerp(cx_l, cx_r + rng.uniform(-150, 150), e)
                y = lerp(cy + 90, cy + rng.uniform(-170, 200), e) - 220 * math.sin(math.pi * e) * rng.uniform(0.4, 1)
                put(base, SPHERE, x, y, rng.uniform(12, 30) * (1 - 0.5 * e), 1 - q * 0.3)
        if ap > 0:
            for i in range(8):
                th = u * 2.2 + i * 0.785
                put(base, DROP if i % 2 else SPHERE, cx_r + 260 * math.cos(th), cy + 300 * math.sin(th) * 0.85,
                    26 + 8 * math.sin(th), 0.85 * ap)
        draw_text(base, text_img("Bola PDRN pekat", 36, BROWN, "sb"), cx_l, 1170, u, 0.3, "up")
        draw_text(base, text_img("Partikel mikro", 36, BROWN, "sb"), cx_r, 1170, u, 1.4, "up")
        draw_text(base, text_img("Sebatikan serum\nsebelum digunakan.", 54, BROWN, "xb",
                                 shadow=(3, 8, (255, 255, 255, 220))), 540, 1340, u, 0.5, "up")
        burst(base, t, 4.6, cx_r, cy, n=10, radius=320, seed=41)
    F5_SPARK.draw(base, t)
    title = text_img("GONCANG DAHULU! 🧡", 92, ORANGE, "xb", shadow=(4, 10, (255, 255, 255, 230)))
    s, a, dy = appear(t, 0.15, "pop")
    wob = 4 * math.sin(t * 2 * math.pi * 3) * (1 - prog(t, 0.5, 3.0))
    place(base, title, 540, 250 + dy, s, a, rot=wob)
    burst(base, t, 0.2, 540, 250, seed=42, radius=480)
    return base


F6_DROPS = Field(15, 9, DROP, (50, 120), vy=(25, 60), vx=(-30, -10), alpha=(0.7, 1.0), wob=20)
F6_SPARK = Field(16, 18, SPARK, (30, 80), twinkle=True)


def s_skin(t):
    base = zoom_view(model_big(), 1.15 + 0.12 * t / 4.6, 0.6, 0.4)
    p = prog(t, 0.1, 2.6)
    if 0 < p < 1:
        put(base, GLOW_WH, lerp(-300, W + 300, ease_io(p)), lerp(500, 1100, p), 1200, 0.6)
    a = np.zeros((H, W), np.float32)
    a[950:] = np.linspace(0, 0.62, H - 950)[:, None]
    base.alpha_composite(rgba(np.broadcast_to(np.array([70, 36, 20], np.float32), (H, W, 3)), a * 255))
    F6_DROPS.draw(base, t)
    F6_SPARK.draw(base, t)
    sh = (4, 12, (60, 25, 10, 200))
    draw_text(base, text_img("KULIT NAMPAK SEGAR ✨", 76, WHITE, "xb", shadow=sh), 540, 1120, t, 0.3, "pop")
    draw_text(base, text_img("LEMBAP & BERSERI 💧", 76, WHITE, "xb", shadow=sh), 540, 1230, t, 1.1, "pop")
    draw_text(base, pill("JAGA KULIT DARI SEKARANG 🧡", 52), 540, 1380, t, 2.0, "pop")
    burst(base, t, 0.35, 540, 1120, seed=50, radius=440)
    burst(base, t, 2.05, 540, 1380, seed=51, radius=440, n=12)
    return base


F7_SPARK = Field(17, 14, SPARK, (26, 60), twinkle=True)
F7_BUB = Field(18, 10, BUBBLE, (24, 56), vy=(-60, -30))
STEPS = [
    (0.45, "Bersihkan wajah."),
    (2.05, "Goncang serum\nsehingga sebati."),
    (3.65, "Sapukan serum\nsecukupnya."),
    (5.25, "Tepuk perlahan\nsehingga meresap."),
]
MEDIA_C = (540, 780)


def step_index(t):
    k = -1
    for i, (t0, _) in enumerate(STEPS):
        if t >= t0:
            k = i
    return k


@lru_cache(None)
def num_badge(n, r=54):
    sz = r * 2 + 20
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    sp = make_sphere(r * 2, base=(245, 108, 36), core=(255, 170, 90), alpha=255)
    im.alpha_composite(sp, (10, 10))
    t = text_img(str(n), int(r * 1.1), WHITE, "xb")
    im.alpha_composite(t, ((sz - t.width) // 2, (sz - t.height) // 2))
    return im


def s_howto(t):
    base = BG_PEARL.copy()
    rays(base, t, 540, 780, 0.6)
    F7_BUB.draw(base, t)
    k = step_index(t)
    for i, (t0, _) in enumerate(STEPS):
        t1 = STEPS[i + 1][0] if i + 1 < len(STEPS) else 99
        if not (t0 - 0.05 <= t < t1 + 0.25):
            continue
        u = t - t0
        a = clamp(u / 0.25) * (1 - prog(t, t1, t1 + 0.25))
        sc = 0.9 + 0.1 * ease_out(clamp(u / 0.35))
        cx, cy = MEDIA_C
        if i == 0:
            place(base, HOWTO08, cx, cy, 0.97 * sc, a)
            if 0 < u < 1.2:
                rng = np.random.default_rng(60)
                for j in range(22):
                    vx, vy = rng.uniform(-420, 420), rng.uniform(-1100, -700)
                    x, y = cx + vx * u, cy + 330 + vy * u + 1300 * u * u
                    put(base, DROP, x, y, rng.uniform(28, 70), a * (1 - u / 1.2))
        elif i == 1:
            framed_clip(base, 6.0 + u, (90, 420, 990, 1160), 860, 700, cx, cy, sc, a,
                        rot=2.5 * math.sin(u * 2 * math.pi * 3))
            for j in range(8):
                th = u * 3 + j * 0.785
                put(base, SPHERE, cx + 480 * math.cos(th), cy + 400 * math.sin(th), 30, a * 0.9)
        elif i == 2:
            framed_clip(base, 14.0 + u, (0, 520, 1080, 1400), 860, 700, cx, cy, sc, a)
            for j in range(4):
                q = ((u * 1.3 + j * 0.25) % 1)
                put(base, SPHERE, cx - 150 + j * 100, lerp(380, 820, ease_in(q)), 34, a * (1 - q))
        else:
            framed_clip(base, 17.6 + u, (0, 560, 1080, 1440), 860, 700, cx, cy, sc, a)
            for j in range(3):
                q = (u * 0.9 + j / 3) % 1
                ring = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
                ImageDraw.Draw(ring).ellipse((10, 10, 490, 490), outline=(255, 220, 190, int(220 * (1 - q))), width=8)
                place(base, ring, cx, cy + 40, 0.2 + 1.2 * q, a)
    title = text_img("CARA PENGGUNAAN 🧡", 84, ORANGE, "xb", shadow=(4, 10, (255, 255, 255, 230)))
    draw_text(base, title, 540, 230, t, 0.05, "pop")
    burst(base, t, 0.1, 540, 230, seed=70, radius=460)
    # step card
    if k >= 0:
        t0 = STEPS[k][0]
        s, a, dy = appear(t, t0, "up", 0.35)
        card = glass_card(900, 170, 40, fill=(255, 255, 255, 215)).copy()
        card.alpha_composite(num_badge(k + 1), (30 + 18, 30 + 21))
        tx = text_img(STEPS[k][1], 46, BROWN, "sb", align="left", max_w=700, line_h=1.12)
        card.alpha_composite(tx, (30 + 160, 30 + (170 - tx.height) // 2))
        place(base, card, 540, 1310 + dy, s, a)
    # progress row
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    xs = [300, 460, 620, 780]
    for i, x in enumerate(xs):
        if i < 3:
            d.line((x + 28, 1480, xs[i + 1] - 28, 1480), fill=(240, 150, 100, 200), width=4)
            ax = xs[i + 1] - 36
            d.polygon([(ax, 1472), (ax + 10, 1480), (ax, 1488)], fill=(240, 120, 60, 230))
        active = i <= k
        d.ellipse((x - 22, 1458, x + 22, 1502), fill=(240, 104, 32, 255) if active else (255, 255, 255, 230),
                  outline=(240, 104, 32, 255), width=4)
    base.alpha_composite(layer)
    for i, x in enumerate(xs):
        tc = WHITE if i <= k else ORANGE
        place(base, text_img(str(i + 1), 26, tc, "b"), x, 1481)
    F7_SPARK.draw(base, t)
    return base


F8_SPHERES = Field(19, 9, [SPHERE, SPHERE_GOLD], (36, 80), vy=(-45, -20), alpha=(0.75, 1), wob=40)
F8_SPARK = Field(20, 22, SPARK, (30, 80), twinkle=True)
F8_HEART = Field(21, 7, emoji("1f9e1", 120), (36, 64), vy=(-110, -60), yr=(500, H), alpha=(0.7, 1), wob=50)
F8_DROPS = Field(22, 6, DROP, (40, 90), vy=(-30, -10))


def s_cta(t):
    base = BG_CHAMP.copy()
    rays(base, t, 540, 900, 1.25, speed=8)
    put(base, GLOW_OR, 540, 900, 1100, 0.45)
    F8_DROPS.draw(base, t)
    ribbon(base, t, 820, 80, GOLD, 1.0, 14, 140)
    ribbon(base, t, 1020, 60, (255, 175, 120), 3.0, 10, 110, slope=0.2)
    place(base, PEDESTAL, 540, 1200, 1.0, clamp(t / 0.3))
    put(base, GLOW_WH, 540, 1130, 900, 0.5)
    pe = ease_out(prog(t, 0, 0.8))
    prod = gloss_sweep(PACK09.resize((900, 662), Image.BICUBIC), prog(t, 0.8, 1.9))
    place(base, prod, 540, 840 + 40 * (1 - pe) + 6 * math.sin(t * 1.5), 0.85 + 0.15 * pe, pe)
    F8_SPHERES.draw(base, t)
    F8_HEART.draw(base, t, clamp((t - 0.5) / 0.5))
    base = zoom_frame(base, 1 + 0.06 * t / 5.2, 540, 950)
    F8_SPARK.draw(base, t)
    draw_text(base, text_img("SKINCARE ROUTINE\nUPGRADE! 🧡", 84, BROWN, "xb", shadow=(4, 10, (255, 255, 255, 230))),
              540, 260, t, 0.15, "pop")
    burst(base, t, 0.2, 540, 260, seed=80, radius=480)
    draw_text(base, text_img("JAGA KULIT, JAGA KEYAKINAN ✨", 50, ORANGE, "xb"), 540, 425, t, 1.2, "up")
    draw_text(base, text_img("Formula sama • Pembungkusan mungkin berbeza", 26, (120, 88, 66), "m"),
              540, 1290, t, 1.6, "fade")
    draw_text(base, text_img("KENALI FRANKLY PDRN SERUM", 52, BROWN, "xb", shadow=(3, 8, (255, 255, 255, 230))),
              540, 1370, t, 2.4, "up")
    s, a, dy = appear(t, 3.0, "pop")
    pulse = 1 + 0.045 * math.sin((t - 3.0) * 2 * math.pi * 1.6) * prog(t, 3.4, 3.6)
    place(base, pill("SEMAK BAKUL KUNING 🛒", 58, fg=BROWN, bg=CTA_YELLOW, bg2=(255, 178, 40)),
          540, 1480 + dy, s * pulse, a)
    burst(base, t, 3.05, 540, 1480, seed=81, radius=460, n=14)
    return base


SCENES = [  # (fn, duration, transition into this scene)
    (s_hook, 4.6, None),
    (s_reveal, 5.6, "flash"),
    (s_pdrn, 6.0, "circle"),
    (s_ingredient, 5.8, "liquid"),
    (s_shake, 6.0, "circle"),
    (s_skin, 4.6, "flash"),
    (s_howto, 7.0, "liquid"),
    (s_cta, 5.4, "circle"),
]
TR = 0.4
STARTS = np.cumsum([0] + [d for _, d, _ in SCENES]).tolist()
DURATION = STARTS[-1]

_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
_RAD = np.sqrt((_XX - W / 2) ** 2 + (_YY - H / 2) ** 2)


def transition(prev, nxt, p, kind, t):
    if kind == "flash":
        out = Image.blend(prev, nxt, ease_io(clamp((p - 0.35) / 0.3)))
        fl = math.sin(math.pi * p) * 0.85
        return Image.blend(out, Image.new("RGBA", (W, H), (255, 250, 244, 255)), fl)
    if kind == "circle":
        r = ease_in(p) * 1150
        m = np.clip((r - _RAD) / 60 + 0.5, 0, 1)
    else:  # liquid wipe from bottom with a wavy edge
        edge = H * (1 - ease_io(p) * 1.15) + 60 * np.sin(_XX / 90 + t * 9) + 30 * np.sin(_XX / 37 - t * 5)
        m = np.clip((_YY - edge) / 40, 0, 1)
    out = Image.composite(nxt, prev, Image.fromarray((m * 255).astype(np.uint8)))
    if kind == "circle" and 0.05 < p < 0.98:
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        r = ease_in(p) * 1150
        ImageDraw.Draw(ring).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), outline=(255, 236, 214, 220), width=14)
        out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(4)))
    return out


def render_frame(i):
    t = i / FPS
    j = max(k for k in range(len(SCENES)) if STARTS[k] <= t + 1e-9)
    j = min(j, len(SCENES) - 1)
    fn, _, kind = SCENES[j]
    lt = t - STARTS[j]
    im = fn(lt)
    if kind and lt < TR and j > 0:
        prev = SCENES[j - 1][0](t - STARTS[j - 1])
        im = transition(prev, im, lt / TR, kind, t)
    return im.convert("RGB").tobytes()


def sfx_events():
    S = STARTS
    ev = [
        (0.10, "whoosh"), (0.15, "pop"), (0.45, "ting"), (1.40, "whoosh_soft"), (2.80, "pop"), (2.90, "sparkle"),
        (3.70, "riser"),
        (S[1] + 0.0, "impact"), (S[1] + 0.5, "pop"), (S[1] + 0.9, "whoosh_soft"), (S[1] + 1.5, "pop"),
        (S[1] + 1.4, "shimmer"), (S[1] + 3.3, "whoosh"), (S[1] + 4.5, "ting"),
        (S[2] - 0.05, "whoosh"), (S[2] + 0.8, "pop"), (S[2] + 0.9, "sparkle"),
        (S[3] - 0.05, "splash"), (S[3] + 0.25, "pop"), (S[3] + 0.65, "whoosh_soft"), (S[3] + 1.2, "pop"),
        (S[4] - 0.05, "whoosh"), (S[4] + 0.15, "pop"), (S[4] + 0.3, "shake"), (S[4] + 1.5, "tik"),
        (S[4] + 1.8, "tik"), (S[4] + 2.2, "shake"), (S[4] + 3.3, "whoosh_soft"), (S[4] + 3.4, "shake"),
        (S[4] + 4.2, "splash"), (S[4] + 4.6, "ting"),
        (S[5] - 0.05, "whoosh"), (S[5] + 0.3, "pop"), (S[5] + 1.1, "pop"), (S[5] + 2.0, "pop"),
        (S[5] + 2.05, "sparkle"),
        (S[6] - 0.05, "splash"), (S[6] + 0.05, "pop"),
        (S[7] - 0.05, "whoosh"), (S[7] + 0.15, "pop"), (S[7] + 0.2, "shimmer"), (S[7] + 1.2, "whoosh_soft"),
        (S[7] + 2.4, "pop"), (S[7] + 3.0, "pop"), (S[7] + 3.05, "sparkle"), (S[7] + 3.6, "ting"),
    ]
    for k, (t0, _) in enumerate(STEPS):
        st = S[6] + t0
        ev.append((st, "pop"))
        ev.append((st + 0.05, ["splash", "shake", "drip", "ting"][k]))
    for k in range(4):
        ev.append((S[2] + 1.5 + 0.7 * k, "tik"))
        ev.append((S[2] + 1.75 + 0.7 * k, "pop"))
    for k in range(3):
        ev.append((S[3] + 2.8 + 0.35 * k, "tik"))
    return sorted(ev)


def main():
    global CLIP_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="hands-on phone video of the real product")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "output", "frankly-pdrn-bounce-ball-serum.mp4"))
    ap.add_argument("--stills", help="comma-separated times (s) to render as PNG previews")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    args = ap.parse_args()

    work = tempfile.mkdtemp(prefix="frankly-")
    CLIP_DIR = os.path.join(work, "clip")
    os.makedirs(CLIP_DIR)
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(CLIP_T0), "-i", args.video, "-t", "15", "-r", str(FPS),
                    "-q:v", "2", os.path.join(CLIP_DIR, "f%04d.jpg")], check=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    if args.stills:
        outdir = os.path.dirname(os.path.abspath(args.out))
        for s in args.stills.split(","):
            i = int(float(s) * FPS)
            Image.frombytes("RGB", (W, H), render_frame(i)).save(os.path.join(outdir, f"still_{float(s):05.2f}.jpg"), quality=90)
        print("stills written to", outdir)
        return

    wav = os.path.join(work, "audio.wav")
    audio.render(wav, DURATION, sfx_events(), scene_starts=STARTS)
    n = int(round(DURATION * FPS))
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", args.out],
        stdin=subprocess.PIPE)
    with Pool(args.workers) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(n), chunksize=4)):
            enc.stdin.write(buf)
            if k % 60 == 0:
                print(f"frame {k}/{n}", file=sys.stderr, flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
