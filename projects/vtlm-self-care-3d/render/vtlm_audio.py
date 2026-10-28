"""Synthesize the soundtrack for the VTLM ad: an original Korean-aesthetic pop
instrumental (~122 BPM, bars locked to the BOOM at 3.2s and the reveal at
17.0s) plus every SFX cue from the PROMPT_PACK cue sheet.

    python3 vtlm_audio.py out_dir

Writes music.wav, sfx.wav and mix.wav (48 kHz stereo). Everything is
generated here, so there is nothing to license. Swap music.wav for a TikTok
Commercial Music Library track in CapCut if preferred.
"""
import os
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter

import vtlm_render as V

SR = 48000
N = int(SR * V.DUR)
rng = np.random.default_rng(1)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def put(buf, t0, sig, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    buf[0, i:i + len(sig)] += sig * gain * (1 - max(0, pan))
    buf[1, i:i + len(sig)] += sig * gain * (1 + min(0, pan))


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, x)


def lp(x, hz, order=2):
    b, a = butter(order, hz / (SR / 2), "low")
    return lfilter(b, a, x)


def hp(x, hz, order=2):
    b, a = butter(order, hz / (SR / 2), "high")
    return lfilter(b, a, x)


# ------------------------------------------------------------- instruments

def bell(f, dur=1.6, bright=1.0):
    t = np.arange(int(SR * dur)) / SR
    s = np.zeros_like(t)
    for ratio, amp, dec in ((1, 1, 1.0), (2.0, 0.5 * bright, 0.5), (2.76, 0.35 * bright, 0.35),
                            (5.4, 0.18 * bright, 0.18)):
        s += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / (dur * dec * 0.5))
    return s * np.minimum(1, t / 0.002)


def pluck(f, dur=0.35):
    t = np.arange(int(SR * dur)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * env(len(t), 0.003, 0.09)


def saw(f, n, harm):
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 12):
        s += np.sin(2 * np.pi * f * k * t + k) / k * np.exp(-k / harm)
    return s


def kick():
    n = int(SR * 0.35)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13) * 1.1


def clap():
    n = int(SR * 0.22)
    s = bp(rng.normal(0, 1, n), 900, 4000) * env(n, 0.002, 0.06)
    return s * 0.9


def hat():
    n = int(SR * 0.06)
    return hp(rng.normal(0, 1, n), 7000) * env(n, 0.001, 0.018) * 0.5


