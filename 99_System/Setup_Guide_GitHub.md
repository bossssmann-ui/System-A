# Установка: GitHub private repo + Obsidian + Obsidian Git

> Пошаговая инструкция. Делается один раз, ~45–60 минут. Не требует быть программистом. Все действия через мышь, кроме одного копирования команды.

## Архитектура, которую мы ставим

```
┌────────────────┐    git push/pull    ┌────────────────┐
│  Mac: Obsidian │ ◄─────────────────► │ GitHub private │
│  + Obsidian Git│                     │ repo "vault"   │
└────────────────┘                     └───┬────────────┘
                                           │ REST API
                                           ▼
                              ┌────────────────────┐
                              │ Telegram Voice Bot │
                              │  (собираем позже)  │
                              └────────────────────┘
```

На этом этапе iPhone в схеме не участвует. Телефон подключится к vault через Telegram-бот (голос → bot → GitHub → Mac подтягивает).
Если позже захочешь открыть vault прямо на iPhone — добавим Working Copy + Obsidian iOS (~$20 один раз).

## Шаг 1. Создать приватный репозиторий на GitHub

1. Если нет GitHub-аккаунта — зарегистрируйся на https://github.com.
2. Нажми ➕ → **New repository**.
3. Имя: `System-A` (или любое).
4. Visibility: **Private** (обязательно — там будут твои данные).
5. **НЕ ставь** галочку "Add a README" (у нас уже есть).
6. Create repository.
7. На открывшейся странице скопируй URL вида `https://github.com/bossssmann-ui/System-A.git`.

## Шаг 2. Установить GitHub Desktop

Самый простой способ работать с Git без командной строки.

1. Скачай https://desktop.github.com.
2. Установи, войди своим GitHub-аккаунтом.

## Шаг 3. Клонировать репозиторий на Mac

1. В GitHub Desktop: **File → Clone repository**.
2. Выбери `System-A` из списка.
3. Local path: `~/Documents/System-A` (или любой удобный).
4. Clone.

## Шаг 4. Положить стартовый контент в репозиторий

1. Открой Finder в папке `~/Documents/System-A/`.
2. Скопируй содержимое папки `AI_OS_Vault/` (которую тебе собрал AI-помощник) внутрь `~/Documents/System-A/`.
3. В GitHub Desktop увидишь список изменений.
4. Внизу слева: Summary = "initial vault content" → **Commit to main** → **Push origin**.

## Шаг 5. Установить Obsidian

1. Скачай https://obsidian.md.
2. Установи, запусти.
3. При запуске: **Open folder as vault** → выбери `~/Documents/System-A/`.
4. В настройках vault: включи **Settings → Community plugins → Turn on community plugins**.
5. Перезапусти Obsidian.

## Шаг 6. Включить core-плагин Daily Notes

1. Settings → **Core plugins** → Daily notes → On.
2. Settings → **Daily notes**:
   - New file location: `Daily`
   - Template file location: `00_Dashboard/Daily_Note_Template.md`
   - Date format: `YYYY-MM-DD`
   - Open daily note on startup: **on**.
3. Теперь кнопка ⌘+D (или иконка календаря в сайдбаре) сама создаёт сегодняшний `Daily/YYYY-MM-DD.md`.

## Шаг 7. Установить плагин Obsidian Git

1. Settings → **Community plugins** → Browse.
2. Найди **Obsidian Git** → Install → Enable.
3. Настрой:
   - Vault backup interval: `15` минут (автоматически коммитит изменения).
   - Auto pull interval: `5` минут (подтягивает новое от бота).
   - Commit message template: можно оставить по умолчанию.
4. Проверь: сделай пустой коммит через Cmd+P → "Obsidian Git: Commit" — должно работать.

## Шаг 8. Проверить round-trip

1. Создай в Obsidian тестовую заметку в `90_Inbox/Quick.md`: добавь строку `- тест sync`.
2. Жди ~15 минут (или запусти вручную Obsidian Git: Commit-and-push).
3. Зайди на github.com/bossssmann-ui/System-A — строка должна появиться.
4. Удали её в GitHub Web UI, жди 5 минут — в Obsidian должна подтянуться как удалённая.

## Готово

На этом Уровень 1 мобильного капчура закрыт. Теперь:
- Любое изменение в Obsidian на Mac → GitHub.
- Любое изменение в GitHub (в т.ч. от бота) → Obsidian на Mac.
- Моя роль (Memory Curator): читаю/пишу vault напрямую, если ты подключишь папку `~/Documents/System-A` в рабочую сессию.

Дальше — собираем Telegram-бота (отдельная задача, Builder track).

## Частые косяки

- **"Push отклонён"** → у тебя на Mac и в GitHub разные начальные коммиты. Решение: в GitHub Desktop → Repository → Pull → затем Push.
- **Obsidian Git не видит репу** → проверь, что в Obsidian открыта папка, в которой реально есть скрытая `.git/`.
- **Конфликты при одновременном редактировании с iPhone и Mac** → пока не актуально (iPhone в схеме позже). Когда появится — Obsidian Git сам поймает и покажет.
