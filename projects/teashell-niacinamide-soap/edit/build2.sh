#!/bin/bash
# Edit v2: problem hook -> unboxing with FAB pills + circle bubbles -> CTA end card.
# Needs part1.mp4 / part2.mp4 from build.sh and assets from prep2.py.
set -e
S="$1"; cd "$S"
FB=/usr/share/fonts/opentype/inter/Inter-Black.otf
DJ=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
ENC="-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 -ac 2"
sed -i 's/("KENAPA KENA KLIK SEKARANG?", BLACK, 66/("KENAPA KENA KLIK SEKARANG?", BLACK, 56/' prep2.py

# ---------- HOOK v2 (2.6 s, 3 fast cuts + flash) ----------
ZP="zoompan=z='1.0+0.10*on/27':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30"
ffmpeg -v error -y -loop 1 -t 0.9 -i h1.jpg -loop 1 -t 0.9 -i h2.jpg -loop 1 -t 0.8 -i h3.jpg \
  -f lavfi -t 2.6 -i anullsrc=r=44100:cl=stereo -filter_complex "
  [0:v]scale=1188:2112,$ZP,trim=duration=0.9,setsar=1[a];
  [1:v]scale=1188:2112,$ZP,trim=duration=0.9,setsar=1[b];
  [2:v]scale=1188:2112,$ZP,trim=duration=0.8,setsar=1[c];
  [a][b][c]concat=n=3:v=1:a=0,format=yuv420p,
  drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='between(t,0.88,0.95)+between(t,1.78,1.85)',
  drawbox=x=0:y=1060:w=1080:h=470:color=black@0.55:t=fill,
  drawtext=fontfile=$FB:text='MUKA KETAT & KUSAM':fontsize=84:fontcolor=0xFFE14D:borderw=7:bordercolor=black:x=(w-tw)/2:y=1110,
  drawtext=fontfile=$FB:text='LEPAS CUCI?':fontsize=96:fontcolor=0xFFE14D:borderw=7:bordercolor=black:x=(w-tw)/2:y=1215,
  drawtext=fontfile=$DJ:text='Tengok sabun busa 3 saat ni ↓':fontsize=54:fontcolor=white:borderw=5:bordercolor=black:x=(w-tw)/2:y=1375:enable='gte(t,0.9)'[v]" \
  -map "[v]" -map 3:a -t 2.6 $ENC hook2.mp4

# ---------- CTA END CARD (5.5 s) ----------
E=5.5
ffmpeg -v error -y -loop 1 -t $E -i end_bg.jpg -loop 1 -t $E -i end_box.png \
  -loop 1 -t $E -i e0.png -loop 1 -t $E -i e1.png -loop 1 -t $E -i e2.png -loop 1 -t $E -i e3.png -loop 1 -t $E -i e4.png \
  -f lavfi -t $E -i anullsrc=r=44100:cl=stereo -filter_complex "
  [0:v]scale=1188:2112,zoompan=z='1.0+0.08*on/165':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,trim=duration=$E,setsar=1[bg];
  [1:v]format=rgba,fade=in:st=0:d=0.25:alpha=1[bx];
  [2:v]format=rgba,fade=in:st=0.15:d=0.2:alpha=1[t0];
  [3:v]format=rgba,fade=in:st=0.9:d=0.2:alpha=1[t1];
  [4:v]format=rgba,fade=in:st=1.5:d=0.2:alpha=1[t2];
  [5:v]format=rgba,fade=in:st=2.3:d=0.25:alpha=1[t3];
  [6:v]format=rgba,fade=in:st=3.3:d=0.15:alpha=1[t4];
  [bg][bx]overlay=x=200:y='if(lt(t,0.3),225+300*pow(1-t/0.3,3),225)'[a];
  [a][t0]overlay[b];[b][t1]overlay[c];[c][t2]overlay[d];[d][t3]overlay[e];
  [e][t4]overlay=x=0:y='if(gte(t,3.3),-12*abs(sin((t-3.3)*7)),0)',format=yuv420p[v]" \
  -map "[v]" -map 7:a -t $E $ENC end2.mp4

printf "file 'hook2.mp4'\nfile 'part1.mp4'\nfile 'part2.mp4'\nfile 'end2.mp4'\n" > list2.txt
ffmpeg -v error -y -f concat -safe 0 -i list2.txt $ENC base2.mp4

D1=$(ffprobe -v error -show_entries format=duration -of csv=p=0 part1.mp4)
D2=$(ffprobe -v error -show_entries format=duration -of csv=p=0 part2.mp4)
python3 - "$D1" "$D2" <<'PY' > ov2.txt
import sys
H = 2.6; D1, D2 = map(float, sys.argv[1:3]); E = 5.5
B = H; A = H + D1; END = A + D2; TOT = END + E
A_ = 0.22
# pills: (png, start, end)
pills = [("p1", B+7.0, B+9.8), ("p2", B+10.2, B+12.9), ("p3", B+17.0, B+19.9), ("p4", B+20.0, B+24.0),
         ("p5", A+0.2, A+2.1), ("p6", A+2.1, A+4.3), ("p7", A+5.0, A+8.0), ("p8", A+9.0, A+11.0)]
