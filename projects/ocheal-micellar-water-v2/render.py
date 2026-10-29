"""Step 3 (v2 "sticker pop" style): graphics, sound design and final encode.

Same pipeline as ../ocheal-micellar-water/render.py, with a different look:
bold tape-strip type that slams in with screen shake, die-cut stickers,
hand-drawn scribble + arrow tracked to the bottle, a 300ML burst badge, an
animated checklist, stripe-wipe transitions and a yellow-bag CTA.
Text helpers, sprites and the synth engine are reused from v1.

    python3 render.py            # full render -> output/ocheal_micellar_tiktok_v2.mp4
    python3 render.py --stills   # preview stills -> build/stills/
"""
import argparse
import importlib.util
import json
import math
import random
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from edl import FPS, H, TOTAL, W, seg_end, seg_start, timeline

ROOT = Path(__file__).resolve().parent
V1 = ROOT.parent / "ocheal-micellar-water" / "render.py"
_spec = importlib.util.spec_from_file_location("kbeauty_v1", V1)
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)  # v1 picks up this folder's edl.py (same API)

text_img, paste, clamp = v1.text_img, v1.paste, v1.clamp
ease_out_cubic, ease_out_back, ease_in_out, env = v1.ease_out_cubic, v1.ease_out_back, v1.ease_in_out, v1.env
OUT = ROOT / "output" / "ocheal_micellar_tiktok_v2.mp4"

HOT = (255, 46, 126)
YEL = (255, 222, 60)
INK = (34, 18, 30)
WHITE = (255, 255, 255)

SAFE_L, SAFE_R = 60, 880        # lower half: keep clear of the right-rail buttons
TOP_L, TOP_R = 50, 1030         # top info zone (y < 900) can use the full width
TOP_Y = 255

SLAMS = []  # times that trigger a screen shake


# ---------------------------------------------------------------- sprites

def hard_shadow(im, off=(9, 11), alpha=0.38):
    out = Image.new("RGBA", (im.width + off[0] + 4, im.height + off[1] + 4))
    sh = Image.new("RGBA", im.size, INK + (0,))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, off)
    out.alpha_composite(im)
    return out


