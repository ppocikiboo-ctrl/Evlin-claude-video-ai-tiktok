"""Durimex Coffee — VERSION 4 (stirring clip, "3 SEBAB" listicle, green brand look).

Different look from v1: warm cinematic grade + vignette + grain, coffee-brown /
cream / orange palette, kinetic word-by-word captions on marker boxes, chapter
tags + segmented story bar, flash/shake transitions, magnified label inset
(real label text, highlighted), spec cards with count-up numbers, synthesized
lo-fi music bed with voice ducking, boom/riser/tick/ding SFX.

Structure: HOOK -> FEATURES -> PROOF -> BENEFITS (emotion) -> WHY NOW -> CTA.
Usage: python3 render4.py cut.mov box_video.mp4 out.mp4  (box_video = original box clip, for the coffee photo)
"""
import sys, json, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, sys.path[0])
from gfx import (stroke_text, ingredient_card, font, shadow, black_turmeric, turmeric, sacha_inchi, coffee_beans, circle_crop,
                 cart_icon, FONT_BLACK, FONT_XB)

cut, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS, SR = 1080, 1920, 30, 44100
segs = json.load(open(cut + ".json"))
s = [x["out"] for x in segs]
VID_END = s[-1][1]
HOLD = 2.6
TOTAL = VID_END + HOLD
NF = int(TOTAL * FPS)

BROWN = (16, 62, 32)      # dark green  (text / boxes)
CREAM = (244, 252, 236)   # mint white
ORANGE = (46, 160, 67)    # brand green (pills, highlights)
YEL = (255, 210, 0)
WHITE = (255, 255, 255)

def grab(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return Image.frombuffer("RGB", (W, H), raw)
FRONT = grab(1.0)
COFFEE = FRONT.crop((565, 905, 985, 1255))      # latte-art cup printed on the box

# ------------------------------------------------------------------ section plan
B = [0.0, 2.3, 4.9, 7.5, 10.1, VID_END]
SECTIONS = [(B[i], B[i + 1], None) for i in range(5)] + [(VID_END, TOTAL, None)]
CUTS = [b[0] for b in SECTIONS[1:]]
# per-section camera: (zoom start, zoom end, vertical focus 0..1)
CAM = {0: (1.00, 1.04, 0.40), 1: (1.06, 1.02, 0.40), 2: (1.00, 1.05, 0.40), 3: (1.06, 1.02, 0.40),
       4: (1.00, 1.04, 0.40), 5: (1.04, 1.04, 0.40)}

# ------------------------------------------------------------------ graphics
def marker_line(words, size, fg=BROWN, bg=CREAM, hi=None, rot=0.0):
    """Return per-word images for one boxed line + the box image + word x offsets."""
    f = font(FONT_BLACK, size)
    sp = f.getlength(" ")
    asc, desc = f.getmetrics()
    padx, pady = int(size * 0.35), int(size * 0.18)
    ws = [f.getlength(w) for w in words]
    Wt = int(sum(ws) + sp * (len(words) - 1) + padx * 2)
    Ht = int(asc + desc * 0.4 + pady * 2)
    box = Image.new("RGBA", (Wt, Ht), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, Wt - 1, Ht - 1], radius=int(size * 0.18), fill=bg)
    imgs, xs = [], []
    x = padx
    for w, wl in zip(words, ws):
        col = ORANGE if (hi and w.strip("?!.,").upper() in hi) else fg
        im = Image.new("RGBA", (int(wl) + 4, Ht), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, pady), w, font=f, fill=col)
        imgs.append(im); xs.append(x); x += wl + sp
    return box, imgs, xs


E = []  # elements: dict(img, t0, t1, x, y (top-left), anim, extra)
SFX = []  # (time, kind)

def add(img, t0, t1, x, y, anim="fade", **kw):
    E.append(dict(img=img, t0=t0, t1=t1, x=x, y=y, anim=anim, **kw))

