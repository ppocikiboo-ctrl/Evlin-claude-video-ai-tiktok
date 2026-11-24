#!/usr/bin/env python3
"""Video 3: "3 SEBAB" listicle cut of the collagen soup recording (~31s).

Usage:  python3 edit_v3.py SOURCE.mp4 OUTPUT.mp4 [--preview]

Hook: split screen "DARI INI..." (raw ingredients) / "...JADI INI" (jelly
soup). Then three numbered reasons, each with its own overlay, and a
brand-coloured CTA end card with scrolling FLASH SALE tickers.
Visual language follows the pack: deep green + cream. Transitions are a
green diagonal wipe across every cut. Helpers come from edit.py.
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

import edit as E
from edit import (W, H, FPS, YELLOW, RED, FONT_BLACK, FONT_BOLD, font, emoji, ease_out,
                  pop_scale, text_img, pill, card, paste_center, zoom, gradient)

SP = 1.2
G = (20, 84, 58)        # pack green
G2 = (46, 140, 96)      # light green
CREAM = (252, 246, 228)
DARK = (22, 30, 26)

SEGMENTS = [  # (name, src_in, src_out, speed, audio_gain)
    ("hook", 103.0, 106.1, 1.0, 0.0),
    ("intro", 0.00, 5.46, SP, 1.0),
    ("r1a", 5.46, 8.05, SP, 1.0),
    ("r1b", 14.40, 21.85, SP, 1.0),
    ("r2a", 36.45, 40.35, SP, 1.0),
    ("r2b", 71.75, 75.45, SP, 1.0),
    ("r3", 96.05, 99.35, SP, 1.0),
    ("r3b", 99.60, 101.60, 1.0, 0.0),
    ("cta", 104.0, 110.4, 1.0, 0.0),
]
HOOK_TOP = (30.0, 33.1)  # source range of the raw-ingredient plate for the split screen


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


# ---------------------------------------------------------------- captions (cream box style)
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
    size, space, padx = 62, 18, 16
    f = font(FONT_BLACK, size)
    toks = [w[2].upper().rstrip(",.") for w in c["words"]]
    widths = [f.getbbox(x)[2] for x in toks]
    total = sum(widths) + (space + 2 * padx) * (len(toks) - 1) + 2 * padx
    x0 = (W - total) // 2
    k = pop_scale(t, c["start"], 0.18)
    lay = Image.new("RGBA", (W, 140))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 - 18, 8, x0 + total + 18, 8 + size + 40), 26, fill=CREAM + (245,))
    x = x0
    for (a, b, _), tok, wdt in zip(c["words"], toks, widths):
        if a <= t < b + 0.15:
            d.rounded_rectangle((x, 16, x + wdt + 2 * padx, 16 + size + 24), 18, fill=G)
            d.text((x + padx, 24), tok, font=f, fill=(255, 255, 255))
        else:
            d.text((x + padx, 24), tok, font=f, fill=G)
        x += wdt + 2 * padx + space
    paste_center(base, lay, W / 2, y + 60 + (1 - k) * 30, 0.85 + 0.15 * k)


# ---------------------------------------------------------------- building blocks
def number_badge(n):
    d = 190
    im = Image.new("RGBA", (d + 30, d + 30))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).ellipse((15, 25, 15 + d, 25 + d), fill=(0, 0, 0, 140))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    dr = ImageDraw.Draw(im)
    dr.ellipse((15, 15, 15 + d, 15 + d), fill=YELLOW, outline=(255, 255, 255), width=8)
    tx = text_img(f"#{n}", 104, G)
    im.alpha_composite(tx, (15 + (d - tx.width) // 2, 15 + (d - tx.height) // 2))
    return im


def title_card(title, sub):
    t1 = text_img(title, 52, (255, 255, 255))
    t2 = text_img(sub, 36, CREAM, path=FONT_BOLD)
    w = max(t1.width, t2.width) + 70
    h = t1.height + t2.height + 60
    im = Image.new("RGBA", (w + 30, h + 30))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((15, 25, 15 + w, 25 + h), 30, fill=(0, 0, 0, 130))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((15, 15, 15 + w, 15 + h), 30, fill=G)
    d.rounded_rectangle((15, 15 + h - 12, 15 + w, 15 + h), 6, fill=YELLOW)
    im.alpha_composite(t1, (15 + 35, 15 + 22))
    im.alpha_composite(t2, (15 + 35, 15 + 22 + t1.height + 12))
    return im


REASONS = {
    1: (("r1a", "r1b"), title_card("SEMUA BAHAN DAH ADA", "6 bahan premium dalam 1 pek")),
    2: (("r2a", "r2b"), title_card("SENANG GILA NAK MASAK", "Rendam, rebus, siap!")),
    3: (("r3", "r3b"), title_card("JIMAT & CUKUP SEKELUARGA", "1 pek = 4–6 mangkuk")),
}
BADGES = {n: number_badge(n) for n in REASONS}

INGR = card(E.ingr, 600)
BOWL = card(E.bowl, 520)
PROMO = card(E.promo, 760, radius=34, border=10)
ICHIPS = [  # (label, emoji, src word time) -> pops on the word
    ("Sarang Burung Salji", "🤍", 15.20),
    ("Biji Teratai Salji", "🌸", 17.64),
    ("Getah Peach", "🍑", 19.90),
]
ICHIP_IMGS = [(pill(a, 46, CREAM, fg=G, emo=e, pad=(26, 14)), src2out(ts)) for a, e, ts in ICHIPS]
CHECKS = [("Rendam 24 jam", "r2a", 0.3), ("Didih 1.5L air", "r2a", 1.3), ("Rebus 45 minit", "r2b", 0.9),
          ("Siap dihidang!", "r2b", 2.0)]


def check_row(txt, done):
    box = Image.new("RGBA", (64, 64))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle((2, 2, 62, 62), 14, fill=G2 if done else (255, 255, 255), outline=G, width=5)
    if done:
        d.line((14, 33, 27, 46, 50, 18), fill=(255, 255, 255), width=9, joint="curve")
    tx = text_img(txt, 46, DARK if done else (120, 120, 120))
    w = 64 + 20 + tx.width + 60
    im = Image.new("RGBA", (w, 100))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, 99), 26, fill=CREAM + (240,))
    im.alpha_composite(box, (24, 18))
    im.alpha_composite(tx, (24 + 64 + 20, (100 - tx.height) // 2))
    return im


CHECK_IMGS = [(check_row(t, False), check_row(t, True), SEG[s]["start"] + dt) for t, s, dt in CHECKS]

# hook
TOPLBL = pill("DARI INI...", 62, (255, 255, 255), fg=G, pad=(34, 16))
BOTLBL = pill("...JADI INI!", 62, YELLOW, fg=G, emo="🤤", pad=(34, 16))
STAMP = pill("RM9.76 JE!", 70, RED, emo="🔥", pad=(34, 18))
INTRO1 = text_img("3 SEBAB", 150, YELLOW, 14)
INTRO2 = text_img("KAMU WAJIB CUBA", 66, (255, 255, 255), 9)
INTRO3 = text_img("SUP COLLAGEN NI", 66, (255, 255, 255), 9)
DOWN = emoji("👇", 90)

# CTA
TICK_TXT = "  ⚡ FLASH SALE  •  FREE SHIPPING  •  RM9.76  •"


def ticker_strip(bg, fg):
    seg = text_img(TICK_TXT.replace("⚡ ", ""), 40, fg)
    bolt = emoji("⚡", 40)
    unit = Image.new("RGBA", (seg.width + bolt.width + 10, 70))
    unit.alpha_composite(bolt, (10, (70 - bolt.height) // 2))
    unit.alpha_composite(seg, (bolt.width + 14, (70 - seg.height) // 2))
    strip = Image.new("RGBA", (W + unit.width * 2, 70), bg)
    x = 0
    while x < strip.width:
        strip.alpha_composite(unit, (x, 0))
        x += unit.width
    return strip, unit.width


TICK1 = ticker_strip(G, (255, 255, 255))
TICK2 = ticker_strip(YELLOW, G)
CTA_LINES = [  # (tag, text, emoji)
    ("SEBAB", "Harga flash sale + free shipping", "💸"),
    ("UNTUNG", "Dessert collagen cukup sekeluarga", "🍲"),
]
CTA_IMGS = []
for tag, txt, e in CTA_LINES:
    tg = pill(tag, 30, G, pad=(16, 8), shadow=False)
    row = pill(txt, 42, (255, 255, 255), fg=DARK, emo=e, pad=(26, 14))
    im = Image.new("RGBA", (row.width, row.height + tg.height - 30))
    im.alpha_composite(row, (0, tg.height - 30))
    im.alpha_composite(tg, (30, 0))
    CTA_IMGS.append(im)
LOSS = pill("Flash sale tamat = harga naik semula", 38, (60, 60, 60), emo="⚠️", pad=(24, 12))


def cta_button():
    e = emoji("🛒", 70)
    tx = text_img("TEKAN BEG KUNING", 62, G)
    w, h = tx.width + e.width + 100, 140
    im = Image.new("RGBA", (w + 40, h + 40))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((20, 30, 20 + w, 30 + h), h // 2, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), h // 2, fill=YELLOW, outline=G, width=8)
    im.alpha_composite(e, (60, 20 + (h - e.height) // 2))
    im.alpha_composite(tx, (60 + e.width + 20, 20 + (h - tx.height) // 2))
    return im


BTN = cta_button()
ARROW = emoji("👇", 100)


def cta_bg():
    bg = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(bg)
    for i in range(-H, W, 90):  # soft diagonal stripes
        d.line((i, 0, i + H, H), fill=(244, 234, 206, 255), width=34)
    return bg


CTA_BG = cta_bg()
TOP_GRAD = gradient(560, True, 150)
BOT_GRAD = gradient(560, False, 140)


# ---------------------------------------------------------------- effects
def wipe(base, t):
    """Green diagonal band sweeping across each cut (0.28s centred on it)."""
    for s in TL[1:]:
        dt = t - s["start"]
        if -0.14 <= dt <= 0.14:
            k = (dt + 0.14) / 0.28
            x = -700 + k * (W + 1400)
            lay = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(lay)
            d.polygon([(x - 260, 0), (x + 120, 0), (x + 120 - 500, H), (x - 260 - 500, H)], fill=G + (255,))
            d.polygon([(x + 120, 0), (x + 170, 0), (x + 170 - 500, H), (x + 120 - 500, H)], fill=YELLOW + (255,))
            base.alpha_composite(lay)
            return


def reason_of(name):
    for n, (names, _) in REASONS.items():
        if name in names:
            return n
    return None


HOOK_FRAMES = []


def load_hook_top(src):
    a, b = HOOK_TOP
    n = int(round((b - a) * FPS))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", src,
                          "-vf", f"scale={W}:{H},crop={W}:{H // 2}:0:{H // 4},fps={FPS}",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    sz = W * (H // 2) * 3
    HOOK_FRAMES.extend(Image.frombuffer("RGB", (W, H // 2), raw[i * sz:(i + 1) * sz])
                       for i in range(len(raw) // sz))


def render_frame(fr, t):
    seg = next(s for s in TL if s["start"] <= t < s["end"] + 1e-6)
    lt = t - seg["start"]
    name = seg["name"]

    if name == "hook":
        top = HOOK_FRAMES[min(int(lt * FPS), len(HOOK_FRAMES) - 1)]
        bot = zoom(fr, 1.2 - 0.08 * ease_out(lt / 3.1), 0.55, 0.42)
        bot = bot.crop((0, H // 4, W, H // 4 + H // 2))
        base = Image.new("RGBA", (W, H))
        # top slides down, bottom slides up into place
        ky = ease_out(lt / 0.35)
        base.paste(top, (0, int(-H // 2 * (1 - ky))))
        kb = ease_out((lt - 0.2) / 0.35)
        if kb > 0:
            base.paste(bot, (0, int(H // 2 + H // 2 * (1 - kb))))
        d = ImageDraw.Draw(base)
        d.rectangle((0, H // 2 - 7, int(W * ky), H // 2 + 7), fill=YELLOW)
        paste_center(base, TOPLBL, W / 2, 200, pop_scale(lt, 0.2))
        paste_center(base, BOTLBL, W / 2, H // 2 + 170, pop_scale(lt, 0.7))
        paste_center(base, STAMP, W / 2, H // 2, pop_scale(lt, 1.7, 0.3) * (1 + 0.05 * math.sin(t * 11)),
                     rot=-8)
        if t < 0.1:
            base = Image.blend(base, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.8 * (1 - t / 0.1))
        return base

    if name == "cta":
        base = CTA_BG.copy()
        off1 = int((t * 160) % TICK1[1])
        base.alpha_composite(TICK1[0].crop((off1, 0, off1 + W, 70)), (0, 70))
        off2 = int((t * 160) % TICK2[1])
        x2 = (TICK2[1] - off2) % TICK2[1]
        base.alpha_composite(TICK2[0].crop((x2, 0, x2 + W, 70)),
                             (0, H - 300))
        paste_center(base, PROMO, W / 2, 620, pop_scale(lt, 0.05, 0.4), rot=-2 + 1.5 * math.sin(t * 3))
        for i, im in enumerate(CTA_IMGS):
            k = ease_out((lt - 0.6 - 0.3 * i) / 0.3)
            if k > 0:
                paste_center(base, im, W / 2 + (1 - k) * (900 if i % 2 else -900), 1095 + i * 112)
        paste_center(base, BTN, W / 2, 1335, pop_scale(lt, 1.3) * (1 + 0.06 * math.sin(t * 9)))
        if lt > 1.7:
            paste_center(base, ARROW, W / 2, 1455 + 16 * abs(math.sin(t * 6)))
        if lt > 2.2:
            paste_center(base, LOSS, W / 2, 1560, 1.0, alpha=min(1, (lt - 2.2) / 0.3))
        wipe(base, t)
        return base

    fr = zoom(fr, 1.0 + 0.05 * (1 - ease_out(lt / 0.35)))
    base = fr.convert("RGBA")
    base.alpha_composite(TOP_GRAD, (0, 0))
    base.alpha_composite(BOT_GRAD, (0, H - 560))

    if name == "intro":
        paste_center(base, INTRO1, W / 2, 330, pop_scale(lt, 0.1, 0.35), rot=-3)
        paste_center(base, INTRO2, W / 2, 470, pop_scale(lt, 0.35))
        paste_center(base, INTRO3, W / 2, 560, pop_scale(lt, 0.55))
        if lt > 0.9:
            paste_center(base, DOWN, W / 2, 680 + 18 * abs(math.sin(t * 6)))

    n = reason_of(name)
    if n:
        names, tc = REASONS[n]
        t0 = SEG[names[0]]["start"]
        paste_center(base, tc, min(215 + tc.width / 2, W - 20 - tc.width / 2), 300, pop_scale(t, t0 + 0.15, 0.35))
        sp = 1 - ease_out((t - t0 - 0.05) / 0.4)
        paste_center(base, BADGES[n], 125, 300, pop_scale(t, t0 + 0.05, 0.4), rot=360 * sp)

    if name == "r1a":
        paste_center(base, INGR, W / 2, 880, pop_scale(lt, 0.3, 0.4), rot=3)
    if name == "r1b":
        for i, (im, t0) in enumerate(ICHIP_IMGS):
            if t0 is not None and t >= t0:
                k = ease_out((t - t0) / 0.3)
                paste_center(base, im, 60 + im.width / 2 - (1 - k) * 800, 520 + i * 110)
    if name in ("r2a", "r2b"):
        for i, (off, on, tdone) in enumerate(CHECK_IMGS):
            k = ease_out((t - SEG["r2a"]["start"] - 0.2 - 0.1 * i) / 0.3)
            im = on if t >= tdone else off
            sc = 1.08 if 0 <= t - tdone < 0.12 else 1.0
            paste_center(base, im, 60 + im.width / 2 - (1 - k) * 800, 540 + i * 118, sc)
    if name == "r3":
        paste_center(base, BOWL, 740, 830, pop_scale(lt, 0.25, 0.4) * 0.9, rot=4)
    if name == "r3b":
        base = Image.blend(base, Image.new("RGBA", (W, H), (0, 0, 0, 255)), 0.35)
        paste_center(base, BOWL, 740, 830, 0.9, rot=4)
        paste_center(base, text_img("≈ RM2.44", 150, YELLOW, 14), W / 2, 1180, pop_scale(lt, 0.1), rot=-3)
        paste_center(base, text_img("SEMANGKUK!", 72, (255, 255, 255), 9), W / 2, 1320, pop_scale(lt, 0.35))

    draw_caption(base, t)
    wipe(base, t)
    return base


def main(src, dst):
    load_hook_top(src)
    E.TL = TL
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
    load_hook_top(src)
    os.makedirs(outdir, exist_ok=True)
    times = [0.4, 1.2, 2.5]
    for s in TL[1:]:
        times += [s["start"] + 0.03, s["start"] + (s["end"] - s["start"]) * 0.6, s["end"] - 0.1]
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
