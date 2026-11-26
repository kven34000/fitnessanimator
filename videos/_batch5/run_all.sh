#!/bin/bash
cd /home/claude/fitnessanimator/videos/_batch5
for x in "08_pushup_ladder|08 · How to Do 80+ Push-Ups" "09_morning_routine|09 · 5-Minute Morning Calisthenics" "07_calisthenics_vs_gym|07 · Calisthenics or Gym" "05_leg_day|05 · Why Leg Day Changes Everything" "06_dead_hang|06 · The Most Boring Exercise That Fixes Everything"; do
  d=${x%%|*}; t=${x#*|}
  [ -f "/home/claude/fitnessanimator/videos/$d/$t.mp4" ] && continue
  bash build.sh $d "$t" > /tmp/f_$d.log 2>&1 < /dev/null
done
echo ALLDONE > /tmp/r_all.log
