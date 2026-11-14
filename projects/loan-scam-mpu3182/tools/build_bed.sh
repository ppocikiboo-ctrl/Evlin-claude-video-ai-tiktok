#!/usr/bin/env bash
# Rebuild assets/bgm/bed.wav from the four catalog tracks, aligned to the chapters.
# Usage: build_bed.sh <hyperframes-project-dir> <total-seconds> <etika-start> <undang-start>
set -euo pipefail
P=$1; TOTAL=$2; ET=${3:-244.9}; UN=${4:-347.6}; B=$P/assets/bgm; T=$(mktemp -d)
for f in tense_a tense_b hope_a hope_b; do ffmpeg -v error -y -i $B/$f.mp3 -af "loudnorm=I=-20:TP=-2:LRA=11" -ar 48000 -ac 2 $T/$f.wav; done
xf(){ ffmpeg -v error -y -i $1 -i $2 -filter_complex "acrossfade=d=3:c1=tri:c2=tri" $3; }
# chain alternating takes until each part covers its chapter span (3 s crossfades)
chain(){ out=$1; need=$2; shift 2; cp $T/$1.wav $out; i=1; set -- "$@"; n=$#; arr=("$@")
  while (( $(python3 -c "print(int($(ffprobe -v error -show_entries format=duration -of csv=p=0 $out) < $need))") )); do
    nxt=${arr[$((i % n))]}; xf $out $T/$nxt.wav $T/tmp.wav; mv $T/tmp.wav $out; i=$((i+1)); done; }
TE=$(python3 -c "print($ET+2.5)"); RL=$(python3 -c "print(round($UN+2.5-$ET,2))"); HL=$(python3 -c "print(round($TOTAL-$UN,2))")
chain $T/tense.wav $TE tense_a tense_b
chain $T/refl.wav $RL hope_b hope_b
chain $T/hope.wav $HL hope_a hope_b
ffmpeg -v error -y -i $T/tense.wav -i $T/refl.wav -i $T/hope.wav -filter_complex "\
[0]atrim=0:$TE,afade=t=out:st=$ET:d=2.5[a];\
[1]atrim=0:$RL,afade=t=in:d=2.5,afade=t=out:st=$(python3 -c "print($RL-2.5)"):d=2.5,adelay=$(python3 -c "print(int($ET*1000))")|$(python3 -c "print(int($ET*1000))")[b];\
[2]atrim=0:$HL,afade=t=in:d=2.5,afade=t=out:st=$(python3 -c "print(round($HL-3,2))"):d=3,adelay=$(python3 -c "print(int($UN*1000))")|$(python3 -c "print(int($UN*1000))")[c];\
[a][b][c]amix=inputs=3:normalize=0:duration=longest,atrim=0:$TOTAL" -ar 48000 $B/bed.wav
rm -rf $T
