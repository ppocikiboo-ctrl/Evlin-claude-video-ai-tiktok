#!/usr/bin/env bash
# Render the v3 "digicam aesthetic" MIRORA edit.
# Usage: ./render.sh <input.mp4> <output.mp4>
set -euo pipefail
IN="$(realpath "$1")"; OUT="$(realpath -m "$2")"
cd "$(dirname "$0")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
python3 gen_audio.py "$DUR" "$TMP/music.wav" "$TMP/sfx.wav"

# Slow Ken Burns: each section eases from 1.03 to 1.08 zoom, drifting
# alternately left/right (no hard punches — this version is calm and dreamy).
read -r Z X < <(python3 - <<'PY'
from timeline import SECTIONS, FPS
z, x = "1.03", "0"
for i, (_, s, e, *_r) in enumerate(reversed(SECTIONS)):
    a, b = int(s * FPS), int(min(e, 41.2) * FPS)
    p = f"((in-{a})/{max(1, b - a)})"
    d = 1 if (len(SECTIONS) - 1 - i) % 2 == 0 else -1
    z = f"if(gte(in,{a}),1.015+0.03*{p},{z})"
    x = f"if(gte(in,{a}),{d}*20*{p},{x})"
print(z, x)
PY
)

MIX="[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[voice][key];[1:a]volume=0.22[mus];[2:a]volume=0.6[fx];[mus][key]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=400[duck];[voice][duck][fx]amix=inputs=3:normalize=0:duration=first"
L=$(ffmpeg -i "$IN" -i "$TMP/music.wav" -i "$TMP/sfx.wav" -filter_complex "$MIX,ebur128" -f null - 2>&1 | grep -A1 Integrated | tail -1 | awk '{print $2}')
GAIN=$(python3 -c "print(round(-14-($L),2))")

python3 overlay_frames.py "$DUR" | ffmpeg -y -v error -stats \
  -i "$IN" -i "$TMP/music.wav" -i "$TMP/sfx.wav" \
  -f rawvideo -pix_fmt rgba -s 1080x1920 -r 30 -i - \
  -filter_complex "
[0:v]scale=2160:3840:flags=lanczos,
 zoompan=z='$Z':x='iw/2-iw/zoom/2+$X':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,
 curves=all='0/0.07 0.25/0.27 0.5/0.53 0.75/0.78 1/0.96',
 eq=saturation=0.92:contrast=1.02:gamma=1.03,
 colorbalance=rs=0.05:gs=0.01:bs=-0.05:rm=0.04:gm=0.01:bm=-0.03:rh=0.02:bh=-0.04,
 split[a][b];[b]gblur=sigma=24,format=gbrp[blur];[a]format=gbrp[sharp];
 [sharp][blur]blend=all_mode=screen:all_opacity=0.22,format=yuv420p,
 rgbashift=rh=-3:bh=3,
 noise=alls=9:allf=t+u,
 vignette=PI/5[base];
[base][3:v]overlay=0:0:format=auto,format=yuv420p[vout];
$MIX[mixed];
[mixed]volume=${GAIN}dB,alimiter=limit=0.84:level=false[aout]" \
  -map "[vout]" -map "[aout]" -t "$DUR" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
