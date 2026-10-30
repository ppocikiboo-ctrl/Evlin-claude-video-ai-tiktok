#!/usr/bin/env python3
"""Re-edit a UGC selfie video of the FRANKLY PDRN serum with a scroll-stopping hook.

The edit opens with a 1.3 s teaser of the glowiest close-up (taken from the end
of the clip, with its own audio so the lip-sync holds), then plays the original
video with Malay captions and a yellow-basket CTA. Text, sparkles and sound
effects reuse the toolkit in ../frankly-pdrn-bounce-ball-serum/render.

Usage:
  python3 edit.py --video /path/to/selfie.mp4 [--out ../output.mp4] [--stills 0.3,2,9]
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "frankly-pdrn-bounce-ball-serum", "render"))
import audio  # noqa: E402
from render import (BROWN, CTA_YELLOW, SPARK, WHITE, Field, appear, burst, clamp, ease_io,  # noqa: E402
                    ease_out, pill, place, prog, text_img)

W, H, FPS = 1080, 1920, 30
HOOK_SRC = 13.0   # teaser source start (s)
HOOK_LEN = 1.3
MAIN_LEN = 14.3   # original clip minus its silent tail
DURATION = HOOK_LEN + MAIN_LEN
FRAMES = None

SHADOW = (4, 12, (40, 20, 10, 210))
# (start, end, caption) in original-clip time
CAPTIONS = [
    (2.3, 4.8, "Sapu & tepuk perlahan ✨"),
    (4.8, 7.0, "Rasa lembap & segar 💧"),
    (7.0, 9.3, "Bouncy & comel! 🧡"),
    (9.3, 12.0, "Kulit nampak glowing ✨"),
]
SPARKS = Field(31, 16, SPARK, (30, 70), yr=(150, 1500), twinkle=True)


def src_frame(t):
    i = int(round(t * FPS)) + 1
    i = max(1, min(i, len(os.listdir(FRAMES))))
    return Image.open(os.path.join(FRAMES, f"f{i:04d}.jpg")).convert("RGB")


def grade(im):
    a = np.asarray(im, np.float32) / 255
    a = a * np.array([1.04, 1.01, 0.96], np.float32) + 0.015
    a = np.clip(a, 0, 1)
    a = a + 0.35 * (a - 0.5) * a * (1 - a) * 4 * 0.5        # gentle S-curve
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = lum + (a - lum) * 1.1
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


def zoom(im, z, cx=W / 2, cy=H / 2):
    if z <= 1.001:
        return im
    cw, ch = W / z, H / z
    x = clamp(cx - cw / 2, 0, W - cw)
    y = clamp(cy - ch / 2, 0, H - ch)
    return im.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


def flash(im, a):
    if a <= 0.01:
        return im
    return Image.blend(im, Image.new("RGBA", (W, H), (255, 252, 246, 255)), clamp(a))


def hook(t):
    base = grade(src_frame(HOOK_SRC + t))
    z = 1.16 - 0.1 * ease_out(prog(t, 0, 0.5))
    jx = 14 * math.sin(t * 60) * (1 - prog(t, 0, 0.25))
    base = zoom(base, z, W / 2 + jx, 820)
    SPARKS.draw(base, t, 0.8)
    place(base, text_img("RAHSIA KULIT\nGLOWING AKU 👀", 96, WHITE, "xb", shadow=SHADOW), 540, 300,
          *_sa(t, 0.05))
    burst(base, t, 0.08, 540, 300, seed=1, radius=460, n=12)
    place(base, pill("Serum ada BOLA OREN dalam botol! 🧡", 50), 540, 1570, *_sa(t, 0.45))
    burst(base, t, 0.5, 540, 1570, seed=2, radius=440)
    base = flash(base, 0.9 * (1 - prog(t, 0, 0.12)) + 0.9 * prog(t, HOOK_LEN - 0.12, HOOK_LEN))
    return base


def _sa(t, t0, kind="pop", t_out=None):
    s, a, dy = appear(t, t0, kind, 0.4, t_out, 0.2)
    return s, a


def main_part(u):
    base = grade(src_frame(u))
    z = 1.0 + 0.06 * (1 - ease_out(prog(u, 0, 0.35)))     # punch-in after the cut
    base = zoom(base, z)
    # product intro
    s, a, dy = appear(u, 0.1, "up", 0.4, 2.1, 0.2)
    place(base, text_img("FRANKLY PDRN\nBounce Ball Serum 🧡", 76, WHITE, "xb", shadow=SHADOW), 540, 270 + dy, s, a)
    s, a, dy = appear(u, 0.5, "pop", 0.4, 2.1, 0.2)
    place(base, pill("Salmon DNA PDRN", 40), 540, 430 + dy, s, a)
    burst(base, u, 0.15, 540, 270, seed=3, radius=420)
    for k, (t0, t1, txt) in enumerate(CAPTIONS):
        if t0 - 0.05 <= u < t1 + 0.25:
            s, a, dy = appear(u, t0, "pop", 0.35, t1 - 0.2, 0.2)
            place(base, pill(txt, 60), 540, 270 + dy, s, a)
            burst(base, u, t0 + 0.05, 540, 270, seed=10 + k, radius=420, n=8)
    # CTA
    s, a, dy = appear(u, 12.0, "up", 0.35)
    place(base, text_img("Nak cuba? 👀", 64, WHITE, "xb", shadow=SHADOW), 540, 1440 + dy, s, a)
    s, a, _ = appear(u, 12.3, "pop", 0.4)
    pulse = 1 + 0.05 * math.sin((u - 12.3) * 2 * math.pi * 1.8) * prog(u, 12.7, 12.9)
    place(base, pill("Tekan BAKUL KUNING 🛒", 62, fg=BROWN, bg=CTA_YELLOW, bg2=(255, 178, 40)),
          540, 1575, s * pulse, a)
    burst(base, u, 12.35, 540, 1575, seed=20, radius=460, n=14)
    base = flash(base, 0.7 * (1 - prog(u, 0, 0.15)))
    return base


def render_frame(i):
    t = i / FPS
    im = hook(t) if t < HOOK_LEN else main_part(t - HOOK_LEN)
    return im.convert("RGB").tobytes()


def build_audio(video, path, work):
    raw = os.path.join(work, "orig.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "2", "-ar", str(audio.SR), raw], check=True)
    with wave.open(raw) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768
    sr = audio.SR

    def seg(a, b, fi=0.01, fo=0.06):
        s = x[int(a * sr):int(b * sr)].copy()
        n = len(s)
        e = np.ones(n)
        e[:int(fi * sr)] = np.linspace(0, 1, int(fi * sr))
        e[n - int(fo * sr):] = np.linspace(1, 0, int(fo * sr))
        return s * e[:, None]

    orig = np.concatenate([seg(HOOK_SRC, HOOK_SRC + HOOK_LEN) * 0.8, seg(0, MAIN_LEN, 0.01, 0.4)])
    fx = np.zeros_like(orig)
    rng = np.random.default_rng(5)
    hl = HOOK_LEN
    events = [(0.0, "impact"), (0.05, "pop"), (0.1, "shimmer"), (0.45, "pop"), (hl - 0.3, "whoosh"),
              (hl + 0.1, "whoosh_soft"), (hl + 0.5, "pop"), (hl + 12.0, "whoosh_soft"), (hl + 12.3, "pop"),
              (hl + 12.35, "sparkle"), (hl + 12.8, "ting")]
    events += [(hl + t0, "pop") for t0, _, _ in CAPTIONS]
    for t0, kind in events:
        audio.add(fx, audio.sfx(kind, rng), t0)
    mix = orig + fx * 0.45
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix *= 0.93 / np.abs(mix).max()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


def main():
    global FRAMES
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "output", "frankly-pdrn-ugc-hook.mp4"))
    ap.add_argument("--stills")
    args = ap.parse_args()
    work = tempfile.mkdtemp(prefix="ugc-")
    FRAMES = os.path.join(work, "f")
    os.makedirs(FRAMES)
    subprocess.run(["ffmpeg", "-v", "error", "-i", args.video, "-vf", f"fps={FPS}", "-q:v", "2",
                    os.path.join(FRAMES, "f%04d.jpg")], check=True)
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    if args.stills:
        for s in args.stills.split(","):
            Image.frombytes("RGB", (W, H), render_frame(int(float(s) * FPS))).save(
                os.path.join(out_dir, f"still_{float(s):05.2f}.jpg"), quality=90)
        return
    wav = os.path.join(work, "mix.wav")
    build_audio(args.video, wav, work)
    n = int(round(DURATION * FPS))
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", args.out], stdin=subprocess.PIPE)
    from multiprocessing import Pool
    with Pool(os.cpu_count()) as pool:
        for buf in pool.imap(render_frame, range(n), chunksize=4):
            enc.stdin.write(buf)
    enc.stdin.close()
    enc.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
