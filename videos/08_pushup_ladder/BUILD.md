# Сборка 08 · How to Do 80+ Push-Ups
1. `bash tools/setup_env.sh`
2. Голос (бесплатный черновик): `python3 videos/_batch5/make_vo.py $PWD/videos/08_pushup_ladder` → vo/vo.wav, segs.json, dur.txt; тайминги слов: `python3 tools/es_dub/whisper_words.py videos/08_pushup_ladder/vo/vo.wav videos/08_pushup_ladder/vo/words.json`.
   Для платного голоса: положить запись в vo/vo.wav, пересчитать segs.json по началу каждой фразы (whisper) и dur.txt.
3. `cd videos/_batch5 && bash build.sh 08_pushup_ladder "08 · How to Do 80+ Push-Ups"` (рендер Pool(2) + звук `LANG_MIX=b5vo` + mux).
4. Стоп-кадры по фразам: `VDIR=$PWD/../08_pushup_ladder python3 stills5.py /tmp/s $(VDIR=$PWD/../08_pushup_ladder python3 seg_times.py 0.7)`.
5. QA: `NOSHEETS=1 python3 qa/qa.py b5:08_pushup_ladder`.
