# DAT-RAG-LLM-PROJECT — Repository Structure

## Repository
- **GitHub**: https://github.com/riosee2415/DAT-RAG-LLM-PROJECT

---

## Branch Map

| Branch | Scope | Stack |
|--------|-------|-------|
| `main` | Root config, shared docs, orchestration rules | — |
| `web` | Frontend only (`frontend/`) | Next.js (latest) + TypeScript strict |
| `ai` | Backend only (`backend/`) | Python 3.11 + FastAPI |

### Branch Rules
- `frontend/` 변경 → `web` 브런치
- `backend/` 변경 → `ai` 브런치
- 루트 설정 변경 → `main`, `web`, `ai` 모두

---

## Directory Structure

```
.
├── frontend/                  # Next.js app (web branch)
│   ├── src/
│   │   ├── app/               # App Router (layout, pages)
│   │   └── types/
│   │       └── api.ts         # Shared API contract types
│   ├── public/
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.mjs
│   ├── CLAUDE.md              # Frontend-specific rules
│   └── work_rule.md           # Frontend token optimization index
│
├── backend/                   # FastAPI app (ai branch)
│   ├── app/
│   │   └── schemas/
│   │       └── api.py         # Pydantic models (mirrors frontend types)
│   ├── CLAUDE.md              # Backend-specific rules
│   └── work_rule.md           # Backend token optimization index
│
├── scripts/                   # Dev utility scripts
│   ├── init-frontend.ps1
│   ├── init-backend.ps1
│   ├── generate-test-report.py
│   └── html-to-pdf.js
│
├── test-reports/              # CI test output (gitignored)
├── .test-results/             # Raw test results (gitignored)
│
├── CLAUDE.md                  # Root orchestration rules
├── STRUCTURE.md               # This file
└── work_rule.md               # Root token optimization index
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (latest), TypeScript strict mode |
| Backend | Python 3.11, FastAPI |
| Database | Supabase (Postgres + Auth + Storage) |
| CI Gates | ESLint, tsc --noEmit, vitest, next build (FE) / ruff, mypy --strict, pytest (BE) |

---

## API Contract

Shared types live in two mirrored locations:
- **Frontend**: `frontend/src/types/api.ts`
- **Backend**: `backend/app/schemas/api.py` (Pydantic models)

Neither layer may deviate from the agreed contract without a contract re-issue phase.

---

## CI Gate Pipeline

```
Gate 1 — Lint         eslint --max-warnings 0  |  ruff check
Gate 2 — Type Check   tsc --noEmit             |  mypy --strict
Gate 3 — Unit Tests   vitest run               |  pytest --tb=short
Gate 4 — Build        next build (FE only)     |  — (BE build is implicit)
```

Full pass → `git commit` (conventional commit) → `git push origin <branch>`

---

## Commit Message Format

```
<type>(<scope>): <subject>

type: feat | fix | refactor | test | chore
scope: frontend | backend | root
```
