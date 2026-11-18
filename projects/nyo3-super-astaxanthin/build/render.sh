#!/usr/bin/env bash
# Usage: render.sh <source.mp4> <assets_dir> <out.mp4>
set -euo pipefail
SRC=$1; A=$2; OUT=$3; PHOTO=${4:-$(dirname "$0")/../reference/kulit_konsep.jpg}
ZP="zoompan=z='if(lte(on,10),1.18-0.018*on,1+0.0015*(on-10))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
ffmpeg -y -v error \
 -i "$SRC" -loop 1 -t 3 -i "$A/aging_bg.png" -loop 1 -t 3 -i "$PHOTO" \
 -loop 1 -i "$A/t1_hook.png" -loop 1 -i "$A/t2_what.png" -loop 1 -i "$A/t3_how.png" \
 -loop 1 -i "$A/t4_ing.png" -loop 1 -i "$A/t5_cta.png" -i "$A/beat.wav" \
 -filter_complex "
 [0:v]split=5[s1][s2][s3][s4][s5];
 [s1]trim=0.9:2.9,setpts=PTS-STARTPTS,$ZP,eq=saturation=1.15:contrast=1.05[v1];
 [s2]trim=3.5:5.0,setpts=PTS-STARTPTS,$ZP,eq=saturation=1.15:contrast=1.05[v2];
 [2:v]fps=30,scale=-2:920,crop=1000:920:x='(iw-1000)*min(t/2.6\,1)':y=0,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(hypot(max(0,abs(X-W/2)-(W/2-40)),max(0,abs(Y-H/2)-(H/2-40))),40),0,255)'[ph];
 [1:v]fps=30,format=rgba[bgc]; [bgc][ph]overlay=40:500:shortest=1,trim=0:2.8,setpts=PTS-STARTPTS,format=yuv420p[v3];
 [s3]trim=5.9:8.6,setpts=PTS-STARTPTS,$ZP,eq=saturation=1.15:contrast=1.05[v4];
 [s4]trim=9.8:12.5,setpts=PTS-STARTPTS,$ZP,eq=saturation=1.15:contrast=1.05[v5];
 [s5]trim=11.6:12.6,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=2,trim=0:2.6,scale=1080:1920,boxblur=18:2,eq=brightness=-0.12:saturation=1.3,fps=30[v6];
 [3:v]trim=0:2,format=rgba,fade=in:st=0:d=0.15:alpha=1[o1];
 [4:v]trim=0:1.5,format=rgba,fade=in:st=0.1:d=0.2:alpha=1[o2];
 [5:v]trim=0:2.7,format=rgba,fade=in:st=0.1:d=0.2:alpha=1[o4];
 [6:v]trim=0:2.7,format=rgba,fade=in:st=0.1:d=0.2:alpha=1[o5];
 [7:v]trim=0:2.6,format=rgba,fade=in:st=0.1:d=0.25:alpha=1[o6];
 [v1][o1]overlay=shortest=1,format=yuv420p,setsar=1[c1];
 [v2][o2]overlay=shortest=1,format=yuv420p,setsar=1[c2];
 [v3]setsar=1[c3];
 [v4][o4]overlay=shortest=1,format=yuv420p,setsar=1[c4];
 [v5][o5]overlay=shortest=1,format=yuv420p,setsar=1[c5];
 [v6][o6]overlay=shortest=1,format=yuv420p,setsar=1[c6];
 [c1][c2][c3][c4][c5][c6]concat=n=6:v=1:a=0[v];
 [8:a]volume=0.9,aformat=sample_rates=44100:channel_layouts=stereo[a]" \
 -map "[v]" -map "[a]" -shortest -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
 -c:a aac -b:a 160k -movflags +faststart "$OUT"
