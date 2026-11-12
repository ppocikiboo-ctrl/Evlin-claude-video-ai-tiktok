"""v6 "luxury editorial" edit of the v5 talking-head take, with FAB cards and a full CTA formula.

Reuses the v5 cut and processed voice (../ocheal-micellar-water-v5/build/base.mp4
and voice.wav); only the look, the sound design and the selling structure change:

* Look: plum glass panels with champagne-gold borders, serif letter-by-letter
  reveals, gold rules that draw on, film grain + vignette + warm tint, and an
  RGB-split + gold light streak on every jump cut.
* Sound: a new SFX set (shimmer riser, glass tap, sub impact, shutter, type
  ticks, water drop, ka-ching) over a slower R&B-style bed ducked under her voice.
* Selling: Feature -> Advantage -> Benefit cards timed to what she shows, then a
  CTA sequence: KENAPA (why) -> TINDAKAN (action) -> KENAPA SEKARANG (reason)
  -> HASIL (benefit) -> KALAU TAK (cost of waiting) -> yellow-bag button.

    python3 render.py            # -> output/ocheal_micellar_tiktok_v6.mp4
    python3 render.py --stills   # preview stills -> build/stills/
"""
import argparse
import importlib.util
import math
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from edl import FPS, H, SPEECH_END, TOTAL, W, src_to_out, timeline

ROOT = Path(__file__).resolve().parent
V5_BUILD = ROOT.parent / "ocheal-micellar-water-v5" / "build"


def _load(name, folder):
    spec = importlib.util.spec_from_file_location(name, ROOT.parent / folder / "render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # picks up this folder's edl.py (same API)
    return mod


v1 = _load("kbeauty_v1", "ocheal-micellar-water")
text_img, paste, clamp = v1.text_img, v1.paste, v1.clamp
ease_out_cubic, ease_out_back, ease_in_out, env = v1.ease_out_cubic, v1.ease_out_back, v1.ease_in_out, v1.env
OUT = ROOT / "output" / "ocheal_micellar_tiktok_v6.mp4"

GOLD = (222, 186, 120)
GOLD_L = (245, 222, 170)
PLUM = (48, 18, 40)
WHITE = (255, 255, 255)
CREAM = (255, 244, 228)
TT_YEL = (255, 214, 51)
INK = (30, 18, 24)

SAFE_L, SAFE_R = 60, 880
TOP_L, TOP_R = 50, 1030
TOP_Y = 250
SERIF, SERIF_I, SANS, SANS_B = "Playfair-ExtraBold.ttf", "Playfair-SemiBoldItalic.ttf", "Montserrat-ExtraBold.ttf", "Montserrat-Bold.ttf"
BPM = 96
CUTS = [s for _, s, _, _ in timeline()[1:]]


def at(t_src):
    t = src_to_out(t_src)
    assert t is not None, f"source time {t_src} was cut"
    return t


# ---------------------------------------------------------------- drawing helpers

def plum_panel(w, h, r=30, alpha=215):
    im = Image.new("RGBA", (w * 2, h * 2))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=PLUM + (alpha,))
    d.rounded_rectangle((4, 4, w * 2 - 5, h * 2 - 5), r * 2 - 4, outline=GOLD + (255,), width=4)
    return im.resize((w, h), Image.LANCZOS)


def soft_shadow(im, blur=16, alpha=0.45):
    out = Image.new("RGBA", (im.width + 4 * blur, im.height + 4 * blur))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, (2 * blur, 2 * blur + 10))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (2 * blur, 2 * blur))
    return out


def letter_reveal(im, prog):
    """Mask reveal left->right with a soft gold edge (for serif lines)."""
    if prog >= 1:
        return im
    w = max(1, int(im.width * prog))
    out = im.crop((0, 0, w, im.height))
    full = Image.new("RGBA", im.size)
    full.alpha_composite(out)
    if 0 < prog < 1:
        d = ImageDraw.Draw(full)
        d.line([(w, 6), (w, im.height - 6)], fill=GOLD_L + (220,), width=5)
    return full


@lru_cache(maxsize=None)
def label(text, size=28, fg=GOLD):
    return text_img(text, SANS, size, fg, tracking=4)