def kinetic(lines, t0, t1, y, size=96, per=0.13, align="left", x=70, styles=None, hi=None, gap=14):
    """lines: list of str. styles: list of (fg,bg) per line. Words rise in one by one."""
    t = t0
    for i, ln in enumerate(lines):
        fg, bg = (styles[i] if styles else (BROWN, CREAM))
        sz = size
        box, imgs, xs = marker_line(ln.split(" "), sz, fg, bg, hi)
        while box.width > W - 140 and sz > 30:
            sz -= 4; box, imgs, xs = marker_line(ln.split(" "), sz, fg, bg, hi)
        bx = x if align == "left" else (W - box.width) // 2
        add(shadow(box, 10, (0, 6), 110), t, t1, bx - 30, y - 30, "wipe", dur=0.18)
        for im, xo in zip(imgs, xs):
            add(im, t, t1, bx + xo, y, "rise")
            SFX.append((t, "tick"))
            t += per
        y += box.height + gap
    return y


def chapter_tag(text):
    f = font(FONT_XB, 34)
    tw = int(f.getlength(text))
    im = Image.new("RGBA", (tw + 70, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, 63], radius=32, fill=(0, 0, 0, 150))
    d.ellipse([20, 24, 36, 40], fill=ORANGE)
    d.text((48, 12), text, font=f, fill=WHITE)
    return im


def rounded(img, r, border=0, bcol=ORANGE):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=255)
    o = img.convert("RGBA"); o.putalpha(m)
    if border:
        b = Image.new("RGBA", (img.width + border * 2, img.height + border * 2), (0, 0, 0, 0))
        ImageDraw.Draw(b).rounded_rectangle([0, 0, b.width - 1, b.height - 1], radius=r + border, fill=bcol)
        b.alpha_composite(o, (border, border)); o = b
    return o


