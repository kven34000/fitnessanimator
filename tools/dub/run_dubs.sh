#!/bin/bash
# Free dub tracks (music+sfx+Piper voice) for all videos.  bash tools/dub/run_dubs.sh  -> /tmp/dub/out/NN_<lang>.m4a
# Needs: whisper words of Long EN 01-04 in /tmp/dub/w/NN.json (tools/es_dub/whisper_words.py), final EN mp4 of 05-09 in videos/.
cd /home/claude/fitnessanimator
W=/tmp/dub; mkdir -p $W/out
declare -A MODE=([01_50_squats_en]=en [02_six_moves]=sixvo [03_saitama_workout]=saivo [04_walking_belly_fat]=walkvo)
declare -A DUROLD=([01_50_squats_en]=82.6 [02_six_moves]=334.5 [03_saitama_workout]=170.17 [04_walking_belly_fat]=314.83)
for key in 01_50_squats_en 02_six_moves 03_saitama_workout 04_walking_belly_fat 05_leg_day 06_dead_hang 07_calisthenics_vs_gym 08_pushup_ladder 09_morning_routine; do
  n=${key:0:2}
  for L in es fr ar; do
    [ -f $W/out/${n}_$L.m4a ] && continue
    if [ -n "${MODE[$key]}" ]; then
      [ $L = es ] && continue   # ES 01-04 already done (tools/es_dub)
      D=${DUROLD[$key]}; [ -f $W/${n}_$L.wav ] || nice python3 tools/dub/make_dub.py $L $key $W/${n}_$L.wav $D $W/w/$n.json
      LANG_MIX=${MODE[$key]} VO_OVERRIDE=$W/${n}_$L.wav OUT_OVERRIDE=$W/${n}_${L}_mix.wav DUR_OVERRIDE=$D python3 engine/audio.py
    else
      V=$(ls videos/$key/$n\ ·\ *.mp4 | grep -v draft | head -1)
      D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
      nice python3 tools/dub/make_dub.py $L $key $W/${n}_$L.wav $D
      VDIR=/home/claude/fitnessanimator/videos/$key LANG_MIX=b5vo VO_OVERRIDE=$W/${n}_$L.wav OUT_OVERRIDE=$W/${n}_${L}_mix.wav DUR_OVERRIDE=$D python3 engine/audio.py
    fi
    ffmpeg -nostdin -v error -y -i $W/${n}_${L}_mix.wav -c:a aac -b:a 192k $W/out/${n}_$L.m4a && echo "OK $n $L"
  done
done
echo DUBDONE
