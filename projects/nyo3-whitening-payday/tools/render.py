"""NYO3 Whitening Pycnogenol — Payday Sales TikTok edit (1080x1920, 30 fps, 30 s).

Usage:
    python3 render.py SOURCE.mp4 COMPARISON.jpg OUT.mp4 [--no-payday] [--preview T1,T2,...]

The original phone footage stays the main footage. Everything added on top
(text, graphics, sparkles, music, SFX) is generated here, so there are no
third-party assets to license. The brand comparison image is used as-is
(no retouching), with the percentage column cropped off.
"""
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade import grade  # noqa: E402
import audio  # noqa: E402

W, H, FPS, DUR = 1080, 1920, 30, 30.0
NF = int(DUR * FPS)

FD = "/usr/share/fonts/opentype/inter/"
F_BLACK = FD + "InterDisplay-Black.otf"
F_XBOLD = FD + "InterDisplay-ExtraBold.otf"
F_BOLD = FD + "InterDisplay-Bold.otf"
F_SEMI = FD + "Inter-SemiBold.otf"
F_MED = FD + "Inter-Medium.otf"
F_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

PINK = (255, 92, 160)
HOTPINK = (236, 48, 132)
ROSE = (255, 182, 208)
PLUM = (92, 24, 62)
GOLD = (246, 205, 130)
CHAMPAGNE = (247, 226, 190)
PEARL = (255, 246, 249)
TT_YELLOW = (254, 196, 0)

rng = np.random.default_rng(42)
_font_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.9):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ drawing primitives
def paste(base, im, x, y, alpha=1.0):
    """Alpha-composite RGBA `im` onto RGBA `base` with its top-left at (x, y), clipped."""
    if alpha <= 0.003:
        return
    x, y = int(round(x)), int(round(y))
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(im.width, base.width - x), min(im.height, base.height - y)
    if ex <= sx or ey <= sy:
        return
    if (sx, sy, ex, ey) != (0, 0, im.width, im.height):
        im = im.crop((sx, sy, ex, ey))
    base.alpha_composite(im, (x + sx, y + sy))


def paste_c(base, im, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if scale <= 0.01:
        return
    if abs(scale - 1) > 0.003:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    paste(base, im, cx - im.width / 2, cy - im.height / 2, alpha)


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def gradient(w, h, c1, c2, horizontal=True):
    t = np.linspace(0, 1, w if horizontal else h)[:, None] if not horizontal else np.linspace(0, 1, w)[None, :]
    c1, c2 = np.array(c1, np.float32), np.array(c2, np.float32)
    if horizontal:
        g = c1[None, None] + (c2 - c1)[None, None] * t[..., None]
        g = np.repeat(g, h, 0)
    else:
        g = c1[None, None] + (c2 - c1)[None, None] * t[..., None]
        g = np.repeat(g, w, 1)
    return Image.fromarray(g.astype(np.uint8)).convert("RGBA")


def glow(im, radius, color, strength=1.0):
    """Return `im` with a soft coloured glow underneath (canvas grows by 2*radius)."""
    pad = radius * 2
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (pad, pad))
    a = a.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", out.size, color + (0,))
    g.putalpha(a)
    out.alpha_composite(g)
    out.alpha_composite(im, (pad, pad))
    return out


def emoji(ch, size):
    f = font(F_EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)


def text_img(text, fpath, size, fill=(255, 255, 255), stroke=0, stroke_fill=PLUM, shadow=True,
             align="center", spacing=1.08):
    f = font(fpath, size)
    lines = text.split("\n")
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    boxes = [d.textbbox((0, 0), ln, font=f, stroke_width=stroke) for ln in lines]
    lh = int(size * spacing)
    w = max(b[2] - b[0] for b in boxes) + 8
    h = lh * (len(lines) - 1) + (boxes[-1][3] - boxes[0][1]) + 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for i, (ln, b) in enumerate(zip(lines, boxes)):
        lw = b[2] - b[0]
        x = (w - lw) / 2 - b[0] if align == "center" else 4 - b[0]
        dr.text((x, 4 + i * lh - boxes[0][1]), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    if shadow:
        sh = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
        a = Image.new("L", sh.size, 0)
        a.paste(im.getchannel("A"), (20, 26))
        a = a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.45))
        s = Image.new("RGBA", sh.size, (60, 10, 40, 0))
        s.putalpha(a)
        sh.alpha_composite(s)
        sh.alpha_composite(im, (20, 20))
        im = sh
    return im


