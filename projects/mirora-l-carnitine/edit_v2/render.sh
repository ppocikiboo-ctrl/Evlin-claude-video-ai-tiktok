#!/usr/bin/env bash
# Render the v2 ("max engagement") MIRORA edit.
# Usage: ./render.sh <input.mp4> <output.mp4>
set -euo pipefail
IN="$(realpath "$1")"; OUT="$2"
cd "$(dirname "$0")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
python3 gen_audio.py "$DUR" "$TMP/music.wav" "$TMP/sfx.wav"

# Zoom: hook starts at 1.12 and eases out, punch on every cut, light pulse on each beat (100 BPM = 18 frames).
Z="if(lt(in,135),1.12-0.08*in/135,1.04)+0.012*exp(-mod(in,18)/3)"
for b in 141 258 450 579 669 894 1083; do
  Z="if(between(in,$b,$((b+12))),1.11-0.07*(in-$b)/12,$Z)"
done

# Two-pass linear loudness: measure the mix, then apply one fixed gain to hit -14 LUFS
# (single-pass loudnorm pumps the music up in the voice gaps).
MIX="[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[voice][key];[1:a]volume=0.16[mus];[2:a]volume=0.6[fx];[mus][key]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=350[duck];[voice][duck][fx]amix=inputs=3:normalize=0:duration=first"
L=$(ffmpeg -i "$IN" -i "$TMP/music.wav" -i "$TMP/sfx.wav" -filter_complex "$MIX,ebur128" -f null - 2>&1 | grep -A1 Integrated | tail -1 | awk '{print $2}')
GAIN=$(python3 -c "print(round(-14-($L),2))")

python3 overlay_frames.py "$DUR" | ffmpeg -y -v error -stats \
  -i "$IN" \
  -f rawvideo -pix_fmt rgba -s 1080x1920 -r 30 -i - \
  -i "$TMP/music.wav" -i "$TMP/sfx.wav" \
  -filter_complex "
[0:v]scale=2160:3840:flags=lanczos,
 eq=contrast=1.08:saturation=1.15:brightness=0.015:gamma=1.02,
 colorbalance=rs=0.035:gs=0.01:bs=-0.04:rm=0.02:bm=-0.02,
 zoompan=z='$Z':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,
 unsharp=5:5:0.6,vignette=PI/6,format=yuva420p[base];
[base][1:v]overlay=0:0:format=auto,format=yuv420p[vout];
[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[voice][key];
[2:a]volume=0.16[mus];[3:a]volume=0.6[fx];
[mus][key]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=350[duck];
[voice][duck][fx]amix=inputs=3:normalize=0:duration=first[mixed];
[mixed]volume=${GAIN}dB,alimiter=limit=0.84:level=false[aout]" \
  -map "[vout]" -map "[aout]" -t "$DUR" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
