# Backend Agent — Scope & Standards

## FIRST: Load Order
1. `backend/work_rule.md` — 먼저 읽음 (FILE MAP + 학습된 패턴 확인)
2. 이 파일 (`backend/CLAUDE.md`)
3. work_rule.md FILE MAP 기준으로 task-relevant 파일만

## Communication
코드만. `Done.` / `Failed: [이유]` 한 줄로 종료. 설명 금지.

## Hard Boundary
- Modify ONLY files under `backend/`
- NEVER touch `frontend/`, `harness_commands/`, or root config files
- Branch: `ai`

---

## Stack
| Concern | Library |
|---------|---------|
| Framework | FastAPI (latest) |
| Language | Python 3.11, async-first |
| Validation | Pydantic v2 |
| DB client | `supabase-py` (async) |
| Auth | `python-jose` + `passlib[bcrypt]` |
| Rate limiting | `slowapi` |
| Background tasks | ARQ (async Redis queue) |
| Logging | Loguru |
| Error tracking | `sentry-sdk` |
| Linting | Ruff |
| Type checking | mypy (strict) |
| Testing | pytest + pytest-asyncio + httpx |
| Test factories | factory-boy |

---

## Directory Structure
```
backend/
├── app/
│   ├── main.py             # FastAPI app factory
│   ├── core/
│   │   ├── config.py       # pydantic-settings BaseSettings
│   │   ├── security.py     # JWT, password hashing
│   │   └── dependencies.py # shared FastAPI Depends()
│   ├── routers/            # one file per domain (users.py, items.py …)
│   ├── services/           # business logic, no HTTP concerns
│   ├── schemas/            # Pydantic request/response models
│   │   └── api.py          # shared contract schemas (mirrors frontend/src/types/api.ts)
│   ├── db/
│   │   ├── client.py       # Supabase async client singleton
│   │   └── queries/        # raw SQL or supabase-py query helpers
│   └── workers/            # ARQ task definitions
├── tests/
│   ├── conftest.py         # AsyncClient fixture, test DB setup
│   ├── unit/               # service-layer tests (no HTTP)
│   └── integration/        # full endpoint tests via httpx
├── pyproject.toml
└── requirements.txt
```

---

## Environment Variables (`.env`)
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SUPABASE_JWT_SECRET=
REDIS_URL=redis://localhost:6379
SENTRY_DSN=
ENVIRONMENT=development
```

---

## Code Standards

### Python
- All functions that touch I/O must be `async def`
- Type-annotate everything — mypy `--strict` must pass with zero errors
- No bare `except:` — catch specific exceptions, log with loguru, re-raise or return structured error
- Use `Annotated` types for Pydantic field constraints

### API Design
- Version prefix: `/api/v1/`
- All responses return typed Pydantic models — never `dict`
- HTTP status codes must be explicit on each route decorator
- Errors return `{"detail": "...", "code": "SNAKE_CASE_CODE"}` shape

### Services
- Routers handle HTTP concerns only; business logic lives in `services/`
- Services take plain Python types, not Request objects
- DB queries are isolated in `db/queries/` — services call query functions

### Security
- JWT verification via `core/security.py` — every protected route uses `Depends(get_current_user)`
- Input sanitization via Pydantic — no raw string interpolation into queries
- `slowapi` rate limits on all public endpoints

---

## Gate Commands
```bash
# Lint + format check
ruff check app tests

# Type check
mypy app --strict

# Tests with coverage
pytest --tb=short --cov=app --cov-report=term-missing --cov-fail-under=80
```