# ---------------------------------------------------------------- elements

class SerifHook:
    """Big serif question revealed letter-by-letter, red underline, italic consequence line."""

    def __init__(self, t0, t1, line, sub, y=TOP_Y + 10):
        self.t0, self.t1, self.y = t0, t1, y
        size = 104
        while text_img(line, SERIF, size, WHITE, 5, INK).width > TOP_R - TOP_L:
            size -= 4
        self.line = text_img(line, SERIF, size, WHITE, 5, INK, shadow=0.6)
        self.sub = text_img(sub, SERIF_I, 62, CREAM, 4, INK, shadow=0.6)

    def sfx(self):
        return [("riser", self.t0 - 0.05), ("impact", self.t0 + 0.42), ("tick", self.t0 + 0.6), ("tick", self.t0 + 0.75),
                ("tick", self.t0 + 0.9)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        a = c.t - self.t0
        out = clamp((self.t1 - c.t) / 0.2)
        cx = (TOP_L + TOP_R) / 2
        l1 = letter_reveal(self.line, ease_out_cubic(a / 0.45))
        sc = 1.08 - 0.08 * ease_out_cubic(a / 0.6)
        paste(c.ov, l1, cx, self.y + self.line.height / 2, alpha=out, scale=sc)
        u = ease_out_cubic((a - 0.4) / 0.3)
        if u > 0:
            d = ImageDraw.Draw(c.ov)
            x0 = cx - self.line.width / 2 + 30
            yy = self.y + self.line.height + 4
            d.line([(x0, yy), (x0 + (self.line.width - 60) * u, yy)], fill=(230, 60, 80, int(255 * out)), width=10)
        s = ease_out_cubic((a - 0.55) / 0.5)
        if s > 0:
            paste(c.ov, letter_reveal(self.sub, s), cx, self.y + self.line.height + 30 + self.sub.height / 2, alpha=out)


class GoldLine:
    """Single elegant line on a thin plum strip with gold rules."""

    def __init__(self, t0, t1, text, y, size=60, italic=True, sfx_kind="glass", font=None):
        self.t0, self.t1, self.y, self.kind = t0, t1, y, sfx_kind
        font = font or (SERIF_I if italic else SERIF)
        self.t = text_img(text, font, size, WHITE)
        while self.t.width > SAFE_R - SAFE_L - 80:
            size -= 3
            self.t = text_img(text, font, size, WHITE)

    def sfx(self):
        return [(self.kind, self.t0)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.25, 0.2)
        if v <= 0:
            return
        a = c.t - self.t0
        w, h = self.t.width + 80, self.t.height + 44
        im = plum_panel(w, h, 22, 190)
        im.alpha_composite(letter_reveal(self.t, ease_out_cubic((a - 0.1) / 0.45)), (40, 22))
        paste(c.ov, soft_shadow(im), (SAFE_L + SAFE_R) / 2, self.y + h / 2, alpha=v,
              scale=0.94 + 0.06 * ease_out_cubic(a / 0.3))


class FABCard:
    """Feature -> Advantage -> Benefit: three gold-labelled rows joined by a gold rule that draws down."""

    LABELS = ["FEATURE", "ADVANTAGE", "BENEFIT"]

    def __init__(self, t0, t1, num, rows, y=TOP_Y):
        self.t0, self.t1, self.y = t0, t1, y
        self.num = text_img(f"0{num}", SERIF, 96, GOLD)
        self.rows = []
        for i, txt in enumerate(rows):
            size = 54
            while text_img(txt, SANS_B, size, WHITE).width > TOP_R - TOP_L - 240:
                size -= 2
            self.rows.append((label(self.LABELS[i], 30), text_img(txt, SANS_B, size, WHITE if i < 2 else GOLD_L)))
        self.row_h = 122
        self.w, self.h = TOP_R - TOP_L, 40 + 3 * self.row_h + 20
        self.row_t = [t0 + 0.35 + i * 0.75 for i in range(3)]

    def sfx(self):
        return [("shutter", self.t0)] + [("glass", rt) for rt in self.row_t[:2]] + [("drop", self.row_t[2])]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.25, 0.25)
        if v <= 0:
            return
        im = plum_panel(self.w, self.h, 30, 205)
        im.alpha_composite(self.num, (30, (self.h - self.num.height) // 2))
        d = ImageDraw.Draw(im)
        gx = 160
        y_top = 40 + self.row_h // 2 - 10
        prog = clamp((c.t - self.row_t[0]) / (self.row_t[2] - self.row_t[0] + 0.2))
        y_bot = y_top + 2 * self.row_h * ease_in_out(prog)
        d.line([(gx, y_top), (gx, y_bot)], fill=GOLD + (255,), width=4)
        for i, ((lab, txt), rt) in enumerate(zip(self.rows, self.row_t)):
            a = c.t - rt
            ry = 40 + i * self.row_h
            if a < 0:
                continue
            k = ease_out_cubic(a / 0.35)
            d.ellipse((gx - 11, ry + self.row_h // 2 - 21, gx + 11, ry + self.row_h // 2 + 1), fill=GOLD + (255,))
            im.alpha_composite(lab, (gx + 30, ry + 2))
            im.alpha_composite(letter_reveal(txt, k), (gx + 30, ry + 6 + lab.height))
        u = ease_out_cubic((c.t - self.t0) / 0.4)
        paste(c.ov, soft_shadow(im), (TOP_L + TOP_R) / 2, self.y + self.h / 2 - (1 - u) * 50, alpha=v)


class CTAStep:
    """One CTA beat: gold label + big line, centred in the lower area, with progress dots."""

    def __init__(self, t0, t1, idx, total, lab, line, sfx_kind="glass", y=TOP_Y):
        self.t0, self.t1, self.y, self.idx, self.total, self.kind = t0, t1, y, idx, total, sfx_kind
        self.lab = label(lab, 36)
        size = 76
        while text_img(line, SERIF, size, WHITE).width > TOP_R - TOP_L - 90:
            size -= 3
        self.line = text_img(line, SERIF, size, WHITE)

    def sfx(self):
        return [(self.kind, self.t0 + 0.02)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.18, 0.15)
        if v <= 0:
            return
        a = c.t - self.t0
        w = TOP_R - TOP_L
        h = self.lab.height + self.line.height + 92
        im = plum_panel(w, h, 30, 215)
        im.alpha_composite(self.lab, ((w - self.lab.width) // 2, 24))
        im.alpha_composite(letter_reveal(self.line, ease_out_cubic((a - 0.08) / 0.4)),
                           ((w - self.line.width) // 2, 34 + self.lab.height))
        d = ImageDraw.Draw(im)
        dots_w = (self.total - 1) * 26
        for k in range(self.total):
            x = w / 2 - dots_w / 2 + k * 26
            yy = h - 24
            on = k <= self.idx
            d.ellipse((x - 6, yy - 6, x + 6, yy + 6), fill=(GOLD if on else (120, 90, 110)) + (255,))
        dx = (1 - ease_out_cubic(a / 0.3)) * 90
        paste(c.ov, soft_shadow(im), (TOP_L + TOP_R) / 2 + dx, self.y + h / 2, alpha=v)


class BuyButton:
    def __init__(self, t0, t1, text="TEKAN BEG KUNING 🛍️", y=1360):
        self.t0, self.t1, self.y = t0, t1, y
        self.txt = text_img(text, SANS, 58, INK)
        while self.txt.width > SAFE_R - SAFE_L - 120:
            self.txt = text_img(text, SANS, int(self.txt.height * 0.8), INK)
        self.hand = v1.emoji_img("👇", 110)

    def sfx(self):
        return [("kaching", self.t0 + 0.05)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        a = c.t - self.t0
        w, h = self.txt.width + 110, self.txt.height + 58
        btn = Image.new("RGBA", (w * 2, h * 2))
        d = ImageDraw.Draw(btn)
        d.rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), h, fill=TT_YEL + (255,))
        d.rounded_rectangle((6, 6, w * 2 - 7, h * 2 - 7), h - 6, outline=GOLD + (255,), width=6)
        btn = btn.resize((w, h), Image.LANCZOS)
        btn.alpha_composite(self.txt, (55, 29))
        sw = (a % 1.4) / 0.5
        if sw < 1:
            band = Image.new("RGBA", (w, h))
            bx = int(-60 + sw * (w + 120))
            ImageDraw.Draw(band).polygon([(bx, 4), (bx + 40, 4), (bx + 10, h - 4), (bx - 30, h - 4)], fill=(255, 255, 255, 140))
            mask = Image.new("L", (w, h))
            ImageDraw.Draw(mask).rounded_rectangle((6, 6, w - 6, h - 6), h // 2, fill=255)
            band.putalpha(Image.fromarray(np.minimum(np.asarray(band.getchannel("A")), np.asarray(mask))))
            btn.alpha_composite(band)
        pulse = 1 + 0.045 * max(0, math.sin(a * 6.5))
        cx = (SAFE_L + SAFE_R) / 2
        paste(c.ov, soft_shadow(btn, 14, 0.5), cx, self.y, scale=max(0.05, ease_out_back(a / 0.35, 2)) * pulse)
        paste(c.ov, self.hand, SAFE_L + 60, self.y + h / 2 + 70 + abs(math.sin(a * 6)) * 22)


class GoldStreak:
    """Diagonal champagne light streak across a cut."""

    def __init__(self, t, dur=0.35):
        self.t, self.dur = t, dur
        band = Image.new("L", (300, 1))
        for x in range(300):
            band.putpixel((x, 0), int(255 * math.sin(math.pi * x / 299) ** 3))
        self.band = band.resize((300, int(H * 2.2)))

    def draw(self, c):
        u = (c.t - (self.t - self.dur / 2)) / self.dur
        if not (0 <= u <= 1):
            return
        im = Image.new("RGBA", self.band.size, GOLD_L + (0,))
        im.putalpha(self.band.point(lambda v: int(v * 0.6 * math.sin(math.pi * u))))
        im = im.rotate(-25, Image.BICUBIC, expand=True)
        paste(c.ov, im, -400 + u * (W + 800), H / 2)


# ---------------------------------------------------------------- look

rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
VIGNETTE = (1 - 0.28 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1)).astype(np.float32)
del yy, xx


def finish(img, fi):
    """Warm tint, vignette, film grain, and RGB split in the 3 frames around each cut."""
    a = np.asarray(img, dtype=np.float32)
    a[..., 0] *= 1.03
    a[..., 2] *= 0.97
    a *= VIGNETTE[..., None]
    g = GRAIN[fi % len(GRAIN)]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)
    a += g[..., None] * 5.0
    t = fi / FPS
    for ct in CUTS:
        k = (t - ct) * FPS
        if -2 <= k < 3:
            s = int(12 * (1 - abs(k + 0.5) / 3.5))
            if s > 0:
                a[..., 0] = np.roll(a[..., 0], s, axis=1)
                a[..., 2] = np.roll(a[..., 2], -s, axis=1)
            break
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def camera(fi):
    t = fi / FPS
    tl = timeline()
    if t >= SPEECH_END:
        z0 = tl[-1][3][4][1]
        z = z0 * (1 + 0.12 * ease_in_out((t - SPEECH_END) / (TOTAL - SPEECH_END)))
    else:
        for n, s, e, seg in tl:
            if s <= t < e:
                break
        z0, z1 = seg[4]
        z = z0 + (z1 - z0) * ease_in_out((t - s) / (e - s))
        z *= 1 - 0.05 * (1 - ease_out_cubic((t - s) / 0.25))  # pull-out settle (v5 punched in)
        z = max(z, 1.06)
    hw, hh = W / (2 * z), H / (2 * z)
    return z, W / 2, clamp(H * 0.45, hh, H - hh)


# ---------------------------------------------------------------- the script

def build_elements():
    P = v1.Particles
    els = [GoldStreak(t) for t in CUTS]

    # 1. HOOK: the problem and its consequence
    els.append(SerifHook(0.0, 2.7, "Tidur dengan makeup?", "esok pagi kulit rasa berat & kusam 😩"))
    els.append(GoldLine(3.4, 6.6, "ni cara aku tanggalkan makeup 👇", 1200, size=56))

    # 2. FAB cards, timed to what she shows
    els.append(FABCard(at(6.8), at(10.45), 1, [
        "Hyaluronic Acid + Rose",
        "Angkat makeup tanpa gosok kuat",
        "Tak pedih, kulit terasa lembut",
    ]))
    els.append(P(at(6.8), at(8.5), "sparkle", (520, 700, 1000, 1300), 12, life=(0.5, 1.0), size=(14, 26),
                 vel=((-20, 20), (-40, 10)), seed=61))
    els.append(FABCard(at(10.6), at(15.45), 2, [
        "Formula tak berminyak",
        "Tak melekit lepas lap",
        "Terus sambung skincare seterusnya",
    ]))
    els.append(FABCard(at(15.55), at(19.2), 3, [
        "Botol pam 300ML",
        "Tekan sekali, kapas terus basah",
        "Rutin malam cepat & kemas",
    ]))

    # 3. Result while she talks
    els.append(GoldLine(at(19.9), at(22.55), "hasilnya: kulit terasa lembut & segar 🤍", 1200, size=54, sfx_kind="drop"))
    els.append(P(at(19.9), at(22.55), "sparkle", (250, 520, 830, 1000), 7, life=(0.6, 1.2), size=(14, 26),
                 vel=((-10, 10), (-30, 0)), seed=62))

    # 4. CTA formula: why -> action -> why now -> benefit -> cost of waiting -> button
    t = at(22.6)
    beats = [
        ("KENAPA", "Sisa makeup buat kulit rasa berat", "glass"),
        ("TINDAKAN", "Tekan beg kuning, checkout O’CHEAL", "shutter"),
        ("KENAPA SEKARANG", "Malam ni pun kau nak tanggal makeup 🌙", "glass"),
        ("HASILNYA", "Esok bangun, kulit terasa lembut ✨", "drop"),
        ("KALAU TAK", "Malam ni tidur dengan sisa makeup lagi 😩", "impact"),
    ]
    step = (TOTAL - 1.6 - t) / len(beats)
    for i, (lab, line, k) in enumerate(beats):
        els.append(CTAStep(t + i * step, t + (i + 1) * step - 0.03, i, len(beats), lab, line, k))
    els.append(GoldLine(TOTAL - 1.6, TOTAL + 1, "O’CHEAL Micellar Water 300ML", TOP_Y + 20, size=56, sfx_kind="glass", font=SANS))
    els.append(BuyButton(TOTAL - 1.55, TOTAL + 1, y=1370))
    els.append(P(SPEECH_END, TOTAL + 1, "sparkle", (80, 300, 1000, 1000), 10, life=(0.6, 1.2), size=(12, 24),
                 vel=((-10, 10), (-30, 0)), seed=63))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    for t in CUTS:
        cues.append(("riser", t - 0.35))
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


# ---------------------------------------------------------------- sound

def make_fx():
    SR = v1.SR
    T = v1._t
    fx = {}
    d = 0.4
    t = T(d)
    noise = v1.noise(d, 71)
    shimmer = sum(np.sin(2 * np.pi * f * t * (1 + t)) for f in (1760, 2637, 3520)) / 3
    fx["riser"] = 0.22 * (v1.bandpass_sweep(noise, 800, 7000) * 0.6 + shimmer * 0.4) * (t / d) ** 2
    t = T(0.6)
    fx["glass"] = 0.26 * (np.sin(2 * np.pi * 2349 * t) + 0.5 * np.sin(2 * np.pi * 2349 * 2.41 * t)
                          + 0.3 * np.sin(2 * np.pi * 2349 * 3.93 * t)) * v1.adsr(len(t), 0.001, 0.12)
    t = T(0.7)
    f = np.linspace(90, 32, len(t))
    fx["impact"] = 0.7 * np.sin(2 * np.pi * np.cumsum(f) / SR) * v1.adsr(len(t), 0.002, 0.22)
    sh = np.zeros(int(0.16 * SR))
    for st in (0, int(0.07 * SR)):
        n = int(0.025 * SR)
        sh[st:st + n] += v1.noise(0.025, 72 + st)[:n] * np.linspace(1, 0, n) ** 2
    fx["shutter"] = 0.4 * sh
    t = T(0.03)
    fx["tick"] = 0.22 * v1.noise(0.03, 73) * v1.adsr(len(t), 0.0005, 0.004)
    t = T(0.25)
    f = np.linspace(700, 1900, len(t))
    fx["drop"] = 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * v1.adsr(len(t), 0.001, 0.05)
    t = T(1.2)
    ka = v1.noise(0.04, 74) * np.linspace(1, 0, int(0.04 * SR)) * 0.6
    ching = (v1.bell(2637, 1.2, 0.35) + 0.8 * v1.bell(3951, 1.2, 0.3))
    k = np.zeros(len(t))
    k[:len(ka)] += ka
    off = int(0.06 * SR)
    k[off:] += ching[:len(k) - off]
    fx["kaching"] = 0.3 * k
    return fx


def make_audio():
    SR = v1.SR
    chords = [[50, 53, 57, 60, 64], [46, 50, 53, 57, 60], [48, 52, 55, 59, 62], [45, 48, 52, 55, 59]]  # Dm9 Bbmaj7 C Am7
    music = v1.make_music(TOTAL, bpm=BPM, chords=[c[:4] for c in chords])
    n = int((TOTAL + 0.05) * SR)
    music = music[:n]
    music /= np.abs(music).max() + 1e-9
    tail = int(1.2 * SR)
    music[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 1.5
    fx = make_fx()
    sfx = np.zeros((n, 2))
    for kind, t in cue_list(build_elements()):
        s = fx[kind]
        st = int(t * SR)
        seg = sfx[st:st + len(s)]
        seg += s[:len(seg), None]

    def write(path, x):
        pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())

    (ROOT / "build").mkdir(exist_ok=True)
    write(ROOT / "build" / "music.wav", music * 0.5)
    write(ROOT / "build" / "sfx.wav", sfx * 0.6)
    mix = ROOT / "build" / "mix.wav"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-i", str(V5_BUILD / "voice.wav"), "-i", str(ROOT / "build" / "music.wav"), "-i", str(ROOT / "build" / "sfx.wav"),
        "-filter_complex",
        "[0]aformat=channel_layouts=stereo,apad,asplit=2[v][key];"
        "[1]volume=-14dB[m];"
        "[m][key]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=400:makeup=1[md];"
        "[2]volume=-8dB[fx];"
        "[v][md][fx]amix=inputs=3:duration=longest:normalize=0,atrim=0:" + f"{TOTAL:.3f}",
        "-ar", "48000", str(mix)], check=True)
    return mix


# ---------------------------------------------------------------- main

def render_frame(fi, img, els):
    z, cx, cy = camera(fi)
    img = v1.apply_camera(img, z, cx, cy)
    img = v1.bloom(img, 0.08)
    img = finish(img, fi)
    frame = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    c = v1.Ctx(fi, frame, ov, (z, cx, cy))
    for el in els:
        el.draw(c)
    return Image.alpha_composite(frame, ov).convert("RGB")


def all_frames(base):
    last, fi = None, 0
    for img in v1.frames_from(base):
        last = img
        yield fi, img
        fi += 1
    while fi < round(TOTAL * FPS):
        yield fi, last
        fi += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    els = build_elements()
    base = V5_BUILD / "base.mp4"
    if args.stills:
        outdir = ROOT / "build" / "stills"
        outdir.mkdir(parents=True, exist_ok=True)
        want = {round(t * FPS) for t in [0.5, 1.4, 2.4, 5.0, 7.4, 8.8, 11.5, 13.2, 15.0, 16.4, 17.0, 20.0,
                                          19.6, 21.0, 22.4, 23.8, 25.0, 26.5, 27.3]}
        for fi, img in all_frames(base):
            if fi in want:
                render_frame(fi, img, els).save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
        return
    mix = make_audio()
    OUT.parent.mkdir(exist_ok=True)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(mix),
        "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)
    for fi, img in all_frames(base):
        enc.stdin.write(render_frame(fi, img, els).tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{round(TOTAL * FPS)}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
