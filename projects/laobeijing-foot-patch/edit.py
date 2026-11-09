#!/usr/bin/env python3
"""Edit the Laobeijing foot patch unboxing video into a TikTok Shop ad.

Usage:  python3 edit.py SOURCE.mp4 OUTPUT.mp4
        python3 edit.py SOURCE.mp4 PREVIEW_DIR --preview

Same pipeline as the collagen soup edit:
  1. ffmpeg cuts the source into SEGMENTS, speeds the talking up a little and
     scales to 1080x1920 / 30 fps.
  2. Pillow draws the hook, captions, price card, social proof, step banners,
     product pop-ups and the end CTA on every frame, then ffmpeg encodes it.

Captions come from PHRASES: the narration was transcribed with Whisper
(small) and corrected by hand; times are in the source video's seconds.
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
W, H, FPS = 1080, 1920, 30
SP = 1.1  # speed for the talking part

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

YELLOW = (255, 222, 0)
RED = (226, 30, 45)
DARK_RED = (150, 12, 22)
GREEN = (24, 120, 70)
WHITE = (255, 255, 255)
INK = (22, 22, 22)

# ---- offer (check in the shop before posting) ----
PRICE = "RM9.99"
PRICE_OLD = "RM36.00"
DISCOUNT = "-72%"
RATING, REVIEWS, SOLD = "4.7", "6.7K", "44.3K"

# (name, src_in, src_out, speed, audio_gain)
SEGMENTS = [
    ("talk", 0.45, 25.45, SP, 1.0),    # whole narration, nothing to cut
    ("why", 24.70, 25.40, 0.3, 0.0),   # slow-mo on both feet, benefit list
    ("cta", 24.95, 25.40, 0.1, 0.0),   # near-freeze, blurred, product + price
]

# Narration, corrected by hand: (src_start, src_end, text)
PHRASES = [
    (0.55, 2.20, "Siapa-siapa yang rasa"),
    (2.20, 3.60, "lenguh-lenguh kaki,"),
    (3.60, 4.70, "kerja lama berdiri,"),
    (4.70, 6.70, "haa, belilah ni!"),
    (6.80, 8.00, "Dalam satu kotak ni"),
    (8.00, 9.30, "ada 50 keping,"),
    (9.30, 12.00, "harga pun tak mahal sangat."),
    (12.00, 13.30, "Lepas pakai ni,"),
    (13.30, 14.70, "rasa selesa betul."),
    (14.80, 16.00, "Cara pasang senang je,"),
    (16.00, 17.30, "tengok cara saya pasang."),
    (17.40, 18.50, "Ada 2 sticker,"),
    (18.60, 21.00, "bahagian yang ada bunga"),
    (21.00, 22.40, "letak dekat luar."),
    (22.50, 24.30, "Lepas tu tampal dekat sini,"),
    (24.40, 25.30, "yeay!"),
]


# ---------------------------------------------------------------- timeline
def build_timeline():
    t, out = 0.0, []
    for name, a, b, sp, g in SEGMENTS:
        d = (b - a) / sp
        out.append(dict(name=name, a=a, b=b, sp=sp, g=g, start=t, end=t + d))
        t += d
    return out, t


TL, TOTAL = build_timeline()
SEG = {s["name"]: s for s in TL}


def o(ts):
    """Source time in the talking segment -> output time."""
    s = SEG["talk"]
    return s["start"] + (min(max(ts, s["a"]), s["b"]) - s["a"]) / s["sp"]


# ---------------------------------------------------------------- base cut
def render_base(src, dst):
    parts = []
    for i, s in enumerate(TL):
        d = s["end"] - s["start"]
        part = f"{dst}.{i:02d}.mov"
        nfr = int(round(s["end"] * FPS)) - int(round(s["start"] * FPS))
        vf = f"setpts=(PTS-STARTPTS)/{s['sp']},scale={W}:{H},fps={FPS},setsar=1"
        if s["g"] > 0:
            af = (f"asetpts=PTS-STARTPTS,atempo={s['sp']},volume={s['g']},"
                  f"afade=t=in:d=0.04,afade=t=out:st={max(d - 0.08, 0)}:d=0.08,"
                  f"apad,atrim=0:{nfr / FPS}")
            ain = ["-ss", str(s["a"]), "-t", str(s["b"] - s["a"]), "-i", src]
            amap = ["-map", "0:v", "-map", "0:a"]
        else:  # silent tail: music is added in the TikTok app
            af = f"atrim=0:{nfr / FPS}"
            ain = ["-ss", str(s["a"]), "-t", str(s["b"] - s["a"]), "-i", src,
                   "-f", "lavfi", "-t", str(nfr / FPS + 0.1), "-i", "anullsrc=r=44100:cl=stereo"]
            amap = ["-map", "0:v", "-map", "1:a"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ain, *amap, "-vf", vf, "-af", af,
                        "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
                        "-threads", "2", "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", part], check=True)
        parts.append(part)
    lst = dst + ".txt"
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", dst], check=True)
    for p in parts + [lst]:
        os.remove(p)


# ---------------------------------------------------------------- drawing helpers
_fc, _ec = {}, {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


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
    return 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def pop_scale(t, t0, dur=0.35):
    return ease_out_back((t - t0) / dur) if t >= t0 else 0.0


def text_img(txt, size, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), path=FONT_BLACK):
    f = font(path, size)
    bb = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4))
    ImageDraw.Draw(im).text((-bb[0] + 2, -bb[1] + 2), txt, font=f, fill=fill,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def pill(txt, size, bg, fg=WHITE, pad=(34, 18), radius=None, emo=None, shadow=True, path=FONT_BLACK):
    t = text_img(txt, size, fg, path=path)
    e = emoji(emo, int(size * 1.05)) if emo else None
    ew = (e.width + 14) if e else 0
    w, h = t.width + ew + pad[0] * 2, max(t.height, e.height if e else 0) + pad[1] * 2
    r = radius if radius is not None else h // 2
    im = Image.new("RGBA", (w + 24, h + 24))
    if shadow:
        sh = Image.new("RGBA", im.size)
        ImageDraw.Draw(sh).rounded_rectangle((12, 20, 12 + w, 20 + h), r, fill=(0, 0, 0, 110))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).rounded_rectangle((12, 12, 12 + w, 12 + h), r, fill=bg)
    x = 12 + pad[0]
    if e:
        im.alpha_composite(e, (x, 12 + (h - e.height) // 2))
        x += ew
    im.alpha_composite(t, (x, 12 + (h - t.height) // 2))
    return im


def panel(w, h, bg=(255, 255, 255, 245), radius=40, border=None):
    im = Image.new("RGBA", (w + 40, h + 50))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((20, 32, 20 + w, 32 + h), radius, fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).rounded_rectangle((20, 20, 20 + w, 20 + h), radius, fill=bg,
                                         outline=border, width=8 if border else 0)
    return im


def card(img, width, radius=36, border=10, border_col=WHITE):
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


def stars(n, size):
    s = emoji("⭐", size)
    im = Image.new("RGBA", (n * (size + 6), s.height))
    for i in range(n):
        im.alpha_composite(s, (i * (size + 6), 0))
    return im


def stack_v(items, gap=0, align="center"):
    w = max(i.width for i in items)
    h = sum(i.height for i in items) + gap * (len(items) - 1)
    im = Image.new("RGBA", (w, h))
    y = 0
    for i in items:
        x = (w - i.width) // 2 if align == "center" else 0
        im.alpha_composite(i, (x, y))
        y += i.height + gap
    return im


def stack_h(items, gap=0):
    w = sum(i.width for i in items) + gap * (len(items) - 1)
    h = max(i.height for i in items)
    im = Image.new("RGBA", (w, h))
    x = 0
    for i in items:
        im.alpha_composite(i, (x, (h - i.height) // 2))
        x += i.width + gap
    return im


def strike(im, col=RED, width=9):
    im = im.copy()
    ImageDraw.Draw(im).line((0, im.height * 0.55, im.width, im.height * 0.5), fill=col, width=width)
    return im


# ---------------------------------------------------------------- assets
BOX = Image.open(os.path.join(ASSETS, "box.png")).convert("RGB")
FEET = Image.open(os.path.join(ASSETS, "feet.png")).convert("RGB")
GUIDE = Image.open(os.path.join(ASSETS, "caraguna.png")).convert("RGB")

BOX_CARD = card(BOX, 470, radius=28, border=8)
FEET_CARD = card(FEET, 600, radius=32, border=10)
GUIDE_CARD = card(GUIDE, 900, radius=30, border=10)

# hook
H1 = stack_h([text_img("KAKI LENGUH?", 112, WHITE, 13), emoji("😩", 104)], gap=16)
H2 = text_img("KERJA LAMA BERDIRI?", 74, YELLOW, 10)
H3 = pill(f"50 KEPING CUMA {PRICE}!", 56, RED, pad=(34, 18))
DISC = pill(DISCOUNT, 58, YELLOW, fg=INK, pad=(26, 14))

# 50 keping + price
BIG50 = text_img("50 KEPING", 170, YELLOW, 15)
BIG50_SUB = text_img("dalam 1 kotak", 60, WHITE, 8, path=FONT_BOLD)


def price_card():
    p = panel(820, 470, bg=(255, 255, 255, 250), radius=46, border=RED)
    tag = pill("HARGA TAK MAHAL", 44, RED, pad=(28, 12), shadow=False)
    old = strike(text_img(PRICE_OLD, 70, (140, 140, 140), path=FONT_BOLD))
    frm = text_img("DARI", 56, INK)
    new = text_img(PRICE, 160, RED)
    row = stack_h([frm, new], gap=18)
    content = stack_v([tag, old, row], gap=18)
    paste_center(p, content, p.width / 2, p.height / 2 - 6)
    return p


PRICE_CARD = price_card()

# social proof
def review_card():
    w = 900
    q1 = text_img("“Malam sebelum tidur pakai…", 50, INK, path=FONT_BOLD)
    q2 = text_img("bangun tidur rasa ringan badan,", 50, INK, path=FONT_BOLD)
    q3 = text_img("tapak kaki kurang sakit”", 50, INK, path=FONT_BOLD)
    who = text_img("— pembeli, review 5 bintang", 38, (110, 110, 110), path=FONT_BOLD)
    body = stack_v([stars(5, 54), q1, q2, q3, who], gap=16, align="left")
    p = panel(w, body.height + 80, radius=40)
    p.alpha_composite(body, (20 + 44, 20 + 40))
    return p


REVIEW = review_card()
PROOF = stack_h([pill(f"{RATING}  ({REVIEWS} review)", 44, INK, emo="⭐", pad=(26, 14)),
                 pill(f"{SOLD} terjual", 44, RED, emo="🔥", pad=(26, 14))], gap=4)
SELESA = pill("RASA SELESA BETUL", 58, GREEN, emo="✨", pad=(32, 16))

# steps: (src_time, label, text)
STEPS = [
    (14.80, "CARA PASANG", "SENANG JE!"),
    (17.40, "LANGKAH 1", "KOYAK STICKER BESAR"),
    (18.60, "LANGKAH 2", "LETAK PAD, BUNGA DI LUAR"),
    (22.50, "LANGKAH 3", "TAMPAL DI TAPAK KAKI"),
    (24.40, "LANGKAH 4", "PAKAI MASA TIDUR"),
]


def step_banner(a, b):
    p1 = pill(a, 40, RED, pad=(26, 12), shadow=False)
    p2 = pill(b, 56, WHITE, fg=INK, pad=(30, 16), shadow=True)
    im = Image.new("RGBA", (max(p1.width, p2.width) + 20, p1.height + p2.height - 22))
    im.alpha_composite(p2, ((im.width - p2.width) // 2, p1.height - 22))
    im.alpha_composite(p1, ((im.width - p1.width) // 2, 0))
    return im


STEP_IMGS = [(o(ts), step_banner(a, b)) for ts, a, b in STEPS]
GUIDE_T = (o(21.00), o(22.55))  # floor-only shot in the source: cover with the guide
GUIDE_PILL = pill("6 LANGKAH MUDAH", 52, RED, emo="👣", pad=(30, 14))

# why section
WHY_T = pill("KENAPA RAMAI SUKA?", 60, RED, emo="🤔", pad=(32, 16))
BENEFITS = [
    "Untuk kaki lenguh & lama berdiri",
    "Cuka buluh + arang buluh",
    "Bau herba, tak busuk",
    "Pakai malam, buka lepas 8 jam",
]
BEN_IMGS = [pill(t, 44, (255, 255, 255, 240), fg=INK, emo="✅", pad=(26, 14)) for t in BENEFITS]

# CTA
C0 = text_img("NAK CUBA?", 76, WHITE, 10)
C_OLD = strike(text_img(PRICE_OLD, 64, (230, 230, 230), 6, path=FONT_BOLD), RED, 8)
C_FROM = text_img("DARI", 60, WHITE, 8)
C_PRICE = text_img(PRICE, 180, YELLOW, 16)
C_50 = pill("50 KEPING / KOTAK", 48, WHITE, fg=INK, emo="📦", pad=(30, 14))
C_SHIP = pill("FREE SHIPPING", 48, GREEN, emo="🚚", pad=(30, 14))
C_BUY = pill("TEKAN BEG KUNING SEKARANG", 50, YELLOW, fg=INK, emo="🛒", pad=(30, 18))
ARROW = emoji("👇", 120)


# ---------------------------------------------------------------- captions
def build_captions():
    caps = []
    for a, b, txt in PHRASES:
        words = txt.split()
        oa, ob = o(a), o(b)
        step = (ob - oa) / len(words)
        caps.append(dict(start=oa, end=ob,
                         words=[(oa + i * step, oa + (i + 1) * step, w) for i, w in enumerate(words)]))
    for i in range(len(caps) - 1):
        caps[i]["end"] = caps[i + 1]["start"]
    caps[-1]["end"] = SEG["talk"]["end"]
    return caps


CAPS = build_captions()
CAP_Y = 1330


def draw_caption(base, t):
    c = next((c for c in CAPS if c["start"] <= t < c["end"]), None)
    if c is None:
        return
    size = 84
    toks = [w[2].upper() for w in c["words"]]
    space = 30

    def measure(sz):
        f = font(FONT_BLACK, sz)
        return f, [f.getbbox(x, stroke_width=10)[2] for x in toks]

    f, widths = measure(size)
    # wrap to two lines if too wide
    lines, cur, cw = [], [], 0
    for i, wd in enumerate(widths):
        if cur and cw + space + wd > 960:
            lines.append(cur)
            cur, cw = [], 0
        cw += (space if cur else 0) + wd
        cur.append(i)
    lines.append(cur)
    k = pop_scale(t, c["start"], 0.18)
    d = ImageDraw.Draw(base)
    for li, line in enumerate(lines):
        total = sum(widths[i] for i in line) + space * (len(line) - 1)
        x = (W - total) // 2
        y = CAP_Y + li * (size + 18) + (1 - k) * 30
        for i in line:
            a, b, _ = c["words"][i]
            active = a <= t < b + 0.1
            if active:
                ti = text_img(toks[i], int(size * 1.06), YELLOW, 10)
                base.alpha_composite(ti, (int(x + widths[i] / 2 - ti.width / 2), int(y - 6)))
            else:
                d.text((x, y), toks[i], font=f, fill=WHITE, stroke_width=10, stroke_fill=(0, 0, 0))
            x += widths[i] + space


# ---------------------------------------------------------------- frame
def zoom(frame, s, cx=0.5, cy=0.5):
    if abs(s - 1.0) < 1e-3:
        return frame
    w, h = int(W / s), int(H / s)
    x0, y0 = int((W - w) * cx), int((H - h) * cy)
    return frame.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


def gradient(h, top=True, alpha=170):
    g = np.linspace(alpha, 0, h) if top else np.linspace(0, alpha, h)
    a = np.repeat(g[:, None], W, 1).astype(np.uint8)
    im = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


TOP_GRAD = gradient(620, True, 160)
BOT_GRAD = gradient(760, False, 150)

# moments where the picture "punches in" (fake cuts on a single take)
PUNCH = [o(x) for x in (6.80, 12.00, 14.80, 17.40, 18.60, 22.50, 24.40)]


def render_frame(fr, t):
    seg = next(s for s in TL if s["start"] <= t < s["end"] + 1e-6)
    lt = t - seg["start"]
    name = seg["name"]

    if name == "talk":
        s = 1.0
        for p in PUNCH:
            if p <= t < p + 0.3:
                s = 1.0 + 0.07 * (1 - ease_out((t - p) / 0.3))
        if t < 3.0:  # hook: slow push-out
            s = 1.18 - 0.12 * ease_out(t / 3.0)
        fr = zoom(fr, s, 0.5, 0.45)
    elif name == "why":
        fr = zoom(fr, 1.05 + 0.05 * lt / (seg["end"] - seg["start"]), 0.5, 0.7)
        fr = Image.blend(fr, Image.new("RGB", (W, H), (0, 0, 0)), 0.25)
    else:  # cta
        fr = zoom(fr, 1.12 + 0.03 * lt / 4.5).filter(ImageFilter.GaussianBlur(16))
        fr = Image.blend(fr, Image.new("RGB", (W, H), (60, 0, 0)), 0.5)

    base = fr.convert("RGBA")
    if t < 0.12:
        base = Image.blend(base, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.8 * (1 - t / 0.12))

    if name == "cta":
        paste_center(base, C0, W / 2, 200, pop_scale(lt, 0.0))
        paste_center(base, FEET_CARD, W / 2, 600, pop_scale(lt, 0.1, 0.45), rot=-3 + 2 * math.sin(t * 3))
        paste_center(base, DISC, 860, 330, pop_scale(lt, 0.6) * (1 + 0.06 * math.sin(t * 10)), rot=12)
        paste_center(base, C_OLD, W / 2, 1010, pop_scale(lt, 0.8))
        row = stack_h([C_FROM, C_PRICE], gap=20)
        paste_center(base, row, W / 2, 1150, pop_scale(lt, 0.9) * (1 + 0.03 * math.sin(t * 8)), rot=-2)
        paste_center(base, C_50, W / 2 - 230 + 0, 1310, 0.85 * pop_scale(lt, 1.15))
        paste_center(base, C_SHIP, W / 2 + 250, 1310, 0.85 * pop_scale(lt, 1.3))
        paste_center(base, C_BUY, W / 2, 1460, pop_scale(lt, 1.6) * (1 + 0.04 * math.sin(t * 10)))
        if lt > 1.9:
            paste_center(base, ARROW, W / 2, 1610 + 25 * abs(math.sin(t * 6)), 1.0)
        return base

    if name == "why":
        base.alpha_composite(TOP_GRAD, (0, 0))
        paste_center(base, WHY_T, W / 2, 230, pop_scale(lt, 0.0))
        for i, im in enumerate(BEN_IMGS):
            k = ease_out((lt - 0.25 - 0.3 * i) / 0.3)
            if k > 0:
                paste_center(base, im, 50 + im.width / 2 - (1 - k) * 900, 420 + i * 120)
        paste_center(base, PROOF, W / 2, 1000, pop_scale(lt, 1.6))
        return base

    # ---------------- talking part
    base.alpha_composite(BOT_GRAD, (0, H - 760))

    # hook 0 - o(6.8)
    if t < o(6.8):
        base.alpha_composite(TOP_GRAD, (0, 0))
        hk = pop_scale(t, 0.05, 0.3)
        paste_center(base, H1, W / 2, 230, hk * (1 + 0.025 * math.sin(t * 9)))
        paste_center(base, H2, W / 2, 370, pop_scale(t, o(3.6)))
        paste_center(base, H3, W / 2, 500, pop_scale(t, 0.6) * (1 + 0.035 * math.sin(t * 10)), rot=-2)
        paste_center(base, BOX_CARD, 790, 900, pop_scale(t, 1.0, 0.45) * 0.9, rot=7 + 2.5 * math.sin(t * 4))
        paste_center(base, DISC, 935, 700, pop_scale(t, 1.3) * (1 + 0.06 * math.sin(t * 12)), rot=12)

    # 50 keping
    t50 = o(8.0)
    if t50 <= t < o(9.3):
        k = pop_scale(t, t50, 0.35)
        paste_center(base, BIG50, W / 2, 640, k, rot=-4)
        paste_center(base, BIG50_SUB, W / 2, 790, k)
        paste_center(base, BOX_CARD, W / 2, 1030, 0.75 * pop_scale(t, t50 + 0.15, 0.4), rot=4)

    # price
    tp = o(9.3)
    if tp <= t < o(12.0):
        paste_center(base, PRICE_CARD, W / 2, 760, pop_scale(t, tp, 0.4) * (1 + 0.012 * math.sin(t * 6)),
                     rot=-3)
        paste_center(base, DISC, 900, 520, pop_scale(t, tp + 0.3) * (1 + 0.06 * math.sin(t * 12)), rot=14)

    # comfort + social proof
    ts = o(12.0)
    if ts <= t < o(14.8):
        paste_center(base, SELESA, W / 2, 230, pop_scale(t, o(13.3)) if t >= o(13.3) else 0)
        paste_center(base, REVIEW, W / 2, 620, pop_scale(t, ts, 0.4))
        paste_center(base, PROOF, W / 2, 900, pop_scale(t, ts + 0.5))

    # steps
    if t >= STEP_IMGS[0][0] and not GUIDE_T[0] <= t < GUIDE_T[1]:
        cur = [i for i, (t0, _) in enumerate(STEP_IMGS) if t0 <= t][-1]
        t0, im = STEP_IMGS[cur]
        paste_center(base, im, W / 2, 210, pop_scale(t, t0, 0.35))

    # usage guide covers the floor-only shot
    if GUIDE_T[0] <= t < GUIDE_T[1]:
        fade = min(1.0, (GUIDE_T[1] - t) / 0.15)
        paste_center(base, GUIDE_CARD, W / 2, 800, pop_scale(t, GUIDE_T[0], 0.35), alpha=fade)
        paste_center(base, GUIDE_PILL, W / 2, 240, pop_scale(t, GUIDE_T[0] + 0.15), alpha=fade)

    draw_caption(base, t)
    return base


# ---------------------------------------------------------------- main
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
        wr.stdin.write(render_frame(fr, min(i / FPS, TOTAL - 1e-3)).convert("RGB").tobytes())
        i += 1
        if i % 150 == 0:
            print(f"{i}/{n} frames", flush=True)
    wr.stdin.close()
    wr.wait()
    rd.wait()
    os.remove(tmp)
    print("done", dst, f"{TOTAL:.1f}s")


def preview(src, outdir, times):
    os.makedirs(outdir, exist_ok=True)
    tiles = []
    for tt in times:
        if tt >= TOTAL:
            continue
        s = next(s for s in TL if s["start"] <= tt < s["end"])
        st = s["a"] + (tt - s["start"]) * s["sp"]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(st), "-i", src, "-frames:v", "1",
                              "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        im = render_frame(Image.frombuffer("RGB", (W, H), raw), tt).convert("RGB").resize((270, 480))
        ImageDraw.Draw(im).text((6, 4), f"{tt:.1f}", fill=(0, 255, 0), font=font(FONT_BLACK, 28))
        tiles.append(im)
    cols = 6
    sheet = Image.new("RGB", (270 * cols, 480 * math.ceil(len(tiles) / cols)))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
    sheet.save(os.path.join(outdir, "preview.jpg"), quality=85)
    print("total", TOTAL)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[3] == "--preview":
        preview(sys.argv[1], sys.argv[2],
                [0.2, 1.2, 2.5, 4.0, 5.5, 7.3, 8.8, 10.2, 11.0, 12.4, 13.5, 15.6,
                 17.0, 18.9, 19.6, 20.5, 21.9, 22.4, 23.3, 24.6, 25.4, 26.3, 27.5, 29.3])
    else:
        main(sys.argv[1], sys.argv[2])
