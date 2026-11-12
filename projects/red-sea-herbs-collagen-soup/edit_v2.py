#!/usr/bin/env python3
"""Video 2: short (~30s) FAB ad cut of the collagen soup recording.

Usage:  python3 edit_v2.py SOURCE.mp4 OUTPUT.mp4 [--preview]

SOURCE is the same full-quality joined recording used by edit.py.
Structure: problem hook -> 4 FAB blocks (Feature / Advantage / Benefit)
-> value math -> CTA (Action, Reason, Benefit, why now, cost of waiting).
Visual style differs from video 1: top progress bar, whip-blur transitions,
a stacked F/A/B card, a price-per-bowl counter and a pulsing CTA button.
Drawing helpers come from edit.py.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import edit as E
from edit import (W, H, FPS, YELLOW, RED, GREEN, FONT_BLACK, FONT_BOLD, font, emoji,
                  ease_out, ease_out_back, pop_scale, text_img, pill, card, paste_center, zoom,
                  gradient)

SP = 1.15
ORANGE = (255, 140, 0)
DARK = (18, 18, 18)

# (name, src_in, src_out, speed, audio_gain)
SEGMENTS = [
    ("hook", 103.0, 106.1, 1.0, 0.0),
    ("intro", 0.00, 5.46, SP, 1.0),
    ("items", 5.46, 8.05, SP, 1.0),
    ("soak", 14.40, 21.85, SP, 1.0),
    ("boil", 71.75, 75.45, SP, 1.0),
    ("stir", 96.05, 99.35, SP, 1.0),
    ("value", 99.60, 103.00, 1.0, 0.0),
    ("cta", 104.00, 110.40, 1.0, 0.0),
]


def build_timeline():
    t, out = 0.0, []
    for name, a, b, sp, g in SEGMENTS:
        d = (b - a) / sp
        out.append(dict(name=name, a=a, b=b, sp=sp, g=g, start=t, end=t + d))
        t += d
    return out, t


TL, TOTAL = build_timeline()
SEG = {s["name"]: s for s in TL}


def src2out(ts):
    for s in TL:
        if s["g"] > 0 and s["a"] - 0.05 <= ts <= s["b"] + 0.05:
            return s["start"] + (min(max(ts, s["a"]), s["b"]) - s["a"]) / s["sp"]
    return None


# ---------------------------------------------------------------- captions (smaller, lower)
def build_captions():
    words = []
    for seg in json.load(open(os.path.join(E.ASSETS, "transcript.json"))):
        for a, b, w in seg["words"]:
            w = w.strip()
            if w in E.FIX:
                w = E.FIX[w]
                if w is None:
                    continue
            oa, ob = src2out(a), src2out(b)
            if oa is None or ob is None:
                continue
            words.append([oa, max(ob, oa + 0.08), w])
    groups, cur = [], []
    for wd in words:
        cur.append(wd)
        if len(cur) >= 3 or len(" ".join(x[2] for x in cur)) > 16 or wd[2][-1] in ",.":
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    caps = []
    for i, g in enumerate(groups):
        end = g[-1][1] + 0.35
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0][0])
        seg_end = next(s["end"] for s in TL if s["start"] <= g[0][0] < s["end"])
        caps.append(dict(start=g[0][0], end=min(end, seg_end), words=g))
    return caps


CAPS = build_captions()


def draw_caption(base, t, y=1330):
    c = next((c for c in CAPS if c["start"] <= t < c["end"]), None)
    if not c:
        return
    size, space = 66, 26
    f = font(FONT_BLACK, size)
    toks = [w[2].upper().rstrip(",.") for w in c["words"]]
    widths = [f.getbbox(x, stroke_width=8)[2] for x in toks]
    total = sum(widths) + space * (len(toks) - 1)
    x = (W - total) // 2
    d = ImageDraw.Draw(base)
    for (a, b, _), tok, wdt in zip(c["words"], toks, widths):
        active = a <= t < b + 0.15
        if active:  # highlighted word sits on a yellow block
            d.rounded_rectangle((x - 10, y - 6, x + wdt + 10, y + size + 14), 14, fill=YELLOW)
            d.text((x, y), tok, font=f, fill=DARK)
        else:
            d.text((x, y), tok, font=f, fill=(255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
        x += wdt + space


# ---------------------------------------------------------------- FAB stack
TAG_COL = {"F": GREEN, "A": ORANGE, "B": RED}
TAG_NAME = {"F": "FEATURE", "A": "ADVANTAGE", "B": "BENEFIT"}


def fab_row(tag, txt, emo):
    """White card row: coloured letter badge + small label + main text."""
    badge_d = 92
    lab = text_img(TAG_NAME[tag], 26, TAG_COL[tag], path=FONT_BLACK)
    main = text_img(txt, 46, DARK, path=FONT_BLACK)
    e = emoji(emo, 50)
    w = 24 + badge_d + 22 + max(lab.width, main.width) + 20 + e.width + 30
    h = 124
    im = Image.new("RGBA", (w + 30, h + 30))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((12, 20, 12 + w, 20 + h), 30, fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, 12 + w, 12 + h), 30, fill=(255, 255, 255, 242))
    d.rounded_rectangle((12, 12, 24, 12 + h), 6, fill=TAG_COL[tag])
    bx, by = 12 + 24, 12 + (h - badge_d) // 2
    d.ellipse((bx, by, bx + badge_d, by + badge_d), fill=TAG_COL[tag])
    L = text_img(tag, 58, (255, 255, 255))
    im.alpha_composite(L, (bx + (badge_d - L.width) // 2, by + (badge_d - L.height) // 2))
    tx = bx + badge_d + 22
    im.alpha_composite(lab, (tx, 12 + 18))
    im.alpha_composite(main, (tx, 12 + 18 + lab.height + 10))
    im.alpha_composite(e, (12 + w - 30 - e.width, 12 + (h - e.height) // 2))
    return im


FABS = {  # segment(s) the block spans -> rows
    ("intro", "items"): [("F", "6 bahan premium dalam 1 pek", "🎁"),
                         ("A", "Tak payah cari satu-satu", "🛍️"),
                         ("B", "Jimat masa & duit", "💰")],
    ("soak",): [("F", "Bahan semulajadi, gred bersih", "🌿"),
                ("A", "Tanpa bahan pengawet", "🚫"),
                ("B", "Tenang hidang untuk keluarga", "👨‍👩‍👧")],
    ("boil",): [("F", "Rendam + rebus 45 minit", "⏱️"),
                ("A", "Tak perlu pandai masak", "👩‍🍳"),
                ("B", "Sesiapa pun boleh buat", "🙌")],
    ("stir",): [("F", "Tekstur berjeli & lembut", "🤤"),
                ("A", "Sedap panas atau sejuk", "🧊"),
                ("B", "Rahsia cantik dari dalam", "✨")],
}
FAB_IMGS = {k: [fab_row(*r) for r in rows] for k, rows in FABS.items()}


def draw_fab(base, t, segname):
    for names, rows in FAB_IMGS.items():
        if segname not in names:
            continue
        t0 = SEG[names[0]]["start"]
        t1 = SEG[names[-1]]["end"]
        span = t1 - t0
        gap = min(0.9, max(0.35, (span - 1.2) / 3))
        for i, im in enumerate(rows):
            ts = t0 + 0.15 + i * gap
            if t < ts:
                continue
            k = ease_out((t - ts) / 0.28)
            out = ease_out((t - (t1 - 0.18)) / 0.18) if t > t1 - 0.18 else 0
            x = 40 + im.width / 2 - (1 - k) * 900 - out * 1100
            paste_center(base, im, x, 330 + i * 150, 1.0)
            if i < 2 and t > ts + 0.2:  # small arrow between rows
                ar = text_img("↓", 40, (255, 255, 255), 5, path=FONT_BLACK)
                paste_center(base, ar, 92 - out * 1100, 330 + i * 150 + 80, 1.0)


# ---------------------------------------------------------------- assets
INGR_CARD = card(E.ingr, 560)
BOWL_CARD = card(E.bowl, 560)
BAG = card(E.promo.crop((300, 310, 800, 950)), 360, radius=26, border=8)
BAG_BIG = card(E.promo.crop((300, 310, 800, 950)), 420, radius=30, border=10)

HK1 = text_img("NAK DESSERT COLLAGEN", 70, (255, 255, 255), 11)
HK2 = text_img("TAPI TAK NAK", 84, (255, 255, 255), 11)
HK3 = text_img("BAYAR MAHAL?", 132, YELLOW, 14)
HK4 = pill("TENGOK NI", 56, RED, emo="👇", pad=(32, 16))
PRICE_TAG = pill("RM9.76 JE", 54, YELLOW, fg=DARK, emo="🔥", pad=(28, 14))

# CTA rows: Action / Reason / Benefit / Why now / If not
CTA_ROWS = [
    pill("Harga flash sale + FREE SHIPPING", 42, (255, 255, 255, 240), fg=DARK, emo="💸", pad=(26, 14)),
    pill("Minggu ni dah boleh hidang sendiri", 42, (255, 255, 255, 240), fg=DARK, emo="🍲", pad=(26, 14)),
]
URGENT = pill("Flash sale tak kekal!", 46, RED, emo="⏰", pad=(28, 14))
LOSS = text_img("Tunggu esok = harga naik semula", 44, (255, 255, 255), 7, path=FONT_BLACK)
BTN_TXT = text_img("TEKAN BEG KUNING", 64, DARK)


def cta_button(scale_pulse):
    e = emoji("🛒", 72)
    w = BTN_TXT.width + e.width + 100
    h = 140
    im = Image.new("RGBA", (w + 40, h + 40))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((20, 30, 20 + w, 30 + h), h // 2, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), h // 2, fill=YELLOW, outline=(255, 255, 255), width=6)
    im.alpha_composite(e, (20 + 40, 20 + (h - e.height) // 2))
    im.alpha_composite(BTN_TXT, (20 + 40 + e.width + 20, 20 + (h - BTN_TXT.height) // 2))
    return im


BTN = cta_button(1.0)
ARROW = emoji("👇", 110)


# ---------------------------------------------------------------- effects
def whip(fr, k, direction=1):
    """Horizontal motion-blur shift; k in [0,1] strength."""
    if k <= 0.02:
        return fr
    a = np.asarray(fr).astype(np.float32)
    shift = int(140 * k) * direction
    acc = np.zeros_like(a)
    n = 7
    for i in range(n):
        acc += np.roll(a, int(shift * (i / (n - 1) - 0.5)), axis=1)
    return Image.fromarray((acc / n).astype(np.uint8))


def progress_bar(base, t):
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, W, 14), fill=(0, 0, 0, 120))
    d.rectangle((0, 0, int(W * t / TOTAL), 14), fill=YELLOW)


TOP_GRAD = gradient(700, True, 160)
BOT_GRAD = gradient(600, False, 150)


def render_frame(fr, t):
    seg = next(s for s in TL if s["start"] <= t < s["end"] + 1e-6)
    lt = t - seg["start"]
    idx = TL.index(seg)

    # camera
    if seg["name"] == "hook":
        sh = 10 * math.sin(t * 40) * max(0, 1 - t / 0.6)  # shake on open
        fr = zoom(fr, 1.28 - 0.1 * ease_out(lt / 3.1), 0.55 + sh / 1000, 0.42)
    elif seg["name"] in ("value", "cta"):
        fr = zoom(fr, 1.12).filter(ImageFilter.GaussianBlur(16 if seg["name"] == "cta" else 10))
        fr = Image.blend(fr, Image.new("RGB", (W, H), (0, 0, 0)), 0.5)
    else:
        fr = zoom(fr, 1.0 + 0.05 * (1 - ease_out(lt / 0.35)))
    # whip transition across each cut (out of previous / into next)
    if idx > 0 and lt < 0.16:
        fr = whip(fr, 1 - lt / 0.16, 1 if idx % 2 else -1)
    if seg["end"] - t < 0.1 and idx < len(TL) - 1:
        fr = whip(fr, 1 - (seg["end"] - t) / 0.1, 1 if idx % 2 == 0 else -1)

    base = fr.convert("RGBA")
    if t < 0.1:
        base = Image.blend(base, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.85 * (1 - t / 0.1))

    if seg["name"] == "hook":
        base.alpha_composite(TOP_GRAD, (0, 0))
        paste_center(base, HK1, W / 2, 250, pop_scale(t, 0.05, 0.25))
        paste_center(base, HK2, W / 2, 360, pop_scale(t, 0.35, 0.25))
        paste_center(base, HK3, W / 2, 505, pop_scale(t, 0.65, 0.3) * (1 + 0.04 * math.sin(t * 10)), rot=-3)
        paste_center(base, BAG, 770, 1050, pop_scale(t, 1.3, 0.4), rot=7 + 2 * math.sin(t * 4))
        paste_center(base, PRICE_TAG, 770, 820, pop_scale(t, 1.6), rot=7)
        paste_center(base, HK4, 330, 1150, pop_scale(t, 2.0) * (1 + 0.05 * math.sin(t * 12)))
        progress_bar(base, t)
        return base

    if seg["name"] == "value":
        k = ease_out(lt / 1.4)
        per = 9.76 / 4 * k + 9.76 * (1 - k)
        paste_center(base, text_img("1 PEK RM9.76", 80, (255, 255, 255), 10), W / 2, 330, pop_scale(lt, 0.0))
        paste_center(base, text_img("= 4–6 MANGKUK", 80, (255, 255, 255), 10), W / 2, 450, pop_scale(lt, 0.25))
        paste_center(base, BOWL_CARD, W / 2, 870, pop_scale(lt, 0.35, 0.4) * 0.9, rot=-3)
        paste_center(base, text_img("CUMA", 60, (255, 255, 255), 8), W / 2, 1210, pop_scale(lt, 0.5))
        paste_center(base, text_img(f"RM{per:.2f}", 170, YELLOW, 14), W / 2, 1340,
                     pop_scale(lt, 0.5) * (1.06 if 1.4 < lt < 1.6 else 1.0), rot=-2)
        paste_center(base, text_img("SEMANGKUK!", 70, (255, 255, 255), 9), W / 2, 1480, pop_scale(lt, 1.5))
        progress_bar(base, t)
        return base

    if seg["name"] == "cta":
        pulse = 1 + 0.06 * math.sin(t * 9)
        paste_center(base, URGENT, W / 2, 230, pop_scale(lt, 0.0) * (1 + 0.04 * math.sin(t * 14)))
        paste_center(base, BAG_BIG, W / 2, 590, pop_scale(lt, 0.15, 0.4), rot=-3 + 2 * math.sin(t * 3))
        paste_center(base, text_img("RM9.76", 140, YELLOW, 13), W / 2, 905, pop_scale(lt, 0.45), rot=-2)
        for i, im in enumerate(CTA_ROWS):  # reason + benefit
            k = ease_out((lt - 0.8 - 0.3 * i) / 0.3)
            if k > 0:
                paste_center(base, im, W / 2 - (1 - k) * 900, 1050 + i * 100)
        paste_center(base, BTN, W / 2, 1290, pop_scale(lt, 1.5) * pulse)
        if lt > 1.9:
            paste_center(base, ARROW, W / 2, 1430 + 22 * abs(math.sin(t * 6)))
        if lt > 2.4:  # cost of waiting
            a = min(1, (lt - 2.4) / 0.3)
            paste_center(base, LOSS, W / 2, 1530, 1.0, alpha=a)
        progress_bar(base, t)
        return base

    base.alpha_composite(TOP_GRAD, (0, 0))
    base.alpha_composite(BOT_GRAD, (0, H - 600))
    draw_fab(base, t, seg["name"])

    if seg["name"] == "items":
        paste_center(base, INGR_CARD, W / 2, 960, pop_scale(lt, 0.0, 0.35), rot=3)
    if seg["name"] == "stir":
        paste_center(base, BOWL_CARD, 760, 990, pop_scale(lt, 0.3, 0.4) * 0.75, rot=5)

    draw_caption(base, t)
    progress_bar(base, t)
    return base


def main(src, dst):
    E.TL = TL  # reuse edit.py's low-memory segment cutter with this timeline
    tmp = dst + ".base.mp4"
    E.render_base(src, tmp)
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", tmp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", tmp,
                           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                           "-preset", "medium", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                           "-movflags", "+faststart", "-shortest", dst], stdin=subprocess.PIPE)
    i = 0
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = Image.frombuffer("RGB", (W, H), buf)
        wr.stdin.write(render_frame(fr, min(i / FPS, TOTAL - 1e-3)).convert("RGB").tobytes())
        i += 1
    wr.stdin.close()
    wr.wait()
    rd.wait()
    os.remove(tmp)
    print("done", dst, f"{TOTAL:.1f}s")


def preview(src, outdir):
    os.makedirs(outdir, exist_ok=True)
    times = [0.5, 1.5, 2.8]
    for s in TL[1:]:
        times += [s["start"] + 0.1, s["start"] + (s["end"] - s["start"]) * 0.5, s["end"] - 0.15]
    for tt in times:
        s = next(s for s in TL if s["start"] <= tt < s["end"])
        st = s["a"] + (tt - s["start"]) * s["sp"]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(st), "-i", src, "-frames:v", "1",
                              "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        fr = Image.frombuffer("RGB", (W, H), raw)
        render_frame(fr, tt).convert("RGB").resize((360, 640)).save(f"{outdir}/f_{tt:05.2f}.jpg")
    print("total", TOTAL)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[3] == "--preview":
        preview(sys.argv[1], sys.argv[2])
    else:
        main(sys.argv[1], sys.argv[2])
