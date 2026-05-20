---
aliases:
  - HR-System Progress
  - HR-System прогресс-лог
tags:
  - зона/builder
  - тип/progress
  - проект/hr-system
created: 2026-05-20
status: active
---

# HR-System — прогресс-лог

> Хронология фаз. Обновляется по мере merge PR'ов. Полный план — [[HR_System_Roadmap]].

## Phase 0 — Foundation ✅ DONE (2026-05-20)

**PR:** [#2 Phase 0: foundation](https://github.com/bossssmann-ui/hr-system/pull/2) · merged by bossssmann-ui · squash · 8 commits · 44 файла · +3352/−233

**Что вошло на `master`:**

- **Repo hygiene:** переименование из vibe-template в hr-system, README переписан, mobile/landing помечены deferred.
- **docs/contracts/** (6 файлов) — каноничные контракты для будущих AI-сессий: overview, data-model, FSM, RLS-policies, audit, coding-standards.
- **Prisma schema:** 11 моделей (Tenant, UserRole, OrgUnit, HiringRequisition, Vacancy, Candidate, Resume, Application, ApplicationStageEvent, AuditEvent, Notification) + 6 enums. `tenant_id` без DEFAULT — берётся из сессии.
- **Миграции:** baseline DDL + RLS-политики (hand-written SQL с helper-функциями `app.current_user_id()`, `app.has_role()` и т.д.).
- **FSM:** requisitions + applications, pure-функции `canTransition`, 954 ассерта в тестах.
- **Audit middleware** `backend/src/http/audit.ts` + `redact()` для скрабинга секретов.
- **Notifier** stub (in_app работает, email/telegram — заглушки), **Queue** scaffold (BullMQ-совместимый интерфейс).
- **requireRole** guard.
- **Web:** routing skeleton (TanStack Router) + рабочая read-only `/requisitions` страница.
- **Seed script** — идемпотентный bootstrap tenant + owner из env.
- **CI:** `validate` + `backend-integration` (Postgres 18 service), Node 22 pinned.

**Известные хвосты, осознанно отложенные:**
- Полные UI-флоу (формы заявок, FSM-кнопки апрува, kanban с DnD, admin-страницы) — placeholders, доделываются в Phase 1.
- GitGuardian на ветке PR ругался на фейковый JWT в тесте (false positive); squash-merge почистил историю.

## Phase 1 — Recruitment Core 🔜 NEXT

Подфазы по [[HR_System_Roadmap]]: 1A HH.ru ingestion · 1B заявки+воронка (полные флоу) · 1C AI-скоринг · 1D тесты+прокторинг · 1E мессенджер · 1F транскрибация · 1G careers page.

---

## Вспомогательный инструментарий

### claude-tdd v0.1 ✅ DONE (2026-05-20)

**Репо:** [bossssmann-ui/claude-tdd](https://github.com/bossssmann-ui/claude-tdd) · [PR #2](https://github.com/bossssmann-ui/claude-tdd/pull/2) merged · 21 файл · +834

TDD-CLI: тест → Claude пишет код. Bun + @anthropic-ai/sdk, default model `claude-opus-4-6`, флаги `--iterate`/`--model`/`--context`/`--dry-run`, exit codes 0–4, CI на Bun. Замена мёртвого ai-tdd.

**Чтобы начать пользоваться:** склонировать репо, `bun install`, `export ANTHROPIC_API_KEY=...`, затем `bun run build` и `claude-tdd <тест-файл>`.

---

<!-- AUTO-LINK -->
**См. также:** [[HR_System_Roadmap]] | [[00-phase-0-bootstrap]] | [[CLAUDE]]
