# Деплой Telegram Voice Bot → Cloudflare Workers

> Разовая настройка. ~30–45 минут, если все секреты под рукой. Без терминала, кроме одной команды curl в конце.

## Твои конкретные значения

| Параметр | Значение |
|---|---|
| GitHub репо | `bossssmann-ui/System-A` |
| Ветка | `main` |
| Бот | `@Boss_SystemA_bot` |
| Твой Telegram user_id | `105474165` |

Эти 4 значения уже подставлены во все места инструкции. Тебе остаётся только ввести 4 секрета (токен бота, OpenAI key, GitHub PAT, webhook secret).

## Что у нас на выходе

Ты шлёшь голосовое/текст/фото в Telegram → бот получает → голос расшифровывается Whisper → добавляется в `90_Inbox/YYYY-MM-DD.md` в твоём приватном GitHub-репо → Obsidian Git на Mac подтягивает → через 5 минут запись в твоём vault.

Бот отвечает реакциями:
- ✅ — всё записано
- ⚠️ — ошибка (детали тебе придёт текстом)
- ⛔ — кто-то чужой пишет боту (не ты)

## Phase 1. Что ты делаешь руками (регистрации)

Эти 6 шагов ты уже проходишь параллельно. Когда закончишь — у тебя на руках должны быть **7 значений**. Запиши их в надёжное место (например, временно в заметки на Mac):

| # | Значение | Где брать |
|---|---|---|
| 1 | `TELEGRAM_BOT_TOKEN` | От @BotFather → `/mybots` → `@Boss_SystemA_bot` → API Token |
| 2 | `OPENAI_API_KEY` | ✅ у тебя есть |
| 3 | `GITHUB_TOKEN` | Fine-grained PAT с правом Contents: Read & Write на `System-A` (см. отдельно) |
| 4 | `WEBHOOK_SECRET` | Придумай сам: любая случайная строка 20+ символов (например, в терминале `openssl rand -hex 24` или просто набей клавиатуру) |
| 5 | `GITHUB_REPO` | `bossssmann-ui/System-A` ✅ |
| 6 | `GITHUB_BRANCH` | `main` ✅ |
| 7 | `ALLOWED_TG_USER_ID` | `105474165` ✅ |

Если есть вопросы по любому из этих шагов — пиши, распишу детально.

## Phase 2. Создать Cloudflare Worker

### 2.1 Регистрация

1. Если нет аккаунта — https://dash.cloudflare.com/sign-up.
2. Email + пароль. Email-подтверждение.

### 2.2 Создать Worker

1. В дашборде слева: **Workers & Pages** → **Create application** → **Create Worker**.
2. Имя: `cowork-voice-bot` (или любое). Запиши поддомен, который Cloudflare тебе выдаст — будет вида `cowork-voice-bot.TVOJ-POD.workers.dev`. Это будущий webhook URL.
3. **Deploy**. Сейчас там стоит дефолтный "Hello World" код — это ок, мы его сейчас заменим.

### 2.3 Вставить наш код

1. После деплоя: **Edit code** (или **Quick Edit**).
2. В редакторе слева откроется файл `worker.js` с Hello World. **Выдели всё → удали**.
3. Открой на Mac файл `06_Builder/Telegram_Bot/worker.js` (из vault) → **Cmd+A → Cmd+C**.
4. Вставь в Cloudflare редактор.
5. Справа сверху **Save and deploy**.

## Phase 3. Прописать переменные окружения

В том же Worker:

1. Верни назад (стрелка ←) к главному экрану Worker'а.
2. Вкладка **Settings → Variables and Secrets**.
3. Добавь 7 переменных. **Для секретов используй тип Secret (шифруется), для обычных — Text.**

| Имя | Тип | Значение |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Secret | из @BotFather |
| `OPENAI_API_KEY` | Secret | из platform.openai.com |
| `GITHUB_TOKEN` | Secret | fine-grained PAT |
| `WEBHOOK_SECRET` | Secret | твоя случайная строка |
| `GITHUB_REPO` | Text | `bossssmann-ui/System-A` |
| `GITHUB_BRANCH` | Text | `main` |
| `ALLOWED_TG_USER_ID` | Text | `105474165` |

После добавления — **Save and deploy** (в правом верхнем углу).

## Phase 4. Привязать Telegram webhook к Worker

Telegram должен узнать URL, на который слать обновления. Это делается одним curl-запросом.

### 4.1 Собери команду

