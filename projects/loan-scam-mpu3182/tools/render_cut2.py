"""Render the edited talk track: video by frame-select, audio by per-piece atrim + 8 ms fades (no clicks)."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
S = sys.argv[1]; edl = json.load(open(f"{S}/work/edl.json")); os.makedirs(f"{S}/cut", exist_ok=True)
def one(sec):
    ps = [p for p in edl["pieces"] if p["sec"] == sec["id"]]; v = sec["src"]
    vexpr = "+".join(f"between(n,{round(p['in']*30)},{round(p['out']*30)-1})" for p in ps)
    af = []
    for i, p in enumerate(ps):
        a, b = round(p["in"]*30)/30, round(p["out"]*30)/30; d = b - a
        af.append(f"[1:a]atrim=start={a:.5f}:end={b:.5f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(d-0.008,0):.5f}:d=0.008[a{i}]")
    fc = f"[0:v]select='{vexpr}',setpts=N/30/TB[v];" + ";".join(af) + ";" + "".join(f"[a{i}]" for i in range(len(ps))) + f"concat=n={len(ps)}:v=0:a=1[a]"
    out = f"{S}/cut/{sec['id']}.mov"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"{S}/cfr/{v}_v.mp4","-i",f"{S}/cfr/{v}_a.wav","-filter_complex",fc,
        "-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","17","-g","30","-pix_fmt","yuv420p",
        "-c:a","pcm_s16le","-ar","48000","-threads","2",out], check=True)
    print(sec["id"], "ok", flush=True); return out
with ThreadPoolExecutor(2) as ex: outs = list(ex.map(one, edl["sections"]))
open(f"{S}/cut/list.txt","w").write("".join(f"file '{p}'\n" for p in outs))
