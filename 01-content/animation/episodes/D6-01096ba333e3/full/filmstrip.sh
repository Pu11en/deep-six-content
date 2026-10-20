#!/usr/bin/env bash
# 5-frames-per-second filmstrips of an MP4, one strip per 6 seconds, for watching motion as stills.
# Usage: filmstrip.sh <mp4> <out-prefix>
set -euo pipefail
mp4="$1"; out="$2"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$mp4")
n=$(python3 -c "import math;print(math.ceil($dur/6))")
for ((i=0; i<n; i++)); do
  ffmpeg -v error -y -ss $((i*6)) -t 6 -i "$mp4" -vf "fps=5,scale=144:-1,tile=15x2" -frames:v 1 "${out}-$(printf %02d $i).png"
done
echo "$n strips"
