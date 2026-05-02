# Work Rules — Root Token Optimization Index
<!-- Auto-managed by harness Phase 4. NEVER edit manually. Last: INIT -->

## TOKEN PROTOCOL (최우선 규칙)
- 설명 금지. 코드·변경 결과만 출력. 마지막에 "Done." 또는 "Failed: [이유]" 한 줄만.
- 작업 시작 전: work_rule.md 먼저, 그 다음 CLAUDE.md, 그 다음 task-relevant 파일만.
- 디렉토리 전체 스캔 금지. 아래 FILE MAP 기준으로만 탐색.
- 같은 내용 반복 로드 금지. 이미 로드한 파일 재확인 금지.

## SKIP ALWAYS (절대 로드 금지)
```
harness_commands/  test-reports/  .test-results/
node_modules/      .next/         .venv/
__pycache__/       *.pyc          .pytest_cache/
.ruff_cache/       .mypy_cache/   coverage/
storybook-static/  playwright-report/
```

## LOAD ALWAYS (모든 작업 공통)
```
work_rule.md        ← 이 파일 (먼저 읽음)
CLAUDE.md           ← 루트 오케스트레이션 규칙
```

## FILE MAP (task scope → load targets)
| 작업 유형 | 로드 대상 |
|-----------|-----------|
| 전체 기획/설계 | CLAUDE.md, work_rule.md |
| FE + BE 모두 | frontend/CLAUDE.md, frontend/work_rule.md, backend/CLAUDE.md, backend/work_rule.md |
| 프론트만 | frontend/CLAUDE.md, frontend/work_rule.md |
| 백엔드만 | backend/CLAUDE.md, backend/work_rule.md |
| 계약 정의 | frontend/src/types/api.ts, backend/app/schemas/api.py |
| 환경/설정 | .gitignore, .mcp.json (있을 경우) |

## LEARNED PATTERNS
<!-- harness가 각 작업 후 여기에 1줄씩 추가. 오래된 항목은 자동 pruning. -->
