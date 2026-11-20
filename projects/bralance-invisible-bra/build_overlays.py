"""Render text overlays and product cards (1080x1920 RGBA PNGs) for the Bralance ad.

Usage: python3 build_overlays.py <out_dir>
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
REF = HERE / "reference"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"

WHITE = (255, 255, 255)
PINK = (255, 92, 150)
MAUVE = (92, 60, 66)
BLUSH = (248, 236, 236)
GOLD = (255, 196, 46)


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_runs(img, y, lines, fpath, size, stroke=10, stroke_fill=(0, 0, 0), shadow=True):
    """lines: list of lists of (text, color). Centered. Returns bottom y."""
    d = ImageDraw.Draw(img)
    f = font(fpath, size)
    lh = int(size * 1.18)
    for runs in lines:
        widths = [d.textlength(t, font=f) for t, _ in runs]
        x = (W - sum(widths)) / 2
        if shadow:
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            sd = ImageDraw.Draw(sh)
            xx = x
            for (t, _), w in zip(runs, widths):
                sd.text((xx + 4, y + 8), t, font=f, fill=(0, 0, 0, 150),
                        stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
                xx += w
            img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        for (t, c), w in zip(runs, widths):
            d.text((x, y), t, font=f, fill=c, stroke_width=stroke, stroke_fill=stroke_fill)
            x += w
        y += lh
    return y


def pill(img, cx, y, text, fpath, size, bg, fg, pad=(34, 16)):
    d = ImageDraw.Draw(img)
    f = font(fpath, size)
    tw = d.textlength(text, font=f)
    box = (cx - tw / 2 - pad[0], y, cx + tw / 2 + pad[0], y + size + pad[1] * 2)
    d.rounded_rectangle(box, radius=(size + pad[1] * 2) // 2, fill=bg)
    d.text((cx - tw / 2, y + pad[1] - size * 0.08), text, font=f, fill=fg)
    return box[3]


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def poster(name):
    """Crop the square product poster out of a TikTok Shop screenshot."""
    im = Image.open(REF / name).convert("RGB")
    sx, sy = im.width / 901, im.height / 2000
    return im.crop((int(27 * sx), int(527 * sy), int(873 * sx), int(1316 * sy)))


def card(name, kicker, head_lines, sub, out):
    img = Image.new("RGBA", (W, H), BLUSH + (255,))
    d = ImageDraw.Draw(img)
    # soft vignette
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse((-300, -200, W + 300, H + 200), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    tint = Image.new("RGBA", (W, H), (226, 196, 198, 255))
    img = Image.composite(img, tint, v)
    d = ImageDraw.Draw(img)
    pill(img, W / 2, 250, kicker, XBOLD, 38, PINK, WHITE)
    y = 360
    f = font(SERIF, 92)
    for line in head_lines:
        tw = d.textlength(line, font=f)
        d.text(((W - tw) / 2, y), line, font=f, fill=MAUVE)
        y += 104
    p = poster(name)
    pw = 960
    p = p.resize((pw, int(p.height * pw / p.width)), Image.LANCZOS)
    py = y + 40
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(((W - pw) / 2, py + 18, (W + pw) / 2, py + p.height + 18),
                                          radius=36, fill=(90, 50, 60, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    m = Image.new("L", p.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), radius=36, fill=255)
    img.paste(p, ((W - pw) // 2, py), m)
    fs = font(SEMI, 44)
    yy = py + p.height + 50
    for line in sub:
        tw = d.textlength(line, font=fs)
        d.text(((W - tw) / 2, yy), line, font=fs, fill=MAUVE)
        yy += 58
    img.save(OUT / out)


# ---------- HOOK (0.0 - 3.0s) ----------
img = blank()
pill(img, W / 2, 250, "GIRLS, JANGAN SCROLL DULU!", XBOLD, 36, (0, 0, 0, 170), WHITE)
draw_runs(img, 360, [
    [("Pakai baju ", WHITE), ("backless", PINK)],
    [("tapi takut ", WHITE), ("TALI BRA", GOLD)],
    [("NAMPAK?", GOLD)],
], BLACK, 96)
img.save(OUT / "t_hook.png")

img = blank()
draw_runs(img, 380, [[("Cuba yang ni", WHITE)], [("RM25 je!", PINK)]], BLACK, 110)
img.save(OUT / "t_hook2.png")

# ---------- feature captions ----------
def caption(lines, out, size=88, y=340):
    img = blank()
    draw_runs(img, y, lines, BLACK, size, stroke=9)
    img.save(OUT / out)

caption([[("Silikon ", WHITE), ("lembut", PINK)], [("+ klip depan", WHITE)], [("pasang 10 saat", WHITE)]], "t_soft.png")
caption([[("Kekal ", WHITE), ("melekat", PINK)], [("walaupun ", WHITE), ("berpeluh", GOLD)]], "t_sweat.png")
caption([[("Bentuk ", WHITE), ("mango cup", PINK)], [("angkat & bentuk", WHITE)], [("lebih cantik", WHITE)]], "t_mango.png")
caption([[("Nipis sampai", WHITE)], [("nampak tangan!", GOLD)]], "t_thin.png", size=96)
caption([[("Boleh basuh &", WHITE)], [("pakai ", WHITE), ("berulang kali", PINK)]], "t_reuse.png")

# ---------- product cards ----------
card("p2-thin-edge.jpg", "RAHSIA DIA", ["Tepi cuma 0.1cm"], ["Tak timbul langsung bawah baju ketat"], "c_thin.png")
card("p5-how-to-wear.jpg", "CARA PAKAI", ["6 langkah mudah"], ["Tak perlu tali, tak perlu cangkuk belakang"], "c_howto.png")

# ---------- social proof ----------
img = blank()
d = ImageDraw.Draw(img)
box = (90, 330, W - 90, 880)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 16, box[2], box[3] + 16), radius=44, fill=(0, 0, 0, 120))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
d.rounded_rectangle(box, radius=44, fill=(255, 255, 255, 245))
fstar = font(BLACK, 70)
# five stars drawn as polygons (no emoji font needed)
import math
def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)
for i in range(5):
    star(W / 2 - 160 + i * 80, 420, 34, GOLD)
fq = font(SERIF_I, 64)
for i, line in enumerate(["“Lembut & melekat kuat.", "Senang nak bersihkan.”"]):
    tw = d.textlength(line, font=fq)
    d.text(((W - tw) / 2, 490 + i * 78), line, font=fq, fill=MAUVE)
fs = font(XBOLD, 42)
line = "127 review 5 bintang"
tw = d.textlength(line, font=fs)
d.text(((W - tw) / 2, 690), line, font=fs, fill=PINK)
fs2 = font(SEMI, 36)
line = "dari pembeli sebenar di TikTok Shop"
tw = d.textlength(line, font=fs2)
d.text(((W - tw) / 2, 750), line, font=fs2, fill=(140, 110, 115))
img.save(OUT / "t_review.png")

# ---------- CTA end (dark scrim + kit + price) ----------
img = Image.new("RGBA", (W, H), (30, 14, 20, 170))
d = ImageDraw.Draw(img)
p = poster("p7-kit.jpg")
pw = 820
p = p.resize((pw, int(p.height * pw / p.width)), Image.LANCZOS)
m = Image.new("L", p.size, 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), radius=40, fill=255)
img.paste(p, ((W - pw) // 2, 470), m)
pill(img, W / 2, 230, "SET LENGKAP", XBOLD, 40, PINK, WHITE)
draw_runs(img, 320, [[("Kotak + beg satin + pelekat", WHITE)]], XBOLD, 50, stroke=0, shadow=True)
y = 470 + p.height + 40
draw_runs(img, y, [[("RM25", GOLD), (" sahaja", WHITE)]], BLACK, 120, stroke=8)
pill(img, W / 2, y + 160, "FREE SHIPPING  |  SAIZ A - D", XBOLD, 40, WHITE, MAUVE)
draw_runs(img, y + 270, [[("Tekan ", WHITE), ("beg kuning", GOLD), (" sekarang", WHITE)]], BLACK, 64, stroke=7)
img.save(OUT / "t_cta.png")

# brand bug (top-left, whole video)
img = blank()
d = ImageDraw.Draw(img)
f = font(SERIF, 46)
d.text((58, 120), "bralance", font=f, fill=(255, 255, 255, 230), stroke_width=2, stroke_fill=(0, 0, 0, 120))
img.save(OUT / "t_brand.png")
print("ok", sorted(x.name for x in OUT.iterdir()))
