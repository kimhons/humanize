> **Engineering Constitution**: `~/.claude/memory/engineering-constitution.md` — global Spec-Driven PDVA, context-engineering rules (token budgets, just-in-time loading), evidence-first verification, anti-patterns. Read on demand at the start of any non-trivial session. Project-specific guidance below; constitution wins on conflicts.

# humanize — Project conventions

## What this project is
<!-- 1–2 sentences: domain, main users, deployment target -->

## Stack
- Language / runtime: <!-- e.g. TypeScript 5.x on Node 24 -->
- Framework: <!-- e.g. Next.js 15 / NestJS / FastAPI / Axum -->
- Data: <!-- e.g. Postgres 16 via Prisma, Redis for queues -->
- Package manager: <!-- pnpm / npm / bun / yarn — PICK ONE -->
- Deploy target: <!-- AWS / Vercel / Fly.io / Cloudflare / etc. -->

## Commands
```bash
# install
<pnpm install>

# dev
<pnpm dev>

# test (full)
<pnpm test>

# test (fast feedback while iterating)
<pnpm test:unit>

# lint + types
<pnpm lint && pnpm typecheck>

# build (production)
<pnpm build>
```

## Conventions
- Branch names: `feat/…`, `fix/…`, `chore/…`, `refactor/…`
- Commits: conventional commits with structured trailers (see global Commit Protocol)
- PRs: small, single-concern; include a "Test plan" section.

## Hidden gotchas
<!-- Anything a new contributor (or Claude) would get burned by. Examples:
- "DATABASE_URL must use ?sslmode=require on staging or migrations hang."
- "The auth middleware expects the x-trace-id header; tests set it via fixtures/headers.ts."
- "Do not touch src/legacy/ — it's scheduled for deletion in Q3."
-->

## Project-specific exceptions to the constitution
<!-- Only document deviations from `~/.claude/memory/engineering-constitution.md`. Examples:
- "Phase 0 triage threshold lifted to 50 lines for this repo (tight scope, low blast radius)."
- "TDD waived for `src/migrations/` — tests live in `test:integration` only."
- "HIPAA compliance verification required on every PR touching `services/admin-service/` or `packages/llm-orchestrator/`."
-->

## Sub-agents preferred for this project
<!-- Default routing additions/overrides. Examples:
- `jeff-flutter-expert` — Flutter app work in `apps/romas_app/`
- `romas-specialist` — clinical workflow / radiobiology / FHIR
- `security-reviewer` — required on every PR touching auth, db, or PHI
-->

## Imports
<!-- Use @path/to/file.md to pull in additional context files. Each import expands at session start. -->
<!-- @docs/architecture.md -->
<!-- @docs/testing.md -->
