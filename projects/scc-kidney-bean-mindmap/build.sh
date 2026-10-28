#!/usr/bin/env bash
# Builds output/scc-mindmap-tiktok.mp4 (1080x1920, 30 fps, 18 s) from reference/source.mp4.
# usage: ./build.sh            full render
#        ./build.sh preview 0.5,1.2,5   render PNG stills only (into $BUILD_DIR)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="${BUILD_DIR:-$HERE/build}"
PORT="${PORT:-8765}"
mkdir -p "$BUILD/frames" "$HERE/output"
cp "$HERE/scene.html" "$HERE/timeline.json" "$BUILD/"
cp -r "$HERE/fonts" "$BUILD/"

# Footage frames at 30 fps with a light, clean commercial grade (packaging colours kept natural).
if [ ! -f "$BUILD/frames/src_0001.jpg" ]; then
  ffmpeg -v error -y -i "$HERE/reference/source.mp4" \
    -vf "fps=30,eq=brightness=0.025:contrast=1.05:saturation=1.03,unsharp=5:5:0.4" \
    -q:v 2 "$BUILD/frames/src_%04d.jpg"
fi

python3 -m http.server "$PORT" --directory "$BUILD" >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1

if [ "${1:-}" = "preview" ]; then
  node "$HERE/render.js" "http://localhost:$PORT" "$BUILD" --preview "$2"
  exit 0
fi

node "$HERE/render.js" "http://localhost:$PORT" "$BUILD/video.mp4"
python3 "$HERE/audio.py" "$HERE/timeline.json" "$BUILD/audio.wav"
ffmpeg -v error -y -i "$BUILD/video.mp4" -i "$BUILD/audio.wav" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 44100 -c:a aac -b:a 192k \
  -movflags +faststart -shortest "$HERE/output/scc-mindmap-tiktok.mp4"
echo "done: $HERE/output/scc-mindmap-tiktok.mp4"
