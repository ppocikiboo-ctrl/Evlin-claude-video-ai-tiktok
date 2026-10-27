"""Original soundtrack: a 120 BPM instrumental electro-pop bed plus SFX.

Everything is synthesized here from scratch, so the result is free of
third-party rights. To use a licensed track instead of the synthesized bed:

    python audio.py --music path/to/licensed_track.mp3

The SFX layer is kept either way. Output: build/soundtrack.wav (48 kHz stereo).
"""
import argparse
import subprocess
import wave

import numpy as np

from config import BUILD, BPM, CUTS, DURATION

SR = 48000
N = int(SR * DURATION)
BEAT = 60 / BPM
rng = np.random.default_rng(42)

# chord per bar (2 s): Fmaj7 - G6 - Em7 - Am7, in MIDI notes
CHORDS = [[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [57, 60, 64, 67]]
ROOTS = [41, 43, 40, 45]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def stereo(x, pan=0.0):
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * left, x * right], axis=1) * np.sqrt(2)


def place(bus, sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(bus) or i + len(sig) <= 0:
        return
    sig = stereo(sig, pan) if sig.ndim == 1 else sig
    j = max(0, -i)
    end = min(len(bus), i + len(sig))
    bus[max(0, i):end] += sig[j:j + end - max(0, i)] * gain


def fft_filter(x, lo=None, hi=None, order=2):
    """Zero-phase Butterworth-magnitude band filter (static cutoffs)."""
    n = len(x)
    X = np.fft.rfft(x, n * 2)
    f = np.fft.rfftfreq(n * 2, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        g /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, n * 2)[:n]


def sweep_lp(x, fc):
    """One-pole low-pass with a per-sample cutoff (for whooshes and risers)."""
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s)
        y[i] = s
    return y


def reverb(x, seconds=1.8, decay=0.55, mix=0.3):
    n = int(SR * seconds)
    ir = rng.standard_normal((n, 2)) * np.exp(-tt(n) / decay)[:, None]
    ir[:, 0] = fft_filter(ir[:, 0], hi=6000)
    ir[:, 1] = fft_filter(ir[:, 1], hi=6000)
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    out = np.zeros_like(x)
    L = len(x) + n
    for c in range(2):
        out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], L) * np.fft.rfft(ir[:, c], L), L)[:len(x)]
    return x * (1 - mix) + out * mix * 3


# ------------------------------------------------------------------ instruments

def kick():
    t = tt(int(0.45 * SR))
    f = 46 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.25
    return np.tanh((body + click) * 1.6) * 0.9


def clap():
    t = tt(int(0.3 * SR))
    env = np.zeros_like(t)
    for d in (0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) * (90 if d < 0.02 else 18)), 0)
    return fft_filter(rng.standard_normal(len(t)), lo=900, hi=5200) * env * 0.5


def hat(open_=False):
    t = tt(int((0.25 if open_ else 0.06) * SR))
    return fft_filter(rng.standard_normal(len(t)), lo=7000) * np.exp(-t * (14 if open_ else 70)) * 0.22


def saw(f, t, harmonics=10, bright=1.0):
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        out += np.sin(2 * np.pi * f * k * t) / k * np.exp(-(k - 1) / (3 * bright))
    return out


def bass_note(m, dur):
    t = tt(int(dur * SR))
    env = np.minimum(1, t / 0.005) * np.exp(-t * 3.5)
    return np.tanh(saw(hz(m), t, 8, 0.8) * 1.3) * env * 0.42


def pad_chord(notes, dur, bright=0.7):
    t = tt(int(dur * SR))
    env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.3)
    out = np.zeros((len(t), 2))
    for m in notes:
        for det, pan in ((-0.12, -0.7), (0.0, 0.0), (0.12, 0.7)):
            v = saw(hz(m + 12) * 2 ** (det / 12), t + rng.uniform(0, 0.01), 7, bright)
            out += stereo(v, pan)
    return out * env[:, None] * 0.035


def pluck(m, dur=0.35):
    t = tt(int(dur * SR))
    f = hz(m)
    v = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return v * np.minimum(1, t / 0.002) * np.exp(-t * 11) * 0.16


