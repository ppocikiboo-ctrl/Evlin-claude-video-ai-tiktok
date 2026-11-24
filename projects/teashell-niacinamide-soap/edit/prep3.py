"""Assets for edit v3: VS split hook, 'SEBAB #n' stickers, tilted polaroids, recap end card, ding/buzz SFX."""
import sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

U = "/root/.claude/uploads/878573dd-f1f2-5804-95d9-dddb669af68e/"
OUT = sys.argv[1]
SR = 44100
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YEL, PINK, GRN, RED, INK = (255, 225, 77), (255, 77, 141), (60, 200, 110), (235, 60, 60), (22, 20, 20)


def content(name):
    return Image.open(U + name).convert("RGB").crop((0, 428, 1600, 2028))


def realbox():
    return Image.open(U + "40a0ec0f-image.jpg").convert("RGB").crop((1240, 600, 3150, 2560))


def cover(im, w, h):
    return ImageOps.fit(im, (w, h), Image.LANCZOS)


def shadowed(img, blur=12, off=10, alpha=150):
    pad = blur * 2 + off
    c = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    a = img.split()[-1].point(lambda v: alpha if v > 0 else 0)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 255)); sh.putalpha(a)
    c.alpha_composite(sh, (pad, pad + off))
    c = c.filter(ImageFilter.GaussianBlur(blur))
    c.alpha_composite(img, (pad, pad))
    return c


def text_c(d, xy, s, font, fill, stroke=0, sfill="black"):
    d.text(xy, s, font=font, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)


# ---------- HOOK: split screen VS ----------
top = content("b153f49c-image.jpg").crop((980, 560, 1340, 860))       # "ordinary soap" block from brand chart
top = ImageOps.grayscale(cover(top, 1080, 960)).convert("RGB").filter(ImageFilter.GaussianBlur(2))
bot = cover(content("6a18ff34-image.jpg").crop((780, 420, 1600, 1250)), 1080, 960)
for img, name in ((top, "v_top.jpg"), (bot, "v_bot.jpg")):
    img.save(f"{OUT}/{name}", quality=95)


def label(lines, mark, mcol, out, h=960, y0=60):
    img = Image.new("RGBA", (1080, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.ellipse((60, y0, 220, y0 + 160), fill=mcol + (255,), outline="white", width=8)
    text_c(d, (140, y0 + 82), mark, ImageFont.truetype(DJ, 110), "white")
    y = y0 + 45
    for s, f, size, col in lines:
        d.text((250, y), s, font=ImageFont.truetype(f, size), fill=col, anchor="lm", stroke_width=6, stroke_fill="black")
        y += size + 20
    img.save(out)


label([("SABUN BIASA", BLACK, 78, (255, 255, 255)), ("Muka ketat & kering", XB, 54, (255, 150, 150))], "✗", RED, f"{OUT}/v_lt.png")
label([("TEASHELL", BLACK, 78, YEL), ("Busa lembut 3 saat", XB, 54, (170, 255, 190))], "✓", GRN, f"{OUT}/v_lb.png", y0=720)

band = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(band)
d.rounded_rectangle((60, 800, 1020, 1120), 40, fill=YEL + (255,), outline=INK, width=8)
text_c(d, (540, 885), "3 SEBAB saya terus", ImageFont.truetype(BLACK, 72), INK)
text_c(d, (540, 975), "beli 6 kotak", ImageFont.truetype(BLACK, 72), INK)
text_c(d, (540, 1060), "tengok sampai habis ↓", ImageFont.truetype(DJ, 44), (90, 40, 60))
band.rotate(-3, resample=Image.BICUBIC, center=(540, 960)).save(f"{OUT}/v_band.png")


# ---------- SEBAB stickers ----------
def sticker(n, text, out):
    f_n = ImageFont.truetype(BLACK, 40); f_big = ImageFont.truetype(BLACK, 76); f_t = ImageFont.truetype(XB, 46)
    tw = f_t.getbbox(text)[2]
    w, h = max(640, tw + 200), 150
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=YEL + (255,), outline=INK, width=6)
    d.ellipse((18, 15, 138, 135), fill=PINK + (255,), outline=INK, width=5)
    text_c(d, (78, 76), f"#{n}", f_big if n < 10 else f_n, "white", 4, INK)
    d.text((160, 42), "SEBAB", font=f_n, fill=(120, 60, 80), anchor="lm")
    d.text((160, 100), text, font=f_t, fill=INK, anchor="lm")
    img = img.rotate(2.5, resample=Image.BICUBIC, expand=True)
    shadowed(img).save(out)


sticker(1, "Niacinamide + Pro-Vitamin B5", f"{OUT}/s1.png")
sticker(2, "Tak ketat, tak kering lepas cuci", f"{OUT}/s2.png")
sticker(3, "FREE jaring busa, busa 3 saat", f"{OUT}/s3.png")


# ---------- polaroids ----------
def polaroid(im, caption, out, angle):
    ph = cover(im, 360, 360)
    card = Image.new("RGBA", (400, 470), (250, 248, 242, 255))
    card.paste(ph, (20, 20))
    d = ImageDraw.Draw(card)
    text_c(d, (200, 428), caption, ImageFont.truetype(XB, 34), (40, 36, 36))
    # tape strip
    tape = Image.new("RGBA", (150, 44), (255, 240, 170, 200))
    card.alpha_composite(tape, (125, 0))
    card = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    shadowed(card, blur=10, off=8).save(out)


polaroid(realbox(), "6 kotak terus!", f"{OUT}/o1.png", 5)
polaroid(content("a0f6c496-image.jpg").crop((250, 420, 1450, 1300)), "5% Niacinamide", f"{OUT}/o2.png", -4)
polaroid(content("04dd1f5b-image.jpg").crop((0, 0, 1600, 1150)), "Cerah & sekata", f"{OUT}/o3.png", 4)
polaroid(content("93b8d2a1-image.jpg").crop((300, 520, 1500, 1500)), "Busa halus & padat", f"{OUT}/o4.png", -5)


# ---------- recap end card layers ----------
def layer(draw_fn, out):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(img)); img.save(out)


