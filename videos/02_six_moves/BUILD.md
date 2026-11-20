# Сборка 02 · 6 moves (EN)
1. `bash tools/setup_env.sh`
2. Голос: Magnific `creations_get CqnpfeKEEy` → скачать в `/home/claude/v2_6ex/vo/vo_en.mp3`; `ffmpeg -i vo_en.mp3 -ar 16000 -ac 1 vo16.wav`; faster-whisper → `vo/words.json` (уже лежит в git).
3. `cd /home/claude/v2_6ex && python3 render_6ex.py full v11_noaudio.mp4`
4. `LANG_MIX=sixvo python3 /home/claude/work/audio.py` → mix_vo.wav
5. `ffmpeg -i v11_noaudio.mp4 -i mix_vo.wav -c:v copy -c:a aac -b:a 192k -shortest 6_moves_EN_v11.mp4`
6. `cd /home/claude/qa && python3 qa.py six`
