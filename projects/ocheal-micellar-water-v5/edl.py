"""Edit decision list for the O'CHEAL talking-head ad (version 5).

Source: src/original.mp4 (creator talking to camera, 26.6 s, 1080x1920,
variable frame rate, her own voice). Only the dead air is removed, so the
speech stays continuous. Every kept part plays 1.07x faster (pitch kept)
for a more energetic delivery. Zoom alternates between parts so the jump
cuts read as deliberate punch-ins. Same API as ../ocheal-micellar-water/edl.py.
"""

FPS = 30
W, H = 1080, 1920
SPEED = 1.07

# name, src_in, src_out, speed, zoom (start, end), what happens in the footage
SEGMENTS = [
    ("talk1",   0.00,  7.20, SPEED, (1.00, 1.04), "talking to camera, bottles come up at the end"),
    ("product", 8.15, 19.20, SPEED, (1.12, 1.16), "shows the bottles, pumps onto a pad, first wipe"),
    ("talk2",  19.85, 20.82, SPEED, (1.02, 1.02), "talking"),
    ("talk3",  21.63, 26.55, SPEED, (1.14, 1.08), "talking, holds both bottles up at the end"),
]
# Music-only product tail after she finishes (frozen last frame + CTA).
TAIL = 2.6


def timeline():
    """Return [(name, out_start, out_end, segment)] on the output timeline."""
    out, t = [], 0.0
    for seg in SEGMENTS:
        name, a, b, speed = seg[:4]
        n_frames = round((b - a) / speed * FPS)
        dur = n_frames / FPS
        out.append((name, t, t + dur, seg))
        t += dur
    return out


def seg_start(name):
    for n, s, e, _ in timeline():
        if n == name:
            return s
    raise KeyError(name)


def seg_end(name):
    for n, s, e, _ in timeline():
        if n == name:
            return e
    raise KeyError(name)


SPEECH_END = timeline()[-1][2]
TOTAL = SPEECH_END + TAIL


def src_to_out(t_src):
    """Map a source time to the output timeline (None if it was cut)."""
    for n, s, e, seg in timeline():
        if seg[1] <= t_src <= seg[2]:
            return s + (t_src - seg[1]) / seg[3]
    return None


if __name__ == "__main__":
    for n, s, e, seg in timeline():
        print(f"{n:8s} {s:6.2f} -> {e:6.2f}  ({e - s:4.2f}s)  src {seg[1]:.2f}-{seg[2]:.2f} x{seg[3]}  {seg[5]}")
    print(f"speech ends {SPEECH_END:.2f}s, total with tail {TOTAL:.2f}s")
