"""Render the transparent overlay PNGs for the MIRORA L-Carnitine TikTok edit.

All overlays are drawn for a 1080x1920 canvas. The original clip already has
burned-in word captions in the middle of the frame, so every card sits in the
top band (below TikTok's top UI) to avoid covering them.

Usage: python3 render_overlays.py <out_dir>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "overlays")
OUT.mkdir(parents=True, exist_ok=True)

W = 1080
INTER_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
INTER_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF_BOLD = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

# Palette taken from the MIRORA label: cream, gold leaf, deep brown.
CREAM = (250, 242, 232, 238)
BROWN = (92, 45, 20, 255)
GOLD = (196, 146, 82, 255)
GOLD_DARK = (150, 98, 45, 255)
WHITE = (255, 255, 255, 255)


def emoji(ch: str, size: int) -> Image.Image:
    """Noto Color Emoji only renders at 109px; draw there and resize."""
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / im.height
    return im.resize((max(1, int(im.width * r)), size), Image.LANCZOS)


def text_size(font, s):
    b = font.getbbox(s)
    return b[2] - b[0], b[3] - b[1], b


def card(name, lines, *, pad=(48, 30), gap=14, radius=46, emoji_ch=None,
         emoji_size=86, fill=CREAM, border=GOLD, shadow=True):
    """lines: list of (text, font, color). Centered pill card, optional emoji left."""
    metrics = [text_size(f, t) for t, f, _ in lines]
    tw = max(m[0] for m in metrics)
    th = sum(m[1] for m in metrics) + gap * (len(lines) - 1)
    em = emoji(emoji_ch, emoji_size) if emoji_ch else None
    ew = em.width + 24 if em else 0
    cw = tw + ew + pad[0] * 2
    ch = max(th, em.height if em else 0) + pad[1] * 2
    m = 30  # margin for shadow
    im = Image.new("RGBA", (W, ch + m * 2), (0, 0, 0, 0))
    x0 = (W - cw) // 2
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            (x0, m + 10, x0 + cw, m + ch + 10), radius, fill=(60, 30, 10, 90))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, m, x0 + cw, m + ch), radius, fill=fill,
                        outline=border, width=5)
    cx = x0 + pad[0]
    if em:
        im.alpha_composite(em, (cx, m + (ch - em.height) // 2))
        cx += ew
    y = m + (ch - th) // 2
    for (t, f, col), (w_, h_, b) in zip(lines, metrics):
        x = cx + (tw - w_) // 2
        d.text((x - b[0], y - b[1]), t, font=f, fill=col)
        y += h_ + gap
    im.save(OUT / f"{name}.png")
    return im.size


def F(path, size):
    return ImageFont.truetype(path, size)


# 0 — Hook (big, punchy)
card("c0_hook", [
    ("SEHARI SEBIJI JE?", F(INTER_BLACK, 76), BROWN),
    ("ni rutin pagi aku sekarang", F(INTER_SEMI, 44), GOLD_DARK),
], emoji_ch="👀", emoji_size=96, pad=(46, 34))

# 1 — Brand reveal
card("c1_brand", [
    ("MIRORA", F(SERIF_BOLD, 92), BROWN),
    ("L-CARNITINE COMPLEX", F(INTER_BOLD, 40), GOLD_DARK),
], emoji_ch="✨", emoji_size=80)

# 2 — Benefit (label wording only, with disclaimer)
card("c2_benefit", [
    ("Sokong Tenaga", F(INTER_BLACK, 64), BROWN),
    ("& Metabolisme*", F(INTER_BLACK, 64), BROWN),
], emoji_ch="⚡", emoji_size=100)
card("c2_disclaimer", [
    ("*Hasil berbeza bagi setiap individu", F(INTER_SEMI, 30), WHITE),
], fill=(40, 22, 10, 150), border=(0, 0, 0, 0), pad=(28, 14), radius=24,
    shadow=False)

# 3 — Pack size
card("c3_pack", [
    ("10 KAPSUL = 10 HARI", F(INTER_BLACK, 72), BROWN),
    ("cukup untuk cuba dulu", F(INTER_SEMI, 42), GOLD_DARK),
], emoji_ch="💊", emoji_size=100)

# 4 — How to take
card("c4_howto", [
    ("1 BIJI", F(INTER_BLACK, 76), BROWN),
    ("selepas sarapan pagi", F(INTER_SEMI, 46), GOLD_DARK),
], emoji_ch="☀️", emoji_size=100)

# 5 — Water
card("c5_water", [
    ("MINUM 3L AIR", F(INTER_BLACK, 76), BROWN),
    ("setiap hari, wajib!", F(INTER_SEMI, 46), GOLD_DARK),
], emoji_ch="💧", emoji_size=104)

# 6 — Packaging
card("c6_pack", [
    ("Kecil • Premium", F(INTER_BLACK, 66), BROWN),
    ("muat dalam beg tangan", F(INTER_SEMI, 44), GOLD_DARK),
], emoji_ch="👜", emoji_size=100)

# 7 — CTA (gold, inverted)
card("c7_cta", [
    ("TEKAN BEG KUNING", F(INTER_BLACK, 76), WHITE),
    ("stok terhad, jangan tunggu!", F(INTER_BOLD, 44), (255, 240, 215, 255)),
], emoji_ch="🛒", emoji_size=104, fill=(184, 128, 62, 245),
    border=(255, 236, 205, 255))

# Bouncing pointer for the CTA (points down-left toward the shop basket)
arrow = emoji("👇", 130)
pad = Image.new("RGBA", (arrow.width + 20, arrow.height + 20), (0, 0, 0, 0))
pad.alpha_composite(arrow, (10, 10))
pad.save(OUT / "arrow.png")

print("rendered to", OUT)
