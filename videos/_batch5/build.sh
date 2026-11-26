#!/bin/bash
# bash build.sh <video_dir_name> "<NN · Title>"  -> <dir>/<NN · Title> draft1.mp4 (free Piper voice + music + sfx)
set -e
V=/home/claude/fitnessanimator/videos/$1; export VDIR=$V
cd /home/claude/fitnessanimator/videos/_batch5
python3 render_b5.py full $V/noaudio.mp4
LANG_MIX=b5vo python3 /home/claude/fitnessanimator/engine/audio.py
ffmpeg -nostdin -v error -y -i $V/noaudio.mp4 -i $V/mix_vo.wav -c:v copy -c:a aac -b:a 192k -shortest "$V/$2${3:+ $3}.mp4"
ls -la "$V/$2${3:+ $3}.mp4"
