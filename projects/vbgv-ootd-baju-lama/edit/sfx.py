"""Synthesise the whoosh / wip / wup / pop / ding SFX and mix them under the voiceover.

Usage: python3 sfx.py <voice.wav 44.1k mono> <out.wav>
"""
import sys
import wave

import numpy as np

from timeline import SFX

SR = 44100
rng = np.random.default_rng(7)


def env(n, attack=0.1, power=2.0):
    t = np.linspace(0, 1, n)
    a = int(n * attack)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 0.7
    e[a:] = (1 - np.linspace(0, 1, n - a)) ** power
    return e


def onepole_sweep(x, f0, f1, highpass=False):
    """Time-varying one-pole filter: cutoff sweeps f0 -> f1 (log)."""
    n = len(x)
    fc = f0 * (f1 / f0) ** np.linspace(0, 1, n)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(n)
    s = 0.0
    for i in range(n):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return x - y if highpass else y


def whoosh(dur=0.45, up=True):
    n = int(SR * dur)
    noise = rng.standard_normal(n)
    f0, f1 = (300, 5000) if up else (5000, 300)
    lp = onepole_sweep(noise, f0, f1)
    lp = lp - onepole_sweep(lp, 120, 120)  # drop rumble
    t = np.linspace(0, 1, n)
    e = np.sin(np.pi * t ** (0.6 if up else 1.4)) ** 1.5
    out = lp * e
    return out / (np.abs(out).max() + 1e-9)


def wip(dur=0.16, f0=500, f1=1800):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.3 * np.sin(2 * ph)
    return s * env(n, 0.05, 1.5) / 1.3


def wup(dur=0.22):
    return wip(dur, 900, 260)


def pop(dur=0.07):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 40) + 250
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.02, 3)


def ding(dur=0.7):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 1568 * t) + 0.5 * np.sin(2 * np.pi * 2352 * t)
         + 0.25 * np.sin(2 * np.pi * 3136 * t))
    return s * np.exp(-t * 6) * np.minimum(1, t * 400) / 1.75


GEN = {
    "whoosh": lambda: whoosh(0.45, True),
    "whoosh_down": lambda: whoosh(0.4, False),
    "wip": wip,
    "wup": wup,
    "pop": pop,
    "ding": ding,
}
GAIN = {"whoosh": 0.32, "whoosh_down": 0.28, "wip": 0.18, "wup": 0.2, "pop": 0.25, "ding": 0.16}


def main(voice_path, out_path):
    with wave.open(voice_path) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    mix = voice.copy()
    for t, kind in SFX:
        s = GEN[kind]() * GAIN[kind]
        i = int(t * SR)
        j = min(len(mix), i + len(s))
        mix[i:j] += s[: j - i]
    peak = np.abs(mix).max()
    if peak > 0.97:
        mix *= 0.97 / peak
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
