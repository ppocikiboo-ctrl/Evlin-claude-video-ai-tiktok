"""Version 3 render: "Chat Bestie" — group-chat bubbles, frosted phone notifications,
stock alert, pulsing CTA button, floating reactions, whip-pan transitions.

Usage: python3 render_v3.py <source.mp4> <mixed_audio.wav> <out.mp4> [--preview t1,t2,...]
"""
import math
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import timeline_v3 as T
from render import (FONT_BLACK, FONT_XB, FPS, H, W, back_out, clamp, ease_out, emoji_img, font,
                    place, rich_text)

PURPLE = (124, 58, 237)
VIOLET = (168, 85, 247)
INK = (24, 20, 38)
WHITE = (255, 255, 255)
LIME = (190, 255, 90)
RED = (239, 68, 68)
YELLOW = (255, 222, 89)


def wrap(text, fpath, size, maxw):
    words, lines, cur = text.split(), [], ""
    f = font(fpath, size)
    for w in words:
        cand = (cur + " " + w).strip()
        if cur and f.getlength(cand) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    lines.append(cur)
    return lines


def gradient(w, h, c0, c1):
    g = np.linspace(0, 1, w)[None, :, None]
    arr = (np.array(c0)[None, None, :] * (1 - g) + np.array(c1)[None, None, :] * g)
    arr = np.repeat(arr, h, axis=0).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def bubble(text, side):
    lines = wrap(text, FONT_XB, 46, 640)
    imgs = [rich_text(s, FONT_XB, 46, WHITE if side == "R" else INK, shadow=False) for s in lines]
    tw = max(i.width for i in imgs) - 28
    th = sum(i.height - 28 for i in imgs) + 8 * (len(imgs) - 1)
    pw, ph = 30, 22
    w, h = tw + pw * 2, th + ph * 2
    im = Image.new("RGBA", (w + 30, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox = 0 if side == "R" else 18
    d.rounded_rectangle((ox + 4, 8, ox + w + 4, h + 8), 34, fill=(0, 0, 0, 70))
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((ox, 0, ox + w, h), 34, fill=255)
    if side == "R":  # tail bottom-right
        md.polygon([(ox + w - 40, h - 30), (ox + w + 22, h + 4), (ox + w - 8, h - 6)], fill=255)
        fill = gradient(im.width, im.height, VIOLET, PURPLE)
    else:  # tail bottom-left
        md.polygon([(ox + 40, h - 30), (ox - 18, h + 4), (ox + 8, h - 6)], fill=255)
        fill = Image.new("RGBA", im.size, (255, 255, 255, 250))
    im.paste(fill, (0, 0), mask)
    y = ph - 14
    for i in imgs:
        im.alpha_composite(i, (ox + pw - 14, y))
        y += i.height - 28 + 8
    return im


def notif_card(title, body, w=960, h=132, accent=PURPLE, big=False):
    """Foreground of a notification (frosted background is added per frame)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(255, 255, 255, 150),
                        outline=(255, 255, 255, 210), width=2)
    s = h - 44
    d.rounded_rectangle((22, 22, 22 + s, 22 + s), 22, fill=accent + (255,))
    e = emoji_img("💜" if not big else "🔥", int(s * 0.6))
    im.alpha_composite(e, (22 + (s - e.width) // 2, 22 + (s - e.height) // 2))
    x = 22 + s + 24
    ts, bs = (40, 50) if big else (34, 42)
    tt = rich_text(title, FONT_BLACK, ts, INK if not big else RED, shadow=False)
    bt = rich_text(body, FONT_XB, bs, INK, shadow=False)
    im.alpha_composite(tt, (x - 14, 14 if not big else 12))
    im.alpha_composite(bt, (x - 14, h // 2 - 6 if not big else h // 2 - 2))
    d.text((w - 30, 30), "now", font=font(FONT_XB, 28), fill=(90, 80, 110), anchor="rt")
    return im


def frosted(frame, card, cx, cy, alpha=1.0, scale=1.0):
    """Blur the video under the card, then lay the card on top."""
    if alpha <= 0.01:
        return
    c = card
    if abs(scale - 1) > 0.005:
        c = c.resize((max(1, int(c.width * scale)), max(1, int(c.height * scale))), Image.BILINEAR)
    x, y = int(cx - c.width / 2), int(cy - c.height / 2)
    box = (max(0, x), max(0, y), min(W, x + c.width), min(H, y + c.height))
    if box[2] <= box[0] or box[3] <= box[1]:
        return
    region = frame.crop(box).filter(ImageFilter.GaussianBlur(18))
    mask = Image.new("L", c.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, c.width - 1, c.height - 1), int(36 * scale), fill=255)
    mask = mask.crop((box[0] - x, box[1] - y, box[2] - x, box[3] - y))
    if alpha < 0.999:
        mask = mask.point(lambda v: int(v * alpha))
    frame.paste(region, box[:2], mask)
    place(frame, c, cx, cy, scale, alpha)


def cta_button(text, sub):
    t = rich_text(text, FONT_BLACK, 76, WHITE, shadow=False)
    w, h = t.width + 60, t.height + 20
    im = Image.new("RGBA", (w + 16, h + 20), (0, 0, 0, 0))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    sh = Image.new("RGBA", (w, h), (40, 0, 60, 120))
    im.paste(sh, (8, 14), m)
    im.paste(gradient(w, h, (236, 72, 153), PURPLE), (0, 0), m)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, outline=WHITE + (255,), width=5)
    im.alpha_composite(t, (30, 10))
    s = rich_text(sub, FONT_BLACK, 50, YELLOW, INK, 7)
    out = Image.new("RGBA", (im.width, im.height + s.height - 10), (0, 0, 0, 0))
    out.alpha_composite(im, (0, 0))
    out.alpha_composite(s, ((im.width - s.width) // 2, im.height - 10))
    return out


def pointer():
    lab = rich_text("Beg kuning 🛒", FONT_BLACK, 44, YELLOW, INK, 7)
    fin = rich_text("👇", FONT_BLACK, 130, (0, 0, 0)).rotate(28, resample=Image.BICUBIC, expand=True)
    out = Image.new("RGBA", (max(lab.width + 40, fin.width), lab.height + fin.height - 30), (0, 0, 0, 0))
    out.alpha_composite(lab, (40, 0))
    out.alpha_composite(fin, (0, lab.height - 30))
    return out


def header_pill(text):
    t = rich_text(text, FONT_BLACK, 36, WHITE, shadow=False)
    w, h = t.width + 70, t.height + 2
    im = Image.new("RGBA", (w + 10, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 8, w + 4, h + 8), h // 2, fill=(0, 0, 0, 80))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=INK + (225,))
    d.ellipse((24, h // 2 - 9, 42, h // 2 + 9), fill=(74, 222, 128, 255))  # online dot
    im.alpha_composite(t, (46, 0))
    return im


def build():
    A = {}
    A["chats"] = [(end, [(t0, side, bubble(txt, side)) for t0, side, txt in msgs]) for end, msgs in T.CHATS]
    A["header"] = header_pill(T.CHAT_HEADER)
    A["notifs"] = [(t0, notif_card(a, b)) for t0, a, b in T.NOTIFS["items"]]
    al = T.ALERT
    A["alert"] = notif_card(al["title"], al["body"], w=980, h=170, accent=RED, big=True)
    A["cta"] = cta_button(T.CTA["text"], T.CTA["sub"])
    A["pointer"] = pointer()
    A["react"] = {e: emoji_img(e.replace("️", ""), 76) for e in T.REACTIONS["emojis"]}
    return A


random.seed(5)
REACTS = []
for a0, a1 in T.REACTIONS["windows"]:
    t = a0
    while t < a1 - 0.4:
        REACTS.append(dict(t=t, e=random.choice(T.REACTIONS["emojis"]), x=random.randint(900, 1010),
                           sway=random.uniform(20, 45), ph=random.uniform(0, 6), dur=random.uniform(1.6, 2.2),
                           s=random.uniform(0.7, 1.1)))
        t += random.uniform(0.25, 0.5)


# ---------------- effects ----------------
def whip(arr, t):
    """Vertical whip-pan: content slides up with motion blur into each new section."""
    for p in T.PUNCHES[1:]:
        dt = t - p
        if -0.06 <= dt < 0.24:
            u = clamp((dt + 0.06) / 0.30)
            off = int(420 * (1 - ease_out(u)))
            if off < 4:
                return arr
            acc = np.zeros(arr.shape, np.float32)
            n = 6
            for k in range(n):
                acc += np.roll(arr, -(off * k // n) - off // 2, axis=0)
            return (acc / n).astype(np.uint8)
    return arr


def zoom_factor(t):
    starts = T.PUNCHES + [36.2]
    for a, b in zip(starts, starts[1:]):
        if a <= t < b:
            return 1.0 + 0.04 * ease_out((t - a) / (b - a))
    return 1.0


def draw_chat(frame, t, A):
    for gi, (end, msgs) in enumerate(A["chats"]):
        g0 = msgs[0][0]
        if not (g0 - 0.3 <= t < end):
            continue
        ga = clamp((end - t) / 0.2)
        place(frame, A["header"], 40 + A["header"].width / 2, 205, 1, ga * clamp((t - g0 + 0.3) / 0.25))
        shown = [(t0, s, im) for t0, s, im in msgs if t >= t0]
        if not shown:
            return
        # bottom-anchored stack; newest pushes older up
        y = T.CHAT_AREA["bottom"]
        newest_t0, _, newest = shown[-1]
        push = (newest.height + 14) * (1 - ease_out((t - newest_t0) / 0.28))
        y += push
        for idx in range(len(shown) - 1, -1, -1):
            t0, side, im = shown[idx]
            y -= im.height
            top = y
            y -= 14
            if top + im.height < T.CHAT_AREA["top"] - 60:
                break
            fade = clamp((top - (T.CHAT_AREA["top"] - 80)) / 120)
            dt = t - t0
            sc = max(0.01, back_out(dt / 0.28, 1.8)) if dt < 0.28 else 1.0
            cx = (W - 50 - im.width / 2) if side == "R" else (50 + im.width / 2)
            # scale from the tail corner
            ax = cx + (im.width / 2 if side == "R" else -im.width / 2)
            ay = top + im.height
            px = ax + (cx - ax) * sc
            py = ay + (top + im.height / 2 - ay) * sc
            place(frame, im, px, py, sc, fade * ga)
        return


def draw_notifs(frame, t, A):
    n = T.NOTIFS
    if not (n["items"][0][0] <= t < n["t1"]):
        return
    a = clamp((n["t1"] - t) / 0.2)
    for i, (t0, card) in enumerate(A["notifs"]):
        if t < t0:
            continue
        dt = t - t0
        k = ease_out(dt / 0.35)
        cy = n["y0"] + i * n["gap"] - (1 - k) * 260
        frosted(frame, card, W / 2, cy, a * clamp(dt / 0.15), 0.92 + 0.08 * back_out(dt / 0.35))


def draw_alert(frame, t, A):
    al = T.ALERT
    if not (al["t0"] <= t < al["t1"]):
        return
    dt, rem = t - al["t0"], al["t1"] - t
    a = clamp(dt / 0.12) * clamp(rem / 0.15)
    shake = 14 * math.sin(dt * 55) * math.exp(-dt * 3.5)
    sc = max(0.01, back_out(dt / 0.3))
    frosted(frame, A["alert"], W / 2 + shake, al["y"], a, sc if dt < 0.3 else 1.0)
    # stock bar draining
    bw, bh = 760, 34
    x0, y0 = W / 2 - bw / 2, al["y"] + 130
    lvl = 0.35 - 0.27 * ease_out(dt / 1.6)
    bar = Image.new("RGBA", (bw + 8, bh + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(bar)
    d.rounded_rectangle((4, 4, bw + 4, bh + 4), bh // 2, fill=(255, 255, 255, 200))
    blink = 255 if int(dt * 6) % 2 == 0 else 170
    d.rounded_rectangle((4, 4, 4 + max(bh, int(bw * lvl)), bh + 4), bh // 2, fill=RED + (blink,))
    lab = rich_text(f"Stok tinggal {int(lvl * 100)}%", FONT_BLACK, 34, WHITE, INK, 5, shadow=False)
    bar.alpha_composite(lab, (bw // 2 - lab.width // 2 + 4, bh - 4))
    place(frame, bar, W / 2 + shake, y0 + 30, 1, a)


def draw_cta(frame, t, A):
    c = T.CTA
    if not (c["t0"] <= t < c["t1"]):
        return
    dt = t - c["t0"]
    sc = back_out(dt / 0.3) if dt < 0.3 else 1.0 + 0.05 * math.sin((dt - 0.3) * 10)
    place(frame, A["cta"], W / 2, c["y"], max(0.01, sc), clamp((c["t1"] - t) / 0.1))


def draw_reacts(frame, t, A):
    for r in REACTS:
        dt = t - r["t"]
        if 0 <= dt < r["dur"]:
            u = dt / r["dur"]
            y = 1300 - u * 700
            x = r["x"] + math.sin(r["ph"] + dt * 4) * r["sway"]
            a = clamp(u / 0.12) * clamp((1 - u) / 0.35)
            place(frame, A["react"][r["e"]], x, y, r["s"] * (0.6 + 0.4 * clamp(u / 0.15)), a)


def draw_subs(frame, t):
    for start, end, words in T.SUBS:
        if not (start <= t < end):
            continue
        f = font(FONT_BLACK, 62)
        space = f.getlength(" ") + 6
        shown = [(w, wt) for w, wt in words if wt <= t + 0.02] or [words[0]]
        items = []
        for i, (w, wt) in enumerate(shown):
            nxt = words[i + 1][1] if i + 1 < len(words) else end
            items.append((w, wt <= t < nxt, f.getlength(w), t - wt))
        lines, cur, cw = [], [], 0
        allw = [f.getlength(w) for w, _ in words]  # wrap on full chunk so lines don't jump
        breaks, acc = set(), 0
        for i, wl in enumerate(allw):
            if acc and acc + space + wl > W - 150:
                breaks.add(i)
                acc = 0
            acc += (space if acc else 0) + wl
        for i, it in enumerate(items):
            if i in breaks:
                lines.append(cur)
                cur = []
            cur.append(it)
        lines.append(cur)
        nlines = len(breaks) + 1
        lh = 86
        layer = Image.new("RGBA", (W, lh * nlines + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        # centre each line using its full (final) width so words type in place
        full_lines, cur2 = [], []
        for i, wl in enumerate(allw):
            if i in breaks:
                full_lines.append(cur2)
                cur2 = []
            cur2.append(wl)
        full_lines.append(cur2)
        for li, ln in enumerate(lines):
            tw = sum(full_lines[li]) + space * (len(full_lines[li]) - 1)
            x = (W - tw) / 2
            y = 20 + li * lh + lh / 2
            for w, speaking, wl, age in ln:
                col = LIME if speaking else ((216, 180, 254) if w.lower() in T.KEYWORDS else WHITE)
                lift = 10 * (1 - ease_out(age / 0.12))
                d.text((x, y + lift), w, font=f, fill=col, anchor="lm", stroke_width=9, stroke_fill=INK)
                x += wl + space
        sh = layer.split()[3].filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.5))
        s = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        s.putalpha(sh)
        frame.alpha_composite(s, (6, int(1400 - layer.height / 2) + 8))
        frame.alpha_composite(layer, (0, int(1400 - layer.height / 2)))
        return


def compose(base, t, A):
    z = zoom_factor(t)
    if z > 1.001:
        cw, ch = W / z, H / z
        cy = min(max(H * 0.46, ch / 2), H - ch / 2)
        base = base.resize((W, H), Image.BILINEAR,
                           box=(W / 2 - cw / 2, cy - ch / 2, W / 2 + cw / 2, cy + ch / 2))
    frame = Image.fromarray(whip(np.asarray(base), t)).convert("RGBA")
    draw_reacts(frame, t, A)
    draw_chat(frame, t, A)
    draw_notifs(frame, t, A)
    draw_alert(frame, t, A)
    draw_cta(frame, t, A)
    for p0, p1 in T.POINTERS:
        if p0 <= t < p1:
            dt = t - p0
            b = abs(math.sin(dt * 7)) * 30
            ptr = A["pointer"]
            place(frame, ptr, 50 + ptr.width / 2 - b * 0.5, 1150 + b,
                  max(0.01, back_out(dt / 0.25)) if dt < 0.25 else 1.0, clamp((p1 - t) / 0.12))
    draw_subs(frame, t)
    return frame.convert("RGB")


def main():
    src, audio, out = sys.argv[1:4]
    preview = None
    if len(sys.argv) > 5 and sys.argv[4] == "--preview":
        preview = [float(x) for x in sys.argv[5].split(",")]
    A = build()
    vf = (f"fps={FPS},scale={W}:{H},eq=contrast=1.07:saturation=1.12:brightness=0.03,"
          "colorbalance=bs=0.03:bm=0.02:rh=0.02,unsharp=5:5:0.6,vignette=angle=PI/6")
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
