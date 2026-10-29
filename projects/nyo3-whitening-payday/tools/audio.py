"""Original K-beauty style backing track (120 BPM, royalty-free because it is
synthesised here) plus the SFX hits, mixed to a single WAV."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 30.0
BPM = 120
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(SR * d)) / SR


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def onepole_lp(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter  # noqa
    return lfilter([a], [1, a - 1], x)


try:
    import scipy.signal  # noqa
    LP = onepole_lp
except ImportError:  # pragma: no cover
    def LP(x, cutoff):
        return lowpass(x, 1 - np.exp(-2 * np.pi * cutoff / SR))


def noise(d):
    return rng.standard_normal(int(SR * d))


# ---------------------------------------------------------------- instruments
def pluck(f, d=0.45, bright=1.0):
    t = t_(d)
    env = np.exp(-t * 9) * (1 - np.exp(-t * 400))
    s = sum(np.sin(2 * np.pi * f * k * t) * (bright / k ** 1.6) for k in range(1, 6))
    return s * env


def pad(freqs, d):
    t = t_(d)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.25, 0.0, 0.25):
            ph = rng.random() * 2 * np.pi
            s += ((2 * ((f * (1 + det / 100) * t + ph / 6.28) % 1)) - 1)
    s = LP(s / (len(freqs) * 3), 1400)
    att = np.clip(t / 0.25, 0, 1)
    rel = np.clip((d - t) / 0.3, 0, 1)
    return s * att * rel


def bass(f, d):
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    env = np.clip(t / 0.01, 0, 1) * np.exp(-t * 2.2) * np.clip((d - t) / 0.05, 0, 1)
    return np.tanh(1.6 * s) * env


def kick():
    t = t_(0.35)
    f = 50 + 110 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)


def clap():
    t = t_(0.25)
    n = noise(0.25)
    n = n - LP(n, 900)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return LP(n, 6000) * env


def hat(open_=False):
    d = 0.18 if open_ else 0.05
    t = t_(d)
    n = noise(d)
    n = n - LP(n, 7000)
    return n * np.exp(-t * (18 if open_ else 70))


# ---------------------------------------------------------------- sfx
def sfx_cash():
    out = np.zeros(int(SR * 0.9))
    place(out, LP(noise(0.04), 3000) * np.exp(-t_(0.04) * 80), 0, 0.6)
    for at in (0.05, 0.14):
        t = t_(0.7)
        s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy)
                for f, a, dcy in ((2093, 1, 5), (2793, .6, 6), (4186, .4, 8), (5400, .25, 10)))
        place(out, s, at, 0.55)
    return out


def sfx_whoosh(d=0.45):
    t = t_(d)
    n = noise(d)
    out = np.zeros_like(n)
    seg = 512
    for i in range(0, len(n), seg):
        c = 400 + 5000 * np.sin(np.pi * min(1, i / len(n))) ** 2
        out[i:i + seg] = LP(n[i:i + seg + 0], c)[: len(out[i:i + seg])]
    env = np.sin(np.pi * t / d) ** 2
    return out * env * 0.9


def sfx_pop():
    t = t_(0.09)
    f = 900 * np.exp(-t * 28) + 220
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)


def sfx_ding():
    t = t_(1.2)
    return (np.sin(2 * np.pi * 1760 * t) + .4 * np.sin(2 * np.pi * 3520 * t)
            + .15 * np.sin(2 * np.pi * 5280 * t)) * np.exp(-t * 4) * (1 - np.exp(-t * 600))


def sfx_sparkle():
    out = np.zeros(int(SR * 0.8))
    for i in range(9):
        f = rng.uniform(3200, 7000)
        t = t_(0.2)
        place(out, np.sin(2 * np.pi * f * t) * np.exp(-t * 30), i * 0.06 + rng.uniform(0, .02), 0.35)
    return out


def sfx_click():
    t = t_(0.03)
    return (np.sin(2 * np.pi * 1600 * t) * 0.6 + noise(0.03) * 0.4) * np.exp(-t * 220)


SFX = dict(cash=sfx_cash, whoosh=sfx_whoosh, pop=sfx_pop, ding=sfx_ding,
           sparkle=sfx_sparkle, click=sfx_click)


def music():
    m = np.zeros(N + SR)
    # IV - V - iii - vi in C (Fmaj7, G6, Em7, Am9) — 2 s per chord (one bar)
    prog = [[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [57, 60, 64, 67]]
    roots = [41, 43, 40, 45]
    bars = int(DUR / (4 * BEAT)) + 1
    for b in range(bars):
        t0 = b * 4 * BEAT
        ch = prog[b % 4]
        place(m, pad([midi(n) for n in ch], 4 * BEAT + 0.2), t0, 0.16)
        # bass: root on 1, octave pickup on the "and" of 3
        place(m, bass(midi(roots[b % 4]), 1.4), t0, 0.32)
        place(m, bass(midi(roots[b % 4] + 12), 0.45), t0 + 2.5 * BEAT, 0.2)
        place(m, bass(midi(roots[b % 4]), 0.45), t0 + 3.0 * BEAT, 0.25)
        # pluck arpeggio, 16ths
        arp = [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[3] + 12, ch[2] + 24, ch[3] + 12, ch[1] + 12, ch[2] + 12]
        for k in range(16):
            place(m, pluck(midi(arp[k % 8])), t0 + k * BEAT / 4, 0.10 if k % 2 else 0.14)
        if b == 0:
            continue  # sparse intro bar: pads, bass and plucks only
        for k in range(4):
            place(m, kick(), t0 + k * BEAT, 0.55)
            place(m, hat(), t0 + k * BEAT + BEAT / 2, 0.06)
            place(m, hat(), t0 + k * BEAT + BEAT / 4, 0.03)
            place(m, hat(), t0 + k * BEAT + 3 * BEAT / 4, 0.03)
        for k in (1, 3):
            place(m, clap(), t0 + k * BEAT, 0.22)
        place(m, hat(True), t0 + 3.5 * BEAT, 0.07)
    m = m[:N]
    # sidechain-style pump keyed to the beat for the "K-pop" bounce
    t = np.arange(N) / SR
    ph = (t % BEAT) / BEAT
    duck = 1 - 0.28 * np.exp(-ph * 9) * (t > 4 * BEAT)
    m *= duck
    # outro: let the last 0.8 s ring out
    m *= np.clip((DUR - t) / 0.8, 0, 1) ** 0.7
    return m


def render(cues, path):
    mix = music() * 0.85
    for name, at, gain in cues:
        place(mix, SFX[name](), at, gain)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix *= 0.89 / np.max(np.abs(mix))
    st = np.stack([mix, mix], 1)
    st[:, 0] = np.roll(mix, 9)  # tiny Haas widening
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    render([("cash", 1.0, .5), ("ding", 0.1, .25)], sys.argv[1])
