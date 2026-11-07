import subprocess, sys, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

# ---- timeline mapping (original -> cut) ----
KEEP = [(0.85, 21.6), (23.15, 25.0), (27.45, 31.15), (31.95, 71.2)]
def m(t):
    acc = 0.0
    for a, b in KEEP:
        if t < a: return acc
        if t <= b: return acc + t - a
        acc += b - a
    return acc
DUR = m(99)

PINK, CYAN, YEL, WHITE, DARK = (254, 44, 85), (37, 244, 238), (255, 225, 77), (255, 255, 255), (22, 22, 28)

def font(p, s): return ImageFont.truetype(p, s)

# ---- captions ----
SEGS = [
 (1.10, 9.64, "Untuk monitor sample score, supaya seller senang approve sample yang kamu request"),
 (10.19, 14.72, "Ok, siapa yang belum tahu macam mana nak tengok sample score kamu"),
 (15.09, 20.41, "Saya tunjuk sini. Kamu pergi ke TikTok Shop for Creator"),
 (20.49, 21.49, "tekan sini"),
 (23.25, 24.73, "kemudian..."),
 (27.69, 30.57, "tekan Manage Samples"),
 (32.17, 33.57, "di sini"),
 (34.14, 37.77, "Dan ini adalah sample score"),
 (37.98, 43.02, "Pastu, View Sample Score. Ini kamu punya keseluruhan sample score"),
 (43.40, 48.13, "Yang ini, berapa kali kamu post sample kamu"),
 (48.61, 53.08, "Frekuensi sample yang kamu post, sama ada naik ataupun"),
 (53.62, 59.33, "turun. Kamu punya sales generation daripada sample kamu"),
 (59.85, 65.31, "dan content quality. Sangat penting untuk monitor sample score kamu"),
 (65.73, 68.96, "supaya kamu senang approve sample daripada seller!"),
]
KEY = {"sample", "score", "seller", "approve", "tiktok", "shop", "creator", "manage", "samples", "view",
       "frekuensi", "post", "sales", "generation", "content", "quality", "penting", "naik", "turun", "request"}

def chunks_for(seg):
    a, b, text = seg
    a, b = m(a), m(b)
    words = text.split()
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[-1] in ".,!?" or sum(len(x) for x in cur) > 16:
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    total = sum(sum(len(w) + 1 for w in g) for g in groups)
    out, t = [], a
    for g in groups:
        d = (b - a) * sum(len(w) + 1 for w in g) / total
        out.append((t, t + d, g)); t += d
    return out

CAPS = [c for s in SEGS for c in chunks_for(s)]
# extend each caption until next one starts (max +0.4s) to avoid flicker
for i in range(len(CAPS)):
    s, e, g = CAPS[i]
    nxt = CAPS[i + 1][0] if i + 1 < len(CAPS) else e + 0.4
    CAPS[i] = (s, min(nxt, e + 0.4), g)

