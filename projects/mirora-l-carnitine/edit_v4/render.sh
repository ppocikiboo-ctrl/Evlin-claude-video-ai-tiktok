#!/usr/bin/env bash
# Render the v4 "sticker meme" MIRORA edit (16.6s clip).
# No zoom/crop on the footage and all stickers stay in the top band,
# so the product and the original captions are never covered.
# Usage: ./render.sh <input.mp4> <output.mp4>
set -euo pipefail
IN="$(realpath "$1")"; OUT="$(realpath -m "$2")"
cd "$(dirname "$0")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
python3 gen_audio.py "$DUR" "$TMP/music.wav" "$TMP/sfx.wav"

MIX="[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[voice][key];[1:a]volume=0.2[mus];[2:a]volume=0.6[fx];[mus][key]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=300[duck];[voice][duck][fx]amix=inputs=3:normalize=0:duration=first"
L=$(ffmpeg -i "$IN" -i "$TMP/music.wav" -i "$TMP/sfx.wav" -filter_complex "$MIX,ebur128" -f null - 2>&1 | grep -A1 Integrated | tail -1 | awk '{print $2}')
GAIN=$(python3 -c "print(round(-14-($L),2))")

python3 overlay_frames.py "$DUR" | ffmpeg -y -v error -stats \
  -i "$IN" -i "$TMP/music.wav" -i "$TMP/sfx.wav" \
  -f rawvideo -pix_fmt rgba -s 1080x1920 -r 30 -i - \
  -filter_complex "
[0:v]scale=1080:1920:flags=lanczos,
 curves=all='0/0 0.5/0.49 0.85/0.82 1/0.95',
 eq=contrast=1.06:saturation=1.12,
 colorbalance=rs=0.02:bs=-0.02:rh=-0.02:bh=0.01,
 unsharp=5:5:0.5,format=yuv420p[base];
[base][3:v]overlay=0:0:format=auto,format=yuv420p[vout];
$MIX[mixed];
[mixed]volume=${GAIN}dB,alimiter=limit=0.84:level=false[aout]" \
  -map "[vout]" -map "[aout]" -t "$DUR" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
