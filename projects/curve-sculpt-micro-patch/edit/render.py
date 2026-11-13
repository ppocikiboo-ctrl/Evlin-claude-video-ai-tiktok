"""Re-edit a TikTok product video: hide old burned-in subtitles, add new
karaoke subtitles, hooks, effects, CTA and an end card.

Usage: python3 render.py INPUT.mp4 OUTPUT.mp4
"""
import math
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
SRC_DUR = 19.0
END_DUR = 1.6
TOTAL = SRC_DUR + END_DUR
NF = int(round(TOTAL * FPS))
NSRC = int(round(SRC_DUR * FPS))
SR = 44100

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BLACK_IT = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

YELLOW = (255, 221, 0)
PINK = (255, 64, 129)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Band (in 1080x1920 coords) that holds the old burned-in subtitles.
BAND_Y0, BAND_Y1 = 1110, 1590

_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x2705, 0x2728)


def emoji_img(ch, size):
    f = font(FONT_EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    s = size / im.height
    return im.resize((max(1, int(im.width * s)), size), Image.LANCZOS)


def text_img(text, size, fill=WHITE, stroke=0, stroke_fill=BLACK, path=FONT_BLACK):
    """Render a run of text (emoji allowed) to a tight RGBA image."""
    f = font(path, size)
    asc, desc = f.getmetrics()
    h = asc + desc + stroke * 2
    parts, buf = [], ""
    for ch in text:
        if ch == "️":
            continue
        if is_emoji(ch):
            if buf:
                parts.append(("t", buf))
                buf = ""
            parts.append(("e", ch))
        else:
            buf += ch
    if buf:
        parts.append(("t", buf))
    pieces = []
    for kind, s in parts:
        if kind == "t":
            w = int(f.getlength(s)) + stroke * 2 + 2
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((stroke, stroke), s, font=f, fill=fill,
                                    stroke_width=stroke, stroke_fill=stroke_fill)
            pieces.append((im, 0))
        else:
            e = emoji_img(s, int(size * 1.0))
            pieces.append((e, (h - e.height) // 2))
    tw = sum(p.width for p, _ in pieces) + 6 * (len(pieces) - 1)
    out = Image.new("RGBA", (max(tw, 1), h), (0, 0, 0, 0))
    x = 0
    for p, dy in pieces:
        out.alpha_composite(p, (x, max(0, dy)))
        x += p.width + 6
    return out


def pill(im, bg, pad_x=34, pad_y=16, radius=None, shadow=True, border=None):
    w, h = im.width + pad_x * 2, im.height + pad_y * 2
    r = radius if radius is not None else h // 2
    out = Image.new("RGBA", (w + 24, h + 28), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((12, 20, 12 + w, 20 + h), r, fill=(0, 0, 0, 120))
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((12, 10, 12 + w, 10 + h), r, fill=bg,
                        outline=border, width=6 if border else 0)
    out.alpha_composite(im, (12 + pad_x, 10 + pad_y))
    return out


def stack(images, gap=8, align="center"):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for i in images:
        x = (w - i.width) // 2 if align == "center" else 0
        out.alpha_composite(i, (x, y))
        y += i.height + gap
    return out


def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    x = min(max(x, 0.0), 1.0)
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def place(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1.0) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    canvas.alpha_composite(im, (x, y)) if x >= 0 and y >= 0 and x + im.width <= W and y + im.height <= H \
        else _safe_paste(canvas, im, x, y)


def _safe_paste(canvas, im, x, y):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(im, (x, y), im)
    canvas.alpha_composite(layer)


def pop(t, t0, t1, fade=0.12):
    """Scale/alpha for an element that pops in at t0 and fades at t1."""
    if t < t0 or t > t1:
        return 0.0, 0.0
    s = ease_out_back((t - t0) / 0.22)
    a = min(1.0, (t - t0) / 0.06, (t1 - t) / fade)
    return max(s, 0.01), max(a, 0.0)


# ---------------------------------------------------------------- subtitles
# Fixed wording from the original auto-captions (e.g. "micronidel" ->
# "microneedle", "belalang" -> "belah", "kuning sekarang" -> "beg kuning").
CHUNKS = [
    (0.70, 1.20, "EH, KORANG"),
    (1.20, 1.72, "PERNAH NAMPAK PATCH"),
    (1.72, 2.45, "MACAM NI? 👀"),
    (2.45, 3.05, "INI ADALAH"),
    (3.05, 4.10, "CURVE SCULPT MICRO-PATCH"),
    (4.12, 4.60, "PATCH KHAS"),
    (4.60, 5.20, "UNTUK PENJAGAAN"),
    (5.20, 5.95, "BAHAGIAN PUNGGUNG 🍑"),
    (5.95, 6.65, "DIA MENGGUNAKAN"),
    (6.65, 7.70, "TEKNOLOGI MICRONEEDLE YANG"),
    (7.70, 8.40, "BOLEH LARUT 💧"),
    (10.95, 11.55, "DALAM 1"),
    (11.55, 12.20, "KOTAK NI"),
    (12.20, 13.15, "ADA 6 PATCHES ✨"),
    (13.15, 13.90, "BERSAMAAN DENGAN"),
    (13.90, 14.72, "3 PASANG"),
    (14.72, 15.20, "UNTUK KEDUA-DUA"),
    (15.20, 15.72, "BELAH KIRI"),
    (15.72, 16.45, "DAN KANAN."),
    (16.70, 17.30, "SIAPA YANG"),
    (17.30, 18.00, "CURIOUS BOLEH 🤭"),
    (18.00, 18.45, "TENGOK DETAIL DEKAT"),
    (18.45, 19.00, "BEG KUNING SEKARANG 🛒"),
]
CAP_SIZE = 84
CAP_Y = 1350


def build_caption(words, active):
    """Words laid out (wrapped) with the active word on a yellow box."""
    imgs = []
    for i, wd in enumerate(words):
        if any(is_emoji(c) for c in wd):
            imgs.append(("e", text_img(wd, int(CAP_SIZE * 1.05))))
        elif i == active:
            t = text_img(wd, CAP_SIZE, fill=BLACK)
            imgs.append(("a", pill(t, YELLOW, pad_x=16, pad_y=4, radius=18, shadow=False)))
        else:
            imgs.append(("w", text_img(wd, CAP_SIZE, fill=WHITE, stroke=9)))
    lines, cur, cw = [], [], 0
    for kind, im in imgs:
        add = im.width + (14 if cur else 0)
        if cur and cw + add > 960:
            lines.append(cur)
            cur, cw = [], 0
            add = im.width
        cur.append((kind, im))
        cw += add
    lines.append(cur)
    line_imgs = []
    for ln in lines:
        lh = max(im.height for _, im in ln)
        lw = sum(im.width for _, im in ln) + 14 * (len(ln) - 1)
        L = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        x = 0
        for kind, im in ln:
            L.alpha_composite(im, (x, (lh - im.height) // 2))
            x += im.width + 14
        line_imgs.append(L)
    return stack(line_imgs, gap=0)


def word_weights(words):
    return [max(2, len(w)) if not any(is_emoji(c) for c in w) else 0 for w in words]


CAP_CACHE = {}


def caption_frame(t):
    exact = [c for c in CHUNKS if c[0] <= t < c[1]]
    linger = [c for c in CHUNKS if c[1] <= t < c[1] + 0.25]
    for t0, t1, text in (exact or linger)[:1]:
        if True:
            words = text.split()
            ws = word_weights(words)
            tot = sum(ws)
            acc, active = 0.0, None
            rel = (min(t, t1) - t0) / (t1 - t0) * tot
            for i, wgt in enumerate(ws):
                if wgt and acc <= rel < acc + wgt:
                    active = i
                acc += wgt
            if active is None:
                active = max(i for i, wgt in enumerate(ws) if wgt)
            key = (text, active)
            if key not in CAP_CACHE:
                CAP_CACHE[key] = build_caption(words, active)
            fade = 1.0 if t < t1 else max(0.0, 1 - (t - t1) / 0.25)
            s = ease_out_back((t - t0) / 0.18) * 0.25 + 0.75
            return CAP_CACHE[key], s, fade
    return None


# ---------------------------------------------------------------- overlays
def build_overlays():
    o = {}
    o["stop"] = pill(text_img("JANGAN SCROLL DULU! ✋", 58, fill=WHITE), (230, 30, 60))
    l1 = text_img("PUNGGUNG NAMPAK", 92, fill=WHITE, stroke=10, path=FONT_BLACK_IT)
    l2a = text_img("LEPER? 😩", 120, fill=YELLOW, stroke=11, path=FONT_BLACK_IT)
    o["hook"] = stack([l1, l2a], gap=0)
    o["try"] = pill(text_img("CUBA PATCH NI DULU 🍑", 56, fill=BLACK), WHITE, border=PINK)
    o["name"] = pill(text_img("✨ CURVE SCULPT MICRO-PATCH ✨", 46, fill=WHITE), PINK)

    # Benefit card shown during the silent part of the clip.
    title = text_img("KENAPA RAMAI NAK TRY? 😍", 58, fill=WHITE, stroke=8)
    rows = [text_img(s, 54, fill=BLACK) for s in
            ("✅ ENHANCE", "✅ LIFT", "✅ VOLUME", "💧 MICRONEEDLE LARUT")]
    o["benefit_title"] = title
    o["benefit_rows"] = [pill(r, (255, 255, 255, 240), pad_x=28, pad_y=12, radius=26) for r in rows]

    st = text_img("6 PATCH = 3 PASANG 💯", 74, fill=WHITE, stroke=0)
    o["six"] = pill(st, PINK, pad_x=40, pad_y=20, radius=30, border=WHITE)

    o["link"] = pill(text_img("LINK PRODUK DI BAWAH 👇", 52, fill=BLACK), YELLOW)
    o["cta"] = pill(text_img("🛒 TEKAN BEG KUNING SEKARANG!", 54, fill=BLACK), YELLOW,
                    pad_x=40, pad_y=26, border=WHITE)
    o["finger"] = emoji_img("👇", 130)

    # End card
    o["end_title"] = text_img("CURVE SCULPT", 110, fill=WHITE, stroke=10, path=FONT_BLACK_IT)
    o["end_title2"] = text_img("MICRO-PATCH", 110, fill=PINK, stroke=10, path=FONT_BLACK_IT)
    o["end_sub"] = text_img("ENHANCE • LIFT • VOLUME", 52, fill=WHITE, stroke=6)
    o["end_cta"] = pill(text_img("🛒 BELI KAT BEG KUNING", 64, fill=BLACK), YELLOW,
                        pad_x=46, pad_y=30, border=WHITE)
    o["end_note"] = text_img("Stok & harga terkini dalam link 👇", 44, fill=WHITE, stroke=6)
    return o


def star(draw, cx, cy, r, alpha):
    pts = []
    for k in range(8):
        ang = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.22
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=(255, 255, 255, int(255 * alpha)))


random.seed(7)
SPARKLES = [(random.uniform(120, 960), random.uniform(250, 1050), random.uniform(16, 34),
             random.uniform(0, 1)) for _ in range(14)]


# ---------------------------------------------------------------- base frame FX
PUNCHES = [(0.0, 0.10), (0.70, 0.07), (2.45, 0.12), (5.95, 0.07), (10.95, 0.08),
           (12.20, 0.12), (16.70, 0.10)]
FLASHES = [2.45, 12.20, 16.70]
GLITCH = [0.0, 2.45, 16.70]


def zoom_at(t):
    z = 1.0 + 0.05 * (t / SRC_DUR)
    for p, a in PUNCHES:
        dt = t - p
        if 0 <= dt < 0.6:
            z += a * math.exp(-dt * 7.0)
    return z


def shake_at(t):
    for t0, dur, amp in ((0.0, 0.5, 14), (2.45, 0.25, 8), (16.70, 0.3, 10)):
        dt = t - t0
        if 0 <= dt < dur:
            k = amp * (1 - dt / dur)
            return (k * math.sin(t * 91.0), k * math.cos(t * 77.0))
    return (0.0, 0.0)


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = np.clip(1.0 - 0.28 * np.clip(_r - 0.55, 0, None) ** 1.6, 0.6, 1.0)[..., None]

band_mask = np.zeros((H, W), np.float32)
band_mask[BAND_Y0:BAND_Y1] = 1.0
BAND_MASK = Image.fromarray((band_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))


def hide_old_subs(frame):
    """Blur + soften the strip that has the old burned-in captions."""
    y0, y1 = BAND_Y0 - 80, BAND_Y1 + 80
    crop = frame.crop((0, y0, W, y1))
    small = crop.resize((W // 16, (y1 - y0) // 16), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    blurred = small.resize(crop.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    arr = np.asarray(blurred).astype(np.float32)
    grey = arr.mean(axis=2, keepdims=True)
    arr = (grey + (arr - grey) * 0.25) * 0.72
    blurred = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    full = frame.copy()
    full.paste(blurred, (0, y0))
    return Image.composite(full, frame, BAND_MASK)


def transform(frame, t):
    z = zoom_at(t)
    sx, sy = shake_at(t)
    cw, ch = W / z, H / z
    x0 = (W - cw) / 2 - sx / z
    y0 = (H - ch) / 2 - sy / z
    x0 = min(max(x0, 0), W - cw)
    y0 = min(max(y0, 0), H - ch)
    return frame.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def grade(arr, t):
    a = arr.astype(np.float32)
    a = (a - 128) * 1.07 + 128 + 4
    a[..., 0] *= 1.03
    a *= VIGNETTE
    for g in GLITCH:
        dt = t - g
        if 0 <= dt < 0.14:
            off = int(16 * (1 - dt / 0.14)) + 2
            a[..., 0] = np.roll(a[..., 0], off, axis=1)
            a[..., 2] = np.roll(a[..., 2], -off, axis=1)
    for f in FLASHES:
        dt = t - f
        if 0 <= dt < 0.18:
            k = 0.65 * (1 - dt / 0.18)
            a = a * (1 - k) + 255 * k
    return a.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- per-frame overlays
def draw_overlays(canvas, t, O):
    # Hook (0 - 2.45)
    s, a = pop(t, 0.0, 2.45)
    if a:
        wob = 4 * math.sin(t * 9) if t < 1.2 else 0
        place(canvas, O["stop"], W / 2, 190, s, a, rot=wob)
    s, a = pop(t, 0.30, 2.45)
    if a:
        place(canvas, O["hook"], W / 2, 450, s * (1 + 0.03 * math.sin(t * 6)), a, rot=-3)
    s, a = pop(t, 1.05, 2.45)
    if a:
        place(canvas, O["try"], W / 2, 720, s, a, rot=2)

    # Product name tag
    if 2.45 <= t < 5.95:
        p = ease_out((t - 2.45) / 0.35)
        a = min(1.0, (5.95 - t) / 0.15)
        place(canvas, O["name"], -400 + p * (W / 2 + 400), 260, 1.0, a)

    # Sparkles on product moments
    for t0, t1 in ((2.45, 4.1), (12.2, 13.2), (19.0, TOTAL)):
        if t0 <= t < t1:
            d = ImageDraw.Draw(canvas)
            for (x, y, r, ph) in SPARKLES:
                tw = 0.5 + 0.5 * math.sin((t * 5.5) + ph * 6.28)
                star(d, x, y, r * (0.4 + 0.8 * tw), 0.85 * tw)

    # Benefit card (8.4 - 10.95)
    if 8.40 <= t < 10.95:
        s, a = pop(t, 8.40, 10.95)
        place(canvas, O["benefit_title"], W / 2, 300, s, a)
        for i, row in enumerate(O["benefit_rows"]):
            t0 = 8.75 + i * 0.42
            if t >= t0:
                p = ease_out_back((t - t0) / 0.3)
                a2 = min(1.0, (10.95 - t) / 0.15)
                x = -300 + p * (300 + 330)
                place(canvas, row, x, 420 + i * 118, 1.0, a2)

    # 6 patch sticker
    s, a = pop(t, 12.20, 14.72)
    if a:
        place(canvas, O["six"], W / 2, 330, s * (1 + 0.04 * math.sin(t * 8)), a, rot=-5)

    # CTA (16.45 - end of clip)
    s, a = pop(t, 16.45, SRC_DUR + 0.01)
    if a:
        place(canvas, O["link"], W / 2, 280, s, a)
    s, a = pop(t, 16.70, SRC_DUR + 0.01)
    if a:
        pulse = 1 + 0.05 * math.sin((t - 16.7) * 9)
        place(canvas, O["cta"], W / 2, 1010, s * pulse, a)
        bob = 22 * abs(math.sin((t - 16.7) * 6))
        place(canvas, O["finger"], 200, 1690 + bob, 1.0, a)


def end_card(last_frame, t, O):
    dt = t - SRC_DUR
    bg = last_frame.filter(ImageFilter.GaussianBlur(min(22, 4 + dt * 60)))
    arr = np.asarray(bg).astype(np.float32)
    arr = arr * (1 - min(0.55, dt * 2.5)) + np.array(PINK) * min(0.12, dt * 0.6)
    canvas = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
    s1 = ease_out_back(dt / 0.25)
    place(canvas, O["end_title"], W / 2, 620, s1, 1.0, rot=-3)
    place(canvas, O["end_title2"], W / 2, 750, ease_out_back((dt - 0.08) / 0.25), 1.0, rot=-3)
    if dt > 0.2:
        place(canvas, O["end_sub"], W / 2, 880, 1.0, min(1, (dt - 0.2) / 0.15))
    if dt > 0.3:
        pulse = 1 + 0.06 * math.sin((dt - 0.3) * 10)
        place(canvas, O["end_cta"], W / 2, 1080, ease_out_back((dt - 0.3) / 0.25) * pulse, 1.0)
    if dt > 0.45:
        place(canvas, O["end_note"], W / 2, 1230, 1.0, min(1, (dt - 0.45) / 0.15))
        bob = 24 * abs(math.sin(dt * 6))
        place(canvas, O["finger"], 200, 1680 + bob, 1.0, 1.0)
    d = ImageDraw.Draw(canvas)
    for (x, y, r, ph) in SPARKLES:
        tw = 0.5 + 0.5 * math.sin((t * 5.5) + ph * 6.28)
        star(d, x, y + 250, r * (0.4 + 0.8 * tw), 0.8 * tw)
    return canvas


# ---------------------------------------------------------------- audio
def build_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-f", "s16le", "-ac", "2",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    voice = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
    n = int(TOTAL * SR)
    mix = np.zeros((n, 2), np.float32)
    mix[:len(voice)] += voice[:n]
    rng = np.random.default_rng(1)

    def add(sig, t, gain):
        i = int(t * SR)
        j = min(n, i + len(sig))
        mix[i:j] += (sig[:j - i] * gain)[:, None]

    def whoosh(d=0.35):
        m = int(d * SR)
        x = rng.standard_normal(m).astype(np.float32)
        x = np.convolve(x, np.ones(25) / 25, mode="same")
        env = np.sin(np.linspace(0, np.pi, m)) ** 2
        return x * env * 3.0

    def popsnd(f0=900, d=0.09):
        m = int(d * SR)
        tt = np.arange(m) / SR
        f = f0 * np.exp(-tt * 18)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40)

    def ding(f0=1320, d=0.9):
        m = int(d * SR)
        tt = np.arange(m) / SR
        s = sum(np.sin(2 * np.pi * f0 * k * tt) / k for k in (1, 2, 3))
        return s * np.exp(-tt * 5) * 0.6

    for t in (0.0, 1.05):
        add(popsnd(), t, 0.35)
    for t in (0.30, 2.40, 5.90, 10.90, 12.15, 16.65, 18.95):
        add(whoosh(), t, 0.22)
    for i in range(4):
        add(popsnd(1100 + 120 * i), 8.75 + i * 0.42, 0.28)
    add(popsnd(1300), 12.2, 0.3)
    add(ding(), 16.70, 0.20)
    add(ding(1568), 19.30, 0.25)
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


def main():
    audio_path = OUT + ".audio.wav"
    build_audio(audio_path)
    O = build_overlays()
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", SRC, "-vf",
         "scale=1080:1920:flags=lanczos,eq=saturation=1.15", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", audio_path, "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
         "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    fsz = W * H * 3
    last = None
    for i in range(NF):
        t = i / FPS
        if i < NSRC:
            buf = dec.stdout.read(fsz)
            if len(buf) == fsz:
                last = Image.frombuffer("RGB", (W, H), buf)
            frame = hide_old_subs(last)
            frame = transform(frame, t)
            frame = Image.fromarray(grade(np.asarray(frame), t)).convert("RGBA")
            cap = caption_frame(t)
            if cap:
                im, s, a = cap
                place(frame, im, W / 2, CAP_Y, s, a)
            draw_overlays(frame, t, O)
            if i == NSRC - 1:
                last_clean = transform(hide_old_subs(last), t)
        else:
            frame = end_card(last_clean, t, O)
        enc.stdin.write(frame.convert("RGB").tobytes())
        if i % 60 == 0:
            print(f"frame {i}/{NF}", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()


if __name__ == "__main__":
    main()
