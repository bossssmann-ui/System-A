---
aliases:
  - Журнал делегирования
  - Delegation Log
tags:
  - зона/система
---

# Delegation Log — Журнал делегирования sub-agents

> Создан по пункту TODO из `Multi_Agent_Architecture.md`.
>
> **Зачем:** измерить, работает ли новая модель оркестрации. Цель — 50%+ задач уходит на sub-agents, не на Opus. Раз в неделю смотрим статистику.

## Как заполнять

При каждой задаче, которую делегируешь sub-agent (не делаешь сам):

```
| Дата | Задача | Модель | Токены saved (est.) | Результат |
```

- **Задача** — 1 строка, суть
- **Модель** — Gemini Flash / Gemini Pro / Sonnet / Haiku / Script (с 10.05.26 дефолт = Gemini, см. [[Multi_Agent_Architecture]] v2)
- **Токены saved** — грубая оценка: сколько бы ушло на Opus
- **Результат** — OK / Итерация (сколько итераций) / Отказ (пришлось делать самому)

## Журнал

| Дата | Задача | Модель | Tokens saved (est.) | Результат |
|---|---|---|---|---|
| 2026-05-05 | Заполнение Assistant_Brief.md | Sonnet (Cowork) | ~8K | OK |
| 2026-05-05 | Создание папок 03/04/20/30 + README | Sonnet (Cowork) | ~3K | OK |
| 2026-05-05 | Skill weekly-inbox-review | Sonnet (Cowork) | ~4K | OK |
| 2026-05-05 | Delegation_Log + AI Staging | Sonnet (Cowork) | ~2K | OK |
| 2026-05-10 | Research для Carrier Lookup — попытка 1 (с web) | Gemini Flash | — | Отказ: google_web_search заблокирован из РФ-сети |
| 2026-05-10 | Research для Carrier Lookup — попытка 2 (без web) | Gemini Flash | ~5K | Итерация: черновик нужного формата, но без конкретики; верифицировал и обогатил Opus через WebSearch. Результат — секция «Research-вывод» в `06_Builder/Carrier_Lookup_Service.md`. Главный урок: Gemini в нашей сети не годится как researcher для свежих фактов; годится как formatter/reasoner из своих знаний |

## Метрики (обновлять раз в неделю)

| Неделя | Задач всего | На Opus | На Sonnet | На Haiku | % делегировано |
|---|---|---|---|---|---|
| 2026-W18 | — | — | — | — | — |

## Цель

- **Текущее** (до 28.04.26): ~85% Opus, 10% Sonnet, 5% Haiku
- **Целевое**: ~20% Opus, 50% Sonnet, 30% Haiku
- **Проверка**: раз в неделю. Если делегировано < 50% — нужно пересмотреть привычку.

---

<!-- AUTO-LINK -->
**См. также:** [[Multi_Agent_Architecture]] | [[Карта системы]] | [[Pinned Facts]]
