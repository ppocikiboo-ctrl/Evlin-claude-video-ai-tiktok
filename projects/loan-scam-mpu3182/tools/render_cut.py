import json, subprocess, sys, os
S=sys.argv[1]; edl=json.load(open(f"{S}/work/edl.json")); os.makedirs(f"{S}/cut",exist_ok=True)
lst=[]
for sec in edl["sections"]:
    ps=[p for p in edl["pieces"] if p["sec"]==sec["id"]]; v=sec["src"]
    expr="+".join(f"between(n,{round(p['in']*30)},{round(p['out']*30)-1})" for p in ps)
    aexpr="+".join(f"between(n,{round(p['in']*30)},{round(p['out']*30)-1})" for p in ps)
    out=f"{S}/cut/{sec['id']}.mp4"
    cmd=["ffmpeg","-v","error","-y","-i",f"{S}/cfr/{v}_v.mp4","-i",f"{S}/cfr/{v}_a.wav",
      "-filter_complex",f"[0:v]select='{expr}',setpts=N/30/TB[v];[1:a]asetnsamples=n=1600:p=1,aselect='{aexpr}',asetpts=N/48000/TB,afade=t=in:d=0.02[a]",
      "-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","16","-g","30","-pix_fmt","yuv420p","-c:a","pcm_s16le","-ar","48000",out.replace(".mp4",".mov")]
    subprocess.run(cmd,check=True); lst.append(out.replace(".mp4",".mov"))
    print(sec["id"], "ok", flush=True)
open(f"{S}/cut/list.txt","w").write("".join(f"file '{p}'\n" for p in lst))
