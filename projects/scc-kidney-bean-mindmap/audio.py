"""Synthesises the soundtrack: upbeat K-pop style loop (120 BPM, F major royal-road
progression) plus POP / TING / WHOOSH / BOING / sparkle effects placed from timeline.json.

usage: python3 audio.py timeline.json out.wav
"""
import json
import sys
import wave

import numpy as np

SR = 44100
rs = np.random.default_rng(42)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, a=0.005, d=0.2, s=0.0, r=0.05, hold=None):
    """ADSR envelope over n samples (hold = seconds before release)."""
    t = np.arange(n) / SR
    hold = hold if hold is not None else n / SR - r
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rel = np.clip(1 - (t - hold) / max(r, 1e-6), 0, 1)
    return e * np.where(t > hold, rel, 1.0)


def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if hi:
        m *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if lo:
        m *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X * m, len(x))


def reverb(x, seconds=1.4, mix=0.25):
    n = int(seconds * SR)
    ir = rs.standard_normal(n) * np.exp(-np.arange(n) / SR * 4.5)
    ir = fft_filter(ir, lo=300, hi=7000)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[: len(x)]
    return x + mix * y


class Track:
    def __init__(self, dur):
        self.L = np.zeros(int(dur * SR) + SR)
        self.R = np.zeros_like(self.L)

    def add(self, sig, t0, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if i >= len(self.L):
            return
        sig = sig[: len(self.L) - i]
        gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.L[i:i + len(sig)] += sig * gain * gl * 1.414
        self.R[i:i + len(sig)] += sig * gain * gr * 1.414


# ---------------- instruments ----------------
def kick():
    t = tt(0.35)
    f = 50 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 9))


def clap():
    t = tt(0.25)
    n = fft_filter(rs.standard_normal(len(t)), lo=900, hi=5000)
    e = np.exp(-t * 22)
    for off in (0.0, 0.011, 0.022):
        e += 0.6 * np.exp(-np.clip(t - off, 0, None) * 160) * (t >= off)
    return n * e * 0.5


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    n = fft_filter(rs.standard_normal(len(t)), lo=7000)
    return n * np.exp(-t * (14 if open_ else 70)) * 0.6


def pluck(f, dur=0.25):
    t = tt(dur)
    s = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) for k in range(4))
    return s * np.exp(-t * 14) * 0.35


def bell(f, dur=0.9):
    t = tt(dur)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 4)
         + 0.45 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 7)
         + 0.25 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 11)
         + 0.12 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t * 16))
    return s * np.minimum(1, t / 0.003) * 0.5


def pad(notes, dur):
    t = tt(dur)
    s = np.zeros_like(t)
    for n in notes:
        for det in (-0.08, 0.0, 0.08):
            f = midi(n + det)
            ph = (f * t + rs.random()) % 1.0
            s += 2 * ph - 1  # saw
    s = fft_filter(s, hi=1800) / (len(notes) * 3)
    return s * env(len(t), a=0.08, d=1.0, s=0.7, r=0.25) * 0.5


def bass(f, dur):
    t = tt(dur)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sign(np.sin(2 * np.pi * f * t))
    return np.tanh(1.3 * s) * env(len(t), a=0.004, d=0.18, s=0.45, r=0.04) * 0.55


# ---------------- sound effects ----------------
def sfx_pop(big=False):
    t = tt(0.18 if not big else 0.4)
    f = (380 if big else 520) + (900 if big else 1100) * np.exp(-t * 45)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (18 if big else 34))
    click = fft_filter(rs.standard_normal(len(t)), lo=2000) * np.exp(-t * 300) * 0.3
    if big:
        sub = np.sin(2 * np.pi * np.cumsum(60 + 120 * np.exp(-t * 20)) / SR) * np.exp(-t * 10)
        s = s + 0.9 * sub + fft_filter(rs.standard_normal(len(t)), lo=500, hi=6000) * np.exp(-t * 25) * 0.5
    return s + click


def sfx_ting(f0=2637):
    s = bell(f0, 1.0) * 0.9
    s[: int(0.6 * SR)] += bell(f0 * 1.5, 0.6) * 0.35
    return s


def sfx_boing():
    t = tt(0.55)
    f = 210 * (1 + 0.55 * np.exp(-t * 6) * np.sin(2 * np.pi * 13 * t)) * (1 + 0.6 * np.exp(-t * 12))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    return s * np.exp(-t * 5.5) * np.minimum(1, t / 0.004) * 0.6


def sfx_funny():
    # cartoon slide-whistle drop ("uh-oh!") with wobble
    t = tt(0.7)
    f = 1500 * np.exp(-t * 1.6) * (1 + 0.04 * np.sin(2 * np.pi * 9 * t)) + 350
    ph = 2 * np.pi * np.cumsum(f) / SR
    breath = fft_filter(rs.standard_normal(len(t)), lo=1500, hi=6000) * 0.06
    return (np.sin(ph) * 0.7 + breath) * env(len(t), a=0.02, d=2, s=1, r=0.15)


def sfx_whoosh(dur=0.55):
    n = int(dur * SR)
    x = rs.standard_normal(n)
    y = np.zeros(n)
    low = band = 0.0
    q = 0.35
    for i in range(n):  # state-variable band-pass with rising cutoff
        k = i / n
        fc = 300 * (25 ** k)
        g = 2 * np.sin(np.pi * min(fc, 9000) / SR)
        high = x[i] - low - q * band
        band += g * high
        low += g * band
        y[i] = band
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return y * e * 0.9


