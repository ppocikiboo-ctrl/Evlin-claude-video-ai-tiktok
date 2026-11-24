"""Stream v4 "sticker meme" RGBA overlay frames (1080x1920 @30fps) to stdout.

Usage: python3 overlay_frames.py <duration_s> | ffmpeg -f rawvideo -pix_fmt rgba ...
Everything is kept above timeline.SAFE_BOTTOM so the product and the
original captions are never covered.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from timeline import (BRAND, CRAVE_IN, CTA, FPS, FRIEND_PRICE, H, HOOK, HOWTO,
                      OUTRO, POOF, SAFE_BOTTOM, STRUGGLE, W)

DUR = float(sys.argv[1])
NF = int(round(DUR * FPS))

BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

PINK = (236, 32, 122, 255)
INK = (40, 22, 14, 255)
WHITE = (255, 255, 255, 255)
YELLOW = (255, 212, 59, 255)
GOLD = (196, 146, 82, 255)
CREAM = (252, 244, 232, 255)


def F(p, s):
    return ImageFont.truetype(p, s)


_EMO = {}


def emoji(ch, size):
    key = (ch, size)
    if key not in _EMO:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        r = size / im.height
        _EMO[key] = im.resize((max(1, int(im.width * r)), size), Image.LANCZOS)
    return _EMO[key]


def sticker(parts, *, fill=WHITE, angle=0, pad=(36, 22), radius=30, outline=WHITE,
            outline_w=10, gap=10):
    """parts: rows of [(kind, value, font_or_size, color)] where kind is 't' or 'e'.
    Returns a rotated sticker with a thick die-cut border and drop shadow."""
    rows = []
    for row in parts:
        items, rw, rh = [], 0, 0
        for kind, val, f, col in row:
            if kind == "t":
                b = f.getbbox(val)
                w_, h_ = b[2] - b[0], b[3] - b[1]
                items.append(("t", val, f, col, w_, h_, b))
            else:
                im = emoji(val, f)
                w_, h_ = im.width, im.height
                items.append(("e", im, None, None, w_, h_, None))
            rw += w_ + (14 if rw else 0)
            rh = max(rh, h_)
        rows.append((items, rw, rh))
    cw = max(r[1] for r in rows) + pad[0] * 2
    ch = sum(r[2] for r in rows) + gap * (len(rows) - 1) + pad[1] * 2
    m = 40
    base = Image.new("RGBA", (cw + 2 * m, ch + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((m - outline_w, m - outline_w, m + cw + outline_w, m + ch + outline_w),
                        radius + outline_w, fill=outline)
    d.rounded_rectangle((m, m, m + cw, m + ch), radius, fill=fill)
    y = m + pad[1]
    for items, rw, rh in rows:
        x = m + (cw - rw) / 2
        for kind, val, f, col, w_, h_, b in items:
            yy = y + (rh - h_) / 2
            if kind == "t":
                d.text((x - b[0], yy - b[1]), val, font=f, fill=col)
            else:
                base.alpha_composite(val, (int(x), int(yy)))
            x += w_ + 14
        y += rh + gap
    rot = base.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", rot.size, (0, 0, 0, 0))
    a = rot.getchannel("A").filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.45))
    sh.putalpha(a)
    out = Image.new("RGBA", (rot.width + 16, rot.height + 16), (0, 0, 0, 0))
    out.alpha_composite(sh, (10, 14))
    out.alpha_composite(rot, (0, 0))
    return out


# ------------------------------------------------------------------ assets
S_HOOK = sticker([[("t", "DAH LAMA STUCK?", F(BLACK, 76), PINK), ("e", "😩", 76, None)],
                  [("t", "diet on-off, on-off...", F(BOLD, 42), INK)]], angle=-3)
S_STRUGGLE = sticker([[("t", "NAK DISIPLIN TAPI", F(BLACK, 66), INK)],
                      [("t", "CRAVING MENANG", F(BLACK, 80), PINK), ("e", "😭", 80, None)]],
                     angle=2.5)
FOODS = ["🍔", "🍟", "🍩", "🧋", "🍕", "🍰"]
FOOD_IMG = [emoji(f, 104) for f in FOODS]
FOOD_X = [130, 290, 450, 630, 790, 950]
FOOD_Y = 470

S_BRAND = sticker([[("t", "kenalkan:", F(BOLD, 50), GOLD)],
                   [("e", "✨", 96, None), ("t", "MIRORA", F(SERIF_B, 150), (92, 45, 20, 255)),
                    ("e", "✨", 96, None)],
                   [("t", "L-CARNITINE COMPLEX", F(BOLD, 44), GOLD)]],
                  fill=CREAM, outline=(230, 200, 150, 255), angle=0, pad=(50, 26))
S_ONE = sticker([[("e", "💊", 78, None), ("t", "1 BIJI SEHARI", F(BLACK, 70), INK)]], angle=-3)
S_TEN = sticker([[("e", "📅", 78, None), ("t", "10 KAPSUL = 10 HARI", F(BLACK, 62), PINK)]],
                angle=2.5)
S_DISC = sticker([[("t", "*hasil berbeza bagi setiap individu", F(BOLD, 28), WHITE)]],
                 fill=(30, 18, 12, 200), outline=(30, 18, 12, 0), outline_w=0, pad=(22, 10),
                 radius=20)
S_CTA = sticker([[("e", "🛒", 92, None), ("t", "KLIK BEG KUNING", F(BLACK, 84), INK)],
                 [("t", "sekarang!", F(BLACK, 50), INK)]], fill=YELLOW, angle=-2)
S_FRIEND = sticker([[("t", "HARGA KAWAN-KAWAN", F(BLACK, 56), WHITE), ("e", "🤝", 64, None)]],
                   fill=PINK, angle=4)
S_OUTRO = sticker([[("t", "SEMOGA BERJAYA!", F(BLACK, 80), PINK), ("e", "💪", 80, None)]],
                  angle=-2)
POINT = emoji("👇", 110)


# ------------------------------------------------------------------ helpers
def ease_out_back(x, s=2.2):
    x = min(1, max(0, x)) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def put(cv, img, cx, top, scale=1.0, alpha=1.0, angle=0.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    im = img
    if abs(scale - 1) > 0.004:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                       Image.BILINEAR)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(top + (img.height * 1.0 - im.height) / 2)
    # hard guard: never draw below the safe line
    if y + im.height > SAFE_BOTTOM:
        im = im.crop((0, 0, im.width, max(1, SAFE_BOTTOM - y)))
    cv.alpha_composite(im, (x, max(0, y)) if y >= 0 else (x, 0))


def pop_in(lt, dur=0.3):
    return 0.4 + 0.6 * ease_out_back(lt / dur)


def out_fade(rem, d=0.15):
    return min(1, max(0, rem / d))


def puff(cv, cx, cy, k):
    """Little white smoke puff for the 'poof'."""
    d = ImageDraw.Draw(cv)
    for i in range(7):
        a = i * 2 * math.pi / 7
        r = 20 + 70 * k
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        s = 34 * (1 - k) + 8
        d.ellipse((x - s, y - s, x + s, y + s), fill=(255, 255, 255, int(230 * (1 - k))))


def glint(img, p):
    """Diagonal shine sweeping across a sticker (p 0..1)."""
    w, h = img.size
    band = Image.new("L", (w, h), 0)
    bd = ImageDraw.Draw(band)
    x = -w * 0.3 + p * w * 1.6
    bd.polygon([(x, 0), (x + 70, 0), (x - 40, h), (x - 110, h)], fill=170)
    band = band.filter(ImageFilter.GaussianBlur(10))
    shine = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    shine.putalpha(Image.composite(band, Image.new("L", (w, h), 0), img.getchannel("A")))
    out = img.copy()
    out.alpha_composite(shine)
    return out


# ------------------------------------------------------------------ frames
out = sys.stdout.buffer
for fi in range(NF):
    t = fi / FPS
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # HOOK: slam + shake, then a gentle wobble
    s, e = HOOK
    if s <= t < e:
        lt, rem = t - s, e - t
        k = min(1, lt / 0.2)
        sc = 1.7 - 0.7 * (1 - (1 - k) ** 3)
        dx = 12 * (1 - (lt - 0.2) / 0.35) * math.sin(lt * 95) if 0.2 < lt < 0.55 else 0
        ang = 1.5 * math.sin(lt * 3) if lt > 0.6 else 0
        put(cv, S_HOOK, W / 2 + dx, 150, sc, min(1, lt / 0.08) * out_fade(rem), ang)

    # STRUGGLE + cravings dropping in, then POOF
    s, e = STRUGGLE
    if s <= t < e + 0.45:
        lt, rem = t - s, e - t
        if t < e:
            put(cv, S_STRUGGLE, W / 2, 130, pop_in(lt), min(1, lt / 0.1) * out_fade(rem),
                1.2 * math.sin(lt * 3.5))
        c0, c1 = CRAVE_IN
        step = (c1 - c0) / len(FOODS)
        for i, im in enumerate(FOOD_IMG):
            ts = c0 + i * step
            if t < ts:
                continue
            if t < POOF:
                fall = min(1, (t - ts) / 0.28)
                y = FOOD_Y - 160 * (1 - fall) ** 2
                squash = 1 + (0.18 * math.sin(math.pi * min(1, (t - ts - 0.28) / 0.18))
                              if t - ts > 0.28 else 0)
                bob = 6 * math.sin((t - ts) * 7 + i)
                put(cv, im, FOOD_X[i], y - im.height / 2 + bob, squash, min(1, fall * 2),
                    8 * math.sin((t - ts) * 5 + i))
            else:
                k = min(1, (t - POOF) / 0.4)
                put(cv, im, FOOD_X[i], FOOD_Y - im.height / 2, 1 - k, 1 - k)
                puff(cv, FOOD_X[i], FOOD_Y, k)

    # BRAND: pop + glint sweep
    s, e = BRAND
    if s <= t < e:
        lt, rem = t - s, e - t
        img = glint(S_BRAND, (lt - 0.35) / 0.6) if 0.35 < lt < 0.95 else S_BRAND
        put(cv, img, W / 2, 150 + 6 * math.sin(lt * 4), pop_in(lt), min(1, lt / 0.1) * out_fade(rem))

    # HOWTO: two stickers slide in from opposite sides + disclaimer
    s, e = HOWTO
    if s <= t < e:
        lt, rem = t - s, e - t
        a = out_fade(rem)
        k1 = ease_out_back(lt / 0.35, 1.4)
        put(cv, S_ONE, -400 + (W / 2 + 400) * k1, 120, 1, a)
        if lt > 0.55:
            k2 = ease_out_back((lt - 0.55) / 0.35, 1.4)
            put(cv, S_TEN, W + 500 - (W / 2 + 500) * k2, 290, 1, a)
        if lt > 0.9:
            put(cv, S_DISC, W / 2, 470, 1, min(1, (lt - 0.9) / 0.2) * a)

    # CTA: yellow sticker heartbeat + friend-price sticker + pointer
    s, e = CTA
    if s <= t < e:
        lt, rem = t - s, e - t
        a = out_fade(rem)
        beat = 1 + 0.05 * abs(math.sin(math.pi * lt * 1.9)) if lt > 0.35 else 1
        put(cv, S_CTA, W / 2, 110, pop_in(lt) * beat, min(1, lt / 0.1) * a, 2 * math.sin(lt * 4))
        if t >= FRIEND_PRICE:
            l2 = t - FRIEND_PRICE
            put(cv, S_FRIEND, W / 2 + 40, 360, pop_in(l2, 0.25), min(1, l2 / 0.08) * a,
                3 * math.sin(l2 * 6))
        # pointer at the far left edge, above the captions, toward the shop basket
        if lt > 0.4:
            put(cv, POINT, 92, 470 + 22 * abs(math.sin((lt - 0.4) * 5)), 0.8,
                min(1, (lt - 0.4) / 0.2) * a)

    # OUTRO
    s, e = OUTRO
    if s <= t < min(e, DUR):
        lt = t - s
        put(cv, S_OUTRO, W / 2, 150, pop_in(lt, 0.25), min(1, lt / 0.08))

    # progress bar
    pw = int(W * min(1, t / DUR))
    if pw:
        cv.paste((236, 32, 122, 255), (0, 0, pw, 9))

    out.write(cv.tobytes())
