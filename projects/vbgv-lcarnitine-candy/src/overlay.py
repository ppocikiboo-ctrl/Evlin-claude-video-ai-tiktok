"""Composite the motion graphics over the graded base clip.

    python overlay.py                 # full render -> build/video.mp4
    python overlay.py --stills 1,4.5  # preview PNGs at those seconds -> build/stills/
"""
import argparse
import math
import random
import subprocess

import numpy as np
from PIL import Image

import gfx
from config import (BUILD, CUTS, DEEP_PURPLE, FONT_BLACK, FONT_BOLD, FONT_SEMI, FONT_XBOLD, FPS,
                    FRAMES, GOLD, GOLD_HI, H, LAVENDER, PURPLE, W, WHITE)
from gfx import (clamp, ease_in_out, ease_out_back, ease_out_cubic, place, text_layer, twinkle,
                 window)

BEAT = 0.5
GLOW_PURPLE = (170, 90, 255)
GLOW_GOLD = (255, 200, 110)


# ------------------------------------------------------------------ sprites

def build_sprites():
    S = {}
    # scene 1 - hook
    S["hook"] = text_layer([[("@weary", None), ("BOSAN PENAMPILAN", WHITE)],
                            [("TAK BERUBAH", "gold"), ("?", WHITE)]],
                           FONT_BLACK, 104, max_width=940, glow=GLOW_PURPLE, glow_radius=22)
    # scene 2 - problem
    S["prob1"] = text_layer([[("@fries", None), ("SUKA MAKAN", LAVENDER), (", TAPI", WHITE)]],
                            FONT_BLACK, 92, max_width=900, glow=GLOW_PURPLE)
    S["prob2"] = text_layer([[("RISAU NAK ", WHITE), ("JAGA BADAN", "gold"), ("?", WHITE)]],
                            FONT_BLACK, 92, max_width=900, glow=GLOW_PURPLE)
    # scene 3 - reveal
    S["reveal"] = text_layer([[("@sparkles", None), ("KENALI ", WHITE), ("VBGV", "gold"), ("@sparkles", None)]],
                             FONT_BLACK, 118, max_width=940, glow=GLOW_GOLD, glow_radius=24, glow_strength=0.7)
    S["reveal_sub"] = gfx.pill([[("VBGV L-CARNITINE CANDY", WHITE)]], FONT_XBOLD, 44,
                               text_kwargs=dict(stroke=0, glow=None, shadow=0.0, tracking=3))
    # scene 4 - highlights
    S["hl_head"] = text_layer([[("@heart", None), ("RUTIN PENJAGAAN BADAN", WHITE)]],
                              FONT_BLACK, 76, max_width=920, glow=GLOW_PURPLE)
    S["cards"] = [gfx.card("sparkles", "L-CARNITINE 90%*"),
                  gfx.card("heart", "MUDAH DIBAWA"),
                  gfx.card("blossom", "MUDAH DIJADIKAN RUTIN")]
    S["hl_foot"] = text_layer([[("*Berdasarkan maklumat pada label produk.", (235, 225, 255))]],
                              FONT_SEMI, 30, max_width=820, stroke=2, glow=None, shadow=0.8)
    # scene 5 - lifestyle
    S["life"] = text_layer([[("UNTUK YANG SIBUK", WHITE)], [("SETIAP HARI ", "gold"), ("@sparkles", None)]],
                           FONT_BLACK, 98, max_width=920, glow=GLOW_PURPLE)
    S["bubbles"] = [gfx.pill([[("@briefcase", None), ("Kerja", WHITE)]], FONT_BOLD, 46, outline="lavender"),
                    gfx.pill([[("@sun", None), ("Aktiviti harian", WHITE)]], FONT_BOLD, 46, outline="lavender"),
                    gfx.pill([[("@blossom", None), ("Rutin penjagaan diri", WHITE)]], FONT_BOLD, 46, outline="lavender")]
    # scene 6 - product information
    info_line = [("@heart", None), ("1", "gold"), (" PEK = ", WHITE), ("5", "gold"), (" BIJI", WHITE)]
    big = text_layer([info_line], FONT_BLACK, 112, max_width=760, glow=None, stroke=0, shadow=0.0)
    hi_line = [("@heart", "hide"), ("1", "gold"), (" PEK = ", None), ("5", "gold"), (" BIJI", None)]
    S["info_hi"] = text_layer([hi_line], FONT_BLACK, 112, max_width=760, glow=GLOW_GOLD,
                              glow_radius=20, glow_strength=1.0, stroke=0, shadow=0.0)
    sub = text_layer([[("Maklumat produk: L-Carnitine 90%*", WHITE)]], FONT_SEMI, 44, max_width=760,
                     glow=None, stroke=0, shadow=0.0)
    foot = text_layer([[("*Sahkan kandungan melalui label rasmi.", (215, 200, 250))]], FONT_SEMI, 30,
                      max_width=760, glow=None, stroke=0, shadow=0.0)
    pw, ph = 860, 360
    panel, pad = gfx.panel(pw, ph, radius=44, fill=(48, 14, 96, 165))
    for layer, y in ((big, 40), (sub, 196), (foot, 268)):
        panel.alpha_composite(layer, (pad + (pw - layer.size[0]) // 2, pad + y - (layer.size[1] - _ink_h(layer)) // 2))
    S["info_panel"] = panel
    bx, by = pad + (pw - big.size[0]) // 2, pad + 40 - (big.size[1] - _ink_h(big)) // 2
    S["info_big_center"] = (bx + big.size[0] / 2, by + big.size[1] / 2)
    # scene 7 - self-care
    S["care1"] = text_layer([[("JAGA BADAN,", WHITE)]], FONT_BLACK, 104, max_width=900, glow=GLOW_PURPLE)
    S["care2"] = text_layer([[("JAGA ", WHITE), ("KEYAKINAN", "gold"), ("@heart", None)]],
                            FONT_BLACK, 104, max_width=900, glow=GLOW_PURPLE)
    S["care_sub"] = gfx.pill([[("Pemakanan seimbang dan gaya hidup", WHITE)], [("aktif tetap penting.", WHITE)]],
                             FONT_SEMI, 40, fill=(30, 8, 64, 150), outline="lavender")
    # scene 8 - CTA
    S["cta"] = text_layer([[("@heart", None), ("NAK KENAL ", WHITE), ("VBGV", "gold"), ("?", WHITE)]],
                          FONT_BLACK, 112, max_width=940, glow=GLOW_PURPLE, glow_radius=22)
    S["cta_btn"] = gfx.pill([[("TEKAN BEG KUNING", "gold")], [("UNTUK INFO LANJUT ", WHITE), ("@bag", None)]],
                            FONT_BLACK, 58, pad_x=60, pad_y=32, fill=(76, 22, 150, 235),
                            text_kwargs=dict(stroke=0, glow=None, shadow=0.0))
    S["arrow"] = gfx.icon("arrow", 64)
    return S


def _ink_h(img):
    b = img.getbbox()
    return b[3] - b[1] if b else img.size[1]


# ------------------------------------------------------------------ camera

def camera(t):
    """Return (scale, focus_x, focus_y, shake_x, shake_y) for the footage."""
    if t < 3:
        s = 1.20 - 0.12 * ease_out_cubic(t / 0.35) + 0.03 * t / 3
        fx, fy = 580, 760
    elif t < 6:
        s, fx, fy = 1.04 + 0.06 * (t - 3) / 3, 600, 800
    elif t < 9:
        s, fx, fy = 1.00 + 0.16 * ease_in_out((t - 6) / 3), 600, 820
    elif t < 13:
        s, fx, fy = 1.05 + 0.03 * (t - 9) / 4, 640, 1100
    elif t < 17:
        s, fx, fy = 1.02 + 0.06 * (t - 13) / 4, 560, 900
    elif t < 21:
        s, fx, fy = 1.06 + 0.08 * (t - 17) / 4, 660, 1150
    elif t < 25:
        s, fx, fy = 1.03 + 0.06 * (t - 21) / 4, 580, 860
    else:
        s, fx, fy = 1.10 + 0.16 * ease_in_out((t - 25) / 5), 620, 780
    # punch-in at every cut
    for c in CUTS:
        if c <= t < c + 0.25:
            s *= 1 + 0.07 * (1 - (t - c) / 0.25) ** 2
    sx = sy = 0.0
    if t < 0.6:  # opening bass-hit screen shake
        amp = 16 * (1 - t / 0.6) ** 2
        sx, sy = amp * math.sin(t * 95), amp * math.cos(t * 77)
    elif 25 <= t < 25.35:
        amp = 9 * (1 - (t - 25) / 0.35) ** 2
        sx, sy = amp * math.sin(t * 90), amp * math.cos(t * 70)
    return s, fx, fy, sx, sy


def apply_camera(img, t):
    s, fx, fy, sx, sy = camera(t)
    a = 1 / s
    c = fx * (1 - a) - sx
    f = fy * (1 - a) - sy
    return img.transform((W, H), Image.AFFINE, (a, 0, c, 0, a, f), Image.BICUBIC)


# ------------------------------------------------------------------ frame

TOP_SHADE = gfx.vgrad(1.0, 0.0, 0, 820)
BOTTOM_SHADE = gfx.vgrad(0.0, 1.0, 1300, H)
VIGNETTE = 1 - gfx.radial(540, 900, 900, 1300)
GLOW_HOOK = gfx.radial(540, 470, 620, 360)
GLOW_PACK = gfx.radial(600, 830, 430, 520)
GLOW_CTA = gfx.radial(540, 340, 640, 320)
RAYS_ORIGIN = (120, -120)


def beat_pulse(t, sharp=6):
    return math.exp(-((t % BEAT) / BEAT) * sharp)


def render_frame(base, t, S, P):
    cam = apply_camera(base, t)
    arr = np.asarray(cam, np.float32)

    # grade-friendly shading for legibility + brand tint
    arr = gfx.darken(arr, TOP_SHADE, (24, 6, 52), 0.62)
    arr = gfx.darken(arr, BOTTOM_SHADE, (24, 6, 52), 0.48 + (0.2 if t >= 25 else 0))
    arr = gfx.darken(arr, VIGNETTE, (14, 4, 30), 0.35)

    if t < 3:
        arr = gfx.add_light(arr, GLOW_HOOK, GLOW_PURPLE, 0.55 + 0.25 * beat_pulse(t))
    if 6 <= t < 9:
        k = window(t, 6, 9, 0.5, 0.3)
        arr = gfx.add_light(arr, GLOW_PACK, (150, 90, 255), 0.55 * k)
        if 6.4 <= t < 7.6:
            pos = -300 + (t - 6.4) / 1.2 * 1900
            arr = gfx.add_light(arr, gfx.sweep(pos, -28, 110), GOLD_HI, 0.55)
    if 21 <= t < 25:
        k = window(t, 21, 25, 0.6, 0.3)
        arr = gfx.add_light(arr, gfx.rays(*RAYS_ORIGIN, phase=t * 0.35), (215, 190, 255), 0.42 * k)
    if t >= 25:
        k = clamp((t - 25) / 0.4)
        arr = gfx.add_light(arr, GLOW_CTA, GLOW_PURPLE, (0.45 + 0.25 * beat_pulse(t)) * k)
        if 25.2 <= t < 26.4:
            pos = -300 + (t - 25.2) / 1.2 * 1900
            arr = gfx.add_light(arr, gfx.sweep(pos, -28, 120), GOLD_HI, 0.45)
    # cut flash
    for c in CUTS:
        if c <= t < c + 0.2:
            f = 0.32 * (1 - (t - c) / 0.2) ** 2
            arr = arr * (1 - f) + np.array((240, 228, 255), np.float32) * f
    if t < 1 / FPS * 2:  # opening impact flash
        arr = arr * 0.8 + np.array((245, 230, 255), np.float32) * 0.2

    canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    # ambient particles
    amount = 0.35
    if 6 <= t < 9 or t >= 25:
        amount = 0.85
    elif 21 <= t < 25:
        amount = 0.6
    P.draw(canvas, t, amount)

    scene_text(canvas, t, S)
    return canvas.convert("RGB")


def scene_text(cv, t, S):
    # 1. hook ---------------------------------------------------------
    if t < 3:
        p = t / 0.3
        sc = 0.8 + 0.2 * ease_out_back(p, 2.6)
        a = clamp((3 - t) / 0.18)  # visible from frame 0 so the cover frame carries the hook
        if t > 2.82:
            sc *= 1 + 0.2 * (t - 2.82) / 0.18
        sc *= 1 + 0.025 * beat_pulse(t)
        place(cv, S["hook"], 540, 470, scale=sc, alpha=a)
        twinkle(cv, t, [(250, 560), (830, 520), (700, 380), (170, 380)], 0.4, size=70, color="gold")

    # 2. problem ------------------------------------------------------
    if 3 <= t < 6:
        for i, (key, y) in enumerate((("prob1", 400), ("prob2", 520))):
            lt = t - 3.05 - i * 0.15
            if lt < 0:
                continue
            p = ease_out_cubic(lt / 0.45)
            x = -560 + (540 + 560) * p
            vel = (1 - clamp(lt / 0.45)) ** 2 * 140
            a = clamp(lt / 0.15) * clamp((6 - t) / 0.2)
            place(cv, S[key], x, y, alpha=a, blur_dx=vel)
        twinkle(cv, t, [(210, 330), (880, 360), (620, 610), (330, 610), (940, 560)], 3.4, size=54)

    # 3. reveal -------------------------------------------------------
    if 6 <= t < 9:
        lt = t - 6.05
        sc = 0.55 + 0.45 * ease_out_back(lt / 0.5)
        a = clamp(lt / 0.2) * clamp((9 - t) / 0.2)
        place(cv, S["reveal"], 540, 330, scale=sc, alpha=a)
        st = t - 6.6
        if st > 0:
            place(cv, S["reveal_sub"], 540, 480 + 30 * (1 - ease_out_cubic(st / 0.5)),
                  alpha=clamp(st / 0.35) * clamp((9 - t) / 0.2))
        twinkle(cv, t, [(300, 700), (860, 760), (380, 1240), (820, 1200), (560, 640)], 6.3, size=66, color="gold")

    # 4. highlights ---------------------------------------------------
    if 9 <= t < 13:
        out = clamp((13 - t) / 0.2)
        lt = t - 9.05
        place(cv, S["hl_head"], 540, 280 + 30 * (1 - ease_out_cubic(lt / 0.4)), alpha=clamp(lt / 0.25) * out)
        for i, cd in enumerate(S["cards"]):
            ct = t - (9.5 + 0.5 * i)  # one card per beat
            if ct < 0:
                continue
            sc = 0.4 + 0.6 * ease_out_back(ct / 0.32, 2.2)
            place(cv, cd, 505, 440 + i * 150, scale=sc, alpha=clamp(ct / 0.12) * out)
        ft = t - 11.0
        if ft > 0:
            place(cv, S["hl_foot"], 505, 870, alpha=clamp(ft / 0.4) * out * 0.95)

    # 5. lifestyle ----------------------------------------------------
    if 13 <= t < 17:
        out = clamp((17 - t) / 0.2)
        lt = t - 13.05
        place(cv, S["life"], 540, 330 + 70 * (1 - ease_out_cubic(lt / 0.5)), alpha=clamp(lt / 0.3) * out)
        spots = ((360, 1250), (640, 1370), (460, 1490))
        for i, (bub, (x, y)) in enumerate(zip(S["bubbles"], spots)):
            bt = t - (13.6 + 0.5 * i)
            if bt < 0:
                continue
            rise = 90 * (1 - ease_out_cubic(bt / 0.7))
            bob = 10 * math.sin(t * 2.4 + i * 1.7)
            sway = 6 * math.sin(t * 1.6 + i)
            place(cv, bub, x + sway, y + rise + bob, alpha=clamp(bt / 0.4) * out,
                  rotate=1.5 * math.sin(t * 1.9 + i))

    # 6. product information -----------------------------------------
    if 17 <= t < 21:
        out = clamp((21 - t) / 0.2)
        lt = t - 17.05
        sc = 0.93 + 0.07 * ease_out_cubic(lt / 0.6) + 0.025 * (t - 17) / 4
        cy = 470
        a = clamp(lt / 0.3) * out
        place(cv, S["info_panel"], 540, cy, scale=sc, alpha=a)
        # pulsing gold glow around the numbers, aligned with the panel text
        pw, ph = S["info_panel"].size
        bx, by = S["info_big_center"]
        hx = 540 + (bx - pw / 2) * sc
        hy = cy + (by - ph / 2) * sc
        hi = S["info_hi"]
        place(cv, hi, hx, hy, scale=sc, alpha=a * (0.55 + 0.45 * beat_pulse(t, 4)))

    # 7. self-care ----------------------------------------------------
    if 21 <= t < 25:
        out = clamp((25 - t) / 0.2)
        for i, (key, y) in enumerate((("care1", 300), ("care2", 420))):
            lt = t - 21.15 - i * 0.35
            if lt < 0:
                continue
            e = ease_out_cubic(lt / 0.7)
            place(cv, S[key], 540, y + 40 * (1 - e), scale=1.06 - 0.06 * e, alpha=clamp(lt / 0.5) * out)
        st = t - 22.2
        if st > 0:
            place(cv, S["care_sub"], 520, 1400 + 30 * (1 - ease_out_cubic(st / 0.6)), alpha=clamp(st / 0.5) * out)
        twinkle(cv, t, [(240, 560), (840, 250), (900, 520), (180, 220)], 21.6, size=50)

    # 8. CTA ----------------------------------------------------------
    if t >= 25:
        lt = t - 25.02
        sc = 1.6 - 0.6 * ease_out_back(lt / 0.35, 1.6)
        sc *= 1 + 0.035 * beat_pulse(t, 5)
        place(cv, S["cta"], 540, 330, scale=sc, alpha=clamp(lt / 0.1))
        bt = t - 25.6
        if bt > 0:
            bsc = 0.5 + 0.5 * ease_out_back(bt / 0.4, 2.0)
            bsc *= 1 + 0.04 * math.sin((t - 25.6) * math.pi * 2 * 1.0)
            place(cv, S["cta_btn"], 520, 1390, scale=bsc, alpha=clamp(bt / 0.15))
            at = t - 26.2
            if at > 0:
                place(cv, S["arrow"], 520, 1515 + 12 * abs(math.sin(at * math.pi * 2)), alpha=clamp(at / 0.3))
            twinkle(cv, t, [(170, 1330), (880, 1320), (230, 1470), (820, 1480), (520, 1270)], 25.7, size=64, color="gold")
        twinkle(cv, t, [(150, 250), (930, 280), (780, 430), (300, 440)], 25.3, size=60, color="gold")


# ------------------------------------------------------------------ io

def read_frames(path):
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE)
    size = W * H * 3
    last = None
    for _ in range(FRAMES):
        buf = proc.stdout.read(size)
        if len(buf) == size:
            last = Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1)
        yield last
    proc.stdout.close()
    proc.wait()


def frame_at(path, t):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.frombuffer("RGB", (W, H), out, "raw", "RGB", 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", help="comma-separated seconds to preview instead of a full render")
    args = ap.parse_args()
    random.seed(1)
    S = build_sprites()
    P = gfx.Particles()
    base = BUILD / "base.mp4"
    if args.stills:
        (BUILD / "stills").mkdir(exist_ok=True)
        for ts in args.stills.split(","):
            t = float(ts)
            img = render_frame(frame_at(base, t), t, S, P)
            img.save(BUILD / "stills" / f"t{t:05.2f}.png")
        print("stills ->", BUILD / "stills")
        return
    out = BUILD / "video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            str(out)], stdin=subprocess.PIPE)
    for i, frame in enumerate(read_frames(base)):
        t = i / FPS
        enc.stdin.write(render_frame(frame, t, S, P).tobytes())
        if i % 30 == 0:
            print(f"  {t:4.1f}s / {FRAMES / FPS:.0f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    print("graphics pass ->", out)


if __name__ == "__main__":
    main()
