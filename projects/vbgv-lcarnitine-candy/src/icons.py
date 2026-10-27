"""Emoji-style icons drawn as vectors, so the render needs no emoji font.

Each function returns an RGBA image of `size` x `size` pixels. Icons are
drawn at 4x and downsampled for clean anti-aliasing.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersampling factor


def _canvas(size):
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), s


def _finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


def _heart_points(cx, cy, r, n=160):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * r / 17, cy - y * r / 17))
    return pts


def _star4(cx, cy, r, thin=0.28):
    pts = []
    for i in range(8):
        a = math.pi / 2 * (i // 2) + (math.pi / 4 if i % 2 else 0) - math.pi / 2
        rr = r if i % 2 == 0 else r * thin
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def heart(size, color=(155, 93, 229)):
    img, d, s = _canvas(size)
    d.polygon(_heart_points(s / 2, s * 0.52, s * 0.47), fill=color + (255,))
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse((s * 0.2, s * 0.22, s * 0.38, s * 0.36), fill=(255, 255, 255, 120))
    img.alpha_composite(hi.filter(ImageFilter.GaussianBlur(s * 0.02)))
    return _finish(img, size)


def sparkles(size, color=(255, 214, 110)):
    img, d, s = _canvas(size)
    d.polygon(_star4(s * 0.42, s * 0.56, s * 0.40), fill=color + (255,))
    d.polygon(_star4(s * 0.80, s * 0.22, s * 0.17), fill=color + (255,))
    d.polygon(_star4(s * 0.82, s * 0.80, s * 0.12), fill=color + (255,))
    return _finish(img, size)


def sparkle(size, color=(255, 255, 255)):
    img, d, s = _canvas(size)
    d.polygon(_star4(s / 2, s / 2, s * 0.48, thin=0.18), fill=color + (255,))
    return _finish(img, size)


def blossom(size):
    img, d, s = _canvas(size)
    petal = (247, 168, 205, 255)
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        px, py = s / 2 + math.cos(a) * s * 0.22, s / 2 + math.sin(a) * s * 0.22
        r = s * 0.22
        d.ellipse((px - r, py - r, px + r, py + r), fill=petal)
    r = s * 0.12
    d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=(255, 206, 84, 255))
    return _finish(img, size)


def weary(size):
    img, d, s = _canvas(size)
    d.ellipse((s * 0.03, s * 0.03, s * 0.97, s * 0.97), fill=(255, 204, 77, 255))
    w = int(s * 0.045)
    ink = (102, 69, 0, 255)
    # squeezed eyes ">" "<"
    d.line([(s * 0.24, s * 0.36), (s * 0.38, s * 0.44), (s * 0.24, s * 0.50)], fill=ink, width=w, joint="curve")
    d.line([(s * 0.76, s * 0.36), (s * 0.62, s * 0.44), (s * 0.76, s * 0.50)], fill=ink, width=w, joint="curve")
    # worried brows
    d.line([(s * 0.20, s * 0.26), (s * 0.38, s * 0.20)], fill=ink, width=w)
    d.line([(s * 0.80, s * 0.26), (s * 0.62, s * 0.20)], fill=ink, width=w)
    # open frowning mouth
    d.chord((s * 0.30, s * 0.60, s * 0.70, s * 0.92), 180, 360, fill=ink)
    return _finish(img, size)


def fries(size):
    img, d, s = _canvas(size)
    stick = (255, 205, 60, 255)
    edge = (226, 160, 20, 255)
    for k, (x, top, tilt) in enumerate([(0.30, 0.10, -0.05), (0.40, 0.04, -0.02), (0.50, 0.08, 0.0),
                                        (0.60, 0.03, 0.02), (0.70, 0.12, 0.05)]):
        x0 = s * (x - 0.05)
        d.polygon([(x0 + s * tilt, s * top), (x0 + s * (0.09 + tilt), s * top),
                   (x0 + s * 0.09, s * 0.6), (x0, s * 0.6)], fill=stick, outline=edge)
    d.polygon([(s * 0.18, s * 0.40), (s * 0.82, s * 0.40), (s * 0.74, s * 0.96), (s * 0.26, s * 0.96)],
              fill=(226, 45, 55, 255))
    d.chord((s * 0.36, s * 0.30, s * 0.64, s * 0.58), 0, 180, fill=(190, 25, 40, 255))
    return _finish(img, size)


def shopping_bag(size):
    img, d, s = _canvas(size)
    w = int(s * 0.06)
    d.arc((s * 0.32, s * 0.06, s * 0.68, s * 0.46), 180, 360, fill=(170, 110, 20, 255), width=w)
    d.line([(s * 0.32 + w / 2, s * 0.26), (s * 0.32 + w / 2, s * 0.36)], fill=(170, 110, 20, 255), width=w)
    d.line([(s * 0.68 - w / 2, s * 0.26), (s * 0.68 - w / 2, s * 0.36)], fill=(170, 110, 20, 255), width=w)
    d.rounded_rectangle((s * 0.14, s * 0.30, s * 0.86, s * 0.95), radius=s * 0.08, fill=(255, 196, 40, 255))
    d.rectangle((s * 0.14, s * 0.30, s * 0.86, s * 0.40), fill=(255, 220, 110, 255))
    return _finish(img, size)


def briefcase(size, color=(255, 255, 255)):
    img, d, s = _canvas(size)
    w = int(s * 0.07)
    d.rounded_rectangle((s * 0.34, s * 0.14, s * 0.66, s * 0.38), radius=s * 0.06, outline=color + (255,), width=w)
    d.rounded_rectangle((s * 0.08, s * 0.30, s * 0.92, s * 0.88), radius=s * 0.1, fill=color + (255,))
    d.rectangle((s * 0.08, s * 0.52, s * 0.92, s * 0.56), fill=(0, 0, 0, 0))
    return _finish(img, size)


def sun(size, color=(255, 255, 255)):
    img, d, s = _canvas(size)
    r = s * 0.2
    d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=color + (255,))
    w = int(s * 0.07)
    for k in range(8):
        a = k * math.pi / 4
        d.line([(s / 2 + math.cos(a) * s * 0.3, s / 2 + math.sin(a) * s * 0.3),
                (s / 2 + math.cos(a) * s * 0.45, s / 2 + math.sin(a) * s * 0.45)], fill=color + (255,), width=w)
    return _finish(img, size)


def arrow_down(size, color=(255, 228, 160)):
    img, d, s = _canvas(size)
    w = int(s * 0.14)
    d.line([(s * 0.5, s * 0.1), (s * 0.5, s * 0.78)], fill=color + (255,), width=w)
    d.polygon([(s * 0.16, s * 0.52), (s * 0.84, s * 0.52), (s * 0.5, s * 0.94)], fill=color + (255,))
    return _finish(img, size)


ICONS = {
    "weary": weary,
    "fries": fries,
    "sparkles": sparkles,
    "sparkle": sparkle,
    "heart": heart,
    "blossom": blossom,
    "bag": shopping_bag,
    "briefcase": briefcase,
    "sun": sun,
    "arrow": arrow_down,
}


@lru_cache(maxsize=None)
def icon(name, size):
    return ICONS[name](size)
