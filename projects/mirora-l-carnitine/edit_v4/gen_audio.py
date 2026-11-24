"""Synthesize the v4 bouncy marimba bed + cartoon SFX (royalty-free, numpy only).

Usage: python3 gen_audio.py <duration_s> <music.wav> <sfx.wav>
"""
import sys
import wave

import numpy as np

from timeline import BPM, BRAND, CRAVE_IN, CTA, CUTS, FRIEND_PRICE, HOOK, HOWTO, OUTRO, POOF

SR = 48000
DUR = float(sys.argv[1])
N = int(SR * (DUR + 0.5))
rng = np.random.default_rng(4)


def t_(sec):
    return np.arange(int(SR * sec)) / SR


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if 0 <= i < len(buf):
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


def marimba(f, d=0.5):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-25 * t)) \
        * np.exp(-7 * t) * np.minimum(1, t / 0.002)


# ------------------------------------------------------------- music
music = np.zeros(N)
beat = 60 / BPM
bar = 4 * beat
# C - G - Am - F, cheerful
prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
roots = [36, 43, 45, 41]
patt = [0, 2, 1, 2, 0, 2, 1, 2]  # chord tone pattern on 8ths
tk = t_(0.3)
kick = np.sin(2 * np.pi * (50 * tk + (100 / 22) * (1 - np.exp(-22 * tk)))) * np.exp(-12 * tk)
tc = t_(0.15)
clap = np.zeros(len(tc))
for off in (0, 0.008, 0.016):
    i = int(off * SR)
    n = rng.standard_normal(len(tc) - i)
    clap[i:] += (n - onepole(n, 1000)) * np.exp(-30 * tc[: len(tc) - i])
th = t_(0.04)
hat = (lambda n: n - onepole(n, 7000))(rng.standard_normal(len(th))) * np.exp(-100 * th)

for b in range(int(DUR / bar) + 2):
    t0 = b * bar
    ch = prog[b % 4]
    for k in range(8):
        m = ch[patt[k]] + 12 + (12 if k in (3, 7) else 0)
        add(music, marimba(note(m)), t0 + k * beat / 2, 0.16)
    for k in (0, 3, 6):  # bouncy bass
        tb = t_(beat * 0.9)
        add(music, np.sin(2 * np.pi * note(roots[b % 4]) * tb) * np.exp(-4 * tb), t0 + k * beat / 2, 0.3)
    for k in range(4):
        add(music, kick, t0 + k * beat, 0.45 if k % 2 == 0 else 0.3)
        if k % 2:
            add(music, clap, t0 + k * beat, 0.18)
        add(music, hat, t0 + k * beat + beat / 2, 0.06)

# drop the drums out during the "struggle" beat for contrast, back in on the brand
s0, s1 = int(HOOK[1] * SR), int(BRAND[0] * SR)
duck = np.ones(N)
duck[s0:s1] = 0.55
music *= duck
end = int(DUR * SR)
music[end - int(0.6 * SR):end] *= np.linspace(1, 0, int(0.6 * SR))
music[end:] = 0

# ------------------------------------------------------------- sfx
sfx = np.zeros(N)


def boom():
    t = t_(1.0)
    return np.sin(2 * np.pi * (40 * t + (90 / 6) * (1 - np.exp(-6 * t)))) * np.exp(-3.5 * t)


def pop():
    t = t_(0.1)
    f = 1000 * np.exp(-30 * t) + 280
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-32 * t)


def boing(f0):
    t = t_(0.35)
    f = f0 * (1 + 0.25 * np.sin(2 * np.pi * 14 * t) * np.exp(-6 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-9 * t)


def poof():
    t = t_(0.5)
    n = onepole(rng.standard_normal(len(t)), 1800)
    return n * np.exp(-7 * t) * np.minimum(1, t / 0.01)


def whoosh(d=0.35):
    t = t_(d)
    n = rng.standard_normal(len(t))
    return (n - onepole(n, 1500)) * np.sin(np.pi * t / d) ** 2


def sparkle():
    out = np.zeros(int(0.9 * SR))
    for k, m in enumerate([88, 91, 95, 100]):
        t = t_(0.5)
        s = np.sin(2 * np.pi * note(m) * t) * np.exp(-8 * t)
        i = int(k * 0.06 * SR)
        out[i:i + len(s)] += s
    return out


def kaching():
    t = t_(0.9)
    bell = (np.sin(2 * np.pi * 2093 * t) + 0.6 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-5 * t)
    n = rng.standard_normal(len(t))
    rattle = (n - onepole(n, 4000)) * np.exp(-30 * t) * 0.5
    out = np.zeros(int(1.0 * SR))
    out[:len(t)] += rattle
    i = int(0.07 * SR)
    out[i:i + len(t)] += bell
    return out


add(sfx, boom(), 0.0, 0.5)
add(sfx, pop(), 0.02, 0.3)
for c in CUTS:
    add(sfx, whoosh(), c - 0.22, 0.25)
add(sfx, pop(), HOOK[1] + 0.03, 0.28)
c0, c1 = CRAVE_IN
for i in range(6):
    add(sfx, boing(note(67 + 2 * i)), c0 + i * (c1 - c0) / 6 + 0.26, 0.16)
add(sfx, poof(), POOF, 0.35)
add(sfx, sparkle(), BRAND[0] + 0.35, 0.10)
add(sfx, pop(), HOWTO[0] + 0.05, 0.28)
add(sfx, pop(), HOWTO[0] + 0.6, 0.28)
add(sfx, pop(), CTA[0] + 0.05, 0.3)
add(sfx, kaching(), FRIEND_PRICE, 0.22)
add(sfx, pop(), OUTRO[0] + 0.03, 0.3)


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
