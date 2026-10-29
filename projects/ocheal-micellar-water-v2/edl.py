"""Edit decision list for the O'CHEAL micellar water TikTok ad, version 2.

Source: src/original.mp4 (second UGC take, 29.8 s, 1080x1920, 30 fps).
Times are seconds of the source. Speed > 1 is a speed ramp, < 1 is an
optical-flow slow motion. Same API as ../ocheal-micellar-water/edl.py.
"""

FPS = 30
W, H = 1080, 1920

# name, src_in, src_out, speed, zoom (start, end), what happens in the footage
SEGMENTS = [
    ("hook",   4.85,  7.35, 1.00, (1.16, 1.04), "pad wiped over lips and cheek"),
    ("intro",  1.50,  4.20, 1.00, (1.00, 1.07), "bottle held up beside face, pad in other hand"),
    ("eyes",  10.70, 11.90, 1.00, (1.04, 1.10), "pad wiped over closed eye"),
    ("lips",  14.60, 15.80, 1.00, (1.10, 1.04), "pad wiped over lips"),
    ("wipe",   7.20,  9.90, 1.35, (1.00, 1.05), "cheek and forehead wipe"),
    ("wipe2", 13.00, 14.40, 1.00, (1.05, 1.00), "forehead and cheek wipe"),
    ("pads",  17.25, 19.30, 1.00, (1.00, 1.06), "both used pads held up to camera"),
    ("soft",  20.00, 24.00, 1.00, (1.02, 1.10), "clean face turning to camera"),
    ("cta",    1.60,  3.40, 0.60, (1.03, 1.15), "bottle close-up, slow motion"),
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
