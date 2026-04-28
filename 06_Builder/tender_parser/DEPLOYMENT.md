# Развёртывание парсера на production

## Предварительные требования

- Linux сервер (Ubuntu 20.04+ или CentOS 7+) или macOS
- Python 3.10+
- pip
- Git (опционально, для клонирования репозитория)
- Минимум 500 МБ свободного места
- Доступ в интернет (для загрузки Chromium и зависимостей)

## Шаг 1: Подготовка окружения

### 1.1 Создать пользователя для парсера (опционально, рекомендуется)

```bash
# На Linux сервере
sudo useradd -m -s /bin/bash tender_parser
sudo su - tender_parser
```

### 1.2 Клонировать проект

```bash
git clone <repo_url> /home/tender_parser/parser
cd /home/tender_parser/parser
```

Или скопировать файлы:

```bash
cp -r tender_parser/ /home/tender_parser/parser
cd /home/tender_parser/parser
```

### 1.3 Создать виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 1.4 Установить зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt

# Установить Chromium для Playwright
playwright install chromium
```

## Шаг 2: Инициализация БД

```bash
# БД создаётся автоматически при первом запуске
python3 parser.py --limit 5
```

Проверить создание БД:

```bash
ls -lh tenders.db
sqlite3 tenders.db ".tables"
```

## Шаг 3: Тестовый запуск

```bash
# Пробный запуск с 10 тендерами
python3 parser.py --limit 10

# Проверить результаты
tail -20 parser.log
sqlite3 tenders.db "SELECT COUNT(*) FROM tenders;"
```

Ожидаемый вывод:
```
====================================================================================================
=== РЕЗУЛЬТАТЫ ПАРСИНГА ТЕНДЕРОВ ===
====================================================================================================

Найдено всего: X
Добавлено новых: Y
Всего в БД: Z
```

## Шаг 4: Настройка резервной копии БД

### 4.1 Создать скрипт резервной копии

```bash
# backup_db.sh
#!/bin/bash

BACKUP_DIR="/home/tender_parser/backups"
DB_PATH="/home/tender_parser/parser/tenders.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cp "$DB_PATH" "$BACKUP_DIR/tenders_$DATE.db"

# Удалить старые копии (старше 30 дней)
find "$BACKUP_DIR" -name "tenders_*.db" -mtime +30 -delete

echo "Резервная копия создана: $BACKUP_DIR/tenders_$DATE.db"
```

### 4.2 Сделать скрипт исполняемым

```bash
chmod +x /home/tender_parser/backup_db.sh
```

### 4.3 Добавить в cron

```bash
# Резервная копия ежедневно в 02:00
0 2 * * * /home/tender_parser/backup_db.sh >> /home/tender_parser/backup.log 2>&1
```

## Шаг 5: Настройка cron задачи

### 5.1 Отредактировать crontab

```bash
crontab -e
```

### 5.2 Добавить задачу парсера

```bash
# Запуск парсера ежедневно в 03:00 UTC
0 3 * * * cd /home/tender_parser/parser && /home/tender_parser/parser/venv/bin/python3 parser.py >> /home/tender_parser/cron.log 2>&1
```

### 5.3 Добавить задачу резервной копии

```bash
# Резервная копия в 02:00 UTC
0 2 * * * /home/tender_parser/backup_db.sh >> /home/tender_parser/backup.log 2>&1

# Очистка старых логов (старше 60 дней)
0 5 * * * find /home/tender_parser -name "*.log" -mtime +60 -delete
```

### 5.4 Проверить установленные cron задачи

```bash
crontab -l
```

## Шаг 6: Мониторинг и логирование

### 6.1 Проверить логи

```bash
# Последние 100 строк парсера
tail -100 /home/tender_parser/parser/parser.log

# Логи cron
tail -50 /home/tender_parser/cron.log

# Ошибки в cron логах
grep ERROR /home/tender_parser/cron.log
```

### 6.2 Настроить отправку логов (опционально)

```bash
# На end of cron command добавить отправку по почте
0 3 * * * cd /home/tender_parser/parser && /home/tender_parser/parser/venv/bin/python3 parser.py >> /home/tender_parser/cron.log 2>&1 && cat /home/tender_parser/cron.log | mail -s "Парсер тендеров - результаты $(date +\%Y-\%m-\%d)" admin@example.com
```

### 6.3 Использовать systemd timer (альтернатива cron)

```bash
# /etc/systemd/system/tender-parser.service
[Unit]
Description=Tender Parser Service
After=network.target

