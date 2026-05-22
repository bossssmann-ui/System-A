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

## Phase 1 — Recruitment Core 🔄 IN PROGRESS

Подфазы по [[HR_System_Roadmap]]: 1A HH.ru ingestion · 1B заявки+воронка (полные флоу) · 1C AI-скоринг · 1D тесты+прокторинг · 1E мессенджер · 1F транскрибация · 1G careers page.

### Phase 1B — Core recruiting flows ✅ DONE (2026-05-21)

**PR:** [#4 Phase 1B: core recruiting flows](https://github.com/bossssmann-ui/hr-system/pull/4) · merged by bossssmann-ui · squash · 5 commits · 28 файлов · +3191/−256 · issue [#3](https://github.com/bossssmann-ui/hr-system/issues/3)

**Что вошло на `master`:**

- **Backend routes (`/api/...`):** org-units (POST/GET), requisitions (POST/GET/GET:id/PATCH:id/transition), vacancies (GET/GET:id/PATCH:id/publish), candidates (POST с дедупом/GET/GET:id), applications (POST/GET/GET:id/PATCH:id/stage), admin (users, audit-events). Паттерн `route → zValidator → requireRole → service → Prisma → DTO`.
- **FSM энфорсится по-настоящему:** `canTransition()` в роутах requisitions + applications → HTTP 422 при отказе.
- **Авто-вакансия:** `vacancy.upsert` при `approved` (идемпотентно).
- **Дедуп кандидатов:** existing record + `deduped:true` при совпадении email/phone.
- **Stage-move:** аппендит `ApplicationStageEvent` в одной транзакции.
- **Audit:** каждый мутирующий роут пишет AuditEvent.
- **Web UI:** реальные страницы вместо placeholder'ов — заявки (list/create/detail с FSM-кнопками по ролям), вакансии, кандидаты, applications **Kanban на нативном HTML5 DnD**, admin (users + audit-log).
- **Contracts:** Zod-схемы в `packages/contracts` — единый источник для backend+web.
- **Тесты:** 44 backend-интеграционных + RLS cross-tenant на новые таблицы + Playwright smoke (полный журней под засеянным owner'ом).
- **e2e инфра:** Vite `/api` proxy, postgres-сервис + seed owner в `validate`-джобе, `docs/TESTING.md` обновлён.

**Ревью:** прошло через субагента (сверка с acceptance-критериями), вердикт MERGE WITH NOTES. Незаблокирующие хвосты: `ApplicationDetailPage` — placeholder с `TODO(phase-1c)`; у вакансий только publish-toggle без generic-edit.

### Phase 1A — HH.ru negotiations sync ✅ DONE (2026-05-21)

**PR:** [#6 Phase 1A: HH negotiations sync](https://github.com/bossssmann-ui/hr-system/pull/6) · merged by bossssmann-ui · issue [#5](https://github.com/bossssmann-ui/hr-system/issues/5)

**Что вошло на `master` (выключено feature-flag'ом `HH_INTEGRATION_ENABLED=false` до подключения реального HH):**

- Стратегия: синхронизируем **только отклики (negotiations) на свои вакансии**, НЕ платную базу резюме (дёшево + чисто по ToS/152-ФЗ).
- Миграции: `Vacancy.hh_vacancy_id` (unique), таблицы `hh_connections` (токены **зашифрованы AES-256-GCM**, `crypto.ts`), `hh_sync_cursors`; RLS tenant-scoped + admin-gated.
- `HhClient` (`backend/src/integrations/hh/`): инъектируемый HTTP-транспорт (тесты на фикстурах, без сети), лимитер 8 rps, exponential 429-backoff, host-guard `isHhApiUrl`.
- Sync-воркер: negotiation → `Candidate` (`source=hh_ru`) + `Application`, идемпотентно по `hh_negotiation_id`, переиспользует дедуп 1B, пишет AuditEvent `hh.sync.candidate_imported`.
- OAuth-роуты `/api/integrations/hh/*` (authorize-url, callback, status, vacancy link, sync), все `requireRole('owner','hr_admin')` + feature-flag; `client_id/secret` из env.
- Admin-страница `/admin/integrations/hh`: connect, link vacancy, manual sync, status.
- 152-ФЗ: `consent_context` на импортированных кандидатах (основание — кандидат сам откликнулся).

**Ревью:** через субагента, вердикт MERGE WITH NOTES — все 10 критериев выполнены, утечки в платный resume-search НЕТ, шифрование токенов реальное. Незаблокирующие хвосты: в `consent_context` нет явной строки «152-ФЗ» (написано legal basis).

**Для боевого включения (шаги Романа в HH, позже):** завести OAuth-приложение на dev.hh.ru (`HH_CLIENT_ID`/`HH_CLIENT_SECRET`), задать `HH_TOKEN_ENCRYPTION_KEY`, выставить `HH_INTEGRATION_ENABLED=true`, разместить вакансию на HH и слинковать её `hh_vacancy_id`.

### Phase 1C — AI-скоринг резюме ✅ DONE (2026-05-22)

**PR:** [#8 Phase 1C: AI candidate scoring](https://github.com/bossssmann-ui/hr-system/pull/8) · merged by bossssmann-ui · issue [#7](https://github.com/bossssmann-ui/hr-system/issues/7) · 34 файла · +1484/−13

**Что вошло на `master` (выключено feature-flag'ом `AI_SCORING_ENABLED=false` до LLM-ключа):**

- Провайдер-абстракция `ScoringProvider` + `AnthropicScoringProvider` (инъектируемый клиент, без живого LLM в CI); провайдер/модель/ключ из env. Seam под Gemini оставлен.
- Zod-схема `ScoringResult` (relevance_score, strengths/gaps, soft-skills, **red_flags + anti_fraud_signals**, values_fit, interview_focus); malformed JSON → retry раз → graceful `status:"failed"`, воронка не падает.
- Async-скоринг при создании Application (ручное + HH-импорт), ручной `POST /:id/rescore`, идемпотентность по `input_hash`.
- Human-in-the-loop: `POST /:id/score-feedback` (agree/disagree + note). **Скоринг advisory — НЕ двигает стадию и не реджектит** (смена стадии только через FSM-роут).
- **152-ФЗ:** контактные PII (имя/email/телефон) **не уходят в LLM** — `buildScoringInput` собирает только job-relevant поля, есть тест на это.
- **Анти-байас** в системном промпте (защищённые характеристики).
- Web: бейдж AI-скора на канбане + достроена `/applications/:id` с панелью скоринга и фидбеком.

**Ревью:** через субагента, вердикт MERGE WITH NOTES — все 8 критериев, PII strip + анти-байас + отсутствие авто-решений подтверждены. Незаблокирующее: плоское именование метаданных в схеме.

**Для боевого включения:** дать `LLM_SCORING_API_KEY` (Anthropic), `AI_SCORING_ENABLED=true`, опц. `LLM_SCORING_MODEL`.

### Phase 1F — транскрибация интервью → протокол → черновик оффера ✅ DONE (2026-05-22)

**PR:** [#10 Phase 1F](https://github.com/bossssmann-ui/hr-system/pull/10) · merged by bossssmann-ui · issue [#9](https://github.com/bossssmann-ui/hr-system/issues/9)

**Что вошло на `master` (выключено `TRANSCRIPTION_ENABLED=false` до ASR-ключа):**

- Модель `Interview` (consent_recorded, статус-FSM created→transcribing→transcribed→protocol_ready→failed), JSONB transcript/protocol/offer_draft; RLS (ENABLE+FORCE) на таблице.
- ASR-абстракция `TranscriptionProvider` + `YandexSpeechKitProvider` (инъектируемый HTTP, без живого ASR в CI); seam под self-hosted Whisper; feature-flag.
- Очередь transcribe→protocol→offer_draft, идемпотентно, graceful; AuditEvents.
- Протокол через LLM-seam (1C), Zod-валидация, **quote-links** {segment_index, quote}.
- **Offer draft — детерминированный маппинг** из agreed_terms (не LLM, аудируемо).
- 152-ФЗ: consent-гейт блокирует транскрипцию без согласия; запись/транскрипт по основанию согласия.
- Web: InterviewPanel (upload, consent, статус, transcript, протокол, offer-draft с «Show source»).

**Ревью:** пост-фактум через **Gemini** (по директиве — не Sonnet). Offer детерминирован ✅, consent-гейт держит ✅ (skip-return), RLS на БД ✅. Gemini флагнул app-level отсутствие tenant-фильтра — ложная тревога (БД-RLS закрывает). Мелочь на потом: добавить app-level tenantId-фильтр для defense-in-depth.

**Для боевого включения:** ASR-провайдер + ключ (Yandex SpeechKit `ASR_API_KEY`/`ASR_FOLDER_ID` или self-hosted Whisper), `TRANSCRIPTION_ENABLED=true`; LLM-ключ общий с 1C.

### Phase 1E — мессенджер с кандидатом ✅ DONE (2026-05-22)

**PR:** [#12 Phase 1E](https://github.com/bossssmann-ui/hr-system/pull/12) · merged by bossssmann-ui · issue [#11](https://github.com/bossssmann-ui/hr-system/issues/11)

**Что вошло на `master` (каналы за feature-flag'ами):**

- Единый тред: `Conversation` + `Message` (channel/direction/status) + `MessageTemplate`; RLS; дедуп входящих по `(channel, external_id)`.
- Channel-адаптеры: `InAppChannel`, `HhChatChannel` (переиспользует HH-клиент), `TelegramChannel` (вебхук + Bot API), `EmailChannel` (исходящий SMTP, nodemailer). Все инъектируемы, мокаются.
- Async-отправка через очередь (queued→sent|failed); AI-черновики через 1C LLM-seam (всегда draft, без авто-отправки; PII не уходит).
- Шаблоны с переменными; Web `/inbox` + `/inbox/:id`.

**Quiet Hours fix ✅** ([PR #14](https://github.com/bossssmann-ui/hr-system/pull/14) merged 2026-05-22): конфигурируемое окно, дефолт активной отправки **23:00→15:00 UTC** (09:00 Владивосток → 18:00 Москва), обработка перехода через полночь; manual-отправки не глушатся. 119/119 unit-тестов, CodeQL 0 alerts.

**Для боевого включения:** Telegram bot token + webhook; SMTP-креды; `Candidate.externalIds.telegram_chat_id` для роутинга.

### Phase 1G — careers-страница ✅ DONE (2026-05-22)

**PR:** [#16 Phase 1G](https://github.com/bossssmann-ui/hr-system/pull/16) · merged by bossssmann-ui · issue [#15](https://github.com/bossssmann-ui/hr-system/issues/15)

**Что вошло на `master` (за флагом `CAREERS_PAGE_ENABLED`):**

- Публичные (без авторизации) эндпоинты `/api/public/vacancies`, `/:slug`, `POST /:slug/apply`; `Vacancy.slug` (уникальный, авто из title).
- Публичные web-роуты `/careers` + `/careers/:slug` (работают залогаут), apply-форма, OG-метатеги для превью ссылок.
- Apply → Candidate(`source=careers_page`)+Application(`new`) в воронку, дедуп, AI-скоринг если включён.
- Свой бесплатный канал откликов, 0 зависимости от HH/платных ключей.

**Ревью:** через **Gemini** (целевое, публичная security-часть). Вердикт OK: отдаёт только `is_published`, tenant сервером (`resolveBootstrapTenant`, не из запроса), consent обязателен (422), honeypot+rate-limit, дедуп. Утечек внутренних полей нет.

**Для боевого включения:** `CAREERS_PAGE_ENABLED=true`, опубликовать вакансию, шарить ссылку.

### Phase 1D — тесты с прокторингом + автогенерация вопросов 🔜 NEXT (последняя в Phase 1)

Прокторинг тестов (Trust Score: paste-detection, focus-loss, видео-фрейминг) + AI-генерация именных вопросов для интервью под вакансию и резюме.

> Хвост закрыт: [#14 Quiet Hours fix](https://github.com/bossssmann-ui/hr-system/pull/14) merged 2026-05-22 (конфликты разрулены, активное окно 09:00 ВЛ → 18:00 МСК).

---

## Вспомогательный инструментарий

### claude-tdd v0.1 ✅ DONE (2026-05-20)

**Репо:** [bossssmann-ui/claude-tdd](https://github.com/bossssmann-ui/claude-tdd) · [PR #2](https://github.com/bossssmann-ui/claude-tdd/pull/2) merged · 21 файл · +834

TDD-CLI: тест → Claude пишет код. Bun + @anthropic-ai/sdk, default model `claude-opus-4-6`, флаги `--iterate`/`--model`/`--context`/`--dry-run`, exit codes 0–4, CI на Bun. Замена мёртвого ai-tdd.

**Чтобы начать пользоваться:** склонировать репо, `bun install`, `export ANTHROPIC_API_KEY=...`, затем `bun run build` и `claude-tdd <тест-файл>`.

---

<!-- AUTO-LINK -->
**См. также:** [[HR_System_Roadmap]] | [[00-phase-0-bootstrap]] | [[CLAUDE]]