# bubbles: (png, start, end, side)
bubbles = [("b1", B+7.0, B+9.8, "R"), ("b2", B+10.2, B+12.9, "R"), ("b3", B+17.0, B+19.9, "R"),
           ("b4", B+20.0, B+24.0, "R"), ("b5", A+0.2, A+4.3, "L"), ("b6", A+5.0, A+8.0, "L")]
# punch-in zoom moments (start, end)
punch = [(B+5.9, B+7.0), (A+5.0, A+6.0), (A+12.9, A+14.2)]

z = "+".join(f"between(t,{s},{e})*sin(PI*(t-{s})/{e-s})" for s, e in punch)
pre = (f"[0:v]eq=saturation=1.12:contrast=1.04,colorbalance=rm=0.04:bm=-0.04,"
       f"scale=w='2*trunc(540*(1+0.09*({z})))':h='2*trunc(960*(1+0.09*({z})))':eval=frame,"
       f"crop=1080:1920,setsar=1[g0]")
inputs, chain, sfx = [], [pre], []
idx = 1; prev = "g0"
# progress bar
inputs.append(f"-f lavfi -t {TOT} -i color=c=0xFF4D8D:s=1080x10:r=30")
chain.append(f"[{prev}][{idx}:v]overlay=x='-W+W*t/{TOT}':y=0:shortest=1[g{idx}]"); prev = f"g{idx}"; idx += 1
for name, s, e in pills:
    inputs.append(f"-loop 1 -t 60 -i {name}.png")
    y = (f"if(lt(t,{s+A_}),-130+(55+130)*(1-pow(1-(t-{s})/{A_},3)),"
         f"if(gt(t,{e-A_}),55-(185)*pow((t-{e-A_})/{A_},3),55))")
    chain.append(f"[{prev}][{idx}:v]overlay=x=(W-w)/2:y='{y}':enable='between(t,{s},{e})'[g{idx}]")
    prev = f"g{idx}"; idx += 1
    sfx += [("pop", s), ("whoop_out", e - A_)]
for name, s, e, side in bubbles:
    inputs.append(f"-loop 1 -t 60 -i {name}.png")
    X = "W-w-14" if side == "R" else "14"
    off = "W" if side == "R" else "-w"
    x = (f"if(lt(t,{s+0.1+A_}),{off}+(({X})-({off}))*(1-pow(1-max(t-{s}-0.1,0)/{A_},3)),"
         f"if(gt(t,{e-A_}),({X})+(({off})-({X}))*pow((t-{e-A_})/{A_},3),{X}))")
    chain.append(f"[{prev}][{idx}:v]overlay=x='{x}':y=185:enable='between(t,{s},{e})'[g{idx}]")
    prev = f"g{idx}"; idx += 1
    sfx += [("wip_in", s + 0.05)]
sfx += [("whoosh_big", 0.0), ("whoosh_big", 0.8), ("whoosh_big", 1.7), ("pop", 0.95),
        ("whoosh_big", B - 0.3), ("whoosh_big", A - 0.35), ("whoosh_big", END - 0.35),
        ("riser", END - 0.2), ("pop", END + 0.15), ("pop", END + 0.9), ("pop", END + 1.5),
        ("pop", END + 2.3), ("whoosh_big", END + 3.1), ("pop", END + 3.3)]
vol = {"whoosh_big": 0.55, "wip_in": 0.45, "whoop_out": 0.3, "pop": 0.45, "riser": 0.35}
mix = []
for j, (n, t) in enumerate(sfx):
    inputs.append(f"-i {n}.wav")
    ms = max(0, int(t * 1000))
    mix.append(f"[{idx + j}:a]adelay={ms}|{ms},volume={vol[n]}[s{j}]")
mix.append(f"[0:a]{''.join(f'[s{j}]' for j in range(len(sfx)))}amix=inputs={len(sfx)+1}:duration=first:normalize=0,alimiter=limit=0.95[aout]")
print(" ".join(inputs)); print(";".join(chain + mix)); print(prev)
PY
IN=$(sed -n 1p ov2.txt); FC=$(sed -n 2p ov2.txt); LAST=$(sed -n 3p ov2.txt)
ffmpeg -v error -y -i base2.mp4 $IN -filter_complex "$FC" -map "[$LAST]" -map "[aout]" -t $(ffprobe -v error -show_entries format=duration -of csv=p=0 base2.mp4) $ENC -movflags +faststart final2.mp4
ffprobe -v error -show_entries format=duration,size -of compact final2.mp4
