# Project Harness — Root Orchestration

## FIRST: Load Order (토큰 최적화)
1. `work_rule.md` (이 파일과 같은 경로) — 먼저 읽음
2. 이 파일 (`CLAUDE.md`)
3. task-relevant 파일만 (work_rule.md FILE MAP 참조)

## Communication Protocol — 설명 금지
- 코드·결과만 출력. 설명·요약·서론 금지.
- 응답 마지막: `Done.` 또는 `Failed: [이유]` 한 줄만.
- 예외: 사용자가 "설명해줘", "왜?" 라고 명시한 경우만.
- sub-agent에도 동일 규칙 적용.

## Architecture
| Layer | Tech | Branch |
|-------|------|--------|
| Frontend | Next.js (latest) + TypeScript strict | `web` |
| Backend | Python 3.11 + FastAPI | `ai` |
| Database | Supabase (Postgres + Auth + Storage) | — |

---

## ABSOLUTE RESTRICTIONS
1. **`harness_commands/`** — NEVER read, list, reference, or access. No exceptions. No sub-agent may touch this path.
2. **Cross-scope writes** — Frontend agent writes ONLY to `frontend/`. Backend agent writes ONLY to `backend/`. Zero exceptions.
3. **No clarifying questions** — Make decisions autonomously. Document rationale inline if needed.

---

## Orchestration Philosophy

### Contract-First
Before any implementation begins, the orchestrator extracts and documents the shared API contract:
- Endpoint paths, HTTP methods, status codes
- Request / response schemas (JSON shape)
- Supabase table definitions affected
- Shared TypeScript types (written to `frontend/src/types/api.ts` and mirrored as Pydantic models in `backend/app/schemas/`)

Both agents receive this contract. Neither may deviate from it without re-issuing a new contract phase.

### Parallel Execution
Independent frontend and backend tasks MUST be spawned in a single Agent tool call (two parallel blocks).
Sequential execution is only permitted when one layer's output is a hard dependency of the other.

### Review Loop (mandatory)
After every sub-agent completion, spawn a review agent with a structured checklist (see below).
- **APPROVED** → proceed to next phase
- **REJECTED** → re-invoke the working agent with exact, line-level feedback
- Maximum 3 re-runs; on 4th failure, halt and surface to user

### Review Checklist
Every code review must verify:
- [ ] No `any` / untyped paths (TypeScript) or missing type annotations (Python)
- [ ] No bare `except:` / swallowed errors
- [ ] All new endpoints / components have corresponding tests
- [ ] Contract compliance — matches the agreed API contract exactly
- [ ] No secrets, hardcoded tokens, or debug artifacts
- [ ] Security: no SQL injection vectors, no XSS sinks, auth guards present
- [ ] No N+1 query patterns; async context used correctly
- [ ] Lint and type-check pass locally (reviewer must state this explicitly)

---

## CI Gate Pipeline
The hook runs all gates in order. A failure at any gate aborts everything downstream.

```
Gate 1 — Lint         eslint --max-warnings 0  |  ruff check
Gate 2 — Type Check   tsc --noEmit             |  mypy --strict
Gate 3 — Unit Tests   vitest run               |  pytest --tb=short
Gate 4 — Build        next build (FE only)     |  — (BE build is implicit)
```

On full pass → `git commit` (conventional commit format) → `git push origin <branch>`

---

## Branch Rules
| Change area | Target branch |
|-------------|---------------|
| `frontend/` | `web` |
| `backend/`  | `ai` |
| Root config (shared) | both `web` and `ai` |

---

## Commit Message Format
```
<type>(<scope>): <subject>

type: feat | fix | refactor | test | chore
scope: frontend | backend | root
```
