"""Generate text overlays, skin illustration card and a light background beat."""
import math, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H = 1080, 1920
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
PINK, PURPLE, WHITE, YEL = (255, 64, 160), (120, 40, 200), (255, 255, 255), (255, 214, 0)

def f(path, size): return ImageFont.truetype(path, size)

def pill_text(d, cx, y, text, font, fg, bg, pad=(34, 18), r=28):
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = cx - tw // 2 - pad[0]; y0 = y
    d.rounded_rectangle([x0, y0, x0 + tw + 2 * pad[0], y0 + th + 2 * pad[1]], r, fill=bg)
    d.text((x0 + pad[0] - bb[0], y0 + pad[1] - bb[1]), text, font=font, fill=fg)
    return y0 + th + 2 * pad[1]

def stroke_text(d, cx, y, text, font, fg=WHITE, sw=10, sc=(0, 0, 0)):
    bb = d.textbbox((0, 0), text, font=font, stroke_width=sw)
    d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], y - bb[1]), text, font=font, fill=fg,
           stroke_width=sw, stroke_fill=sc)
    return y + bb[3] - bb[1]

def overlay(name, lines, y):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for kind, text in lines:
        if kind == "big":   y = stroke_text(d, W // 2, y, text, f(XB, 104)) + 22
        elif kind == "yel": y = stroke_text(d, W // 2, y, text, f(XB, 104), fg=YEL) + 22
        elif kind == "pill": y = pill_text(d, W // 2, y, text, f(XB, 62), WHITE, PINK) + 16
        elif kind == "pillp": y = pill_text(d, W // 2, y, text, f(XB, 58), WHITE, PURPLE) + 16
        elif kind == "small": y = pill_text(d, W // 2, y, text, f(SB, 40), WHITE, (0, 0, 0, 170), pad=(26, 12), r=20) + 12
    im.save(f"{OUT}/{name}.png")

# 1) HOOK
overlay("t1_hook", [("big", "KULIT KUSAM"), ("big", "& KERING?"), ("yel", "TENGOK NI DULU")], 260)
# 2) What it is
overlay("t2_what", [("pill", "12mg ASTAXANTHIN"), ("small", "antioksidan semula jadi dari alga merah"),
                    ("small", "(Haematococcus pluvialis)")], 1330)
# 3) How to take
overlay("t3_how", [("pillp", "2 SOFTGEL SEHARI"), ("small", "ambil bersama makanan"),
                   ("small", "1 botol = 30 hari")], 1330)
# 4) Ingredients
overlay("t4_ing", [("pill", "+ VITAMIN C 120mg"), ("pill", "+ VITAMIN E 60mg"), ("pillp", "+ FLAXSEED OIL")], 1260)

# 5) Skin illustration card (clearly labelled illustration, NOT a real result)
def face(skin, glow):
    s = 440; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([20, 0, 420, 300], fill=(60, 35, 30))                       # hair
    d.ellipse([70, 40, 370, 420], fill=skin)                               # face
    if glow:
        m = Image.new("L", (s, s), 0); md = ImageDraw.Draw(m)
        md.ellipse([105, 250, 195, 330], fill=150); md.ellipse([245, 250, 335, 330], fill=150)
        md.ellipse([180, 80, 290, 150], fill=130); md.ellipse([205, 270, 235, 320], fill=120)
        m = m.filter(ImageFilter.GaussianBlur(20))
        fm = Image.new("L", (s, s), 0); ImageDraw.Draw(fm).ellipse([70, 40, 370, 420], fill=255)
        m = Image.fromarray((np.asarray(m, float) * np.asarray(fm, float) / 255).astype(np.uint8))
        im.paste(Image.new("RGBA", (s, s), (255, 250, 245, 255)), (0, 0), m)
        d = ImageDraw.Draw(im)
        for (x, y) in [(105, 300), (305, 300)]:
            d.ellipse([x - 32, y - 18, x + 32, y + 18], fill=(255, 120, 150, 110))
    else:
        rng = np.random.default_rng(3)
        for _ in range(70):                                                # dry flakes / dull spots
            x, y = rng.integers(100, 340), rng.integers(120, 400)
            if ((x - 220) / 140) ** 2 + ((y - 230) / 180) ** 2 > 1: continue
            d.ellipse([x, y, x + 7, y + 7], fill=(140, 105, 85, 200))
        for x in (115, 295):                                               # fine lines
            d.arc([x - 10, 200, x + 40, 250], 200, 300, fill=(140, 100, 85), width=3)
    d.arc([140, 200, 200, 240], 200, 340, fill=(50, 30, 30), width=6)      # eyes closed
    d.arc([240, 200, 300, 240], 200, 340, fill=(50, 30, 30), width=6)
    d.arc([185, 300, 255, 350], 20, 160, fill=(170, 60, 80), width=7)      # smile
    return im

def sparkle(d, x, y, r, col=WHITE):
    d.polygon([(x, y - r), (x + r * .25, y - r * .25), (x + r, y), (x + r * .25, y + r * .25),
               (x, y + r), (x - r * .25, y + r * .25), (x - r, y), (x - r * .25, y - r * .25)], fill=col)

card = Image.new("RGBA", (W, H)); cd = ImageDraw.Draw(card)
for yy in range(H):                                                        # pink→purple bg
    t = yy / H; cd.line([(0, yy), (W, yy)], fill=(int(255 - 120 * t), int(90 - 50 * t), int(190 + 30 * t)))
stroke_text(cd, W // 2, 120, "KULIT SELEPAS", f(XB, 92))
stroke_text(cd, W // 2, 230, "AMALAN RUTIN", f(XB, 92), fg=YEL)
for i, (lab, skin, glow, y) in enumerate([("SEBELUM", (196, 160, 135), False, 420),
                                           ("SELEPAS", (247, 205, 180), True, 1060)]):
    cd.rounded_rectangle([110, y, 970, y + 580], 40, fill=(255, 255, 255, 235))
    fc = face(skin, glow)
    if not glow: fc = Image.blend(fc, fc.convert("LA").convert("RGBA"), 0.45)
    card.alpha_composite(fc, (100 + 40, y + 70))
    cd = ImageDraw.Draw(card)
    pill_text(cd, 760, y + 120, lab, f(XB, 54), WHITE, PURPLE if glow else (110, 110, 120))
    tf = f(SB, 38)
    notes = ["lembap & anjal", "nampak lebih", "berseri"] if glow else ["kering", "kusam", "garis halus"]
    for j, n in enumerate(notes):
        cd.text((640, y + 250 + j * 60), ("✓ " if glow else "• ") + n, font=tf, fill=(60, 20, 90))
    if glow:
        for (x, yy, r) in [(170, y + 90, 26), (560, y + 110, 20), (470, y + 470, 30), (200, y + 430, 16)]:
            sparkle(cd, x, yy, r, YEL)
cd.text((W // 2, 1700), "ILUSTRASI SAHAJA. Bukan gambar sebenar.", font=f(SB, 36), fill=WHITE, anchor="mm")
cd.text((W // 2, 1750), "Hasil berbeza mengikut individu.", font=f(SB, 36), fill=WHITE, anchor="mm")
card.convert("RGB").save(f"{OUT}/skin_card.png")

# 6) CTA end card overlay
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
y = stroke_text(d, W // 2, 520, "GLOW DARI DALAM", f(XB, 96)) + 30
y = stroke_text(d, W // 2, y, "BERMULA HARI NI", f(XB, 96), fg=YEL) + 70
y = pill_text(d, W // 2, y, "TEKAN BEG KUNING SEKARANG", f(XB, 60), (30, 0, 50), YEL, pad=(40, 26)) + 30
pill_text(d, W // 2, y, "stok terhad - checkout sebelum habis", f(SB, 40), WHITE, PINK, pad=(26, 12), r=20)
d.text((W // 2, 1780), "Suplemen makanan. Bukan ubat. Hasil berbeza mengikut individu.", font=f(SB, 30), fill=WHITE, anchor="mm")
im.save(f"{OUT}/t5_cta.png")

# 7) Light upbeat background beat (~16 s, 110 bpm), royalty-free (synthesised)
sr, dur, bpm = 44100, 16.0, 110
n = int(sr * dur); t = np.arange(n) / sr; out = np.zeros(n)
beat = 60 / bpm
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
bar = beat * 4
for k in range(int(dur / bar) + 1):
    s0 = int(k * bar * sr); s1 = min(n, int((k + 1) * bar * sr))
    if s0 >= n: break
    tt = t[s0:s1] - t[s0]; env = np.minimum(1, tt * 4) * np.exp(-tt * 0.4)
    for fr in chords[k % 4]:
        out[s0:s1] += 0.06 * env * (np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(4 * np.pi * fr * tt))
i = 0
while i * beat < dur:
    s0 = int(i * beat * sr); L = min(int(0.25 * sr), n - s0); tt = np.arange(L) / sr
    out[s0:s0 + L] += 0.5 * np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)  # kick
    h0 = int((i + 0.5) * beat * sr)
    if h0 < n:
        L = min(int(0.05 * sr), n - h0)
        out[h0:h0 + L] += 0.08 * np.random.default_rng(i).standard_normal(L) * np.exp(-np.arange(L) / sr * 80)
    i += 1
out[-int(sr * 1.0):] *= np.linspace(1, 0, int(sr * 1.0))
out = (out / np.abs(out).max() * 0.6 * 32767).astype(np.int16)
with wave.open(f"{OUT}/beat.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(out.tobytes())
print("ok")

# 8) Background card for the user-supplied skin-ageing photo (photo is panned in render.sh)
bg = Image.new("RGBA", (W, H)); bd = ImageDraw.Draw(bg)
for yy in range(H):
    t = yy / H; bd.line([(0, yy), (W, yy)], fill=(int(255 - 120 * t), int(90 - 50 * t), int(190 + 30 * t)))
stroke_text(bd, W // 2, 200, "KULIT CEPAT", f(XB, 100))
stroke_text(bd, W // 2, 320, "NAMPAK PENAT?", f(XB, 100), fg=YEL)
y = pill_text(bd, W // 2, 1480, "JAGA KULIT DARI DALAM", f(XB, 62), WHITE, PURPLE) + 20
pill_text(bd, W // 2, y, "antioksidan bantu kelembapan & keanjalan", f(SB, 42), WHITE, PINK, pad=(26, 12), r=20)
bd.text((W // 2, 1790), "Gambar hiasan. Hasil berbeza mengikut individu.", font=f(SB, 34), fill=WHITE, anchor="mm")
bg.convert("RGB").save(f"{OUT}/aging_bg.png")
