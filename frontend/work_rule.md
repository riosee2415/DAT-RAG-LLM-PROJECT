# Frontend Work Rules — Token Optimization Index
<!-- Auto-managed by harness Phase 4. NEVER edit manually. Last: INIT -->

## TOKEN PROTOCOL
- 설명 없이 코드만. "Done." / "Failed: [이유]" 한 줄로 종료.
- backend/, harness_commands/ 절대 참조 금지.
- FILE MAP 외 파일은 묻지 않고 탐색하지 않음.

## SKIP ALWAYS
```
node_modules/  .next/  coverage/  storybook-static/
playwright-report/  test-results/  .turbo/  out/  build/
```

## LOAD ALWAYS
```
frontend/work_rule.md    ← 먼저
frontend/CLAUDE.md
```

## FILE MAP (task → load targets)
| 작업 유형 | 로드 대상 파일 |
|-----------|----------------|
| 신규 페이지/라우트 | src/app/, src/components/features/ |
| UI 컴포넌트 | src/components/ui/ (shadcn), src/components/features/ |
| 인증 / 세션 | src/lib/supabase/, src/middleware.ts |
| API 호출 (백엔드) | src/lib/api/, src/types/api.ts |
| 폼 | src/schemas/, RHF + Zod 관련 컴포넌트 |
| 전역 상태 | src/store/ |
| 서버 액션 | src/app/**/actions.ts, next-safe-action |
| 테스트 | *.test.tsx, tests/unit/, tests/e2e/ |
| 스타일/디자인 시스템 | src/styles/, tailwind.config.ts, shadcn 컴포넌트 |

## CONTRACT TYPES
```
src/types/api.ts   ← FE-BE 공유 타입. 항상 먼저 확인.
```

## LEARNED PATTERNS
<!-- harness가 각 작업 후 여기에 1줄씩 추가. -->
