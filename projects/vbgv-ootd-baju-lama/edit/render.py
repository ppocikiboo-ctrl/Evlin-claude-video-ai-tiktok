"""Render the edited TikTok video: grade, zoom punches, flashes, overlays, subtitles.

Usage: python3 render.py <source.mp4> <mixed_audio.wav> <out.mp4> [--preview t1,t2,...]
"""
import math
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import timeline as T

W, H, FPS = 1080, 1920, 30
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

PURPLE = (124, 58, 237)
DEEP = (59, 18, 120)
YELLOW = (255, 225, 77)
WHITE = (255, 255, 255)

_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF


_emoji_cache = {}


def emoji_img(ch, size):
    k = (ch, size)
    if k not in _emoji_cache:
        f = ImageFont.truetype(FONT_EMOJI, 109)
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        s = size / im.height
        _emoji_cache[k] = im.resize((max(1, int(im.width * s)), size), Image.LANCZOS)
    return _emoji_cache[k]


def runs(text):
    text = text.replace("️", "")
    out, buf = [], ""
    for ch in text:
        if is_emoji(ch):
            if buf:
                out.append(("t", buf))
                buf = ""
            out.append(("e", ch))
        else:
            buf += ch
    if buf:
        out.append(("t", buf))
    return out


def rich_text(text, fpath, size, fill, stroke_fill=None, stroke=0, shadow=True):
    """Render a single line with emoji support -> RGBA image."""
    f = font(fpath, size)
    parts = runs(text)
    widths = []
    for kind, s in parts:
        if kind == "t":
            widths.append(int(f.getlength(s)))
        else:
            widths.append(int(size * 1.05) + 8)
    pad = stroke + 14
    asc, desc = f.getmetrics()
    w = sum(widths) + pad * 2
    h = asc + desc + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for (kind, s), wd in zip(parts, widths):
        if kind == "t":
            d.text((x, pad), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        else:
            e = emoji_img(s, int(size * 0.95))
            im.alpha_composite(e, (x + 4, pad + (asc - e.height) // 2 + int(size * 0.12)))
        x += wd
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        a = im.split()[3].filter(ImageFilter.GaussianBlur(8))
        sh.putalpha(a.point(lambda v: int(v * 0.55)))
        base = Image.new("RGBA", (w + 8, h + 10), (0, 0, 0, 0))
        base.alpha_composite(sh, (6, 9))
        base.alpha_composite(im, (0, 0))
        im = base
    return im


def styled_line(text, style):
    if style == "big":
        return rich_text(text, FONT_BLACK, 84, WHITE, DEEP, 10)
    if style == "huge":
        return rich_text(text, FONT_BLACK, 104, YELLOW, DEEP, 12)
    if style == "mid":
        return rich_text(text, FONT_BLACK, 74, WHITE, DEEP, 9)
    if style == "head":
        return pill(text, 66, PURPLE, WHITE)
    if style == "tag":
        return pill(text, 52, YELLOW, DEEP)
    if style == "hl":
        return pill(text, 50, YELLOW, DEEP)
    raise ValueError(style)


def pill(text, size, bg, fg, padx=34, pady=16, radius=None):
    t = rich_text(text, FONT_BLACK, size, fg, shadow=False)
    w, h = t.width + padx * 2 - 28, t.height + pady * 2 - 28
    im = Image.new("RGBA", (w + 12, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = radius if radius is not None else h // 2
    d.rounded_rectangle((6, 10, w + 6, h + 10), r, fill=(0, 0, 0, 90))
    d.rounded_rectangle((0, 0, w, h), r, fill=bg + (255,))
    im.alpha_composite(t, (padx - 14, pady - 14))
    return im


def stack(images, gap=-6):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for i in images:
        out.alpha_composite(i, ((w - i.width) // 2, y))
        y += i.height + gap
    return out


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def back_out(x, s=2.2):
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


# ---------- prebuilt assets ----------
def build_assets():
    ov = []
    for o in T.OVERLAYS:
        img = stack([styled_line(t, s) for t, s in o["lines"]], gap=-22)
        if img.width > W - 60:
            k = (W - 60) / img.width
            img = img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
        ov.append((o, img))
    cl_rows = [(t, pill(txt, 56, (255, 255, 255), DEEP, padx=40, pady=20, radius=30))
               for t, txt in T.CHECKLIST["items"]]
    tag = pill(T.CORNER_TAG["text"], 34, PURPLE, WHITE, padx=26, pady=12)
    arrow = make_arrow()
    return ov, cl_rows, tag, arrow


def make_arrow():
    im = Image.new("RGBA", (360, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Thick arrow pointing down-left.
    pts = [(300, 40), (330, 70), (150, 230), (205, 230), (205, 275), (60, 275), (60, 130),
           (105, 130), (105, 190)]
    d.polygon([(x + 5, y + 7) for x, y in pts], fill=(0, 0, 0, 110))
    d.polygon(pts, fill=YELLOW + (255,), outline=DEEP + (255,), width=8)
    label = pill("Beg kuning 🛒", 42, YELLOW, DEEP)
    out = Image.new("RGBA", (max(im.width, label.width + 60), im.height + label.height), (0, 0, 0, 0))
    out.alpha_composite(label, (60, 0))
    out.alpha_composite(im, (0, label.height - 30))
    return out


def sparkle_img(size, color):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    r1, r2 = size / 2, size / 9
    pts = []
    for k in range(8):
        a = k * math.pi / 4 - math.pi / 2
        r = r1 if k % 2 == 0 else r2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=color + (255,))
    glow = im.filter(ImageFilter.GaussianBlur(size / 8))
    glow.alpha_composite(im)
    return glow


random.seed(3)
SPARKS = []
for t0, t1 in T.SPARKLES:
    for _ in range(int((t1 - t0) * 2.2)):
        SPARKS.append(dict(t=random.uniform(t0, t1 - 0.6), x=random.choice(
            [random.randint(40, 260), random.randint(820, 1020)]), y=random.randint(560, 1250),
            s=random.randint(34, 70), c=random.choice([YELLOW, WHITE, (216, 180, 254)])))
_spark_imgs = {}


# ---------- frame composition ----------
def zoom_factor(t):
    z = 1.0
    for p in T.PUNCHES:
        dt = t - p
        if 0 <= dt < 0.45:
            z += 0.09 * (1 - ease_out(dt / 0.45))
    # slow push-in within each section
    starts = T.PUNCHES + [36.2]
    for a, b in zip(starts, starts[1:]):
        if a <= t < b:
            z *= 1.0 + 0.035 * (t - a) / (b - a)
    return z


def flash_alpha(t):
    a = 0.0
    for p in T.PUNCHES[1:]:
        dt = t - p
        if -0.04 <= dt < 0.22:
            a = max(a, 0.55 * (1 - clamp((dt + 0.04) / 0.26)))
    return a


def place(frame, img, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    im = img
    if abs(scale - 1) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(angle) > 0.05:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    frame.alpha_composite(im, (x, y)) if x >= 0 and y >= 0 and x + im.width <= W and y + im.height <= H \
        else paste_clipped(frame, im, x, y)


def paste_clipped(frame, im, x, y):
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(im.width, W - x), min(im.height, H - y)
    if ex <= sx or ey <= sy:
        return
    frame.alpha_composite(im.crop((sx, sy, ex, ey)), (x + sx, y + sy))


def draw_overlay(frame, t, o, img):
    if not (o["t0"] <= t < o["t1"]):
        return
    dt, rem = t - o["t0"], o["t1"] - t
    alpha = clamp(rem / 0.15)
    cx, cy, sc, ang = W / 2, o["y"], 1.0, 0.0
    anim = o["anim"]
    if anim == "pop":
        sc = back_out(dt / 0.3) if dt < 0.3 else 1.0
        sc = max(sc, 0.01)
    elif anim in ("slide_l", "slide_r"):
        k = 1 - ease_out(dt / 0.32)
        cx += (-1 if anim == "slide_l" else 1) * k * W
        ang = (4 if anim == "slide_l" else -4) * k
    elif anim == "shake":
        sc = back_out(dt / 0.25) if dt < 0.25 else 1.0 + 0.03 * math.sin(dt * 18)
        ang = 2.5 * math.sin(dt * 31) * math.exp(-dt * 1.2)
    if rem < 0.15:
        sc *= 0.9 + 0.1 * alpha
    place(frame, img, cx, cy, sc, alpha, ang)


def draw_subs(frame, t):
    for start, end, words in T.SUBS:
        if not (start <= t < end):
            continue
        dt = t - start
        imgs = []
        for i, (w, wt) in enumerate(words):
            nxt = words[i + 1][1] if i + 1 < len(words) else end
            speaking = wt <= t < nxt
            key = w.lower() in T.KEYWORDS
            if speaking:
                fill = YELLOW
            elif key:
                fill = (216, 180, 254)
            else:
                fill = WHITE
            imgs.append(subword(w, fill, speaking))
        gap = -18
        lines, cur, cw = [], [], 0
        for im in imgs:
            if cur and cw + im.width + gap > W - 120:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(im)
            cw += im.width + gap
        lines.append(cur)
        lh = 84
        y = 1395 - lh * (len(lines) - 1) / 2
        sc = back_out(dt / 0.18, 1.6) if dt < 0.18 else 1.0
        sc = 0.75 + 0.25 * sc
        for ln in lines:
            tw = sum(i.width for i in ln) + gap * (len(ln) - 1)
            x = W / 2 - tw * sc / 2
            for im in ln:
                place(frame, im, x + im.width * sc / 2, y, sc)
                x += (im.width + gap) * sc
            y += lh
        return


_sub_cache = {}


def subword(w, fill, speaking):
    k = (w, fill, speaking)
    if k not in _sub_cache:
        _sub_cache[k] = rich_text(w, FONT_BLACK, 66 if speaking else 60, fill, (15, 5, 30), 8)
    return _sub_cache[k]


def compose(base, t, assets):
    ov, cl_rows, tag, arrow = assets
    # zoom punch (center slightly above middle where the product sits)
    z = zoom_factor(t)
    if z > 1.001:
        cw, ch = W / z, H / z
        cx = W / 2
        cy = min(max(H * 0.46, ch / 2), H - ch / 2)
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        base = base.resize((W, H), Image.BILINEAR, box=box)
    frame = base.convert("RGBA")

    fa = flash_alpha(t)
    if fa > 0:
        frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 245, 255, 255)), fa)

    # sparkles
    for s in SPARKS:
        dt = t - s["t"]
        if 0 <= dt < 0.7:
            k = math.sin(math.pi * dt / 0.7)
            key = (s["s"], s["c"])
            if key not in _spark_imgs:
                _spark_imgs[key] = sparkle_img(s["s"], s["c"])
            place(frame, _spark_imgs[key], s["x"], s["y"], 0.3 + 0.7 * k, k, dt * 90)

    # corner tag
    ct = T.CORNER_TAG
    if ct["t0"] <= t < ct["t1"]:
        dt = t - ct["t0"]
        x = 40 + tag.width / 2 - (1 - ease_out(dt / 0.4)) * (tag.width + 60)
        place(frame, tag, x, 205)

    # checklist
    cl = T.CHECKLIST
    for i, (t0, img) in enumerate(cl_rows):
        if t0 <= t < cl["t1"]:
            dt, rem = t - t0, cl["t1"] - t
            sc = back_out(dt / 0.3) if dt < 0.3 else 1.0
            place(frame, img, W / 2, cl["y0"] + i * cl["gap"], max(sc, 0.01), clamp(rem / 0.15))

    for o, img in ov:
        draw_overlay(frame, t, o, img)

    for a0, a1 in T.ARROWS:
        if a0 <= t < a1:
            dt = t - a0
            b = abs(math.sin(dt * 7)) * 26
            sc = back_out(dt / 0.25) if dt < 0.25 else 1.0
            place(frame, arrow, 60 + arrow.width / 2 - b * 0.6, 1130 + b, max(sc, 0.01),
                  clamp((a1 - t) / 0.12))

    draw_subs(frame, t)
    return frame.convert("RGB")


def main():
    src, audio, out = sys.argv[1:4]
    preview = None
    if len(sys.argv) > 5 and sys.argv[4] == "--preview":
        preview = [float(x) for x in sys.argv[5].split(",")]
    assets = build_assets()
    vf = (f"fps={FPS},scale={W}:{H},eq=contrast=1.06:saturation=1.18:brightness=0.015:gamma=1.02,"
          "colorbalance=rs=0.02:bs=0.03:rh=0.02,vignette=angle=PI/5")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", vf, "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = None
    if preview is None:
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
             "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    n = 0
    fsz = W * H * 3
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        t = n / FPS
        if preview is not None:
            hit = [p for p in preview if abs(p - t) < 0.5 / FPS]
            if hit:
                img = compose(Image.frombuffer("RGB", (W, H), buf), t, assets)
                img.save(f"{out}_{hit[0]:05.2f}.jpg", quality=85)
        else:
            img = compose(Image.frombuffer("RGB", (W, H), buf), t, assets)
            enc.stdin.write(img.tobytes())
        n += 1
        if n % 150 == 0:
            print(f"{n} frames", file=sys.stderr, flush=True)
    dec.wait()
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    main()
