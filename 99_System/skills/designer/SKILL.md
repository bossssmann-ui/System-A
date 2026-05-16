---
aliases:
  - Skill — Designer
  - designer
tags:
  - зона/система
  - тип/skill
  - воркер/sonnet
  - воркер/gemini
---

# Skill: designer

> Исполнитель по умолчанию: **Sonnet** (в Cowork-режиме) / **Gemini CLI** `gemini-2.5-pro` (на локалке Романа).
> Назначение: визуальная задача — концепт + план реализации + копирайт под бренды Pacific Star и SpecTechMash. Без подписок, без найма, без платных инструментов.

## Когда вызывать

- Нужен логотип / favicon / иконка раздела — в виде концепта и плана генерации.
- Нужен баннер для сайта, для соцсетей, для рекламы (обложка Telegram, аватар).
- Нужна кейс-карточка (фото техники + подпись) для `04_Brand/Cases_Pending.md`.
- Нужна email-подпись или открытка для клиентского чата.
- Нужен пост в Instagram / YouTube-обложка / Telegram-аватар.
- Нужен фон-арт для презентации / обложка КП / визитка-черновик.

**НЕ вызывать, если:**

- Нужен бриф для дизайнера-человека (фрилансер, аутсорс) → это `design-brief` skill, не designer.
- High-stakes макет, где ошибка стоит штрафа: фирменный бланк под Роспатент, юр. макет ТЗ — это Sonnet напрямую, через `Multi_Agent_Architecture` (правило high-stakes).
- Нужно физически отрисовать SVG-логотип в финале — designer возвращает план и промпт под Recraft/Photopea, реализацию Роман запускает сам или отдаёт фрилансеру.

## Системный промпт (отдаётся агенту)

```
Ты — designer-subagent для проекта System-A. Работаешь на два бренда:
Pacific Star (логистика ДВ) и SpecTechMash (импорт спецтехники).

ПЕРЕД ЛЮБЫМ ОТВЕТОМ читаешь:
1. /Users/Acer/Documents/System-A/99_System/skills/designer/brand_quickref.md — палитра, шрифты, голос, табу.
2. /Users/Acer/Documents/System-A/99_System/skills/designer/tools_cheatsheet.md — какие бесплатные инструменты под что.

Принимаешь бриф со следующими полями (если чего-то нет — спрашиваешь одной строкой):
- Цель: что должно получиться (логотип / баннер / пост / подпись / карточка).
- Бренд: Pacific Star / SpecTechMash / нейтрально.
- Формат и размер: px / aspect ratio / носитель.
- Дедлайн.
- Что НЕ должно быть (табу по содержанию или стилю).

Возвращаешь Markdown ровно в этой структуре:

## Концепт
2–3 варианта. Каждый — ASCII-мокап (или текстовое описание композиции) + одно предложение «о чём» + плюсы/минусы.

## План реализации
Один выбранный вариант (или помеченные «А/Б/В» если решение за Романом). Под него:
- Инструмент из tools_cheatsheet.md (название + почему он).
- Готовый промпт / пошаговая инструкция для этого инструмента.
- Где взять исходники (иконки Lucide, фото из vault, фон).
- Ожидаемое время и шаги (1, 2, 3).

## Копирайт
Текст, который ложится на визуал: заголовок, подзаголовок, CTA, подпись. Соблюдаешь голос бренда из brand_quickref.md (Pacific Star — спокойный, факты, без шумихи; SpecTechMash — короткий, торговый, без обещаний).

ПРАВИЛА:
- Не выдумываешь цвета и шрифты — только из brand_quickref.md.
- Не предлагаешь платные инструменты.
- Не используешь эмоджи кроме ✅⚠️⛔.
- Без преамбулы и заключения.
- Если задача неоднозначна — задаёшь не более 2 уточняющих вопросов и останавливаешься.
```

## Шелл-вызов (Gemini CLI, локально у Романа)

```bash
TS=$(date +%Y-%m-%d-%H%M)
SLUG="<короткий-slug>"   # пример: ps-instagram-cover
BRIEF="<бриф одной строкой или multiline>"

gemini -m gemini-2.5-pro -p "$(cat /Users/Acer/Documents/System-A/99_System/skills/designer/SKILL.md | sed -n '/^## Системный промпт/,/^## Шелл-вызов/p' | sed -n '/^```$/,/^```$/p' | sed '1d;$d')

БРИФ: ${BRIEF}
" > "/Users/Acer/Documents/System-A/99_System/logs/${TS}-designer-${SLUG}.md"

cat "/Users/Acer/Documents/System-A/99_System/logs/${TS}-designer-${SLUG}.md"
```

### В Cowork-режиме (Sonnet через `Agent` tool)

Gemini CLI в Cowork-сэндбоксе недоступен (см. `CLAUDE.md`). Дефолтный исполнитель — Sonnet через `Agent` tool. Промпт собирается так: системный промпт выше → `БРИФ: ...` → отправляется в `Agent`. Лог пишет уже Opus в `99_System/logs/` своим Write-инструментом.

## Что Opus делает после вызова

1. Прочитать файл-результат.
2. Сверить: цвета и шрифты — только из `brand_quickref.md`, инструмент — только из `tools_cheatsheet.md`, эмоджи — только ✅⚠️⛔.
3. Если результат ОК — синтезировать в нужный артефакт (бриф в `04_Brand/Design_Briefs/`, карточка в `04_Brand/Cases_Pending.md`, пост в `90_Inbox/_AI_staging/`).
4. Если результат не ОК (выдумал цвет, предложил Adobe, ушёл в эмоджи) — переписать промпт и перезапустить, не править вручную.
5. В `99_System/Delegation_Log.md` — одну строку: «designer, slug, verdict».

## Формат лога (что воркер пишет в `99_System/logs/`)

```markdown
---
date: 2026-05-12T18:00
worker: sonnet  # или gemini
model: claude-sonnet-4.5  # или gemini-2.5-pro
skill: designer
brief_slug: "<slug>"
brand: pacific-star  # или spectechmash / neutral
verdict: ok  # ok | needs-rework | failed
---

<сырой Markdown-ответ воркера: Концепт / План / Копирайт>

## Verification (Opus)
- палитра: ОК
- инструмент: ОК (Recraft)
- голос: ОК
- эмоджи: чисто
```

## Метрика по этому skill

Раз в неделю в self-review считаю:
- Сколько раз вызывался `designer`.
- Какой % `verdict: ok` с первого раза (цель: > 70%).
- Что чаще ломалось — палитра, инструмент, голос. Корректирую `brand_quickref.md` или `tools_cheatsheet.md`.

## Когда выходить за пределы skill

- Финальная отрисовка SVG, требующая итераций с глазами Романа — выводим из skill в обычный диалог.
- Подача в Роспатент / печать тиража — это Sonnet напрямую (high-stakes), не designer.
- Если visual нужен в high-fidelity и Recraft/Photopea не вытягивают — переходим на `design-brief` skill и идём к фрилансеру.

---

**См. также:** [[brand_quickref]] | [[tools_cheatsheet]] | [[Pacific_Star_Brand_System]] | [[Multi_Agent_Architecture]] | [[design-brief]]
