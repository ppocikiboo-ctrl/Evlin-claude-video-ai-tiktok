"""Synthesize the soundtrack pieces for the VBGV office-routine edit.

Writes to public/audio/:
  music.wav    18.5 s upbeat electro-pop bed, 120 BPM, no vocals (replaces the original audio)
  klik.wav     hologram panel switches on
  tiktik.wav   text typing in
  ting.wav     panel fully activated
  whoosh.wav   panel sliding in
  sparkle.wav  stars / butterflies / sakura appearing
  boom.wav     the hook's opening impact (frame 0)
  pop, clink, plink, bloop   icon pops, dumbbell reps, sweat drops, water bottle

Everything is generated here from scratch (no samples), so the audio is free
to use commercially. Remotion places the SFX on the timeline (src/timeline.ts).
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
BPM = 120
BEAT = 60 / BPM
OUT = Path(__file__).resolve().parent.parent / "public" / "audio"
rng = np.random.default_rng(11)

# one chord per bar (2 s), the bright K-pop IV-V-iii-vi in F:
# Bbmaj7 - C6 - Am7 - Dm9, looped, then Fmaj9 to end
CHORDS = [[58, 62, 65, 69, 74], [60, 64, 67, 69, 72], [57, 60, 64, 67, 72], [62, 65, 69, 72, 76],
          [58, 62, 65, 69, 74], [65, 69, 72, 76, 79]]
ROOTS = [34, 36, 33, 38, 34, 41]
DURATION = 18.5
LOOP = 4  # the first four chords repeat; CHORDS[-1] is the ending chord


def bar_chord(t0):
    return CHORDS[int(t0 // 2) % LOOP]


def bar_root(t0):
    return ROOTS[int(t0 // 2) % LOOP]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def stereo(x, pan=0.0):
    return np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], axis=1) * np.sqrt(2)


def place(bus, sig, t0, pan=0.0, gain=1.0):
    sig = stereo(sig, pan) if sig.ndim == 1 else sig
    i = int(t0 * SR)
    end = min(len(bus), i + len(sig))
    if end > i:
        bus[i:end] += sig[:end - i] * gain


def band(x, lo=None, hi=None, order=2):
    n = len(x)
    X = np.fft.rfft(x, n * 2)
    f = np.fft.rfftfreq(n * 2, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        g /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, n * 2)[:n]


def reverb(x, seconds=2.0, decay=0.7, mix=0.3):
    n = int(SR * seconds)
    out = np.zeros_like(x)
    L = len(x) + n
    for c in range(2):
        ir = band(rng.standard_normal(n), hi=7000) * np.exp(-tt(n) / decay)
        ir /= np.sqrt((ir ** 2).sum())
        out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], L) * np.fft.rfft(ir, L), L)[:len(x)]
    return x * (1 - mix) + out * mix * 3


def write(name, x, peak=0.89):
    x = x if x.ndim == 2 else stereo(x)
    x = x / (np.abs(x).max() + 1e-9) * peak
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    print("  ", name, f"{len(x) / SR:.2f}s")


# ------------------------------------------------------------------ instruments

def kick():
    t = tt(int(0.4 * SR))
    f = 50 + 100 * np.exp(-t * 30)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) * 1.5) * 0.8


def snap():
    t = tt(int(0.25 * SR))
    return band(rng.standard_normal(len(t)), lo=1200, hi=6000) * np.exp(-t * 35) * 0.45


def shaker():
    t = tt(int(0.07 * SR))
    env = np.minimum(1, t / 0.01) * np.exp(-t * 60)
    return band(rng.standard_normal(len(t)), lo=6000) * env * 0.12


def soft_saw(f, t, n=7, bright=0.7):
    return sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-(k - 1) / (3 * bright)) for k in range(1, n + 1))


def pad(notes, dur):
    t = tt(int(dur * SR))
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.4)
    out = np.zeros((len(t), 2))
    for m in notes:
        for det, pan in ((-0.1, -0.6), (0.1, 0.6)):
            out += stereo(soft_saw(hz(m) * 2 ** (det / 12), t), pan)
    return out * env[:, None] * 0.03


def bell_pluck(m, dur=0.6):
    t = tt(int(dur * SR))
    f = hz(m)
    v = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 6) \
        + 0.15 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 9)
    return v * np.minimum(1, t / 0.002) * np.exp(-t * 6) * 0.13


def sub(m, dur):
    t = tt(int(dur * SR))
    return np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / 0.01) * np.exp(-t * 2.5) * 0.5


def music(dur=DURATION):
    n = int(dur * SR)
    drums, inst = np.zeros((n, 2)), np.zeros((n, 2))
    k, s = kick(), snap()
    for b in range(int(dur / BEAT)):
        t0 = b * BEAT
        if t0 >= DURATION - 0.5:
            break
        place(drums, k, t0, gain=0.85)  # full energy from frame 0, under the hook
        if b % 2 == 1:
            place(drums, s, t0, gain=0.8)
        for q in range(4):
            place(drums, shaker(), t0 + q * BEAT / 4, pan=0.35, gain=0.6 if q % 2 else 1.0)
        place(inst, sub(bar_root(t0), BEAT * 0.9), t0 + BEAT / 2, gain=0.8)
        # bouncy chord stab on the off-beat, the K-pop "bubble" feel
        stab = sum(bell_pluck(m + 12, 0.25) for m in bar_chord(t0)[1:4])
        place(inst, stab * 0.55, t0 + BEAT / 2, pan=0.2 if b % 2 else -0.2)
    bars = int(np.ceil(dur / 2.0))
    for bar in range(bars):
        notes = CHORDS[-1] if bar == bars - 1 else CHORDS[bar % LOOP]
        place(inst, pad(notes, min(2.0, dur - bar * 2.0)), bar * 2.0)
    # bell arpeggio in eighths
    pattern = [0, 2, 4, 3, 1, 2, 4, 2]
    i, t0 = 0, 0.0
    end = DURATION - 0.5
    while t0 < end:
        notes = bar_chord(t0)
        place(inst, bell_pluck(notes[pattern[i % 8]] + 12), t0, pan=-0.35 if i % 2 else 0.35)
        # airy sparkle layer an octave up on the off-beats
        if i % 2:
            place(inst, bell_pluck(notes[pattern[(i + 3) % 8]] + 24, 0.4) * 0.35, t0 + BEAT / 4, pan=0.6 if i % 4 == 1 else -0.6)
        t0 += BEAT / 2
        i += 1
    place(inst, bell_pluck(CHORDS[-1][4] + 24, 1.5) * 1.2, end)
    place(drums, k, end, gain=0.9)
    # gentle sidechain pump
    t = tt(n)
    pump = 1 - 0.45 * np.exp(-(t % BEAT) / 0.12)
    inst *= pump[:, None]
    mix = reverb(inst, mix=0.32) + drums
    mix *= np.clip(t / 0.03, 0, 1)[:, None] * np.clip((dur - t) / 0.5, 0, 1)[:, None]
    return np.tanh(mix * 1.2)


# ------------------------------------------------------------------ sfx

def klik():
    t = tt(int(0.09 * SR))
    click = band(rng.standard_normal(len(t)), lo=2500) * np.exp(-t * 900)
    blip = np.sin(2 * np.pi * (2200 - 900 * t / 0.09) * t) * np.exp(-t * 70) * 0.6
    low = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90) * 0.5
    return click + blip + low


def tik(f=4200):
    t = tt(int(0.04 * SR))
    return (np.sin(2 * np.pi * f * t) * 0.7 + band(rng.standard_normal(len(t)), lo=5000) * 0.5) * np.exp(-t * 220)


def tiktik():
    x = np.zeros(int(0.16 * SR))
    a, b = tik(4200), tik(4700)
    x[:len(a)] += a
    i = int(0.075 * SR)
    x[i:i + len(b)] += b
    return x


def ting():
    t = tt(int(1.2 * SR))
    f = hz(93)  # A6
    v = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in
            ((1, 1, 3.5), (2.0, 0.35, 5), (2.76, 0.3, 6), (5.4, 0.12, 9)))
    return reverb(stereo(v * np.minimum(1, t / 0.002)), 1.0, 0.4, 0.25)


def whoosh(dur=0.5):
    n = int(dur * SR)
    t = tt(n)
    p = t / dur
    x = rng.standard_normal(n)
    fc = 300 + 6000 * np.sin(np.pi * p) ** 2
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y, s = np.empty(n), 0.0
    for i in range(n):
        s += a[i] * (x[i] - s)
        y[i] = s
    y = band(y, lo=200) * np.sin(np.pi * p) ** 1.5
    pan = 0.8 - 1.6 * p  # right to left, matching the panel sliding in from the right
    return np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], axis=1)


def sparkle(dur=0.9, count=16):
    out = np.zeros(int((dur + 0.4) * SR))
    for _ in range(count):
        f = rng.uniform(3000, 8000)
        t = tt(int(0.35 * SR))
        v = np.sin(2 * np.pi * f * t) * np.exp(-t * 16) * rng.uniform(0.4, 1.0)
        i = int(rng.uniform(0, dur) ** 1.3 * SR / dur ** 0.3)
        out[i:i + len(v)] += v[: len(out) - i]
    return reverb(stereo(out), 0.8, 0.3, 0.3)


# ------------------------------------------------------------------ playful sfx

def pop():
    """Bubbly pop: quick upward pitch blip."""
    t = tt(int(0.14 * SR))
    f = 300 + 1200 * (1 - np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.8







def clink():
    """Light dumbbell clink: two inharmonic metallic partials."""
    t = tt(int(0.5 * SR))
    v = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((1850, 1, 9), (2940, 0.6, 12), (4720, 0.35, 16)))
    return v * np.minimum(1, t / 0.001) * 0.45


def plink():
    """Water-drop plink for the sweat light drops."""
    t = tt(int(0.3 * SR))
    f = 900 + 1400 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.6



def bloop():
    """Water filling: a few rising bubble bloops."""
    out = np.zeros(int(0.7 * SR))
    for k in range(5):
        t = tt(int(0.12 * SR))
        f0 = 350 + k * 90 + rng.uniform(-20, 20)
        f = f0 + f0 * 1.5 * (1 - np.exp(-t * 50))
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * 0.5
        i = int(k * 0.11 * SR)
        out[i:i + len(b)] += b
    return out



def boom():
    """Hook impact: deep sub drop + punchy body + bright crack, with a tail."""
    t = tt(int(1.6 * SR))
    f = 32 + 90 * np.exp(-t * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    body = band(rng.standard_normal(len(t)), hi=600) * np.exp(-t * 8) * 0.9
    crack = band(rng.standard_normal(len(t)), lo=2500) * np.exp(-t * 45) * 0.35
    return reverb(stereo(np.tanh((sub + body + crack) * 1.6)), 1.4, 0.5, 0.2)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write("music.wav", music(), peak=0.8)
    write("boom.wav", boom(), peak=0.95)
    write("klik.wav", klik())
    write("tiktik.wav", tiktik(), peak=0.7)
    write("ting.wav", ting(), peak=0.75)
    write("whoosh.wav", whoosh(), peak=0.7)
    write("sparkle.wav", sparkle(), peak=0.6)
    write("pop.wav", pop(), peak=0.7)
    write("clink.wav", clink(), peak=0.55)
    write("plink.wav", plink(), peak=0.55)
    write("bloop.wav", bloop(), peak=0.6)


if __name__ == "__main__":
    main()
