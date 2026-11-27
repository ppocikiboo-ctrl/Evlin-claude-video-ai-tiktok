"""Bralance TikTok ad, version 3 (satin-bag unboxing footage).

Usage: python3 build_v3.py <source.mp4> <work_dir> <out.mp4>

Story: cheap-but-premium hook -> satin storage bag -> extra adhesive covers ->
how to wear -> front clip / mango cup -> stick-to-hand demo (uncovered) ->
pack back into the satin bag (reusable) -> real reviews -> benefit recap + CTA.
Original audio is dropped: a tablet in the background is playing a film.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, WORK, OUT = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
REF = Path(__file__).resolve().parent.parent / "reference"
OV = WORK / "ov3"
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
MAUVE = (92, 60, 66)
BLUSH = (248, 236, 236)
ROSE = (236, 196, 200)


def F(path, size):
    return ImageFont.truetype(path, size)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def centered(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def boxed(img, y, runs, size, font=BLACK, pad=22):
    """One caption line; each run sits on its own solid rounded box. runs=[(text, fg, bg)]."""
    d = ImageDraw.Draw(img)
    f = F(font, size)
    widths = [d.textlength(t, font=f) for t, _, _ in runs]
    x = (W - sum(widths) - pad * 2 * len(runs)) / 2
    for (t, fg, bg), w in zip(runs, widths):
        d.rounded_rectangle((x, y, x + w + pad * 2, y + size * 1.3), radius=18, fill=bg)
        d.text((x + pad, y + size * 0.1), t, font=f, fill=fg)
        x += w + pad * 2
    return y + size * 1.3 + 12


def cap(lines, out, size=70, y=190):
    img = blank()
    for runs in lines:
        y = boxed(img, y, runs, size)
    img.save(OV / out)


def check(d, x, y, s, color):
    d.line([(x, y + s * 0.55), (x + s * 0.38, y + s * 0.9), (x + s, y + s * 0.1)],
           fill=color, width=max(6, int(s * 0.17)), joint="curve")


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def poster(name):
    im = Image.open(REF / name).convert("RGB")
    sx, sy = im.width / 901, im.height / 2000
    return im.crop((int(27 * sx), int(527 * sy), int(873 * sx), int(1316 * sy)))


def rounded_paste(img, pic, x, y, r=36):
    m = Image.new("L", pic.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pic.width, pic.height), radius=r, fill=255)
    img.paste(pic, (x, y), m)


# ---------------- captions (top strip) ----------------
W_, P_, I_, G_ = (INK, WHITE), (WHITE, PINK), (WHITE, INK), (INK, GOLD)
cap([[("Bra ", *W_), ("RM25", *G_), (" je...", *W_)],
     [("tapi packaging", *W_)], [("macam brand mahal?!", *P_)]], "hook.png", size=74)
cap([[("Siap ", *W_), ("beg satin", *P_)], [("untuk simpan bra", *W_)]], "bag.png")
cap([[("Free ", *W_), ("pelekat ekstra", *P_)], [("dalam kotak", *W_)]], "covers.png")
cap([[("Klip depan", *P_)], [("tanpa tali, tanpa cangkuk", *W_)]], "clip.png")
cap([[("Mango cup", *P_), (" tepi 0.1cm", *W_)], [("tak timbul bawah baju", *W_)]], "mango.png")
cap([[("Melekat kuat", *P_)], [("walaupun ", *W_), ("berpeluh", *G_)]], "stick.png", size=66)
cap([[("Lepas pakai, simpan", *W_)], [("dalam beg satin", *P_)]], "store1.png")
cap([[("Boleh pakai", *W_)], [("berulang kali", *G_)]], "store2.png", size=78)

# ---------------- how-to-wear card ----------------
img = Image.new("RGBA", (W, H), BLUSH + (255,))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse((60, 480, W - 60, 1560), fill=(255, 150, 180, 90))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(150)))
d = ImageDraw.Draw(img)
boxed(img, 250, [("CARA PAKAI", WHITE, PINK)], 38, font=XBOLD)
centered(d, 340, "6 langkah mudah", F(SERIF, 96), MAUVE)
p = poster("p5-how-to-wear.jpg")
p = p.resize((960, int(p.height * 960 / p.width)), Image.LANCZOS)
rounded_paste(img, p, 60, 500)
centered(d, 500 + p.height + 50, "Pasang sendiri, siap dalam beberapa saat", F(SEMI, 44), MAUVE)
img.convert("RGB").save(OV / "card_howto.png")

# ---------------- review slate ----------------
img = Image.new("RGBA", (W, H), (30, 14, 20, 150))
d = ImageDraw.Draw(img)
boxed(img, 230, [("APA KATA PEMBELI", WHITE, PINK)], 40, font=XBOLD)
for i in range(5):
    star(d, W / 2 - 200 + i * 100, 400, 42, GOLD)
centered(d, 460, "127 review 5 bintang", F(BLACK, 64), WHITE)
centered(d, 545, "daripada 149 review di TikTok Shop", F(SEMI, 38), ROSE)
quotes = [("“Lembut & melekat kuat.", "Senang nak bersihkan.”"),
          ("“Ok jer bagi ku, ngam", "n selesa, senang cuci.”")]
y = 720
fq = F(SERIF_I, 52)
for a, b in quotes:
    d.rounded_rectangle((90, y, W - 90, y + 220), radius=36, fill=(255, 255, 255, 240))
    for k in range(5):
        star(d, 150 + k * 44, y + 44, 17, GOLD)
    d.text((130, y + 78), a, font=fq, fill=MAUVE)
    d.text((130, y + 142), b, font=fq, fill=MAUVE)
    y += 270
img.save(OV / "reviews.png")

# ---------------- recap + CTA slate ----------------
img = Image.new("RGBA", (W, H), (30, 14, 20, 165))
d = ImageDraw.Draw(img)
p = poster("p7-kit.jpg")
pw = 700
p = p.resize((pw, int(p.height * pw / p.width)), Image.LANCZOS)
rounded_paste(img, p, (W - pw) // 2, 200, r=40)
bx, by, br = W - 230, 200 + p.height - 40, 140
d.ellipse((bx - br, by - br, bx + br, by + br), fill=PINK, outline=WHITE, width=8)
fb = F(BLACK, 76)
d.text((bx - d.textlength("RM25", font=fb) / 2, by - 62), "RM25", font=fb, fill=WHITE)
fs = F(XBOLD, 32)
d.text((bx - d.textlength("SAHAJA", font=fs) / 2, by + 34), "SAHAJA", font=fs, fill=WHITE)
items = ["Murah, cuma RM25", "Boleh pakai berulang kali", "Simpan kemas dalam beg satin",
         "127 review 5 bintang"]
y = 200 + p.height + 70
fi = F(XBOLD, 50)
for it in items:
    d.ellipse((150, y, 206, y + 56), fill=PINK)
    check(d, 163, y + 13, 30, WHITE)
    d.text((232, y + 2), it, font=fi, fill=WHITE)
    y += 84
y += 20
y = boxed(img, y, [("FREE SHIPPING", INK, GOLD), ("SAIZ A - D", INK, WHITE)], 48, font=XBOLD)
boxed(img, y + 20, [("Tekan beg kuning sekarang", WHITE, PINK)], 58)
img.save(OV / "cta.png")

# ---------------- edit decision list ----------------
# ("src", start, end, speed) | ("card", png, seconds) | ("freeze", src_time, seconds)
EDL = [
    ("src", 0.0, 2.5, 1.0),      # 0 box -> hook
    ("src", 2.5, 7.0, 1.5),      # 1 satin bag
    ("src", 7.0, 11.6, 1.5),     # 2 bra + extra adhesive covers
    ("card", "card_howto.png", 2.2),  # 3
    ("src", 11.6, 17.0, 1.4),    # 4 unclip / mango cup
    ("src", 17.0, 20.6, 1.0),    # 5 stick-to-hand demo (uncovered)
    ("src", 20.6, 26.0, 1.3),    # 6 pack back into satin bag
    ("freeze", 25.9, 2.8),       # 7 reviews
    ("freeze", 25.9, 3.2),       # 8 recap + CTA
]
inputs, chains, labels, starts, t = [], [], [], [], 0.0
for k, seg in enumerate(EDL):
    i = inputs.count("-i")
    starts.append(t)
    if seg[0] == "src":
        _, a, b, sp = seg
        inputs += ["-ss", str(a), "-t", str(b - a), "-i", SRC]
        dur = (b - a) / sp
        chains.append(f"[{i}:v]fps={FPS},scale={W}:{H},setsar=1,setpts=(PTS-STARTPTS)/{sp},"
                      f"eq=saturation=1.1:contrast=1.05:brightness=0.01,unsharp=5:5:0.4,"
                      f"trim=0:{dur:.3f},setpts=PTS-STARTPTS[v{k}];")
    elif seg[0] == "card":
        _, png, dur = seg
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", str(OV / png)]
        chains.append(f"[{i}:v]scale={W * 2}:{H * 2},zoompan=z='1+0.04*on/{dur * FPS:.0f}':"
                      f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                      f"setsar=1,format=yuv420p,trim=0:{dur},setpts=PTS-STARTPTS[v{k}];")
    else:
        _, at, dur = seg
        inputs += ["-ss", str(at), "-i", SRC]
        chains.append(f"[{i}:v]fps={FPS},scale={W}:{H},setsar=1,trim=end_frame=1,"
                      f"tpad=stop_mode=clone:stop_duration={dur},boxblur=22:2,"
                      f"trim=0:{dur},setpts=PTS-STARTPTS[v{k}];")
    labels.append(f"[v{k}]")
    t += dur
TOTAL = t
s = starts
fc = "".join(chains) + "".join(labels) + f"concat=n={len(EDL)}:v=1:a=0[cv];"

# audio: silent bed + soft whoosh on each scene change (add a TikTok sound on upload)
cuts = s[1:]
fc += f"anullsrc=r=48000:cl=stereo,atrim=0:{TOTAL:.3f}[bed];"
for j, c in enumerate(cuts):
    d0 = max(0, int((c - 0.2) * 1000))
    fc += (f"anoisesrc=d=0.45:c=pink:r=48000:a=0.5,highpass=f=600,lowpass=f=5000,"
           f"afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2,volume=0.3,"
           f"aformat=channel_layouts=stereo,adelay={d0}|{d0}[w{j}];")
fc += "[bed]" + "".join(f"[w{j}]" for j in range(len(cuts))) + \
      f"amix=inputs={len(cuts) + 1}:normalize=0:duration=first,alimiter=limit=0.9[aout];"

mid4 = s[4] + (s[5] - s[4]) / 2
mid6 = s[6] + (s[7] - s[6]) * 0.5
OVL = [
    ("hook.png", 0.0, s[1]),
    ("bag.png", s[1] + 0.1, s[2]),
    ("covers.png", s[2] + 0.1, s[3]),
    ("clip.png", s[4] + 0.1, mid4),
    ("mango.png", mid4, s[5]),
    ("stick.png", s[5] + 0.2, s[6]),
    ("store1.png", s[6] + 0.1, mid6),
    ("store2.png", mid6, s[7]),
    ("reviews.png", s[7] + 0.1, s[8]),
    ("cta.png", s[8] + 0.1, TOTAL),
]
for png, a, b in OVL:
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{TOTAL:.3f}", "-i", str(OV / png)]
first = inputs.count("-i") - len(OVL)
prev = "[cv]"
for j, (png, a, b) in enumerate(OVL):
    fo = max(a, b - 0.12)
    fc += (f"[{first + j}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.12:alpha=1,"
           f"fade=t=out:st={fo:.3f}:d=0.12:alpha=1[o{j}];"
           f"{prev}[o{j}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[x{j}];")
    prev = f"[x{j}]"
fc += (f"color=c=0xFF5C96:s={W}x10:r={FPS}:d={TOTAL:.3f}[bar];"
       f"{prev}[bar]overlay=x='-w+w*t/{TOTAL:.3f}':y=0:shortest=1[vout]")

subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
                "-map", "[vout]", "-map", "[aout]", "-t", f"{TOTAL:.3f}",
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
print(f"total={TOTAL:.2f}s starts=" + ", ".join(f"{x:.2f}" for x in s))
