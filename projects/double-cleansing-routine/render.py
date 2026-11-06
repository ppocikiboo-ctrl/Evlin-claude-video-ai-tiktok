"""Step 2 ("skincare diary" style): graphics, sound design and final encode.

A routine explainer for double cleansing. A two-step tracker sits at the
top (1 Buang makeup -> 2 Cuci muka), big outline numerals open each step,
cream tip cards slide up timed to the real actions, the hook strikes
through "cuci muka je", and cuts use a soft freeze-dissolve. Step 2 is
not in the footage, so it is shown as a graphic card only.
Text helpers, sprites and the synth engine are reused from
../ocheal-micellar-water/render.py.

    python3 build_base.py && python3 render.py   # -> output/double_cleansing_routine.mp4
    python3 render.py --stills                    # preview stills -> build/stills/
"""
import argparse
import importlib.util
import math
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from edl import FPS, H, TOTAL, W, seg_end, seg_start, timeline

ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("kbeauty_v1", ROOT.parent / "ocheal-micellar-water" / "render.py")
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)  # v1 picks up this folder's edl.py (same API)

text_img, paste, clamp = v1.text_img, v1.paste, v1.clamp
ease_out_cubic, ease_out_back, ease_in_out, env = v1.ease_out_cubic, v1.ease_out_back, v1.ease_in_out, v1.env
OUT = ROOT / "output" / "double_cleansing_routine.mp4"

CREAM = (250, 244, 234)
MOCHA = (120, 84, 64)
SAGE = (150, 170, 150)
BLUSH = (232, 150, 150)
INK = (52, 40, 36)
WHITE = (255, 255, 255)

SAFE_L, SAFE_R = 60, 880
TOP_L, TOP_R = 50, 1030
SANS, SANS_B, SERIF, SERIF_I, SCRIPT = ("Montserrat-ExtraBold.ttf", "Montserrat-Bold.ttf", "Playfair-ExtraBold.ttf",
                                        "Playfair-SemiBoldItalic.ttf", "GreatVibes.ttf")
DISSOLVE = 7  # frames


def shadowed(im, blur=14, alpha=0.28, off=(0, 10)):
    out = Image.new("RGBA", (im.width + 2 * blur + abs(off[0]), im.height + 2 * blur + abs(off[1])))
    sh = Image.new("RGBA", im.size, (60, 40, 30, 0))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, (blur + off[0], blur + off[1]))
    out = out.filter(ImageFilter.GaussianBlur(blur / 2))
    out.alpha_composite(im, (blur, blur))
    return out


def card(w, h, r=34, fill=CREAM, alpha=240):
    im = Image.new("RGBA", (w * 2, h * 2))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=fill + (alpha,))
    return im.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- elements

