#!/usr/bin/env bash
# Render the MIRORA L-Carnitine TikTok edit.
# Usage: ./render.sh <input.mp4> <output.mp4> [overlay_dir]
set -euo pipefail
IN="$1"; OUT="$2"; OV="${3:-$(mktemp -d)}"
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/render_overlays.py" "$OV" >/dev/null
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")

# Cards: name start end y   (timed to the voice-over of the source clip)
CARDS=(
  "c0_hook       0.00  4.50  150"
  "c1_brand      4.70  8.50  160"
  "c2_benefit    8.60 14.40  150"
  "c2_disclaimer 8.80 14.40  400"
  "c3_pack      15.00 19.30  160"
  "c4_howto     19.30 22.30  160"
  "c5_water     22.30 28.80  160"
  "c6_pack      29.80 36.00  160"
  "c7_cta       36.10 ${DUR}  150"
)

inputs=(-i "$IN"); fc=""; i=1
# Base: warm grade + dynamic punch-in zoom (frame index n, 30fps).
# Hook starts zoomed (1.12) and eases out; each section change gets a small punch.
Z="if(lt(in,135),1.12-0.08*in/135,1.04)"
for b in 141 258 450 579 669 894 1083; do
  Z="if(between(in,$b,$((b+12))),1.10-0.06*(in-$b)/12,$Z)"
done
fc+="[0:v]scale=2160:3840:flags=lanczos,"
fc+="eq=contrast=1.07:saturation=1.12:brightness=0.015:gamma=1.02,"
fc+="colorbalance=rs=0.035:gs=0.01:bs=-0.04:rm=0.02:bm=-0.02,"
fc+="zoompan=z='$Z':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,"
fc+="unsharp=5:5:0.6,vignette=PI/6,format=yuv420p[v0];"
last="v0"
for c in "${CARDS[@]}"; do
  read -r name s e y <<<"$c"
  d=$(python3 -c "print(round($e-$s,3))")
  inputs+=(-loop 1 -framerate 30 -t "$d" -i "$OV/$name.png")
  fc+="[$i:v]format=rgba,fade=t=in:st=0:d=0.22:alpha=1,fade=t=out:st=$(python3 -c "print(max(0,$d-0.22))"):d=0.22:alpha=1,setpts=PTS+$s/TB[o$i];"
  # slide up 40px while fading in
  fc+="[$last][o$i]overlay=x=0:y='$y+40*max(0,1-(t-$s)/0.22)':eof_action=pass[v$i];"
  last="v$i"; i=$((i+1))
done
# Bouncing pointer toward the TikTok Shop basket during the CTA
inputs+=(-loop 1 -framerate 30 -t 6 -i "$OV/arrow.png")
fc+="[$i:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1,setpts=PTS+36.4/TB[ar];"
fc+="[$last][ar]overlay=x=90:y='1330+28*abs(sin((t-36.4)*5))':eof_action=pass[va];"
# Gold progress bar along the top edge
fc+="color=c=0xC49252:s=1080x10:r=30[bar];"
fc+="[va][bar]overlay=x='-w+W*t/$DUR':y=0:shortest=1[vout];"
# Audio: light clean-up + loudness normalised for TikTok (~-14 LUFS)
fc+="[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-14:TP=-1.5:LRA=9[aout]"

ffmpeg -y -v error -stats "${inputs[@]}" -filter_complex "$fc" \
  -map "[vout]" -map "[aout]" -t "$DUR" \
  -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
