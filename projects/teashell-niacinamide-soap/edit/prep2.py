"""Assets for edit v2: FAB pills, circle bubbles, hook frames, CTA end-card layers, riser SFX."""
import sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

U = "/root/.claude/uploads/878573dd-f1f2-5804-95d9-dddb669af68e/"
OUT = sys.argv[1]
SR = 44100
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
COL = {"CIRI": (77, 208, 225), "KELEBIHAN": (255, 225, 77), "MANFAAT": (255, 77, 141)}


def content(name):
    return Image.open(U + name).convert("RGB").crop((0, 428, 1600, 2028))


def realbox():
    return Image.open(U + "40a0ec0f-image.jpg").convert("RGB").crop((1240, 600, 3150, 2560))


# ---------- FAB pills ----------
def pill(kind, text, out, maxw=1040):
    f_lab = ImageFont.truetype(BLACK, 30)
    f_txt = ImageFont.truetype(XB, 44)
    lw = f_lab.getbbox(kind)[2] + 36
    tw = f_txt.getbbox(text)[2]
    h = 92
    w = min(maxw, lw + tw + 70)
    img = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((15, 21, 15 + w, 21 + h), h // 2, fill=(0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((15, 15, 15 + w, 15 + h), h // 2, fill=(20, 18, 18, 235))
    c = COL[kind]
    d.rounded_rectangle((27, 31, 27 + lw, 15 + h - 16), 30, fill=c)
    d.text((27 + 18, 15 + h // 2), kind, font=f_lab, fill=(20, 18, 18), anchor="lm")
    d.text((27 + lw + 22, 15 + h // 2 + 2), text, font=f_txt, fill="white", anchor="lm")
    img.save(out)


# ---------- circle bubbles ----------
def bubble(im, box, out, size=330, ring=(255, 255, 255)):
    im = im.crop(box).resize((size, size), Image.LANCZOS)
    full = size + 16
    canvas = Image.new("RGBA", (full + 40, full + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((20, 28, 20 + full, 28 + full), fill=(0, 0, 0, 150))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(canvas).ellipse((20, 20, 20 + full, 20 + full), fill=ring + (255,))
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    canvas.paste(im, (28, 28), m)
    canvas.save(out)


def fill916(im, out, box=None, blur=0, dark=1.0):
    if box:
        im = im.crop(box)
    w, h = im.size
    tw = int(h * 9 / 16)
    if tw <= w:
        im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
    else:
        th = int(w * 16 / 9)
        im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th))
    im = im.resize((1080, 1920), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1.0:
        im = Image.eval(im, lambda v: int(v * dark))
    im.save(out, quality=95)


def textlayer(lines, out, H=1920):
    """lines: list of (text, font, size, color, y) -> transparent 1080xH PNG."""
    img = Image.new("RGBA", (1080, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, font, size, color, y in lines:
        f = ImageFont.truetype(font, size)
        d.text((540, y), text, font=f, fill=color, anchor="mm", stroke_width=max(3, size // 14), stroke_fill="black")
    img.save(out)


# pills (Ciri / Kelebihan / Manfaat)
pill("CIRI", "Wangi Citrus · Jasmine · Cedarwood", f"{OUT}/p1.png")
pill("CIRI", "5% Niacinamide + Alpha-Arbutin", f"{OUT}/p2.png")
pill("KELEBIHAN", "Berdaftar NPRA · lebih yakin", f"{OUT}/p3.png")
pill("MANFAAT", "Kulit nampak cerah & sekata", f"{OUT}/p4.png")
pill("KELEBIHAN", "4 lapis pelembap dalam 1 sabun", f"{OUT}/p5.png")
pill("MANFAAT", "Tak ketat, tak kering lepas cuci", f"{OUT}/p6.png")
pill("KELEBIHAN", "FREE jaring busa · busa 3 saat", f"{OUT}/p7.png")
pill("MANFAAT", "Kurang geseran, kulit lebih selesa", f"{OUT}/p8.png")

# circle bubbles from different crops than v1
bubble(content("67064db4-image.jpg"), (700, 500, 1600, 1400), f"{OUT}/b1.png")        # wood/scent texture
bubble(content("a0f6c496-image.jpg"), (200, 650, 1100, 1550), f"{OUT}/b2.png")         # soap on plate close-up
bubble(content("a0f6c496-image.jpg"), (0, 1340, 760, 1600), f"{OUT}/b3_tmp.png")       # placeholder (unused)
bubble(content("04dd1f5b-image.jpg"), (300, 150, 1300, 1150), f"{OUT}/b4.png")         # cream texture
bubble(content("93b8d2a1-image.jpg"), (500, 600, 1450, 1550), f"{OUT}/b5.png")         # soap in foam
bubble(content("6a18ff34-image.jpg"), (900, 450, 1600, 1150), f"{OUT}/b6.png")         # lathered hands

# NPRA badge: the registration lines from the soap image as a small card
reg = content("a0f6c496-image.jpg").crop((40, 1320, 760, 1560))
reg = reg.resize((540, 180), Image.LANCZOS)
c = Image.new("RGBA", (560, 200), (0, 0, 0, 0))
m = Image.new("L", reg.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 539, 179), 22, fill=255)
ImageDraw.Draw(c).rounded_rectangle((0, 0, 559, 199), 30, fill=(255, 255, 255, 255))
c.paste(reg, (10, 10), m); c.save(f"{OUT}/b3.png")

# hook frames (3 quick cuts)
fill916(content("93b8d2a1-image.jpg"), f"{OUT}/h1.jpg", box=(400, 520, 1400, 1430))
fill916(content("a0f6c496-image.jpg"), f"{OUT}/h2.jpg", box=(250, 560, 1150, 1300))
fill916(realbox(), f"{OUT}/h3.jpg")

# CTA end card
fill916(content("93b8d2a1-image.jpg"), f"{OUT}/end_bg.jpg", blur=22, dark=0.45)
rb = realbox().resize((620, 638), Image.LANCZOS)
card = Image.new("RGBA", (680, 700), (0, 0, 0, 0))
sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((20, 34, 660, 692), 36, fill=(0, 0, 0, 170))
card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
ImageDraw.Draw(card).rounded_rectangle((20, 20, 660, 678), 36, fill=(255, 255, 255, 255))
m = Image.new("L", rb.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 619, 637), 28, fill=255)
card.paste(rb, (30, 30), m); card.save(f"{OUT}/end_box.png")

Y, P, W, PK = (255, 225, 77), (255, 77, 141), (255, 255, 255), (77, 208, 225)
textlayer([("KENAPA KENA KLIK SEKARANG?", BLACK, 56, Y, 150)], f"{OUT}/e0.png")
textlayer([("✔ Dapat FREE jaring busa", DJ, 60, PK, 1010)], f"{OUT}/e1.png")
textlayer([("✔ Stok terhad, saya pun beli 6!", DJ, 52, PK, 1095)], f"{OUT}/e2.png")
textlayer([("Kalau tunggu esok...", XB, 66, P, 1205),
           ("muka masih rasa ketat & kusam", XB, 56, W, 1285),
           ("setiap kali lepas cuci", XB, 56, W, 1352)], f"{OUT}/e3.png")
# CTA button
btn = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
d = ImageDraw.Draw(btn)
d.rounded_rectangle((90, 1450, 990, 1600), 70, fill=(255, 77, 141, 255), outline="white", width=6)
d.text((540, 1525), "TEKAN BEG KUNING SEKARANG", font=ImageFont.truetype(BLACK, 54), fill="white", anchor="mm")
d.text((540, 1690), "↓", font=ImageFont.truetype(DJ, 110), fill=Y, anchor="mm", stroke_width=5, stroke_fill="black")
btn.save(f"{OUT}/e4.png")

# riser SFX for the end card
rng = np.random.default_rng(3)
n = int(1.3 * SR); t = np.linspace(0, 1, n)
fc = 300 * (6000 / 300) ** t
x = rng.standard_normal(n); low = band = 0.0; y = np.empty(n)
for i in range(n):
    f = 2 * np.sin(np.pi * fc[i] / SR); hi = x[i] - low - 0.8 * band; band += f * hi; low += f * band; y[i] = band
y *= t ** 2 * (1 - np.clip((t - 0.92) / 0.08, 0, 1))
y /= np.abs(y).max()
with wave.open(f"{OUT}/riser.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([y, y], 1) * 0.8 * 32767).astype(np.int16).tobytes())
print("ok")