[Service]
User=tender_parser
WorkingDirectory=/home/tender_parser/parser
ExecStart=/home/tender_parser/parser/venv/bin/python3 parser.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/systemd/system/tender-parser.timer
[Unit]
Description=Tender Parser Timer
Requires=tender-parser.service

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Активировать:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tender-parser.timer
sudo systemctl start tender-parser.timer
sudo systemctl status tender-parser.timer
```

## Шаг 7: Веб-интерфейс для просмотра результатов (планируется)

На данный момент парсер выводит результаты в консоль и SQLite. Для следующей итерации планируется:

- REST API для доступа к БД
- Веб-панель для просмотра тендеров
- Экспорт в CSV/Excel

## Шаг 8: Обновление парсера

```bash
# Переходим в директорию
cd /home/tender_parser/parser

# Получаем обновления (если используется Git)
git pull origin main

# Переактивируем виртуальное окружение
source venv/bin/activate

# Переустанавливаем зависимости
pip install -r requirements.txt --upgrade

# Тестируем
python3 parser.py --limit 5

# Перезагружаем cron
sudo systemctl reload cron  # или systemctl restart cron на некоторых системах
```

## Troubleshooting

### Проблема: "Module not found: playwright"

```bash
# Убедиться, что виртуальное окружение активно
source /home/tender_parser/parser/venv/bin/activate

# Переустановить зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблема: "Chromium not found"

```bash
# Переустановить Chromium
playwright install chromium
```

### Проблема: "Connection refused" при подключении к закупки.gov.ru

1. Проверить интернет соединение
2. Увеличить timeout в config.py
3. Использовать прокси (планируется для итерации 0.2)

### Проблема: "Permission denied" при запуске cron

```bash
# Проверить права на файлы
ls -la /home/tender_parser/parser/

# Дать права на исполнение
chmod 755 /home/tender_parser/parser/parser.py
chmod 755 /home/tender_parser/parser/venv/bin/python3
```

### Проблема: Cron не запускается

1. Проверить crontab
   ```bash
   crontab -l
   ```

2. Проверить логи cron
   ```bash
   grep CRON /var/log/syslog  # на Ubuntu
   # или
   tail -50 /var/log/cron  # на CentOS
   ```

3. Убедиться, что путь корректный
   ```bash
   which python3
   pwd
   ```

4. Перезагрузить cron daemon
   ```bash
   sudo systemctl restart cron
   ```

## Безопасность

### Чек-лист безопасности

- [ ] БД расположена в защищённой директории (не в /tmp)
- [ ] Права доступа: 700 на директорию, 600 на БД
- [ ] Логи содержат чувствительную информацию? (нет)
- [ ] Cron запускается от специального пользователя (не от root)
- [ ] Резервные копии хранятся отдельно
- [ ] Настроен мониторинг ошибок

### Рекомендации

```bash
# Установить правильные права на БД
chmod 600 /home/tender_parser/parser/tenders.db
chmod 700 /home/tender_parser/parser

# Убедиться, что парсер запускается от непривилегированного пользователя
sudo -u tender_parser python3 parser.py --limit 5
```

## Масштабирование

Если парсер обрабатывает более 10 000 тендеров в день:

1. **Увеличить timeout**:
   ```python
   TIMEOUT_MS = 60000  # 60 сек вместо 30
   ```

2. **Использовать прокси**:
   ```python
   PROXY_URL = "http://proxy.example.com:8080"
   ```

3. **Распределённая обработка**:
   - Разделить поиск по регионам
   - Запускать несколько инстансов параллельно
   - Использовать очередь задач (Redis, RabbitMQ)

4. **Оптимизация БД**:
   ```sql
   -- Анализ запроса
   EXPLAIN QUERY PLAN SELECT * FROM tenders WHERE amount > 100000;
   
   -- Добавить индексы при необходимости
   CREATE INDEX idx_amount_law ON tenders(amount DESC, law);
   ```

## Контакты поддержки

Для вопросов и проблем обратитесь к разработчику.

---

**Дата**: апрель 2026  
**Версия**: 0.1.0 (MVP)