def spec_card(art, big, small, sub=None, photo=False):
    """Horizontal spec card: image tile left, big number + label right."""
    CW, CH = 900, 230
    card = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, CW - 1, CH - 1], radius=36, fill=CREAM + (245,))
    tile = Image.new("RGBA", (190, 190), (255, 250, 240, 255))
    a = art.resize((190, 190), Image.LANCZOS) if photo else art.resize((170, 170), Image.LANCZOS)
    tile.alpha_composite(a, ((190 - a.width) // 2, (190 - a.height) // 2))
    card.alpha_composite(rounded(tile, 28), (20, 20))
    d = ImageDraw.Draw(card)
    d.text((240, 26), big, font=font(FONT_BLACK, 92), fill=ORANGE)
    d.text((242, 132), small, font=font(FONT_BLACK, 44), fill=BROWN)
    if sub:
        d.text((242, 182), sub, font=font(FONT_XB, 28), fill=(120, 90, 70))
    return shadow(card, 14, (0, 10), 140)


def label_inset():
    """Magnified crop of the real ingredient label, with marker highlights."""
    ox, oy = 235, 835
    crop = BACK.crop((ox, oy, ox + 605, oy + 215))
    sc = 940 / crop.width
    big = crop.resize((940, int(crop.height * sc)), Image.LANCZOS)
    # (x0, x1, top_y_at_x0, height) in BACK coords; the printed text is tilted (slope SL)
    hl = [(355, 628, 917, 24),   # serbuk jus durian belanda (2%)
          (250, 445, 939, 24),   # durian belanda (1.5%)
          (445, 655, 934, 24),   # ekstrak kunyit (0.5%)
          (650, 794, 951, 24),   # ekstrak kunyit ...
          (250, 378, 992, 24)]   # ... hitam (0.5%)
    return big, sc, [((a - ox) * sc, (c - ox) * sc, (y - oy) * sc, h * sc) for a, c, y, h in hl]

SL = -0.028



# ------------------------------------------------------------------ timeline
# LAYOUT RULE: the real coffee in the mug (y ~380-1040) is never covered.
# Text lives in the TOP band (y 165-360) and the BOTTOM band (y >= 1080).
TOP, BOT = 168, 1085

def no_sugar_icon(S=400):
    """White sugar cubes with a red 'no' sign."""
    im = Image.new("RGBA", (S * 2, S * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); Z = S * 2
    for (cx, cy, r) in [(0.38, 0.58, 0.17), (0.62, 0.58, 0.17), (0.5, 0.36, 0.17)]:
        x0, y0, w = Z * (cx - r), Z * (cy - r), Z * r * 2
        d.polygon([(x0, y0 + w * 0.25), (x0 + w * 0.5, y0), (x0 + w, y0 + w * 0.25), (x0 + w * 0.5, y0 + w * 0.5)],
                  fill=(255, 255, 255), outline=(190, 190, 190), width=4)
        d.polygon([(x0, y0 + w * 0.25), (x0 + w * 0.5, y0 + w * 0.5), (x0 + w * 0.5, y0 + w), (x0, y0 + w * 0.75)],
                  fill=(225, 225, 225), outline=(190, 190, 190), width=4)
        d.polygon([(x0 + w, y0 + w * 0.25), (x0 + w * 0.5, y0 + w * 0.5), (x0 + w * 0.5, y0 + w), (x0 + w, y0 + w * 0.75)],
                  fill=(205, 205, 205), outline=(190, 190, 190), width=4)
    m = Z * 0.06
    d.ellipse([m, m, Z - m, Z - m], outline=(225, 40, 50), width=int(Z * 0.07))
    d.line([(Z * 0.2, Z * 0.2), (Z * 0.8, Z * 0.8)], fill=(225, 40, 50), width=int(Z * 0.07))
    return im.resize((S, S), Image.LANCZOS)

def number_badge(n):
    return stroke_text([f"#{n}"], 230, fill=YEL, stroke=BROWN, sw=16)

def sub_chip(text, size=56):
    box, imgs, xs = marker_line(text.split(" "), size, WHITE, BROWN, None)
    while box.width > W - 120:
        size -= 4; box, imgs, xs = marker_line(text.split(" "), size, WHITE, BROWN, None)
    for im, xo in zip(imgs, xs):
        box.alpha_composite(im, (int(xo), 0))
    return shadow(box, 10, (0, 6), 120)

def reason(i, t0, t1, title, accent, sub, cards):
    kinetic([title[0]], t0 + 0.05, t1, TOP, size=78, per=0.0, styles=[(BROWN, CREAM)], align="center")
    kinetic([accent], t0 + 0.2, t1, TOP + 108, size=84, per=0.0, styles=[(WHITE, ORANGE)], align="center")
    nb = number_badge(i)
    E.append(dict(img=nb, t0=t0, t1=t1, x=40, y=BOT, anim="pop")); SFX.append((t0, "boom"))
    x = 300
    for j, (art, lab, photo) in enumerate(cards):
        c = ingredient_card(art, lab, S=255 if len(cards) > 1 else 320, photo=photo)
        E.append(dict(img=c, t0=t0 + 0.25 + j * 0.25, t1=t1, x=x, y=BOT - 10, anim="pop"))
        SFX.append((t0 + 0.25 + j * 0.25, "ding"))
        x += c.width - 10
    ch = sub_chip(sub)
    E.append(dict(img=ch, t0=t0 + 0.6, t1=t1, x=(W - ch.width) // 2, y=BOT + 370, anim="slide"))
    SFX.append((t0 + 0.6, "tick"))

# 0) HOOK — listicle promise, fully visible on frame 0
add(None, 0, 0.8, 0, 0, "darken")
kinetic(["3 SEBAB AKU TUKAR"], 0.0, B[1], TOP, size=92, per=0.0, styles=[(BROWN, CREAM)], align="center")
kinetic(["KE KOPI NI!"], 0.0, B[1], TOP + 120, size=104, per=0.0, styles=[(WHITE, ORANGE)], align="center")
SFX.append((0.0, "boom"))
_tw = int(font(FONT_BLACK, 48).getlength("DURIMEX COFFEE"))
tag = Image.new("RGBA", (_tw + 64, 92), (0, 0, 0, 0))
ImageDraw.Draw(tag).rounded_rectangle([0, 0, tag.width - 1, 91], radius=46, fill=YEL)
ImageDraw.Draw(tag).text((32, 16), "DURIMEX COFFEE", font=font(FONT_BLACK, 48), fill=BROWN)
E.append(dict(img=shadow(tag, 10, (0, 6), 120), t0=0.0, t1=B[1], x=420, y=1240, anim="static"))
arr_ = Image.new("RGBA", (170, 210), (0, 0, 0, 0))
ImageDraw.Draw(arr_).polygon([(55, 0), (115, 0), (115, 115), (165, 115), (85, 205), (5, 115), (55, 115)],
                             fill=YEL, outline=BROWN, width=7)
arr_ = arr_.rotate(-35, expand=True, resample=Image.BICUBIC)
E.append(dict(img=arr_, t0=0.3, t1=B[1], x=190, y=1290, anim="bounce"))
kinetic(["Tonton sampai habis"], 0.9, B[1], 1600, size=44, per=0.06, styles=[(WHITE, BROWN)], align="center")

# 1..3) REASONS
reason(1, B[1], B[2], ["SEBAB PERTAMA:"], "TANPA GULA PUTIH",
       "Guna gula nano, 5.2g gula sesachet", [(no_sugar_icon(400), "GULA NANO", False)])
reason(2, B[2], B[3], ["SEBAB KEDUA:"], "ADA KUNYIT HITAM",
       "Herba tradisional pilihan orang kita", [(black_turmeric(400), "KUNYIT HITAM", False),
                                               (turmeric(400), "KUNYIT", False)])
reason(3, B[3], B[4], ["SEBAB KETIGA:"], "CREAMY MACAM KAFE",
       "Lemak hazelnut & vanila + durian belanda", [(COFFEE.resize((300, 300)), "RASA KAFE", True),
                                                    (circle_crop(FRONT, 410, 1215, 135, 300), "DURIAN BELANDA", True)])

# 4) BONUS — trust
kinetic(["BONUS:"], B[4] + 0.05, B[5], TOP, size=78, per=0.0, styles=[(BROWN, CREAM)], align="center")
kinetic(["HALAL & LULUS MeSTI"], B[4] + 0.15, B[5], TOP + 108, size=84, per=0.0, styles=[(WHITE, ORANGE)],
        align="center")
for j, b_ in enumerate(["Halal JAKIM", "MeSTI", "Bancuh 1 minit"]):
    ch = sub_chip(b_, 64)
    E.append(dict(img=ch, t0=B[4] + 0.3 + j * 0.3, t1=B[5], x=(W - ch.width) // 2, y=BOT + 30 + j * 135,
                  anim="slide"))
    SFX.append((B[4] + 0.3 + j * 0.3, "tick"))

# 5) CTA end card (last frame held, lightly dimmed — coffee stays visible)
E.append(dict(img=None, t0=VID_END, t1=TOTAL + 1, x=0, y=0, anim="dim"))
kinetic(["NAK CUBA?"], VID_END, TOTAL + 1, TOP, size=78, per=0.0, styles=[(BROWN, CREAM)], align="center")
cta = Image.new("RGBA", (940, 150), (0, 0, 0, 0))
ImageDraw.Draw(cta).rounded_rectangle([0, 0, 939, 149], radius=75, fill=YEL)
cta.alpha_composite(cart_icon(100, BROWN), (50, 25))
_fs = 74
while font(FONT_BLACK, _fs).getlength("TEKAN BAKUL KUNING") > 940 - 175 - 50: _fs -= 2
_f = font(FONT_BLACK, _fs); _bb = _f.getbbox("TEKAN BAKUL KUNING")
ImageDraw.Draw(cta).text((175, (150 - (_bb[3] - _bb[1])) // 2 - _bb[1]), "TEKAN BAKUL KUNING", font=_f, fill=BROWN)
E.append(dict(img=shadow(cta, 14, (0, 10), 140), t0=VID_END + 0.1, t1=TOTAL + 1, x=-2, y=TOP + 90, anim="pulse"))
SFX.append((VID_END, "boom"))
y = BOT
for j, b_ in enumerate(["Tanpa gula putih", "Ada kunyit hitam", "Creamy macam kafe"]):
    ch = sub_chip(b_, 60)
    E.append(dict(img=ch, t0=VID_END + 0.4 + j * 0.2, t1=TOTAL + 1, x=(W - ch.width) // 2, y=y, anim="slide"))
    y += 122
kinetic(["Cuba sendiri hari ni!"], VID_END + 1.1, TOTAL + 1, y + 20, size=70, per=0.06,
        styles=[(WHITE, ORANGE)], align="center")
arrow = Image.new("RGBA", (160, 200), (0, 0, 0, 0))
ImageDraw.Draw(arrow).polygon([(50, 0), (110, 0), (110, 110), (155, 110), (80, 195), (5, 110), (50, 110)],
                              fill=YEL, outline=BROWN, width=6)
E.append(dict(img=arrow, t0=VID_END + 1.2, t1=TOTAL + 1, x=60, y=y + 140, anim="bounce"))
for c in CUTS:
    SFX.append((c, "whoosh"))

# ------------------------------------------------------------------ animation
def ease_out(x): return 1 - (1 - x) ** 3
def ease_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def set_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a))); return im

_spec_cache = {}
def comp(canvas, im, x, y):
    cx0, cy0 = max(0, -x), max(0, -y)
    cx1, cy1 = min(im.width, W - x), min(im.height, H - y)
    if cx1 <= cx0 or cy1 <= cy0: return
    if (cx0, cy0, cx1, cy1) != (0, 0, im.width, im.height):
        im = im.crop((cx0, cy0, cx1, cy1))
    canvas.alpha_composite(im, (x + cx0, y + cy0))
def draw(canvas, e, t):
    if t < e["t0"] or t >= e["t1"]:
        return
    age, left = t - e["t0"], e["t1"] - t
    if e["t0"] == 0 and e["anim"] in ("wipe", "rise"):
        age = 1.0  # hook is fully visible on frame 0 (thumbnail)
    out_a = min(1, left / 0.15)
    an = e["anim"]
    if an == "dim":
        a = 0.25 * ease_out(min(1, age / 0.4))
        canvas.alpha_composite(Image.new("RGBA", (W, H), (20, 10, 5, int(255 * a))))
        return
    if an == "darken":
        a = 0.55 * (1 - ease_out(min(1, age / 1.0)))
        canvas.alpha_composite(Image.new("RGBA", (W, H), (20, 10, 5, int(255 * a))))
        return
    im = e["img"]; x, y = e["x"], e["y"]
    if an == "wipe":
        k = ease_out(min(1, age / e.get("dur", 0.2)))
        if k <= 0: return
        im = im.crop((0, 0, max(1, int(im.width * k)), im.height))
    elif an == "rise":
        k = min(1, age / 0.18); y += (1 - ease_out(k)) * 40; im = set_alpha(im, k)
    elif an in ("pop", "pulse"):
        k = min(1, age / 0.28); sc = 0.5 + 0.5 * ease_back(k)
        if an == "pulse" and k >= 1: sc = 1 + 0.035 * math.sin((age - 0.28) * 2 * math.pi * 1.5)
        cx, cy = x + im.width / 2, y + im.height / 2
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        x, y = cx - im.width / 2, cy - im.height / 2
        im = set_alpha(im, min(1, age / 0.1))
    elif an == "slide":
        k = min(1, age / 0.3); x -= (1 - ease_back(k)) * 900
    elif an == "bounce":
        y -= abs(math.sin(age * math.pi * 2.0)) * 60; im = set_alpha(im, min(1, age / 0.15))
    elif an == "spec":
        art, num, unit, lab, sub, ph = e["card"]
        k = min(1, age / 0.6)
        txt = unit if num is None else (f"{num * ease_out(k):.1f}" if isinstance(num, float) else f"{int(round(num * ease_out(k)))}") + unit
        key = (id(e), txt)
        if key not in _spec_cache:
            _spec_cache[key] = spec_card(art, txt, lab, sub, ph)
        im = _spec_cache[key]
        k2 = min(1, age / 0.35); x += (1 - ease_back(k2)) * 1000
        if left < 0.2: x -= (1 - left / 0.2) * 1100
    elif an == "inset":
        k = min(1, age / 0.4); sc = 0.3 + 0.7 * ease_back(k)
        base = im.convert("RGBA")
        ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for i, (a0, a1, y0_, hh) in enumerate(e["hls"]):
            hk = min(1, max(0, (age - 0.6 - i * 0.35) / 0.3))
            if hk > 0:
                xe = a0 + (a1 - a0) * hk; ye = y0_ + SL * (xe - a0)
                d.polygon([(a0, y0_), (xe, ye), (xe, ye + hh), (a0, y0_ + hh)], fill=ORANGE + (105,))
        base = Image.alpha_composite(base, ov)
        im = shadow(rounded(base, 30, 8), 16, (0, 10), 150)
        cx, cy = x + im.width / 2, y + im.height / 2
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        x, y = cx - im.width / 2, cy - im.height / 2
    if out_a < 1 and an not in ("spec",):
        im = set_alpha(im, out_a)
    comp(canvas, im, int(x), int(y))


chapter_tag_cache = {}
# vignette + grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = 1 - 0.28 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.48) / (H * 0.62)) ** 2, 0, 1) ** 1.4
vig = vig[..., None]
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 6, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1) for _ in range(6)]

def seg_at(t):
    for i, x in enumerate(segs):
        if t < x["out"][1]:
            return i, t - x["out"][0], x["out"][1] - x["out"][0]
    return len(segs) - 1, t - segs[-1]["out"][0], segs[-1]["out"][1] - segs[-1]["out"][0]

# ------------------------------------------------------------------ render video
grade = ("eq=contrast=1.06:saturation=1.12:gamma=1.10:brightness=0.02,"
         "colorbalance=rs=0.05:gs=0.0:bs=-0.06:rm=0.04:bm=-0.04:rh=0.02:bh=-0.03,"
         f"unsharp=5:5:0.3,tpad=stop_mode=clone:stop_duration={HOLD}")
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", cut, "-vf", grade, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-maxrate", "9M", "-bufsize", "18M", "-tune", "grain", out + ".video.mp4"], stdin=subprocess.PIPE)
for n in range(NF):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = n / FPS
    # slow continuous push-in per section + shake on section change
    sec = max(i for i, b in enumerate(SECTIONS) if t >= b[0])
    sa, sb_ = SECTIONS[sec][0], SECTIONS[sec][1]
    z0_, z1_, fy = CAM[sec]
    z = z0_ + (z1_ - z0_) * ease_out(min(1, (t - sa) / max(0.1, sb_ - sa)))
    since = min([t - c for c in CUTS if t >= c] + [9])
    sx = sy = 0
    if since < 0.12:
        sx = 30 * (1 - since / 0.12) * (1 if n % 2 else -1)
    cw, ch = W / z, H / z
    x0 = min(max(0, (W - cw) / 2 + sx), W - cw); y0 = min(max(0, (H - ch) * fy + sy), H - ch)
    img = Image.frombuffer("RGB", (W, H), buf).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    arr = np.asarray(img, np.float32) * vig + GRAIN[n % 6]
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
    for e in E:
        draw(img, e, t)
    # chapter tag + segmented story bar
    if SECTIONS[sec][2]:
        img.alpha_composite(chapter_tag_cache.setdefault(sec, chapter_tag(SECTIONS[sec][2])), (60, 160))
    d = ImageDraw.Draw(img)
    gw = (W - 120 - 5 * 10) / 6
    for i, (a, b, _) in enumerate(SECTIONS):
        x = 60 + i * (gw + 10)
        d.rounded_rectangle([x, 128, x + gw, 136], radius=4, fill=(255, 255, 255, 90))
        k = 0 if t < a else min(1, (t - a) / (b - a))
        if k > 0:
            d.rounded_rectangle([x, 128, x + gw * k, 136], radius=4, fill=ORANGE)
    out_rgb = img.convert("RGB")
    if since < 0.13:  # RGB-split glitch on section change
        k = int(18 * (1 - since / 0.13)) + 2
        a_ = np.asarray(out_rgb).copy()
        a_[:, :, 0] = np.roll(a_[:, :, 0], k, 1); a_[:, :, 2] = np.roll(a_[:, :, 2], -k, 1)
        out_rgb = Image.fromarray(a_)
    enc.stdin.write(out_rgb.tobytes())
enc.stdin.close(); enc.wait(); dec.kill()


# ------------------------------------------------------------------ audio
v = subprocess.run(["ffmpeg", "-v", "error", "-i", cut, "-af", "highpass=f=80,acompressor=threshold=-20dB:ratio=3",
                    "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
voice = np.frombuffer(v, np.int16).astype(np.float32) / 32768
N = int(TOTAL * SR)
vo = np.zeros(N, np.float32); vo[:min(N, len(voice))] = voice[:N]
vo /= max(1e-6, np.percentile(np.abs(vo), 99.5)) / 0.7

# lo-fi bed, 88 BPM, Am7 - Fmaj7 - Cmaj7 - G6
bpm = 104; beat = 60 / bpm
music = np.zeros(N, np.float32)
tt = np.arange(N) / SR
def note(f, t0, d, amp, kind="keys"):
    k0, k1 = int(t0 * SR), min(N, int((t0 + d) * SR))
    if k0 >= N: return
    x = np.arange(k1 - k0) / SR
    if kind == "keys":
        sig = (np.sin(2*np.pi*f*x) + 0.35*np.sin(2*np.pi*2*f*x) + 0.12*np.sin(2*np.pi*3*f*x)) \
              * np.exp(-x * 1.6) * (1 - np.exp(-x * 60))
        sig *= 1 + 0.15 * np.sin(2 * np.pi * 5 * x)
    else:  # bass
        sig = np.sin(2*np.pi*f*x) * np.exp(-x * 2.2) * (1 - np.exp(-x * 80))
    music[k0:k1] += sig * amp
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]  # C G Am F
bars = int(TOTAL / (beat * 4)) + 2
for b in range(bars):
    c = chords[b % 4]; t0 = b * 4 * beat
    for j, m in enumerate(c):
        note(mid(m), t0 + j * 0.01, beat * 1.6, 0.04)
    for k8 in range(8):  # plucky 8th-note arpeggio
        note(mid(c[[0, 1, 2, 3, 2, 1, 2, 3][k8]] + 12), t0 + k8 * beat / 2, beat * 0.45, 0.03)
    note(mid(c[0] - 12), t0, beat * 2, 0.22, "bass"); note(mid(c[0] - 12), t0 + 2.5 * beat, beat * 1.4, 0.16, "bass")
rngm = np.random.default_rng(3)
for i in range(int(TOTAL / beat) + 2):
    t0 = i * beat
    if i % 2 == 0:  # kick
        k0 = int(t0 * SR); x = np.arange(int(0.25 * SR)) / SR
        sig = np.sin(2 * np.pi * (50 + 90 * np.exp(-x * 30)) * x) * np.exp(-x * 14) * 0.5
        m = min(len(sig), N - k0); music[k0:k0 + m] += sig[:m] if m > 0 else 0
    else:  # clap
        k0 = int(t0 * SR); nz = rngm.normal(0, 1, int(0.15 * SR)); x = np.arange(len(nz)) / SR
        env_ = np.exp(-x * 30) + 0.6 * np.exp(-np.maximum(0, x - 0.012) * 40) * (x > 0.012)
        sig = (nz - np.convolve(nz, np.ones(6) / 6, "same")) * env_ * 0.16
        m = min(len(sig), N - k0); music[k0:k0 + m] += sig[:m] if m > 0 else 0
    for hh in (0, 0.5):  # hats
        k0 = int((t0 + hh * beat + (0.03 if hh else 0)) * SR); nz = rngm.normal(0, 1, int(0.04 * SR))
        nz = nz - np.convolve(nz, np.ones(3) / 3, "same"); x = np.arange(len(nz)) / SR
        sig = nz * np.exp(-x * 90) * (0.05 if hh else 0.035)
        m = min(len(sig), N - k0); music[k0:k0 + m] += sig[:m] if m > 0 else 0
music = np.convolve(music, np.ones(3) / 3, "same")  # warm it a bit
# sidechain duck under voice
env = np.sqrt(np.convolve(vo ** 2, np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"))
duck = 1 - 0.55 * np.clip(env / 0.08, 0, 1)
music *= duck * 0.55
fade = np.clip((TOTAL - tt) / 0.8, 0, 1); music *= fade

sfx = np.zeros(N, np.float32)
def place(sig, t):
    k = int(t * SR); m = min(len(sig), N - k)
    if m > 0 and k >= 0: sfx[k:k + m] += sig[:m]
def mk(kind):
    if kind == "boom":
        x = np.arange(int(0.9 * SR)) / SR
        return (np.sin(2 * np.pi * (40 + 60 * np.exp(-x * 8)) * x) * np.exp(-x * 4) * 0.9
                + np.random.default_rng(1).normal(0, 1, len(x)) * np.exp(-x * 30) * 0.15)
    if kind == "tick":
        x = np.arange(int(0.03 * SR)) / SR
        return np.sin(2 * np.pi * 2200 * x) * np.exp(-x * 180) * 0.12
    if kind == "ding":
        x = np.arange(int(0.6 * SR)) / SR
        return (np.sin(2 * np.pi * 1318 * x) + 0.5 * np.sin(2 * np.pi * 1976 * x)) * np.exp(-x * 7) * 0.12
    if kind == "riser":
        x = np.arange(int(0.8 * SR)) / SR; f = 300 + 1500 * (x / 0.8) ** 2
        nz = np.random.default_rng(2).normal(0, 1, len(x))
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.05 + nz * 0.03) * (x / 0.8) ** 2
    if kind == "whoosh":
        nz = np.random.default_rng(4).normal(0, 1, int(0.35 * SR))
        nz = np.convolve(nz, np.ones(16) / 16, "same"); env_ = np.sin(np.linspace(0, np.pi, len(nz))) ** 3
        return nz * env_ * 0.35
SFX_TAB = {k: mk(k) for k in ("boom", "tick", "ding", "riser", "whoosh")}
for t, kind in SFX:
    place(SFX_TAB[kind], t - (0.15 if kind == "whoosh" else 0))
mix = vo * 0.9 + music + sfx
st = np.stack([mix, mix], 1)
st[:, 0] += music * 0.08; st[:, 1] -= music * 0.08  # tiny stereo width on the bed
with wave.open(out + ".audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st / max(1, np.abs(st).max()), -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".video.mp4", "-i", out + ".audio.wav",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-ar", "44100", "-shortest", "-movflags", "+faststart", out], check=True)
print("done", out, TOTAL)
