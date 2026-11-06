"""Step 1: cut, stabilise, speed-ramp and colour-grade the original footage.

Writes build/seg_XX.mp4 for every EDL segment and joins them into
build/base.mp4 (video only, 1080x1920, 30 fps). Audio is replaced later.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

from edl import FPS, H, SEGMENTS, W

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "original.mp4"
BUILD = ROOT / "build"

# Korean-beauty grade: cool cyan wall pulled towards pearl, warm skin, soft
# highlights. Done in RGB so selectivecolor works on real hues.
GRADE = (
    "format=gbrp,"
    "selectivecolor=cyans='-0.40 0.12 0.05 0':blues='-0.25 0.12 0 0',"
    "colorbalance=rs=0.035:bs=-0.02:rm=0.04:gm=-0.01:bm=-0.01:rh=0.02:gh=-0.005:bh=0.01,"
    "eq=contrast=1.06:brightness=0.02:saturation=1.05:gamma=1.03,"
    "unsharp=5:5:0.45"
)


def run(cmd):
    print(" ".join(str(c) for c in cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def build_segment(i, seg):
    name, a, b, speed = seg[:4]
    key = hashlib.md5(repr((seg[:4], GRADE)).encode()).hexdigest()[:8]
    out = BUILD / f"seg_{i:02d}_{key}.mp4"
    trf = BUILD / f"seg_{i:02d}_{key}.trf"
    if out.exists():
        return out
    trim = ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(SRC)]
    # Pass 1: motion analysis for stabilisation.
    run(["ffmpeg", "-v", "error", "-y", *trim,
         "-vf", f"vidstabdetect=shakiness=4:accuracy=12:result={trf}", "-f", "null", "-"])
    chain = [
        f"vidstabtransform=input={trf}:smoothing=12:optzoom=1:zoomspeed=0.2:interpol=bicubic",
        f"scale={W}:{H}:flags=lanczos,setsar=1",
    ]
    if speed > 1:
        chain.append(f"setpts=PTS/{speed}")
    elif speed < 1:
        chain.append(f"setpts=PTS/{speed},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    chain += [f"fps={FPS}", GRADE, "format=yuv420p"]
    n_frames = round((b - a) / speed * FPS)
    run(["ffmpeg", "-v", "error", "-y", *trim, "-an", "-vf", ",".join(chain),
         "-frames:v", str(n_frames), "-c:v", "libx264", "-preset", "medium", "-crf", "12", str(out)])
    return out


def main():
    BUILD.mkdir(exist_ok=True)
    parts = [build_segment(i, seg) for i, seg in enumerate(SEGMENTS)]
    lst = BUILD / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(BUILD / "base.mp4")])


if __name__ == "__main__":
    main()
