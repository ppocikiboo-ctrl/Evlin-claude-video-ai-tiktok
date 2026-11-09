"""Graphics assets for the Durimex Coffee TikTok edit (all drawn with PIL)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"

YELLOW = (255, 214, 10)
RED = (232, 38, 52)
GREEN_D = (20, 83, 45)
LIME = (163, 230, 53)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SS = 2  # supersample factor for smooth edges


def font(path, size):
    return ImageFont.truetype(path, size)


def shadow(img, radius=14, offset=(0, 10), alpha=150):
    """Return img with a soft drop shadow underneath (canvas grows)."""
    pad = radius * 3
    W, H = img.width + pad * 2, img.height + pad * 2
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 255))
    sh.putalpha(a)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(sh, (pad + offset[0], pad + offset[1]))
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    out = Image.alpha_composite(out, layer)
    out.alpha_composite(img, (pad, pad))
    return out


def stroke_text(lines, size, fill=WHITE, stroke=BLACK, sw=None, fnt=FONT_BLACK,
                spacing=0.05, align="center", max_w=None):
    """Multi-line text with thick outline. lines: list of list[(text,color)] or str."""
    sw = sw if sw is not None else max(4, size // 9)
    f = font(fnt, size)
    norm = []
    for ln in lines:
        if isinstance(ln, str):
            ln = [(ln, fill)]
        norm.append(ln)
    asc, desc = f.getmetrics()
    lh = asc + desc
    widths = [sum(f.getlength(t) for t, _ in ln) for ln in norm]
    W = int(max(widths) + sw * 2 + 8)
    H = int(lh * len(norm) + lh * spacing * (len(norm) - 1) + sw * 2 + 8)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = sw + 4
    for ln, w in zip(norm, widths):
        x = (W - w) / 2 if align == "center" else sw + 4
        for t, c in ln:
            d.text((x, y), t, font=f, fill=c, stroke_width=sw, stroke_fill=stroke)
            x += f.getlength(t)
        y += lh * (1 + spacing)
    img = img.crop(img.getbbox())
    if max_w and img.width > max_w:
        r = max_w / img.width
        img = img.resize((max_w, int(img.height * r)), Image.LANCZOS)
    return img


def pill(text, size, bg=RED, fg=WHITE, padx=None, pady=None, fnt=FONT_BLACK, rot=0):
    f = font(fnt, size)
    padx = padx or int(size * 0.6)
    pady = pady or int(size * 0.32)
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    W, H = tw + padx * 2, th + pady * 2
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W * SS - 1, H * SS - 1], radius=H * SS // 2, fill=bg)
    f2 = font(fnt, size * SS)
    d.text((padx * SS - bbox[0] * SS, pady * SS - bbox[1] * SS), text, font=f2, fill=fg)
    img = img.resize((W, H), Image.LANCZOS)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    return shadow(img, radius=8, offset=(0, 6), alpha=120)


# ---------------------------------------------------------------- illustrations
def _noise(size, scale=1.0, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (size, size)).astype(np.float32)
    im = Image.fromarray(((n * 30 * scale) + 128).clip(0, 255).astype(np.uint8))
    return im.filter(ImageFilter.GaussianBlur(1.2))


def radial(size, inner, outer, center=None, power=1.0):
    cx, cy = center or (size / 2, size / 2)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (size / 2)
    t = np.clip(r, 0, 1) ** power
    a = np.array(inner, np.float32)[None, None, :]
    b = np.array(outer, np.float32)[None, None, :]
    arr = a + (b - a) * t[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB")


def blob_mask(size, cx, cy, rx, ry, rot=0, wobble=0.08, seed=1):
    """Irregular organic ellipse mask (for rhizomes)."""
    rng = random.Random(seed)
    pts = []
    k = [rng.uniform(-wobble, wobble) for _ in range(5)]
    ph = [rng.uniform(0, 6.28) for _ in range(5)]
    for i in range(120):
        a = i / 120 * 2 * math.pi
        m = 1 + sum(k[j] * math.sin((j + 2) * a + ph[j]) for j in range(5))
        x, y = rx * m * math.cos(a), ry * m * math.sin(a)
        c, s = math.cos(rot), math.sin(rot)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def rhizome(size, skin_dark, skin_light, flesh_in, flesh_out, seed=3, ring_col=None):
    """Draw a turmeric-style rhizome cluster + a cut slice showing the flesh."""
    S = size
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rng = random.Random(seed)
    # knobby fingers
    parts = [
        (0.42, 0.40, 0.30, 0.13, -0.35),
        (0.30, 0.55, 0.20, 0.10, 0.5),
        (0.58, 0.30, 0.18, 0.09, -1.0),
        (0.60, 0.52, 0.22, 0.10, 0.15),
        (0.22, 0.38, 0.14, 0.08, -0.9),
    ]
    for i, (cx, cy, rx, ry, rot) in enumerate(parts):
        m = blob_mask(S, cx * S, cy * S, rx * S, ry * S, rot, 0.07, seed + i)
        skin = radial(S, skin_light, skin_dark, (cx * S - rx * S * 0.3, cy * S - ry * S * 0.6), 0.9)
        n = _noise(S, 1.4, seed + i)
        skin = Image.blend(skin, Image.merge("RGB", (n, n, n)), 0.12)
        layer = skin.convert("RGBA")
        layer.putalpha(m)
        # ring lines across finger
        d = ImageDraw.Draw(layer)
        for j in range(1, 6):
            t = -1 + j / 3
            px = cx * S + math.cos(rot) * rx * S * t
            py = cy * S + math.sin(rot) * rx * S * t
            nx, ny = -math.sin(rot) * ry * S * 0.95, math.cos(rot) * ry * S * 0.95
            d.arc([px - abs(nx) - 6, py - abs(ny) - 6, px + abs(nx) + 6, py + abs(ny) + 6],
                  0, 360, fill=tuple(int(c * 0.6) for c in skin_dark) + (90,), width=max(2, S // 160))
        layer.putalpha(ImageChops.multiply(layer.split()[3], m))
        img = Image.alpha_composite(img, layer)
    # slice (cross-section) bottom right
    r = int(S * 0.20)
    cx, cy = int(S * 0.66), int(S * 0.72)
    flesh = radial(S, flesh_in, flesh_out, (cx, cy), 1.3)
    n = _noise(S, 1.0, seed + 9)
    flesh = Image.blend(flesh, Image.merge("RGB", (n, n, n)), 0.10)
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92], fill=255)
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(rim).ellipse([cx - r - 8, cy - r * 0.92 - 8, cx + r + 8, cy + r * 0.92 + 8],
                                fill=skin_dark + (255,))
    img = Image.alpha_composite(img, rim)
    fl = flesh.convert("RGBA")
    fl.putalpha(m)
    d = ImageDraw.Draw(fl)
    rc = ring_col or tuple(min(255, int(c * 1.25)) for c in flesh_out)
    d.ellipse([cx - r * 0.62, cy - r * 0.57, cx + r * 0.62, cy + r * 0.57], outline=rc + (170,),
              width=max(2, S // 120))
    for _ in range(40):  # fibre specks
        a = rng.uniform(0, 6.28); rr = rng.uniform(0, r * 0.85)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.92
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=rc + (120,))
    fl.putalpha(ImageChops.multiply(fl.split()[3], m))
    img = Image.alpha_composite(img, fl)
    # highlight
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([cx - r * 0.7, cy - r * 0.75, cx - r * 0.1, cy - r * 0.45],
                               fill=(255, 255, 255, 60))
    img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(6)))
    return img


def black_turmeric(S):
    # Curcuma caesia: brownish-grey skin, bluish-purple / dark navy flesh
    return rhizome(S, (78, 58, 48), (150, 120, 98), (135, 120, 205), (48, 38, 98), seed=11,
                   ring_col=(180, 170, 240))


def turmeric(S):
    return rhizome(S, (150, 95, 40), (215, 160, 90), (255, 190, 40), (230, 110, 10), seed=5)


def sacha_inchi(S):
    """Star-shaped green pod + brown seeds."""
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    Z = S * SS
    d = ImageDraw.Draw(img)

    def star(cx, cy, R, r, n, rot, col, outline):
        pts = []
        for i in range(n * 2):
            a = rot + i * math.pi / n
            rad = R if i % 2 == 0 else r
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        # rounded via smoothing: draw polygon then blur alpha slightly
        d.polygon(pts, fill=col, outline=outline)
        return pts

    star(Z * 0.40, Z * 0.40, Z * 0.30, Z * 0.15, 5, -0.3, (70, 140, 50), (40, 90, 30))
    star(Z * 0.40, Z * 0.40, Z * 0.20, Z * 0.10, 5, -0.3, (110, 180, 70), None)
    d.ellipse([Z * 0.36, Z * 0.36, Z * 0.44, Z * 0.44], fill=(60, 110, 40))
    for i, (x, y, rot) in enumerate([(0.62, 0.70, 20), (0.78, 0.58, -30), (0.70, 0.84, 70)]):
        seed = Image.new("RGBA", (int(Z * 0.2), int(Z * 0.14)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seed)
        sd.ellipse([0, 0, seed.width - 1, seed.height - 1], fill=(92, 58, 36))
        sd.ellipse([seed.width * 0.15, seed.height * 0.15, seed.width * 0.55, seed.height * 0.45],
                   fill=(150, 105, 70))
        seed = seed.rotate(rot, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(seed, (int(Z * x - seed.width / 2), int(Z * y - seed.height / 2)))
    img = img.resize((S, S), Image.LANCZOS)
    return img


def coffee_beans(S):
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    Z = S * SS
    for (x, y, rot, sc) in [(0.38, 0.40, 30, 1.0), (0.64, 0.58, -25, 0.95), (0.40, 0.72, 75, 0.85)]:
        w, h = int(Z * 0.36 * sc), int(Z * 0.26 * sc)
        b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g = radial(max(w, h), (140, 84, 44), (60, 32, 16), (max(w, h) * 0.38, max(w, h) * 0.35), 1.0)
        g = g.resize((w, h)).convert("RGBA")
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).ellipse([0, 0, w - 1, h - 1], fill=255)
        g.putalpha(m)
        sd = ImageDraw.Draw(g)
        sd.arc([w * 0.05, -h * 0.35, w * 0.95, h * 0.62], 20, 160, fill=(40, 20, 10, 255),
               width=max(3, h // 12))
        g = g.rotate(rot, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(g, (int(Z * x - g.width / 2), int(Z * y - g.height / 2)))
    return img.resize((S, S), Image.LANCZOS)


def circle_crop(src_img, cx, cy, r, out):
    c = src_img.crop((cx - r, cy - r, cx + r, cy + r)).resize((out, out), Image.LANCZOS).convert("RGBA")
    return c


def ingredient_card(art, label, S=300, ring=YELLOW, bg=(255, 248, 225), photo=False, sub=None):
    """Round badge with illustration + label pill underneath."""
    Z = S * SS
    base = Image.new("RGBA", (Z, Z), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.ellipse([0, 0, Z - 1, Z - 1], fill=ring)
    inner = int(Z * 0.055)
    d.ellipse([inner, inner, Z - inner - 1, Z - inner - 1], fill=bg)
    base = base.resize((S, S), Image.LANCZOS)
    ins = int(S * 0.055)
    isz = S - ins * 2
    if photo:
        a = art.resize((isz, isz), Image.LANCZOS)
        m = Image.new("L", (isz * SS, isz * SS), 0)
        ImageDraw.Draw(m).ellipse([0, 0, isz * SS - 1, isz * SS - 1], fill=255)
        a.putalpha(m.resize((isz, isz), Image.LANCZOS))
        base.alpha_composite(a, (ins, ins))
    else:
        a = art.resize((int(isz * 0.86), int(isz * 0.86)), Image.LANCZOS)
        base.alpha_composite(a, ((S - a.width) // 2, (S - a.height) // 2))
    lbl = pill(label, int(S * 0.15), bg=GREEN_D, fg=YELLOW)
    sb = shadow(base, 12, (0, 8), 140)
    W = max(sb.width, lbl.width) + 4
    ly = 36 + S - int(S * 0.20)
    out = Image.new("RGBA", (W, ly + lbl.height), (0, 0, 0, 0))
    out.alpha_composite(sb, ((W - sb.width) // 2, 0))
    out.alpha_composite(lbl, ((W - lbl.width) // 2, ly))
    return out.crop(out.getbbox())


def cart_icon(S, col=BLACK):
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    Z = S * SS
    d = ImageDraw.Draw(img)
    w = int(Z * 0.08)
    d.line([(Z * 0.05, Z * 0.18), (Z * 0.2, Z * 0.18), (Z * 0.32, Z * 0.66), (Z * 0.82, Z * 0.66)],
           fill=col, width=w, joint="curve")
    d.polygon([(Z * 0.24, Z * 0.28), (Z * 0.95, Z * 0.28), (Z * 0.86, Z * 0.56), (Z * 0.31, Z * 0.56)], fill=col)
    for x in (0.38, 0.76):
        d.ellipse([Z * x - Z * 0.08, Z * 0.74, Z * x + Z * 0.08, Z * 0.90], fill=col)
    return img.resize((S, S), Image.LANCZOS)


def check_icon(S, bg=(34, 160, 70)):
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    Z = S * SS
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, Z - 1, Z - 1], fill=bg)
    d.line([(Z * 0.27, Z * 0.52), (Z * 0.44, Z * 0.68), (Z * 0.74, Z * 0.34)], fill=WHITE,
           width=int(Z * 0.11), joint="curve")
    return img.resize((S, S), Image.LANCZOS)


def arrow_down(S, col=YELLOW):
    img = Image.new("RGBA", (S * SS, int(S * 1.3) * SS), (0, 0, 0, 0))
    Z = S * SS
    d = ImageDraw.Draw(img)
    pts = [(Z * 0.32, 0), (Z * 0.68, 0), (Z * 0.68, Z * 0.7), (Z * 0.95, Z * 0.7), (Z * 0.5, Z * 1.25),
           (Z * 0.05, Z * 0.7), (Z * 0.32, Z * 0.7)]
    d.polygon(pts, fill=col, outline=BLACK, width=int(Z * 0.05))
    return img.resize((S, int(S * 1.3)), Image.LANCZOS)


def check_row(text, size=58, max_w=900):
    ic = check_icon(int(size * 1.15))
    tx = stroke_text([text], size, sw=max(4, size // 10))
    W = ic.width + 18 + tx.width
    H = max(ic.height, tx.height)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(ic, (0, (H - ic.height) // 2))
    out.alpha_composite(tx, (ic.width + 18, (H - tx.height) // 2))
    if out.width > max_w:
        r = max_w / out.width
        out = out.resize((max_w, int(out.height * r)), Image.LANCZOS)
    return out


def panel(content, pad=36, bg=(255, 255, 255, 235), radius=40):
    W, H = content.width + pad * 2, content.height + pad * 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, W - 1, H - 1], radius=radius, fill=bg)
    img.alpha_composite(content, (pad, pad))
    return shadow(img, 16, (0, 10), 130)
