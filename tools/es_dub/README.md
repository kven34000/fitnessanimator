# Испанская дорожка (бесплатно, Piper es_ES-davefx-medium)
1. Голос: `pip install piper-tts onnxruntime num2words`; модель `es_ES-davefx-medium.onnx(.json)` с huggingface.co/rhasspy/piper-voices (es/es_ES/davefx/medium) → /home/claude/tts/.
2. Тайминги английского: `python3 whisper_words.py <en.mp3|mp4> words.json` (faster-whisper base.en).
3. Перевод по фразам английского сценария: `es_segs.py` (ключ = папка ролика), английские фразы — `en_segs.json`.
4. `python3 make_es.py <key> words.json <длительность EN-ролика> es.wav` — каждая фраза ставится на старт английской, длина подгоняется length_scale (0.72–1.12), при нужде atempo.
5. Музыка+звуки с испанским голосом: `LANG_MIX=<saivo|walkvo|sixvo|en> VO_OVERRIDE=es.wav OUT_OVERRIDE=mix_es.wav DUR_OVERRIDE=<длит.> python3 engine/audio.py` → `ffmpeg -i mix_es.wav -c:a aac -b:a 192k "NN · Title (ES audio).m4a"`.
Проверено: сдвиг 0 с, длина совпадает с английским роликом (±0,02 с).
