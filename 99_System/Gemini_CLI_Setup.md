---
aliases:
  - Gemini CLI Setup
  - Установка Gemini
  - Gemini operational guide
tags:
  - зона/система
  - тип/гайд
---

# Gemini CLI — установка и операционка

> Операционный спутник к [[Multi_Agent_Architecture|Multi_Agent_Architecture v2]]. Архитектурное «зачем» — там, здесь — «как руками».
>
> Создано 08.05.26.

## TL;DR

Gemini CLI = бесплатный воркер. Opus (я) даёт ТЗ через bash → `gemini -m gemini-2.5-flash -p "..."`, читает результат, верифицирует, кладёт в нужное место vault'а. Лог каждого вызова падает в `99_System/logs/`.

**Статус**: установлено и проверено E2E 10.05.26 на MacBook Романа (Владивосток). Сетевой канал нестабильный — gemini-cli уходит в retry 1–3 раза перед каждым запросом, конечный ответ приходит. Принимаем как плату за бесплатность.

## ⚠️ Обязательные настройки окружения

Без этих двух вещей не работает в нашей сети — проверено опытным путём.

### 1. NODE_OPTIONS — форсить IPv4

В `~/.zshrc` должно быть:

```bash
export NODE_OPTIONS=--dns-result-order=ipv4first
```

Без этого Node fetch внутри gemini-cli уходит в IPv6 / HTTP-3 и стабильно падает с `TypeError: fetch failed sending request`. Прописали 10.05.26.

### 2. Всегда явная модель через `-m`

Дефолтный «классификатор» gemini-cli (NumericalClassifierStrategy) ходит на отдельный endpoint, который у нас стабильно блокируется. Решение — указывать модель руками:

- `-m gemini-2.5-flash` — для рутины (быстрее, дешевле, обычно достаточно)
- `-m gemini-2.5-pro` — для сложного research / writing / кода

Без `-m` запрос будет умирать на ретраях классификатора и в итоге проскакивать кое-как — медленно и ненадёжно.

## Шаг 1. Установка (Роман делает один раз)

Требования: Node.js ≥ 18.

```bash
node -v   # >= 18
npm install -g @google/gemini-cli
```

Авторизация — через личный Google-аккаунт (откроется браузер):

```bash
gemini
```

Войти, разрешить. Бесплатный тариф — Gemini 2.5 Pro/Flash, лимиты ~60 запросов/мин и ~1000/день (точные цифры могут меняться, проверять у Google).

Проверка:

```bash
gemini -p "Скажи одной фразой, кто ты."
```

Если ответил — готово.

## Шаг 2. Полезные флаги

- `gemini -m gemini-2.5-flash -p "prompt"` — стандартный non-interactive вызов (наш дефолт).
- `gemini -m gemini-2.5-pro -p "prompt"` — для сложных research/code/writing.
- `gemini -m gemini-2.5-flash -p "prompt" -f path/to/file.md` — добавить файл в контекст.

⚠️ Не забывать `-m` (см. выше) — без явной модели запрос идёт через классификатор и падает.

## Шаг 3. Промпт-шаблоны

Шаблоны живут в `99_System/skills/` (как и все skills). На v2 минимум три:

- `gemini-research.md` — research-обёртка.
- `gemini-writer.md` — writer-обёртка.
- `gemini-critic.md` — critic-обёртка.

Каждый шаблон — самодостаточный системный промпт + плейсхолдер `<TASK>`. При вызове Opus подставляет конкретный TASK и шлёт всё в `gemini -p`.

## Шаг 4. Способы вызова из Opus-оркестратора

### A. Прямой bash (минимум, работает сразу)

```bash
TS=$(date +%Y-%m-%d-%H%M)
gemini -m gemini-2.5-flash -p "$(cat /Users/Acer/Documents/System-A/99_System/skills/gemini-research.md)

TASK: Современные подходы к multi-agent orchestration, 2025.
" > /Users/Acer/Documents/System-A/99_System/logs/${TS}-research-multiagent.md
```

Дальше Opus читает файл и встраивает результат в свой ответ.

⚠️ **Подвох с copy-paste**: при копировании команд из чата Markdown-разметка вокруг имён файлов (`[name.md](http://name.md)`) может попасть в shell как литерал и создать файл с квадратными скобками в имени. Профилактика: либо набирать имя файла руками, либо до запуска проверять команду глазами. Если попался — `mv "странное-имя" "нормальное-имя"` чинит.

### B. MCP `gemini-mcp-tool` (рекомендую после MVP)

```bash
npm install -g gemini-mcp-tool
claude mcp add gemini-cli -- npx -y gemini-mcp-tool
```

После рестарта Claude Code появится инструмент `ask-gemini` — Opus вызывает его как обычный tool, без ручного pipe'а.

### C. Subagent в Claude Code (для шаблонных задач)

`~/.claude/agents/gemini-researcher.md`:

```markdown
---
name: gemini-researcher
description: Делегирует research-задачу в Gemini CLI и сохраняет результат в vault System-A
tools: Bash, Read, Write
---

Ты — обёртка над Gemini CLI для research-задач.
Вход: topic.
Действия:
1) TS=$(date +%Y-%m-%d-%H%M).
2) gemini -p "$(cat /Users/Acer/Documents/System-A/99_System/skills/gemini-research.md)\n\nTOPIC: <topic>" \
     > /Users/Acer/Documents/System-A/99_System/logs/${TS}-research-<slug>.md
3) Прочитай результат.
4) Верни Opus'у: путь к файлу + summary 3–5 строк.
```

## Шаг 5. Дисциплина записи в vault

Вся работа в твоей привычной структуре:

