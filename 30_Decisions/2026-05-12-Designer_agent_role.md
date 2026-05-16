---
aliases:
  - Designer как роль агента
  - Решение 2026-05-12-Designer
tags:
  - зона/система
  - тип/решение
date: 2026-05-12
---

# Решение: заводим роль «designer» как специализированную надстройку над Sonnet/Gemini

## Контекст

В проекте регулярно возникают визуальные задачи: лого, баннеры, кейс-карточки техники, email-подписи, посты соцсетей, обложки Telegram/YouTube. Нанимать дизайнера на постоянку дорого, фрилансер через `design-brief` нужен только для high-stakes (логотип под Роспатент, фирменный бланк). Для всего остального — концепты, превью, посты — нужен внутренний AI-помощник с дисциплиной по бренду, без выдумывания цветов и без платных инструментов.

## Решение

Заводим роль **`designer`** в архитектуру мульти-агентов как специализированную надстройку:

1. **Исполнитель**: Sonnet через `Agent` tool в Cowork-режиме / Gemini CLI `gemini-2.5-pro` на локалке Романа. По правилу из `CLAUDE.md` про вынужденную замену.
2. **Артефакты skill'а**: `99_System/skills/designer/SKILL.md` (системный промпт, шелл-вызов, формат лога), `brand_quickref.md` (палитры обоих брендов в одном месте), `tools_cheatsheet.md` (бесплатный стек: Recraft, Photopea, Canva, Figma, Lucide, Remove.bg, Squoosh, Coolors).
3. **Зона ответственности**: концепт + план реализации (с конкретным промптом под инструмент) + копирайт под визуал. Финальную отрисовку Роман запускает сам или отдаёт фрилансеру через `design-brief`.
4. **Граница с `design-brief`**: `design-brief` — бриф для дизайнера-человека на аутсорс (логотип в Роспатент, фирменный бланк). `designer` — inhouse-генерация концепта и инструкций под бесплатные инструменты. Не пересекаются.
5. **Граница с прямым Sonnet**: high-stakes визуальные задачи (макет под Роспатент, юр. документ, реклама с риском штрафа) идут не через designer, а напрямую в Sonnet по правилу high-stakes из `Multi_Agent_Architecture`.

## Что внедрено в эту сессию

- `99_System/skills/designer/SKILL.md` — системный промпт + шелл-вызов + формат лога + метрика.
- `99_System/skills/designer/brand_quickref.md` — палитра Pacific Star (`#002B5C` Pacific Deep, `#E8B647` Star Gold, Manrope/Inter), SpecTechMash (палитра TBD, нейтральная по умолчанию), голос обоих брендов, табу.
- `99_System/skills/designer/tools_cheatsheet.md` — Recraft.ai (дефолт по вектору), Photopea (растровая постобработка), Canva/Figma (с VPN), Lucide/Tabler (иконки), Remove.bg, Squoosh, Coolors.
- `99_System/Multi_Agent_Architecture.md` — короткая вставка про роль designer в таблицу skills.
- `99_System/Pinned Facts.md` — одна строка в разделе про делегирование sub-agent'ам.

## Триггеры пересмотра

- Если Sonnet/Gemini регулярно (>30%) выдают результат вне палитры или с платными инструментами — ужесточить системный промпт или вынести brand_quickref в обязательный prefix.
- Если задачи начнут массово требовать финальную отрисовку (а не концепт+план) — пересмотреть зону ответственности или подключить отдельный image-generation MCP.
- Если SpecTechMash утвердит свою палитру — обновить `brand_quickref.md` (сейчас TBD).
- Если появится бесплатный российский аналог Recraft с доступом без VPN — добавить в `tools_cheatsheet.md`.

## См. также

- [[SKILL|designer/SKILL]] — сам skill.
- [[brand_quickref]] | [[tools_cheatsheet]] — компаньоны skill'а.
- [[2026-05-08-Gemini_as_default_worker]] — базовая модель дефолтного воркера.
- [[2026-05-12-CLAUDE_md_director_role]] — правило про Sonnet в Cowork как вынужденную замену.
- [[Multi_Agent_Architecture]] — общая архитектура.
- [[Pacific_Star_Brand_System]] | [[SpecTechMash]] — источники правды по брендам.
