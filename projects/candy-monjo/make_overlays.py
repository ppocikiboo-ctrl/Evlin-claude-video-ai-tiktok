"""Render text overlays (PNG, 576x1024, transparent) for the Candy Monjo edit.
All text sits in the top band (y 11%-36%) so the bottle in the middle is never covered."""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 576, 1024
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
out = sys.argv[1]
PINK, WHITE, DARK, YELLOW = (230, 30, 90), (255, 255, 255), (20, 20, 20), (255, 214, 0)

def pill(draw, cx, y, text, size, fg, bg, pad=(22, 12), r=22):
    f = ImageFont.truetype(FONT, size)
    l, t, rr, b = draw.textbbox((0, 0), text, font=f)
    w, h = rr - l, b - t
    x0, y0 = cx - w // 2 - pad[0], y
    draw.rounded_rectangle([x0, y0, x0 + w + 2 * pad[0], y0 + h + 2 * pad[1]], r, fill=bg)
    draw.text((x0 + pad[0] - l, y0 + pad[1] - t), text, font=f, fill=fg)
    return y0 + h + 2 * pad[1]

def outlined(draw, cx, y, text, size, fg):
    f = ImageFont.truetype(FONT, size)
    l, t, rr, b = draw.textbbox((0, 0), text, font=f)
    draw.text((cx - (rr - l) // 2 - l, y - t), text, font=f, fill=fg, stroke_width=6, stroke_fill=DARK)
    return y + (b - t)

def save(name, fn):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im))
    im.save(f"{out}/{name}.png")

# Hook (0 - 8.4s)
save("hook", lambda d: (
    pill(d, W // 2, 118, "RAMAI DM TANYA...", 26, WHITE, PINK),
    outlined(d, W // 2, 180, "CARA AMBIL", 54, WHITE),
    outlined(d, W // 2, 245, "CANDY MONJO", 54, YELLOW)))
# Info chips, timed to the voiceover
save("chip_pagi", lambda d: pill(d, W // 2, 318, "1) PAGI, SEBELUM SARAPAN", 28, DARK, (255, 255, 255, 235)))
save("chip_biji", lambda d: pill(d, W // 2, 318, "2) 1 BIJI SEHARI  |  1 BOTOL = 7 BIJI", 25, DARK, (255, 255, 255, 235)))
# CTA (8.4s - end)
save("cta", lambda d: (
    outlined(d, W // 2, 160, "NAK CUBA?", 54, WHITE),
    pill(d, W // 2, 232, "TEKAN BEG KUNING", 34, DARK, YELLOW)))
