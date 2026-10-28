#!/usr/bin/env bash
# Prepare the original SCC clip for Remotion:
#   - the whole clip is used (11.49 s), the last frame is held to fill 11.5 s
#   - constant 30 fps H.264 (the phone clip is variable-rate HEVC)
#   - light denoise, gentle brighten, mild sharpen
# Hue and saturation are untouched so the pack keeps its original colours.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:-input/original.mp4}"
ffmpeg -y -v error -i "$SRC" -an \
  -vf "fps=30,scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.5:3:3,eq=brightness=0.035:contrast=1.04:gamma=1.04,unsharp=5:5:0.5:5:5:0,tpad=stop_mode=clone:stop_duration=0.5" \
  -t 11.5 -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -movflags +faststart public/footage.mp4
echo "footage -> public/footage.mp4"
