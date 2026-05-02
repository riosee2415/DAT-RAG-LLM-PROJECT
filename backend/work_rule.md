# Backend Work Rules — Token Optimization Index
<!-- Auto-managed by harness Phase 4. NEVER edit manually. Last: INIT -->

## TOKEN PROTOCOL
- 설명 없이 코드만. "Done." / "Failed: [이유]" 한 줄로 종료.
- frontend/, harness_commands/ 절대 참조 금지.
- FILE MAP 외 파일은 묻지 않고 탐색하지 않음.

## SKIP ALWAYS
```
.venv/  __pycache__/  *.pyc  .pytest_cache/
.ruff_cache/  .mypy_cache/  dist/  *.egg-info/
htmlcov/  .coverage  alembic/versions/*.pyc
```

## LOAD ALWAYS
```
backend/work_rule.md    ← 먼저
backend/CLAUDE.md
```

## FILE MAP (task → load targets)
| 작업 유형 | 로드 대상 파일 |
|-----------|----------------|
| 신규 엔드포인트 | app/routers/, app/schemas/, app/services/ |
| 인증 / JWT | app/core/security.py, app/core/dependencies.py |
| DB 쿼리 / Supabase | app/db/client.py, app/db/queries/ |
| 설정 / 환경변수 | app/core/config.py |
| 백그라운드 태스크 | app/workers/ |
| 미들웨어 / 공통 | app/main.py, app/core/ |
| 테스트 | tests/conftest.py, tests/unit/, tests/integration/ |
| 스키마 (공유 계약) | app/schemas/api.py |

## CONTRACT SCHEMAS
```
app/schemas/api.py   ← FE-BE 공유 Pydantic 모델. 항상 먼저 확인.
```

## LEARNED PATTERNS
<!-- harness가 각 작업 후 여기에 1줄씩 추가. -->