def bell(m, dur=1.6):
    t = tt(int(dur * SR))
    f = hz(m)
    v = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in
            ((1, 1, 2.2), (2.76, 0.4, 4), (5.4, 0.2, 7), (8.9, 0.1, 10)))
    return v * np.minimum(1, t / 0.003) * 0.12


# ------------------------------------------------------------------ sfx

def sfx_impact():
    t = tt(int(1.6 * SR))
    f = 34 + 70 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    boom = fft_filter(rng.standard_normal(len(t)), hi=500) * np.exp(-t * 6) * 0.9
    crack = fft_filter(rng.standard_normal(len(t)), lo=1500) * np.exp(-t * 40) * 0.25
    return np.tanh((sub + boom + crack) * 1.4) * 0.95


def sfx_whoosh(dur=0.55):
    n = int(dur * SR)
    t = tt(n)
    p = t / dur
    fc = 300 + 5200 * np.sin(np.pi * p) ** 2
    x = fft_filter(sweep_lp(rng.standard_normal(n), fc), lo=150)
    env = np.sin(np.pi * p) ** 1.6
    sig = x * env
    sig /= np.abs(sig).max() + 1e-9
    pan = -0.8 + 1.6 * p
    return np.stack([sig * np.cos((pan + 1) * np.pi / 4), sig * np.sin((pan + 1) * np.pi / 4)], axis=1) * 0.5


def sfx_pop():
    t = tt(int(0.12 * SR))
    f = 380 + 900 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * 0.55


def sfx_sparkle(count=6, spread=0.35):
    out = np.zeros(int((spread + 0.5) * SR))
    for _ in range(count):
        f = rng.uniform(3200, 7800)
        n = int(0.4 * SR)
        t = tt(n)
        v = np.sin(2 * np.pi * f * t) * np.exp(-t * 14) * rng.uniform(0.05, 0.12)
        i = int(rng.uniform(0, spread) * SR)
        out[i:i + n] += v
    return out


def sfx_shimmer():
    out = np.zeros(int(2.4 * SR))
    for k, m in enumerate((81, 84, 88, 93, 96)):
        b = bell(m, 2.0) * 0.8
        i = int(k * 0.07 * SR)
        out[i:i + len(b)] += b
    sp = sfx_sparkle(18, 1.0)
    out[:len(sp)] += sp
    return out


def sfx_riser(dur=2.0):
    n = int(dur * SR)
    t = tt(n)
    p = t / dur
    noise = sweep_lp(rng.standard_normal(n), 400 + 9000 * p ** 2)
    noise = fft_filter(noise, lo=250)
    f = 180 + 1300 * p ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    return (noise * 0.6 + tone) * p ** 2.2 * 0.5


# ------------------------------------------------------------------ arrangement

