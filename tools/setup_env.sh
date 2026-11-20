#!/usr/bin/env bash
# Код ссылается на старые абсолютные пути /home/claude/{work,p2d,qa,v2_6ex,v3_sai,en,cover}.
# Скрипт делает из них ссылки на папки репозитория.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
link() {  # link <старый путь> <папка в репо>
  if [ -e "$1" ] && [ ! -L "$1" ]; then echo "пропуск: $1 уже существует (не ссылка)"; return; fi
  ln -sfn "$REPO/$2" "$1"; echo "$1 -> $REPO/$2"
}
link /home/claude/work   engine
link /home/claude/p2d    sprites2d
link /home/claude/qa     qa
link /home/claude/en     videos/01_50_squats_en
link /home/claude/v2_6ex videos/02_six_moves
link /home/claude/v3_sai videos/03_saitama_workout
link /home/claude/cover  covers
pip install --break-system-packages -q numpy pillow scipy faster-whisper 2>/dev/null || true
command -v ffmpeg >/dev/null || echo "нужен ffmpeg"