class Tracker:
    """Persistent two-step routine tracker at the top of the frame."""

    STEPS = ["Buang makeup", "Cuci muka"]

    def __init__(self, t0, t1, step2_at, step1_start, step1_end, y=232):
        self.t0, self.t1, self.y = t0, t1, y
        self.step2_at, self.s1a, self.s1b = step2_at, step1_start, step1_end
        self.labels = [text_img(s, SANS_B, 34, INK) for s in self.STEPS]
        self.title = text_img("DOUBLE CLEANSING", SANS, 30, MOCHA, tracking=4)

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.3, 0.3)
        if v <= 0:
            return
        w, h = TOP_R - TOP_L, 210
        im = card(w, h, 40, CREAM, 225)
        d = ImageDraw.Draw(im)
        im.alpha_composite(self.title, ((w - self.title.width) // 2, 14))
        xs = [w * 0.27, w * 0.73]
        cy = 96
        # connecting line + progress
        prog = clamp((c.t - self.s1a) / (self.s1b - self.s1a)) * 0.5 + 0.5 * clamp((c.t - self.step2_at) / 0.8)
        x0, x1 = xs[0] + 34, xs[1] - 34
        d.line([(x0, cy), (x1, cy)], fill=(215, 200, 185, 255), width=8)
        d.line([(x0, cy), (x0 + (x1 - x0) * prog, cy)], fill=MOCHA + (255,), width=8)
        for i, (x, lab) in enumerate(zip(xs, self.labels)):
            active = (c.t >= self.step2_at) if i == 1 else (c.t < self.step2_at)
            done = i == 0 and c.t >= self.step2_at
            r = 32
            fill = MOCHA if (active or done) else CREAM
            d.ellipse((x - r, cy - r, x + r, cy + r), fill=fill + (255,), outline=MOCHA + (255,), width=5)
            if done:
                d.line([(x - 13, cy + 1), (x - 3, cy + 11), (x + 15, cy - 10)], fill=WHITE, width=7, joint="curve")
            else:
                n = text_img(str(i + 1), SANS, 36, WHITE if active else MOCHA)
                im.alpha_composite(n, (int(x - n.width / 2), int(cy - n.height / 2)))
            im.alpha_composite(lab, (int(x - lab.width / 2), int(cy + r + 10)))
            if active:  # soft pulse ring
                ph = (c.t * 1.2) % 1.0
                rr = r + 6 + ph * 16
                d.ellipse((x - rr, cy - rr, x + rr, cy + rr), outline=MOCHA + (int(160 * (1 - ph)),), width=4)
        u = ease_out_cubic((c.t - self.t0) / 0.45)
        paste(c.ov, shadowed(im), (TOP_L + TOP_R) / 2, self.y + h / 2 - (1 - u) * 60, alpha=v)


class Hook:
    """'Cuci muka je' gets struck through, then 'TAK CUKUP!' lands, then the script line."""

    def __init__(self, t0, t1, y=300):
        self.t0, self.t1, self.y = t0, t1, y
        self.l1 = text_img("Cuci muka je?", SERIF, 112, WHITE, 6, INK, shadow=0.5)
        self.l2 = text_img("TAK CUKUP!", SANS, 132, BLUSH, 9, WHITE, shadow=0.6)
        self.l3 = text_img("ni rutin double cleansing aku 🌙", SCRIPT, 92, WHITE, 3, INK, shadow=0.5)

    def sfx(self):
        return [("pop", self.t0 + 0.05), ("swish", self.t0 + 0.55), ("thud", self.t0 + 0.8), ("sparkle", self.t0 + 1.35)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        a = c.t - self.t0
        out = clamp((self.t1 - c.t) / 0.2)
        cx = (TOP_L + TOP_R) / 2
        u1 = ease_out_back(a / 0.3, 1.5)
        paste(c.ov, self.l1, cx, self.y + self.l1.height / 2, alpha=clamp(a / 0.1) * out, scale=max(0.05, 0.8 + 0.2 * u1))
        s = clamp((a - 0.5) / 0.22)
        if s > 0:
            d = ImageDraw.Draw(c.ov)
            x0 = cx - self.l1.width / 2 + 20
            x1 = x0 + (self.l1.width - 40) * ease_out_cubic(s)
            yy = self.y + self.l1.height * 0.52
            d.line([(x0, yy + 6), (x1, yy - 6)], fill=BLUSH + (int(255 * out),), width=16)
        a2 = a - 0.8
        if a2 > 0:
            sc = 1 + 0.7 * (1 - ease_out_back(a2 / 0.25, 1.4)) if a2 < 0.25 else 1
            paste(c.ov, self.l2, cx, self.y + self.l1.height + self.l2.height / 2 - 10, alpha=clamp(a2 / 0.06) * out, scale=sc,
                  rot=-3)
        a3 = a - 1.35
        if a3 > 0:
            reveal = ease_out_cubic(a3 / 0.6)
            l3 = self.l3.crop((0, 0, max(1, int(self.l3.width * reveal)), self.l3.height))
            paste(c.ov, l3, cx - self.l3.width / 2, self.y + self.l1.height + self.l2.height + 40, alpha=out, anchor="lt")


class Explainer:
    """'Apa tu double cleansing?' with the two steps written out."""

    def __init__(self, t0, t1, y=470):
        self.t0, self.t1, self.y = t0, t1, y
        self.q = text_img("Apa tu double cleansing?", SERIF_I, 64, INK)
        self.rows = [("1", "Tanggalkan makeup & sunscreen", "pencuci berasaskan minyak / micellar"),
                     ("2", "Baru cuci muka", "dengan pencuci muka biasa")]
        self.rimg = [(text_img(a, SANS_B, 46, INK), text_img(b, SANS_B, 34, MOCHA)) for _, a, b in self.rows]

    def sfx(self):
        return [("click", self.t0), ("ting", self.t0 + 0.55), ("ting", self.t0 + 1.05)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.25, 0.2)
        if v <= 0:
            return
        w = TOP_R - TOP_L
        h = 120 + 2 * 150
        im = card(w, h, 40, CREAM, 238)
        im.alpha_composite(self.q, ((w - self.q.width) // 2, 34))
        d = ImageDraw.Draw(im)
        for i, ((n, *_), (a_img, b_img)) in enumerate(zip(self.rows, self.rimg)):
            a = c.t - self.t0 - 0.5 - i * 0.5
            if a < 0:
                continue
            k = ease_out_cubic(a / 0.3)
            ry = 130 + i * 150
            dx = int((1 - k) * -80)
            d.ellipse((50 + dx, ry + 18, 130 + dx, ry + 98), fill=MOCHA + (int(255 * k),))
            nn = text_img(n, SANS, 50, WHITE)
            im.alpha_composite(nn, (90 + dx - nn.width // 2, ry + 58 - nn.height // 2))
            im.alpha_composite(a_img, (160 + dx, ry + 10))
            im.alpha_composite(b_img, (160 + dx, ry + 10 + a_img.height + 2))
        u = ease_out_back((c.t - self.t0) / 0.35, 1.2)
        paste(c.ov, shadowed(im), (TOP_L + TOP_R) / 2, self.y + h / 2, alpha=v, scale=max(0.05, 0.9 + 0.1 * u))


class StepTitle:
    """Big outline numeral + step name, e.g. '01  Buang makeup'."""

    def __init__(self, t0, t1, num, title, sub, y=440):
        self.t0, self.t1, self.y = t0, t1, y
        n = text_img(num, SERIF, 230, (0, 0, 0, 0), 5, WHITE)
        self.num = n
        self.title = text_img(title, SANS, 70, WHITE, 6, INK, shadow=0.5)
        self.sub = text_img(sub, SERIF_I, 52, WHITE, 4, INK, shadow=0.5)

    def sfx(self):
        return [("whoosh", self.t0 - 0.1), ("ting", self.t0 + 0.2)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.25, 0.25)
        if v <= 0:
            return
        a = c.t - self.t0
        x = TOP_L + 30
        paste(c.ov, self.num, x - (1 - ease_out_cubic(a / 0.4)) * 120, self.y, alpha=v * 0.95, anchor="lt")
        tx = x + self.num.width + 10
        ty = self.y + 40
        k = ease_out_cubic((a - 0.15) / 0.35)
        paste(c.ov, self.title, tx + (1 - k) * 80, ty, alpha=v * k, anchor="lt")
        k2 = ease_out_cubic((a - 0.35) / 0.35)
        paste(c.ov, self.sub, tx + (1 - k2) * 80, ty + self.title.height + 6, alpha=v * k2, anchor="lt")


class Tip:
    """Cream tip card that slides up in the lower area."""

    def __init__(self, t0, t1, label, text, y=1220, emoji=None):
        self.t0, self.t1, self.y = t0, t1, y
        self.label = text_img(label, SANS, 30, WHITE, tracking=3)
        size = 56
        while text_img(text, SANS_B, size, INK).width > SAFE_R - SAFE_L - 80:
            size -= 2
        self.text = text_img(text, SANS_B, size, INK)
        self.emoji = v1.emoji_img(emoji, 84) if emoji else None

    def sfx(self):
        return [("click", self.t0), ("pop", self.t0 + 0.12)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.25, 0.2)
        if v <= 0:
            return
        w = max(self.text.width + 80, self.label.width + 120)
        h = self.text.height + 110
        im = card(w, h, 34)
        pill = card(self.label.width + 40, self.label.height + 18, 18, MOCHA, 255)
        pill.alpha_composite(self.label, (20, 9))
        im.alpha_composite(pill, (40, 22))
        im.alpha_composite(self.text, (40, 34 + pill.height))
        u = ease_out_back((c.t - self.t0) / 0.38, 1.3)
        cx = (SAFE_L + SAFE_R) / 2
        paste(c.ov, shadowed(im), cx, self.y + h / 2 + (1 - clamp(u)) * 120, alpha=v)
        if self.emoji is not None:
            a = c.t - self.t0 - 0.2
            if a > 0:
                paste(c.ov, self.emoji, cx + w / 2 - 20, self.y - 10 + math.sin(a * 5) * 8, alpha=v,
                      scale=max(0.05, ease_out_back(a / 0.3, 2.2)), rot=math.sin(a * 4) * 10)


class FoamCard:
    """Step 2 explained as a graphic: foam bubbles rise behind a cream card."""

    def __init__(self, t0, t1, y=1120):
        self.t0, self.t1, self.y = t0, t1, y
        self.l1 = text_img("Cuci muka dengan", SANS_B, 52, INK)
        self.l2 = text_img("pencuci muka biasa 🫧", SERIF_I, 64, MOCHA)
        self.l3 = text_img("buang sisa minyak & kotoran", SANS_B, 38, (120, 110, 105))
        self.bub = v1.Particles(t0, t1, "bubble", (SAFE_L + 40, y + 40, SAFE_R - 40, y + 360), 16, life=(1.0, 1.8),
                                size=(18, 46), vel=((-25, 25), (-260, -160)), seed=41)

    def sfx(self):
        return [("sparkle", self.t0 + 0.2)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.3, 0.25)
        if v <= 0:
            return
        w = SAFE_R - SAFE_L
        h = self.l1.height + self.l2.height + self.l3.height + 90
        im = card(w, h, 40)
        y = 30
        for t in (self.l1, self.l2, self.l3):
            im.alpha_composite(t, ((w - t.width) // 2, y))
            y += t.height + 10
        u = ease_out_back((c.t - self.t0) / 0.4, 1.2)
        self.bub.draw(c)
        paste(c.ov, shadowed(im), (SAFE_L + SAFE_R) / 2, self.y + h / 2 + (1 - clamp(u)) * 120, alpha=v)


class ScriptLine:
    def __init__(self, t0, t1, text, y, size=96):
        self.t0, self.t1, self.y = t0, t1, y
        self.im = text_img(text, SCRIPT, size, WHITE, 3, INK, shadow=0.55)

    def sfx(self):
        return [("sparkle", self.t0)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.2, 0.25)
        if v <= 0:
            return
        reveal = ease_out_cubic((c.t - self.t0) / 0.7)
        im = self.im.crop((0, 0, max(1, int(self.im.width * reveal)), self.im.height))
        paste(c.ov, im, (TOP_L + TOP_R) / 2 - self.im.width / 2, self.y, alpha=v, anchor="lt")


class Headline:
    def __init__(self, t0, t1, text, y, size=80, font=SANS, fill=WHITE):
        self.t0, self.t1, self.y = t0, t1, y
        while text_img(text, font, size, fill, 7, INK).width > TOP_R - TOP_L:
            size -= 3
        self.im = text_img(text, font, size, fill, 7, INK, shadow=0.55)

    def sfx(self):
        return [("pop", self.t0)]

    def draw(self, c):
        v = env(c.t, self.t0, self.t1, 0.15, 0.2)
        if v <= 0:
            return
        u = ease_out_back((c.t - self.t0) / 0.3, 1.6)
        paste(c.ov, self.im, (TOP_L + TOP_R) / 2, self.y + self.im.height / 2, alpha=v, scale=max(0.05, 0.85 + 0.15 * u))


class CTA:
    def __init__(self, t0, t1, y=1170):
        self.t0, self.t1, self.y = t0, t1, y
        self.l1 = text_img("Langkah 1 aku:", SERIF_I, 56, MOCHA)
        self.l2 = text_img("O’CHEAL Micellar Water", SANS, 60, INK)
        self.btn_t = text_img("Tekan beg kuning 🛍️", SANS, 50, INK)
        self.hand = v1.emoji_img("👇", 110)

    def sfx(self):
        return [("click", self.t0), ("chime", self.t0 + 0.45)]

    def draw(self, c):
        if c.t < self.t0:
            return
        a = c.t - self.t0
        w = SAFE_R - SAFE_L
        h = self.l1.height + self.l2.height + 70
        im = card(w, h, 40)
        im.alpha_composite(self.l1, ((w - self.l1.width) // 2, 24))
        im.alpha_composite(self.l2, ((w - self.l2.width) // 2, 34 + self.l1.height))
        cx = (SAFE_L + SAFE_R) / 2
        u = ease_out_back(a / 0.4, 1.2)
        paste(c.ov, shadowed(im), cx, self.y + h / 2 + (1 - clamp(u)) * 100)
        b = a - 0.45
        if b > 0:
            bw, bh = self.btn_t.width + 90, self.btn_t.height + 50
            btn = Image.new("RGBA", (bw * 2, bh * 2))
            ImageDraw.Draw(btn).rounded_rectangle((0, 0, bw * 2 - 1, bh * 2 - 1), bh, fill=(255, 214, 64, 255))
            btn = btn.resize((bw, bh), Image.LANCZOS)
            btn.alpha_composite(self.btn_t, (45, 25))
            pulse = 1 + 0.04 * max(0, math.sin(b * 6.5))
            paste(c.ov, shadowed(btn), cx, self.y + h + 40 + bh / 2, scale=max(0.05, ease_out_back(b / 0.35, 2)) * pulse)
            paste(c.ov, self.hand, SAFE_L + 70, self.y + h + bh + 130 + abs(math.sin(b * 6)) * 22)


# ---------------------------------------------------------------- camera + dissolves

def camera(fi):
    t = fi / FPS
    for n, s, e, seg in timeline():
        if s <= t < e:
            break
    z0, z1 = seg[4]
    u = (t - s) / (e - s)
    z = max(1.0, z0 + (z1 - z0) * ease_in_out(u))
    hh = H / (2 * z)
    return z, W / 2, clamp(H * 0.47, hh, H - hh)


CUT_FRAMES = {round(s * FPS) for _, s, _, _ in timeline()[1:]}


# ---------------------------------------------------------------- the script

def build_elements():
    S, E = seg_start, seg_end
    P = v1.Particles
    els = []
    els.append(Hook(0.0, E("hook") - 0.02))
    els.append(Tracker(S("explain"), E("smile") - 0.02, step2_at=S("clean") + 0.3, step1_start=S("pump"), step1_end=E("repeat")))
    els.append(Explainer(S("explain") + 0.05, E("explain") - 0.02))

    # STEP 1, timed to the real actions
    els.append(StepTitle(S("pump") + 0.05, S("pump") + 1.6, "01", "Buang makeup", "micellar water dulu"))
    els.append(Tip(S("pump") + 0.4, E("pump") - 0.02, "MICELLAR WATER", "Basahkan kapas dulu", emoji="💦"))
    els.append(Tip(S("wipe") + 0.05, E("wipe") - 0.02, "TIP", "Lap lembut-lembut, jangan gosok"))
    els.append(Tip(S("eyes") + 0.05, E("eyes") - 0.02, "MATA", "Tekap dulu ±3 saat, baru lap", emoji="👁️"))
    els.append(Tip(S("mouth") + 0.05, E("mouth") - 0.02, "TIP", "Sekeliling mulut & dagu sekali"))
    els.append(Tip(S("neck") + 0.05, E("neck") - 0.02, "JANGAN LUPA", "Leher pun kena cuci!", emoji="👀"))
    els.append(Tip(S("repeat") + 0.05, E("repeat") - 0.02, "TIP", "Ulang guna kapas baru"))
    els.append(P(S("pump") + 0.4, E("pump"), "droplet", (300, 1000, 800, 1150), 4, life=(0.8, 1.1), size=(16, 24),
                 vel=((-10, 10), (60, 120)), seed=40))

    # STEP 2 (graphic only, not in the footage) over the clean-face close-up
    els.append(StepTitle(S("clean") + 0.3, S("clean") + 1.9, "02", "Cuci muka", "baru guna facial wash"))
    els.append(FoamCard(S("clean") + 0.6, E("clean") - 0.02))

    # RESULT
    t, e = S("smile"), E("smile")
    els.append(ScriptLine(t + 0.05, e - 0.02, "bersih & terasa lembut ✨", 470, size=112))
    els.append(Tip(t + 0.6, e - 0.02, "LEPAS NI", "Baru sambung toner & pelembap", emoji="🧴"))
    els.append(P(t, e, "sparkle", (250, 650, 830, 1100), 8, life=(0.6, 1.2), size=(14, 26), vel=((-10, 10), (-30, 0)), seed=42))

    # CTA
    t, e = S("cta"), E("cta")
    els.append(Headline(t + 0.05, e + 1, "Rutin malam aku 🌙", 300, size=96, font=SERIF_I))
    els.append(CTA(t + 0.25, e))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


def make_fx():
    fx = v1.make_sfx()
    t = v1._t(0.3)
    import numpy as np
    f = np.linspace(140, 50, len(t))
    fx["thud"] = 0.5 * np.sin(2 * np.pi * np.cumsum(f) / v1.SR) * v1.adsr(len(t), 0.001, 0.09)
    for k in ("ting", "pop", "whoosh"):
        fx[k] = fx[k] * 0.75  # calmer mix for a routine video
    return fx


def make_music():
    # calm lo-fi bed: Cmaj7 - Am7 - Dm7 - G7, 90 BPM
    chords = [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 65]]
    return v1.make_music(TOTAL, bpm=90, chords=chords)


# ---------------------------------------------------------------- main

def render_frame(fi, img, els, held):
    z, cx, cy = camera(fi)
    img = v1.apply_camera(img, z, cx, cy)
    img = v1.bloom(img, 0.06)
    if held["img"] is not None and fi - held["fi"] < DISSOLVE:
        k = (fi - held["fi"]) / DISSOLVE
        img = Image.blend(held["img"], img, ease_in_out(k))
    frame = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    c = v1.Ctx(fi, frame, ov, (z, cx, cy))
    for el in els:
        el.draw(c)
    return img, Image.alpha_composite(frame, ov).convert("RGB")


def frames(base, els, want=None):
    held, last = {"img": None, "fi": -99}, None
    for fi, img in enumerate(v1.frames_from(base)):
        if fi in CUT_FRAMES and last is not None:
            held = {"img": last, "fi": fi}
        if want is None or fi in want or fi + 1 in CUT_FRAMES:
            graded, out = render_frame(fi, img, els, held)
            last = graded
            yield fi, out
        else:
            last = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    els = build_elements()
    base = ROOT / "build" / "base.mp4"
    if args.stills:
        outdir = ROOT / "build" / "stills"
        outdir.mkdir(exist_ok=True)
        want = {round(t * FPS) for t in [0.4, 1.0, 1.9, 3.6, 4.6, 5.5, 6.8, 8.3, 10.5, 12.6, 14.6, 16.6,
                                          18.2, 19.5, 21.5, 23.0, 24.4, 25.6]}
        for fi, out in frames(base, els, want):
            if fi in want:
                out.save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
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
    for fi, out in frames(base, els):
        enc.stdin.write(out.tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{round(TOTAL * FPS)}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
