"""Cut, retime and grade the original 35 s office clip into a 19 s edit.

    python3 scripts/prep_footage.py [input.mp4]   -> public/footage.mp4

Every shot comes from the original recording (nothing is generated). The
original audio is dropped; the soundtrack is made by scripts/make_audio.py.
Shot lengths are multiples of 0.5 s, so every cut lands on a beat at 120 BPM.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30

# src_in/src_out in seconds of the original; dur = seconds in the edit
SHOTS = [
    dict(src_in=2.0, src_out=11.0, dur=3.0),  # hook: desk work sped up 3x (timelapse)
    dict(src_in=11.7, src_out=15.7, dur=4.0),  # takes out the VBGV pack and shows it
    dict(src_in=17.0, src_out=25.0, dur=4.0),  # opens the pack (2x)
    dict(src_in=24.8, src_out=27.8, dur=3.0),  # holds up a tablet
    dict(src_in=28.4, src_out=30.4, dur=2.0),  # drinks water
    dict(src_in=33.1, src_out=35.0, dur=2.5),  # smiling close-up (slight slow-mo)
]

# Light grade: a little brighter and warmer, gentle contrast and saturation,
# denoise + mild sharpen. Skin and the purple pack stay natural.
GRADE = ",".join([
    "hqdn3d=1.5:1.5:3:3",
    "eq=brightness=0.03:contrast=1.06:saturation=1.08:gamma=1.04",
    "colorbalance=rm=0.03:gm=0.0:bm=-0.02:rh=0.02:bh=0.01",
    "unsharp=5:5:0.5:5:5:0",
])


def chain(i, s):
    speed = (s["src_out"] - s["src_in"]) / s["dur"]
    # speed-ups simply drop frames; slow-downs blend neighbours for smoothness
    resample = f"framerate=fps={FPS}" if speed < 1 else f"fps={FPS}"
    return (
        f"[0:v]trim=start={s['src_in']}:end={s['src_out']},setpts=PTS-STARTPTS,"
        f"scale=1080:1920:flags=lanczos,setsar=1,fps={FPS * 2},"
        f"setpts=(PTS-STARTPTS)/{speed:.5f},{resample},"
        f"trim=duration={s['dur']},setpts=PTS-STARTPTS[s{i}]"
    )


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "input" / "original.mp4"
    total = sum(s["dur"] for s in SHOTS)
    graph = ";".join(chain(i, s) for i, s in enumerate(SHOTS))
    graph += ";" + "".join(f"[s{i}]" for i in range(len(SHOTS)))
    graph += f"concat=n={len(SHOTS)}:v=1,tpad=stop_mode=clone:stop_duration=0.2,{GRADE},format=yuv420p[v]"
    out = ROOT / "public" / "footage.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(src), "-filter_complex", graph,
        "-map", "[v]", "-an", "-r", str(FPS), "-t", str(total),
        "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-movflags", "+faststart", str(out),
    ], check=True)
    print(f"footage -> {out} ({total:.1f} s)")


if __name__ == "__main__":
    main()
