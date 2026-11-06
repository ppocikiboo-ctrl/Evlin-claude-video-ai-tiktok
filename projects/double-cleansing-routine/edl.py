"""Edit decision list for the double-cleansing routine TikTok video.

Source: src/original.mp4 (UGC take, 84.8 s, 1280x2276, variable frame rate).
Times are seconds of the source. Speed > 1 is a speed ramp, < 1 is an
optical-flow slow motion. Same API as ../ocheal-micellar-water/edl.py.
"""

FPS = 30
W, H = 1080, 1920

# name, src_in, src_out, speed, zoom (start, end), what happens in the footage
SEGMENTS = [
    ("hook",     0.30,  2.70, 1.00, (1.06, 1.00), "face to camera, bottle brought up"),
    ("explain", 17.60, 20.00, 1.00, (1.00, 1.05), "settles in frame, talking"),
    ("pump",     7.00, 11.00, 1.60, (1.02, 1.08), "pad pressed on the pump"),
    ("wipe",    20.00, 23.00, 1.40, (1.00, 1.05), "forehead and cheek wipes"),
    ("eyes",    39.50, 41.80, 1.00, (1.04, 1.10), "pads held on both eyes"),
    ("mouth",   29.60, 32.00, 1.20, (1.06, 1.00), "two pads around mouth and chin"),
    ("neck",    46.30, 48.20, 1.00, (1.00, 1.06), "pad wiped down the neck, chin up"),
    ("repeat",  52.00, 55.00, 1.60, (1.04, 1.00), "more cheek and forehead wipes"),
    ("clean",   77.50, 80.50, 1.00, (1.02, 1.08), "clean face close to camera"),
    ("smile",   80.50, 83.50, 1.00, (1.06, 1.00), "clean face, smile"),
    ("cta",      1.50,  2.70, 0.50, (1.04, 1.14), "bottle beside face, slow motion"),
]


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


TOTAL = timeline()[-1][2]

if __name__ == "__main__":
    for n, s, e, seg in timeline():
        print(f"{n:8s} {s:6.2f} -> {e:6.2f}  ({e - s:4.2f}s)  src {seg[1]:.2f}-{seg[2]:.2f} x{seg[3]}  {seg[5]}")
    print(f"total {TOTAL:.2f}s")
