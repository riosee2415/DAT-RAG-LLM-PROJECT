# update-work-rules — Harness Self-Optimization

Internal command. /harness Phase 4에서 자동 호출. 사용자 직접 호출 가능.

## 목적
작업 완료 후 work_rule.md 파일들을 갱신해 다음 작업의 토큰 사용을 최소화.

## 실행 절차

### 1. 변경 내역 수집
```
git diff HEAD --name-only
git diff HEAD --stat
```

### 2. 현재 규칙 파일 읽기
- `work_rule.md` (root)
- `frontend/work_rule.md` (변경 있을 때만)
- `backend/work_rule.md` (변경 있을 때만)

### 3. 각 work_rule.md 업데이트 규칙

**FILE MAP 업데이트:**
- 새 파일이 추가됐으면 → 해당 task scope에 1줄 추가
- 파일이 삭제/이동됐으면 → 해당 항목 제거
- 기존에 없던 연관 파일 패턴 발견 시 → 새 scope 행 추가

**LEARNED PATTERNS 업데이트:**
- 이번 작업에서 리뷰 루프가 발생했으면 → 원인 패턴 1줄 추가
- 특정 파일들이 항상 함께 수정됐으면 → co-edit 패턴 1줄 추가
- 테스트 실패 원인이 반복됐으면 → anti-pattern 1줄 추가
- 형식: `[날짜] [패턴 설명] → [권장 대응]`

**SKIP ALWAYS 업데이트:**
- 새로 생긴 무시 대상 디렉토리/파일 발견 시 추가

**Pruning (파일이 80줄 초과 시):**
- LEARNED PATTERNS에서 60일 이상 된 항목 제거
- FILE MAP에서 삭제된 파일 경로 제거
- 중복 항목 병합

### 4. 타임스탬프 갱신
각 파일 첫 줄 `<!-- ... Last: -->` → 현재 날짜/시간으로 교체

### 5. 출력
```
Updated: work_rule.md [+N lines]
Updated: frontend/work_rule.md [+N lines]
Updated: backend/work_rule.md [+N lines]
```
설명 없이 위 3줄만.

## 작성 원칙
- 1항목 = 1줄. 절대 verbose하게 쓰지 않음.
- 테이블 형식 유지 (pipe-delimited).
- work_rule.md는 에이전트를 위한 인덱스, 문서가 아님.
- 각 파일 80줄 이내 유지.