@lru_cache(maxsize=None)
def tape(text, size, bg, fg, angle=0.0, font="Montserrat-ExtraBold.ttf", max_w=TOP_R - TOP_L):
    """Text on a torn tape strip, hard shadow, slight tilt."""
    while True:
        t = text_img(text, font, size, fg)
        if t.width + 70 <= max_w:
            break
        size -= 3
    pw, ph = t.width + 70, t.height + 40
    rng = random.Random(text)
    pts = [(0, 0), (pw, 0)]
    for i in range(1, 7):  # torn right edge
        pts.append((pw - rng.uniform(0, 12), ph * i / 7))
    pts += [(pw, ph), (0, ph)]
    for i in range(6, 0, -1):  # torn left edge
        pts.append((rng.uniform(0, 12), ph * i / 7))
    strip = Image.new("RGBA", (pw * 2, ph * 2))
    ImageDraw.Draw(strip).polygon([(x * 2, y * 2) for x, y in pts], fill=bg + (255,))
    strip = strip.resize((pw, ph), Image.LANCZOS)
    strip.alpha_composite(t, ((pw - t.width) // 2, (ph - t.height) // 2))
    im = hard_shadow(strip)
    return im.rotate(angle, Image.BICUBIC, expand=True) if angle else im


@lru_cache(maxsize=None)
def sticker(text, size, fill, outline=WHITE, width=13, font="Montserrat-ExtraBold.ttf", angle=0.0, max_w=TOP_R - TOP_L):
    """Die-cut sticker lettering: thick white border + hard shadow."""
    while True:
        t = text_img(text, font, size, fill, stroke=4, stroke_fill=fill)
        if t.width + 2 * width + 20 <= max_w:
            break
        size -= 3
    pad = width + 6
    base = Image.new("RGBA", (t.width + 2 * pad, t.height + 2 * pad))
    base.alpha_composite(t, (pad, pad))
    a = base.getchannel("A").filter(ImageFilter.MaxFilter(2 * (width // 2) + 1))
    a = a.filter(ImageFilter.MaxFilter(2 * (width // 2) + 1)).filter(ImageFilter.GaussianBlur(1))
    border = Image.new("RGBA", base.size, outline + (255,))
    border.putalpha(a)
    border.alpha_composite(base)
    im = hard_shadow(border)
    return im.rotate(angle, Image.BICUBIC, expand=True) if angle else im


@lru_cache(maxsize=None)
def burst(text, r=120):
    s = r * 2 + 40
    im = Image.new("RGBA", (s * 2, s * 2))
    pts = []
    for i in range(32):
        rr = r * (1.0 if i % 2 == 0 else 0.8)
        a = math.pi * 2 * i / 32
        pts.append((s + rr * 2 * math.cos(a), s + rr * 2 * math.sin(a)))
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=YEL + (255,), outline=INK + (255,))
    d.polygon(pts, outline=INK + (255,), width=8)
    im = im.resize((s, s), Image.LANCZOS)
    t = text_img(text, "Montserrat-ExtraBold.ttf", int(r * 0.52), INK)
    im.alpha_composite(t, ((s - t.width) // 2, (s - t.height) // 2))
    return hard_shadow(im)


@lru_cache(maxsize=None)
def check_box(size, on):
    s = size * 2
    im = Image.new("RGBA", (s, s))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, s - 4, s - 4), s // 4, fill=HOT + (255,) if on else WHITE + (255,), outline=INK + (255,), width=8)
    return im.resize((size, size), Image.LANCZOS)


def draw_check(im, x, y, size, prog):
    """Animated check-mark stroke inside a box at (x, y)."""
    if prog <= 0:
        return
    pts = [(x + size * 0.22, y + size * 0.52), (x + size * 0.43, y + size * 0.72), (x + size * 0.80, y + size * 0.28)]
    d = ImageDraw.Draw(im)
    l1 = math.dist(pts[0], pts[1])
    l2 = math.dist(pts[1], pts[2])
    L = (l1 + l2) * prog
    if L <= l1:
        u = L / l1
        d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * u, pts[0][1] + (pts[1][1] - pts[0][1]) * u)],
               fill=WHITE, width=int(size * 0.14), joint="curve")
    else:
        u = (L - l1) / l2
        d.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * u, pts[1][1] + (pts[2][1] - pts[1][1]) * u)],
               fill=WHITE, width=int(size * 0.14), joint="curve")


# ---------------------------------------------------------------- tracking + camera

def load_track():
    p = ROOT / "build" / "track.json"
    if p.exists():
        v1.TRACK.clear()
        v1.TRACK.update({int(k): v for k, v in json.loads(p.read_text()).items()})


def shake(t):
    dx = dy = 0.0
    for ts in SLAMS:
        a = t - ts
        if 0 <= a < 0.3:
            k = 16 * math.exp(-a * 14)
            dx += k * math.sin(a * 95)
            dy += k * math.cos(a * 77)
    return dx, dy


def camera(fi):
    t = fi / FPS
    for n, s, e, seg in timeline():
        if s <= t < e:
            break
    z0, z1 = seg[4]
    u = (t - s) / (e - s)
    z = z0 + (z1 - z0) * (ease_out_cubic(u * 2.5) if n == "hook" else ease_in_out(u))
    z *= 1 + 0.07 * (1 - ease_out_cubic((t - s) / 0.2))  # punch at every cut
    cx, cy = W / 2, H * 0.47
    tr = v1.cap_at(fi)
    if tr and tr[2] > 0.5:
        cx = cx * 0.65 + tr[0] * 0.35
        cy = cy * 0.7 + (tr[1] + 300) * 0.3
    dx, dy = shake(t)
    z = max(z, 1.03)  # headroom for the shake
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(cx + dx / z, hw, W - hw)
    cy = clamp(cy + dy / z, hh, H - hh)
    return z, cx, cy


# ---------------------------------------------------------------- elements

def slam_draw(c, im, x, y, t0, t1, rot=0.0):
    """Slam-in (big -> 1 with overshoot), slide-out to the left."""
    a = c.t - t0
    if a < 0 or c.t > t1:
        return
    u = a / 0.22
    sc = 1.0 + 0.8 * (1 - ease_out_back(u, 1.3)) if u < 1 else 1.0
    out = clamp((t1 - c.t) / 0.16)
    dx = -(1 - ease_out_cubic(out)) * 260
    paste(c.ov, im, x + dx, y, alpha=clamp(a / 0.07) * out, scale=max(0.05, sc), rot=rot)


class Stack:
    """Lines (tapes / stickers) that slam in one after another."""

    def __init__(self, t0, t1, items, y, x=None, align="m", slam=True):
        self.t0, self.t1, self.items, self.y, self.slam = t0, t1, items, y, slam
        self.x = x if x is not None else (TOP_L + TOP_R) / 2
        self.align = align
        if slam:
            SLAMS.extend(t0 + d for _, d in items[:2])

    def sfx(self):
        return [("thud", self.t0 + d) for _, d in self.items]

    def draw(self, c):
        y = self.y
        for im, d in self.items:
            x = self.x
            if self.align == "l":
                x = self.x + im.width / 2
            slam_draw(c, im, x, y + im.height / 2, self.t0 + d, self.t1)
            y += im.height - 18


class Burst:
    def __init__(self, t0, t1, text, off=(170, 130), r=118):
        self.t0, self.t1, self.off, self.im = t0, t1, off, burst(text, r)

    def sfx(self):
        return [("pop", self.t0)]

    def draw(self, c):
        cap = c.cap()
        if cap is None or not (self.t0 <= c.t <= self.t1):
            return
        u = (c.t - self.t0) / 0.3
        v = env(c.t, self.t0, self.t1, 0.1, 0.15)
        x = clamp(cap[0] + self.off[0], 140, SAFE_R - 40)
        paste(c.ov, self.im, x, cap[1] + self.off[1], alpha=v,
              scale=max(0.05, ease_out_back(u, 2.2)) * (1 + 0.04 * math.sin(c.t * 9)), rot=8 * math.sin(c.t * 2.2))


class Scribble:
    """Hand-drawn yellow loop drawn on around the tracked bottle."""

    def __init__(self, t0, t1, rx=215, ry=455, dy=340, seed=3):
        self.t0, self.t1, self.rx, self.ry, self.dy = t0, t1, rx, ry, dy
        rng = random.Random(seed)
        self.n = [rng.uniform(-1, 1) for _ in range(6)]

    def sfx(self):
        return [("scribble", self.t0)]

    def draw(self, c):
        cap = c.cap()
        if cap is None or not (self.t0 <= c.t <= self.t1):
            return
        prog = ease_out_cubic((c.t - self.t0) / 0.45)
        v = env(c.t, self.t0, self.t1, 0.05, 0.15)
        cx, cy = cap[0], cap[1] + self.dy * c.z / 1.05
        rx, ry = self.rx * c.z / 1.05, self.ry * c.z / 1.05
        turns = 1.12
        pts = []
        steps = int(120 * prog) + 2
        for i in range(steps):
            th = -2.2 + 2 * math.pi * turns * prog * i / (steps - 1)
            wob = 1 + 0.045 * math.sin(th * 3 + self.n[0] * 3) + 0.03 * math.sin(th * 5 + self.n[1] * 3) + 0.04 * th / 6
            pts.append((cx + rx * wob * math.cos(th), cy + ry * wob * math.sin(th)))
        d = ImageDraw.Draw(c.ov)
        d.line([(x + 6, y + 7) for x, y in pts], fill=INK + (int(110 * v),), width=15, joint="curve")
        d.line(pts, fill=YEL + (int(255 * v),), width=13, joint="curve")


class Arrow:
    """Hand-drawn curved arrow from a fixed point to the tracked bottle."""

    def __init__(self, t0, t1, start, to_off=(-150, 120)):
        self.t0, self.t1, self.start, self.to_off = t0, t1, start, to_off

    def draw(self, c):
        cap = c.cap()
        if cap is None or not (self.t0 <= c.t <= self.t1):
            return
        prog = ease_out_cubic((c.t - self.t0) / 0.35)
        v = env(c.t, self.t0, self.t1, 0.05, 0.15)
        sx, sy = self.start
        ex, ey = cap[0] + self.to_off[0], cap[1] + self.to_off[1]
        mx, my = (sx + ex) / 2 - 120, (sy + ey) / 2 - 40
        pts = []
        n = max(2, int(40 * prog))
        for i in range(n):
            u = prog * i / (n - 1)
            pts.append(((1 - u) ** 2 * sx + 2 * (1 - u) * u * mx + u * u * ex,
                        (1 - u) ** 2 * sy + 2 * (1 - u) * u * my + u * u * ey))
        d = ImageDraw.Draw(c.ov)
        d.line([(x + 5, y + 6) for x, y in pts], fill=INK + (int(110 * v),), width=12, joint="curve")
        d.line(pts, fill=WHITE + (int(255 * v),), width=11, joint="curve")
        if prog > 0.97:
            (x1, y1), (x2, y2) = pts[-3], pts[-1]
            ang = math.atan2(y2 - y1, x2 - x1)
            for s in (-1, 1):
                a = ang + math.pi + s * 0.55
                d.line([(x2, y2), (x2 + 46 * math.cos(a), y2 + 46 * math.sin(a))], fill=WHITE + (int(255 * v),), width=11)


class Checklist:
    def __init__(self, t0, t1, header, rows, row_times, y=TOP_Y):
        self.t0, self.t1, self.y, self.row_times = t0, t1, y, row_times
        self.header = tape(header, 64, YEL, INK, -2.5)
        self.rows = [tape(r, 66, WHITE, INK, 0) for r in rows]
        SLAMS.append(t0)

    def sfx(self):
        return [("thud", self.t0)] + [("pop", rt) for rt in self.row_times] + [("ting", rt + 0.2) for rt in self.row_times]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        slam_draw(c, self.header, TOP_L + self.header.width / 2 + 30, self.y + self.header.height / 2, self.t0, self.t1)
        y = self.y + self.header.height + 6
        out = clamp((self.t1 - c.t) / 0.16)
        for row, rt in zip(self.rows, self.row_times):
            a = c.t - rt
            if a >= 0:
                u = ease_out_back(a / 0.3, 1.5)
                box = 100
                card = Image.new("RGBA", (row.width + box + 30, max(row.height, box + 14)))
                on = a > 0.18
                card.alpha_composite(hard_shadow(check_box(box, on)), (0, (card.height - box) // 2 - 4))
                draw_check(card, 0, (card.height - box) // 2 - 4, box, clamp((a - 0.18) / 0.22))
                card.alpha_composite(row, (box + 22, (card.height - row.height) // 2))
                x = TOP_L + 40 + card.width / 2 + (1 - clamp(u)) * -380
                paste(c.ov, card, x - (1 - out) * 260, y + card.height / 2, alpha=clamp(a / 0.1) * out)
                y += card.height + 4


class EmojiPop:
    def __init__(self, t0, t1, ch, x, y, size=150, follow_cap=False):
        self.t0, self.t1, self.x, self.y, self.follow = t0, t1, x, y, follow_cap
        self.im = hard_shadow(v1.emoji_img(ch, size), (6, 8), 0.3)

    def sfx(self):
        return [("pop", self.t0)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        x, y = self.x, self.y
        if self.follow:
            cap = c.cap()
            if cap is None:
                return
            x, y = cap[0] + self.x, cap[1] + self.y
        a = c.t - self.t0
        sc = ease_out_back(a / 0.3, 2.4)
        bob = math.sin(a * 6) * 10
        paste(c.ov, self.im, x, y + bob, alpha=env(c.t, self.t0, self.t1, 0.05, 0.15), scale=max(0.05, sc),
              rot=math.sin(a * 5) * 12)


class StripeWipe:
    """Diagonal pink/yellow/white stripes sweep across a cut."""

    def __init__(self, t, dur=0.36):
        self.t, self.dur = t, dur

    def sfx(self):
        return [("whoosh", self.t - self.dur / 2 - 0.05)]

    def draw(self, c):
        u = (c.t - (self.t - self.dur / 2)) / self.dur
        if not (0 <= u <= 1):
            return
        d = ImageDraw.Draw(c.ov)
        span = W + H * 0.6
        for i, col in enumerate([HOT, YEL, WHITE, HOT]):
            lag = i * 0.09
            head = ease_in_out(clamp((u - lag) / 0.55)) * (span + 400) - 200
            tail = ease_in_out(clamp((u - lag - 0.3) / 0.55)) * (span + 400) - 200
            if head <= tail:
                continue
            sk = H * 0.6
            d.polygon([(tail - sk, H), (head - sk, H), (head, 0), (tail, 0)], fill=col + (255,))


class LightSweep:
    def __init__(self, t0, dur=0.9):
        self.t0, self.dur = t0, dur
        band = Image.new("L", (360, 1))
        for x in range(360):
            band.putpixel((x, 0), int(255 * math.sin(math.pi * x / 359) ** 2))
        self.band = band.resize((360, H * 2))

    def draw(self, c):
        u = (c.t - self.t0) / self.dur
        if not (0 <= u <= 1):
            return
        im = Image.new("RGBA", self.band.size, (255, 245, 250, 0))
        im.putalpha(self.band.point(lambda v: int(v * 0.34 * math.sin(math.pi * u))))
        im = im.rotate(-22, Image.BICUBIC, expand=True)
        paste(c.ov, im, -300 + u * (W + 600), H / 2)


class FlashCut:
    def __init__(self, t):
        self.t = t

    def draw(self, c):
        u = (c.t - self.t) / 0.12
        if 0 <= u <= 1:
            c.ov.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(140 * (1 - u)))))


class CTA:
    def __init__(self, t0, t1, ask, button, y=1320):
        self.t0, self.t1, self.y = t0, t1, y
        self.ask = tape(ask, 64, HOT, WHITE, -2.5, max_w=SAFE_R - SAFE_L)
        txt = text_img(button, "Montserrat-ExtraBold.ttf", 60, INK)
        while txt.width > SAFE_R - SAFE_L - 100:
            txt = text_img(button, "Montserrat-ExtraBold.ttf", int(txt.height * 0.8), INK)
        w, h = txt.width + 100, txt.height + 56
        btn = Image.new("RGBA", (w * 2, h * 2))
        ImageDraw.Draw(btn).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), h, fill=YEL + (255,), outline=INK + (255,), width=12)
        btn = btn.resize((w, h), Image.LANCZOS)
        btn.alpha_composite(txt, ((w - txt.width) // 2, (h - txt.height) // 2))
        self.btn, self.w, self.h = hard_shadow(btn, (10, 12), 0.6), w, h
        self.finger = hard_shadow(v1.emoji_img("👇", 120), (6, 8), 0.3)
        SLAMS.append(t0)

    def sfx(self):
        return [("thud", self.t0), ("pop", self.t0 + 0.35), ("chime", self.t0 + 0.4)]

    def draw(self, c):
        if c.t < self.t0:
            return
        cx = (SAFE_L + SAFE_R) / 2
        slam_draw(c, self.ask, cx, self.y - self.h / 2 - self.ask.height / 2 + 6, self.t0, self.t1 + 5)
        a = c.t - self.t0 - 0.3
        if a < 0:
            return
        pulse = 1 + 0.05 * max(0, math.sin(a * 7))
        paste(c.ov, self.btn, cx, self.y + 30, scale=max(0.05, ease_out_back(a / 0.35, 2)) * pulse)
        # light sweep on the button
        sw = (a % 1.3) / 0.5
        if sw < 1:
            band = Image.new("RGBA", (self.w, self.h))
            bx = int(-60 + sw * (self.w + 120))
            ImageDraw.Draw(band).polygon([(bx, 6), (bx + 46, 6), (bx + 12, self.h - 6), (bx - 34, self.h - 6)], fill=(255, 255, 255, 150))
            mask = Image.new("L", (self.w, self.h))
            ImageDraw.Draw(mask).rounded_rectangle((8, 8, self.w - 8, self.h - 8), self.h // 2, fill=255)
            band.putalpha(Image.fromarray(np.minimum(np.asarray(band.getchannel("A")), np.asarray(mask))))
            paste(c.ov, band, cx - 5, self.y + 24, scale=pulse)
        if a > 0.4:
            paste(c.ov, self.finger, SAFE_L + 70, self.y + self.h + 90 + abs(math.sin(a * 6)) * 26, scale=0.9)


# ---------------------------------------------------------------- the script

def build_elements():
    S, E = seg_start, seg_end
    P = v1.Particles
    els = [v1.Vignette()]

    # 1. HOOK: x pedas + kulit terasa lembut, over the real wipe on lips/cheek
    els.append(Stack(0.0, E("hook") - 0.02, [
        (tape("MICELLAR WATER", 80, YEL, INK, -3), 0.05),
        (sticker("X PEDAS! 😍", 150, HOT, angle=2), 0.42),
        (tape("KULIT TERASA LEMBUT ✨", 62, WHITE, HOT, -1.5), 1.0),
    ], y=TOP_Y - 10))
    els.append(P(0.42, 0.9, "sparkle", (120, 300, 960, 700), 30, life=(0.4, 0.8), size=(16, 30), vel=((-180, 180), (-140, 80)), seed=21))
    els.append(StripeWipe(S("intro")))

    # 2. PRODUCT: name, 300ML burst, scribble + arrow on the tracked bottle
    t, e = S("intro"), E("intro")
    els.append(Stack(t + 0.12, e - 0.02, [
        (sticker("O’CHEAL", 116, HOT, font="Playfair-ExtraBold.ttf", angle=-3, max_w=640), 0.0),
        (tape("MICELLAR WATER", 58, INK, WHITE, 1.5, max_w=620), 0.25),
    ], y=TOP_Y, x=TOP_L + 20, align="l"))
    els.append(Scribble(t + 0.45, e - 0.02))
    els.append(Arrow(t + 0.6, e - 0.02, (330, 610)))
    els.append(Burst(t + 0.8, e - 0.02, "300ML", off=(200, 40)))
    els.append(Stack(t + 1.25, e - 0.02, [(tape("🌹 HYALURONIC ACID + ROSE", 50, WHITE, HOT, -1, max_w=SAFE_R - SAFE_L), 0.0)],
                     y=1330, x=(SAFE_L + SAFE_R) / 2, slam=False))

    # 3. EYES + LIPS (one beat across two real shots)
    t, e = S("eyes"), E("lips")
    els.append(FlashCut(t))
    els.append(Stack(t + 0.05, e - 0.02, [
        (tape("BOLEH GUNA KAT", 62, INK, WHITE, -2), 0.0),
        (sticker("MATA & BIBIR", 120, HOT, angle=1.5), 0.25),
    ], y=TOP_Y))
    els.append(EmojiPop(t + 0.5, E("eyes") + 0.05, "👀", 860, 640, 140))
    els.append(EmojiPop(S("lips") + 0.05, e - 0.02, "💋", 860, 640, 140))
    els.append(FlashCut(S("lips")))
    els.append(Stack(t + 0.6, e - 0.02, [(tape("Bantu tanggalkan solekan", 52, WHITE, INK, 0, font="Montserrat-Bold.ttf",
                                               max_w=SAFE_R - SAFE_L), 0.0)], y=1360, x=(SAFE_L + SAFE_R) / 2, slam=False))

    # 4. WHY I LIKE IT: animated checklist over the real wipes
    t, e = S("wipe"), E("wipe2")
    els.append(FlashCut(t))
    els.append(Checklist(t + 0.05, e - 0.02, "KENAPA SUKA? 💗", ["X PEDAS", "X BERMINYAK", "X RASA KERING"],
                         [t + 0.35, t + 1.05, t + 1.75]))
    els.append(FlashCut(S("wipe2")))
    els.append(StripeWipe(S("pads")))

    # 5. USED PADS: gentle wipe, no scrubbing (text low, the pads fill the top)
    t, e = S("pads"), E("pads")
    els.append(Stack(t + 0.15, e - 0.02, [
        (tape("CUKUP LAP", 64, YEL, INK, -2, max_w=SAFE_R - SAFE_L), 0.0),
        (sticker("LEMBUT-LEMBUT ✨", 92, HOT, angle=1.5, max_w=SAFE_R - SAFE_L), 0.25),
        (tape("Tak perlu gosok kuat", 46, WHITE, INK, 0, font="Montserrat-Bold.ttf", max_w=SAFE_R - SAFE_L), 0.6),
    ], y=1190, x=(SAFE_L + SAFE_R) / 2))
    els.append(P(t + 0.3, e, "sparkle", (150, 250, 930, 900), 12, life=(0.5, 1.0), size=(14, 26), vel=((-20, 20), (-30, 10)), seed=22))

    # 6. SOFT SKIN payoff on the clean face
    t, e = S("soft"), E("soft")
    els.append(FlashCut(t))
    els.append(Stack(t + 0.08, t + 2.1, [
        (tape("KULIT TERASA", 70, WHITE, INK, -2), 0.0),
        (sticker("LEMBUT & SEGAR 💗", 116, HOT, angle=1.5), 0.25),
    ], y=TOP_Y))
    els.append(LightSweep(t + 0.35, 1.0))
    els.append(LightSweep(t + 2.3, 1.0))
    els.append(P(t + 0.3, e, "sparkle", (250, 620, 830, 1150), 10, life=(0.6, 1.2), size=(14, 28), vel=((-10, 10), (-30, 0)), seed=23))
    els.append(P(t + 0.5, t + 2.0, "heart", (180, 1200, 860, 1380), 5, life=(1.1, 1.5), size=(22, 36), vel=((-30, 30), (-220, -140)), seed=24))
    els.append(Stack(t + 2.15, e - 0.02, [
        (tape("💧 DENGAN HYALURONIC ACID", 56, YEL, INK, -1.5), 0.0),
        (tape("Bantu kekalkan kelembapan", 52, WHITE, HOT, 1, font="Montserrat-Bold.ttf"), 0.3),
    ], y=TOP_Y))
    els.append(StripeWipe(S("cta")))

    # 7. CTA on the slow-motion bottle close-up
    t, e = S("cta"), E("cta")
    els.append(Stack(t + 0.12, e + 1, [
        (sticker("O’CHEAL", 110, HOT, font="Playfair-ExtraBold.ttf", angle=-3, max_w=640), 0.0),
        (tape("MICELLAR WATER 300ML", 54, INK, WHITE, 1.5, max_w=660), 0.2),
    ], y=TOP_Y, x=TOP_L + 20, align="l"))
    els.append(Scribble(t + 0.3, e + 1, rx=230, ry=470, dy=360, seed=7))
    els.append(CTA(t + 0.75, e, "NAK KULIT LEMBUT? 😍", "CHECK BEG KUNING 🛍️"))
    els.append(P(t + 0.3, e + 1, "sparkle", (-200, -150, 200, 700), 14, life=(0.5, 1.0), size=(12, 26), vel=((-20, 20), (-40, 20)),
                 follow_cap=True, seed=25))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    for n, s, e, seg in timeline()[1:]:
        cues.append(("swish", s - 0.08))
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


# ---------------------------------------------------------------- audio

def make_fx():
    fx = v1.make_sfx()
    SR = v1.SR
    t = v1._t(0.32)
    f = np.linspace(150, 48, len(t))
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * v1.adsr(len(t), 0.001, 0.09)
    thud += 0.35 * v1.noise(0.32, 31) * v1.adsr(len(t), 0.0005, 0.012)
    fx["thud"] = 0.6 * thud
    sc = np.zeros(int(0.45 * SR))
    rng = np.random.default_rng(32)
    for k in range(5):  # marker scratches
        st = int(k * 0.085 * SR)
        n = int(0.06 * SR)
        burst_ = v1.bandpass_sweep(rng.standard_normal(n + 4096), 2500 + 600 * k, 4200) [:n] * np.hanning(n)
        sc[st:st + n] += burst_
    fx["scribble"] = 0.16 * sc
    return fx


def make_music():
    # brighter, faster bed: I - V - vi - IV in F major, 126 BPM
    chords = [[53, 57, 60, 64], [60, 64, 67, 74], [62, 65, 69, 72], [58, 62, 65, 69]]
    return v1.make_music(TOTAL, bpm=126, chords=chords)


# ---------------------------------------------------------------- main

def render_frame(fi, img, els):
    z, cx, cy = camera(fi)
    img = v1.apply_camera(img, z, cx, cy)
    img = v1.bloom(img, 0.08)
    frame = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    c = v1.Ctx(fi, frame, ov, (z, cx, cy))
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
        want = {round(t * FPS) for t in [0.3, 0.7, 1.4, 2.2, 3.3, 4.6, 5.8, 7.0, 8.2, 9.4, 10.6, 11.9, 12.8,
                                          14.0, 15.6, 16.6, 17.8, 18.8, 19.8]}
        for fi, img in enumerate(v1.frames_from(base)):
            if fi in want:
                render_frame(fi, img, els).save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
        return
    wav = ROOT / "build" / "audio.wav"
    v1.make_audio(cue_list(els), wav, music=make_music(), fx=make_fx())
    OUT.parent.mkdir(exist_ok=True)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(wav),
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)
    for fi, img in enumerate(v1.frames_from(base)):
        enc.stdin.write(render_frame(fi, img, els).tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{round(TOTAL * FPS)}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
