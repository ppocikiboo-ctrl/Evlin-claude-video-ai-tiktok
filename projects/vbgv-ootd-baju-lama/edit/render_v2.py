"""Version 2 render: "Closet Diary" fashion-magazine look.

Serif italic headlines, white-box subtitles, versus card, rubber stamp, notes-app
routine card, caution-tape banners, diagonal swipe wipes with RGB glitch, warm
film grade + grain.

Usage: python3 render_v2.py <source.mp4> <mixed_audio.wav> <out.mp4> [--preview t1,t2,...]
"""
import math
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import timeline_v2 as T
from render import (FONT_BLACK, FONT_XB, H, W, FPS, back_out, clamp, ease_out, font, place,
                    rich_text, sparkle_img, stack)

FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"

PINK = (255, 79, 158)
BLUSH = (255, 214, 232)
PLUM = (68, 16, 84)
CREAM = (255, 248, 236)
YELLOW = (255, 222, 89)


def pill(text, size, bg, fg, padx=34, pady=16, fpath=FONT_BLACK, radius=None, shadow=True):
    t = rich_text(text, fpath, size, fg, shadow=False)
    w, h = t.width + padx * 2 - 28, t.height + pady * 2 - 28
    im = Image.new("RGBA", (w + 12, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = radius if radius is not None else h // 2
    if shadow:
        d.rounded_rectangle((6, 10, w + 6, h + 10), r, fill=(40, 0, 40, 90))
    d.rounded_rectangle((0, 0, w, h), r, fill=bg + (255,))
    im.alpha_composite(t, (padx - 14, pady - 14))
    return im


def line(text, style):
    if style == "serif":
        return rich_text(text, FONT_SERIF, 88, CREAM, PLUM, 7)
    if style == "kicker":
        return pill(text, 48, PINK, (255, 255, 255))
    if style == "pinkpill":
        return pill(text, 46, PINK, (255, 255, 255))
    if style == "shout":
        return rich_text(text, FONT_BLACK, 98, YELLOW, PLUM, 12)
    raise ValueError(style)


def fit(img, maxw=W - 60):
    if img.width > maxw:
        k = maxw / img.width
        img = img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
    return img


def make_stamp(lines):
    f = font(FONT_BLACK, 54)
    tw = max(int(f.getlength(s)) for s in lines)
    w, h = tw + 80, 70 * len(lines) + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = PINK + (240,)
    d.rounded_rectangle((4, 4, w - 4, h - 4), 18, outline=col, width=8)
    d.rounded_rectangle((18, 18, w - 18, h - 18), 10, outline=col, width=3)
    for i, s in enumerate(lines):
        d.text((w / 2, 25 + 35 + i * 70), s, font=f, fill=col, anchor="mm")
    # worn ink texture
    rng = np.random.default_rng(1)
    a = np.array(im.split()[3]).astype(np.float32)
    a *= (rng.random(a.shape) > 0.12)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    bg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle((4, 4, w - 4, h - 4), 18, fill=(255, 248, 236, 150))
    bg.alpha_composite(im)
    return bg.rotate(-11, resample=Image.BICUBIC, expand=True)


def make_notes():
    n = T.NOTES
    w = 820
    header = rich_text(n["title"], FONT_BLACK, 52, PLUM, shadow=False)
    rows = []
    for i, (_, txt) in enumerate(n["items"]):
        r = Image.new("RGBA", (w - 60, 96), (0, 0, 0, 0))
        d = ImageDraw.Draw(r)
        d.ellipse((0, 14, 68, 82), fill=PINK + (255,))
        d.text((34, 48), str(i + 1), font=font(FONT_BLACK, 42), fill=(255, 255, 255), anchor="mm")
        t = rich_text(txt, FONT_XB, 50, PLUM, shadow=False)
        r.alpha_composite(t, (90, (96 - t.height) // 2))
        rows.append(r)
    h = 130 + 100 * len(rows) + 30
    card = Image.new("RGBA", (w + 16, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((8, 14, w + 8, h + 14), 40, fill=(40, 0, 40, 80))
    d.rounded_rectangle((0, 0, w, h), 40, fill=CREAM + (238,))
    d.rounded_rectangle((0, 0, w, 120), 40, fill=BLUSH + (255,))
    d.rectangle((0, 80, w, 120), fill=BLUSH + (255,))
    card.alpha_composite(header, (30, (120 - header.height) // 2))
    for k in range(len(rows)):  # faint ruled lines
        y = 130 + 100 * k + 98
        d.line((40, y, w - 40, y), fill=(230, 190, 210, 255), width=2)
    return card, rows


def make_tape(text):
    f = font(FONT_BLACK, 60)
    seg = int(f.getlength(text))
    reps = 3000 // seg + 2
    im = Image.new("RGBA", (seg * reps, 112), YELLOW + (255,))
    d = ImageDraw.Draw(im)
    for k in range(0, seg * reps, 60):  # hazard stripes on the edges
        d.polygon([(k, 0), (k + 30, 0), (k + 18, 12), (k - 12, 12)], fill=PLUM + (255,))
        d.polygon([(k, 112), (k + 30, 112), (k + 42, 100), (k + 12, 100)], fill=PLUM + (255,))
    for r in range(reps):
        d.text((r * seg, 56), text, font=f, fill=PLUM, anchor="lm")
    return im, seg


def make_pointer():
    label = pill("Beg kuning 🛒", 44, YELLOW, PLUM)
    finger = rich_text("👇", FONT_BLACK, 130, (0, 0, 0), shadow=True).rotate(
        28, resample=Image.BICUBIC, expand=True)
    out = Image.new("RGBA", (max(label.width + 40, finger.width + 20), label.height + finger.height - 20),
                    (0, 0, 0, 0))
    out.alpha_composite(label, (40, 0))
    out.alpha_composite(finger, (0, label.height - 20))
    return out


def build():
    A = {}
    A["heads"] = [(o, fit(stack([line(t, s) for t, s in o["lines"]], gap=-26))) for o in T.HEADLINES]
    v = T.VERSUS
    A["vs_l"] = pill(v["left"], 46, PLUM, (255, 255, 255))
    A["vs_r"] = pill(v["right"], 46, PINK, (255, 255, 255))
    vs = Image.new("RGBA", (170, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(vs)
    d.ellipse((8, 12, 162, 166), fill=(40, 0, 40, 100))
    d.ellipse((4, 4, 158, 158), fill=YELLOW + (255,), outline=PLUM + (255,), width=7)
    d.text((81, 81), "VS", font=font(FONT_SERIF, 74), fill=PLUM, anchor="mm")
    A["vs"] = vs
    A["vs_sub"] = pill(v["sub"][0], 44, CREAM, PLUM)
    A["stamp"] = make_stamp(T.STAMP["lines"])
    A["notes"] = make_notes()
    A["tape"] = make_tape(T.TAPE["text"])
    A["pointer"] = make_pointer()
    A["tag"] = pill(T.CORNER_TAG["text"], 34, CREAM, PLUM, padx=26, pady=12)
    return A


random.seed(11)
SPARKS = []
for a0, a1 in T.SPARKLES:
    for _ in range(int((a1 - a0) * 2.4)):
        SPARKS.append(dict(t=random.uniform(a0, max(a0, a1 - 0.6)),
                           x=random.choice([random.randint(40, 240), random.randint(840, 1030)]),
                           y=random.randint(620, 1250), s=random.randint(34, 72),
                           c=random.choice([PINK, CREAM, YELLOW])))
_sp = {}


# ---------------- effects ----------------
def zoom_factor(t):
    z = 1.0
    for p in T.PUNCHES:
        dt = t - p
        if 0 <= dt < 0.5:
            z += 0.07 * (1 - ease_out(dt / 0.5))
    starts = T.PUNCHES + [36.2]
    for a, b in zip(starts, starts[1:]):
        if a <= t < b:
            z *= 1.0 + 0.03 * (t - a) / (b - a)
    return z


def wipe(frame, t):
    """Diagonal pink/plum panel sweeping left->right, centred on each punch."""
    for p in T.PUNCHES[1:]:
        u = (t - p + 0.16) / 0.34
        if 0 <= u <= 1:
            d = ImageDraw.Draw(frame)
            x = -700 + u * (W + 1400)
            slant = 420
            d.polygon([(x - 260, 0), (x + 260, 0), (x + 260 - slant, H), (x - 260 - slant, H)],
                      fill=PINK + (255,))
            d.polygon([(x + 200, 0), (x + 290, 0), (x + 290 - slant, H), (x + 200 - slant, H)],
                      fill=PLUM + (255,))
            d.polygon([(x - 330, 0), (x - 260, 0), (x - 260 - slant, H), (x - 330 - slant, H)],
                      fill=CREAM + (255,))


def glitch(arr, t):
    for p in T.PUNCHES[1:]:
        dt = t - p
        if 0 <= dt < 0.14:
            k = int(16 * (1 - dt / 0.14)) + 2
            out = arr.copy()
            out[:, k:, 0] = arr[:, :-k, 0]
            out[:, :-k, 2] = arr[:, k:, 2]
            return out
    return arr


def anim_place(frame, img, t, t0, t1, cx, cy, anim="rise"):
    if not (t0 <= t < t1):
        return
    dt, rem = t - t0, t1 - t
    a = clamp(dt / 0.2) * clamp(rem / 0.15)
    sc, ang = 1.0, 0.0
    if anim == "rise":
        cy += 70 * (1 - ease_out(dt / 0.35))
    elif anim == "pop":
        sc = max(0.01, back_out(dt / 0.3)) if dt < 0.3 else 1.0 + 0.025 * math.sin(dt * 9)
    place(frame, img, cx, cy, sc, a, ang)


def draw_subs(frame, t):
    for start, end, words in T.SUBS:
        if not (start <= t < end):
            continue
        dt = t - start
        f = font(FONT_BLACK, 56)
        space = f.getlength(" ") + 16
        items = []
        for i, (w, wt) in enumerate(words):
            nxt = words[i + 1][1] if i + 1 < len(words) else end
            items.append((w, wt <= t < nxt, f.getlength(w)))
        lines, cur, cw = [], [], 0
        for it in items:
            if cur and cw + space + it[2] > W - 150:
                lines.append(cur)
                cur, cw = [], 0
            cw += (space if cur else 0) + it[2]
            cur.append(it)
        lines.append(cur)
        lh = 88
        sc = 0.85 + 0.15 * (back_out(dt / 0.16, 1.6) if dt < 0.16 else 1.0)
        layer = Image.new("RGBA", (W, lh * len(lines) + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for li, ln in enumerate(lines):
            tw = sum(x[2] for x in ln) + space * (len(ln) - 1)
            x0 = (W - tw) / 2
            y0 = 10 + li * lh
            d.rounded_rectangle((x0 - 26, y0, x0 + tw + 26, y0 + lh - 6), 22, fill=(255, 255, 255, 245))
            x = x0
            for w, speaking, wl in ln:
                if speaking:
                    d.rounded_rectangle((x - 8, y0 + 10, x + wl + 8, y0 + lh - 16), 14,
                                        fill=PINK + (255,))
                    col = (255, 255, 255)
                else:
                    col = PINK if w.lower() in T.KEYWORDS else PLUM
                d.text((x, y0 + (lh - 6) / 2), w, font=f, fill=col, anchor="lm")
                x += wl + space
        place(frame, layer, W / 2, 1400, sc)
        return


def compose(base, t, A):
    z = zoom_factor(t)
    if z > 1.001:
        cw, ch = W / z, H / z
        cy = min(max(H * 0.46, ch / 2), H - ch / 2)
        base = base.resize((W, H), Image.BILINEAR,
                           box=(W / 2 - cw / 2, cy - ch / 2, W / 2 + cw / 2, cy + ch / 2))
    arr = glitch(np.asarray(base), t)
    frame = Image.fromarray(arr).convert("RGBA")

    for s in SPARKS:
        dt = t - s["t"]
        if 0 <= dt < 0.7:
            k = math.sin(math.pi * dt / 0.7)
            key = (s["s"], s["c"])
            if key not in _sp:
                _sp[key] = sparkle_img(s["s"], s["c"])
            place(frame, _sp[key], s["x"], s["y"], 0.3 + 0.7 * k, k, dt * 90)

    ct = T.CORNER_TAG
    if ct["t0"] <= t < ct["t1"]:
        dt = t - ct["t0"]
        tag = A["tag"]
        place(frame, tag, 40 + tag.width / 2 - (1 - ease_out(dt / 0.4)) * (tag.width + 60), 205)

    for o, img in A["heads"]:
        anim_place(frame, img, t, o["t0"], o["t1"], W / 2, o["y"], o["anim"])

    # versus card
    v = T.VERSUS
    if v["t0"] <= t < v["t1"]:
        dt, rem = t - v["t0"], v["t1"] - t
        a = clamp(rem / 0.15)
        k = 1 - ease_out(dt / 0.35)
        place(frame, A["vs_l"], 280 - k * 700, v["y"], 1, a, 0)
        place(frame, A["vs_r"], 800 + k * 700, v["y"], 1, a, 0)
        if dt > 0.2:
            place(frame, A["vs"], W / 2, v["y"], max(0.01, back_out((dt - 0.2) / 0.3)), a,
                  8 * math.sin(dt * 6))
        st = v["sub"][1]
        if t >= st:
            place(frame, A["vs_sub"], W / 2, v["y"] + 150 + 40 * (1 - ease_out((t - st) / 0.3)), 1,
                  a * clamp((t - st) / 0.2))

    # stamp
    s = T.STAMP
    if s["t0"] <= t < s["t1"]:
        dt, rem = t - s["t0"], s["t1"] - t
        sc = 1 + 1.3 * (1 - ease_out(dt / 0.16)) if dt < 0.16 else 1.0
        jit = 6 * math.exp(-dt * 25) * math.sin(dt * 90)
        place(frame, A["stamp"], s["x"] + jit, s["y"], sc, clamp(dt / 0.08) * clamp(rem / 0.15))

    # notes card
    n = T.NOTES
    if n["t0"] <= t < n["t1"]:
        card, rows = A["notes"]
        dt, rem = t - n["t0"], n["t1"] - t
        a = clamp(rem / 0.15)
        cy = n["y0"] + card.height / 2 - (1 - ease_out(dt / 0.4)) * 120
        c = card.copy()
        for i, (t0, _) in enumerate(n["items"]):
            if t >= t0:
                rk = ease_out((t - t0) / 0.3)
                r = rows[i]
                if rk < 0.999:
                    r = r.copy()
                    r.putalpha(r.split()[3].point(lambda q: int(q * rk)))
                c.alpha_composite(r, (30 + int(40 * (1 - rk)), 130 + 100 * i))
        place(frame, c, W / 2, cy, 1, a * clamp(dt / 0.2))

    # caution tape
    tp = T.TAPE
    if tp["t0"] <= t < tp["t1"]:
        dt, rem = t - tp["t0"], tp["t1"] - t
        strip, seg = A["tape"]
        a = clamp(rem / 0.15)
        for k, (yy, ang, dirn) in enumerate([(430, 7, 1), (590, -6, -1)]):
            off = int((dt * 420) % seg)
            x0 = off if dirn > 0 else seg - off
            win = strip.crop((x0, 0, x0 + 1400, strip.height))
            inn = ease_out((dt - 0.08 * k) / 0.25)
            place(frame, win, W / 2 + dirn * (1 - inn) * 1400, yy, 1.0, a, ang)

    for p0, p1 in T.POINTERS:
        if p0 <= t < p1:
            dt = t - p0
            b = abs(math.sin(dt * 7)) * 30
            ptr = A["pointer"]
            place(frame, ptr, 50 + ptr.width / 2 - b * 0.5, 1150 + b,
                  max(0.01, back_out(dt / 0.25)) if dt < 0.25 else 1.0, clamp((p1 - t) / 0.12))

    draw_subs(frame, t)
    wipe(frame, t)
    return frame.convert("RGB")


def main():
    src, audio, out = sys.argv[1:4]
    preview = None
    if len(sys.argv) > 5 and sys.argv[4] == "--preview":
        preview = [float(x) for x in sys.argv[5].split(",")]
    A = build()
    vf = (f"fps={FPS},scale={W}:{H},eq=contrast=1.04:saturation=1.08:brightness=0.02,"
          "colorbalance=rs=0.05:gs=0.01:bs=-0.02:rm=0.03:bm=0.02,"
          "curves=all='0/0.05 0.5/0.52 1/0.97',noise=alls=7:allf=t,vignette=angle=PI/6")
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
    n, fsz = 0, W * H * 3
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        t = n / FPS
        if preview is not None:
            hit = [p for p in preview if abs(p - t) < 0.5 / FPS]
            if hit:
                compose(Image.frombuffer("RGB", (W, H), buf), t, A).save(
                    f"{out}_{hit[0]:05.2f}.jpg", quality=85)
        else:
            enc.stdin.write(compose(Image.frombuffer("RGB", (W, H), buf), t, A).tobytes())
        n += 1
    dec.wait()
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    main()