- Финальные артефакты — `10_Operations/`, `02_Sales/`, `04_Brand/`, `06_Builder/` (по зоне задачи).
- Знания/SOP, которые имеет смысл унести в постоянную память — `20_SOP/`.
- Решения с обоснованием — `30_Decisions/`.
- Входящее, не разобранное — `90_Inbox/`.
- **Логи вызовов внешних воркеров** — `99_System/logs/` (новая папка).
- **Делегирование** — `99_System/Delegation_Log.md` (уже есть, дополняем пометкой «Gemini / Sonnet / sam»).

Никаких параллельных папок не плодим — Gemini пишет туда же, куда писал бы я сам.

### Формат лога вызова Gemini

`99_System/logs/2026-05-08-1430-research-multiagent.md`:

```markdown
---
date: 2026-05-08T14:30
worker: gemini
model: gemini-2.5-pro
skill: gemini-research
task: "Современные подходы к multi-agent orchestration"
duration_s: 12
escalated_to: null   # null | sonnet | self
verdict: ok          # ok | needs-rework | failed
---

## Prompt
<полный промпт, который ушёл в Gemini>

## Output
<сырой ответ Gemini>

## Verification (Opus)
- факт 1: проверен через X — ОК
- факт 2: ссылка битая — выкинут
- противоречий не найдено

## Outcome
- что пошло в 06_Builder/.../draft.md
- что записано в 30_Decisions/...
```

Минимум лога: фронтматтер + Prompt + Output + одна строка Verdict. Расширенно — для случаев, где будем потом разбираться, что пошло не так.

## Шаг 6. Чувствительные данные — куда не пускать Gemini

Free tier по ToS Google **может использовать промпты для улучшения модели**. Поэтому в Gemini НЕ кладём:

- ИНН/ОГРН контрагентов в связке с именами/коммерческими условиями.
- Тендерные документы клиентов.
- Реквизиты, телефоны, адреса конкретных людей в связке с бизнес-контекстом.
- Внутренние финансовые данные (выручка, маржа по клиентам).

Эти задачи идут в Sonnet (платный API → не используется для обучения по Anthropic'у).

Если задача смешанная — Opus режет: фактическую часть отдаёт Gemini в обезличенной форме, чувствительную обрабатывает сам или Sonnet'ом.

## Шаг 7. Тестовый запуск (как проверить, что всё работает)

Прогон 10.05.26 — успешный (со 2-3 ретраями). Команда для повторной проверки:

```bash
cd ~/Documents/System-A
mkdir -p 99_System/logs
TS=$(date +%Y-%m-%d-%H%M)
gemini -m gemini-2.5-flash -p "Сформулируй в трёх пунктах, чем мульти-агентная архитектура с дешёвым воркером выгоднее монолита из одной модели. Кратко, фактично, без воды." \
  > 99_System/logs/${TS}-test-multiagent-cost.md
cat 99_System/logs/${TS}-test-multiagent-cost.md
```

Если в файле — три осмысленных пункта, всё ОК. Сообщения «Attempt 1 failed / Attempt 2 failed» в stderr — это нормальное retry-поведение в нашей сети, не ошибка.

## Шаг 8. Параллельные вызовы (когда задач много и они независимы)

```bash
TS=$(date +%Y-%m-%d-%H%M)
gemini -m gemini-2.5-flash -p "research: тема 1" > 99_System/logs/${TS}-r1.md &
gemini -m gemini-2.5-flash -p "research: тема 2" > 99_System/logs/${TS}-r2.md &
gemini -m gemini-2.5-flash -p "research: тема 3" > 99_System/logs/${TS}-r3.md &
wait
```

Лимиты free-tier через API-ключ: ~15 запросов/мин, ~1500/день на Flash. Поэтому 3–5 параллельных — норма, 15 одновременно — край.

## Шаг 9. Цепочка writer → critic → arbiter (для качественных артефактов)

1. Gemini-writer пишет черновик документа.
2. Gemini-critic ревьюит этот же черновик и возвращает список замечаний.
3. Gemini-writer вносит правки с учётом замечаний.
4. Opus читает финал и принимает/правит лично.

Ловит почти все «глупые» ошибки, которые Gemini делает в одиночку. Стоимость — 0 (всё внутри free tier).

## Шаг 10. Метрики и пересмотр

Раз в неделю смотрю по `99_System/logs/`:

- Сколько вызовов Gemini ушло.
- Какой % `verdict: ok` с первого раза.
- Сколько раз `escalated_to: sonnet` — что это были за задачи.
- Где Gemini регулярно валит — корректирую промпты или переношу класс задач в Sonnet.

Цель: > 70% «с первого раза». Если ниже — разбираемся.

## Чек-лист готовности

- [x] Node 18+ установлен
- [x] Gemini CLI установлен (`gemini -m gemini-2.5-flash -p "ping"` отвечает) — 10.05.26
- [x] API-ключ получен в AI Studio и прописан в `~/.zshrc` как `GEMINI_API_KEY` — 10.05.26
- [x] `NODE_OPTIONS=--dns-result-order=ipv4first` прописан в `~/.zshrc` — 10.05.26
- [x] `99_System/logs/` создана
- [x] Тестовый прогон сделан, лог появился — 10.05.26
- [x] [[Multi_Agent_Architecture]] v2 прочитан, правила маршрутизации усвоены Opus'ом
- [x] Решение зафиксировано в `30_Decisions/2026-05-08-Gemini_as_default_worker.md`
- [ ] `99_System/skills/gemini-research.md` создан
- [ ] Первый боевой прогон по реальной задаче — ждёт выбора проекта

---

<!-- AUTO-LINK -->
**См. также:** [[Multi_Agent_Architecture|Архитектура мульти-агентов v2]] | [[Карта системы]] | [[Pinned Facts]] | [[Setup_Guide_GitHub]]