def with_emoji(em, txt_im, em_size, gap=14):
    e = emoji(em, em_size)
    w = e.width + gap + txt_im.width
    h = max(e.height, txt_im.height)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(e, (0, (h - e.height) // 2))
    out.alpha_composite(txt_im, (e.width + gap, (h - txt_im.height) // 2))
    return out


def pill(content, c1, c2, padx=40, pady=22, radius=None, border=None):
    w, h = content.width + padx * 2, content.height + pady * 2
    radius = radius if radius is not None else h // 2
    bg = gradient(w, h, c1, c2)
    bg.putalpha(rounded_mask(w, h, radius))
    if border:
        ImageDraw.Draw(bg).rounded_rectangle((1, 1, w - 2, h - 2), radius, outline=border, width=3)
    # glossy top highlight
    hl = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    hm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(hm).rounded_rectangle((6, 4, w - 7, h // 2), radius, fill=48)
    hl.putalpha(hm)
    bg.alpha_composite(hl)
    bg.alpha_composite(content, (padx, pady))
    return bg


def glass_card(frame_rgba, x, y, w, h, radius=34, tint=(255, 240, 246), opacity=0.55):
    """Frosted-glass card: blurs whatever is behind it in `frame_rgba`, then tints it."""
    x, y = int(x), int(y)
    region = frame_rgba.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(18))
    tintl = Image.new("RGBA", (w, h), tint + (int(255 * opacity),))
    region.alpha_composite(tintl)
    mask = rounded_mask(w, h, radius)
    region.putalpha(mask)
    ImageDraw.Draw(region).rounded_rectangle((1, 1, w - 2, h - 2), radius, outline=(255, 255, 255, 200), width=3)
    return region


# ------------------------------------------------------------------ sprites
def star_sprite(size, color):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    r1, r2 = s * 0.46, s * 0.07
    pts = []
    for k in range(8):
        r = r1 if k % 2 == 0 else r2
        a = k * math.pi / 4 - math.pi / 2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=color + (255,))
    core = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse((c - s * .12, c - s * .12, c + s * .12, c + s * .12), fill=(255, 255, 255, 255))
    g = im.filter(ImageFilter.GaussianBlur(s * 0.06))
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(im)
    out.alpha_composite(core.filter(ImageFilter.GaussianBlur(s * 0.03)))
    return out.resize((size, size), Image.LANCZOS)


STAR_COLORS = [GOLD, ROSE, (255, 255, 255), CHAMPAGNE]
STARS = {(c, sz): star_sprite(sz, c) for c in STAR_COLORS for sz in (18, 28, 40, 56)}


def bokeh_sprite(r, color, a=70):
    im = Image.new("RGBA", (r * 2 + 20, r * 2 + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((10, 10, 10 + 2 * r, 10 + 2 * r), fill=color + (a,))
    return im.filter(ImageFilter.GaussianBlur(4))


def bag_sprite(size, body=PINK, handle=GOLD, label=True):
    s = size * 3
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc((s * .3, s * .05, s * .7, s * .55), 180, 360, fill=handle + (255,), width=int(s * .07))
    d.rounded_rectangle((s * .12, s * .3, s * .88, s * .95), int(s * .08), fill=body + (255,))
    d.rounded_rectangle((s * .12, s * .3, s * .88, s * .45), int(s * .06), fill=tuple(min(255, c + 30) for c in body) + (255,))
    if label:
        d.ellipse((s * .38, s * .52, s * .62, s * .76), fill=(255, 255, 255, 235))
        d.text((s * .5, s * .645), "♥", font=font(F_BLACK, int(s * .17)), fill=body + (255,), anchor="mm")
    return glow(im.resize((size, size), Image.LANCZOS), 6, (255, 220, 235), 0.8)


class Sparkles:
    """Twinkling star field with deterministic per-particle phases."""

    def __init__(self, n, box, sizes=(18, 28, 40), colors=STAR_COLORS, drift=(0, -30), seed=0):
        r = np.random.default_rng(seed)
        x0, y0, x1, y1 = box
        self.p = [dict(x=r.uniform(x0, x1), y=r.uniform(y0, y1), sz=int(r.choice(sizes)),
                       c=colors[int(r.integers(len(colors)))], ph=r.uniform(0, 6.28),
                       sp=r.uniform(2.5, 5.5)) for _ in range(n)]
        self.drift = drift

    def draw(self, base, t, alpha=1.0, offset=(0, 0)):
        for q in self.p:
            tw = max(0.0, math.sin(t * q["sp"] + q["ph"])) ** 2
            if tw < 0.05:
                continue
            spr = STARS[(q["c"], q["sz"])]
            paste_c(base, spr, q["x"] + self.drift[0] * t + offset[0], q["y"] + self.drift[1] * t + offset[1],
                    alpha * tw, 0.6 + 0.5 * tw, rot=t * 40 % 90)


# ------------------------------------------------------------------ animated icons (220x220)
def icon_hydration(t, s=220):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(3):  # ripples
        ph = (t * 0.9 + k / 3) % 1
        r = 30 + ph * 80
        d.ellipse((s / 2 - r, s * .8 - r * .28, s / 2 + r, s * .8 + r * .28), outline=(120, 190, 255, int(200 * (1 - ph))), width=4)
    for k in range(3):  # falling drops
        ph = (t * 1.3 + k / 3) % 1
        cx, cy = s * (.3 + .2 * k), s * (.05 + .65 * ph)
        r = 9
        d.polygon([(cx, cy - r * 2), (cx - r, cy), (cx + r, cy)], fill=(140, 205, 255, int(230 * (1 - ph * .6))))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(140, 205, 255, int(230 * (1 - ph * .6))))
    cx, cy, r = s / 2, s * .52, 40 + 3 * math.sin(t * 5)  # big drop
    d.polygon([(cx, cy - r * 1.9), (cx - r * .95, cy - r * .2), (cx + r * .95, cy - r * .2)], fill=(90, 170, 255, 255))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(90, 170, 255, 255))
    d.ellipse((cx - r * .5, cy - r * .6, cx - r * .15, cy - r * .1), fill=(255, 255, 255, 200))
    return glow(im, 8, (170, 215, 255), 0.7)


def icon_face(t, s=220):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    for k in range(10):  # rotating rays
        a = k * math.pi / 5 + t * 0.8
        r0, r1 = 80, 98 + 6 * math.sin(t * 6 + k)
        d.line((c + r0 * math.cos(a), c + r0 * math.sin(a), c + r1 * math.cos(a), c + r1 * math.sin(a)),
               fill=GOLD + (220,), width=5)
    d.ellipse((c - 58, c - 70, c + 58, c + 70), fill=(255, 226, 214, 255), outline=(236, 120, 160, 255), width=4)
    d.arc((c - 34, c - 18, c - 8, c + 4), 20, 160, fill=PLUM + (255,), width=4)
    d.arc((c + 8, c - 18, c + 34, c + 4), 20, 160, fill=PLUM + (255,), width=4)
    d.arc((c - 22, c + 10, c + 22, c + 42), 20, 160, fill=(220, 70, 120, 255), width=5)
    d.ellipse((c - 46, c + 8, c - 28, c + 22), fill=(255, 160, 185, 160))
    d.ellipse((c + 28, c + 8, c + 46, c + 22), fill=(255, 160, 185, 160))
    out = glow(im, 8, (255, 225, 200), 0.6)
    tw = abs(math.sin(t * 4))
    paste_c(out, STARS[(GOLD, 40)], out.width * .74, out.height * .3, tw)
    paste_c(out, STARS[((255, 255, 255), 28)], out.width * .28, out.height * .26, 1 - tw)
    return out


def icon_collagen(t, s=220):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cols = [(255, 120, 170), (255, 190, 120), (200, 140, 255)]
    for k, col in enumerate(cols):
        pts = [(s * .12 + x, s / 2 + 42 * math.sin(x / 26 + t * 3 + k * 2.094)) for x in range(0, int(s * .76), 3)]
        d.line(pts, fill=col + (255,), width=7, joint="curve")
        for x in range(0, int(s * .76), 36):
            y = s / 2 + 42 * math.sin(x / 26 + t * 3 + k * 2.094)
            d.ellipse((s * .12 + x - 6, y - 6, s * .12 + x + 6, y + 6), fill=(255, 255, 255, 230))
    return glow(im, 8, (255, 200, 225), 0.6)


def icon_capsule(t, s=220):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    sh = [(c, 22), (c + 72, 50), (c + 64, 140), (c, 196), (c - 64, 140), (c - 72, 50)]
    d.polygon(sh, fill=(255, 214, 230, 255), outline=(236, 90, 150, 255))
    d.line(sh + [sh[0]], fill=(236, 90, 150, 255), width=5)
    cap = Image.new("RGBA", (150, 60), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap)
    cd.rounded_rectangle((0, 0, 149, 59), 30, fill=(255, 255, 255, 255))
    cd.rounded_rectangle((0, 0, 75, 59), 30, fill=(255, 110, 165, 255))
    cd.rectangle((45, 0, 75, 59), fill=(255, 110, 165, 255))
    cd.ellipse((14, 10, 40, 22), fill=(255, 255, 255, 140))
    cap = cap.rotate(-30 + 8 * math.sin(t * 3), Image.BICUBIC, expand=True)
    im.alpha_composite(cap, (int(c - cap.width / 2), int(c - cap.height / 2 + 6)))
    for k in range(5):
        a = t * 2 + k * 2 * math.pi / 5
        x, y = c + 96 * math.cos(a), c + 30 * math.sin(a) + 4
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=GOLD + (230,))
    return glow(im, 8, (255, 210, 225), 0.6)


def molecule(t, s=260, seed=0):
    r = np.random.default_rng(seed)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts3 = r.uniform(-1, 1, (7, 3))
    pts3 /= np.linalg.norm(pts3, axis=1, keepdims=True)
    a = t * 0.7 + seed
    rot = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    p = pts3 @ rot.T
    pr = [(s / 2 + q[0] * s * .34, s / 2 + q[1] * s * .34, q[2]) for q in p]
    for i in range(len(pr)):
        for j in range(i + 1, len(pr)):
            if np.linalg.norm(pts3[i] - pts3[j]) < 1.15:
                d.line((pr[i][0], pr[i][1], pr[j][0], pr[j][1]), fill=(255, 255, 255, 150), width=3)
    for x, y, z in sorted(pr, key=lambda q: q[2]):
        rr = 12 + 6 * z
        col = (255, 150, 195) if z > 0 else (255, 214, 160)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (235,))
        d.ellipse((x - rr * .5, y - rr * .6, x - rr * .05, y - rr * .2), fill=(255, 255, 255, 170))
    return glow(im, 6, (255, 220, 235), 0.5)


# ------------------------------------------------------------------ footage
def load_clip(src, start, src_dur, out_dur):
    n = int(round(out_dur * FPS))
    factor = out_dur / src_dur
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{src_dur + 0.05:.3f}", "-i", src,
           "-vf", f"setpts={factor:.5f}*PTS,fps={FPS},scale={W}:{H}:flags=lanczos", "-an",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    idx = np.minimum(np.arange(n), len(fr) - 1)
    return fr, idx


def zoom(img, s, cx=W / 2, cy=H / 2):
    """Crop around (cx, cy) by factor s>=1 and scale back to full frame."""
    if s <= 1.0005:
        return img
    cw, ch = W / s, H / s
    x0 = clamp(cx - cw / 2, 0, W - cw)
    y0 = clamp(cy - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def track_box(rgb):
    """Centroid/bbox of the white packaging (bright, low-saturation pixels)."""
    a = rgb[::8, ::8].astype(np.int16)
    mn, mx = a.min(2), a.max(2)
    m = (mn > 165) & (mx - mn < 50)
    if m.sum() < 60:
        return None
    ys, xs = np.nonzero(m)
    return (xs.mean() * 8, ys.mean() * 8, np.percentile(xs, 3) * 8, np.percentile(ys, 3) * 8,
            np.percentile(xs, 97) * 8, np.percentile(ys, 97) * 8)


def shine(base_rgb, t_rel, dur=0.7, strength=0.32):
    """Diagonal light sweep restricted to the packaging pixels (the box only)."""
    if not 0 <= t_rel <= dur:
        return base_rgb
    a = base_rgb.astype(np.float32)
    mn, mx = a.min(2), a.max(2)
    m = np.clip((mn - 150) / 40, 0, 1) * (mx - mn < 60)
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    pos = (xx + yy * 0.6) / (W + H * 0.6)
    c = -0.2 + 1.4 * (t_rel / dur)
    band = np.exp(-((pos - c) / 0.05) ** 2)
    band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)) / 255.0
    a += ((255 - a) * (band * m * strength)[..., None])
    return np.clip(a, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ text layers (built once)
class Layer:
    def __init__(self, im, t0, t1, cx, cy, anim="pop", pulse=0.0):
        self.im, self.t0, self.t1, self.cx, self.cy, self.anim, self.pulse = im, t0, t1, cx, cy, anim, pulse

    def draw(self, base, t):
        if not self.t0 <= t < self.t1:
            return
        a_in = (t - self.t0) / 0.32
        a_out = (self.t1 - t) / 0.22
        alpha = clamp(min(a_in * 2.2, a_out))
        sc, dy = 1.0, 0
        if self.anim == "pop":
            sc = 0.55 + 0.45 * ease_out_back(a_in)
        elif self.anim == "slam":
            sc = 1.6 - 0.6 * ease_out_cubic(a_in * 1.3)
        elif self.anim == "slide":
            dy = 60 * (1 - ease_out_cubic(a_in))
        if a_out < 1:
            sc *= 1 + 0.06 * (1 - clamp(a_out))
        if self.pulse:
            sc *= 1 + self.pulse * max(0.0, math.sin((t - self.t0) * 2 * math.pi * 1.6)) ** 2
        paste_c(base, self.im, self.cx, self.cy + dy, alpha, sc)


def headline(em, txt, size, fill=(255, 255, 255), stroke=7, stroke_fill=HOTPINK, font_path=F_BLACK, em_size=None):
    t = text_img(txt, font_path, size, fill, stroke, stroke_fill)
    return with_emoji(em, t, em_size or int(size * 1.05)) if em else t


def build_layers(payday):
    L = {}
    # Hook
    L["hook1"] = glow(headline("🔥", "GAJI DAH\nMASUK?!", 118, stroke=9), 14, (255, 120, 180), 0.9)
    hook2_txt = "PAYDAY SALES NYO3!" if payday else "JOM KENALI NYO3!"
    L["hook2"] = glow(pill(with_emoji("💗", text_img(hook2_txt, F_BLACK, 62, shadow=False), 64),
                           (255, 84, 150), (255, 160, 120), border=GOLD), 16, GOLD, 0.8)
    # Comparison
    L["cmp1"] = with_emoji("✨", text_img("NAK KULIT NAMPAK\nLEBIH BERSERI?", F_BLACK, 72, PLUM, 0, shadow=False), 74)
    L["cmp2"] = with_emoji("💗", text_img("KENALI PENJAGAAN\nKULIT NYO3!", F_BLACK, 72, HOTPINK, 0, shadow=False), 74)
    L["cmp_label"] = pill(text_img("Visual perbandingan promosi jenama — bukan bukti\n"
                                   "hasil pengguna yang disahkan. Hasil individu mungkin berbeza.",
                                   F_SEMI, 27, PLUM, shadow=False, spacing=1.25),
                          (255, 255, 255), (255, 240, 246), padx=26, pady=14, radius=22, border=(255, 170, 200))
    # Formula
    L["form_title"] = glow(pill(with_emoji("🌸", text_img("KENALI FORMULA NYO3!", F_BLACK, 56, shadow=False), 58),
                                (236, 72, 140), (255, 140, 170), border=(255, 230, 240)), 14, (255, 150, 200), 0.7)
    chips = [("✨", "Pycnogenol®", "Ekstrak kulit pain Perancis"),
             ("💧", "Sodium\nHyaluronate", "Sokongan hidrasi"),
             ("🌸", "Kolagen Marin", "Naticol®"),
             ("🛡️", "Vitamin E\n+ Zink", "Nutrien penjagaan kulit")]
    L["chips"] = []
    for em, name, sub in chips:
        nm = text_img(name, F_XBOLD, 38, PLUM, shadow=False, align="left", spacing=1.0)
        sb = text_img(sub, F_MED, 24, (150, 60, 105), shadow=False, align="left")
        col = Image.new("RGBA", (max(nm.width, sb.width), nm.height + sb.height), (0, 0, 0, 0))
        col.alpha_composite(nm, (0, 0))
        col.alpha_composite(sb, (0, nm.height))
        L["chips"].append(with_emoji(em, col, 62, gap=16))
    # Infographic
    L["benefits"] = [text_img(s, F_BLACK, 50, PLUM, shadow=False, align="left", spacing=1.05) for s in
                     ("SOKONGAN HIDRASI\nKULIT", "NUTRISI UNTUK\nKULIT BERSERI",
                      "SOKONGAN\nKEANJALAN KULIT", "PENJAGAAN KULIT\nDARI DALAM")]
    L["benefit_em"] = [emoji(e, 56) for e in ("💧", "✨", "🌸", "🛡️")]
    L["foot"] = pill(text_img("Suplemen makanan · sokongan nutrisi, bukan rawatan", F_SEMI, 26, PLUM, shadow=False),
                     (255, 255, 255), (255, 236, 244), padx=24, pady=12, radius=20)
    # Hero
    L["hero1"] = glow(headline("💗", "NYO3 WHITENING\nPYCNOGENOL", 86, stroke=6, stroke_fill=(214, 40, 120)), 16,
                      (255, 140, 190), 0.9)
    L["hero2"] = pill(with_emoji("✨", text_img("PENJAGAAN KULIT\nBERMULA DARI DALAM", F_XBOLD, 50, PLUM,
                                               shadow=False), 54),
                      CHAMPAGNE, (255, 214, 226), padx=36, pady=20, radius=40, border=(255, 255, 255))
    # Close
    close1 = "PAYDAY SALES\nHARI INI!" if payday else "DAPATKAN DI\nTIKTOK SHOP!"
    L["close1"] = glow(headline("💗", close1, 96, stroke=8), 16, (255, 120, 180), 0.9)
    L["close2"] = with_emoji("✨", text_img("MASA UNTUK UPGRADE\nRUTIN PENJAGAAN KULIT!", F_XBOLD, 50, (255, 255, 255),
                                           5, (196, 40, 112)), 54)
    bag = bag_sprite(84, TT_YELLOW, (255, 140, 0), label=False)
    cta_txt = text_img("TEKAN BEG KUNING\nSEKARANG!", F_BLACK, 52, shadow=False)
    row = Image.new("RGBA", (bag.width + 10 + cta_txt.width, max(bag.height, cta_txt.height)), (0, 0, 0, 0))
    row.alpha_composite(bag, (0, (row.height - bag.height) // 2))
    row.alpha_composite(cta_txt, (bag.width + 10, (row.height - cta_txt.height) // 2))
    L["cta"] = glow(pill(row, (255, 60, 140), (255, 120, 170), padx=34, pady=18, border=(255, 230, 150)), 18,
                    (255, 120, 180), 1.0)
    L["bag_pink"] = bag_sprite(110)
    L["bag_gold"] = bag_sprite(96, (250, 200, 120), PINK)
    L["bag_yellow"] = bag_sprite(90, TT_YELLOW, (255, 140, 0), label=False)
    return L


# ------------------------------------------------------------------ comparison scene assets
def build_comparison(cmp_path):
    src = Image.open(cmp_path).convert("RGB")
    # Keep both columns with all four skin rows; drop title and the % column.
    panel = src.crop((105, 190, 693, 905))
    pw = 820
    ph = int(panel.height * pw / panel.width)
    bg = gradient(W, H, (255, 244, 248), (250, 214, 228), horizontal=False)
    return dict(panel=panel, pw=pw, ph=ph, bg=bg,
                bokeh=[(rng.uniform(0, W), rng.uniform(0, H), int(rng.uniform(30, 90)),
                        [ROSE, (255, 255, 255), CHAMPAGNE][int(rng.integers(3))], rng.uniform(-20, 20),
                        rng.uniform(-40, -10)) for _ in range(16)])


BOKEH_CACHE = {}


def comparison_frame(C, L, t_local):
    base = C["bg"].copy()
    for x, y, r, col, vx, vy in C["bokeh"]:
        k = (r, col)
        if k not in BOKEH_CACHE:
            BOKEH_CACHE[k] = bokeh_sprite(r, col)
        paste_c(base, BOKEH_CACHE[k], x + vx * t_local, y + vy * t_local, 0.9)

    pw, ph = C["pw"], C["ph"]
    px, py = (W - pw) // 2, 392
    # entrance: slide up + scale in
    e = ease_out_cubic(t_local / 0.45)
    # slow push-in on the faces (crop inside panel; pixels themselves are not edited)
    z = 1.0 + 0.07 * ease_in_out(t_local / 4.0)
    panel = C["panel"]
    cw, ch = panel.width / z, panel.height / z
    x0, y0 = (panel.width - cw) / 2, (panel.height - ch) * 0.55
    content = panel.resize((pw, ph), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    content.putalpha(rounded_mask(pw, ph, 30))
    framed = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
    fd = ImageDraw.Draw(framed)
    fd.rounded_rectangle((0, 0, pw + 23, ph + 23), 40, fill=(255, 120, 175, 255))
    fd.rounded_rectangle((5, 5, pw + 18, ph + 18), 36, fill=(255, 214, 230, 255))
    framed.alpha_composite(content, (12, 12))
    framed = glow(framed, 22, (255, 120, 180), 0.55)
    paste_c(base, framed, W / 2, py + ph / 2 + 160 * (1 - e), e, 0.9 + 0.1 * e)

    # magnifier sweeping across the second (pigmentation) row, both columns
    if 1.3 < t_local < 3.75 and e >= 1:
        k = ease_in_out((t_local - 1.3) / 2.45)
        la = clamp(min((t_local - 1.3) / 0.25, (3.75 - t_local) / 0.25))
        row_y = 0.495  # relative to the panel, row 2 centre
        u = 0.18 + 0.64 * k
        cx_p, cy_p = px + u * pw, py + row_y * ph
        R, mag = 105, 1.8
        sx, sy = (cx_p - px) / pw * panel.width, (cy_p - py) / ph * panel.height
        sx = x0 + sx / z
        sy = y0 + sy / z
        rr = R / (pw / panel.width * z) / mag
        lens = panel.resize((2 * R, 2 * R), Image.LANCZOS, box=(sx - rr, sy - rr, sx + rr, sy + rr)).convert("RGBA")
        m = Image.new("L", (2 * R, 2 * R), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
        lens.putalpha(m)
        ring = Image.new("RGBA", (2 * R + 40, 2 * R + 80), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rd.line((2 * R + 4, 2 * R + 4, 2 * R + 34, 2 * R + 70), fill=(236, 72, 140, 255), width=14)
        ring.alpha_composite(lens, (4, 4))
        rd.ellipse((2, 2, 2 * R + 6, 2 * R + 6), outline=(255, 255, 255, 255), width=8)
        rd.ellipse((0, 0, 2 * R + 8, 2 * R + 8), outline=(236, 72, 140, 255), width=4)
        ring = glow(ring, 10, (255, 140, 190), 0.6)
        paste(base, ring, cx_p - R - 4 - 20, cy_p - R - 4 - 20, la)

    Layer(L["cmp1"], 0.15, 2.05, W / 2, 245, "pop").draw(base, t_local)
    Layer(L["cmp2"], 2.0, 4.2, W / 2, 245, "pop").draw(base, t_local)
    Layer(L["cmp_label"], 0.5, 4.2, W / 2, py + ph + 70, "fade").draw(base, t_local)
    return base


# ------------------------------------------------------------------ main compositor
def make_frames(src, cmp_path, payday, only=None):
    L = build_layers(payday)
    C = build_comparison(cmp_path)

    scenes = [  # name, out_start, out_end, src_start, src_dur, zoom(t)->(s, cx, cy)
        ("hook", 0, 2, 1.05, 1.55, lambda u: (1.0 + 0.14 * ease_out_cubic(u), 540, 1080)),
        ("cmp", 2, 6, None, None, None),
        ("formula", 6, 11, 3.0, 2.3, lambda u: (1.04 + 0.03 * u, 600, 1100)),
        ("info", 11, 17, 11.0, 4.9, lambda u: (1.0 + 0.05 * u, 540, 1150)),
        ("hero", 17, 23, 9.8, 1.2, lambda u: (1.0 + 0.10 * ease_in_out(u), 540, 880)),
        ("close", 23, 30, 1.6, 1.35, lambda u: (1.12 - 0.04 * u, 540, 1130)),
    ]
    sp_hook = Sparkles(26, (40, 60, 1040, 1500), (28, 40, 56), seed=1)
    sp_cmp = Sparkles(14, (40, 120, 1040, 1700), (18, 28), seed=2)
    sp_soft = Sparkles(16, (40, 80, 1040, 1700), (18, 28, 40), seed=3, drift=(0, -20))
    sp_close = Sparkles(30, (40, 60, 1040, 1750), (28, 40, 56), seed=4)
    bags = [(float(rng.choice([rng.uniform(70, 200), rng.uniform(880, 1010)])), rng.uniform(-25, 25), rng.uniform(0.0, 0.8), rng.uniform(0.7, 1.15),
             int(rng.integers(2))) for _ in range(7)]

    for name, t0, t1, ss, sd, zf in scenes:
        n0, n1 = int(t0 * FPS), int(t1 * FPS)
        if only is not None and not any(n0 <= f < n1 for f in only):
            continue
        if ss is not None:
            clip, idx = load_clip(src, ss, sd, t1 - t0)
        trk = None
        for fi in range(n0, n1):
            if only is not None and fi not in only:
                continue
            t = fi / FPS
            tl = t - t0
            u = tl / (t1 - t0)
            if name == "cmp":
                base = comparison_frame(C, L, tl)
                sp_cmp.draw(base, t, 0.7)
            else:
                g = grade(clip[idx[fi - n0]])
                s, cx, cy = zf(u)
                # zoom punch on every cut for energy
                s *= 1 + 0.07 * (1 - ease_out_cubic(tl / 0.35))
                img = zoom(Image.fromarray(g), s, cx, cy)
                arr = np.asarray(img)
                if name in ("hero", "close", "hook"):
                    for st in {"hero": (0.6, 3.6), "close": (0.4, 4.4), "hook": (0.9,)}[name]:
                        arr = shine(arr, tl - st)
                base = Image.fromarray(arr).convert("RGBA")
                tb = track_box(arr)
                if tb:
                    trk = tb if trk is None else tuple(0.7 * a + 0.3 * b for a, b in zip(trk, tb))
                draw_overlays(name, base, t, tl, L, trk, sp_hook, sp_soft, sp_close, bags)
            # flash transition into every scene except the first
            if t0 > 0 and tl < 0.22:
                fl = (1 - tl / 0.22) ** 2 * 0.75
                base.alpha_composite(Image.new("RGBA", (W, H), (255, 236, 244, int(255 * fl))))
            if t1 < DUR and t1 - t < 0.12:
                fl = (1 - (t1 - t) / 0.12) ** 2 * 0.6
                base.alpha_composite(Image.new("RGBA", (W, H), (255, 236, 244, int(255 * fl))))
            yield fi, base.convert("RGB")


def draw_overlays(name, base, t, tl, L, trk, sp_hook, sp_soft, sp_close, bags):
    if name == "hook":
        sp_hook.draw(base, t, 0.9)
        Layer(L["hook1"], 0.03, 2.0, W / 2, 300, "slam").draw(base, t)
        Layer(L["hook2"], 0.9, 2.0, W / 2, 545, "pop").draw(base, t)
        if tl > 0.85:  # shopping bags floating up
            for x, rot, d0, sc, kind in bags:
                k = (tl - 0.85 - d0 * 0.4) / 1.0
                if 0 < k < 1.2:
                    spr = L["bag_pink"] if kind else L["bag_gold"]
                    paste_c(base, spr, x, 1960 - 420 * ease_out_cubic(k), clamp(min(k * 4, (1.2 - k) * 3)),
                            sc, rot + 10 * math.sin(k * 6))

    elif name == "formula":
        sp_soft.draw(base, t, 0.6)
        for k, (mx, my) in enumerate([(130, 1650), (950, 1480), (120, 780)]):
            paste_c(base, molecule(t, 200, seed=k), mx, my + 20 * math.sin(t * 1.5 + k), 0.55)
        Layer(L["form_title"], 0.05, 5.0, W / 2, 150, "pop").draw(base, t - 6)
        slots = [(285, 330), (795, 330), (285, 520), (795, 520)]
        for k, (cx, cy) in enumerate(slots):
            ts = 7.0 + k
            if t < ts:
                continue
            a = (t - ts) / 0.3
            card = glass_card(base, cx - 245, cy - 82, 490, 164, opacity=0.62)
            card.alpha_composite(L["chips"][k], (22, (164 - L["chips"][k].height) // 2))
            paste_c(base, card, cx, cy, clamp(a * 2), 0.6 + 0.4 * ease_out_back(a))
            # glowing connector to the product for the newest chip
            if trk and t - ts < 0.9:
                p = ease_out_cubic((t - ts) / 0.5)
                ex, ey = trk[0], trk[1]
                sx, sy = cx, cy + 82
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov)
                fx, fy = sx + (ex - sx) * p, sy + (ey - sy) * p
                od.line((sx, sy, fx, fy), fill=(255, 220, 240, 230), width=4)
                od.ellipse((fx - 10, fy - 10, fx + 10, fy + 10), fill=(255, 255, 255, 255))
                ov = glow(ov, 8, (255, 120, 180), 0.8)
                fa = clamp((0.9 - (t - ts)) / 0.25)
                paste(base, ov, -16, -16, fa)
                paste_c(base, STARS[(GOLD, 56)], fx, fy, fa, 1.0, t * 90)
            # particles bursting out when a chip pops
            if t - ts < 0.6:
                for j in range(8):
                    ang = j * math.pi / 4 + k
                    d = 40 + 160 * ease_out_cubic((t - ts) / 0.6)
                    paste_c(base, STARS[(STAR_COLORS[j % 4], 28)], cx + d * math.cos(ang),
                            cy + d * math.sin(ang) * 0.6, 1 - (t - ts) / 0.6)

    elif name == "info":
        sp_soft.draw(base, t, 0.5)
        k = min(3, int(tl / 1.5))
        tk = tl - k * 1.5
        a = tk / 0.3
        fade = clamp((1.5 - tk) / 0.2) if k < 3 else 1.0
        cw, chh = 960, 300
        card = glass_card(base, (W - cw) // 2, 170, cw, chh, opacity=0.66)
        icon = [icon_hydration, icon_face, icon_collagen, icon_capsule][k](tl)
        card.alpha_composite(icon.resize((240, 240), Image.LANCZOS) if icon.width != 240 else icon,
                             (14, (chh - 240) // 2))
        em = L["benefit_em"][k]
        tx = L["benefits"][k]
        card.alpha_composite(em, (268, 40))
        card.alpha_composite(tx, (268, 40 + em.height + 8))
        # progress dots
        dd = ImageDraw.Draw(card)
        for j in range(4):
            x = cw - 150 + j * 32
            dd.ellipse((x, chh - 38, x + 16, chh - 22), fill=(236, 72, 140, 255) if j == k else (255, 255, 255, 200))
        paste_c(base, card, W / 2, 170 + chh / 2 + 40 * (1 - ease_out_cubic(a)), clamp(a * 2) * fade,
                0.92 + 0.08 * ease_out_back(a))
        Layer(L["foot"], 0.3, 6.0, W / 2, 520, "fade").draw(base, tl)
        if trk:  # soft halo hugging the packaging as the hand moves it
            x0, y0, x1, y1 = trk[2:]
            for j in range(6):
                ang = tl * 1.6 + j * math.pi / 3
                paste_c(base, STARS[(STAR_COLORS[j % 4], 40)], (x0 + x1) / 2 + (x1 - x0) * 0.55 * math.cos(ang),
                        (y0 + y1) / 2 + (y1 - y0) * 0.75 * math.sin(ang), 0.75, 0.9, tl * 60)

    elif name == "hero":
        sp_soft.draw(base, t, 0.7)
        Layer(L["hero1"], 0.15, 6.0, W / 2, 255, "slam").draw(base, tl)
        Layer(L["hero2"], 2.4, 6.0, W / 2, 1420, "slide").draw(base, tl)
        if trk:
            x0, y0, x1, y1 = trk[2:]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            rx, ry = (x1 - x0) * 0.62, (y1 - y0) * 0.9
            for j in range(10):
                ang = tl * 1.2 + j * math.pi / 5
                z = math.sin(ang)
                paste_c(base, STARS[([GOLD, ROSE, (255, 255, 255)][j % 3], 40)], cx + rx * math.cos(ang),
                        cy + ry * z * 0.55, 0.55 + 0.4 * z, 0.7 + 0.3 * z, tl * 50)

    elif name == "close":
        sp_close.draw(base, t, 0.85)
        Layer(L["close1"], 0.15, 7.0, W / 2, 245, "slam").draw(base, tl)
        Layer(L["close2"], 2.2, 7.0, W / 2, 470, "pop").draw(base, tl)
        Layer(L["cta"], 4.2, 7.0, W / 2, 1520, "pop", pulse=0.05).draw(base, tl)
        if tl > 4.4:  # arrow nudging towards the TikTok Shop product link (bottom-left)
            bob = 14 * math.sin(tl * 7)
            ov = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            od.polygon([(60, 110), (15, 50), (45, 50), (45, 8), (75, 8), (75, 50), (105, 50)],
                       fill=TT_YELLOW + (255,), outline=(255, 255, 255, 255))
            ov = glow(ov, 6, (255, 200, 80), 0.8)
            paste_c(base, ov, 230, 1700 + bob, clamp((tl - 4.4) / 0.2))
            paste_c(base, L["bag_yellow"], 120, 1700 - bob * 0.5, clamp((tl - 4.4) / 0.2), 1.0, -8)
        if tl > 6.3:  # finale sparkle burst
            k = (tl - 6.3) / 0.7
            for j in range(14):
                ang = j * 2 * math.pi / 14
                d = 80 + 420 * ease_out_cubic(k)
                paste_c(base, STARS[(STAR_COLORS[j % 4], 56)], W / 2 + d * math.cos(ang),
                        1050 + d * math.sin(ang) * 0.8, 1 - k, 1.0, k * 120)


SFX_CUES = [
    ("sparkle", 0.03, .30), ("ding", 0.05, .22), ("cash", 0.92, .55), ("whoosh", 1.78, .55),
    ("sparkle", 2.1, .30), ("pop", 2.2, .35), ("sparkle", 3.3, .25), ("pop", 4.0, .40), ("whoosh", 5.78, .55),
    ("pop", 6.1, .35), ("pop", 7.0, .45), ("pop", 8.0, .45), ("pop", 9.0, .45), ("pop", 10.0, .45),
    ("whoosh", 10.78, .55), ("ding", 11.1, .22), ("ding", 12.6, .22), ("ding", 14.1, .22), ("ding", 15.6, .22),
    ("whoosh", 16.78, .55), ("sparkle", 17.15, .35), ("sparkle", 17.6, .30), ("pop", 19.4, .35),
    ("sparkle", 20.6, .30), ("whoosh", 22.78, .55), ("cash", 23.15, .45), ("pop", 25.2, .40),
    ("click", 27.2, .60), ("sparkle", 27.25, .30), ("sparkle", 29.3, .35), ("ding", 29.3, .30),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    payday = "--no-payday" not in sys.argv
    src, cmp_path, out = args[:3]
    only = None
    if "--preview" in sys.argv:
        ts = sys.argv[sys.argv.index("--preview") + 1]
        only = {int(float(x) * FPS) for x in ts.split(",")}
        os.makedirs(out, exist_ok=True)
        for fi, im in make_frames(src, cmp_path, payday, only):
            im.save(os.path.join(out, f"p_{fi / FPS:05.2f}.jpg"), quality=88)
        return

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "mix.wav")
        audio.render(SFX_CUES, wav)
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
             "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
             "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
            stdin=subprocess.PIPE)
        for fi, im in make_frames(src, cmp_path, payday):
            enc.stdin.write(im.tobytes())
            if fi % 60 == 0:
                print(f"frame {fi}/{NF}", flush=True)
        enc.stdin.close()
        enc.wait()
        if enc.returncode:
            raise SystemExit("ffmpeg failed")


if __name__ == "__main__":
    main()
