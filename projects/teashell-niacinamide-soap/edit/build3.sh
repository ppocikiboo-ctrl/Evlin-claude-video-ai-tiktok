#!/bin/bash
# Edit v3: "Sabun biasa vs TeaShell" split hook -> 3 SEBAB stickers + polaroids -> recap checklist CTA.
# Needs part1.mp4 / part2.mp4 + v1 SFX (build.sh/prep.py), riser.wav (prep2.py) and prep3.py assets.
set -e
S="$1"; cd "$S"
ENC="-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 -ac 2"
H=3.0; E=5.0

# ---------- HOOK v3: split-screen VS ----------
ffmpeg -v error -y -f lavfi -t $H -i color=c=black:s=1080x1920:r=30 \
  -loop 1 -t $H -i v_top.jpg -loop 1 -t $H -i v_bot.jpg -loop 1 -t $H -i v_lt.png -loop 1 -t $H -i v_lb.png -loop 1 -t $H -i v_band.png \
  -f lavfi -t $H -i anullsrc=r=44100:cl=stereo -filter_complex "
  [3:v]format=rgba,fade=in:st=0.15:d=0.15:alpha=1[lt];
  [4:v]format=rgba,fade=in:st=1.05:d=0.15:alpha=1[lb];
  [5:v]format=rgba,fade=in:st=1.8:d=0.12:alpha=1[bd];
  [0:v][1:v]overlay=x=0:y='if(lt(t,0.25),-960+960*(1-pow(1-t/0.25,3)),0)'[a];
  [a][2:v]overlay=x=0:y='if(lt(t,0.9),1920,if(lt(t,1.15),960+960*pow(1-(t-0.9)/0.25,3),960))'[b];
  [b][lt]overlay[c];[c][lb]overlay=x=0:y=960[d];
  [d]drawbox=x=0:y=954:w=1080:h=12:color=white:t=fill[e];
  [e][bd]overlay=x=0:y='if(between(t,1.8,2.0),-40*sin(PI*(t-1.8)/0.2),0)',format=yuv420p[v]" \
  -map "[v]" -map 6:a -t $H $ENC hook3.mp4

# ---------- RECAP END CARD ----------
ffmpeg -v error -y -sseof -0.1 -i part2.mp4 -frames:v 1 -update 1 last2.png
ffmpeg -v error -y -loop 1 -t $E -i last2.png \
  -loop 1 -t $E -i r0.png -loop 1 -t $E -i r1.png -loop 1 -t $E -i r2.png -loop 1 -t $E -i r3.png -loop 1 -t $E -i r4.png \
  -f lavfi -t $E -i anullsrc=r=44100:cl=stereo -filter_complex "
  [0:v]scale=1080:1920,gblur=sigma=28,eq=brightness=-0.22:saturation=0.8,setsar=1[bg];
  [1:v]format=rgba,fade=in:st=0.1:d=0.2:alpha=1[t0];
  [2:v]format=rgba,fade=in:st=0.6:d=0.15:alpha=1[t1];
  [3:v]format=rgba,fade=in:st=1.1:d=0.15:alpha=1[t2];
  [4:v]format=rgba,fade=in:st=1.6:d=0.15:alpha=1[t3];
  [5:v]format=rgba,fade=in:st=2.3:d=0.15:alpha=1[t4];
  [bg][t0]overlay[a];
  [a][t1]overlay=x='if(lt(t,0.8),-300*pow(1-(t-0.6)/0.2,3),0)':y=0[b];
  [b][t2]overlay=x='if(lt(t,1.3),-300*pow(1-(t-1.1)/0.2,3),0)':y=0[c];
  [c][t3]overlay=x='if(lt(t,1.8),-300*pow(1-(t-1.6)/0.2,3),0)':y=0[d];
  [d][t4]overlay=x=0:y='if(gte(t,2.3),-14*abs(sin((t-2.3)*6)),0)',format=yuv420p[v]" \
  -map "[v]" -map 6:a -t $E $ENC end3.mp4

printf "file 'hook3.mp4'\nfile 'part1.mp4'\nfile 'part2.mp4'\nfile 'end3.mp4'\n" > list3.txt
ffmpeg -v error -y -f concat -safe 0 -i list3.txt $ENC base3.mp4

