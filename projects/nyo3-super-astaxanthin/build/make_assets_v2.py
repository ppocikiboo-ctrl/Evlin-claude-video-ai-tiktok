"""V2 assets: 'Jangan scroll' hook + '3 sebab' listicle, dark ruby/gold theme."""
import sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]; W, H = 1080, 1920
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
RUBY, GOLD, WHITE, DARK = (214, 20, 70), (255, 200, 60), (255, 255, 255), (25, 5, 20)
f = ImageFont.truetype

def txt(d, cx, y, s, font, fg=WHITE, sw=9, sc=(0, 0, 0)):
    bb = d.textbbox((0, 0), s, font=font, stroke_width=sw)
    d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], y - bb[1]), s, font=font, fill=fg, stroke_width=sw, stroke_fill=sc)
    return y + bb[3] - bb[1]

def box(d, cx, y, s, font, fg, bg, pad=(32, 16), r=16):
    bb = d.textbbox((0, 0), s, font=font); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = cx - tw // 2 - pad[0]
    d.rounded_rectangle([x0, y, x0 + tw + 2 * pad[0], y + th + 2 * pad[1]], r, fill=bg)
    d.text((x0 + pad[0] - bb[0], y + pad[1] - bb[1]), s, font=font, fill=fg)
    return y + th + 2 * pad[1]

def badge(d, cx, y, n):
    d.ellipse([cx - 70, y, cx + 70, y + 140], fill=GOLD, outline=DARK, width=8)
    d.text((cx, y + 70), n, font=f(XB, 96), fill=DARK, anchor="mm")
    return y + 160

def card(name, draw_fn):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(im)); im.save(f"{OUT}/{name}.png")

def hook(d):
    d.rectangle([0, 230, W, 560], fill=(214, 20, 70, 235))
    txt(d, W // 2, 260, "JANGAN SCROLL", f(XB, 120), sw=0)
    txt(d, W // 2, 420, "kalau kulit kau tak pernah", f(SB, 52), sw=0)
    txt(d, W // 2, 490, "kering & kusam", f(XB, 60), fg=GOLD, sw=0)
card("v2_hook", hook)

def reasons(d):
    y = txt(d, W // 2, 300, "3 SEBAB", f(XB, 140), fg=GOLD, sw=12)
    txt(d, W // 2, y + 30, "AKU MAKAN NI TIAP HARI", f(XB, 72), sw=10)
card("v2_3sebab", reasons)

def r1(d):
    y = badge(d, W // 2, 1180, "1")
    y = box(d, W // 2, y, "12mg ASTAXANTHIN", f(XB, 72), WHITE, RUBY) + 14
    box(d, W // 2, y, "antioksidan semula jadi dari alga merah", f(SB, 40), WHITE, (0, 0, 0, 190), pad=(24, 12))
card("v2_r1", r1)

def r2(d):
    y = badge(d, W // 2, 1180, "2")
    y = box(d, W // 2, y, "+ VITAMIN C & E", f(XB, 72), WHITE, RUBY) + 14
    box(d, W // 2, y, "bantu kelembapan & keanjalan kulit", f(SB, 40), WHITE, (0, 0, 0, 190), pad=(24, 12))
card("v2_r2", r2)

def r3(d):
    y = badge(d, W // 2, 1180, "3")
    y = box(d, W // 2, y, "SENANG GILA", f(XB, 72), DARK, GOLD) + 14
    box(d, W // 2, y, "2 biji sehari lepas makan - 1 botol 30 hari", f(SB, 40), WHITE, (0, 0, 0, 190), pad=(24, 12))
card("v2_r3", r3)

# photo card background (photo panned in render): dark ruby
bg = Image.new("RGB", (W, H)); bd = ImageDraw.Draw(bg)
for yy in range(H):
    t = yy / H; bd.line([(0, yy), (W, yy)], fill=(int(70 - 40 * t), int(8 + 2 * t), int(35 - 10 * t)))
txt(bd, W // 2, 200, "MATAHARI. STRES. UMUR.", f(XB, 76), fg=GOLD, sw=0)
txt(bd, W // 2, 320, "kulit pun penat...", f(XB, 84), sw=0)
y = box(bd, W // 2, 1490, "LAWAN DENGAN ANTIOKSIDAN", f(XB, 58), WHITE, RUBY)
bd.text((W // 2, 1790), "Gambar hiasan. Hasil berbeza mengikut individu.", font=f(SB, 34), fill=(230, 200, 210), anchor="mm")
bg.save(f"{OUT}/v2_photo_bg.png")

def cta(d):
    txt(d, W // 2, 380, "CUBA 30 HARI", f(XB, 130), fg=GOLD, sw=12)
    txt(d, W // 2, 560, "rasa sendiri bezanya", f(XB, 70), sw=9)
    y = box(d, W // 2, 1300, "TEKAN BEG KUNING", f(XB, 76), DARK, GOLD, pad=(44, 26), r=24)
    d.polygon([(200, y + 40), (280, y + 40), (240, y + 130)], fill=GOLD)          # arrow toward basket
    d.rectangle([225, y + 10, 255, y + 45], fill=GOLD)
    d.text((W // 2, 1790), "Suplemen makanan. Bukan ubat. Hasil berbeza mengikut individu.", font=f(SB, 30), fill=WHITE, anchor="mm")
card("v2_cta", cta)

# faster 124 bpm beat with clap on 2 & 4
sr, dur, bpm = 44100, 17.0, 124
n = int(sr * dur); out = np.zeros(n); beat = 60 / bpm; rng = np.random.default_rng(7)
bass = [55.0, 55.0, 43.65, 49.0]
i = 0
while i * beat < dur:
    s0 = int(i * beat * sr); L = min(int(0.3 * sr), n - s0); tt = np.arange(L) / sr
    out[s0:s0 + L] += 0.55 * np.sin(2 * np.pi * (45 + 100 * np.exp(-tt * 35)) * tt) * np.exp(-tt * 12)
    if i % 2 == 1:
        L2 = min(int(0.12 * sr), n - s0)
        out[s0:s0 + L2] += 0.18 * rng.standard_normal(L2) * np.exp(-np.arange(L2) / sr * 30)
    for half in (0.5,):
        h0 = int((i + half) * beat * sr)
        if h0 < n:
            L3 = min(int(0.2 * sr), n - h0); t3 = np.arange(L3) / sr
            fb = bass[(i // 4) % 4]
            out[h0:h0 + L3] += 0.22 * np.sign(np.sin(2 * np.pi * fb * t3)) * np.exp(-t3 * 10)
    i += 1
out[-sr:] *= np.linspace(1, 0, sr)
out = (out / np.abs(out).max() * 0.6 * 32767).astype(np.int16)
with wave.open(f"{OUT}/v2_beat.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(out.tobytes())
print("ok")