def pop(f0=900):
    n = int(SR * 0.14)
    t = np.arange(n) / SR
    f = f0 * (0.35 + 0.65 * np.exp(-t / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.045)


def whoosh(dur=0.6, lo=300, hi=5000, up=True):
    n = int(SR * dur)
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    seg = 1024
    for i in range(0, n, seg):
        u = i / n if up else 1 - i / n
        c = lo * (hi / lo) ** u
        out[i:i + seg] = bp(x[i:i + seg], max(60, c * 0.6), min(SR / 2 - 100, c * 1.6), 1)
    t = np.linspace(0, 1, n)
    return out * np.sin(np.pi * t) ** 1.5 * 0.8


def sparkle(dur=0.7, count=14, lo=2500, hi=6500):
    n = int(SR * dur)
    s = np.zeros(n)
    for _ in range(count):
        i = int(rng.uniform(0, n * 0.8))
        b = bell(rng.uniform(lo, hi), 0.35, 0.3)[: n - i]
        s[i:i + len(b)] += b * rng.uniform(0.2, 0.5)
    return s


def boom():
    n = int(SR * 1.2)
    t = np.arange(n) / SR
    f = 32 + 60 * np.exp(-t / 0.12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    hit = lp(rng.normal(0, 1, n), 1200) * np.exp(-t / 0.08)
    return sub * 1.2 + hit * 0.5


def click():
    n = int(SR * 0.03)
    return hp(rng.normal(0, 1, n), 2500) * env(n, 0.0005, 0.005) + \
        np.sin(2 * np.pi * 3200 * np.arange(n) / SR) * env(n, 0.0005, 0.008) * 0.5


# ------------------------------------------------------------------ music

CHORDS = [[58, 62, 65, 69], [60, 64, 67, 74], [57, 60, 64, 67], [62, 65, 69, 72]]  # Bbmaj7 Cadd9 Am7 Dm7
BASS = [46, 48, 45, 50]
MELODY = [[77, 74, 72, 69], [76, 79, 76, 72], [76, 72, 69, 67], [74, 77, 81, 77]]


def section(t):
    if t < V.T_BOOM:
        return "intro"
    if t < V.T_MAP:
        return "groove"
    if t < V.T_RIBBON:
        return "break"
    return "chorus"


def music():
    buf = np.zeros((2, N))
    first = -2  # bars before the BOOM (the pickup starts at t < 0, clipped)
    last = int((V.DUR - V.B0) / V.BAR) + 1
    for k in range(first, last + 1):
        t0 = V.bt(k)
        if t0 >= V.DUR:
            break
        sec = section(max(0.0, t0 + 0.01))
        ch = CHORDS[k % 4]
        nbar = int(V.BAR * SR)
        # pad
        harm = {"intro": 1.2, "groove": 3.0, "break": 2.0, "chorus": 4.0}[sec]
        pad = sum(saw(midi(m), nbar, harm) for m in ch) / 4
        pad *= np.minimum(1, np.arange(nbar) / (0.08 * SR)) * np.minimum(1, (nbar - np.arange(nbar)) / (0.05 * SR))
        if sec != "intro":
            ph = (np.arange(nbar) / SR) % V.BEAT
            pad *= 0.55 + 0.45 * np.minimum(1, ph / 0.22)  # sidechain pump
        put(buf, t0, pad, 0.16, -0.15)
        put(buf, t0 + 0.006, pad, 0.16, 0.15)
        # arp
        if sec != "intro" or t0 > 0.5:
            for i in range(16):
                m = ch[[0, 1, 2, 3, 2, 1, 2, 3][i % 8]] + 12
                put(buf, t0 + i * V.BEAT / 4, pluck(midi(m)), 0.10 if sec != "intro" else 0.05,
                    0.4 if i % 2 else -0.4)
        # bass
        if sec in ("groove", "chorus", "break"):
            for i in range(8):
                n = int(V.BEAT / 2 * SR)
                tt = np.arange(n) / SR
                b = (np.sin(2 * np.pi * midi(BASS[k % 4]) * tt) + 0.25 * np.sin(4 * np.pi * midi(BASS[k % 4]) * tt))
                b *= env(n, 0.01, 0.18)
                put(buf, t0 + i * V.BEAT / 2, b, 0.32 if sec != "break" else 0.18)
        # drums
        for i in range(4):
            tb = t0 + i * V.BEAT
            if sec in ("groove", "chorus"):
                put(buf, tb, kick(), 0.55)
                if i in (1, 3):
                    put(buf, tb, clap(), 0.25, 0.1)
            if sec == "break" and i == 0:
                put(buf, tb, kick(), 0.35)
            if sec != "intro":
                put(buf, tb + V.BEAT / 2, hat(), 0.35, 0.3)
                if sec == "chorus":
                    put(buf, tb, hat(), 0.2, -0.3)
        # bell melody
        if sec in ("chorus", "break"):
            for i, m in enumerate(MELODY[k % 4]):
                put(buf, t0 + i * V.BEAT, bell(midi(m), 1.2, 0.6), 0.11 if sec == "chorus" else 0.07,
                    -0.2 if i % 2 else 0.2)
    # intro low-pass that opens on the BOOM, gentle tail at the end
    i3 = int(V.T_BOOM * SR)
    for c in range(2):
        buf[c, :i3] = lp(buf[c, :i3], 900)
    fade = np.ones(N)
    fade[-int(0.35 * SR):] = np.linspace(1, 0, int(0.35 * SR))
    return buf * fade


# --------------------------------------------------------------------- sfx

def sfx():
    buf = np.zeros((2, N))
    put(buf, 0.0, click(), 0.6, -0.3)
    put(buf, V.BEAT, click(), 0.5, -0.3)
    put(buf, 0.25, sparkle(0.9), 0.35)
    for i, t in enumerate(V.WORD_T):
        put(buf, t, pop(700 + 120 * i), 0.55)
    for i, t in enumerate(V.FOOD_T):
        put(buf, t, pop(1300 + 150 * i), 0.3, 0.5 if i % 2 else -0.5)
    put(buf, V.T_BOOM - 0.25, whoosh(0.3, 400, 6000), 0.4)
    put(buf, V.T_BOOM, boom(), 0.9)
    put(buf, V.T_BOOM, sparkle(0.8, 20), 0.4)
    put(buf, V.T_WHIP - 0.05, whoosh(0.45, 300, 4000, False), 0.5)
    put(buf, V.T_TOUCH, bell(1760, 1.6, 0.8), 0.35)
    put(buf, V.T_TOUCH + 0.05, whoosh(1.4, 200, 7000), 0.45)
    for i in range(10):
        put(buf, V.T_TOUCH + 0.1 + i * 0.12, bell(midi(77 + [0, 3, 5, 7, 10, 12, 15, 17, 19, 22][i]), 0.6, 0.4),
            0.12, -0.5 + i * 0.1)
    put(buf, V.T_TITLE2 - 0.1, whoosh(0.4, 500, 6000), 0.35)
    for t in V.BUB_T:
        put(buf, t, click(), 0.7)
        put(buf, t + 0.02, bell(2637, 0.5, 0.3), 0.12)
    for t in V.T_FOCUS:
        put(buf, t + 0.12, bell(2093, 1.0, 0.6), 0.3)
        put(buf, t, click(), 0.5)
    put(buf, 16.25, sparkle(1.0, 24, 3000, 8000), 0.35)
    put(buf, V.T_RIBBON - 0.2, whoosh(0.9, 80, 2500, False), 0.6)
    put(buf, V.T_RIBBON + 0.2, whoosh(1.1, 300, 3000), 0.3)
    for i, m in enumerate([77, 81, 84, 89]):
        put(buf, V.T_POUCH + i * 0.07, bell(midi(m), 2.2, 0.7), 0.2, -0.3 + 0.2 * i)
    put(buf, 19.5, sparkle(0.8, 16, 4000, 9000), 0.35)
    put(buf, V.T_BRAND, bell(midi(89), 1.5, 0.5), 0.12)
    put(buf, V.T_SHOP - 0.15, whoosh(0.35, 600, 7000), 0.35)
    for i, t in enumerate([V.T_SHOP + 0.3, V.T_SHOP + 0.3 + 2 * V.BEAT, V.bt(11)]):
        put(buf, t, pop(800 + 150 * i), 0.5)
    put(buf, V.bt(11), sparkle(0.7), 0.3)
    put(buf, V.T_END - 0.2, whoosh(0.3, 500, 7000), 0.35)
    put(buf, V.T_END + 0.1, bell(midi(88), 0.4, 0.4), 0.3)
    put(buf, V.T_END + 0.22, bell(midi(95), 0.7, 0.4), 0.3)
    put(buf, V.T_END + 4 * V.BEAT, bell(midi(96), 1.8, 0.9), 0.35)
    put(buf, V.T_END + 4 * V.BEAT, sparkle(0.9), 0.3)
    return buf


def reverb(buf, wet=0.18, dur=1.4):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = buf.copy()
    for c in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-t / (dur / 5))
        ir = lp(ir, 6000) / np.sqrt(np.sum(ir ** 2))
        out[c] += fftconvolve(buf[c], ir)[: buf.shape[1]] * wet
    return out


def write(path, buf):
    x = np.clip(buf, -1, 1)
    pcm = (x.T * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    m = reverb(music(), 0.15)
    s = reverb(sfx(), 0.2)
    m /= np.abs(m).max() + 1e-9
    s /= np.abs(s).max() + 1e-9
    # duck the music under the BOOM and the reveal
    duck = np.ones(N)
    for t, dur in ((V.T_BOOM, 0.6), (V.T_POUCH, 0.5)):
        i = int(t * SR)
        k = np.linspace(0, 1, int(dur * SR))
        duck[i:i + len(k)] = np.minimum(duck[i:i + len(k)], 0.6 + 0.4 * k)
    mix = m * 0.55 * duck + s * 0.6
    mix = np.tanh(mix * 1.3) / np.tanh(1.3)
    mix *= 0.8 / (np.abs(mix).max() + 1e-9)
    write(os.path.join(out_dir, "music.wav"), m * 0.89)
    write(os.path.join(out_dir, "sfx.wav"), s * 0.89)
    write(os.path.join(out_dir, "mix.wav"), mix)


if __name__ == "__main__":
    main(sys.argv[1])
