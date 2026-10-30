"""Step 3 (v3 "review caption" style): graphics, sound design and final encode.

A conversion-first edit: the hook opens on the real used pads with a
magnifier lens, CapCut-style word-by-word captions with neon highlighter
keywords carry the story, STEP chips follow the real actions, a personal
rating card stacks the reasons to buy, cuts are whip-pans, the picture
pulses on the beat, and the ending points to the yellow bag.
Text helpers, sprites and the synth engine are reused from v1.

    python3 build_base.py && python3 render.py      # -> output/ocheal_micellar_tiktok_v3.mp4
    python3 render.py --stills                       # preview stills -> build/stills/
"""
import argparse
import importlib.util
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from edl import FPS, H, TOTAL, W, seg_end, seg_start, timeline

ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("kbeauty_v1", ROOT.parent / "ocheal-micellar-water" / "render.py")
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)  # v1 picks up this folder's edl.py (same API)

text_img, paste, clamp = v1.text_img, v1.paste, v1.clamp
ease_out_cubic, ease_out_back, ease_in_out, env = v1.ease_out_cubic, v1.ease_out_back, v1.ease_in_out, v1.env
OUT = ROOT / "output" / "ocheal_micellar_tiktok_v3.mp4"

INK = (20, 16, 20)
WHITE = (255, 255, 255)
NEON = (255, 61, 139)    # highlighter pink
LIME = (205, 255, 64)    # highlighter lime
YEL = (255, 221, 51)     # yellow bag

SAFE_L, SAFE_R = 60, 880
TOP_L, TOP_R = 50, 1030
TOP_Y = 250
BPM = 104
BEAT = 60 / BPM
FONT = "Montserrat-ExtraBold.ttf"


# ---------------------------------------------------------------- type

