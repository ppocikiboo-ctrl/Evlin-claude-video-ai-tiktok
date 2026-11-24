"""v7 "aqua countdown" edit of the v5 talking-head take: 3 SEBAB (3 reasons) listicle.

Reuses the v5 cut and processed voice (../ocheal-micellar-water-v5/build/base.mp4
and voice.wav). New in this version:

* Format: a "3 SEBAB" countdown (3 -> 2 -> 1) timed to what she shows, then a
  result bubble, a bonus fact and a save + yellow-bag CTA.
* Look: water theme. Big countdown numerals fill with rising water (wavy surface),
  ripple rings, rising bubbles, frosted bubble panels in Fredoka/Baloo, a fresh
  cool grade with lifted aqua shadows, and a "water rises" wipe on every cut.
* Sound: drip, bubble plop, splash, sonar bloop and a water whoosh over a brighter
  122 BPM bed, ducked under her voice.

    python3 render.py            # -> output/ocheal_micellar_tiktok_v7.mp4
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
OUT = ROOT / "output" / "ocheal_micellar_tiktok_v7.mp4"

AQUA = (62, 198, 255)
DEEP = (24, 110, 230)
NAVY = (18, 40, 90)
PINK = (255, 92, 150)
WHITE = (255, 255, 255)
TT_YEL = (255, 214, 51)

SAFE_L, SAFE_R = 60, 880
TOP_L, TOP_R = 50, 1030
TOP_Y = 250
ROUND, ROUND_SB, NUM, SANS_B = "Fredoka-Bold.ttf", "Fredoka-SemiBold.ttf", "Baloo2-ExtraBold.ttf", "Montserrat-Bold.ttf"
BPM = 122
CUTS = [s for _, s, _, _ in timeline()[1:]]
WIPE = 9  # frames


def at(t_src):
    t = src_to_out(t_src)
    assert t is not None, f"source time {t_src} was cut"
    return t


# ---------------------------------------------------------------- sprites

def bubble_panel(w, h, r=56, alpha=232, tail=None):
    """Frosted white bubble with an aqua rim; optional speech tail ('bl' / 'br')."""
    s = 2
    im = Image.new("RGBA", (w * s, (h + 50) * s))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=WHITE + (alpha,), outline=AQUA + (255,), width=5 * s)
    if tail:
        x = 120 if tail == "bl" else w - 160
        d.polygon([(x * s, (h - 4) * s), ((x + 70) * s, (h - 4) * s), ((x + 10) * s, (h + 46) * s)], fill=WHITE + (alpha,))
        d.line([((x + 70) * s, (h - 2) * s), ((x + 10) * s, (h + 46) * s), (x * s, (h - 2) * s)], fill=AQUA + (255,), width=5 * s)
    return im.resize((w, h + 50), Image.LANCZOS)


def soft_shadow(im, blur=14, alpha=0.3, col=(10, 40, 90)):
    out = Image.new("RGBA", (im.width + 4 * blur, im.height + 4 * blur))
    sh = Image.new("RGBA", im.size, col + (0,))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, (2 * blur, 2 * blur + 12))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (2 * blur, 2 * blur))
    return out


@lru_cache(maxsize=None)
def numeral_parts(n, size):
    mask = text_img(str(n), NUM, size, WHITE).getchannel("A")
    outline = text_img(str(n), NUM, size, (0, 0, 0, 0), 10, WHITE)
    return mask, outline


def water_numeral(n, size, fill, t):
    """Numeral that fills with water up to `fill` (0..1), with a moving wavy surface."""
    mask, outline = numeral_parts(n, size)
    w, h = outline.size
    mw, mh = mask.size
    ox, oy = (w - mw) // 2, (h - mh) // 2
    yy, xx = np.mgrid[0:mh, 0:mw]
    level = mh * (1 - fill * 1.04)
    surf = level + 10 * np.sin(xx / 26 + t * 9) + 5 * np.sin(xx / 11 - t * 13)
    water = (yy > surf).astype(np.float32)
    grad = np.clip((yy - surf) / max(1, mh * 0.6), 0, 1)
    rgb = np.zeros((mh, mw, 3), np.float32)
    for k in range(3):
        rgb[..., k] = AQUA[k] * (1 - grad) + DEEP[k] * grad
    foam = ((yy > surf) & (yy < surf + 7)).astype(np.float32)
    rgb = rgb * (1 - foam[..., None]) + 255 * foam[..., None]
    a_mask = np.asarray(mask, np.float32) / 255
    glass = 0.28 * a_mask
    alpha = np.maximum(glass, water * a_mask)
    rgb = rgb * water[..., None] + 255 * (1 - water[..., None])
    num = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (w, h))
    out.alpha_composite(num, (ox, oy))
    out.alpha_composite(outline)
    return out


# ---------------------------------------------------------------- elements

class Hook:
    """Water-filled '3' + 'SEBAB AKU SAYANG / MICELLAR WATER NI 💧'."""

    def __init__(self, t0, t1, y=TOP_Y):
        self.t0, self.t1, self.y = t0, t1, y
        self.l1 = text_img("SEBAB AKU SAYANG", ROUND, 74, WHITE, 8, NAVY, shadow=0.5)
        self.l2 = text_img("MICELLAR WATER NI 💧", ROUND, 74, AQUA, 8, WHITE, shadow=0.5)

    def sfx(self):
        return [("bloop", self.t0 + 0.05), ("splash", self.t0 + 0.15), ("plop", self.t0 + 0.55), ("plop", self.t0 + 0.8)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        a = c.t - self.t0
        out = clamp((self.t1 - c.t) / 0.2)
        num = water_numeral(3, 330, ease_out_cubic(a / 0.7), c.t)
        paste(c.ov, soft_shadow(num), TOP_L + 130, self.y + 170, alpha=out, scale=max(0.05, ease_out_back(a / 0.35, 1.8)))
        x = TOP_L + 270
        for i, im in enumerate((self.l1, self.l2)):
            k = ease_out_back((a - 0.45 - i * 0.22) / 0.3, 1.6)
            if k > 0:
                paste(c.ov, im, x + (1 - clamp(k)) * 120, self.y + 70 + i * 110, alpha=clamp(k) * out, anchor="lm",
                      scale=min(1.0, (TOP_R - x) / im.width))


class Reason:
    """Countdown card: water-filled numeral + title + subtitle on a frosted bubble panel."""

    def __init__(self, t0, t1, n, title, sub, y=TOP_Y):
        self.t0, self.t1, self.n, self.y = t0, t1, n, y
        avail = TOP_R - TOP_L - 300
        size = 66
        while text_img(title, ROUND, size, NAVY).width > avail and size > 46:
            size -= 2
        self.title = text_img(title, ROUND, size, NAVY)
        if self.title.width > avail:  # still too long: two lines
            words = title.split(" ")
            half = len(words) // 2
            l1 = text_img(" ".join(words[:half + 1]), ROUND, size, NAVY)
            l2 = text_img(" ".join(words[half + 1:]), ROUND, size, NAVY)
            t = Image.new("RGBA", (max(l1.width, l2.width), l1.height + l2.height - 10))
            t.alpha_composite(l1, (0, 0))
            t.alpha_composite(l2, (0, l1.height - 10))
            self.title = t
        size = 40
        while text_img(sub, SANS_B, size, DEEP).width > avail and size > 28:
            size -= 2
        self.sub = text_img(sub, SANS_B, size, DEEP)
        self.tag = text_img(f"SEBAB #{n}", ROUND, 34, WHITE)

    def sfx(self):
        return [("whooshw", self.t0 - 0.1), ("bloop", self.t0 + 0.05), ("drip", self.t0 + 0.45), ("plop", self.t0 + 0.7)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.2, 0.2)
        if v <= 0:
            return
        a = c.t - self.t0
        w = TOP_R - TOP_L
        h = max(300, self.title.height + self.sub.height + 120)
        panel = bubble_panel(w, h)
        pill = Image.new("RGBA", (self.tag.width + 36, self.tag.height + 16))
        ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, pill.height - 1), pill.height // 2, fill=PINK + (255,))
        pill.alpha_composite(self.tag, (18, 8))
        panel.alpha_composite(pill, (290, 28))
        k = ease_out_cubic((a - 0.3) / 0.35)
        ty = 38 + pill.height
        tt = self.title.crop((0, 0, max(1, int(self.title.width * k)), self.title.height))
        panel.alpha_composite(tt, (290, ty))
        k2 = ease_out_cubic((a - 0.5) / 0.35)
        st = self.sub.crop((0, 0, max(1, int(self.sub.width * k2)), self.sub.height))
        panel.alpha_composite(st, (290, ty + self.title.height + 8))
        u = ease_out_back(a / 0.4, 1.3)
        cx = (TOP_L + TOP_R) / 2
        paste(c.ov, soft_shadow(panel), cx, self.y + (h + 50) / 2 - (1 - clamp(u)) * 80, alpha=v,
              scale=max(0.05, 0.9 + 0.1 * clamp(u)))
        num = water_numeral(self.n, 280, ease_out_cubic(a / 0.8), c.t)
        nx, ny = TOP_L + 140, self.y + h / 2 + 8
        paste(c.ov, soft_shadow(num), nx, ny, alpha=v, scale=max(0.05, ease_out_back(a / 0.35, 2.0)),
              rot=(1 - clamp(a / 0.4)) * -20)
        d = ImageDraw.Draw(c.ov)  # ripple rings from the numeral
        for k3 in range(3):
            ph = (a * 0.9 - k3 * 0.25)
            if 0 < ph < 1:
                r = 120 + ph * 260
                d.ellipse((nx - r, ny - r * 0.35, nx + r, ny + r * 0.35), outline=WHITE + (int(170 * (1 - ph) * v),), width=4)


class Callout:
    """Speech-bubble callout in the lower area."""

    def __init__(self, t0, t1, text, y=1150, tail="bl", size=58, sfx_kind="plop"):
        self.t0, self.t1, self.y, self.tail, self.kind = t0, t1, y, tail, sfx_kind
        # top-zone callouts may use the full width; lower ones stay clear of the right rail
        self.l, self.r = (TOP_L, TOP_R) if y < 900 else (SAFE_L, SAFE_R)
        while text_img(text, ROUND, size, NAVY).width > self.r - self.l - 90:
            size -= 2
        self.t = text_img(text, ROUND, size, NAVY)

    def sfx(self):
        return [(self.kind, self.t0)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.15, 0.15)
        if v <= 0:
            return
        a = c.t - self.t0
        w, h = self.t.width + 90, self.t.height + 50
        im = bubble_panel(w, h, 46, 238, self.tail)
        im.alpha_composite(self.t, (45, 25))
        sc = ease_out_back(a / 0.35, 2.2)
        wob = 1 + 0.015 * math.sin(a * 7)
        paste(c.ov, soft_shadow(im), (self.l + self.r) / 2, self.y + h / 2, alpha=v, scale=max(0.05, sc) * wob)


class SaveCTA:
    """Final CTA: question, yellow-bag button, save prompt, pointing hand."""

    def __init__(self, t0, t1, y=1190):
        self.t0, self.t1, self.y = t0, t1, y
        size = 64
        while text_img("NAK KULIT TERASA LEMBUT? 😍", ROUND, size, WHITE, 8, NAVY).width > SAFE_R - SAFE_L:
            size -= 2
        self.q = text_img("NAK KULIT TERASA LEMBUT? 😍", ROUND, size, WHITE, 8, NAVY, shadow=0.5)
        self.btn_t = text_img("TEKAN BEG KUNING 🛍️", ROUND, 62, NAVY)
        self.save = text_img("🔖 simpan video ni untuk rutin malam kau", SANS_B, 36, WHITE, 5, NAVY)
        self.hand = v1.emoji_img("👇", 110)

    def sfx(self):
        return [("splash", self.t0), ("chime", self.t0 + 0.45), ("plop", self.t0 + 0.95)]

    def draw(self, c):
        if c.t < self.t0:
            return
        a = c.t - self.t0
        cx = (SAFE_L + SAFE_R) / 2
        paste(c.ov, self.q, cx, self.y, scale=max(0.05, ease_out_back(a / 0.3, 1.8)))
        b = a - 0.4
        if b > 0:
            w, h = self.btn_t.width + 110, self.btn_t.height + 54
            btn = Image.new("RGBA", (w * 2, h * 2))
            ImageDraw.Draw(btn).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), h, fill=TT_YEL + (255,), outline=WHITE + (255,), width=10)
            btn = btn.resize((w, h), Image.LANCZOS)
            btn.alpha_composite(self.btn_t, (55, 27))
            # water sloshing inside the button
            wave_h = int(h * (0.25 + 0.06 * math.sin(b * 5)))
            sl = Image.new("RGBA", (w, h))
            pts = [(x, h - wave_h + 8 * math.sin(x / 40 + b * 8)) for x in range(0, w + 1, 10)] + [(w, h), (0, h)]
            ImageDraw.Draw(sl).polygon(pts, fill=(255, 255, 255, 70))
            m = Image.new("L", (w, h))
            ImageDraw.Draw(m).rounded_rectangle((6, 6, w - 6, h - 6), h // 2, fill=255)
            sl.putalpha(Image.fromarray(np.minimum(np.asarray(sl.getchannel("A")), np.asarray(m))))
            btn.alpha_composite(sl)
            pulse = 1 + 0.05 * max(0, math.sin(b * 6.5))
            paste(c.ov, soft_shadow(btn, 12, 0.4), cx, self.y + 140, scale=max(0.05, ease_out_back(b / 0.35, 2)) * pulse)
            paste(c.ov, self.hand, SAFE_L + 10, self.y + 150 + abs(math.sin(b * 6)) * 22)
        s = a - 0.9
        if s > 0:
            paste(c.ov, self.save, cx, self.y + 255, alpha=clamp(s / 0.25))


# ---------------------------------------------------------------- look + transitions

def fresh_grade(img):
    a = np.asarray(img, dtype=np.float32) / 255
    lum = a.mean(axis=2, keepdims=True)
    shadow = (1 - lum) ** 2
    a[..., 2:3] += shadow * 0.05     # aqua lift in the shadows
    a[..., 1:2] += shadow * 0.025
    a[..., 0:1] -= shadow * 0.02
    a = lum + (a - lum) * 1.08       # a touch more saturation (pink lips, pink bottle)
    a = a * 1.02 + 0.01
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


XS = np.arange(W)[None, :]
YS = np.arange(H)[:, None]


def water_wipe(prev, cur, k, t):
    """New shot rises from the bottom with a wavy waterline and a foam edge."""
    level = H * (1 - ease_in_out(k)) + 60 * (1 - k)
    surf = level + 34 * np.sin(XS / 85 + t * 14) + 14 * np.sin(XS / 31 - t * 21)
    m = (YS > surf).astype(np.float32)
    foam = ((YS > surf - 10) & (YS < surf + 12)).astype(np.float32)
    p = np.asarray(prev, np.float32)
    q = np.asarray(cur, np.float32)
    out = p * (1 - m[..., None]) + q * m[..., None]
    tint = np.array(AQUA, np.float32)
    band = ((YS > surf + 12) & (YS < surf + 160)).astype(np.float32) * 0.18
    out = out * (1 - band[..., None]) + tint * band[..., None]
    out = out * (1 - foam[..., None] * 0.85) + 255 * foam[..., None] * 0.85
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def camera(fi):
    t = fi / FPS
    tl = timeline()
    if t >= SPEECH_END:
        z0 = tl[-1][3][4][1]
        z = z0 * (1 + 0.10 * ease_in_out((t - SPEECH_END) / (TOTAL - SPEECH_END)))
    else:
        for n, s, e, seg in tl:
            if s <= t < e:
                break
        z0, z1 = seg[4]
        z = z0 + (z1 - z0) * ease_in_out((t - s) / (e - s))
    z *= 1 + 0.015 * math.exp(-((t % (60 / BPM)) * 8))  # gentle bounce on the beat
    z = max(z, 1.03)
    hw, hh = W / (2 * z), H / (2 * z)
    # slow floating drift, like being under water
    cx = clamp(W / 2 + 10 * math.sin(t * 0.9), hw, W - hw)
    cy = clamp(H * 0.45 + 8 * math.cos(t * 0.7), hh, H - hh)
    return z, cx, cy


# ---------------------------------------------------------------- the script

def build_elements():
    P = v1.Particles
    els = []
    els.append(Hook(0.0, 2.9))
    els.append(P(0.1, 2.9, "bubble", (80, 900, 1000, 1500), 9, life=(1.4, 2.2), size=(18, 44), vel=((-20, 20), (-300, -180)), seed=71))
    els.append(Callout(3.2, 6.3, "tengok sampai habis 👀", y=1180))

    els.append(Reason(at(6.8), at(10.45), 3, "Ada Hyaluronic Acid + Rose 🌹", "bantu kekalkan kelembapan kulit"))
    els.append(Reason(at(10.6), at(15.45), 2, "Tak berminyak, tak melekit", "lepas lap, kulit rasa ringan"))
    els.append(Reason(at(15.55), at(19.2), 1, "Tak pedih langsung 🙌", "pam atas kapas, lap lembut-lembut"))
    for i, (a, b) in enumerate([(6.8, 10.45), (10.6, 15.45), (15.55, 19.2)]):
        els.append(P(at(a), at(b), "bubble", (80, 1100, 1000, 1550), 5, life=(1.6, 2.4), size=(16, 40),
                     vel=((-20, 20), (-260, -160)), seed=72 + i))

    els.append(Callout(at(19.9), at(22.55), "hasilnya? kulit terasa lembut & segar 🤍", y=1180, sfx_kind="drip"))
    els.append(P(at(19.9), at(22.55), "sparkle", (250, 520, 830, 1000), 7, life=(0.6, 1.2), size=(14, 26),
                 vel=((-10, 10), (-30, 0)), seed=75))

    els.append(Callout(at(22.6), SPEECH_END - 0.02, "BONUS: botol pam 300ML, senang & kemas 💧", y=TOP_Y + 20, tail=None,
                       size=62, sfx_kind="bloop"))
    els.append(Callout(SPEECH_END, TOTAL + 1, "O’CHEAL Micellar Water 300ML", y=TOP_Y + 20, tail=None, size=66,
                       sfx_kind="drip"))
    els.append(SaveCTA(SPEECH_END + 0.2, TOTAL + 1))
    els.append(P(SPEECH_END, TOTAL + 1, "bubble", (80, 900, 1000, 1600), 10, life=(1.4, 2.2), size=(18, 46),
                 vel=((-20, 20), (-300, -180)), seed=76))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    for t in CUTS:
        cues.append(("whooshw", t - 0.12))
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


# ---------------------------------------------------------------- sound

def make_fx():
    SR = v1.SR
    T = v1._t
    fx = {"chime": v1.make_sfx()["chime"]}
    t = T(0.09)
    f = np.linspace(280, 1100, len(t))
    fx["plop"] = 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * v1.adsr(len(t), 0.001, 0.025)
    t = T(0.18)
    f = 1300 + 900 * np.exp(-t * 40)
    fx["drip"] = 0.45 * np.sin(2 * np.pi * np.cumsum(f) / SR) * v1.adsr(len(t), 0.001, 0.04)
    t = T(0.55)
    vib = 1 + 0.02 * np.sin(2 * np.pi * 7 * t)
    fx["bloop"] = 0.4 * np.sin(2 * np.pi * np.cumsum(520 * vib) / SR) * v1.adsr(len(t), 0.004, 0.14)
    d = 0.6
    nz = v1.noise(d, 81) * np.hanning(int(d * SR)) ** 0.5
    sp = v1.bandpass_sweep(nz, 4500, 700) * v1.adsr(int(d * SR), 0.003, 0.16)
    gurgle = 1 + 0.5 * np.sin(2 * np.pi * 28 * T(d))
    fx["splash"] = 0.32 * sp * gurgle
    d = 0.45
    nz = v1.noise(d, 82) * np.hanning(int(d * SR))
    fx["whooshw"] = 0.26 * v1.bandpass_sweep(nz, 350, 1600) * np.hanning(int(d * SR)) * (1 + 0.4 * np.sin(2 * np.pi * 22 * T(d)))
    return fx


def make_audio():
    SR = v1.SR
    chords = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]]  # Cmaj7 Am7 Fmaj7 G
    music = v1.make_music(TOTAL, bpm=BPM, chords=chords)
    n = int((TOTAL + 0.05) * SR)
    music = music[:n]
    music /= np.abs(music).max() + 1e-9
    tail = int(1.1 * SR)
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
        "[m][key]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350:makeup=1[md];"
        "[2]volume=-8dB[fx];"
        "[v][md][fx]amix=inputs=3:duration=longest:normalize=0,atrim=0:" + f"{TOTAL:.3f}",
        "-ar", "48000", str(mix)], check=True)
    return mix


# ---------------------------------------------------------------- main

CUT_FRAMES = {round(t * FPS) for t in CUTS}


def frames(base, els, want=None):
    """Yields (fi, final frame). Keeps the last graded frame so cuts can water-wipe from it."""
    held, last, fi = None, None, 0
    src = v1.frames_from(base)
    img = None
    while fi < round(TOTAL * FPS):
        nxt = next(src, None)
        img = nxt if nxt is not None else img
        if fi in CUT_FRAMES and last is not None:
            held = (last, fi)
        need = want is None or fi in want or (fi + 1) in CUT_FRAMES or any(0 <= fi - cf < WIPE for cf in CUT_FRAMES)
        if need:
            z, cx, cy = camera(fi)
            g = fresh_grade(v1.bloom(v1.apply_camera(img, z, cx, cy), 0.07))
            last = g
            shown = g
            if held and fi - held[1] < WIPE:
                shown = water_wipe(held[0], g, (fi - held[1] + 1) / WIPE, fi / FPS)
            if want is None or fi in want:
                frame = shown.convert("RGBA")
                ov = Image.new("RGBA", (W, H))
                c = v1.Ctx(fi, frame, ov, (z, cx, cy))
                for el in els:
                    el.draw(c)
                yield fi, Image.alpha_composite(frame, ov).convert("RGB")
        else:
            last = None
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
        want = {round(t * FPS) for t in [0.4, 1.2, 2.4, 4.5, 6.6, 6.85, 7.6, 9.2, 11.3, 13.0, 14.9, 16.4,
                                          18.9, 20.6, 22.8, 23.6, 24.8, 25.9]}
        for fi, out in frames(base, els, want):
            out.save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
        return
    mix = make_audio()
    OUT.parent.mkdir(exist_ok=True)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(mix),
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)
    for fi, out in frames(base, els):
        enc.stdin.write(out.tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{round(TOTAL * FPS)}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
