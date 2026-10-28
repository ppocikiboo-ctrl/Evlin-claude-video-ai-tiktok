"""Edit decision list for the O'CHEAL micellar water TikTok ad.

Every segment points at a real moment in the original UGC clip
(src/original.mp4, 96 s, 1080x1920, 30 fps). Times are in seconds of the
source. Speed > 1 is a speed ramp, < 1 is an optical-flow slow motion.
"""

FPS = 30
W, H = 1080, 1920

# name, src_in, src_out, speed, zoom (start, end), what happens in the footage
SEGMENTS = [
    ("hook",     53.80, 55.70, 1.00, (1.14, 1.02), "cotton pad lands on cheek, first wipe"),
    ("intro",    17.60, 20.60, 1.00, (1.00, 1.06), "two bottles brought up to camera"),
    ("lift",     21.55, 23.10, 1.00, (1.04, 1.00), "single bottle lifted and turned"),
    ("label",    23.10, 24.15, 0.60, (1.00, 1.08), "front label held steady, slowed"),
    ("closer",   40.00, 42.40, 1.00, (1.06, 1.00), "bottle close to lens, pad on pump"),
    ("pump",     44.60, 48.40, 1.45, (1.00, 1.05), "pad pressed onto the dispenser pump"),
    ("press",    76.80, 78.90, 1.00, (1.03, 1.08), "pads held on both eyes"),
    ("wipe",     57.40, 60.40, 1.25, (1.00, 1.04), "pad wiped across forehead"),
    ("wipe2",    63.40, 67.20, 1.30, (1.05, 1.00), "nose and cheek wipe"),
    ("wipe3",    68.50, 73.50, 1.50, (1.00, 1.05), "cheek and jaw wipe"),
    ("clean",    92.00, 94.90, 1.00, (1.06, 1.00), "clean face, smile"),
    ("hero",     22.60, 24.00, 0.50, (1.02, 1.14), "product close-up, slow motion"),
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
