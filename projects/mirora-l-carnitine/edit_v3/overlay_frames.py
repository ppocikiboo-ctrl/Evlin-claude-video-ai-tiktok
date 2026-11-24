"""Stream v3 "digicam aesthetic" RGBA overlay frames (1080x1920 @30fps) to stdout.

Usage: python3 overlay_frames.py <duration_s> | ffmpeg -f rawvideo -pix_fmt rgba ...
HUD (REC + timecode + battery + orange date stamp), editorial serif
typewriter titles, light-leak sweeps on cuts, shutter blink at the start,
water / day counters, minimal CTA with bouncing arrow.
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from timeline import (CUTS, DATE_STAMP, DAY_COUNT, FPS, H, SECTIONS, TYPE_CPS, W,
                      WATER_COUNT)

DUR = float(sys.argv[1])
NF = int(round(DUR * FPS))

SERIF_BI = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
INTER_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MONO_B = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"

CREAM = (255, 248, 236)
GOLD = (236, 196, 128)
ORANGE = (255, 150, 40)
RED = (235, 50, 40)

F_TITLE = ImageFont.truetype(SERIF_BI, 82)
F_BRAND = ImageFont.truetype(SERIF_B, 150)
F_SUB = ImageFont.truetype(INTER_SEMI, 34)
F_SMALL = ImageFont.truetype(INTER_SEMI, 26)
F_HUD = ImageFont.truetype(MONO_B, 34)
F_DATE = ImageFont.truetype(MONO_B, 44)
F_COUNT = ImageFont.truetype(MONO_B, 64)


_TITLE_FONTS = {}


def title_font(s):
    """Shrink the serif title so the full line fits within 940px."""
    if s not in _TITLE_FONTS:
        b = F_TITLE.getbbox(s)
        size = int(82 * min(1, 940 / (b[2] - b[0])))
        _TITLE_FONTS[s] = ImageFont.truetype(SERIF_BI, size)
    return _TITLE_FONTS[s]


def spaced(s, n=4):
    """Letter-spaced small caps look."""
    return (" " * 0).join(s) if n == 0 else " ".join(s)


def text_layer(draw_fn, size=(W, 360), glow=None, shadow=True):
    """Draw text via draw_fn(draw) onto a layer, add soft shadow (+ optional glow)."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    if shadow:
        a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(10))
        sh = Image.new("RGBA", size, (40, 20, 8, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.75)))
        out.alpha_composite(sh, (0, 4))
    if glow:
        a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(glow[1]))
        g = Image.new("RGBA", size, glow[0] + (0,))
        g.putalpha(a.point(lambda v: int(v * 0.8)))
        out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def centered(d, y, s, font, fill):
    b = font.getbbox(s)
    d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), s, font=font, fill=fill)
    return b[3] - b[1]


def visible(s, n):
    return s[:max(0, min(len(s), n))]


# ---- precomputed pieces
def light_leak():
    """Warm radial blob (orange -> pink) with soft alpha falloff."""
    s = 1400
    y, x = np.mgrid[0:s, 0:s]
    r = np.sqrt((x - s / 2) ** 2 + (y - s / 2) ** 2) / (s / 2)
    a = np.clip(1 - r, 0, 1) ** 1.8
    img = np.zeros((s, s, 4), np.uint8)
    img[..., 0] = 255
    img[..., 1] = (150 + 60 * (1 - a)).astype(np.uint8)
    img[..., 2] = (70 + 90 * (1 - a)).astype(np.uint8)
    img[..., 3] = (a * 200).astype(np.uint8)
    return Image.fromarray(img, "RGBA")


LEAK = light_leak()

BATTERY = Image.new("RGBA", (90, 44), (0, 0, 0, 0))
_d = ImageDraw.Draw(BATTERY)
_d.rounded_rectangle((2, 4, 78, 40), 6, outline=CREAM + (255,), width=4)
_d.rectangle((80, 14, 87, 30), fill=CREAM + (255,))
for i in range(3):
    _d.rectangle((10 + i * 22, 11, 26 + i * 22, 33), fill=CREAM + (255,))

CORNER = 46  # viewfinder corner bracket length


