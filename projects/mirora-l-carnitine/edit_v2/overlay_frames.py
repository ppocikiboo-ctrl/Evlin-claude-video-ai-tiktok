"""Stream animated RGBA overlay frames (1080x1920 @30fps) to stdout.

Usage: python3 overlay_frames.py <duration_s> | ffmpeg -f rawvideo -pix_fmt rgba ...
Contains: pop-in cards, hook slam + shake, white flashes on cuts, gold
sparkles, 10-day tracker, 3L water bar, pulsing CTA, bouncing pointer,
progress bar.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from timeline import CARDS, CUTS, DAY_DOTS, FPS, H, W, WATER_FILL

DUR = float(sys.argv[1])
NF = int(round(DUR * FPS))

INTER_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
INTER_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF_BOLD = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

CREAM = (250, 242, 232, 240)
BROWN = (92, 45, 20, 255)
GOLD = (196, 146, 82, 255)
GOLD_DARK = (150, 98, 45, 255)
WHITE = (255, 255, 255, 255)


def F(p, s):
    return ImageFont.truetype(p, s)


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / im.height
    return im.resize((max(1, int(im.width * r)), size), Image.LANCZOS)


def card(lines, *, pad=(48, 30), gap=14, radius=46, emoji_ch=None,
         emoji_size=90, fill=CREAM, border=GOLD):
    """Returns a tightly-cropped RGBA card (with soft shadow)."""
    ms = []
    for t, f, _ in lines:
        b = f.getbbox(t)
        ms.append((b[2] - b[0], b[3] - b[1], b))
    tw = max(m[0] for m in ms)
    th = sum(m[1] for m in ms) + gap * (len(lines) - 1)
    em = emoji(emoji_ch, emoji_size) if emoji_ch else None
    ew = em.width + 24 if em else 0
    cw, ch = tw + ew + pad[0] * 2, max(th, em.height if em else 0) + pad[1] * 2
    m = 30
    im = Image.new("RGBA", (cw + 2 * m, ch + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 10, m + cw, m + ch + 10), radius,
                                         fill=(60, 30, 10, 100))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((m, m, m + cw, m + ch), radius, fill=fill, outline=border, width=5)
    cx = m + pad[0]
    if em:
        im.alpha_composite(em, (cx, m + (ch - em.height) // 2))
        cx += ew
    y = m + (ch - th) // 2
    for (t, f, col), (w_, h_, b) in zip(lines, ms):
        d.text((cx + (tw - w_) // 2 - b[0], y - b[1]), t, font=f, fill=col)
        y += h_ + gap
    return im


CARD_IMG = {
    "hook": card([("SEHARI SEBIJI JE?", F(INTER_BLACK, 80), BROWN),
                  ("ni rutin pagi aku sekarang", F(INTER_SEMI, 44), GOLD_DARK)],
                 emoji_ch="👀", emoji_size=100, pad=(46, 34)),
    "brand": card([("MIRORA", F(SERIF_BOLD, 96), BROWN),
                   ("L-CARNITINE COMPLEX", F(INTER_BOLD, 40), GOLD_DARK)],
                  emoji_ch="✨", emoji_size=84),
    "benefit": card([("Sokong Tenaga", F(INTER_BLACK, 64), BROWN),
                     ("& Metabolisme*", F(INTER_BLACK, 64), BROWN)],
                    emoji_ch="⚡", emoji_size=100),
    "pack": card([("10 KAPSUL = 10 HARI", F(INTER_BLACK, 72), BROWN),
                  ("cukup untuk cuba dulu", F(INTER_SEMI, 42), GOLD_DARK)],
                 emoji_ch="💊", emoji_size=100),
    "howto": card([("1 BIJI", F(INTER_BLACK, 80), BROWN),
                   ("selepas sarapan pagi", F(INTER_SEMI, 46), GOLD_DARK)],
                  emoji_ch="☀️", emoji_size=104),
    "water": card([("MINUM 3L AIR", F(INTER_BLACK, 76), BROWN),
                   ("setiap hari, wajib!", F(INTER_SEMI, 46), GOLD_DARK)],
                  emoji_ch="💧", emoji_size=104),
    "bag": card([("Kecil • Premium", F(INTER_BLACK, 66), BROWN),
                 ("muat dalam beg tangan", F(INTER_SEMI, 44), GOLD_DARK)],
                emoji_ch="👜", emoji_size=100),
    "cta": card([("TEKAN BEG KUNING", F(INTER_BLACK, 76), WHITE),
                 ("stok terhad, jangan tunggu!", F(INTER_BOLD, 44), (255, 240, 215, 255))],
                emoji_ch="🛒", emoji_size=104, fill=(184, 128, 62, 248),
                border=(255, 236, 205, 255)),
}
DISCLAIMER = card([("*Hasil berbeza bagi setiap individu", F(INTER_SEMI, 30), WHITE)],
                  fill=(40, 22, 10, 160), border=(0, 0, 0, 0), pad=(28, 14), radius=24)
ARROW = emoji("👇", 130)

# ----------------------------------------------------------- small widgets
DOT_R = 26
DOT_GAP = 22
DOT_FONT = F(INTER_BLACK, 24)
LABEL_FONT = F(INTER_BOLD, 34)


def day_tracker(n_on, pop_i, pop_k):
    w = 10 * DOT_R * 2 + 9 * DOT_GAP + 60
    im = Image.new("RGBA", (w, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 139), 36, fill=(40, 22, 10, 150))
    lbl = "HARI 1 → 10" if n_on < 10 else "10 HARI ✓"
    b = LABEL_FONT.getbbox(lbl)
    d.text(((w - (b[2] - b[0])) // 2 - b[0], 14 - b[1]), lbl, font=LABEL_FONT, fill=WHITE)
    for i in range(10):
        cx = 30 + DOT_R + i * (DOT_R * 2 + DOT_GAP)
        cy = 95
        r = DOT_R
        if i < n_on:
            if i == pop_i:
                r = int(DOT_R * (1 + 0.35 * math.sin(math.pi * pop_k)))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD, outline=WHITE, width=3)
            s = str(i + 1)
            bb = DOT_FONT.getbbox(s)
            d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), s,
                   font=DOT_FONT, fill=WHITE)
        else:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 170), width=3)
    return im


def water_bar(p):
    w, h = 640, 120
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(40, 22, 10, 150))
    x0, y0, x1, y1 = 30, 62, w - 30, 98
    d.rounded_rectangle((x0, y0, x1, y1), 18, fill=(255, 255, 255, 70))
    fx = x0 + (x1 - x0) * p
    if fx > x0 + 36:
        d.rounded_rectangle((x0, y0, fx, y1), 18, fill=(86, 180, 233, 255))
        # wave highlight
        d.rounded_rectangle((x0 + 6, y0 + 5, fx - 6, y0 + 13), 4, fill=(200, 235, 255, 200))
    litres = 3 * p
    lbl = f"{litres:0.1f}L / 3L" if p < 1 else "3L ✓  badan terhidrat!"
    b = LABEL_FONT.getbbox(lbl)
    d.text(((w - (b[2] - b[0])) // 2 - b[0], 14 - b[1]), lbl, font=LABEL_FONT, fill=WHITE)
    return im


def sparkle(size, alpha):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    r1, r2 = size / 2, size / 9
    pts = []
    for k in range(8):
        a = k * math.pi / 4 - math.pi / 2
        r = r1 if k % 2 == 0 else r2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=(255, 226, 160, int(255 * alpha)))
    d.ellipse((c - r2, c - r2, c + r2, c + r2), fill=(255, 255, 255, int(255 * alpha)))
    return im


SPARKS = [(-0.05, 0.1, 0.0), (1.02, 0.2, 1.3), (0.15, 1.05, 2.1), (0.85, -0.05, 0.7),
          (0.5, 1.12, 3.0), (-0.02, 0.85, 4.2), (1.05, 0.9, 5.1), (0.35, -0.12, 2.6)]


# ----------------------------------------------------------- easing
def ease_out_back(x, s=1.9):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def paste_scaled(canvas, img, cx, cy, scale, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if abs(scale - 1) > 0.003:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))),
                         Image.BILINEAR)
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


out = sys.stdout.buffer
BAR_H = 10
for fi in range(NF):
    t = fi / FPS
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    for name, s, e, y in CARDS:
        if not (s <= t < min(e, DUR)):
            continue
        img = CARD_IMG[name]
        lt, rem = t - s, min(e, DUR) - t
        cx, cy = W / 2, y + img.height / 2
        if name == "hook":
            # slam: big -> 1, plus a short shake
            k = min(1, lt / 0.22)
            scale = 1.6 - 0.6 * (1 - (1 - k) ** 3)
            alpha = min(1, lt / 0.1)
            if 0.22 < lt < 0.6:
                amp = 14 * (1 - (lt - 0.22) / 0.38)
                cx += amp * math.sin(lt * 90)
                cy += amp * 0.5 * math.cos(lt * 70)
            if lt > 1.2:  # gentle breathing so it never feels static
                scale *= 1 + 0.02 * math.sin((lt - 1.2) * 4)
        else:
            k = min(1, lt / 0.32)
            scale = 0.55 + 0.45 * ease_out_back(k)
            alpha = min(1, lt / 0.12)
        if name == "cta" and lt > 0.4:
            scale *= 1 + 0.045 * abs(math.sin(math.pi * (lt - 0.4) * 1.6))
        if rem < 0.18:
            scale *= 0.85 + 0.15 * rem / 0.18
            alpha *= rem / 0.18
        paste_scaled(cv, img, cx, cy, scale, alpha)

        # sparkles around premium moments
        if name in ("brand", "cta", "bag"):
            bw, bh = img.width * scale, img.height * scale
            for (px, py, ph) in SPARKS:
                tw = 0.5 + 0.5 * math.sin(lt * 5 + ph * 2)
                sz = int(26 + 26 * tw)
                sx = cx - bw / 2 + px * bw
                sy = cy - bh / 2 + py * bh
                paste_scaled(cv, sparkle(sz, 0.35 + 0.65 * tw), sx, sy, 1, alpha)

        bottom = y + img.height + 10
        if name == "benefit" and lt > 0.2:
            paste_scaled(cv, DISCLAIMER, W / 2, bottom + DISCLAIMER.height / 2 - 20,
                         1, min(1, (lt - 0.2) / 0.2) * (alpha if rem < 0.18 else 1))
        if name == "pack":
            d0, d1 = DAY_DOTS
            step = (d1 - d0) / 10
            n_on = max(0, min(10, int((t - d0) / step) + 1)) if t >= d0 else 0
            pop_i = n_on - 1
            pop_k = min(1, ((t - d0) - pop_i * step) / 0.15) if n_on else 1
            if n_on == 10 and t - d0 > 10 * step:
                pop_k = 1
            tr = day_tracker(n_on, pop_i, pop_k)
            a2 = min(1, max(0, (lt - 0.15) / 0.2)) * (rem / 0.18 if rem < 0.18 else 1)
            paste_scaled(cv, tr, W / 2, bottom + tr.height / 2 - 14, 1, a2)
        if name == "water":
            w0, w1 = WATER_FILL
            p = max(0, min(1, (t - w0) / (w1 - w0)))
            p = 1 - (1 - p) ** 2
            wb = water_bar(p)
            a2 = min(1, max(0, (lt - 0.15) / 0.2)) * (rem / 0.18 if rem < 0.18 else 1)
            pulse = 1 + (0.08 * math.sin(math.pi * min(1, (t - w1) / 0.3)) if t >= w1 else 0)
            paste_scaled(cv, wb, W / 2, bottom + wb.height / 2 - 14, pulse, a2)
        if name == "cta" and lt > 0.3:
            ay = 1330 + 30 * abs(math.sin((lt - 0.3) * 5))
            paste_scaled(cv, ARROW, 150, ay, 1, min(1, (lt - 0.3) / 0.2))

    # progress bar (gold, top edge)
    pw = int(W * min(1, t / DUR))
    if pw > 0:
        cv.paste((196, 146, 82, 255), (0, 0, pw, BAR_H))

    # white flash on start + every cut
    fl = 0.0
    if t < 0.3:
        fl = 0.85 * (1 - t / 0.3)
    for c in CUTS:
        if c <= t < c + 0.17:
            fl = max(fl, 0.55 * (1 - (t - c) / 0.17))
    if fl > 0:
        cv.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 240, int(255 * fl))))

    out.write(cv.tobytes())
