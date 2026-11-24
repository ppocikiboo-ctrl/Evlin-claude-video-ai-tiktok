"""Bralance TikTok ad, version 2 ("demo-first" + 5-reason checklist).

Usage: python3 build_v2.py <source.mp4> <work_dir> <out.mp4>

Opens on the stick-to-hand demo, speeds up the unboxing, builds a 5-item
checklist, cuts to dark premium product cards, returns to the demo uncovered,
and ends on a blurred-frame price slate. All overlays stay in the top strip
whenever the stick-to-hand demo is on screen.
"""
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, WORK, OUT = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
REF = Path(__file__).resolve().parent.parent / "reference"
OV = WORK / "ov2"
OV.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1080, 1920, 30
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
WHITE = (255, 255, 255)
PINK = (255, 92, 150)
GOLD = (255, 200, 60)
INK = (24, 14, 18)
PLUM = (42, 24, 31)
ROSE = (236, 196, 200)


def F(path, size):
    return ImageFont.truetype(path, size)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def centered(d, y, text, font, fill, **kw):
    tw = d.textlength(text, font=font)
    d.text(((W - tw) / 2, y), text, font=font, fill=fill, **kw)


def highlight_line(img, y, runs, size, font=BLACK, pad=22):
    """TikTok-style caption: each line sits on its own solid box. runs=[(text, fg, bg)]."""
    d = ImageDraw.Draw(img)
    f = F(font, size)
    widths = [d.textlength(t, font=f) for t, _, _ in runs]
    x = (W - sum(widths) - pad * 2 * len(runs)) / 2
    for (t, fg, bg), w in zip(runs, widths):
        d.rounded_rectangle((x, y, x + w + pad * 2, y + size * 1.3), radius=18, fill=bg)
        d.text((x + pad, y + size * 0.1), t, font=f, fill=fg)
        x += w + pad * 2
    return y + size * 1.3 + 12


def check(d, x, y, s, color):
    d.line([(x, y + s * 0.55), (x + s * 0.38, y + s * 0.9), (x + s, y + s * 0.1)],
           fill=color, width=max(6, int(s * 0.17)), joint="curve")


def poster(name):
    im = Image.open(REF / name).convert("RGB")
    sx, sy = im.width / 901, im.height / 2000
    return im.crop((int(27 * sx), int(527 * sy), int(873 * sx), int(1316 * sy)))


def rounded_paste(img, pic, x, y, r=36):
    m = Image.new("L", pic.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pic.width, pic.height), radius=r, fill=255)
    img.paste(pic, (x, y), m)


# ---------------- hook (over demo: top strip only) ----------------
img = blank()
y = highlight_line(img, 200, [("Bra ni boleh", INK, WHITE)], 72)
highlight_line(img, y, [("MELEKAT", WHITE, PINK), ("kat tangan?!", INK, WHITE)], 72)
img.save(OV / "hook1.png")

img = blank()
y = highlight_line(img, 200, [("Tak ada tali.", INK, WHITE)], 72)
highlight_line(img, y, [("Tak ada cangkuk.", WHITE, PINK)], 72)
img.save(OV / "hook2.png")

# ---------------- 5-reason checklist (cumulative states) ----------------
ITEMS = [
    "Tiada tali, tiada cangkuk",
    "Klip depan, senang pasang",
    "Tepi nipis cuma 0.1cm",
    "Kekal melekat walaupun berpeluh",
    "Boleh basuh & guna semula",
]
for n in range(1, 6):
    img = blank()
    d = ImageDraw.Draw(img)
    top, row = 180, 74
    bottom = top + 100 + row * 5 + 20
    d.rounded_rectangle((60, top, W - 60, bottom), radius=36, fill=(24, 14, 18, 200))
    ft = F(BLACK, 50)
    d.text((100, top + 28), "5 sebab ", font=ft, fill=WHITE)
    d.text((100 + d.textlength("5 sebab ", font=ft), top + 28), "wajib ada", font=ft, fill=PINK)
    fi = F(XBOLD, 44)
    for i, item in enumerate(ITEMS):
        yy = top + 112 + i * row
        if i < n:
            d.ellipse((100, yy, 150, yy + 50), fill=PINK)
            check(d, 112, yy + 12, 26, WHITE)
            d.text((172, yy + 2), item, font=fi, fill=WHITE)
        else:
            d.ellipse((100, yy, 150, yy + 50), outline=(255, 255, 255, 90), width=4)
            d.text((172, yy + 2), item, font=fi, fill=(255, 255, 255, 70))
    img.save(OV / f"chk{n}.png")