def hud(cv, t):
    d = ImageDraw.Draw(cv)
    # viewfinder brackets
    m, L, w = 40, CORNER, 4
    col = CREAM + (170,)
    for (x, y, sx, sy) in ((m, 110, 1, 1), (W - m, 110, -1, 1),
                           (m, H - 330, 1, -1), (W - m, H - 330, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=col, width=w)
        d.line((x, y, x, y + sy * L), fill=col, width=w)
    # REC + timecode
    if int(t * 2) % 2 == 0:
        d.ellipse((72, 140, 100, 168), fill=RED + (255,))
    d.text((112, 136), "REC", font=F_HUD, fill=CREAM + (240,))
    fr = int(t * FPS) % FPS
    s = int(t)
    d.text((72, 182), f"00:{s // 60:02d}:{s % 60:02d}:{fr:02d}", font=F_SMALL,
           fill=CREAM + (210,))
    cv.alpha_composite(BATTERY, (W - 72 - 90, 134))
    d.text((W - 72 - 90 - 92, 140), "4K", font=F_SMALL, fill=CREAM + (210,))


DATE_LAYER = text_layer(lambda d: d.text((10, 10), DATE_STAMP, font=F_DATE, fill=ORANGE + (255,)),
                        size=(360, 90), glow=((255, 120, 20), 6), shadow=False)


def section_text(name, l1, l2, lt, rem, cv, t):
    n1 = int(lt * TYPE_CPS)
    n2 = int((lt - len(l1) / TYPE_CPS - 0.1) * TYPE_CPS * 1.4)
    fade = min(1, rem / 0.3)

    if name == "brand":
        # brand: big serif fades + tracks in instead of typing
        k = min(1, lt / 0.6)
        e = 1 - (1 - k) ** 3

        def draw(d):
            word = "MIRORA"
            gap = int(40 * (1 - e)) + 6
            widths = [F_BRAND.getbbox(c)[2] - F_BRAND.getbbox(c)[0] for c in word]
            total = sum(widths) + gap * (len(word) - 1)
            x = (W - total) / 2
            for c, wdt in zip(word, widths):
                b = F_BRAND.getbbox(c)
                d.text((x - b[0], 40 - b[1]), c, font=F_BRAND, fill=CREAM + (int(255 * e),))
                x += wdt + gap
            if lt > 0.5:
                ln = int(260 * min(1, (lt - 0.5) / 0.4))
                d.line((W / 2 - ln, 222, W / 2 + ln, 222), fill=GOLD + (255,), width=3)
            centered(d, 250, visible(spaced(l2), int((lt - 0.7) * 40)), F_SUB, GOLD + (255,))
        lay = text_layer(draw, glow=((255, 220, 170), 18))
    else:
        cursor = "|" if (n1 < len(l1) and int(t * 4) % 2 == 0) else ""

        def draw(d):
            h = centered(d, 40, visible(l1, n1) + cursor, title_font(l1), CREAM + (255,))
            h = max(h, 60)
            if n1 >= len(l1):
                ln = int(120 * min(1, (lt - len(l1) / TYPE_CPS) / 0.3))
                d.line((W / 2 - ln, 70 + h, W / 2 + ln, 70 + h), fill=GOLD + (230,), width=3)
            font2 = F_SMALL if name == "benefit" else F_SUB
            centered(d, 96 + h, visible(spaced(l2), n2), font2, GOLD + (255,))
        lay = text_layer(draw)

    if fade < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * fade)))
    cv.alpha_composite(lay, (0, 250))

    # counters
    if name == "water" and t >= WATER_COUNT[0] - 0.2:
        p = max(0, min(1, (t - WATER_COUNT[0]) / (WATER_COUNT[1] - WATER_COUNT[0])))
        p = 1 - (1 - p) ** 2
        txt = f"{3 * p:0.1f} L" + ("  ✓" if p >= 1 else "")
        c = text_layer(lambda d: centered(d, 10, txt, F_COUNT, CREAM + (255,)),
                       size=(W, 110))
        if fade < 1:
            c.putalpha(c.getchannel("A").point(lambda v: int(v * fade)))
        cv.alpha_composite(c, (0, 520))
    if name == "pack" and t >= DAY_COUNT[0] - 0.2:
        p = max(0, min(1, (t - DAY_COUNT[0]) / (DAY_COUNT[1] - DAY_COUNT[0])))
        day = max(1, math.ceil(p * 10))
        txt = f"HARI {day:02d} / 10"
        c = text_layer(lambda d: centered(d, 10, txt, F_COUNT, CREAM + (255,)), size=(W, 110))
        if fade < 1:
            c.putalpha(c.getchannel("A").point(lambda v: int(v * fade)))
        cv.alpha_composite(c, (0, 520))
    if name == "cta" and lt > 0.8:
        d = ImageDraw.Draw(cv)
        a = int(255 * min(1, (lt - 0.8) / 0.3))
        # outlined pill + bouncing arrow down toward the shop basket
        d.rounded_rectangle((W / 2 - 230, 560, W / 2 + 230, 640), 40, outline=GOLD + (a,), width=4)
        centered(d, 584, "TEKAN SEKARANG ↓", F_SUB, GOLD + (a,))
        by = 1110 + 26 * abs(math.sin((lt - 0.8) * 4.5))
        d.line((150, by - 90, 150, by), fill=CREAM + (a,), width=8)
        d.polygon([(118, by - 20), (182, by - 20), (150, by + 22)], fill=CREAM + (a,))


out = sys.stdout.buffer
for fi in range(NF):
    t = fi / FPS
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hud(cv, t)
    cv.alpha_composite(DATE_LAYER, (W - 72 - 300, 176))

    for name, s, e, l1, l2 in SECTIONS:
        e = min(e, DUR)
        if s <= t < e:
            section_text(name, l1, l2, t - s, e - t, cv, t)

    # light leak sweeps across on each cut
    for c in CUTS:
        if c - 0.25 <= t < c + 0.55:
            p = (t - (c - 0.25)) / 0.8
            a = math.sin(math.pi * p)
            lk = LEAK.copy()
            lk.putalpha(lk.getchannel("A").point(lambda v, a=a: int(v * a)))
            x = int(-1400 + p * (W + 1400))
            y = int(300 + 500 * math.sin(p * 2 + c))
            cv.paste(Image.alpha_composite(cv.crop((x, y, x + 1400, y + 1400)), lk), (x, y))

    # shutter blink at the very start (closed -> opens)
    if t < 0.25:
        a = int(255 * (1 - t / 0.25))
        cv = Image.alpha_composite(cv, Image.new("RGBA", (W, H), (10, 6, 4, a)))

    out.write(cv.tobytes())
