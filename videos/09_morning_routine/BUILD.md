# Сборка 09 · 5-Minute Morning Calisthenics
1. `bash tools/setup_env.sh`
2. Голос (бесплатный черновик): `python3 videos/_batch5/make_vo.py $PWD/videos/09_morning_routine` → vo/vo.wav, segs.json, dur.txt; тайминги слов: `python3 tools/es_dub/whisper_words.py videos/09_morning_routine/vo/vo.wav videos/09_morning_routine/vo/words.json`.
   Для платного голоса: положить запись в vo/vo.wav, пересчитать segs.json по началу каждой фразы (whisper) и dur.txt.
3. `cd videos/_batch5 && bash build.sh 09_morning_routine "09 · 5-Minute Morning Calisthenics"` (рендер Pool(2) + звук `LANG_MIX=b5vo` + mux).
4. Стоп-кадры по фразам: `VDIR=$PWD/../09_morning_routine python3 stills5.py /tmp/s $(VDIR=$PWD/../09_morning_routine python3 seg_times.py 0.7)`.
5. QA: `NOSHEETS=1 python3 qa/qa.py b5:09_morning_routine`.
