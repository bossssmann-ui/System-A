# Примеры использования парсера тендеров

## Примеры 1: Базовые запуски

### Пример 1.1: Запуск с параметрами по умолчанию

```bash
python3 parser.py
```

Результат:
- Парсит 50 тендеров
- Сохраняет в `tenders.db`
- Выводит топ-10 по сумме
- Логирует в `parser.log` и stdout

### Пример 1.2: Парсить больше тендеров

```bash
python3 parser.py --limit 100
```

Парсит 100 тендеров вместо 50.

### Пример 1.3: Отладка с видимым браузером

```bash
python3 parser.py --limit 10 --headful
```

Откроется окно Chromium, видны все действия парсера. Полезно для отладки селекторов.

### Пример 1.4: Использовать альтернативную БД

```bash
python3 parser.py --db-path /var/tender_parser/archive.db --limit 50
```

БД создаётся автоматически если не существует.

## Пример 2: Использование в Python коде

### Пример 2.1: Прямой импорт и запуск

```python
from scraper import run_scraper
from storage import TenderDB

# Запустить скрейпер и получить список тендеров
tenders = run_scraper(headless=True, limit=50)

# Инициализировать БД
db = TenderDB("my_tenders.db")

# Сохранить все тендеры
for tender in tenders:
    db.upsert_tender(tender)

# Получить топ-10 новых
top = db.get_recent_new_tenders(limit=10)
for t in top:
    print(f"{t['id']}: {t['title']} — {t['amount']} руб")
```

### Пример 2.2: Работа с фильтрами

```python
from filters import has_stop_keyword, normalize_amount

# Проверить стоп-слово
title = "Авиадоставка грузов по России"
if has_stop_keyword(title):
    print("Эта закупка исключена (авиа-доставка)")

# Распарсить сумму
amount_str = "1 234 567,89 руб"
amount = normalize_amount(amount_str)
print(f"Распарсена сумма: {amount} руб")  # Output: 1234567 руб
```

### Пример 2.3: SQL запросы к БД

```python
import sqlite3
from storage import TenderDB

db = TenderDB("tenders.db")

# Получить все тендеры заданного закона
with sqlite3.connect(db.db_path) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tenders WHERE law = '44-ФЗ' ORDER BY amount DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"{row['title']}: {row['amount']} руб")

# Подсчитать количество тендеров по регионам
with sqlite3.connect(db.db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT region, COUNT(*) as count, SUM(amount) as total
        FROM tenders
        GROUP BY region
        ORDER BY total DESC
    """)
    for region, count, total in cursor.fetchall():
        print(f"{region}: {count} тендеров, сумма {total} руб")
```

## Пример 3: Интеграция с cron

### Пример 3.1: Ежедневный запуск в 03:00 UTC

```bash
# Отредактировать crontab
crontab -e

# Добавить строку
0 3 * * * cd /home/user/tender_parser && /usr/bin/python3 parser.py >> cron.log 2>&1

# Проверить установленные cron задачи
crontab -l
```

Логирование в `cron.log`.

### Пример 3.2: Запуск несколько раз в день

```bash
# Запуск в 03:00, 09:00 и 18:00 UTC
0 3,9,18 * * * cd /home/user/tender_parser && /usr/bin/python3 parser.py >> cron.log 2>&1
```

### Пример 3.3: Запуск с ограничением по памяти

```bash
# Запуск с максимум 1 ГБ памяти
0 3 * * * cd /home/user/tender_parser && timeout 600 /usr/bin/python3 parser.py >> cron.log 2>&1
```

## Пример 4: Обработка результатов

### Пример 4.1: Экспорт в CSV

```python
import csv
from storage import TenderDB

db = TenderDB("tenders.db")
tenders = db.get_recent_new_tenders(limit=100)

with open("export.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "title", "law", "customer", "amount", "region", "deadline", "link"
    ])
    writer.writeheader()
    for tender in tenders:
        writer.writerow(tender)

print(f"Экспортировано {len(tenders)} тендеров в export.csv")
```