Замени `TOKEN`, `POD`, `SECRET`:
- `TOKEN` = твой `TELEGRAM_BOT_TOKEN`
- `POD` = поддомен Worker'а (например, `cowork-voice-bot.roman-123.workers.dev` — то, что Cloudflare дал)
- `SECRET` = твой `WEBHOOK_SECRET` (тот же, что в переменных Worker'а)

```bash
curl -X POST "https://api.telegram.org/botTOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://POD",
    "secret_token": "SECRET",
    "allowed_updates": ["message", "edited_message"]
  }'
```

### 4.2 Запуск

**Mac → открой Терминал** (Spotlight → "Терминал"):
1. Вставь собранную команду → Enter.
2. Telegram должен ответить `{"ok":true,"result":true,"description":"Webhook was set"}`.

Если отвечает `{"ok":false,...}` — скорее всего опечатка в URL или токене. Перечитай — исправь.

### 4.3 Проверить статус webhook

```bash
curl "https://api.telegram.org/botTOKEN/getWebhookInfo"
```

Должен показать твой URL и `pending_update_count: 0`.

## Phase 5. Round-trip test

1. **Открой [@Boss_SystemA_bot](https://t.me/Boss_SystemA_bot) в Telegram → /start**. Можно не ждать ответа — /start — просто вход.
2. **Пришли текст**: "тест — привет бот".
3. В течение 5–10 секунд должна появиться реакция ✅.
4. Зайди на github.com/bossssmann-ui/System-A → папка `90_Inbox/` → файл `2026-04-22.md` (или сегодняшняя дата). Там должна быть запись.
5. **Пришли голосовое** на 5–10 секунд. Реакция ✅. В том же файле появится запись типа `### HH:MM — voice` с расшифровкой.
6. В Obsidian на Mac: подожди ~5 минут (auto-pull Obsidian Git) или Cmd+P → "Obsidian Git: Pull". Запись подтянется.

## Если что-то не работает

### Нет реакции от бота вообще
- Проверь `getWebhookInfo` (шаг 4.3). Если там `last_error_message` — читаем его.
- Самое частое: секрет не совпадает (SECRET в curl ≠ `WEBHOOK_SECRET` в переменных Worker'а).

### Реакция ⛔
- Ты пишешь не с того аккаунта, который указан в `ALLOWED_TG_USER_ID`, или вписал чужой user_id. Проверь у @userinfobot ещё раз.

### Реакция ⚠️ + сообщение `whisper failed: 401`
- OpenAI API ключ неверный или биллинг не настроен. Зайди на platform.openai.com → Billing → проверь, что есть платный способ оплаты.

### Реакция ⚠️ + сообщение `github put failed: 404`
- `GITHUB_REPO` указан неверно, или у PAT нет доступа к этому репо, или ветка `main` ещё не создана (сделай первый push из GitHub Desktop).

### Реакция ⚠️ + сообщение `github put failed: 403`
- PAT не имеет права Contents: Read & Write. Пересоздай PAT с правильным scope.

### Реакция ⚠️ + сообщение `tg setMessageReaction failed`
- Это не блокирует запись, просто твой Telegram-клиент старый или в группе без прав на реакции. Игнор. Запись в Inbox всё равно идёт.

### Worker логи
В Cloudflare: Worker → вкладка **Logs** → **Begin log stream**. Видно каждый запрос от Telegram и ошибки консоли (`console.error` из нашего кода).

## После того как заработало

- **Запиши WEBHOOK_SECRET в 1Password / Keychain**. Если потеряется — придётся генерить новый и переустанавливать webhook.
- **Не коммить секреты в GitHub.** В worker.js их нет (они в переменных Cloudflare). Это правильно.
- **Лимиты бесплатных тарифов:**
  - Cloudflare Workers: 100k requests/day free. Мы уложимся в ~0.1% этого.
  - OpenAI Whisper: платный по факту. $0.006/минута. 100 голосовых по 30 сек в месяц = $0.30.
  - GitHub API: 5000 запросов/час на PAT. Запас огромный.

## Что дальше

1. **День 1–2**: обкатай голосовые. Вали всё в Inbox, не структурируй.
2. **День 3**: начинаем пересаживать голосовые в структуру (Fleet, Drivers, SOP — по онбордингу диспетчера). Я читаю Inbox и предлагаю, куда что положить.
3. **Неделя 2**: добавим команды боту — `/task`, `/decide`, `/fleet`, чтобы голос шёл сразу в нужный файл, а не в общий Inbox.

На этом Уровень 2 мобильного капчура закрыт. Теперь мысль из головы доезжает до vault за 10 секунд из любого места.
