#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Weijie Zhang
# Rebuild marketing/findnet-ad-20s-zh.mp4 from scratch. Requirements: see README.md in this folder.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
python3 render_zh.py
python3 build_audio.py
ffmpeg -y -loglevel error -i build/mix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=7" -ar 44100 build/mix_norm.wav
ffmpeg -y -loglevel error -framerate 30 -i build/frames/f%04d.png -i build/mix_norm.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 44100 \
  -shortest -movflags +faststart ../findnet-ad-20s-zh.mp4
echo "wrote marketing/findnet-ad-20s-zh.mp4"
