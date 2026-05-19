---
aliases:
  - Phase 0 issue body
  - HR-System Phase 0
tags:
  - зона/builder
  - тип/issue
  - проект/hr-system
  - фаза/0
created: 2026-05-20
status: ready-to-paste
---

# Phase 0 — issue body для GitHub

> **Назначение:** готовый текст GitHub Issue. Создаётся в репозитории `bossssmann-ui/hr-system` и назначается Copilot Coding Agent (Opus).

## Инструкция по созданию issue (3 клика)

1. Откройте https://github.com/new
   - **Repository name:** `hr-system`
   - **Description:** `Собственная HRIS-платформа уровня Onboardix`
   - **Private** — включить
   - **Initialize this repository with: README** — НЕ ставить галочку (vibe-шаблон даст свой)
   - Нажать **Create repository**

2. На странице нового репо открыть **Issues → New issue**.

3. Скопировать всё содержимое раздела **«Issue body»** ниже (от заголовка `# Phase 0: Project bootstrap from vibe template` до конца этого файла) и вставить в тело issue.
   - **Title:** `Phase 0: Project bootstrap from vibe template`
   - В правом сайдбаре **Assignees → Copilot**
   - **Submit new issue**

4. Сразу после Submit — пришлите мне ссылку на issue. Я подключу read-MCP для отслеживания PR.

---

## Что делать после, когда Copilot создаст PR

1. В репо появится **draft Pull Request** с веткой `copilot/phase-0-foundation` (или похожей).
2. Пришлите мне номер PR (например, `#1` или `#2`).
3. Я через read-MCP прочитаю diff, проверю соответствие spec'у, и **выдам вам**:
   - Либо вердикт «✓ мержить» — вы делаете Merge в GitHub UI.
   - Либо набор review-комментариев в виде текста — вы вставляете их в PR как comment, Copilot подхватывает и исправляет.
4. Цикл повторяется 1-2 раза до полной готовности Phase 0.

---

# Issue body

# Phase 0: Project bootstrap from vibe template

## Context