layer(lambda d: text_c(d, (540, 300), "3 SEBAB WAJIB CUBA", ImageFont.truetype(BLACK, 80), YEL, 7), f"{OUT}/r0.png")
reasons = ["Niacinamide + Pro-Vitamin B5", "Tak ketat, tak kering", "FREE jaring busa 3 saat"]
for i, s in enumerate(reasons):
    def f(d, i=i, s=s):
        y = 480 + i * 170
        d.rounded_rectangle((90, y, 990, y + 130), 34, fill=(255, 255, 255, 235), outline=INK, width=5)
        d.ellipse((115, y + 15, 215, y + 115), fill=GRN + (255,))
        text_c(d, (165, y + 66), "✓", ImageFont.truetype(DJ, 64), "white")
        d.text((245, y + 66), s, font=ImageFont.truetype(XB, 44), fill=INK, anchor="lm")
    layer(f, f"{OUT}/r{i+1}.png")


def cta(d):
    text_c(d, (540, 1080), "Stok terhad, jangan terlepas!", ImageFont.truetype(XB, 56), "white", 6)
    d.rounded_rectangle((90, 1200, 990, 1350), 75, fill=PINK + (255,), outline="white", width=7)
    text_c(d, (540, 1275), "TEKAN BEG KUNING ↓", ImageFont.truetype(DJ, 62), "white")


layer(cta, f"{OUT}/r4.png")


# ---------- SFX ----------
def save(name, st, gain):
    st = st / (np.abs(st).max() + 1e-9) * gain
    with wave.open(f"{OUT}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


t = np.arange(int(0.6 * SR)) / SR
ding = (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2636 * t) + 0.25 * np.sin(2 * np.pi * 3954 * t)) * np.exp(-t * 7)
save("ding", np.stack([ding, ding], 1), 0.8)
t = np.arange(int(0.35 * SR)) / SR
buzz = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.6 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.4
buzz *= np.minimum(1, t * 60) * np.exp(-t * 4)
save("buzz", np.stack([buzz, buzz], 1), 0.5)
t = np.arange(int(0.18 * SR)) / SR
tick = np.sin(2 * np.pi * (1800 - 2000 * t) * t) * np.exp(-t * 30)
save("tick", np.stack([tick, tick], 1), 0.7)
print("ok")
