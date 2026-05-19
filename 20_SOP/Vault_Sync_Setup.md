---
aliases:
  - Vault Sync Setup
  - Синхронизация vault Obsidian↔GitHub
tags:
  - зона/система
  - тип/sop
  - проект/vault
created: 2026-05-19
status: active
---

# SOP — Двусторонняя синхронизация vault'а: Obsidian ↔ GitHub

> Назначение: vault `~/Documents/System-A` всегда совпадает с `github.com/bossssmann-ui/System-A` без ручного `git push`/`git pull`. Работает, когда правки приходят и из Obsidian (Роман), и из Cowork-сессии Claude, и из других машин.

## Архитектура синка

Два независимых механизма работают параллельно:

| Механизм | Что делает | Когда работает |
|---|---|---|
| **Obsidian Git** (плагин) | auto-commit + auto-push | Когда Obsidian открыт |
| **launchd-агент** (`com.system-a.gitpull`) | git pull --rebase каждые 10 мин | Всегда, фоном macOS |

Логика: что бы ни закоммитили — через ≤10 минут это есть на всех концах.

## Установка (одноразово)

### 1. Obsidian Git плагин

1. Obsidian → Settings → Community plugins → Browse.
2. Ищем **Obsidian Git** (автор Vinzent Wang). Install → Enable.
3. Settings → Obsidian Git:
   - `Vault backup interval (minutes)` = **10**
   - `Auto pull interval (minutes)` = **10**
   - `Auto pull on startup` = ✓
   - `Commit message` = `vault: {{date}} {{numFiles}} files`
   - `Pull strategy` = `rebase` (чище история, без merge-коммитов)
   - `Disable push` = ✗ (push включён)
4. Перезапустить Obsidian. В status bar внизу появится индикатор плагина.

### 2. launchd-агент (фоновый pull)

В терминале:

```bash
bash ~/Documents/System-A/99_System/launchd/install-gitpull.sh
```

Что произойдёт:
- plist скопируется в `~/Library/LaunchAgents/com.system-a.gitpull.plist`
- агент стартанёт сразу и потом — каждые 10 минут
- лог в `/tmp/system-a-gitpull.log`

## Проверки работоспособности

```bash
# Агент в списке
launchctl list | grep system-a

# Последние логи
tail -20 /tmp/system-a-gitpull.log

# Когда был последний коммит на main
cd ~/Documents/System-A && git log --oneline -5
```

## Правила работы с конфликтами

### Базовое правило

Один файл — один редактор за раз. Договариваемся до начала работы, кто на этот час владеет файлом.

### Что делать в Cowork-сессии (Claude)

В начале каждой сессии Claude обязан:
1. `git pull --rebase` — забрать свежие правки Романа.
2. Только после этого — редактировать файлы.

В конце сессии Claude:
1. `git add` + `git commit` — закоммитить свои изменения.
2. Push делает либо Claude (если есть креды в окружении), либо Роман одной командой `git push`.

### Что делать при merge-конфликте

Obsidian Git покажет уведомление + файл будет помечен. В терминале:

```bash
cd ~/Documents/System-A
git status                          # видим, какой файл в конфликте
# открыть файл, найти блоки <<<<<<< / ======= / >>>>>>>
# решить вручную (оставить нужный вариант, удалить маркеры)
git add <файл>
git rebase --continue               # если ребейзились
# или git commit, если был merge
git push origin main
```

### Профилактика

- Не редактировать в Obsidian те же файлы, что я правлю в Cowork-сессии прямо сейчас.
- Перед началом большой ручной правки в Obsidian — нажать в плагине Obsidian Git → **Pull** (command palette: `Obsidian Git: Pull`).
- Если знаете, что закроете Obsidian надолго — сделать Push (command palette: `Obsidian Git: Create backup`).

## Что делать, если sync «отвалился»

| Симптом | Что проверить |
|---|---|
| В Obsidian нет изменений, которые я закоммитил из Cowork | `launchctl list \| grep system-a` — агент жив? Если нет — `launchctl load ~/Library/LaunchAgents/com.system-a.gitpull.plist` |
| `tail /tmp/system-a-gitpull.log` показывает `Authentication failed` | Истёк GitHub PAT. Обновить в Keychain или переключить remote на SSH |
| Obsidian Git не пушит | Проверить status в плагине; включить debug-логи в его настройках |
| Бесконечно ребейзится с конфликтом | `git rebase --abort` → `git pull origin main` → решать вручную |

## Переключение на SSH (если HTTPS-токен устаёт обновлять)

```bash
cd ~/Documents/System-A
git remote set-url origin git@github.com:bossssmann-ui/System-A.git
git push -u origin main      # проверка
```

Требует настроенного `~/.ssh/id_ed25519` и загруженного в GitHub публичного ключа.

## Если работаем с нескольких машин

То же самое: на каждой машине ставится Obsidian Git + launchd. Логика «pull→правки→push» одинакова. Конфликты разруливаются по тому же сценарию.

---

<!-- AUTO-LINK -->
**См. также:** [[Карта системы]] | [[CLAUDE]] | [[HR_System_Roadmap]]
