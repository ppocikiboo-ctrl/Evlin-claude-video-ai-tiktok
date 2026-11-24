"""Synthesize the v3 dreamy chill bed + SFX (camera shutter, typewriter, film wind).

Usage: python3 gen_audio.py <duration_s> <music.wav> <sfx.wav>
Generated from scratch with numpy: no samples, royalty-free.
"""
import sys
import wave

import numpy as np

from timeline import BPM, CUTS, DAY_COUNT, SECTIONS, TYPE_CPS, WATER_COUNT

SR = 48000
DUR = float(sys.argv[1])
N = int(SR * (DUR + 0.5))
rng = np.random.default_rng(11)


def t_(sec):
    return np.arange(int(SR * sec)) / SR


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf) or i < 0:
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def onepole(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


# ------------------------------------------------------------ music
music = np.zeros(N)
beat = 60 / BPM
bar = beat * 4
# Dmaj9 - Bm9 - Gmaj7 - A6/9 : dreamy, warm
chords = [[50, 54, 57, 61, 64], [47, 50, 54, 57, 61], [43, 47, 50, 54, 59], [45, 49, 52, 54, 59]]
roots = [38, 35, 31, 33]


def rhodes(f, d):
    t = t_(d)
    trem = 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    tone = (np.sin(2 * np.pi * f * t + 0.8 * np.sin(2 * np.pi * f * t) * np.exp(-3 * t))
            + 0.2 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-2 * t))
    return tone * np.exp(-1.1 * t) * np.minimum(1, t / 0.01) * trem


tk = t_(0.4)
kick = np.sin(2 * np.pi * (48 * tk + (70 / 20) * (1 - np.exp(-20 * tk)))) * np.exp(-10 * tk)
tr = t_(0.08)
rim = np.sin(2 * np.pi * 1700 * tr) * np.exp(-70 * tr) + 0.4 * rng.standard_normal(len(tr)) * np.exp(-90 * tr)
th = t_(0.04)
shaker = (rng.standard_normal(len(th)) - onepole(rng.standard_normal(len(th)), 5000)) * np.exp(-80 * th)

for b in range(int(DUR / bar) + 2):
    t0 = b * bar
    ch = chords[b % 4]
    # rhodes chord, slight strum, re-struck on beat 3 softly
    for k, m in enumerate(ch):
        add(music, rhodes(note(m + 12), bar + 0.6), t0 + k * 0.018, 0.05)
        add(music, rhodes(note(m + 12), beat * 2), t0 + 2 * beat + 0.25 * beat + k * 0.015, 0.025)
    tb = t_(bar)
    bass = np.sin(2 * np.pi * note(roots[b % 4]) * tb) * np.exp(-0.9 * tb) * np.minimum(1, tb / 0.02)
    add(music, bass, t0, 0.26)
    # lazy swung drums
    add(music, kick, t0, 0.42)
    add(music, kick, t0 + 2.5 * beat, 0.3)
    add(music, rim, t0 + beat, 0.10)
    add(music, rim, t0 + 3 * beat, 0.10)
    for k in range(8):
        sw = 0.08 * beat if k % 2 else 0
        add(music, shaker, t0 + k * beat / 2 + sw, 0.05 if k % 2 else 0.03)

# vinyl crackle + soft hiss
crackle = np.zeros(N)
pops = rng.integers(0, N - 200, int(DUR * 9))
for p in pops:
    crackle[p:p + 40] += rng.standard_normal(40) * np.exp(-np.arange(40) / 6) * rng.uniform(0.2, 1)
music += crackle * 0.05 + onepole(rng.standard_normal(N), 3000) * 0.004

# gentle lowpass-y warmth on the whole bed (mix of dry + filtered)
music = 0.6 * music + 0.4 * onepole(music, 2500)

env = np.ones(N)
fi = int(0.6 * SR)
env[:fi] = np.linspace(0.2, 1, fi)
end = int(DUR * SR)
fo = int(1.5 * SR)
env[end - fo:end] = np.linspace(1, 0, fo)
env[end:] = 0
music *= env

# ------------------------------------------------------------ sfx
sfx = np.zeros(N)


def shutter():
    t = t_(0.18)
    n = rng.standard_normal(len(t))
    c1 = (n - onepole(n, 1500)) * np.exp(-60 * t)
    out = c1.copy()
    add_at = int(0.07 * SR)
    out[add_at:] += c1[: len(out) - add_at] * 0.8
    return out


def key_click():
    t = t_(0.025)
    n = rng.standard_normal(len(t))
    return (n - onepole(n, 2500)) * np.exp(-200 * t)


def film_wind(d=0.7):
    t = t_(d)
    n = onepole(rng.standard_normal(len(t)), 1200)
    flutter = 1 + 0.5 * np.sin(2 * np.pi * (14 + 20 * t / d) * t)
    return n * np.sin(np.pi * t / d) ** 2 * flutter


def chime(f):
    t = t_(1.6)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.0 * t)) * np.exp(-2.8 * t)


def soft_tick(f):
    t = t_(0.05)
    return np.sin(2 * np.pi * f * t) * np.exp(-60 * t)


add(sfx, shutter(), 0.0, 0.5)
for c in CUTS:
    add(sfx, film_wind(), c - 0.3, 0.35)
for name, s, e, l1, l2 in SECTIONS:
    if name == "brand":
        add(sfx, chime(note(86)), s + 0.1, 0.08)
        continue
    for k in range(0, len(l1), 2):  # typewriter: click every other char
        add(sfx, key_click(), s + k / TYPE_CPS, 0.10)
d0, d1 = DAY_COUNT
for i in range(10):
    add(sfx, soft_tick(note(79 + i)), d0 + i * (d1 - d0) / 10, 0.10)
w0, w1 = WATER_COUNT
add(sfx, chime(note(88)), w1, 0.08)
add(sfx, chime(note(86)), 36.2, 0.09)
add(sfx, chime(note(93)), 36.45, 0.07)


def write(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


write(sys.argv[2], music)
write(sys.argv[3], sfx)
print("audio ok")