def music():
    drums = np.zeros((N, 2))
    synth = np.zeros((N, 2))
    bass = np.zeros((N, 2))
    k, c = kick(), clap()
    beats = int(DURATION / BEAT)
    for b in range(beats):
        t0 = b * BEAT
        bar = int(t0 // (4 * BEAT))
        tension = 24.0 <= t0 < 25.0
        if t0 < 29.5 and not tension:
            place(drums, k, t0, gain=1.0)
        if 3.0 <= t0 < 29.5 and b % 2 == 1 and not (23.0 <= t0 < 25.0):
            place(drums, c, t0, pan=0.05, gain=0.8)
        if 3.0 <= t0 < 29.5:
            place(drums, hat(), t0 + BEAT / 2, pan=0.25, gain=1.0)
            if t0 >= 6.0:
                place(drums, hat(), t0 + BEAT / 4, pan=-0.3, gain=0.45)
                place(drums, hat(), t0 + 3 * BEAT / 4, pan=-0.3, gain=0.45)
        # bass: offbeat eighths on the bar root
        if t0 < 29.5 and not tension:
            root = ROOTS[bar % 4]
            place(bass, bass_note(root, BEAT / 2), t0 + BEAT / 2, gain=1.0)
            if t0 >= 6.0:
                place(bass, bass_note(root, BEAT / 4), t0 + 3 * BEAT / 4, gain=0.7)
    # snare roll into the CTA
    rt = 23.0
    while rt < 25.0:
        p = (rt - 23.0) / 2.0
        place(drums, c, rt, gain=0.25 + 0.6 * p)
        rt += BEAT / (2 if p < 0.5 else 4)
    # pads
    for bar in range(int(DURATION / (4 * BEAT)) + 1):
        t0 = bar * 4 * BEAT
        if t0 >= 30:
            break
        bright = 0.5 if t0 < 6 else (1.1 if 21 <= t0 < 25 else 0.8)
        place(synth, pad_chord(CHORDS[bar % 4], min(4 * BEAT, 30 - t0), bright), t0)
    # pluck arpeggio, sixteenths, from the drop at 6 s
    s = 6.0
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    i = 0
    while s < 29.5:
        bar = int(s // (4 * BEAT))
        if not (24.0 <= s < 25.0):
            m = CHORDS[bar % 4][pattern[i % 8]] + 24
            pl = pluck(m)
            place(synth, pl, s, pan=-0.3 if i % 2 else 0.3)
            place(synth, pl * 0.35, s + 3 * BEAT / 4, pan=0.5 if i % 2 else -0.5)  # dotted-eighth echo
        s += BEAT / 4
        i += 1
    # final chord hit
    place(synth, pad_chord(CHORDS[3], 1.8, 1.2) * 2.2, 29.5)
    place(drums, k, 29.5, gain=1.0)
    place(bass, bass_note(45, 0.5) * 1.2, 29.5)

    # sidechain pump on pads + bass
    t = tt(N)
    pump = 1 - 0.55 * np.exp(-(t % BEAT) / 0.11)
    pump[(t >= 24.0) & (t < 25.0)] = 1.0
    synth *= pump[:, None]
    bass *= pump[:, None]
    synth = reverb(synth, mix=0.35)
    # 50 ms fade so the first sample doesn't click
    fade_in = np.clip(t / 0.05, 0, 1)
    return (drums * 0.9 + bass * 1.0 + synth * 1.0) * fade_in[:, None]


def sfx():
    bus = np.zeros((N, 2))
    place(bus, sfx_impact(), 0.0, gain=1.0)
    for ct in CUTS:
        if ct in (6, 25):
            continue
        w = sfx_whoosh()
        place(bus, w, ct - 0.4, gain=0.55)
    place(bus, sfx_whoosh(0.7), 5.55, gain=0.5)
    place(bus, sfx_shimmer(), 6.0, gain=0.9)                # product reveal
    for i in range(3):
        place(bus, sfx_pop(), 9.5 + 0.5 * i, gain=0.8)      # one per card
    for ts in (3.4, 4.3, 13.6, 14.1, 14.6, 17.1, 22.2):
        place(bus, sfx_sparkle(5, 0.25), ts, pan=rng.uniform(-0.5, 0.5), gain=0.9)
    place(bus, sfx_riser(2.0), 23.0, gain=0.8)              # build into CTA
    place(bus, sfx_impact() * 0.7, 25.0)
    place(bus, sfx_pop(), 25.6, gain=0.7)
    place(bus, sfx_sparkle(10, 0.6), 25.7, gain=0.9)
    place(bus, sfx_shimmer(), 29.3, gain=0.8)               # soft shimmer tail
    return reverb(bus, seconds=1.2, decay=0.35, mix=0.18)


def load_music(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-t", str(DURATION), "-f", "f32le",
                          "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    out = np.zeros((N, 2))
    out[:min(N, len(x))] = x[:N]
    t = tt(N)
    out *= np.clip((DURATION - t) / 0.8, 0, 1)[:, None]
    return out / (np.abs(out).max() + 1e-9) * 0.7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", help="licensed music file to use instead of the synthesized bed")
    args = ap.parse_args()
    bed = load_music(args.music) if args.music else music()
    mix = bed * 0.75 + sfx() * 0.6
    mix = np.tanh(mix * 1.1)
    t = tt(N)
    mix *= np.clip((DURATION - t) / 0.4, 0, 1)[:, None]
    mix /= np.abs(mix).max() / 10 ** (-1 / 20)  # peak at -1 dBFS
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "soundtrack.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("soundtrack ->", out)


if __name__ == "__main__":
    main()
