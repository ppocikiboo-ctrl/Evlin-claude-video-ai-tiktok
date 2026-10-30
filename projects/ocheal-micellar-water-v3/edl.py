"""Edit decision list for the O'CHEAL micellar water TikTok ad, version 3.

Source: src/original.mp4 (third UGC take, 38.4 s, 1080x1920, 30 fps).
Times are seconds of the source. Speed > 1 is a speed ramp, < 1 is an
optical-flow slow motion. Same API as ../ocheal-micellar-water/edl.py.
"""

FPS = 30
W, H = 1080, 1920

# name, src_in, src_out, speed, zoom (start, end), what happens in the footage
SEGMENTS = [
    ("hook",    32.10, 33.80, 1.00, (1.10, 1.02), "both used pads held up to camera"),
    ("product",  0.00,  1.25, 1.00, (1.04, 1.10), "bottle beside face, pad on top"),
    ("pump",     2.90,  6.00, 1.50, (1.02, 1.08), "pad pressed on the pump, dispensing"),
    ("press",    9.30, 10.60, 1.00, (1.08, 1.02), "pads held on both cheeks"),
    ("eye",     15.90, 17.40, 1.00, (1.02, 1.08), "pad wiped over closed eye"),
    ("eye2",    27.00, 29.00, 1.40, (1.06, 1.00), "under-eye wipe"),
    ("wipe",    19.40, 22.50, 1.50, (1.00, 1.05), "cheek and chin wipes"),
    ("result",  34.40, 38.00, 1.00, (1.02, 1.10), "clean face, smile"),
    ("cta",      0.00,  1.25, 0.50, (1.04, 1.16), "bottle close-up, slow motion"),
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
