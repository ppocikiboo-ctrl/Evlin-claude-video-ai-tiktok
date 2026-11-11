#!/bin/bash
# Build edited TeaShell unboxing video: hook + part1 + part2, image cards, whoosh SFX.
set -e
S="$1"; cd "$S"
U=/root/.claude/uploads/878573dd-f1f2-5804-95d9-dddb669af68e
P1=$U/c818d0e0-HnVideoEditor_2026_11_11_211816298.mp4   # unboxing + 6 boxes + box front
P2=$U/d1d6ee69-HnVideoEditor_2026_11_11_211653192.mp4   # soap + foaming net + CTA
FB=/usr/share/fonts/opentype/inter/Inter-Black.otf
FX=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
ENC="-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 -ac 2"

# ---------- 1. HOOK (2.4 s) ----------
ffmpeg -v error -y -ss 4.0 -i "$P1" -frames:v 1 boxes.png
H=2.4
ffmpeg -v error -y \
  -loop 1 -t 1.1 -i hook_foam.jpg \
  -loop 1 -t 1.3 -i boxes.png \
  -f lavfi -t $H -i anullsrc=r=44100:cl=stereo \
  -filter_complex "
   [0:v]scale=1188:2112,zoompan=z='1.0+0.12*on/33':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,trim=duration=1.1,setsar=1[a];
   [1:v]scale=1080:1920,zoompan=z='1.15-0.12*on/39':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,trim=duration=1.3,eq=saturation=1.1,setsar=1[b];
   [a][b]concat=n=2:v=1:a=0,format=yuv420p,
   drawbox=x=0:y=1030:w=1080:h=560:color=black@0.45:t=fill,
   drawtext=fontfile=$FB:text='SAMPAI BELI 6 KOTAK?!':fontsize=80:fontcolor=0xFFE14D:borderw=7:bordercolor=black:x=(w-tw)/2:y=1110:enable='gte(t,0.05)',
   drawtext=fontfile=$FX:text='Busa lembut macam awan':fontsize=62:fontcolor=white:borderw=5:bordercolor=black:x=(w-tw)/2:y=1260:enable='gte(t,0.35)',
   drawtext=fontfile=$FX:text='dalam 3 saat je':fontsize=62:fontcolor=0xFF4D8D:borderw=5:bordercolor=black:x=(w-tw)/2:y=1350:enable='gte(t,0.35)'[v]" \
  -map "[v]" -map 2:a -t $H $ENC hook.mp4

# ---------- 2. Normalise both parts & concat ----------
for i in 1 2; do
  eval SRC=\$P$i
  ffmpeg -v error -y -i "$SRC" -vf "scale=1080:1920,setsar=1,fps=30" $ENC part$i.mp4
done
printf "file 'hook.mp4'\nfile 'part1.mp4'\nfile 'part2.mp4'\n" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt $ENC base.mp4

D1=$(ffprobe -v error -show_entries format=duration -of csv=p=0 part1.mp4)
echo "part1 = $D1"
python3 - "$D1" <<'PY' > overlay_args.txt
import sys
H = 2.4; D1 = float(sys.argv[1])
P2 = H + D1
# (card, start, end) on the final timeline
cards = [
    ("c_soap5",    H + 10.2, H + 12.8),   # "dalam sabun TeaShell / Niacinamide soap"
    ("c_layers",   H + 20.0, H + 23.2),   # "niacinamide bantu kulit nampak cerah & sekata"
    ("c_why",      P2 + 0.2, P2 + 3.9),   # "kekalkan kelembapan / tak ketat / tak kering"
    ("c_foamfine", P2 + 6.1, P2 + 8.5),   # "busa ni / so senang kita nak apply"
    ("c_foam3s",   P2 + 11.0, P2 + 13.2), # "kalau korang nak cuba..."
]
CW = 936; X = (1080 - CW) // 2; Y = 110; A = 0.22
inputs, chain, sfx = [], [], []
prev = "0:v"
for i, (c, s, e) in enumerate(cards):
    inputs.append(f"-loop 1 -t 60 -i {c}.png")
    idx = i + 1
    # slide in from the right with ease-out, slide out to the left with ease-in
    x = (f"if(lt(t,{s+A}),{X}+(W-{X})*pow(1-(t-{s})/{A},3),"
         f"if(gt(t,{e-A}),{X}-(W)*pow((t-{e-A})/{A},3),{X}))")
    out = f"v{idx}"
    chain.append(f"[{idx}:v]format=rgba[c{idx}];[{prev}][c{idx}]overlay=x='{x}':y={Y}:enable='between(t,{s},{e})':eof_action=pass[{out}]")
    prev = out
    sfx.append(("wip_in", s - 0.08)); sfx.append(("whoop_out", e - A))
# hook + section whooshes
sfx += [("whoosh_big", 0.0), ("pop", 0.08), ("whoosh_big", 1.0), ("pop", 0.38),
        ("whoosh_big", H - 0.3), ("whoosh_big", P2 - 0.35)]
n = len(cards) + 1
sfx_in, mix = [], []
for j, (name, t) in enumerate(sfx):
    k = n + j
    sfx_in.append(f"-i {name}.wav")
    ms = max(0, int(t * 1000))
    vol = {"whoosh_big": 0.55, "wip_in": 0.5, "whoop_out": 0.35, "pop": 0.4}[name]
    mix.append(f"[{k}:a]adelay={ms}|{ms},volume={vol}[s{j}]")
labels = "".join(f"[s{j}]" for j in range(len(sfx)))
mix.append(f"[0:a]{labels}amix=inputs={len(sfx)+1}:duration=first:normalize=0,alimiter=limit=0.95[aout]")
fc = ";".join(chain + mix)
print(" ".join(inputs + sfx_in))
print(fc)
print(prev)
PY
IN=$(sed -n 1p overlay_args.txt); FC=$(sed -n 2p overlay_args.txt); LAST=$(sed -n 3p overlay_args.txt)
ffmpeg -v error -y -i base.mp4 $IN -filter_complex "$FC" -map "[$LAST]" -map "[aout]" -shortest $ENC -movflags +faststart final.mp4
ffprobe -v error -show_entries format=duration,size -of compact final.mp4
