#!/usr/bin/env python3
"""Edit the Red Sea Herbs collagen soup cooking video into a TikTok Shop ad.

Usage:  python3 edit.py SOURCE.mp4 OUTPUT.mp4

Pipeline
  1. ffmpeg cuts the source into the segments in SEGMENTS (dead air, repeated
     lines and fumbling removed), speeds the talking parts up slightly and
     scales to 1080x1920.
  2. This script reads those frames back, draws the hook, word-by-word
     captions, step banners, ingredient call-outs, product pop-ups and the
     end CTA with Pillow, and encodes the final video with the cut audio.

assets/transcript.json is the Whisper transcript (with word timings) of the
source narration; captions are built from it.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
W, H, FPS = 1080, 1920, 30
SP = 1.15  # speed for talking segments

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

YELLOW = (255, 222, 0)
RED = (232, 35, 60)
GREEN = (24, 92, 62)
CREAM = (255, 248, 230)

# (name, src_in, src_out, speed, audio_gain)
SEGMENTS = [  # timings for the full-quality source (5 parts joined in order)
    ("hook", 103.0, 106.1, 1.0, 0.0),
    ("intro", 0.00, 5.46, SP, 1.0),
    ("items", 5.46, 8.05, SP, 1.0),
    ("soak", 14.40, 29.18, SP, 1.0),
    ("dry", 29.16, 36.40, SP, 1.0),
    ("water", 36.45, 40.35, SP, 1.0),
    ("dates", 41.85, 45.75, SP, 1.0),
    ("gum", 53.85, 56.80, SP, 1.0),
    ("lotus", 60.40, 64.05, SP, 1.0),
    ("boil", 71.75, 75.45, SP, 1.0),
    ("sugar", 82.70, 88.55, SP, 1.0),
    ("nest", 89.30, 92.70, SP, 1.0),
    ("stir", 96.05, 99.35, SP, 1.0),
    ("lid", 108.60, 110.90, SP, 1.0),
    ("cta", 99.60, 104.10, 1.0, 0.0),
]

# Spelling fixes for the auto-transcript.
FIX = {"telongan": "longan", "telongan.": "longan.", "melakak": "Melaka",
       "melakak.": "Melaka.", "melaka": "Melaka", "melaka.": "Melaka.", "geta": "getah",
       "juci": "cuci", "akhir,": "akhir,", "1500": "1500ML", "ml": None, "just": "just"}


# ---------------------------------------------------------------- timeline
def build_timeline():
    t = 0.0
    out = []
    for name, a, b, sp, g in SEGMENTS:
        d = (b - a) / sp
        out.append(dict(name=name, a=a, b=b, sp=sp, g=g, start=t, end=t + d))
        t += d
    return out, t


TL, TOTAL = build_timeline()
SEG = {s["name"]: s for s in TL}


def src2out(ts):
    """Map a source timestamp to output time (first segment containing it)."""
    for s in TL:
        if s["g"] > 0 and s["a"] - 0.05 <= ts <= s["b"] + 0.05:
            return s["start"] + (min(max(ts, s["a"]), s["b"]) - s["a"]) / s["sp"]
    return None


# ---------------------------------------------------------------- base cut
def render_base(src, dst):
    """Cut each segment to its own file (low memory), then concat."""
    parts = []
    for i, s in enumerate(TL):
        d = s["end"] - s["start"]
        part = f"{dst}.{i:02d}.mp4"
        nfr = int(round(s["end"] * FPS)) - int(round(s["start"] * FPS))
        vf = f"setpts=(PTS-STARTPTS)/{s['sp']},scale={W}:{H},fps={FPS},setsar=1"
        af = (f"asetpts=PTS-STARTPTS,atempo={s['sp']},volume={max(s['g'], 0.25)},"
              f"afade=t=in:d=0.04,afade=t=out:st={max(d - 0.06, 0)}:d=0.06,"
              f"apad,atrim=0:{nfr / FPS}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["a"]), "-t", str(s["b"] - s["a"]),
                        "-i", src, "-vf", vf, "-af", af, "-frames:v", str(nfr),
                        "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-threads", "2",
                        "-c:a", "pcm_s16le", "-ar", "44100", part.replace(".mp4", ".mov")], check=True)
        parts.append(part.replace(".mp4", ".mov"))
    lst = dst + ".txt"
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", dst], check=True)
    for p in parts + [lst]:
        os.remove(p)


# ---------------------------------------------------------------- drawing helpers
_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


_ec = {}


def emoji(ch, size):
    k = (ch, size)
    if k not in _ec:
        im = Image.new("RGBA", (160, 160))
        ImageDraw.Draw(im).text((10, 10), ch, font=font(FONT_EMOJI, 109), embedded_color=True)
        im = im.crop(im.getbbox())
        _ec[k] = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    return _ec[k]


def ease_out_back(x):
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def pop_scale(t, t0, dur=0.35):
    return ease_out_back((t - t0) / dur) if t >= t0 else 0.0


def text_img(txt, size, fill=(255, 255, 255), stroke=0, stroke_fill=(0, 0, 0), path=FONT_BLACK):
    f = font(path, size)
    bb = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4))
    ImageDraw.Draw(im).text((-bb[0] + 2, -bb[1] + 2), txt, font=f, fill=fill,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def pill(txt, size, bg, fg=(255, 255, 255), pad=(34, 18), radius=None, emo=None, shadow=True):
    t = text_img(txt, size, fg)
    e = emoji(emo, int(size * 1.05)) if emo else None
    ew = (e.width + 14) if e else 0
    w, h = t.width + ew + pad[0] * 2, max(t.height, e.height if e else 0) + pad[1] * 2
    r = radius if radius is not None else h // 2
    im = Image.new("RGBA", (w + 24, h + 24))
    d = ImageDraw.Draw(im)
    if shadow:
        sh = Image.new("RGBA", im.size)
        ImageDraw.Draw(sh).rounded_rectangle((12, 20, 12 + w, 20 + h), r, fill=(0, 0, 0, 110))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(8)))
        d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, 12 + w, 12 + h), r, fill=bg)
    x = 12 + pad[0]
    if e:
        im.alpha_composite(e, (x, 12 + (h - e.height) // 2))
        x += ew
    im.alpha_composite(t, (x, 12 + (h - t.height) // 2))
    return im


def card(img, width, radius=36, border=10, border_col=(255, 255, 255)):
    im = img.convert("RGBA")
    im = im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)
    w, h = im.size
    mask = Image.new("L", (w, h))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    out = Image.new("RGBA", (w + 2 * border + 40, h + 2 * border + 40))
    sh = Image.new("RGBA", out.size)
    ImageDraw.Draw(sh).rounded_rectangle((20, 30, 20 + w + 2 * border, 30 + h + 2 * border),
                                         radius + border, fill=(0, 0, 0, 140))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(out).rounded_rectangle((20, 20, 20 + w + 2 * border, 20 + h + 2 * border),
                                          radius + border, fill=border_col)
    im.putalpha(mask)
    out.alpha_composite(im, (20 + border, 20 + border))
    return out


def circle(img, d, border=8):
    im = img.convert("RGBA").resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d))
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new("RGBA", (d + 2 * border, d + 2 * border))
    ImageDraw.Draw(out).ellipse((0, 0, d + 2 * border - 1, d + 2 * border - 1), fill=(255, 255, 255))
    im.putalpha(m)
    out.alpha_composite(im, (border, border))
    return out


def paste_center(base, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


# ---------------------------------------------------------------- assets
promo = Image.open(os.path.join(ASSETS, "promo.png")).convert("RGB")
bowl = Image.open(os.path.join(ASSETS, "bowl.png")).convert("RGB")
ingr = Image.open(os.path.join(ASSETS, "ingr.png")).convert("RGB")

BAG = card(promo.crop((300, 310, 800, 950)), 400, radius=28, border=8)
BAG_BIG = card(promo.crop((300, 310, 800, 950)), 520, radius=32, border=10)
BADGES = [circle(promo.crop(b), 150, 6) for b in
          [(932, 318, 1064, 450), (932, 466, 1064, 598), (932, 618, 1064, 750)]]
INGR_CARD = card(ingr, 760)
BOWL_CARD = card(bowl, 640)
PROMO_CARD = card(promo, 820)

# ---------------------------------------------------------------- captions
def build_captions():
    words = []
    for seg in json.load(open(os.path.join(ASSETS, "transcript.json"))):
        for a, b, w in seg["words"]:
            w = w.strip()
            if w in FIX:
                w = FIX[w]
                if w is None:
                    continue
            oa, ob = src2out(a), src2out(b)
            if oa is None or ob is None or ob - oa < 0.01 and oa is None:
                continue
            words.append([oa, max(ob, oa + 0.08), w])
    # drop words whose time falls into a cut (e.g. hook/cta reuse)
    groups, cur = [], []
    for wd in words:
        cur.append(wd)
        txt = " ".join(x[2] for x in cur)
        if len(cur) >= 3 or len(txt) > 16 or wd[2][-1] in ",." :
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    caps = []
    for i, g in enumerate(groups):
        start = g[0][0]
        end = g[-1][1] + 0.35
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0][0])
        caps.append(dict(start=start, end=end, words=g))
    return caps


CAPS = build_captions()
CAP_Y = 1300


def draw_caption(base, t):
    for c in CAPS:
        if c["start"] <= t < c["end"]:
            break
    else:
        return
    size = 84
    f = font(FONT_BLACK, size)
    toks = [w[2].upper().rstrip(",.") for w in c["words"]]
    space = 34
    widths = [f.getbbox(x, stroke_width=10)[2] for x in toks]
    total = sum(widths) + space * (len(toks) - 1)
    if total > 940:
        size = int(size * 940 / total)
        f = font(FONT_BLACK, size)
        widths = [f.getbbox(x, stroke_width=10)[2] for x in toks]
        total = sum(widths) + space * (len(toks) - 1)
    x = (W - total) // 2
    k = pop_scale(t, c["start"], 0.18)
    d = ImageDraw.Draw(base)
    for (a, b, _), tok, wdt in zip(c["words"], toks, widths):
        active = a <= t < (b + 0.15)
        col = YELLOW if active else (255, 255, 255)
        y = CAP_Y + (1 - k) * 30
        if active:
            ti = text_img(tok, int(size * 1.06), col, 10)
            base.alpha_composite(ti, (int(x + wdt / 2 - ti.width / 2), int(y - (ti.height - size) / 2 - 4)))
        else:
            d.text((x, y), tok, font=f, fill=col, stroke_width=10, stroke_fill=(0, 0, 0))
        x += wdt + space


# ---------------------------------------------------------------- overlays per section
STEPS = [
    ("soak", "LANGKAH 1", "RENDAM 24 JAM"),
    ("dry", "LANGKAH 2", "CUCI SAHAJA"),
    ("water", "LANGKAH 3", "DIDIH 1.5L AIR"),
    ("dates", "LANGKAH 4", "MASUKKAN BAHAN"),
    ("gum", "LANGKAH 4", "MASUKKAN BAHAN"),
    ("lotus", "LANGKAH 4", "MASUKKAN BAHAN"),
    ("boil", "LANGKAH 5", "REBUS 45 MINIT"),
    ("sugar", "LANGKAH 6", "5 MINIT TERAKHIR"),
    ("nest", "LANGKAH 6", "5 MINIT TERAKHIR"),
    ("stir", "SIAP!", "SEDAP & BERJELI"),
    ("lid", "SIAP!", "SEDAP & BERJELI"),
]
_step_cache = {}


def step_banner(a, b):
    k = (a, b)
    if k not in _step_cache:
        p1 = pill(a, 40, RED, pad=(26, 12), shadow=False)
        p2 = pill(b, 54, (255, 255, 255), fg=(20, 20, 20), pad=(30, 16), shadow=True)
        im = Image.new("RGBA", (max(p1.width, p2.width) + 20, p1.height + p2.height - 22))
        im.alpha_composite(p2, ((im.width - p2.width) // 2, p1.height - 22))
        im.alpha_composite(p1, ((im.width - p1.width) // 2, 0))
        _step_cache[k] = im
    return _step_cache[k]


def section_start(name):
    """First time a step label appears (so repeated labels don't re-pop)."""
    label = dict((n, (a, b)) for n, a, b in STEPS)[name]
    for n, a, b in STEPS:
        if (a, b) == label:
            return SEG[n]["start"]


def callouts():
    """(text, emoji, src_time, bg) ingredient pills triggered by narration."""
    return [
        ("Sarang Burung Salji", "🤍", 15.20, GREEN),
        ("Biji Teratai Salji", "🌸", 17.64, GREEN),
        ("Getah Peach", "🍑", 19.90, GREEN),
        ("Kurma Merah", "❤️", 29.74, GREEN),
        ("Longan Kering", "🟤", 30.88, GREEN),
        ("Gula Melaka", "🍯", 32.10, GREEN),
    ]


CALL = [(pill(t, 50, bg, emo=e), src2out(ts), ts) for t, e, ts, bg in callouts()]

BIG_NUMS = [  # (text, sub, out_time, duration, color)
    ("24 JAM", "rendam dalam peti sejuk", src2out(26.02), 2.2, YELLOW),
    ("1.5 LITER", "air (1500ml)", src2out(38.38), 1.9, YELLOW),
    ("45 MINIT", "masa rebus", src2out(73.54), 1.8, YELLOW),
]
BIG_IMGS = [(text_img(a, 150, c, 12), text_img(s, 54, (255, 255, 255), 7, path=FONT_BOLD), t, d)
            for a, s, t, d, c in BIG_NUMS]

BENEFITS = [
    ("Tanpa bahan pengawet", "✅"),
    ("Gred bersih, pilihan tangan", "✅"),
    ("Sedap panas atau sejuk", "✅"),
    ("Cukup untuk 4–6 orang", "✅"),
]
BEN_IMGS = [pill(t, 44, (255, 255, 255, 235), fg=(25, 25, 25), emo=e, pad=(26, 14)) for t, e in BENEFITS]

# Hook texts
H1 = text_img("RAHSIA CANTIK DARI DALAM", 52, (255, 255, 255), 7)
H2 = text_img("RM9 JE DAPAT", 104, (255, 255, 255), 12)
H3 = text_img("4-6 MANGKUK", 128, YELLOW, 13)
H4 = text_img("SUP COLLAGEN!", 118, (255, 255, 255), 13)
FLASH = pill("FLASH SALE", 46, RED, emo="⚡", pad=(26, 14))

# CTA texts
C0 = text_img("NAK CUBA?", 70, (255, 255, 255), 9)
C1 = text_img("RM9.76", 190, YELLOW, 16)
C2 = pill("FREE SHIPPING", 52, GREEN, emo="🚚", pad=(30, 14))
C3 = pill("TEKAN BEG KUNING SEKARANG", 50, YELLOW, fg=(20, 20, 20), emo="🛒", pad=(30, 18))
ARROW = emoji("👇", 120)


def zoom(frame, s, cx=0.5, cy=0.5):
    if abs(s - 1.0) < 1e-3:
        return frame
    w, h = int(W / s), int(H / s)
    x0 = int((W - w) * cx)
    y0 = int((H - h) * cy)
    return frame.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


def gradient(h, top=True, alpha=170):
    g = np.linspace(alpha, 0, h) if top else np.linspace(0, alpha, h)
    a = np.repeat(g[:, None], W, 1).astype(np.uint8)
    im = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


TOP_GRAD = gradient(520, True, 150)
BOT_GRAD = gradient(700, False, 140)


def render_frame(fr, t):
    hook, cta = SEG["hook"], SEG["cta"]
    seg = next(s for s in TL if s["start"] <= t < s["end"] + 1e-6)
    lt = t - seg["start"]

    # --- camera motion: punch-in at each cut, slow push on hook/cta
    if seg["name"] == "hook":
        s = 1.25 - 0.12 * ease_out(lt / 3.1)
        fr = zoom(fr, s, 0.55, 0.42)
    elif seg["name"] == "cta":
        fr = zoom(fr, 1.1 + 0.03 * lt / 4.5).filter(ImageFilter.GaussianBlur(14))
        fr = Image.blend(fr, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    else:
        s = 1.0 + 0.07 * (1 - ease_out(lt / 0.3))
        fr = zoom(fr, s)

    base = fr.convert("RGBA")

    # white flash at very start
    if t < 0.12:
        base = Image.blend(base, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.8 * (1 - t / 0.12))

    if seg["name"] == "hook":
        base.alpha_composite(TOP_GRAD, (0, 0))
        paste_center(base, H1, W / 2, 230, pop_scale(t, 0.05, 0.3))
        paste_center(base, H2, W / 2, 360, pop_scale(t, 0.25))
        wob = 1 + 0.04 * math.sin(t * 9) if t > 0.9 else 1
        paste_center(base, H3, W / 2, 505, pop_scale(t, 0.5) * wob, rot=-3)
        paste_center(base, H4, W / 2, 650, pop_scale(t, 0.75))
        paste_center(base, BAG, 760, 1180, pop_scale(t, 1.1, 0.45) * 0.95, rot=8 + 3 * math.sin(t * 4))
        paste_center(base, FLASH, 760, 880, pop_scale(t, 1.4) * (1 + 0.05 * math.sin(t * 12)), rot=8)
        return base

    if seg["name"] == "cta":
        paste_center(base, C0, W / 2, 230, pop_scale(lt, 0.0))
        paste_center(base, BAG_BIG, W / 2, 680, pop_scale(lt, 0.1, 0.45), rot=-3 + 2 * math.sin(t * 3))
        for i, bdg in enumerate(BADGES):
            bx, by = [(150, 560), (930, 470), (930, 760)][i]
            paste_center(base, bdg, bx, by, 0.85 * pop_scale(lt, 0.6 + 0.15 * i))
        paste_center(base, C1, W / 2, 1120, pop_scale(lt, 0.9) * (1 + 0.03 * math.sin(t * 8)), rot=-2)
        paste_center(base, C2, W / 2, 1270, pop_scale(lt, 1.15))
        paste_center(base, C3, W / 2, 1430, pop_scale(lt, 1.5) * (1 + 0.04 * math.sin(t * 10)))
        if lt > 1.8:
            paste_center(base, ARROW, W / 2, 1580 + 25 * abs(math.sin(t * 6)), 1.0)
        return base

    base.alpha_composite(BOT_GRAD, (0, H - 700))

    # --- intro: product bag + badges
    if seg["name"] == "intro":
        base.alpha_composite(TOP_GRAD, (0, 0))
        for i, bdg in enumerate(BADGES):
            paste_center(base, bdg, 930, 330 + i * 185, pop_scale(lt, 0.4 + 0.25 * i))
        nm = pill("RED SEA HERBS • COLLAGEN SOUP", 44, GREEN, pad=(28, 14))
        paste_center(base, nm, W / 2 - 60, 200, pop_scale(lt, 0.15))

    # --- 6 items: ingredients image pops out
    if seg["name"] == "items":
        paste_center(base, INGR_CARD, W / 2, 720, pop_scale(lt, 0.0, 0.4), rot=-2)
        paste_center(base, pill("6 BAHAN DALAM 1 PEK", 54, RED, emo="🎁"), W / 2, 260,
                     pop_scale(lt, 0.25))

    # --- step banner
    names = [n for n, _, _ in STEPS]
    if seg["name"] in names:
        _, a, b = STEPS[names.index(seg["name"])]
        t0 = section_start(seg["name"])
        paste_center(base, step_banner(a, b), W / 2, 210, pop_scale(t, t0, 0.35))

    # --- ingredient callouts (stack, each lives until end of its segment)
    stack = [c for c in CALL if c[1] is not None and c[1] <= t]
    stack = [c for c in stack if next(s for s in TL if s["start"] <= c[1] < s["end"])["name"] == seg["name"]]
    for i, (im, t0, _) in enumerate(stack):
        k = ease_out((t - t0) / 0.3)
        x = 60 + im.width / 2 - (1 - k) * 700
        paste_center(base, im, x, 420 + i * 112, 1.0)

    # --- big numbers
    for big, sub, t0, dur in BIG_IMGS:
        if t0 is not None and t0 <= t < t0 + dur:
            k = pop_scale(t, t0, 0.35)
            fade = min(1.0, (t0 + dur - t) / 0.2)
            paste_center(base, big, W / 2, 820, k, rot=-4, alpha=fade)
            paste_center(base, sub, W / 2, 940, k, alpha=fade)

    # --- result: bowl pop + benefits
    if seg["name"] == "stir":
        paste_center(base, BOWL_CARD, W / 2, 760, pop_scale(lt, 0.2, 0.45) * (1 + 0.01 * math.sin(t * 5)),
                     rot=3)
        paste_center(base, pill("HASILNYA...", 56, RED, emo="🤤", pad=(30, 14)), W / 2, 380,
                     pop_scale(lt, 0.45))
    if seg["name"] == "lid":
        for i, im in enumerate(BEN_IMGS):
            k = ease_out((lt - 0.12 * i) / 0.3)
            if k > 0:
                paste_center(base, im, 60 + im.width / 2 - (1 - k) * 800, 440 + i * 108)

    draw_caption(base, t)
    return base


def main(src, dst):
    tmp = dst + ".base.mp4"
    render_base(src, tmp)
    n = int(round(TOTAL * FPS))
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", tmp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", tmp,
                           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                           "-preset", "medium", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                           "-movflags", "+faststart", "-shortest", dst], stdin=subprocess.PIPE)
    i = 0
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = Image.frombuffer("RGB", (W, H), buf)
        out = render_frame(fr, min(i / FPS, TOTAL - 1e-3)).convert("RGB")
        wr.stdin.write(out.tobytes())
        i += 1
        if i % 150 == 0:
            print(f"{i}/{n} frames", flush=True)
    wr.stdin.close()
    wr.wait()
    rd.wait()
    os.remove(tmp)
    print("done", dst, f"{TOTAL:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[3] == "--preview":
        # render single frames at given output times for checking
        src, outdir = sys.argv[1], sys.argv[2]
        os.makedirs(outdir, exist_ok=True)
        for tt in [0.4, 1.0, 2.0, 3.0, 4.5, 7.0, 9.0, 11.0, 15.5, 20.0, 24.5, 30.0, 34.5, 38.0,
                   42.0, 47.0, 50.0, 54.0, 58.0, 61.0, 63.5, 64.5, 66.0, 67.5]:
            if tt >= TOTAL:
                continue
            s = next(s for s in TL if s["start"] <= tt < s["end"])
            st = s["a"] + (tt - s["start"]) * s["sp"]
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(st), "-i", src, "-frames:v", "1",
                                  "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                 capture_output=True).stdout
            fr = Image.frombuffer("RGB", (W, H), raw)
            render_frame(fr, tt).convert("RGB").resize((360, 640)).save(f"{outdir}/f_{tt:05.1f}.jpg")
        print("total", TOTAL)
    else:
        main(sys.argv[1], sys.argv[2])
