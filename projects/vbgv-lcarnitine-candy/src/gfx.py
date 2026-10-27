"""Drawing helpers: styled text, cards, pills, light effects and particles."""
import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import DEEP_PURPLE, FONT_BOLD, GOLD, GOLD_HI, H, LAVENDER, W, WHITE
from icons import icon

# ---------------------------------------------------------------- easing

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ease_in_out(p):
    p = clamp(p)
    return 3 * p * p - 2 * p * p * p


def ease_out_back(p, k=1.70158):
    p = clamp(p)
    q = p - 1
    return 1 + (k + 1) * q ** 3 + k * q ** 2


def window(t, t_in, t_out, fade_in=0.3, fade_out=0.2):
    """0..1 visibility envelope for an element living between t_in and t_out."""
    if t < t_in or t >= t_out:
        return 0.0
    a = clamp((t - t_in) / fade_in) if fade_in else 1.0
    b = clamp((t_out - t) / fade_out) if fade_out else 1.0
    return min(a, b)


# ---------------------------------------------------------------- text

@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(str(path), size)


def _gradient_gold(h):
    col = np.linspace(0, 1, h)[:, None]
    hi, lo = np.array(GOLD_HI, float), np.array(GOLD, float) * 0.92
    return (hi * (1 - col) + lo * col)


