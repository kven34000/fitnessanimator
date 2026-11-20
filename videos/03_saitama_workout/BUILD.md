# Сборка 03 · Saitama workout (EN, без голоса)
1. `bash tools/setup_env.sh`
2. `cd /home/claude/v3_sai && python3 render_sai.py full sai_noaudio.mp4`
3. `LANG_MIX=sai python3 /home/claude/work/audio.py` → mix_novo.wav
4. `ffmpeg -i sai_noaudio.mp4 -i mix_novo.wav -c:v copy -c:a aac -b:a 192k -shortest Saitama_workout_EN_draft2_novoice.mp4`
5. Фоны без героя: `NOHERO=1 python3 render_sai.py full hook_plate.mp4 7.2 15.7`
6. `python3 /home/claude/qa/qa.py sai`
