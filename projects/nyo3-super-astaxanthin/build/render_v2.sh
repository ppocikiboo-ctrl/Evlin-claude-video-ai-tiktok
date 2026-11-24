#!/usr/bin/env bash
# Usage: render_v2.sh <source.mp4> <assets_dir> <out.mp4> [photo.jpg]
set -euo pipefail
SRC=$1; A=$2; OUT=$3; PHOTO=${4:-$(dirname "$0")/../reference/kulit_konsep.jpg}
ZP="zoompan=z='if(lte(on,6),1.25-0.03*on,1.07+0.002*(on-6))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
GR="eq=saturation=1.25:contrast=1.12:brightness=-0.03,vignette=PI/4,fade=in:st=0:d=0.12:color=white"
seg(){ echo "[s$1]trim=$2:$3,setpts=PTS-STARTPTS,$ZP,$GR[v$1];"; }
ov(){ echo "[$1:v]trim=0:$2,format=rgba,fade=in:st=0:d=0.12:alpha=1[o$3]; [v$3][o$3]overlay=shortest=1,format=yuv420p,setsar=1[c$3];"; }
FC="[0:v]split=6[s1][s2][s4][s5][s6][s7];
$(seg 1 0.9 2.9) $(seg 2 3.5 4.7) $(seg 4 3.9 5.3) $(seg 5 9.8 11.4) $(seg 6 5.9 7.6)
[2:v]fps=30,scale=-2:900,crop=1000:900:x='(iw-1000)*min(t/2.3\,1)':y=0[ph];
[1:v]fps=30,format=rgba[bgc]; [bgc][ph]overlay=40:510:shortest=1,trim=0:2.5,setpts=PTS-STARTPTS,fade=in:st=0:d=0.12:color=white,format=yuv420p,setsar=1[c3];
$(ov 3 2.0 1) $(ov 4 1.2 2) $(ov 5 1.4 4) $(ov 6 1.6 5) $(ov 7 1.7 6)
[s7]trim=1.8:2.4,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=3,trim=0:2.6,$ZP,eq=saturation=1.2:brightness=-0.1,boxblur=6:1,fade=in:st=0:d=0.12:color=white[v7];
$(ov 8 2.6 7)
[c1][c2][c3][c4][c5][c6][c7]concat=n=7:v=1:a=0[v];
[9:a]aformat=sample_rates=44100:channel_layouts=stereo[a]"
ffmpeg -y -v error -i "$SRC" -loop 1 -t 3 -i "$A/v2_photo_bg.png" -loop 1 -t 3 -i "$PHOTO" \
 -loop 1 -i "$A/v2_hook.png" -loop 1 -i "$A/v2_3sebab.png" -loop 1 -i "$A/v2_r1.png" -loop 1 -i "$A/v2_r2.png" \
 -loop 1 -i "$A/v2_r3.png" -loop 1 -i "$A/v2_cta.png" -i "$A/v2_beat.wav" \
 -filter_complex "$FC" -map "[v]" -map "[a]" -shortest -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
 -c:a aac -b:a 160k -movflags +faststart "$OUT"
