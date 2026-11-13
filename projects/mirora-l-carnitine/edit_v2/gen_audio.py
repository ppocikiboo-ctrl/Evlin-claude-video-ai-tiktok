"""Synthesize an original warm lo-fi bed + SFX track for the v2 edit.

Usage: python3 gen_audio.py <duration_s> <music.wav> <sfx.wav>
Everything is generated from scratch with numpy (no samples), so it is
royalty-free.
"""
import sys
import wave

import numpy as np

from timeline import BPM, CARDS, CUTS, DAY_DOTS, WATER_FILL

SR = 48000
DUR = float(sys.argv[1])
N = int(SR * (DUR + 0.5))
rng = np.random.default_rng(7)


def t_(sec):
    return np.arange(int(SR * sec)) / SR


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def note(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def lowpass(x, cutoff):
    # one-pole low-pass, good enough for softening noise/pads
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


# ---------------------------------------------------------------- music bed
music = np.zeros(N)
beat = 60 / BPM
bar = beat * 4
# Fmaj9 - Em7 - Dm9 - Cmaj7 (soft, "aesthetic" feel)
chords = [[53, 57, 60, 64, 67], [52, 55, 59, 62, 67],
          [50, 53, 57, 60, 64], [48, 52, 55, 59, 62]]
bass_roots = [41, 40, 38, 36]

# pre-render one-shots
tk = t_(0.45)
kick = np.sin(2 * np.pi * (45 * tk + (110 / 18) * (1 - np.exp(-18 * tk)))) * np.exp(-9 * tk)
tn = t_(0.18)
snap = highpass(rng.standard_normal(len(tn)), 1200) * np.exp(-28 * tn)
th = t_(0.05)
hat = highpass(rng.standard_normal(len(th)), 6000) * np.exp(-90 * th)

n_bars = int(DUR / bar) + 2
for b in range(n_bars):
    t0 = b * bar
    ch = chords[b % 4]
    # pad: soft additive tones with slow attack/release
    tp = t_(bar + 0.4)
    env = np.minimum(1, tp / 0.35) * np.minimum(1, np.maximum(0, (bar + 0.4 - tp) / 0.5))
    pad = np.zeros(len(tp))
    for m in ch:
        f = note(m + 12)
        for k, amp in ((1, 1.0), (2, 0.25), (3, 0.08)):
            pad += amp * np.sin(2 * np.pi * f * k * tp + rng.uniform(0, 6))
            pad += 0.5 * amp * np.sin(2 * np.pi * f * k * 1.004 * tp)
    add(music, pad * env, t0, 0.018)
    # bass on beats 1 and 3
    for bt in (0, 2):
        tb = t_(beat * 1.8)
        bs = np.sin(2 * np.pi * note(bass_roots[b % 4]) * tb) * np.exp(-1.6 * tb)
        add(music, bs, t0 + bt * beat, 0.22)
    # drums
    for bt in range(4):
        tt = t0 + bt * beat
        if bt in (0, 2):
            add(music, kick, tt, 0.55)
        if bt == 2 and b % 2 == 1:
            add(music, kick, tt + beat * 0.5, 0.35)
        if bt in (1, 3):
            add(music, snap, tt, 0.16)
        add(music, hat, tt, 0.07)
        add(music, hat, tt + beat / 2, 0.045)
    # bell arpeggio on 8ths
    for k in range(8):
        tb = t_(0.9)
        m = ch[[0, 2, 4, 2, 1, 3, 4, 3][k]] + 24
        bell = (np.sin(2 * np.pi * note(m) * tb) + 0.3 * np.sin(2 * np.pi * note(m) * 2.01 * tb)) * np.exp(-5 * tb)
        add(music, bell, t0 + k * beat / 2, 0.035)

# gentle intro/outro fades
fade = np.ones(N)
fi = int(0.05 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fo = int(1.2 * SR)
end = int(DUR * SR)
fade[end - fo:end] = np.linspace(1, 0, fo)
fade[end:] = 0
music *= fade

# ---------------------------------------------------------------- sfx
sfx = np.zeros(N)


def whoosh(d=0.45):
    t = t_(d)
    n = rng.standard_normal(len(t))
    env = np.sin(np.pi * t / d) ** 2
    # sweep: blend from low-passed to bright as it rises
    lo, hi = lowpass(n, 500), highpass(n, 2500)
    mix = t / d
    return (lo * (1 - mix) + hi * mix * 0.6) * env


def pop():
    t = t_(0.12)
    f = 900 * np.exp(-25 * t) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-30 * t)


def boom():
    t = t_(1.2)
    sub = np.sin(2 * np.pi * (38 * t + (90 / 6) * (1 - np.exp(-6 * t)))) * np.exp(-3.2 * t)
    hit = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-14 * t) * 0.6
    return sub + hit


def ding(f=1318.5):
    t = t_(1.4)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-6 * t)
            + 0.3 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-3.5 * t)


def tick(i):
    t = t_(0.06)
    f = note(84 + [0, 2, 4, 5, 7, 9, 11, 12, 14, 16][i])
    return np.sin(2 * np.pi * f * t) * np.exp(-45 * t)


def bloop():
    t = t_(0.25)
    f = 300 + 900 * t / 0.25
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-10 * t)


add(sfx, boom(), 0.0, 0.55)
for c in CUTS:
    add(sfx, whoosh(), c - 0.3, 0.22)
for name, s, *_ in CARDS[1:]:
    add(sfx, pop(), s + 0.05, 0.28)
d0, d1 = DAY_DOTS
for i in range(10):
    add(sfx, tick(i), d0 + i * (d1 - d0) / 10, 0.16)
w0, w1 = WATER_FILL
for k in range(4):
    add(sfx, bloop(), w0 + k * (w1 - w0) / 4, 0.12)
add(sfx, ding(), w1, 0.16)
add(sfx, ding(1567.98), 36.15, 0.18)
add(sfx, ding(2093.0), 36.35, 0.12)


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