### Пример 4.2: Отправка уведомления (планируется)

```python
# Это пример для будущей итерации
from storage import TenderDB
import smtplib
from email.mime.text import MIMEText

db = TenderDB("tenders.db")
top_tenders = db.get_recent_new_tenders(limit=10)

# Формируем письмо
message = "НОВЫЕ ТЕНДЕРЫ НА ГРУЗОПЕРЕВОЗКИ\n\n"
for t in top_tenders:
    message += f"{t['title']}\nСумма: {t['amount']} руб\nДедлайн: {t['deadline']}\n\n"

# Отправляем на почту (требуется SMTP настройка)
# smtp.sendmail(...)
```

## Пример 5: Отладка

### Пример 5.1: Проверка логов

```bash
# Последние 50 строк логов
tail -50 parser.log

# Поиск ошибок
grep ERROR parser.log

# Поиск предупреждений
grep WARNING parser.log

# В реальном времени
tail -f parser.log
```

### Пример 5.2: Запуск с максимальной детализацией

```python
import logging

# Установить DEBUG уровень
logging.basicConfig(level=logging.DEBUG)

from scraper import run_scraper

tenders = run_scraper(headless=False, limit=5)
```

### Пример 5.3: Проверка структуры БД

```bash
# Просмотр схемы
sqlite3 tenders.db ".schema"

# Количество записей
sqlite3 tenders.db "SELECT COUNT(*) FROM tenders;"

# Статистика по закону
sqlite3 tenders.db "SELECT law, COUNT(*) FROM tenders GROUP BY law;"

# Диапазон сумм
sqlite3 tenders.db "SELECT MIN(amount), MAX(amount), AVG(amount) FROM tenders;"
```

## Пример 6: Работа с .env конфигом

### Пример 6.1: Создание .env файла

```bash
# Скопировать пример
cp .env.example .env

# Отредактировать
nano .env
```

Содержимое `.env`:

```
HEADLESS=true
TIMEOUT_MS=30000
RETRY_ATTEMPTS=3
RETRY_DELAY_SEC=2
DEFAULT_LIMIT=50
MIN_NMC_RUB=60000
DB_PATH=tenders.db
ZAKUPKI_BASE_URL=https://www.zakupki.gov.ru
```

### Пример 6.2: Использование .env в коде

```python
from dotenv import load_dotenv
import os

load_dotenv()

db_path = os.getenv("DB_PATH", "tenders.db")
min_nmc = int(os.getenv("MIN_NMC_RUB", "60000"))

print(f"БД: {db_path}, мин. НМЦ: {min_nmc} руб")
```

## Пример 7: Сценарии использования

### Сценарий 1: Ежедневный мониторинг

```bash
#!/bin/bash
# daily_check.sh

cd /home/user/tender_parser

# Запустить парсер
python3 parser.py --limit 100 > daily_results.txt 2>&1

# Отправить результаты на почту (команда зависит от ОС)
cat daily_results.txt | mail -s "Тендеры $(date +%Y-%m-%d)" user@example.com

# Архивировать результаты
tar czf archive/results_$(date +%Y%m%d).tar.gz tenders.db parser.log
```

Добавить в cron:

```bash
0 4 * * * /home/user/tender_parser/daily_check.sh
```

### Сценарий 2: Проверка релевантности

```python
from storage import TenderDB

db = TenderDB("tenders.db")

# Тендеры, релевантные для нашей компании
keywords = ["грузоперев", "логистическ", "доставк"]

with sqlite3.connect(db.db_path) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    for keyword in keywords:
        cursor.execute(
            "SELECT * FROM tenders WHERE title LIKE ? AND amount > ?",
            (f"%{keyword}%", 100000)
        )
        tenders = cursor.fetchall()
        print(f"\nПо '{keyword}': {len(tenders)} тендеров")
        for t in tenders[:5]:
            print(f"  - {t['title']}")
```

---

**Дата**: апрель 2026  
**Версия MVP**: 0.1.0
