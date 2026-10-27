"""Cut, retime and colour-grade the original footage into a 30 s base clip.

Output: build/base.mp4 (1080x1920, 30 fps, no audio).
"""
import subprocess
import sys
from pathlib import Path

from config import BUILD, DURATION, FPS, GRADE, H, ROOT, SHOTS, W


def shot_chain(i, shot):
    span = shot["src_out"] - shot["src_in"]
    played = span * 2 if shot.get("boomerang") else span
    speed = played / shot["dur"]
    trim = f"trim=start={shot['src_in']}:end={shot['src_out']},setpts=PTS-STARTPTS"
    norm = f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS * 2}"
    if shot.get("boomerang"):
        head = (
            f"[0:v]{trim},{norm},split[f{i}][r{i}];"
            f"[r{i}]reverse[rv{i}];[f{i}][rv{i}]concat=n=2:v=1[b{i}];[b{i}]"
        )
    else:
        head = f"[0:v]{trim},{norm},"
    # Slow down, then blend neighbouring frames back up to 30 fps so the
    # slow-motion stays smooth without warping the packaging.
    tail = (
        f"setpts=(PTS-STARTPTS)/{speed:.5f},framerate=fps={FPS}:interp_start=0:interp_end=255,"
        f"trim=duration={shot['dur']},setpts=PTS-STARTPTS[s{i}]"
    )
    return head + tail


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "input" / "original.mp4"
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "base.mp4"
    chains = [shot_chain(i, s) for i, s in enumerate(SHOTS)]
    joined = "".join(f"[s{i}]" for i in range(len(SHOTS)))
    graph = ";".join(chains) + f";{joined}concat=n={len(SHOTS)}:v=1,tpad=stop_mode=clone:stop_duration=0.2,{GRADE},format=yuv420p[v]"
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-filter_complex", graph, "-map", "[v]", "-an",
        "-r", str(FPS), "-t", str(DURATION),
        "-c:v", "libx264", "-preset", "medium", "-crf", "14", str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"base clip -> {out}")


if __name__ == "__main__":
    main()
