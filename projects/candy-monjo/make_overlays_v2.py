"""V2 overlays: question hook + a checklist that ticks along with the voiceover.
Everything stays in y < 400 px (of 1024) so the bottle is never covered."""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 576, 1024
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
out = sys.argv[1]
PINK, WHITE, DARK, YELLOW, GREEN = (236, 64, 122), (255, 255, 255), (25, 25, 25), (255, 214, 0), (46, 204, 113)

def font(s): return ImageFont.truetype(FONT, s)

def centered(d, y, text, size, fg, stroke=6):
    f = font(size); l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text(((W - (r - l)) // 2 - l, y - t), text, font=f, fill=fg, stroke_width=stroke, stroke_fill=DARK)

def pill(d, y, text, size, fg, bg, pad=(20, 11)):
    f = font(size); l, t, r, b = d.textbbox((0, 0), text, font=f)
    x0 = (W - (r - l)) // 2 - pad[0]
    d.rounded_rectangle([x0, y, x0 + (r - l) + 2 * pad[0], y + (b - t) + 2 * pad[1]], 20, fill=bg)
    d.text((x0 + pad[0] - l, y + pad[1] - t), text, font=f, fill=fg)

def save(name, fn):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fn(ImageDraw.Draw(im)); im.save(f"{out}/{name}.png")

save("v2_hook", lambda d: (
    pill(d, 130, "SOALAN NO.1 DALAM DM", 26, WHITE, PINK),
    centered(d, 200, "MACAM MANA", 58, WHITE),
    centered(d, 268, "NAK AMBIL?", 58, YELLOW)))
save("v2_header", lambda d: pill(d, 112, "CARA AMBIL CANDY MONJO", 28, DARK, YELLOW))
save("v2_cta", lambda d: pill(d, 112, "NAK CUBA? TEKAN BEG KUNING", 28, DARK, YELLOW))

# Checklist rows, one PNG each so they can pop in one by one
ROWS = ["WAKTU PAGI", "SEBELUM SARAPAN", "1 BIJI SEHARI", "1 BOTOL = 7 BIJI"]
X0, Y0, STEP = 150, 180, 52
for i, txt in enumerate(ROWS):
    def row(d, i=i, txt=txt):
        y = Y0 + i * STEP
        d.rounded_rectangle([X0 - 16, y - 6, X0 + 300, y + 40], 14, fill=(255, 255, 255, 225))
        d.ellipse([X0 - 4, y + 3, X0 + 26, y + 33], fill=GREEN)
        d.line([(X0 + 4, y + 18), (X0 + 10, y + 25), (X0 + 20, y + 10)], fill=WHITE, width=4)
        d.text((X0 + 38, y + 5), txt, font=font(25), fill=DARK)
    save(f"v2_row{i}", row)
