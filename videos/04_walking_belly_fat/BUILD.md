# Сборка 04 · Walking (EN, без голоса)
1. `bash tools/setup_env.sh`
2. `cd videos/04_walking_belly_fat && python3 render_walk.py full walk_noaudio.mp4` (Pool(2), ~12 мин; ничего тяжёлого параллельно — OOM)
3. `LANG_MIX=walk python3 /home/claude/work/audio.py` → mix_novo.wav
4. `ffmpeg -i walk_noaudio.mp4 -i mix_novo.wav -c:v copy -c:a aac -b:a 192k -shortest walk_EN_draft1_novoice.mp4`
5. Стоп-кадры: `python3 stills.py /tmp/st 10 20 30` (листы 3×3); QA: `python3 /home/claude/qa/qa.py walk`
