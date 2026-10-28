#!/usr/bin/env bash
# Trim the original phone clip to 10 s and clean it up for Remotion:
#   - skip the first 0.45 s (empty hand before the pack enters)
#   - constant 30 fps H.264 (the phone clip is variable-rate HEVC)
#   - light denoise, gentle brighten, mild sharpen
# Colour/hue is left untouched so the pack keeps its original pink.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:-input/original.mp4}"
ffmpeg -y -v error -ss 0.45 -i "$SRC" -t 10 -an \
  -vf "fps=30,scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.5:3:3,eq=brightness=0.03:contrast=1.04:gamma=1.03,unsharp=5:5:0.5:5:5:0" \
  -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -movflags +faststart public/footage.mp4
echo "footage -> public/footage.mp4"
