"""Synthesised soundtrack: a soft K-beauty style instrumental plus UI sound effects.

Everything is generated with numpy so the video carries no licensed audio.
"""
import math
import wave

import numpy as np

SR = 44100
BPM = 100
BEAT = 60 / BPM


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, d, s, r, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    sus = max(0, n - a - d - r)
    e = np.concatenate([np.linspace(0, 1, max(a, 1)), np.linspace(1, s, max(d, 1)), np.full(sus, s),
                        np.linspace(s, 0, max(r, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be a scalar or a per-sample array."""
    cutoff = np.broadcast_to(np.asarray(cutoff, np.float64), x.shape)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def fft_band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def bell(f, dur, amp=1.0, decay=0.9, index=1.6, ratio=3.5):
    t = np.arange(int(dur * SR)) / SR
    mod = index * np.exp(-t / 0.25) * np.sin(2 * np.pi * f * ratio * t)
    y = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / decay)
    y += 0.25 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t / (decay * 0.5))
    y *= np.minimum(1, t / 0.004)
    return y * amp


def pad_note(f, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for det in (-0.004, 0.0, 0.0045):
        ff = f * (1 + det)
        y += np.sin(2 * np.pi * ff * t) + 0.18 * np.sin(4 * np.pi * ff * t) + 0.06 * np.sin(6 * np.pi * ff * t)
    y *= (1 + 0.12 * np.sin(2 * np.pi * 0.3 * t)) / 3
    return y * env_adsr(n, 0.5, 0.4, 0.8, 0.8) * amp


def add(buf, sig, t0, pan=0.0):
    i = int(t0 * SR)
    if i >= buf.shape[0] or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    sig = sig[: buf.shape[0] - i]
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:i + len(sig), 0] += sig * l * 1.41
    buf[i:i + len(sig), 1] += sig * r * 1.41


# Fmaj9 - G6 - Em7 - Am9, one bar each
CHORDS = [
    (41, [65, 69, 72, 76, 79]),
    (43, [67, 71, 74, 76, 79]),
    (40, [64, 67, 71, 74, 79]),
    (45, [64, 67, 71, 72, 76]),
]
ARP = [0, 2, 4, 3, 1, 3, 4, 2]


def music(dur, drop_at):
    buf = np.zeros((int(dur * SR) + SR, 2))
    bar = BEAT * 4
    nbars = int(dur / bar) + 1
    rng = np.random.default_rng(7)
    for b in range(nbars):
        t0 = b * bar
        root, notes = CHORDS[b % 4]
        for k, n in enumerate(notes[:4]):
            add(buf, pad_note(midi(n), bar + 0.6, 0.05), t0, pan=-0.4 + 0.27 * k)
        add(buf, pad_note(midi(root + 12), bar + 0.3, 0.07), t0)
        # bell arpeggio in 8ths, an octave up
        for s in range(8):
            if (b + s) % 7 == 6:
                continue
            n = notes[ARP[s]] + 12
            add(buf, bell(midi(n), 1.4, 0.06 if s % 2 else 0.085, decay=0.6), t0 + s * BEAT / 2,
                pan=0.5 * math.sin(s * 1.3 + b))
        if t0 >= drop_at - 0.01:
            # sub bass
            n = int((BEAT * 4) * SR)
            t = np.arange(n) / SR
            y = np.sin(2 * np.pi * midi(root) * t) * env_adsr(n, 0.02, 0.3, 0.7, 0.3)
            add(buf, y * 0.16, t0)
            for q in range(4):
                bt = t0 + q * BEAT
                if q in (0, 2) or (q == 3 and b % 2):
                    add(buf, kick(), bt if q != 3 else bt + BEAT / 2)
                if q in (1, 3):
                    add(buf, snap(rng), bt, pan=0.1)
                for h in (0.5, 0.75) if q % 2 else (0.5,):
                    add(buf, hat(rng), bt + h * BEAT, pan=0.35)
    return buf


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 48 + 90 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.13) * 0.32


def hat(rng):
    n = int(0.05 * SR)
    x = rng.standard_normal(n)
    x = x - lowpass(x, 7000)
    return x * np.exp(-np.arange(n) / SR / 0.012) * 0.035


def snap(rng):
    n = int(0.2 * SR)
    x = fft_band(rng.standard_normal(n), 900, 5000)
    return x * np.exp(-np.arange(n) / SR / 0.05) * 0.09


# ------------------------------------------------------------------- effects
def sfx(kind, rng):
    if kind == "pop":
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        f = 380 + 900 * np.exp(-t / 0.018)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03) * 0.35
    if kind == "tik":
        n = int(0.04 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.008) * 0.25
    if kind == "ting":
        y = bell(midi(96), 1.6, 0.22, decay=0.7, index=1.0)
        hi = bell(midi(103), 1.2, 0.1, decay=0.5)
        y[: len(hi)] += hi
        return y
    if kind in ("whoosh", "whoosh_soft"):
        dur = 0.6 if kind == "whoosh" else 0.45
        n = int(dur * SR)
        t = np.arange(n) / SR
        x = rng.standard_normal(n)
        p = t / dur
        cut = 300 + 5000 * np.sin(np.pi * p) ** 2
        y = lowpass(x, cut) * np.sin(np.pi * p) ** 1.5
        return y * (0.5 if kind == "whoosh" else 0.3)
    if kind == "riser":
        dur = 0.95
        n = int(dur * SR)
        t = np.arange(n) / SR
        y = lowpass(rng.standard_normal(n), 200 + 7000 * (t / dur) ** 2) * (t / dur) ** 2 * 0.35
        y += np.sin(2 * np.pi * np.cumsum(300 + 900 * (t / dur) ** 2) / SR) * (t / dur) ** 2 * 0.05
        return y
    if kind == "impact":
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        y = np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.35) * 0.4
        y += lowpass(rng.standard_normal(n), 1500) * np.exp(-t / 0.15) * 0.25
        return y + bell(midi(84), 1.2, 0.1, decay=0.8)
    if kind == "sparkle":
        out = np.zeros(int(1.4 * SR))
        for k, n in enumerate((88, 91, 95, 98, 100, 103)):
            b = bell(midi(n), 0.9, 0.07, decay=0.35, index=0.8)
            i = int(k * 0.055 * SR)
            out[i:i + len(b)] += b[: len(out) - i]
        return out
    if kind == "shimmer":
        out = np.zeros(int(2.0 * SR))
        for k, n in enumerate((84, 88, 91, 96, 100, 103, 108)):
            b = bell(midi(n), 1.2, 0.05, decay=0.6, index=0.6)
            i = int(k * 0.08 * SR)
            out[i:i + len(b)] += b[: len(out) - i]
        return out
    if kind == "shake":
        dur = 1.1
        n = int(dur * SR)
        t = np.arange(n) / SR
        x = fft_band(rng.standard_normal(n), 1500, 7000)
        gate = np.clip(np.sin(2 * np.pi * 7 * t), 0, 1) ** 3
        slosh = lowpass(rng.standard_normal(n), 600) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.5 * t))
        return (x * gate * 0.22 + slosh * 0.5) * np.minimum(1, (dur - t) / 0.2)
    if kind in ("splash", "drip"):
        dur = 0.8 if kind == "splash" else 0.5
        n = int(dur * SR)
        t = np.arange(n) / SR
        y = lowpass(rng.standard_normal(n), 2500) * np.exp(-t / 0.18) * (0.45 if kind == "splash" else 0.12)
        for k in range(7 if kind == "splash" else 3):
            t0 = rng.uniform(0.0, dur * 0.6)
            m = int(0.06 * SR)
            tt = np.arange(m) / SR
            f = rng.uniform(500, 1100) * (1 + 6 * tt)
            b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.02) * 0.18
            i = int(t0 * SR)
            y[i:i + m] += b[: n - i]
        return y
    raise ValueError(kind)


def render(path, dur, events, scene_starts):
    rng = np.random.default_rng(11)
    drop = scene_starts[1]
    mus = music(dur, drop)
    # hook: lighter mix until the drop
    n = mus.shape[0]
    t = np.arange(n) / SR
    g = np.where(t < drop, 0.75, 1.0)
    fade = np.clip((dur - t) / 1.2, 0, 1)
    mus *= (g * fade)[:, None]
    fx = np.zeros_like(mus)
    for t0, kind in events:
        pan = {"whoosh": -0.3, "whoosh_soft": 0.3, "tik": 0.25}.get(kind, 0.0)
        add(fx, sfx(kind, rng), t0, pan)
    # final chord
    for k, nn in enumerate((65, 69, 72, 76, 81)):
        add(mus, bell(midi(nn + 12), 2.5, 0.06, decay=1.2), dur - 2.0 + k * 0.06, pan=-0.4 + 0.2 * k)
    mix = mus * 1.0 + fx * 0.8
    mix = mix[: int(dur * SR)]
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)
    mix *= 0.89 / max(1e-6, np.abs(mix).max())
    pcm = (mix * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
