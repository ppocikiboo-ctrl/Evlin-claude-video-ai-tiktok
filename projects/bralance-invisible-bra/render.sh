#!/usr/bin/env bash
# Render the Bralance TikTok ad. Usage: ./render.sh <source.mp4> <work_dir> <out.mp4>
set -euo pipefail
SRC=$1; WORK=$2; OUT=$3
HERE=$(cd "$(dirname "$0")" && pwd)
python3 "$HERE/build_overlays.py" "$WORK/ov" >/dev/null
O=$WORK/ov
D=22.9
# name start end  (seconds on the source timeline)
TL=(
  "t_brand 0 22.9"
  "t_hook 0 2.1"
  "t_hook2 2.1 3.2"
  "t_soft 3.2 5.6"
  "c_thin 5.6 7.6"
  "t_sweat 7.6 10.0"
  "c_howto 10.0 12.2"
  "t_mango 12.2 14.6"
  "t_thin 14.6 17.0"
  "t_review 17.0 19.4"
  "t_cta 19.4 22.9"
)
ARGS=(); F=""; prev="[base]"; i=1
for row in "${TL[@]}"; do
  read -r n s e <<<"$row"
  ARGS+=(-loop 1 -framerate 30 -t $D -i "$O/$n.png")
  fo=$(python3 -c "print(round($e-0.15,3))")
  F+="[$i]format=rgba,fade=t=in:st=$s:d=0.15:alpha=1,fade=t=out:st=$fo:d=0.15:alpha=1[o$i];"
  F+="${prev}[o$i]overlay=0:0:enable='between(t,$s,$e)'[v$i];"
  prev="[v$i]"; i=$((i+1))
done
# punch-in on the hook, slow push-in on the "thin" demo
Z="if(lt(it,0.5),1.18-0.36*it,if(between(it,14.6,17.0),1+0.05*(it-14.6),1))"
ffmpeg -y -v error -i "$SRC" "${ARGS[@]}" -filter_complex "\
[0:v]fps=30,scale=1080:1920,setsar=1,\
zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,\
eq=saturation=1.1:contrast=1.04:brightness=0.015,unsharp=5:5:0.4,trim=0:$D,setpts=PTS-STARTPTS[base];\
$F\
[0:a]highpass=f=90,volume=9dB,alimiter=limit=0.9,afade=t=out:st=21.9:d=1,atrim=0:$D[a]" \
  -map "$prev" -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high \
  -c:a aac -b:a 192k -movflags +faststart -t $D "$OUT"