This repository was created from the [vibe coding template](https://github.com/bossssmann-ui/vibe). The product we are building is a corporate HRIS/ERP platform: full-cycle from job requisition and resume parsing through offboarding and alumni network. Roadmap (12 phases) lives in a private Obsidian vault; this issue covers **Phase 0 — project bootstrap and architectural foundation only**. Subsequent issues will cover Phase 1+ (recruiting core, offer + DocuSeal, onboarding, lifecycle, LMS, performance, finance, analytics, partner, compliance, mobile).

## Intake answers (from vibe README checklist)

These are the answers to the Agent Intake Checklist from vibe's README. Use them as the source of truth during setup; do not re-ask.

- **Is this a new project from the template or work on the template itself?**
  New project. Detach the original `vibe` template remote. Do not open pull requests back to the template.

- **Project name / slug:** `hr-system`. Package name in `package.json` and any other repository-specific identifiers should be renamed to `hr-system`. Update display names where applicable.

- **GitHub destination:** `https://github.com/bossssmann-ui/hr-system` (this repository). Already set as `origin`; do not add or remove remotes beyond this.

- **What product to build first and the first user journey that should work:**
  Recruiting core. The first end-to-end user journey is:
  1. A recruiter logs into the web app.
  2. Creates a Hiring Requisition (job, grade, salary range, justification).
  3. Once the requisition is approved, an associated Vacancy goes live.
  4. New `Application` records arrive against this Vacancy (manual creation via UI is enough for Phase 0; HH.ru parsing comes in Phase 1).
  5. The recruiter sees applications in a Kanban funnel and can move them between stages.
  This is the **MVP demo path**. Phase 0 only needs the data model, auth, RLS, and skeleton UI scaffolding for this journey; full flows come in Phase 1.

- **Active surfaces now:** `web`, `backend/API`. Deferred for now: `mobile`, `landing`. Keep the `mobile/` and `landing/` directories intact but mark them deferred in their READMEs per vibe template guidance; do not run Expo/EAS/Maestro setup, do not add features there yet.

- **Auth / persistence / uploads / media / integrations / payments / admin:**
  - **Auth:** yes — JWT + Zod-validated login/register flows (already in vibe template). Add an admin/owner bootstrap mechanism (env-driven seed user on first migration).
  - **Persistence:** yes — PostgreSQL via Prisma. Schema below.
  - **Uploads / files / media:** yes, basic — resume files (PDF, DOC, DOCX). Phase 0 only needs the database fields, upload UI, and stub storage layer pointing to local Docker volume; DigitalOcean Spaces wiring comes in Phase 1 alongside HH.ru parsing. Public/private: **private**. Max size: 10 MB per file. Allowed types: `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`. Thumbnails: not needed. Deletion: soft-delete with retention; hard-delete after 365 days for GDPR/152-ФЗ compliance (will be enforced in Phase 11).
  - **Payments:** no.
  - **Admin tools:** yes, basic — bootstrap UI to manage roles and view audit logs.
  - **External integrations:** **none in Phase 0**. HH.ru, СберПодбор, Avito, Работа.ру, DocuSeal, Telegram, Gemini, OpenAI/Anthropic — all explicitly deferred to later phases.

- **Real-time chat / presence / live notifications / WebSocket:**
  Not in Phase 0. The platform will need real-time updates for the recruiter messenger (Phase 1E) and notifications. Architect with future Valkey/Redis Pub/Sub in mind, but **do not stand up Valkey yet**. Single-instance backend is fine. Just ensure the codebase makes adding a real-time layer non-invasive (events emitted via an abstracted `Notifier` service; HTTP-only delivery for now).

- **Mobile (Expo/EAS, Maestro E2E):** deferred. Do not configure `expo.owner` or `extra.eas.projectId`. Do not run EAS init. Add a deferred-surface note to `mobile/README.md` per vibe template guidance.

- **Deployment:** **not now.** Local-only setup for Phase 0. No DigitalOcean, no Yandex Cloud credentials needed yet. Production deployment will be a separate later phase. Use Docker Compose for local PostgreSQL exactly as documented in `docs/LOCAL_DATABASE.md`.

## Phase 0 deliverables (Definition of Done)

### 1. Repository hygiene

- Rename `package.json` `name` field and any other obvious template-specific identifiers from `vibe` to `hr-system`.
- Detach the template git history reference (delete any `template-remote` if present; ensure `origin` is `bossssmann-ui/hr-system` only).
- Delete the marked **Bootstrap-Only Instructions** blocks from `AGENTS.md` and `CLAUDE.md` per vibe template instructions.
- Update root `README.md`: replace the vibe-template README with a short HR-System README that states project goal, active surfaces (web + backend), deferred surfaces (mobile, landing), and quick-start commands. Keep the architecture notes that still apply.
- Confirm `web/README.md` and `landing/README.md` have a "Deferred surface" note where relevant.
- Verify `git remote -v` shows only `origin = bossssmann-ui/hr-system`.

### 2. Backend foundation

Extend the existing vibe backend skeleton with the following:

- **Database schema** (in `backend/prisma/schema.prisma`). Add these models alongside the existing `User`:
  - `Role` — `owner`, `hr_admin`, `recruiter`, `hiring_manager`, `employee`, `candidate`. Each user has many roles; pivot table.
  - `OrgUnit` — `id`, `name`, `parent_id` (self-referential tree). Every business object below has `org_unit_id`.
  - `HiringRequisition` — `id`, `org_unit_id`, `created_by_user_id`, `title`, `grade`, `salary_min`, `salary_max`, `currency` (enum: `RUB`, `USD`, `THB`, `USDT`), `justification`, `status` (FSM enum: `draft`, `submitted`, `manager_approved`, `hr_approved`, `approved`, `rejected`, `in_recruitment`, `closed`), `deadline_at`, `created_at`, `updated_at`.
  - `Vacancy` — `id`, `requisition_id` (one-to-one), `org_unit_id`, `title`, `description`, `is_published`, `created_at`, `updated_at`. A Vacancy may only exist for an `approved` or `in_recruitment` requisition.
  - `Candidate` — `id`, `full_name`, `email`, `phone`, `location`, `source` (enum: `manual`, `hh_ru`, `sberpodbor`, `avito`, `rabota_ru`, `referral`, `careers_page`), `external_ids` (JSONB; e.g. `{"hh_id": "..."}`), `created_at`, `updated_at`. Unique constraints for natural-key fields where applicable (email when non-null, phone when non-null).
  - `Resume` — `id`, `candidate_id`, `file_url` (private), `parsed_payload` (JSONB), `uploaded_at`. One candidate can have many resumes.
  - `Application` — `id`, `candidate_id`, `vacancy_id`, `stage` (FSM enum: `new`, `screen`, `tech`, `final`, `offer`, `hired`, `rejected`), `assigned_to_user_id`, `notes`, `ai_scoring` (JSONB, nullable, populated in Phase 1), `created_at`, `updated_at`. Unique `(candidate_id, vacancy_id)`.
  - `ApplicationStageEvent` — `id`, `application_id`, `from_stage`, `to_stage`, `actor_user_id`, `comment`, `created_at`. Append-only.
  - `AuditEvent` — `id`, `actor_user_id` (nullable for system actions), `action` (e.g., `requisition.submit`, `application.move_stage`), `entity_type`, `entity_id`, `diff` (JSONB), `ip`, `user_agent`, `created_at`. Indexed by `(entity_type, entity_id)` and `(actor_user_id, created_at)`.
  - All tables: `tenant_id UUID NOT NULL DEFAULT gen_random_uuid()` — even though we are single-tenant for now, include this for future multi-tenancy. Default it to a single bootstrap tenant; do not implement tenant switching yet.

- **FSM enforcement at the service layer.**
  - File `backend/src/features/requisitions/requisitions.fsm.ts` — pure function `canTransition(from, to, actorRoles): boolean` for `HiringRequisition`. Tested.
  - File `backend/src/features/applications/applications.fsm.ts` — same shape for `Application` stages.
  - Routes must call `canTransition` before any update; on failure return HTTP 422 with a structured error code.

- **Row-Level Security (RLS).**
  - Migration that enables RLS on `HiringRequisition`, `Vacancy`, `Candidate`, `Resume`, `Application`, `ApplicationStageEvent`, `AuditEvent`.
  - Policy: a session variable `app.user_id` (UUID) and `app.user_roles` (array) is set via `SET LOCAL` at the start of each request. Policies allow:
    - `owner`, `hr_admin` — full access within their `tenant_id`.
    - `recruiter` — read/write on `Application`, `Candidate`, `Resume`; read on `Vacancy`, `HiringRequisition`; insert into `ApplicationStageEvent` only with `actor_user_id = current_user_id`.
    - `hiring_manager` — read/write on `HiringRequisition` they created or for `org_unit_id` they manage; read on `Application` for their requisitions.
    - `employee`, `candidate` — no access for now.
  - Include a `vitest` integration test that connects as a low-privileged role and asserts cross-tenant rows are not returned and forbidden writes are rejected.

- **Audit middleware.**
  - Hono middleware that wraps mutating routes (`POST`, `PATCH`, `DELETE`). After successful write, write an `AuditEvent` row asynchronously with the diff. Failure to write audit must not roll back the business transaction, but must be logged at error level (for now — observability layer comes later).

- **Notifier abstraction (stub).**
  - File `backend/src/services/notifier.ts` exposing `notify(channel, recipient, template, payload)`. Channels: `email`, `telegram`, `in_app`. Phase 0: only `in_app` implemented (writes a row to a `Notification` table). `email` and `telegram` channels exist as stubs that log "not implemented".

- **Background jobs scaffold.**
  - Add `backend/src/queues/index.ts` with a minimal queue interface. Phase 0 uses in-process setTimeout-based execution; abstraction must allow swapping to BullMQ/Valkey later without changing call sites.

- **OpenAPI output.**
  - Ensure the existing OpenAPI generation from `packages/contracts` covers the new endpoints. No manual hand-editing of the OpenAPI doc.

### 3. Web frontend foundation

- **Routing skeleton** with TanStack Router:
  - `/login`, `/logout`, `/`, `/requisitions`, `/requisitions/new`, `/requisitions/:id`, `/vacancies`, `/vacancies/:id`, `/applications`, `/applications/:id`, `/admin/users`, `/admin/audit-log`.
- **Auth flow** — already in vibe; verify it works with the new role model.
- **Requisitions UI** — list, create form (with Zod-validated TanStack Form), detail view with FSM action buttons (Submit, Approve as Manager, Approve as HR, Reject) gated by role.
- **Vacancies UI** — list (read-only for Phase 0; auto-created from approved requisitions).
- **Applications UI** — Kanban-style board with the stages defined above. Drag-and-drop card between columns triggers `PATCH /applications/:id/stage`. No AI scoring panel yet (Phase 1).
- **Admin pages** — list users with their roles; view audit log (paginated, filterable by `actor`, `entity_type`).
- Use `shadcn/ui` components if vibe already vendors them, otherwise the vibe-default Tailwind components.

### 4. Documentation contracts (anchor for future AI work)

This is the most important deliverable. Create the following files; future Copilot/Claude sessions will read them at the start of every task to stay aligned.

- `docs/contracts/00-overview.md` — system goal, active surfaces, deferred surfaces, decision-making rules.
- `docs/contracts/10-data-model.md` — every entity above with field-level descriptions and invariants.
- `docs/contracts/20-fsm.md` — full state diagrams (mermaid) for `HiringRequisition` and `Application`; allowed transitions per role.
- `docs/contracts/30-rls-policies.md` — exhaustive list of policies; one per table; "what each role can see/do".
- `docs/contracts/40-audit.md` — what gets logged, retention, query patterns.
- `docs/contracts/50-coding-standards.md` — rules for AI agents:
  - Migrations are the ONLY way to change schema.
  - Never bypass FSM `canTransition` calls.
  - Never log secrets; pre-commit scanner must catch this.
  - PR must reference one phase / sub-phase from the roadmap and link the issue.
  - No new dependencies without justification in the PR description.

### 5. Tests

- **Unit tests** for both FSM modules — every legal and illegal transition.
- **Integration tests** for RLS — at least 3 scenarios: cross-tenant denial, role-based read denial, role-based write denial.
- **Backend smoke**: `bun run test:backend` and `bun run test:backend:integration` both pass.
- **Web smoke**: `bun run test:web` passes; basic Playwright auth flow from vibe template still passes.

### 6. Local developer experience

- `bun install` from a clean checkout works.
- `docker compose up -d postgres` brings up local DB.
- `bun run --cwd backend prisma:migrate` applies migrations and seeds the bootstrap tenant + owner user (credentials from `.env.example` — DO NOT commit real credentials).
- `bun run dev:backend` + `bun run dev:web` start the stack.
- Recruiter logs in as the seeded `owner`, creates an `org_unit`, creates a requisition, the journey from the Intake section works end-to-end.

### 7. CI

- GitHub Actions workflow in `.github/workflows/ci.yml` runs on every PR:
  - `bun install`
  - `bun run typecheck`
  - `bun run lint` (if vibe template ships ESLint config) or skip
  - `bun run test` (contracts + backend + web unit/integration)
  - `bun run test:backend:integration` against the `postgres_test` Compose service

## What is explicitly OUT of scope for this issue

These are deferred to later phases and **must not be implemented** in this PR:

- HH.ru, СберПодбор, Avito, Работа.ру integrations.
- AI scoring of resumes (Gemini / Anthropic / OpenAI calls of any kind).
- Anti-fraud / proctoring of tests.
- Chrome extension.
- DocuSeal e-signing.
- Telegram bot / messenger integration.
- Probation FSM, 1:1 meetings, 360 reviews, IDP, OKR.
- LMS, learning paths, knowledge hub (RAG).
- Mobile app (Expo) — leave dormant.
- Landing page (Astro) — leave dormant.
- DigitalOcean / Yandex Cloud deployment configuration.
- Valkey / real-time WebSocket layer.
- ML models of any kind (flight-risk, burnout).
- Email delivery to external SMTP (Notifier stays in stub state).
- Payment processing.

If you find yourself reaching for any of the above, stop and add a TODO with a phase reference instead.

## Acceptance criteria

Reviewer will check the PR against this list:

- [ ] All Phase 0 deliverables above are present.
- [ ] `bun run typecheck`, `bun run test`, `bun run test:backend:integration`, `bun run e2e:web` all pass in CI.
- [ ] The end-to-end demo journey from the "Active surfaces" section runs locally with the seeded data.
- [ ] No items from the "OUT of scope" list have leaked in.
- [ ] `docs/contracts/*.md` files exist and are filled, not placeholders.
- [ ] RLS test passes; manual cross-tenant query is rejected by the database, not just by application code.
- [ ] No real secrets in the repo. `.env.example` only contains placeholder values.
- [ ] PR description references this issue and lists any deviation from the spec with a one-line justification.

## Working style for this agent

This issue will be assigned to GitHub Copilot Coding Agent with Opus 4.6. Please:

1. Open one draft PR titled `Phase 0: foundation`. Do not split into multiple PRs.
2. Make incremental commits with clear messages so the reviewer can follow.
3. If any decision point in the spec is ambiguous, leave a `// TODO(phase-0-review): ...` comment in code and call it out in the PR description rather than guessing.
4. Do not introduce dependencies beyond what vibe template already ships, unless strictly necessary; if you do, list each one in the PR description with a one-sentence justification.
5. When done, request review from `@bossssmann-ui`. The reviewer is a non-engineer and depends on the AI summary in the PR body — make it readable and decision-oriented (what was added, what is verified, what is open).

---

<!-- AUTO-LINK -->
**См. также:** [[HR_System_Roadmap]] | [[CLAUDE]] | [[Карта системы]]
