#!/usr/bin/env bash
# Render the VBGV 30 s TikTok ad end to end.
#   ./render.sh                         uses input/original.mp4 and the synthesized soundtrack
#   ./render.sh my_clip.mp4             use another source clip
#   MUSIC=track.mp3 ./render.sh         swap in a licensed music bed (SFX stay)
set -euo pipefail
cd "$(dirname "$0")"

SRC="${1:-input/original.mp4}"
OUT="output/VBGV_TikTok_30s.mp4"
mkdir -p build output

echo "[1/4] cutting + grading footage"
python3 src/build_base.py "$SRC"

echo "[2/4] soundtrack"
if [[ -n "${MUSIC:-}" ]]; then
  python3 src/audio.py --music "$MUSIC"
else
  python3 src/audio.py
fi

echo "[3/4] motion graphics (a few minutes)"
python3 src/overlay.py

echo "[4/4] mux + loudness normalise"
ffmpeg -y -v error -i build/video.mp4 -i build/soundtrack.wav \
  -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-12:TP=-1.0:LRA=9" -c:a aac -b:a 256k -ar 48000 \
  -t 30 -movflags +faststart "$OUT"

echo "done -> $OUT"