D1=$(ffprobe -v error -show_entries format=duration -of csv=p=0 part1.mp4)
D2=$(ffprobe -v error -show_entries format=duration -of csv=p=0 part2.mp4)
python3 - "$D1" "$D2" <<'PY' > ov3.txt
import sys
H = 3.0; D1, D2 = map(float, sys.argv[1:3])
B = H; A = H + D1; END = A + D2
A_ = 0.24
stickers = [("s1", B+13.0, B+17.0), ("s2", A+0.2, A+4.3), ("s3", A+5.0, A+10.8)]
polas = [("o1", B+6.0, B+9.6), ("o2", B+10.2, B+12.9), ("o3", B+20.0, B+24.0), ("o4", A+6.2, A+8.8)]
pre = "[0:v]eq=brightness=0.02:contrast=1.03:saturation=1.06,setsar=1"
# white flash on the cut between part1 and part2
pre += f",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.8:t=fill:enable='between(t,{A-0.03},{A+0.05})'[g0]"
inputs, chain, sfx = [], [pre], []
idx = 1; prev = "g0"
for n, s, e in stickers:
    inputs.append(f"-loop 1 -t 60 -i {n}.png")
    x = (f"if(lt(t,{s+A_}),-w+(w)*(1-pow(1-(t-{s})/{A_},3)),"
         f"if(gt(t,{e-A_}),-(w)*pow((t-{e-A_})/{A_},3),0))")
    chain.append(f"[{prev}][{idx}:v]overlay=x='{x}':y=30:enable='between(t,{s},{e})'[g{idx}]")
    prev = f"g{idx}"; idx += 1
    sfx += [("ding", s + 0.05), ("whoop_out", e - A_)]
for n, s, e in polas:
    inputs.append(f"-loop 1 -t 60 -i {n}.png")
    # drop from top with a small bounce, fly out to the right
    y = (f"if(lt(t,{s+0.3}),-h+(h+215)*(1-pow(1-(t-{s})/0.3,3))+if(gt(t,{s+0.22}),-14*sin(PI*(t-{s}-0.22)/0.08),0),"
         f"215)")
    x = f"if(gt(t,{e-A_}),W-w-6+(w+10)*pow((t-{e-A_})/{A_},2),W-w-6)"
    chain.append(f"[{prev}][{idx}:v]overlay=x='{x}':y='{y}':enable='between(t,{s},{e})'[g{idx}]")
    prev = f"g{idx}"; idx += 1
    sfx += [("wip_in", s), ("pop", s + 0.28)]
sfx += [("whoosh_big", 0.0), ("buzz", 0.2), ("whoosh_big", 0.85), ("ding", 1.1), ("whoosh_big", 1.72), ("pop", 1.82),
        ("whoosh_big", B - 0.3), ("whoosh_big", A - 0.3), ("whoosh_big", END - 0.3), ("riser", END - 0.4),
        ("tick", END + 0.6), ("tick", END + 1.1), ("tick", END + 1.6), ("ding", END + 2.3)]
vol = {"whoosh_big": 0.5, "wip_in": 0.45, "whoop_out": 0.3, "pop": 0.4, "ding": 0.35, "buzz": 0.35, "tick": 0.5, "riser": 0.3}
mix = []
for j, (n, t) in enumerate(sfx):
    inputs.append(f"-i {n}.wav")
    ms = max(0, int(t * 1000))
    mix.append(f"[{idx + j}:a]adelay={ms}|{ms},volume={vol[n]}[s{j}]")
mix.append(f"[0:a]{''.join(f'[s{j}]' for j in range(len(sfx)))}amix=inputs={len(sfx)+1}:duration=first:normalize=0,alimiter=limit=0.95[aout]")
print(" ".join(inputs)); print(";".join(chain + mix)); print(prev)
PY
IN=$(sed -n 1p ov3.txt); FC=$(sed -n 2p ov3.txt); LAST=$(sed -n 3p ov3.txt)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 base3.mp4)
ffmpeg -v error -y -i base3.mp4 $IN -filter_complex "$FC" -map "[$LAST]" -map "[aout]" -t $DUR $ENC -movflags +faststart final3.mp4
ffprobe -v error -show_entries format=duration,size -of compact final3.mp4
