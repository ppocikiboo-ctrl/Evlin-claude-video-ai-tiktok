"""Hook-first TikTok edit of the NYO3 Daily Probiotic clip (blue background).

Usage: python3 make_hook_edit.py <original.mp4> <output.mp4> [--no-music]

Structure (cut on the beat of a 120 BPM track, 13 s):
  0.0 - 2.5   problem hook: blurred footage, "perut kembung?" + problem stickers
  2.5 - 6.0   reveal on the drop: product name, 57 billion CFU counter, specs
  6.0 - 6.5   fast spin to the back of the bottle
  6.5 - 10.5  benefit cards (from the label) with icons
  10.5 - 11.0 fast spin back to the front
  11.0 - 13.0 dosage + "tekan beg kuning" call to action with a bouncing arrow

The graphics are drawn frame by frame with Pillow into a transparent PNG
sequence, the music and sound effects are synthesised with numpy, and ffmpeg
puts it all together.
"""
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_edit import (BLACK, EMOJI, FONT, FONT_BOLD, RED, TEAL, WHITE,  # noqa: E402
                       YELLOW, H, W, FPS)

BPM = 120
BEAT = 60 / BPM
NAVY = (12, 22, 60, 225)

# (source start, source end, output duration); speed = source / output.
SEGMENTS = [
    (0.50, 3.00, 2.5),  # front, held -> blurred problem hook
    (3.00, 6.50, 3.5),  # front, held -> reveal
    (7.65, 8.65, 0.5),  # spin to the back (2x)
    (8.70, 10.55, 2.0),  # back, medium
    (10.55, 12.50, 2.0),  # back, close-up
    (12.50, 14.00, 0.5),  # spin to the front (3x)
    (14.20, 15.65, 2.0),  # front, held -> CTA
]
CUTS = np.cumsum([0] + [s[2] for s in SEGMENTS]).tolist()
TOTAL = CUTS[-1]

# Benefits as printed on the bottle's label, each with an icon.
BENEFITS = [
    ("\U0001F4A8", "Kurangkan kembung", "& angin"),
    ("\U0001F6BD", "Bantu atasi", "sembelit"),
    ("\U0001F9FB", "Kurangkan", "cirit-birit"),
    ("\U0001F95B", "Bantu masalah", "tak tahan laktosa"),
    ("\U0001F6E1️", "Sokong sistem", "imun"),
    ("\U0001F4AA", "Sihatkan", "usus"),
]


# ---------------------------------------------------------------- drawing --

_emoji_cache = {}


