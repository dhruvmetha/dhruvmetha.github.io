#!/usr/bin/env bash
# How the homepage teasers and posters were made (2026-11-25). Kept as a record and
# for the next clip. The inputs are the originals from before the refresh, which stay
# in git history:
#   git show 4972944:videos/legged_probe.mp4 > /tmp/legged_probe_orig.mp4
#   git show 4972944:videos/insert.mp4       > /tmp/insert_orig.mp4
# Usage: _tools/media.sh /tmp/legged_probe_orig.mp4 /tmp/insert_orig.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
probe_in=$1
insert_in=$2
x264=(-an -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -movflags +faststart)

# PROBE: the 1280x720 source is half black letterbox (content at y=180..540).
# Crop it, then stack the camera view (left half) over the estimate (right half).
ffmpeg -y -i "$probe_in" -vf "crop=1280:360:0:180,split[a][b];[a]crop=640:360:0:0[l];[b]crop=640:360:640:0[r];[l][r]vstack,scale=480:-2,fps=24" \
  "${x264[@]}" videos/legged_probe.mp4
# Insertion: 480x848 portrait; the gripper and connector stay in the top 640 rows.
ffmpeg -y -i "$insert_in" -vf "crop=480:640:0:0,scale=360:-2" "${x264[@]}" videos/insert.mp4

# Posters, one frame each, same size as the video.
ffmpeg -y -ss 6 -i videos/legged_probe.mp4 -frames:v 1 -q:v 4 videos/legged_probe.jpg
ffmpeg -y -ss 8 -i videos/insert.mp4 -frames:v 1 -q:v 4 videos/insert.jpg

# A new clip: aim for 5-10 s, about 480 px wide, under 500 KB, then add
# `teaser: videos/<name>.mp4` to _data/publications.yml and run python3 build.py.
