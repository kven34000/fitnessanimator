# fitnessanimator

Код, сценарии, спрайты и инструкции для фитнес-канала @fitnessanimator: анимированный герой @neonfit в красно-неоновом стиле, мышцы подсвечиваются зелёным.

Готовые ролики (mp4), голос и микс (wav/mp3) в git не хранятся. Их можно пересобрать по `videos/<ролик>/BUILD.md`. Голос берётся из Magnific по ID, ID записаны в `SOURCES.json`.

## Структура

| Папка | Что внутри |
|---|---|
| `engine/` | движок рендера `render_v2.py`, звук `audio.py`, шрифты, базовые позы, звуки (`kit/`) |
| `sprites2d/` | листы поз из Magnific (`sheets/`), нарезанные спрайты (`spr/`), фоны (`bg/`), скрипты нарезки и статичных снарядов |
| `qa/` | автоматическая проверка ролика `qa.py`, проверка шрифтов `glyphs.py`, отчёты |
| `videos/01_50_squats_en/` | «50 приседаний каждый день», английская версия |
| `videos/02_six_moves/` | «6 упражнений, которые строят мышцы лучше зала», английская версия |
| `videos/03_saitama_workout/` | «Тренировка Сайтамы 30 дней», черновик без голоса |
| `covers/` | обложки и аватар канала |
| `docs/` | пайплайн, процесс проверки, планы следующих роликов |
| `lessons/INDEX.md` | ошибки и правила, которые уже выучены |
| `tools/setup_env.sh` | ссылки на старые пути `/home/claude/...`, которые ждёт код |

## Быстрый старт в новой сессии

```bash
git clone https://github.com/kven34000/fitnessanimator /home/claude/fitnessanimator
bash /home/claude/fitnessanimator/tools/setup_env.sh
cd /home/claude/v3_sai && python3 render_sai.py still 10      # проверочный кадр
```