@lru_cache(maxsize=None)
def word_img(word, size, fill=WHITE, stroke=None):
    """CapCut-style caption word: white, thick dark outline, soft shadow."""
    stroke = max(6, size // 9) if stroke is None else stroke
    return text_img(word, FONT, size, fill, stroke, INK, shadow=0.5)


def layout(words, size, max_w, gap_k=0.05):
    """Greedy line wrap. Returns rows of (index, word_sprite) and the row heights."""
    rows, row, w = [], [], 0
    for i, (wd, _) in enumerate(words):
        im = word_img(wd, size)
        gap = int(size * gap_k)
        if row and w + gap + im.width > max_w:
            rows.append(row)
            row, w = [], 0
        row.append((i, im))
        w += im.width + (gap if len(row) > 1 else 0)
    if row:
        rows.append(row)
    return rows


def parse(text):
    """'TENGOK *TERANGKAT* 😳' -> [('TENGOK', None), ('TERANGKAT', NEON), ('😳', None)].
    *word* = pink highlighter, _word_ = lime highlighter."""
    out = []
    for w in text.split(" "):
        if w.startswith("*") and w.endswith("*"):
            out.append((w[1:-1], NEON))
        elif w.startswith("_") and w.endswith("_"):
            out.append((w[1:-1], LIME))
        else:
            out.append((w, None))
    return out


def highlighter(w, h, color, prog, seed=0):
    """Marker swipe behind a word: slightly tilted, rough ends, drawn left->right."""
    im = Image.new("RGBA", (w + 40, h + 30))
    if prog <= 0:
        return im
    d = ImageDraw.Draw(im)
    x1 = 20 + (w + 4) * prog
    d.polygon([(14, 22), (x1, 12), (x1 + 6, h + 14), (18, h + 22)], fill=color + (235,))
    return im


class Caption:
    """Words appear one at a time (karaoke); the newest word is pink and bigger.

    words_per_sec controls the pace; highlighted words get a marker swipe."""

    def __init__(self, t0, t1, text, y, size=72, wps=4.2, big=False, align_x=None, max_w=None, sfx=True):
        self.t0, self.t1, self.y, self.size, self.big = t0, t1, y, size, big
        self.words = parse(text)
        self.max_w = max_w or (TOP_R - TOP_L if y < 900 else SAFE_R - SAFE_L)
        self.cx = align_x or ((TOP_L + TOP_R) / 2 if y < 900 else (SAFE_L + SAFE_R) / 2)
        self.rows = layout(self.words, size, self.max_w)
        self.times = [t0 + i / wps for i in range(len(self.words))]
        self.want_sfx = sfx

    def sfx(self):
        if not self.want_sfx:
            return []
        out = [("pop", t) for t in self.times[::2]]
        out += [("ting", t + 0.12) for t, (_, hl) in zip(self.times, self.words) if hl]
        return out

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        out = clamp((self.t1 - c.t) / 0.12)
        y = self.y
        last = max(i for i, t in enumerate(self.times) if t <= c.t)
        for row in self.rows:
            gap = int(self.size * 0.05)
            rw = sum(im.width for _, im in row) + gap * (len(row) - 1)
            rh = max(im.height for _, im in row)
            x = self.cx - rw / 2
            for i, im in row:
                a = c.t - self.times[i]
                if a >= 0:
                    word, hl = self.words[i]
                    u = a / 0.16
                    sc = 1 + 0.35 * (1 - ease_out_back(u, 2.2)) if u < 1 else 1.0
                    if hl:
                        mk = highlighter(im.width - 20, im.height - 34, hl, ease_out_cubic((a - 0.08) / 0.22))
                        paste(c.ov, mk, x + im.width / 2, y + rh / 2, alpha=out)
                    sprite = im
                    if i == last and not hl and not self.big and a < 0.5 and not any(ch in word for ch in "😳🤍🛍️👇💯🌹💦"):
                        sprite = word_img(word, self.size, (255, 120, 170))
                    paste(c.ov, sprite, x + im.width / 2, y + rh / 2 + (1 - clamp(u)) * 10,
                          alpha=clamp(a / 0.05) * out, scale=sc * (0.92 + 0.08 * out))
                x += im.width + gap
            y += rh - int(self.size * 0.22)


class StepChip:
    """Black pill 'STEP n' + label, slides in from the left."""

    def __init__(self, t0, t1, n, label, y=TOP_Y):
        self.t0, self.t1, self.y = t0, t1, y
        num = text_img(f"STEP {n}", FONT, 44, INK)
        lab = text_img(label, FONT, 54, WHITE)
        h = max(num.height, lab.height) + 36
        nw = num.width + 46
        w = nw + lab.width + 60
        im = Image.new("RGBA", (w * 2, h * 2))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), h, fill=INK + (235,))
        d.rounded_rectangle((10, 10, nw * 2, h * 2 - 11), h - 10, fill=LIME + (255,))
        im = im.resize((w, h), Image.LANCZOS)
        im.alpha_composite(num, (23, (h - num.height) // 2))
        im.alpha_composite(lab, (nw + 30, (h - lab.height) // 2))
        self.im = im

    def sfx(self):
        return [("click", self.t0), ("swish", self.t0 - 0.02)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        u = ease_out_back((c.t - self.t0) / 0.3, 1.4)
        out = clamp((self.t1 - c.t) / 0.12)
        x = TOP_L + self.im.width / 2 - (1 - u) * (self.im.width + 80)
        paste(c.ov, self.im, x, self.y + self.im.height / 2, alpha=out)


class Lens:
    """Magnifier on the real footage (no retouching): 1.9x of the area under it."""

    def __init__(self, t0, t1, src_xy, at_xy, r=210, zoom=1.9):
        self.t0, self.t1, self.src, self.at, self.r, self.zoom = t0, t1, src_xy, at_xy, r, zoom
        m = Image.new("L", (r * 4, r * 4))
        ImageDraw.Draw(m).ellipse((0, 0, r * 4 - 1, r * 4 - 1), fill=255)
        self.mask = m.resize((r * 2, r * 2), Image.LANCZOS)
        self.tag = text_img("ZOOM 🔍", FONT, 40, INK)

    def sfx(self):
        return [("pop", self.t0), ("whoosh", self.t0 - 0.1)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        u = ease_out_back((c.t - self.t0) / 0.3, 1.6)
        v = env(c.t, self.t0, self.t1, 0.08, 0.12)
        r = self.r
        sr = r / self.zoom
        sx, sy = self.src
        crop = c.frame.crop((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr))).resize((2 * r, 2 * r), Image.BICUBIC)
        crop.putalpha(self.mask)
        lens = Image.new("RGBA", (2 * r + 60, 2 * r + 60))
        sh = Image.new("RGBA", lens.size)
        ImageDraw.Draw(sh).ellipse((34, 40, 2 * r + 34, 2 * r + 40), fill=(0, 0, 0, 110))
        lens.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        lens.alpha_composite(crop, (30, 30))
        ImageDraw.Draw(lens).ellipse((30, 30, 2 * r + 30, 2 * r + 30), outline=WHITE + (255,), width=10)
        pill = Image.new("RGBA", (self.tag.width + 40, self.tag.height + 22))
        ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, pill.height - 1), pill.height // 2, fill=LIME + (255,))
        pill.alpha_composite(self.tag, (20, 11))
        lens.alpha_composite(pill, (lens.width // 2 - pill.width // 2, lens.height - pill.height - 6))
        # thin guide line from the source point to the lens
        d = ImageDraw.Draw(c.ov)
        d.line([(sx, sy), self.at], fill=WHITE + (int(200 * v),), width=5)
        d.ellipse((sx - 14, sy - 14, sx + 14, sy + 14), outline=WHITE + (int(230 * v),), width=5)
        paste(c.ov, lens, self.at[0], self.at[1], alpha=v, scale=max(0.05, u))


@lru_cache(maxsize=None)
def star_img(size, on):
    s = size * 2
    im = Image.new("RGBA", (s, s))
    pts = []
    for i in range(10):
        rr = s * (0.48 if i % 2 == 0 else 0.2)
        a = -math.pi / 2 + math.pi * i / 5
        pts.append((s / 2 + rr * math.cos(a), s / 2 + rr * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=(YEL if on else (90, 80, 90)) + (255,), outline=INK + (255,))
    return im.resize((size, size), Image.LANCZOS)


class RatingCard:
    """'RATING AKU' card: rows slide in, five stars fill one by one."""

    def __init__(self, t0, t1, title, rows, row_gap=0.42, y=TOP_Y):
        self.t0, self.t1, self.y, self.rows = t0, t1, y, rows
        self.title = text_img(title, FONT, 66, WHITE)
        self.labels = [text_img(r, FONT, 56, WHITE) for r in rows]
        self.row_t = [t0 + 0.3 + i * row_gap for i in range(len(rows))]
        self.w = TOP_R - TOP_L
        self.row_h = 104
        self.h = 120 + self.row_h * len(rows) + 20

    def sfx(self):
        out = [("click", self.t0), ("whoosh", self.t0 - 0.08)]
        for rt in self.row_t:
            out += [("pop", rt)] + [("ting", rt + 0.12 + k * 0.06) for k in (0, 4)]
        return out

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        u = ease_out_back((c.t - self.t0) / 0.35, 1.3)
        out = clamp((self.t1 - c.t) / 0.14)
        card = Image.new("RGBA", (self.w, self.h))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, self.w - 1, self.h - 1), 44, fill=(20, 16, 20, 200))
        d.rounded_rectangle((0, 0, self.w - 1, 108), 44, fill=NEON + (255,))
        d.rectangle((0, 60, self.w - 1, 108), fill=NEON + (255,))
        card.alpha_composite(self.title, ((self.w - self.title.width) // 2, (108 - self.title.height) // 2))
        for i, (lab, rt) in enumerate(zip(self.labels, self.row_t)):
            a = c.t - rt
            if a < 0:
                continue
            ry = 120 + i * self.row_h
            lx = 40 - (1 - ease_out_cubic(a / 0.25)) * 200
            card.alpha_composite(lab, (int(max(0, lx)), ry + (self.row_h - lab.height) // 2))
            for k in range(5):
                on = a > 0.12 + k * 0.06
                st = star_img(66, on)
                sx = self.w - 40 - (5 - k) * 74
                sc = 1 + 0.4 * (1 - clamp((a - 0.12 - k * 0.06) / 0.15)) if on else 1
                paste(card, st, sx + 28, ry + self.row_h / 2, scale=sc)
        paste(c.ov, card, TOP_L + self.w / 2, self.y + self.h / 2, alpha=out, scale=max(0.05, 0.85 + 0.15 * u))


class Tag:
    """Small dark pill (ingredient / size facts)."""

    def __init__(self, t0, t1, text, x, y, fill=INK, fg=WHITE):
        self.t0, self.t1, self.x, self.y = t0, t1, x, y
        t = text_img(text, "Montserrat-Bold.ttf", 44, fg)
        im = Image.new("RGBA", (t.width + 56, t.height + 30))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=fill + (225,))
        im.alpha_composite(t, (28, 15))
        self.im = im

    def sfx(self):
        return [("click", self.t0)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        u = ease_out_back((c.t - self.t0) / 0.28, 2)
        paste(c.ov, self.im, self.x, self.y, alpha=env(c.t, self.t0, self.t1, 0.05, 0.12), scale=max(0.05, u))


class YellowBag:
    """Bouncing 🛍️ + 👇 pointing at the product link, with a pulse ring."""

    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1
        self.bag = v1.emoji_img("🛍️", 150)
        self.hand = v1.emoji_img("👇", 120)

    def sfx(self):
        return [("chime", self.t0)]

    def draw(self, c):
        if c.t < self.t0:
            return
        a = c.t - self.t0
        x, y = SAFE_L + 120, 1470
        d = ImageDraw.Draw(c.ov)
        for k in range(2):
            ph = ((a * 1.4) + k * 0.5) % 1.0
            r = 70 + ph * 110
            d.ellipse((x - r, y + 60 - r, x + r, y + 60 + r), outline=YEL + (int(220 * (1 - ph)),), width=7)
        paste(c.ov, self.hand, x, y - 40 + abs(math.sin(a * 6)) * 24, scale=max(0.05, ease_out_back(a / 0.3, 2)))
        paste(c.ov, self.bag, x + 190, y + 30, scale=max(0.05, ease_out_back((a - 0.1) / 0.3, 2)) * (1 + 0.06 * math.sin(a * 8)) * 0.8,
              rot=math.sin(a * 5) * 10)


# ---------------------------------------------------------------- camera

def cut_times():
    return [s for _, s, _, _ in timeline()][1:]


def camera(fi):
    t = fi / FPS
    for n, s, e, seg in timeline():
        if s <= t < e:
            break
    z0, z1 = seg[4]
    u = (t - s) / (e - s)
    z = z0 + (z1 - z0) * (ease_out_cubic(u * 2.5) if n == "hook" else ease_in_out(u))
    z *= 1 + 0.018 * math.exp(-((t % BEAT) * 9))  # pulse on every kick
    z = max(z, 1.03)
    hh = H / (2 * z)
    return z, W / 2, clamp(H * 0.47, hh, H - hh), n, s, e


def whip(img, t):
    """Whip-pan across cuts: horizontal smear + slide in the 3 frames each side."""
    for ct in cut_times():
        a = (t - ct) * FPS  # frames from cut, negative before
        if -3 <= a < 3:
            k = 1 - abs(a + 0.5) / 3.5
            shift = int((a + 0.5) / 3 * -220)
            small = img.resize((max(8, int(W / (2 + 30 * k))), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
            img = Image.blend(img, small, clamp(0.85 * k))
            # fill the gap with the stretched edge instead of leaving black
            edge = img.crop((0, 0, 4, H)) if shift > 0 else img.crop((W - 4, 0, W, H))
            img = img.transform((W, H), Image.AFFINE, (1, 0, -shift, 0, 1, 0), Image.BILINEAR, fillcolor=None)
            if shift:
                fill = edge.resize((abs(shift), H))
                img.paste(fill, (0, 0) if shift > 0 else (W - abs(shift), 0))
            break
    return img


# ---------------------------------------------------------------- the script

def build_elements():
    S, E = seg_start, seg_end
    P = v1.Particles
    els = []

    # 1. HOOK on the used pads: curiosity + lens on the real residue
    t, e = S("hook"), E("hook")
    els.append(Caption(0.0, e - 0.02, "TENGOK APA YANG *TERANGKAT* 😳", TOP_Y, size=104, wps=6, big=True))
    els.append(Lens(0.55, e - 0.02, src_xy=(330, 520), at_xy=(780, 900), r=190))
    els.append(Caption(0.65, S("pump") - 0.05, "guna micellar water ni je 👇", 1240, size=80, wps=7))

    # 2. PRODUCT
    t, e = S("product"), E("product")
    els.append(Caption(t, e - 0.02, "O’CHEAL *MICELLAR* WATER", TOP_Y, size=92, wps=8, big=True))
    els.append(Tag(t + 0.3, e - 0.02, "300ML", 210, 560, fill=NEON))
    els.append(Tag(t + 0.5, e - 0.02, "🌹 Hyaluronic Acid + Rose", 420, 660))

    # 3. HOW I USE IT, synced to the real actions
    t, e = S("pump"), E("pump")
    els.append(StepChip(t + 0.05, e - 0.02, 1, "BASAHKAN KAPAS"))
    els.append(Caption(t + 0.35, e - 0.02, "tekan pam, kapas terus _basah_ 💦", 1240, size=80))
    t, e = S("press"), E("press")
    els.append(StepChip(t + 0.03, e - 0.02, 2, "TEKAP SEKETIKA"))
    els.append(Caption(t + 0.2, e - 0.02, "biar makeup *cair* dulu", 1240, size=80))
    t, e = S("eye"), E("eye2")
    els.append(StepChip(t + 0.03, e - 0.02, 3, "LAP PERLAHAN"))
    els.append(Caption(t + 0.2, S("eye2") - 0.03, "kat mata pun rasa *selesa*", 1240, size=80))
    els.append(Caption(S("eye2") + 0.05, e - 0.02, "_X_ _PEDAS_ langsung 🙌", 1240, size=88))

    # 4. WHY BUY: personal rating card over the real wipes
    t, e = S("wipe"), E("wipe")
    els.append(RatingCard(t + 0.03, e - 0.02, "RATING AKU 💯", ["Tanggal makeup", "X pedas", "Tak berminyak", "Mudah guna"],
                          row_gap=0.34))

    # 5. RESULT on the clean face
    t, e = S("result"), E("result")
    els.append(Caption(t + 0.05, t + 1.9, "muka *bersih,* kulit terasa _lembut_ 🤍", TOP_Y, size=92, wps=5, big=True))
    els.append(P(t + 0.2, e, "sparkle", (250, 560, 830, 1100), 9, life=(0.6, 1.2), size=(14, 28), vel=((-10, 10), (-30, 0)), seed=31))
    els.append(Caption(t + 1.95, e - 0.02, "bantu *kekalkan* kelembapan 💧", TOP_Y, size=80, wps=6, big=True))
    els.append(Tag(t + 2.1, e - 0.02, "💧 Dengan Hyaluronic Acid", 470, 1300))

    # 6. CTA on the slow-motion product shot
    t, e = S("cta"), E("cta")
    els.append(Caption(t + 0.02, e + 1, "NAK CUBA? 😍", TOP_Y, size=104, wps=6, big=True))
    els.append(Tag(t + 0.25, e + 1, "O’CHEAL Micellar Water 300ML", 470, 470, fill=NEON))
    els.append(Caption(t + 0.55, e + 1, "TEKAN *BEG* *KUNING* 🛍️", 1000, size=92, wps=7, big=True))
    els.append(Caption(t + 1.0, e + 1, "tengok harga hari ni", 1250, size=56, wps=8, max_w=900))
    els.append(YellowBag(t + 0.9, e + 1))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    for ct in cut_times():
        cues.append(("whoosh", ct - 0.2))
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


def make_music():
    # moodier trend bed: vi - IV - I - V in C (Am F C G), 104 BPM
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [60, 64, 67, 71], [55, 59, 62, 67]]
    return v1.make_music(TOTAL, bpm=BPM, chords=chords)


# ---------------------------------------------------------------- main

def render_frame(fi, img, els):
    z, cx, cy, *_ = camera(fi)
    img = v1.apply_camera(img, z, cx, cy)
    img = whip(img, fi / FPS)
    img = v1.bloom(img, 0.07)
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
    els = build_elements()
    base = ROOT / "build" / "base.mp4"
    if args.stills:
        outdir = ROOT / "build" / "stills"
        outdir.mkdir(exist_ok=True)
        want = {round(t * FPS) for t in [0.3, 1.2, 1.65, 2.4, 3.3, 4.6, 5.7, 6.9, 8.6, 9.6, 10.4, 11.1, 12.0, 13.8,
                                          15.3, 16.2, 17.2]}
        for fi, img in enumerate(v1.frames_from(base)):
            if fi in want:
                render_frame(fi, img, els).save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
        return
    wav = ROOT / "build" / "audio.wav"
    v1.make_audio(cue_list(els), wav, music=make_music())
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