def text_layer(lines, font_path, size, max_width=900, line_gap=0.12, stroke=4,
               glow=LAVENDER, glow_radius=16, glow_strength=0.85, shadow=0.55, tracking=0):
    """Render centred multi-line text.

    `lines` is a list of lines; each line is a list of (text, color) runs.
    color may be an RGB tuple, "gold" for a champagne-gold gradient, or a run
    may be ("@iconname", None) to place an emoji-style icon inline. A color of
    None (text) or "hide" (icon) keeps the layout but draws nothing, which is
    how the highlight-only passes line up with the full text.
    The font shrinks until the widest line fits `max_width`.
    """
    while True:
        f = font(font_path, size)
        isz = int(size * 1.0)
        gap = int(size * 0.22)

        def run_w(txt):
            if txt.startswith("@"):
                return isz + gap
            return f.getlength(txt) + tracking * len(txt)

        widths = [sum(run_w(t) for t, _ in line) for line in lines]
        if max(widths) <= max_width or size <= 20:
            break
        size = int(size * 0.96)

    asc, desc = f.getmetrics()
    lh = int((asc + desc) * (1 + line_gap))
    pad = glow_radius * 3 + stroke + 8
    lw = int(max(widths)) + pad * 2
    lhh = lh * len(lines) + pad * 2
    fill_rgb = np.zeros((lhh, lw, 3), np.float32)
    fill_a = Image.new("L", (lw, lhh), 0)
    stroke_a = Image.new("L", (lw, lhh), 0)
    icons = []
    da, ds = ImageDraw.Draw(fill_a), ImageDraw.Draw(stroke_a)
    for li, line in enumerate(lines):
        x = pad + (max(widths) - widths[li]) / 2
        y = pad + li * lh
        for txt, color in line:
            if txt.startswith("@"):
                if color != "hide":
                    icons.append((txt[1:], int(x), int(y + (asc + desc - isz) / 2), isz))
                x += isz + gap
                continue
            m = Image.new("L", (lw, lhh), 0)
            md = ImageDraw.Draw(m)
            cx = x
            for ch in txt if tracking else [txt]:
                if color is not None:
                    md.text((cx, y), ch, font=f, fill=255)
                    da.text((cx, y), ch, font=f, fill=255)
                    ds.text((cx, y), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
                cx += f.getlength(ch) + tracking
            mm = np.asarray(m, np.float32)[..., None] / 255
            if color is None:  # measured but not drawn (used for highlight passes)
                pass
            elif color == "gold":
                grad = np.zeros((lhh, 3), np.float32)
                grad[int(y): int(y) + asc + desc] = _gradient_gold(asc + desc)[: max(0, lhh - int(y))]
                fill_rgb = fill_rgb * (1 - mm) + grad[:, None, :] * mm
            else:
                fill_rgb = fill_rgb * (1 - mm) + np.array(color, np.float32) * mm
            x += run_w(txt)

    out = Image.new("RGBA", (lw, lhh), (0, 0, 0, 0))
    if shadow:
        sh = stroke_a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * shadow))
        out.paste(Image.new("RGBA", out.size, (12, 0, 30, 255)), (0, 6), sh)
    if glow:
        g = stroke_a.filter(ImageFilter.GaussianBlur(glow_radius)).point(lambda v: min(255, int(v * glow_strength * 1.4)))
        out.alpha_composite(_tinted(g, glow))
    if stroke:
        out.alpha_composite(_tinted(stroke_a, DEEP_PURPLE))
    fill = Image.fromarray(np.clip(fill_rgb, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    fill.putalpha(fill_a)
    out.alpha_composite(fill)
    for name, ix, iy, isz in icons:
        out.alpha_composite(icon(name, isz), (ix, iy))
    return out


def _tinted(alpha, rgb):
    im = Image.new("RGBA", alpha.size, rgb + (0,))
    im.putalpha(alpha)
    return im


# ---------------------------------------------------------------- panels

def panel(w, h, radius=36, fill=(40, 12, 80, 175), outline="gold", outline_w=4, glow=(160, 110, 255)):
    pad = 40
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    box = (pad, pad, pad + w, pad + h)
    g = Image.new("L", im.size, 0)
    ImageDraw.Draw(g).rounded_rectangle(box, radius, outline=255, width=outline_w + 6)
    im.alpha_composite(_tinted(g.filter(ImageFilter.GaussianBlur(14)), glow))
    body = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle(box, radius, fill=fill)
    # soft top sheen for a glassy look
    sheen = Image.new("L", im.size, 0)
    ImageDraw.Draw(sheen).rounded_rectangle((pad, pad, pad + w, pad + h // 2), radius, fill=34)
    body.alpha_composite(_tinted(sheen, (255, 255, 255)))
    im.alpha_composite(body)
    # outline: gold on top fading to lavender at the bottom
    ol = Image.new("L", im.size, 0)
    ImageDraw.Draw(ol).rounded_rectangle(box, radius, outline=255, width=outline_w)
    grad = np.zeros((im.size[1], im.size[0], 3), np.float32)
    col = np.linspace(0, 1, im.size[1])[:, None]
    top = np.array(GOLD_HI if outline == "gold" else LAVENDER, np.float32)
    bot = np.array(LAVENDER if outline == "gold" else GOLD, np.float32)
    grad[:] = (top * (1 - col) + bot * col)[:, None, :]
    olim = Image.fromarray(grad.astype(np.uint8), "RGB").convert("RGBA")
    olim.putalpha(ol)
    im.alpha_composite(olim)
    return im, pad


def card(icon_name, label, width=760, height=118, size=50):
    im, pad = panel(width, height, radius=height // 2)
    isz = int(height * 0.6)
    im.alpha_composite(icon(icon_name, isz), (pad + 34, pad + (height - isz) // 2))
    t = text_layer([[(label, WHITE)]], FONT_BOLD, size, max_width=width - isz - 110,
                   stroke=0, glow=None, shadow=0.0)
    tx = pad + 34 + isz + 24 - (t.size[0] - _ink_w(t)) // 2
    im.alpha_composite(t, (max(0, tx), pad + (height - t.size[1]) // 2))
    return im


def _ink_w(img):
    box = img.getbbox()
    return box[2] - box[0] if box else img.size[0]


def pill(lines, font_path, size, pad_x=48, pad_y=26, fill=(40, 12, 80, 190), outline="gold", text_kwargs=None):
    t = text_layer(lines, font_path, size, **(text_kwargs or dict(stroke=0, glow=None, shadow=0.0)))
    bx = t.getbbox()
    tw, th = bx[2] - bx[0], bx[3] - bx[1]
    w, h = tw + pad_x * 2, th + pad_y * 2
    im, pad = panel(w, h, radius=min(h // 2, 44), fill=fill, outline=outline)
    im.alpha_composite(t, (pad + pad_x - bx[0], pad + pad_y - bx[1]))
    return im


# ---------------------------------------------------------------- compositing

def place(canvas, sprite, cx, cy, scale=1.0, alpha=1.0, blur_dx=0.0, rotate=0.0):
    """Alpha-composite `sprite` centred on (cx, cy) with transform and fade."""
    if alpha <= 0.003 or scale <= 0.01:
        return
    sp = sprite
    if abs(scale - 1) > 1e-3:
        sp = sp.resize((max(1, int(sp.size[0] * scale)), max(1, int(sp.size[1] * scale))), Image.BICUBIC)
    if rotate:
        sp = sp.rotate(rotate, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = sp.getchannel("A").point(lambda v: int(v * alpha))
        sp = sp.copy()
        sp.putalpha(a)
    if abs(blur_dx) > 1:
        # cheap directional motion blur: average shifted copies
        n = int(min(24, max(4, abs(blur_dx) / 6)))
        acc = Image.new("RGBA", (sp.size[0] + int(abs(blur_dx)) + 2, sp.size[1]), (0, 0, 0, 0))
        base = np.zeros((acc.size[1], acc.size[0], 4), np.float32)
        arr = np.asarray(sp, np.float32)
        for k in range(n):
            off = int(abs(blur_dx) * k / (n - 1))
            base[:, off: off + sp.size[0]] += arr / n
        sp = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGBA")
        cx -= abs(blur_dx) / 2 * (1 if blur_dx > 0 else -1)
    x, y = int(round(cx - sp.size[0] / 2)), int(round(cy - sp.size[1] / 2))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(sp.size[0], canvas.size[0] - x), min(sp.size[1], canvas.size[1] - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    canvas.alpha_composite(sp, (x + sx0, y + sy0), (sx0, sy0, sx1, sy1))


# light fields are computed at half resolution then upscaled
LW, LH = W // 2, H // 2
_Y, _X = np.mgrid[0:LH, 0:LW].astype(np.float32)
_X *= 2
_Y *= 2


def radial(cx, cy, rx, ry=None):
    ry = ry or rx
    d2 = ((_X - cx) / rx) ** 2 + ((_Y - cy) / ry) ** 2
    return np.exp(-d2 * 2.2)


def sweep(pos, angle_deg=-28, width=90):
    a = math.radians(angle_deg)
    proj = _X * math.cos(a) + _Y * math.sin(a)
    return np.exp(-((proj - pos) / width) ** 2)


def rays(ox, oy, phase, n=9, sharp=6.0, reach=1700):
    ang = np.arctan2(_Y - oy, _X - ox)
    r = np.hypot(_X - ox, _Y - oy)
    beams = (0.5 + 0.5 * np.cos(ang * n * 2 + phase)) ** sharp
    beams *= (0.5 + 0.5 * np.cos(ang * 5 - phase * 0.6))
    return beams * np.exp(-(r / reach) ** 2) * np.clip(r / 200, 0, 1)


def vgrad(top_alpha, bottom_alpha, y0=0, y1=H):
    col = np.clip((_Y - y0) / max(1, (y1 - y0)), 0, 1)
    return top_alpha * (1 - col) + bottom_alpha * col


def upscale(field):
    im = Image.fromarray(np.clip(field * 255, 0, 255).astype(np.uint8), "L").resize((W, H), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255


def add_light(arr, field, color, strength):
    """Screen-blend a monochrome light field (0..1, half-res) onto arr (float RGB)."""
    if strength <= 0.003:
        return arr
    f = upscale(field * strength)[..., None]
    c = np.array(color, np.float32)[None, None, :]
    return 255 - (255 - arr) * (1 - f * c / 255)


def darken(arr, field, color, strength):
    """Tint/darken with a field: lerp toward `color`."""
    if strength <= 0.003:
        return arr
    f = upscale(field * strength)[..., None]
    return arr * (1 - f) + np.array(color, np.float32) * f


# ---------------------------------------------------------------- particles

class Particles:
    """Soft lavender bokeh dots drifting upward, plus twinkling sparkles."""

    def __init__(self, n=70, seed=7):
        rnd = random.Random(seed)
        self.dots = [dict(x=rnd.uniform(0, W), y=rnd.uniform(0, H), vy=rnd.uniform(30, 110),
                          sway=rnd.uniform(10, 40), ph=rnd.uniform(0, 6.28), r=rnd.choice([10, 14, 20, 28, 36]),
                          a=rnd.uniform(0.25, 0.8), gold=rnd.random() < 0.25) for _ in range(n)]
        self.sprites = {}
        for r in (10, 14, 20, 28, 36):
            for gold in (False, True):
                s = r * 4
                im = Image.new("L", (s, s), 0)
                ImageDraw.Draw(im).ellipse((s / 2 - r / 2, s / 2 - r / 2, s / 2 + r / 2, s / 2 + r / 2), fill=255)
                im = im.filter(ImageFilter.GaussianBlur(r / 3))
                self.sprites[(r, gold)] = _tinted(im.point(lambda v: min(255, v * 2)), GOLD_HI if gold else LAVENDER)

    def draw(self, canvas, t, amount):
        if amount <= 0.01:
            return
        for d in self.dots:
            y = (d["y"] - d["vy"] * t) % (H + 100) - 50
            x = d["x"] + math.sin(t * 1.3 + d["ph"]) * d["sway"]
            tw = 0.6 + 0.4 * math.sin(t * 3 + d["ph"] * 2)
            place(canvas, self.sprites[(d["r"], d["gold"])], x, y, alpha=amount * d["a"] * tw)


def twinkle(canvas, t, points, t0, size=60, color="white", period=0.9):
    """Sparkle stars that grow, spin and fade around given points."""
    for i, (x, y) in enumerate(points):
        local = (t - t0 - i * 0.13) % period
        p = local / period
        s = math.sin(math.pi * p)
        if s <= 0.02 or t < t0:
            continue
        name = "sparkle"
        sp = icon(name, size) if color == "white" else _gold_sparkle(size)
        place(canvas, sp, x, y, scale=0.3 + 0.9 * s, alpha=s, rotate=p * 90)


@lru_cache(maxsize=None)
def _gold_sparkle(size):
    from icons import sparkle
    return sparkle(size, GOLD_HI)
