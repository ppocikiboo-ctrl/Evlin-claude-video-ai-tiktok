import subprocess,re,json,sys
src,out=sys.argv[1],sys.argv[2]
import os
SPEED=float(os.environ.get("SPEED", "1.2")); PAD=0.07
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]))
log=subprocess.run(['ffmpeg','-i',src,'-af','silencedetect=noise=-32dB:d=0.2','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]
en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
sil=list(zip(st,en+[dur]*(len(st)-len(en))))
keep=[];t=0.0
for a,b in sil:
    a2=a+PAD if a>0.01 else 0; b2=max(b-PAD,a2)
    if a2>t: keep.append((t,a2))
    t=b2
if dur-t>0.05: keep.append((t,dur))
keep=[(round(a,3),round(b,3)) for a,b in keep if b-a>0.1]
print(keep, sum(b-a for a,b in keep)/SPEED)
fc=''.join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.03:.3f}:d=0.03[a{i}];" for i,(a,b) in enumerate(keep))
fc+=''.join(f"[v{i}][a{i}]" for i in range(len(keep)))+f"concat=n={len(keep)}:v=1:a=1[vc][ac];[vc]setpts=PTS/{SPEED},fps=30[vo];[ac]atempo={SPEED}[ao]"
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-c:v','libx264','-crf','14','-preset','fast','-c:a','pcm_s16le',out],check=True)
# segment boundaries in output time + mapping
segs=[];o=0
for a,b in keep:
    segs.append({"src":[a,b],"out":[o/SPEED,(o+b-a)/SPEED]}); o+=b-a
json.dump(segs,open(out+'.json','w'),indent=1)
