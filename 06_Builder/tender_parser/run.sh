#!/bin/bash
# Скрипт для запуска парсера тендеров
# Использование: ./run.sh [--limit N] [--headful] [--db-path PATH]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не найден"
    exit 1
fi

# Запускаем парсер с переданными аргументами
python3 parser.py "$@"
