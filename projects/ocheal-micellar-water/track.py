"""Step 2: track the pink O'CHEAL cap through the product shots.

The cap is the most saturated pink object in frame, so a hue mask plus
nearest-blob association is enough. Each segment is seeded at a frame where
the cap is clearly visible, then tracked forwards and backwards from there.
Output: build/track.json  {frame_index: [x, y, confidence]} in 1080x1920 px.
"""
import json
from pathlib import Path

import cv2
import numpy as np

from edl import FPS, H, W, seg_end, seg_start

ROOT = Path(__file__).resolve().parent
SCALE = 4  # analyse at 270x480

# segment -> (seed time on output timeline, seed x, seed y normalised)
SEEDS = {
    "intro": (3.0, 0.72, 0.44),
    "lift": (5.8, 0.52, 0.40),
    "label": (7.4, 0.59, 0.39),
    "closer": (9.6, 0.83, 0.50),
    "pump": (11.8, 0.62, 0.52),
    "hero": (28.1, 0.56, 0.45),
}
GATE = 34  # max jump between frames, analysis px


def cap_blobs(frame):
    small = cv2.resize(frame, (W // SCALE, H // SCALE), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    mask = (((h >= 165) | (h <= 6)) & (s > 90) & (v > 90)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    n, _, stats, cents = cv2.connectedComponentsWithStats(mask)
    return [(cents[i][0], cents[i][1], stats[i, cv2.CC_STAT_AREA], stats[i, cv2.CC_STAT_TOP])
            for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 25]


def follow(frames_blobs, order, start, snap=80):
    pos, conf, out = np.array(start, float), 1.0, {}
    for k, i in enumerate(order):
        best, bd = None, snap if k == 0 else GATE
        for cx, cy, area, top in frames_blobs[i]:
            d = np.hypot(cx - pos[0], cy - pos[1])
            if d < bd:
                best, bd = (cx, cy), d
        if best is not None:
            pos = np.array(best) if k == 0 else 0.35 * pos + 0.65 * np.array(best)
            conf = min(1.0, conf + 0.25)
        else:
            conf *= 0.8
        out[i] = (pos.copy(), conf)
    return out


def smooth(track, f0, f1, radius=4):
    xs = np.array([track[i][0] for i in range(f0, f1)])
    cs = np.array([track[i][1] for i in range(f0, f1)])
    k = np.ones(2 * radius + 1) / (2 * radius + 1)
    pad = np.pad(xs, ((radius, radius), (0, 0)), mode="edge")
    sm = np.stack([np.convolve(pad[:, j], k, mode="valid") for j in range(2)], 1)
    return {f0 + i: [float(sm[i, 0] * SCALE), float(sm[i, 1] * SCALE), float(cs[i])] for i in range(len(sm))}


def main():
    cap = cv2.VideoCapture(str(ROOT / "build" / "base.mp4"))
    blobs = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        blobs.append(cap_blobs(frame))
    result = {}
    for name, (ts, sx, sy) in SEEDS.items():
        f0, f1 = round(seg_start(name) * FPS), min(round(seg_end(name) * FPS), len(blobs))
        fs = round(ts * FPS)
        seed = (sx * W / SCALE, sy * H / SCALE)
        tr = follow(blobs, range(fs, f1), seed)
        tr.update(follow(blobs, range(fs, f0 - 1, -1), seed))
        result.update(smooth(tr, f0, f1))
    (ROOT / "build" / "track.json").write_text(json.dumps(result))
    print(f"tracked {len(result)} frames")


if __name__ == "__main__":
    main()
