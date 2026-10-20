#!/usr/bin/env bash
# Burn The Aldus tiled watermark over a 1080x1920 Deep Six video for client previews.
# Usage: watermark.sh IN.mp4 OUT.mp4    (audio copied, picture re-encoded with x264 CRF 18)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ffmpeg -hide_banner -loglevel error -nostdin -y -i "$1" -loop 1 -i "$here/watermark-1080x1920.png" \
  -filter_complex "[0:v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset medium -crf 18 -profile:v high -r 30 -c:a copy -movflags +faststart "$2"
echo "Watermarked: $2"