cap_font = font(FONT_BLACK, 82)
def render_caption(words):
    clean = [re.sub(r"[^\w]", "", w).lower() for w in words]
    txt = " ".join(words).upper()
    tmp = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    # lay out word by word with colour per word
    widths = [d.textlength(w.upper() + " ", font=cap_font) for w in words]
    total = sum(widths) - d.textlength(" ", font=cap_font)
    lines = [[]]; lw = [0]
    for w, wd, c in zip(words, widths, clean):
        if lw[-1] + wd > W - 160 and lines[-1]:
            lines.append([]); lw.append(0)
        lines[-1].append((w, wd, c)); lw[-1] += wd
    img = Image.new("RGBA", (W, 120 * len(lines) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for li, line in enumerate(lines):
        x = (W - (lw[li] - d.textlength(" ", font=cap_font))) / 2; y = 20 + li * 110
        for w, wd, c in line:
            col = YEL if c in KEY else WHITE
            d.text((x, y), w.upper(), font=cap_font, fill=col, stroke_width=9, stroke_fill=(0, 0, 0))
            x += wd
    # soft drop shadow
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.putalpha(img.getchannel("A").point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    base = Image.new("RGBA", img.size, (0, 0, 0, 0)); base.alpha_composite(sh, (0, 6)); base.alpha_composite(img)
    return base

def pill(text, sub=None, bg=PINK, fg=WHITE, size=54):
    f = font(FONT_BLACK, size); fs = font(FONT_BOLD, 44)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = d.textlength(text, font=f)
    sw = d.textlength(sub, font=fs) if sub else 0
    pad = 34
    if sub:
        w = int(tw + pad * 2 + sw + pad * 2 + 10); h = size + 44
        img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        d.rounded_rectangle((10, 14, w + 10, h + 14), radius=h // 2, fill=(0, 0, 0, 90))
        d.rounded_rectangle((10, 10, w + 10, h + 10), radius=h // 2, fill=WHITE + (255,))
        lw = int(tw + pad * 2)
        d.rounded_rectangle((10, 10, 10 + lw, h + 10), radius=h // 2, fill=bg + (255,))
        d.text((10 + pad, 10 + h / 2), text, font=f, fill=fg, anchor="lm")
        d.text((10 + lw + pad, 10 + h / 2), sub, font=fs, fill=DARK, anchor="lm")
    else:
        w = int(tw + pad * 2); h = size + 44
        img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        d.rounded_rectangle((10, 14, w + 10, h + 14), radius=h // 2, fill=(0, 0, 0, 90))
        d.rounded_rectangle((10, 10, w + 10, h + 10), radius=h // 2, fill=bg + (255,))
        d.text((10 + w / 2, 10 + h / 2), text, font=f, fill=fg, anchor="mm")
    return img

def hook_card():
    img = Image.new("RGBA", (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # question bubble
    q = "Ramai tanya: kenapa kena jaga Sample Score?"
    fq = font(FONT_BOLD, 40); qw = d.textlength(q, font=fq)
    bx0 = (W - qw) / 2 - 36; bx1 = (W + qw) / 2 + 36
    d.rounded_rectangle((bx0, 20, bx1, 110), radius=26, fill=(255, 255, 255, 245))
    d.polygon([(bx0 + 60, 108), (bx0 + 100, 108), (bx0 + 62, 140)], fill=(255, 255, 255, 245))
    d.text((W / 2, 65), q, font=fq, fill=DARK, anchor="mm")
    f1 = font(FONT_BLACK, 96); f2 = font(FONT_BLACK, 106)
    for txt, y, f, col in [("CARA TENGOK", 230, f1, WHITE), ("SAMPLE SCORE", 360, f2, YEL)]:
        d.text((W / 2 + 6, y + 8), txt, font=f, fill=PINK, anchor="mm", stroke_width=10, stroke_fill=PINK)
        d.text((W / 2 - 4, y - 4), txt, font=f, fill=CYAN, anchor="mm", stroke_width=10, stroke_fill=CYAN)
        d.text((W / 2, y), txt, font=f, fill=col, anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
    sub = pill("Seller laju approve sample!", bg=PINK, size=50)
    img.alpha_composite(sub, ((W - sub.width) // 2, 470))
    return img

def end_card():
    img = Image.new("RGBA", (W, 620), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 0, W - 70, 600), radius=48, fill=(15, 15, 20, 225))
    d.rounded_rectangle((70, 0, W - 70, 600), radius=48, outline=PINK + (255,), width=6)
    f1 = font(FONT_BLACK, 70); f2 = font(FONT_BLACK, 86); f3 = font(FONT_BOLD, 44)
    d.text((W / 2, 95), "SAMPLE SCORE TINGGI", font=f1, fill=WHITE, anchor="mm")
    d.text((W / 2, 185), "=", font=f1, fill=CYAN, anchor="mm")
    d.text((W / 2, 280), "SAMPLE LAJU", font=f2, fill=YEL, anchor="mm")
    d.text((W / 2, 375), "DI-APPROVE", font=f2, fill=YEL, anchor="mm")
    fb = pill("Follow untuk tips affiliate lagi", bg=PINK, size=44)
    img.alpha_composite(fb, ((W - fb.width) // 2, 450))
    return img

STEPS = [  # (orig start, orig end, label, sub)
 (15.09, 23.2, "STEP 1", "TikTok Shop for Creator"),
 (23.25, 27.6, "STEP 2", "Scroll ke Toolkit"),
 (27.69, 34.1, "STEP 3", "Manage Samples"),
 (34.14, 43.3, "STEP 4", "View Sample Score"),
 (43.40, 48.6, "1/4", "Posts with samples"),
 (48.61, 53.6, "2/4", "Post frequency"),
 (53.62, 59.8, "3/4", "Sales generation"),
 (59.85, 65.6, "4/4", "Content quality"),
]
STEP_IMGS = [(m(a), m(b), pill(l, s, bg=(PINK if "STEP" in l else (20, 20, 28)), fg=(WHITE if "STEP" in l else CYAN))) for a, b, l, s in STEPS]
HOOK = (0.0, 3.4, hook_card())
END_T = m(68.6)
END = end_card()
cap_cache = {}

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def pop(t, t0, dur=0.18):  # scale for pop-in
    x = (t - t0) / dur
    if x >= 1: return 1.0
    x = max(0, x); return 0.7 + 0.3 * ease(x) + 0.08 * math.sin(math.pi * x)

def paste(frame, img, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        a = img.getchannel("A").point(lambda v: int(v * alpha)); img = img.copy(); img.putalpha(a)
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

def zoom_at(t):
    z = 1.04 + 0.02 * math.sin(t * 0.25)  # gentle drift
    for s, e, _ in STEP_IMGS[4:]:  # punch-in on each metric
        if s <= t < e: z += 0.10 * ease((t - s) / 0.35)
    if t < 1.0: z += 0.08 * (1 - ease(t / 1.0))  # opening push
    return z

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS
    fr = Image.frombuffer("RGB", (W, H), raw)
    z = zoom_at(t)
    cw, ch = W / z, H / z; x0 = (W - cw) / 2; y0 = (H - ch) / 2 - 20 * (z - 1)
    fr = fr.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BICUBIC).convert("RGBA")

    hs, he, himg = HOOK
    if t < he:
        dim = Image.new("RGBA", (W, H), (0, 0, 0, int(110 * (1 - ease((t - (he - 0.3)) / 0.3)) if t > he - 0.3 else 110)))
        fr.alpha_composite(dim)
        a = 1 - ease((t - (he - 0.3)) / 0.3) if t > he - 0.3 else 1
        paste(fr, himg, W / 2, 720, pop(t, 0.05, 0.3), a)
    for s, e, img in STEP_IMGS:
        if s <= t < e:
            a = 1 - ease((t - (e - 0.2)) / 0.2) if t > e - 0.2 else 1
            slide = (1 - ease((t - s) / 0.3)) * -300
            paste(fr, img, W / 2 + slide, 300, 1.0, a)
    if t >= END_T:
        dim = Image.new("RGBA", (W, H), (0, 0, 0, int(120 * ease((t - END_T) / 0.4))))
        fr.alpha_composite(dim)
        paste(fr, END, W / 2, 820, pop(t, END_T, 0.3), ease((t - END_T) / 0.25))
    else:
        for s, e, g in CAPS:
            if s <= t < e:
                key = " ".join(g)
                if key not in cap_cache: cap_cache[key] = render_caption(g)
                paste(fr, cap_cache[key], W / 2, 1300, pop(t, s, 0.14))
                break
    enc.stdin.write(fr.tobytes()); n += 1
    if n % 300 == 0: print(f"{t:.1f}/{DUR:.1f}s", flush=True)
enc.stdin.close(); enc.wait(); dec.wait()
print("done", n)
