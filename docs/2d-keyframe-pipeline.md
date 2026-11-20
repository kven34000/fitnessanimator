# 2D-пайплайн по ключевым фазам

## Генерация (бесплатно)
- Magnific через браузер автора (Claude in Chrome), Nano Banana 2.1, режим Relax (0 кредитов). Через MCP Relax не работает. Загрузка своих картинок (creations_request_upload → PUT → finalize) бесплатна.
- Хелперы в localStorage вкладки генератора: `__clr` (очистить поле), `__ins(text)` (дописать текст и нажать Generate), `__editsrc(what)` («убрать только what»), `__platesrc(what)` («убрать человека, оставить what»). Новый лист: `__clr` → «@neonf» + Enter → `__ins(...)`. Правка: `__clr` → «Edit @img» + Enter → `__ins(...)`. Формат 4:3 выбирать в меню соотношения.
- Смена референса: hover на миниатюре → X; страница /app/creation/<id> → Use image → Use as reference.
- Шаблон листа: «anime fitness character sprite sheet, 4:3. EXACTLY 8 figures in a clean 4 columns x 2 rows grid … phases … Full body visible including shoes … Solid pure bright green (#00FF00) background, no floor, no shadows, no text.»

## Нарезка
- `sprites2d/cutgrid.py sheet.png spr/<name>/f rows cols` — строго по сетке; `cut8.py` — по компонентам.
- Маски мышц из правки `_mus` (синий, жёлтый, пурпурный, голубой → каналы 0–3), `masks8.py`.

## Статичные снаряды
- `_noeq` (убрать только снаряд) + `_plate` (только снаряд). Плейт часто сдвинут по сетке — `fixplate.py` (CH/CW через env); `mkplate.py` — плейт из оригинала с закрашенным человеком.
- `build_plate.py name rows cols P frames…` → `spr/<name>S/` (кадры + info.json). `PMB=<px>` — брать человека с запасом под клеткой.

## Рендер
- `engine/render_v2.py` — движок; сцены ролика в `videos/<NN>/render_*.py` + `timeline_*.py`.
- `python3 render_xxx.py still t1 t2 …` — стоп-кадры; `python3 render_xxx.py full out.mp4 [t0 t1]` — рендер (Pool(2)).
- Звук: `LANG_MIX=<six|sixvo|sai|saivo> python3 engine/audio.py` → mix_*.wav; затем ffmpeg mux.

## Озвучка
- Alistair Ashford (id 1472), eleven_v4, stability 0.3. Тайминги слов: faster-whisper base.en → `vo_align.py` (кусочно-линейный перенос старой шкалы сцен на голос, субтитры по реальным словам).