def emoji(ch, size):
    key = (ch, size)
    if key not in _emoji_cache:
        f = ImageFont.truetype(EMOJI, 109)
        img = Image.new("RGBA", (200, 160), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((0, 0), ch, font=f, embedded_color=True)
        img = img.crop(img.getbbox())
        _emoji_cache[key] = img.resize((size, int(size * img.height / img.width)),
                                       Image.LANCZOS)
    return _emoji_cache[key]


def font(path, size):
    return ImageFont.truetype(path, size)


def measure(text, f, stroke=0):
    l, t, r, b = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox(
        (0, 0), text, font=f, stroke_width=stroke)
    return l, t, r - l, b - t


def outlined(text, size, fill=WHITE, stroke=11, path=FONT):
    f = font(path, size)
    l, t, w, h = measure(text, f, stroke)
    img = Image.new("RGBA", (w + 24, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((12 - l + 4, 12 - t + 8), text, font=f, fill=(0, 0, 0, 120),
           stroke_width=stroke, stroke_fill=(0, 0, 0, 120))  # drop shadow
    d.text((12 - l, 12 - t), text, font=f, fill=fill, stroke_width=stroke,
           stroke_fill=BLACK)
    return img


def chip(text, size, box, fill=BLACK, icon=None, path=FONT, pad=(30, 16), radius=999):
    f = font(path, size)
    l, t, w, h = measure(text, f)
    em = emoji(icon, int(size * 1.15)) if icon else None
    ew = em.width + 14 if em else 0
    cw, ch = w + ew + 2 * pad[0], max(h, em.height if em else 0) + 2 * pad[1]
    img = Image.new("RGBA", (cw + 16, ch + 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = min(radius, ch // 2)
    d.rounded_rectangle((8, 12, cw + 8, ch + 12), r, fill=(0, 0, 0, 110))
    d.rounded_rectangle((4, 4, cw + 4, ch + 4), r, fill=box)
    x = 4 + pad[0]
    if em:
        img.alpha_composite(em, (x, 4 + (ch - em.height) // 2))
        x += ew
    d.text((x - l, 4 + (ch - h) // 2 - t), text, font=f, fill=fill)
    return img


def benefit_card(icon, line1, line2, w=470, h=250):
    img = Image.new("RGBA", (w + 12, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 10, w + 6, h + 10), 36, fill=(0, 0, 0, 100))
    d.rounded_rectangle((2, 2, w + 2, h + 2), 36, fill=(255, 255, 255, 240))
    d.rounded_rectangle((2, 2, w + 2, h + 2), 36, outline=YELLOW, width=6)
    # coloured disc so white icons (cloud, toilet, milk) stand out on the card
    cx = w // 2 + 2
    d.ellipse((cx - 62, 10, cx + 62, 134), fill=(255, 214, 0, 255))
    em = emoji(icon, 84)
    img.alpha_composite(em, (cx - em.width // 2, 72 - em.height // 2))
    for i, (txt, f) in enumerate([(line1, font(FONT_BOLD, 40)), (line2, font(FONT, 44))]):
        l, t, tw, th = measure(txt, f)
        d.text(((w - tw) // 2 + 2 - l, 136 + i * 52 - t), txt, font=f,
               fill=(20, 20, 20, 255) if i == 0 else (10, 60, 160, 255))
    return img


def arrow(size=230, color=YELLOW):
    """A chunky down-left arrow pointing at TikTok's product link."""
    img = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    pts = [(0.35, 0.0), (0.65, 0.0), (0.65, 0.55), (0.9, 0.55), (0.5, 1.0),
           (0.1, 0.55), (0.35, 0.55)]
    poly = [(10 + x * s, 10 + y * s) for x, y in pts]
    d.polygon([(x + 5, y + 7) for x, y in poly], fill=(0, 0, 0, 120))
    d.polygon(poly, fill=color, outline=BLACK, width=8)
    return img.rotate(-35, resample=Image.BICUBIC, expand=True)


# ------------------------------------------------------------- animation --

def ease_out_back(x):
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.9, 2.9
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


class Item:
    """A sprite that pops in (scale bounce) at t0 and vanishes at t1."""

    def __init__(self, img, t0, t1, cx, cy, rot=0.0, shake=0.0, bob=0.0):
        self.img, self.t0, self.t1 = img, t0, t1
        self.cx, self.cy, self.rot, self.shake, self.bob = cx, cy, rot, shake, bob

    def draw(self, frame, t):
        if not (self.t0 <= t < self.t1):
            return
        k = (t - self.t0) / 0.22
        s = 0.35 + 0.65 * ease_out_back(k)
        img = self.img
        if self.rot:
            img = img.rotate(self.rot, resample=Image.BICUBIC, expand=True)
        if abs(s - 1) > 1e-3:
            img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))),
                             Image.BILINEAR)
        if k < 0.5:
            a = img.getchannel("A").point(lambda v: int(v * min(1, k * 2)))
            img.putalpha(a)
        dx = dy = 0.0
        if self.shake and t - self.t0 < 0.6:
            dx = self.shake * math.sin((t - self.t0) * 70)
        if self.bob:
            dy = self.bob * abs(math.sin((t - self.t0) * math.pi * 2 / (BEAT * 2) * 2))
        frame.alpha_composite(img, (int(self.cx - img.width / 2 + dx),
                                    int(self.cy - img.height / 2 + dy)))


class Counter:
    """57 BILION CFU counting up in a navy panel, with microbes floating around."""

    def __init__(self, t0, t1, cx, cy, target=57):
        self.t0, self.t1, self.cx, self.cy, self.target = t0, t1, cx, cy, target
        self.label = outlined("BILION CFU", 54, fill=WHITE, stroke=8)
        self.panel = Image.new("RGBA", (470, 300), (0, 0, 0, 0))
        d = ImageDraw.Draw(self.panel)
        d.rounded_rectangle((8, 14, 466, 296), 40, fill=(0, 0, 0, 110))
        d.rounded_rectangle((0, 0, 458, 284), 40, fill=NAVY, outline=YELLOW, width=6)
        self.microbes = [(-250, -120, 0.0), (250, -150, 0.7), (-255, 120, 1.3),
                         (270, 110, 2.1), (-120, -200, 2.7), (140, 190, 3.3)]

    def draw(self, frame, t):
        if not (self.t0 <= t < self.t1):
            return
        dt = t - self.t0
        p = self.panel.copy()
        n = int(round(self.target * min(1, (dt / 0.8)) ** 0.6))
        num = outlined(str(n), 150, fill=YELLOW, stroke=10)
        p.alpha_composite(num, ((458 - num.width) // 2, -8))
        p.alpha_composite(self.label, ((458 - self.label.width) // 2, 180))
        Item(p, self.t0, self.t1, self.cx, self.cy).draw(frame, t)
        for i, (ox, oy, ph) in enumerate(self.microbes):
            if dt < 0.15 + i * 0.08:
                continue
            e = emoji("\U0001F9A0", 70 + (i % 3) * 14)
            x = self.cx + ox + 18 * math.sin(dt * 2.4 + ph)
            y = self.cy + oy + 22 * math.cos(dt * 2.0 + ph)
            e = e.rotate(20 * math.sin(dt * 3 + ph), resample=Image.BICUBIC, expand=True)
            frame.alpha_composite(e, (int(x - e.width / 2), int(y - e.height / 2)))


def build_timeline():
    c = CUTS
    items = []
    # 1. problem hook
    items += [
        Item(outlined("PERUT KEMBUNG", 104), 0.05, c[1], W / 2, 560),
        Item(outlined("LEPAS MAKAN?", 128, fill=YELLOW), 0.30, c[1], W / 2, 700, shake=14),
        Item(chip("Kembung", 54, RED, WHITE, "\U0001F623"), 0.80, c[1], 330, 900, rot=6),
        Item(chip("Banyak angin", 54, WHITE, BLACK, "\U0001F4A8"), 1.20, c[1], 700, 1030, rot=-5),
        Item(chip("Susah buang air", 54, YELLOW, BLACK, "\U0001F6BD"), 1.60, c[1], 420, 1160, rot=4),
        Item(outlined("cuba yang ni...", 60, path=FONT_BOLD, stroke=8), 2.00, c[1], W / 2, 1340),
    ]
    # 2. reveal + specs
    items += [
        Item(chip("NYO3 Daily Probiotic", 64, WHITE, BLACK, radius=28), c[1] + 0.05, c[2], W / 2, 230),
        Item(chip("Pride of Norway", 42, TEAL, BLACK, "\U0001F1F3\U0001F1F4"), c[1] + 0.35, c[2], W / 2, 335),
        Counter(c[1] + 0.75, c[2], 340, 600),
        Item(chip("7 STRAIN PROBIOTIK", 46, YELLOW, BLACK, "\U0001F9EC"), c[1] + 2.0, c[2], 330, 840),
        Item(chip("60 KAPSUL", 46, RED, WHITE, "\U0001F48A"), c[1] + 2.5, c[2], 230, 950),
    ]
    # 3. benefit cards in a 2x3 grid
    items.append(Item(outlined("KEBAIKAN DIA", 96, fill=YELLOW), c[3] + 0.05, c[5], W / 2, 210))
    for i, (icon, l1, l2) in enumerate(BENEFITS):
        col, row = i % 2, i // 2
        items.append(Item(benefit_card(icon, l1, l2), c[3] + 0.4 + i * 0.45, c[5],
                          290 + col * 500, 470 + row * 280, rot=(-2 if col == 0 else 2)))
    # 4. dosage + CTA
    items += [
        Item(chip("1-2 kapsul sehari je", 52, TEAL, BLACK, "\U0001F48A"), c[6] + 0.05, TOTAL, W / 2, 230),
        Item(outlined("TEKAN BEG KUNING", 104, fill=YELLOW), c[6] + 0.5, TOTAL, W / 2, 400, shake=10),
        Item(chip("Order sekarang!", 58, RED, WHITE, "\U0001F6D2"), c[6] + 0.75, TOTAL, W / 2, 545),
        Item(arrow(), c[6] + 0.9, TOTAL, 230, 1300, bob=50),
    ]
    return items


def render_frames(d):
    items = build_timeline()
    n = int(round(TOTAL * FPS))
    for i in range(n):
        t = i / FPS
        frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for it in items:
            it.draw(frame, t)
        frame.save(os.path.join(d, f"g{i:04d}.png"), compress_level=1)
    pops = sorted({round(it.t0, 3) for it in items})
    return pops


# ------------------------------------------------------------------ audio --

SR = 44100


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)


def clap(rng):
    n = int(0.2 * SR)
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0)  # crude high-pass
    return noise * env(n, 0.001, 0.05) * 0.5


def hat(rng):
    n = int(0.05 * SR)
    noise = np.diff(np.diff(rng.standard_normal(n), prepend=0), prepend=0)
    return noise * env(n, 0.0005, 0.012) * 0.25


def bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    return s * env(n, 0.005, dur * 0.6) * 0.45


def pluck(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * freq * k * t) / k for k in (1, 2, 3, 4))
    return s * env(n, 0.002, 0.18) * 0.12


def whoosh(rng, dur=0.45):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    a = 0.0
    for_alpha = np.linspace(0.02, 0.35, n) ** 1.5  # sweep a one-pole low-pass up
    for i in range(n):
        a += for_alpha[i] * (noise[i] - a)
        out[i] = a
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.9


def riser(rng, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR)
    return (tone * 0.15 + whoosh(rng, dur) * 0.5) * (t / dur) ** 2


def impact():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 30 + 90 * np.exp(-t / 0.08)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.35) * 1.1


def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (600 + 2200 * t) * t) * env(n, 0.001, 0.03) * 0.35


def ding():
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * env(n, 0.002, 0.25) * 0.25


def lowpass(x, alpha):
    y = np.zeros_like(x)
    a = 0.0
    for i, v in enumerate(x):
        a += alpha * (v - a)
        y[i] = a
    return y


def make_audio(path, pops, music=True):
    rng = np.random.default_rng(7)
    n = int(TOTAL * SR) + SR
    mus = np.zeros(n)
    sfx = np.zeros(n)
    if music:
        roots = [55.0, 43.65, 65.41, 49.0]  # A1 F1 C2 G1, one bar each
        chord = {55.0: [440, 523.25, 659.25], 43.65: [349.23, 440, 523.25],
                 65.41: [392, 523.25, 659.25], 49.0: [392, 493.88, 587.33]}
        k, cl, beats = kick(), clap(rng), int(TOTAL / BEAT)
        for b in range(beats):
            t = b * BEAT
            root = roots[(b // 4) % 4]
            place(mus, k, t, 0.9)
            if b % 2 == 1:
                place(mus, cl, t, 0.8)
            place(mus, hat(rng), t + BEAT / 2)
            place(mus, bass(root, BEAT * 0.9), t + BEAT / 2)
            if b % 2 == 0:
                for j, f in enumerate(chord[root]):
                    place(mus, pluck(f, 0.4), t + j * BEAT / 4)
        # hook plays muffled, the drop opens the filter at the reveal
        h = int(CUTS[1] * SR)
        mus[:h] = lowpass(mus[:h], 0.06) * 0.9
        mus[h - int(0.02 * SR): h] = 0
    place(sfx, riser(rng, 1.2), CUTS[1] - 1.2, 0.8)
    place(sfx, impact(), CUTS[1])
    for c in CUTS[2:-1]:
        place(sfx, whoosh(rng), c - 0.25, 0.7)
    for t in pops:
        place(sfx, pop(), t)
    place(sfx, ding(), CUTS[6] + 0.5)
    mix = mus * 0.55 + sfx
    mix = np.tanh(mix * 1.2) * 0.85
    mix = mix[: int(TOTAL * SR)]
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ video --

def zoom(dur, punch, push=0.07):
    p = f"{punch}*pow(max(0\\,1-t/0.28)\\,2)"
    return f"(1.05+{p}+{push}*t/{dur})"


def main(src, out, music=True):
    d = tempfile.mkdtemp()
    pops = render_frames(d)
    wav = os.path.join(d, "audio.wav")
    make_audio(wav, pops, music)

    fc, labels = [], []
    for i, (s, e, dur) in enumerate(SEGMENTS):
        sp = (e - s) / dur
        z = zoom(dur, 0.0 if i == 0 else 0.25)
        chain = (f"[0:v]trim={s}:{e},setpts=(PTS-STARTPTS)/{sp:.4f},fps={FPS},"
                 f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,"
                 f"crop={W}:{H},setsar=1")
        if i == 0:  # blurred, dark, desaturated problem shot
            chain += ",boxblur=18:2,eq=brightness=-0.18:saturation=0.5"
        fc.append(chain + f",trim=0:{dur},setpts=PTS-STARTPTS[v{i}]")
        labels.append(f"[v{i}]")
    fc.append(f"{''.join(labels)}concat=n={len(SEGMENTS)}:v=1:a=0[vc]")
    flash = "+".join(f"between(t\\,{c:.3f}\\,{c + 0.07:.3f})" for c in CUTS[1:-1])
    fc.append(
        "[vc]eq=contrast=1.10:saturation=1.25:brightness=0.01,unsharp=5:5:0.6,"
        "vignette=PI/5,"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='{flash}'[vg]")
    fc.append("[vg][1:v]overlay=0:0:format=auto[vout]")

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src,
           "-framerate", str(FPS), "-i", os.path.join(d, "g%04d.png"), "-i", wav,
           "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "2:a",
           "-t", f"{TOTAL:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
           "-ac", "2", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"wrote {out} ({TOTAL:.2f}s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], music="--no-music" not in sys.argv[3:])