def sfx_sparkle():
    out = np.zeros(int(1.6 * SR))
    notes = [84, 88, 91, 96, 100, 103, 108, 103, 108]
    for i, n in enumerate(notes):
        b = bell(midi(n), 1.0) * (0.7 - i * 0.04)
        s = int(i * 0.045 * SR)
        out[s:s + len(b)] += b[: len(out) - s]
    t = np.arange(len(out)) / SR
    shimmer = fft_filter(rs.standard_normal(len(out)), lo=6000) * np.exp(-t * 3) * np.minimum(1, t / 0.1) * 0.12
    return out + shimmer


def sfx_riser(dur):
    t = tt(dur)
    n = fft_filter(rs.standard_normal(len(t)), lo=1500, hi=9000)
    return n * (t / dur) ** 2 * 0.25


# ---------------- arrangement ----------------
def build(tl):
    dur = tl["duration"]
    beat = 60 / tl["bpm"]
    bar = beat * 4
    drums, inst, fx = Track(dur), Track(dur), Track(dur)

    prog = [  # (chord notes, bass midi) — Bbmaj7, C, Am7, Dm7
        ([58, 62, 65, 69], 46), ([60, 64, 67, 72], 48), ([57, 60, 64, 67], 45), ([62, 65, 69, 72], 50),
    ]
    melody = [
        [(0, 77, .5), (.5, 81, .5), (1, 84, .75), (2, 81, .5), (2.5, 79, .5), (3, 77, 1)],
        [(0, 76, .5), (.5, 79, .5), (1, 84, .5), (1.5, 81, .5), (2, 79, 1), (3.5, 76, .5)],
        [(0, 76, .5), (.5, 81, .5), (1, 84, .5), (1.5, 86, .5), (2, 84, .5), (2.5, 81, .5), (3, 79, 1)],
        [(0, 77, .5), (.5, 81, .5), (1, 77, .5), (1.5, 74, .5), (2, 77, 1.5), (3.5, 81, .5)],
    ]
    drop = tl["sections"]["mindmap"][0]
    end = dur - 0.5
    nbars = int(np.ceil(dur / bar))
    for b in range(nbars):
        t0 = b * bar
        notes, bn = prog[b % 4]
        full = t0 + bar > drop
        if t0 < end:
            inst.add(pad(notes, bar), t0, 0.55 if full else 0.3)
        for i in range(16):  # 16th grid
            ts = t0 + i * beat / 4
            if ts >= end:
                break
            is_full = ts >= drop
            if i % 4 == 0:
                drums.add(kick(), ts, 1.0)
            if i in (4, 12):
                drums.add(clap(), ts, 0.8)
            if i % 4 == 2:
                drums.add(hat(open_=is_full and i == 14), ts, 0.45, pan=0.3)
            elif is_full and i % 2 == 1:
                drums.add(hat(), ts, 0.22, pan=-0.3)
            if i % 2 == 0:  # bouncing octave bass on 8ths
                oct_ = 12 if (i // 2) % 2 else 0
                inst.add(bass(midi(bn - 12 + oct_), beat / 2 * 0.9), ts, 0.7)
            if is_full or i % 4 == 2:  # arp plucks
                arp = notes[[0, 1, 2, 3, 2, 1, 3, 2][i % 8]] + 12
                inst.add(pluck(midi(arp)), ts, 0.28 if is_full else 0.22, pan=0.4 if i % 2 else -0.4)
        if t0 >= 4.0 - 1e-6 and t0 < end:
            mel = Track(bar + 2)
            for (bt, n, d) in melody[b % 4]:
                mel.add(bell(midi(n), d * beat + 0.4), bt * beat, 1.0)
            inst.add(mel.L, t0, 0.42, pan=0.1)
    # snare roll + riser into the mind-map drop
    for i in range(8):
        drums.add(clap(), drop - 1.0 + i * 0.125, 0.25 + i * 0.06)
    fx.add(sfx_riser(1.1), drop - 1.1, 0.8)
    # outro: final chord sustain
    inst.add(pad([65, 69, 72, 77], 1.6), end, 0.6)
    inst.add(bell(midi(89), 1.5), end, 0.5)
    drums.add(kick(), end, 1.0)

    s = tl["sfx"]
    for x in s["pop"]:
        fx.add(sfx_pop(), x, 0.75, pan=rs.uniform(-0.3, 0.3))
    for x in s["bigpop"]:
        fx.add(sfx_pop(big=True), x, 1.0)
    for x in s["funny"]:
        fx.add(sfx_funny(), x + 0.12, 0.55)
    for x in s["boing"]:
        fx.add(sfx_boing(), x, 0.55, pan=rs.uniform(-0.4, 0.4))
    for x in s["whoosh"]:
        fx.add(sfx_whoosh(), x - 0.1, 0.5, pan=-0.2)
    for x in s["sparkle"]:
        fx.add(sfx_sparkle(), x, 0.55)
    for st in tl["stars"]:
        fx.add(sfx_ting(rs.choice([2349, 2637, 3136])), st["t"], 0.35, pan=(st["x"] - 540) / 700)

    music_L = drums.L * 0.8 + reverb(inst.L, mix=0.22)
    music_R = drums.R * 0.8 + reverb(inst.R, mix=0.22)
    L = music_L * 0.55 + reverb(fx.L, 0.9, 0.12)
    R = music_R * 0.55 + reverb(fx.R, 0.9, 0.12)
    n = int(dur * SR)
    out = np.stack([L[:n], R[:n]], 1)
    out /= np.max(np.abs(out)) + 1e-9
    out = np.tanh(out * 1.4) / np.tanh(1.4)  # gentle limiter
    fade = int(0.4 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out * 0.89


if __name__ == "__main__":
    tl = json.load(open(sys.argv[1]))
    pcm = (build(tl) * 32767).astype(np.int16)
    with wave.open(sys.argv[2], "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
