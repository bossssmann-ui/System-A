#!/bin/zsh
# Установка launchd-агента автоматического git pull для vault'а System-A.
# Запуск: bash 99_System/launchd/install-gitpull.sh
# После установки — pull origin main каждые 10 минут + при логине.

set -e

VAULT_DIR="$HOME/Documents/System-A"
PLIST_SRC="$VAULT_DIR/99_System/launchd/com.system-a.gitpull.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.system-a.gitpull.plist"

if [[ ! -f "$PLIST_SRC" ]]; then
  echo "❌ Не нашёл $PLIST_SRC" >&2
  exit 1
fi

# Если уже загружен — снимаем перед обновлением
if launchctl list | grep -q "com.system-a.gitpull"; then
  echo "→ Снимаю старую версию агента"
  launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"
launchctl load "$PLIST_DST"

echo "✓ Установлен: $PLIST_DST"
echo "  Интервал: 600 сек (10 мин)"
echo "  Лог:      /tmp/system-a-gitpull.log"
echo ""
echo "Проверка:"
echo "  launchctl list | grep system-a"
echo "  tail -f /tmp/system-a-gitpull.log"
echo ""
echo "Снять:"
echo "  launchctl unload $PLIST_DST"