# ---------------- dark premium product cards ----------------
def card(name, kicker, title, sub, out):
    img = Image.new("RGBA", (W, H), PLUM + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((90, 520, W - 90, 1500), fill=(255, 92, 150, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(140)))
    d = ImageDraw.Draw(img)
    centered(d, 250, kicker, F(XBOLD, 36), PINK)
    d.line((W / 2 - 60, 310, W / 2 + 60, 310), fill=ROSE, width=3)
    centered(d, 340, title, F(SERIF, 96), WHITE)
    p = poster(name)
    pw = 940
    p = p.resize((pw, int(p.height * pw / p.width)), Image.LANCZOS)
    rounded_paste(img, p, (W - pw) // 2, 500)
    fs = F(SEMI, 44)
    for i, line in enumerate(sub):
        centered(d, 500 + p.height + 60 + i * 60, line, fs, ROSE)
    img.convert("RGB").save(OV / out)


card("p3-mango-cup.jpg", "BENTUK MANGO CUP", "Angkat & bentuk", ["Natural, tak nampak tebal"], "card_mango.png")
card("p6-size-guide.jpg", "PILIH SAIZ", "A  ·  B  ·  C  ·  D", ["Ikut saiz bra biasa anda"], "card_size.png")

# ---------------- demo caption (top strip) ----------------
img = blank()
y = highlight_line(img, 200, [("Silikon lembut,", INK, WHITE)], 66)
highlight_line(img, y, [("melekat rapat", WHITE, PINK)], 66)
img.save(OV / "demo.png")

# ---------------- CTA slate (over blurred last frame) ----------------
img = Image.new("RGBA", (W, H), (24, 14, 18, 120))
d = ImageDraw.Draw(img)
centered(d, 210, "SET LENGKAP DALAM KOTAK", F(XBOLD, 40), ROSE)
p = poster("p7-kit.jpg")
pw = 800
p = p.resize((pw, int(p.height * pw / p.width)), Image.LANCZOS)
rounded_paste(img, p, (W - pw) // 2, 290, r=40)
# price badge overlapping the kit photo corner
bx, by, br = W - 200, 290 + p.height - 30, 150
d.ellipse((bx - br, by - br, bx + br, by + br), fill=PINK, outline=WHITE, width=8)
fb = F(BLACK, 80)
tw = d.textlength("RM25", font=fb)
d.text((bx - tw / 2, by - 66), "RM25", font=fb, fill=WHITE)
fs = F(XBOLD, 34)
tw = d.textlength("SAHAJA", font=fs)
d.text((bx - tw / 2, by + 40), "SAHAJA", font=fs, fill=WHITE)
y = 290 + p.height + 150
centered(d, y, "Kotak + beg satin + pelekat ekstra", F(SEMI, 44), WHITE)
y += 90
y = highlight_line(img, y, [("FREE SHIPPING", INK, GOLD), ("SAIZ A - D", INK, WHITE)], 50, font=XBOLD)
y += 30
highlight_line(img, y, [("Tekan beg kuning sekarang", WHITE, PINK)], 58)
img.save(OV / "cta.png")

img = blank()
ImageDraw.Draw(img).text((58, 120), "bralance", font=F(SERIF, 46), fill=(255, 255, 255, 230),
                         stroke_width=2, stroke_fill=(0, 0, 0, 120))
img.save(OV / "brand.png")

# ---------------- edit decision list ----------------
# ("src", start, end, speed) | ("card", png, seconds) | ("freeze", src_time, seconds)
EDL = [
    ("src", 16.0, 18.6, 1.0),   # demo-first hook
    ("src", 0.0, 6.0, 1.6),     # unboxing, sped up
    ("card", "card_mango.png", 2.0),
    ("src", 6.0, 11.0, 1.6),
    ("card", "card_size.png", 2.2),
    ("src", 11.0, 15.6, 1.6),
    ("src", 18.6, 22.9, 1.0),   # demo again, uncovered
    ("freeze", 22.85, 3.3),     # CTA background
]

inputs, chains, labels, starts = [], [], [], []
t = 0.0
for k, seg in enumerate(EDL):
    i = inputs.count("-i")
    starts.append(t)
    if seg[0] == "src":
        _, a, b, sp = seg
        inputs += ["-ss", str(a), "-t", str(b - a), "-i", SRC]
        dur = (b - a) / sp
        chains.append(f"[{i}:v]fps={FPS},scale={W}:{H},setsar=1,setpts=(PTS-STARTPTS)/{sp},"
                      f"eq=saturation=1.12:contrast=1.05:brightness=0.015,unsharp=5:5:0.4,"
                      f"trim=0:{dur:.3f},setpts=PTS-STARTPTS[v{k}];"
                      f"[{i}:a]aresample=48000,atempo={sp},highpass=f=90,volume=9dB,"
                      f"atrim=0:{dur:.3f},asetpts=PTS-STARTPTS[a{k}];")
    elif seg[0] == "card":
        _, png, dur = seg
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", str(OV / png)]
        z = f"1+0.04*on/{dur * FPS:.0f}"  # slow Ken Burns push
        chains.append(f"[{i}:v]scale={W * 2}:{H * 2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
                      f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p,"
                      f"trim=0:{dur},setpts=PTS-STARTPTS[v{k}];"
                      f"anullsrc=r=48000:cl=stereo,atrim=0:{dur}[a{k}];")
    else:
        _, at, dur = seg
        inputs += ["-ss", str(at), "-i", SRC]
        chains.append(f"[{i}:v]fps={FPS},scale={W}:{H},setsar=1,trim=end_frame=1,"
                      f"tpad=stop_mode=clone:stop_duration={dur},boxblur=22:2,"
                      f"eq=brightness=-0.05,trim=0:{dur},setpts=PTS-STARTPTS[v{k}];"
                      f"anullsrc=r=48000:cl=stereo,atrim=0:{dur}[a{k}];")
    labels.append(f"[v{k}][a{k}]")
    t += dur
TOTAL = t
fc = "".join(chains)
fc += "".join(labels) + f"concat=n={len(EDL)}:v=1:a=1[cv][ca0];"
# audio: original crinkle + soft whoosh on each hard transition
cuts = [starts[2], starts[3], starts[4], starts[5], starts[7]]
fc += f"[ca0]aformat=channel_layouts=stereo,afade=t=out:st={starts[7] - 0.6:.2f}:d=0.6[ca];"
for j, c in enumerate(cuts):
    d0 = max(0, int((c - 0.2) * 1000))
    fc += (f"anoisesrc=d=0.45:c=pink:r=48000:a=0.5,highpass=f=600,lowpass=f=5000,"
           f"afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2,volume=0.35,"
           f"aformat=channel_layouts=stereo,adelay={d0}|{d0}[w{j}];")
fc += "[ca]" + "".join(f"[w{j}]" for j in range(len(cuts))) + \
      f"amix=inputs={len(cuts) + 1}:normalize=0:duration=first,alimiter=limit=0.9[aout];"

# overlays on the output timeline
s = starts
OVL = [
    ("brand.png", 0, s[2]), ("brand.png", s[3], s[4]), ("brand.png", s[5], s[7]),
    ("hook1.png", 0, 1.4), ("hook2.png", 1.4, s[1]),
    ("chk1.png", s[1] + 0.2, s[1] + 1.9, True, False), ("chk2.png", s[1] + 1.9, s[2], False, True),
    ("chk3.png", s[3], s[3] + 1.6, True, False), ("chk4.png", s[3] + 1.6, s[4], False, True),
    ("chk5.png", s[5], s[6]),
    ("demo.png", s[6] + 0.3, s[7]),
    ("cta.png", s[7] + 0.1, TOTAL),
]
prev = "[cv]"
# entries: (png, start, end[, fade_in, fade_out]); consecutive checklist states swap without a dip
OVL = [o if len(o) == 5 else (*o, True, True) for o in OVL]
for png, a, b, _, _ in OVL:
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{TOTAL:.3f}", "-i", str(OV / png)]
first_ovl = inputs.count("-i") - len(OVL)
for j, (png, a, b, fin, fout) in enumerate(OVL):
    i = first_ovl + j
    fo = max(a, b - 0.12)
    fades = (f",fade=t=in:st={a:.3f}:d=0.12:alpha=1" if fin else "") + \
            (f",fade=t=out:st={fo:.3f}:d=0.12:alpha=1" if fout else "")
    fc += (f"[{i}:v]format=rgba{fades}[o{j}];"
           f"{prev}[o{j}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[x{j}];")
    prev = f"[x{j}]"
# pink retention progress bar along the top edge
fc += (f"color=c=0xFF5C96:s={W}x10:r={FPS}:d={TOTAL:.3f}[bar];"
       f"{prev}[bar]overlay=x='-w+w*t/{TOTAL:.3f}':y=0:shortest=1[vout]")

cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
       "-map", "[vout]", "-map", "[aout]", "-t", f"{TOTAL:.3f}",
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print(f"total={TOTAL:.2f}s starts=" + ", ".join(f"{x:.2f}" for x in starts))
