# Recommended Skills, Tools & MCP Setup Guide

> 이 문서는 "지금 당장 설치" 가이드가 아닙니다.
> 어떤 도구가 왜 필요한지, 어떻게 세팅하는지 판단 근거를 정리한 레퍼런스입니다.
> 실제 적용 시점은 프로젝트 초기 세팅 단계에서 결정하세요.

---

## FRONTEND — Next.js + TypeScript

### ── A. UI & 디자인 시스템

#### 1. shadcn/ui ★★★ (필수)
**Why:** 2024-2025 프론트엔드 생태계의 사실상 표준. Radix UI 접근성 프리미티브 위에 Tailwind로 스타일링된 컴포넌트 모음. "설치"하는 게 아니라 소스 코드로 복사해와서 완전한 커스터마이징이 가능. v0.dev(아래)와 직접 연동.
**Setup:**
```bash
npx shadcn@latest init
npx shadcn@latest add button input form dialog table
```
컴포넌트는 `src/components/ui/`에 소스로 복사됨. 직접 수정하지 말고 래핑해서 사용.

#### 2. Radix UI Primitives ★★★
**Why:** shadcn/ui의 기반. Dialog, Popover, Select, Toast 등 완전한 접근성(ARIA, keyboard nav)을 보장하는 비스타일 컴포넌트. shadcn을 쓰면 간접적으로 이미 사용중이지만, 커스텀 컴포넌트를 만들 때 직접 필요.
**Setup:** `npm install @radix-ui/react-dialog @radix-ui/react-popover` (필요한 것만 추가)

#### 3. Lucide React ★★
**Why:** shadcn/ui의 공식 아이콘 라이브러리. 트리-쉐이킹 완벽 지원. 5000+ 아이콘.
**Setup:** `npm install lucide-react` (shadcn init 시 자동 설치됨)

#### 4. Motion (Framer Motion v11+) ★★
**Why:** 선언적 애니메이션. Next.js App Router와 SSR 호환. 페이지 전환, 마이크로인터랙션, 레이아웃 애니메이션. 번들 크기 최적화된 v11부터 패키지 이름이 `motion`으로 변경.
**Setup:**
```bash
npm install motion
```
```tsx
import { motion } from "motion/react"
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} />
```

#### 5. Recharts / Tremor ★★
**Why:** 데이터 시각화가 필요한 대시보드에서 필수. Recharts는 D3 기반 범용 차트. Tremor는 Tailwind 네이티브 대시보드 컴포넌트 모음(shadcn과 디자인 철학 일치).
**Setup:** `npm install recharts` 또는 `npm install @tremor/react`

---

### ── B. 상태 관리

#### 6. TanStack Query v5 ★★★ (필수)
**Why:** 서버 상태(Supabase 데이터)의 fetching, caching, background revalidation, optimistic update를 처리. `useQuery` 하나로 로딩·에러·데이터 상태를 선언적으로 관리. Next.js 서버 컴포넌트에서는 prefetch로 연동.
**Setup:**
```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
```
`app/providers.tsx`에 `QueryClientProvider` 래핑 → root layout에 주입.

#### 7. Zustand ★★★ (필수)
**Why:** Redux 없이 전역 클라이언트 상태 관리. boilerplate 제로, TypeScript 친화적, devtools 지원. TanStack Query가 서버 상태를, Zustand가 UI/클라이언트 상태를 담당하면 역할이 명확히 분리됨.
**Setup:**
```bash
npm install zustand
```
```ts
// store/use-auth-store.ts
import { create } from 'zustand'
interface AuthStore { user: User | null; setUser: (u: User | null) => void }
export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}))
```

#### 8. nuqs ★★
**Why:** Next.js App Router에서 URL 쿼리 파라미터를 React 상태처럼 다루는 라이브러리. 필터, 정렬, 페이지네이션 상태를 URL에 동기화해 공유/북마크/뒤로가기가 자연스럽게 동작.
**Setup:** `npm install nuqs`

---

### ── C. 폼 & 유효성 검사

#### 9. React Hook Form ★★★ (필수)
**Why:** 리렌더링 최소화, 비제어 컴포넌트 기반, shadcn/ui Form 컴포넌트와 공식 통합.
**Setup:** `npm install react-hook-form`

#### 10. Zod ★★★ (필수)
**Why:** 런타임 스키마 검증 + TypeScript 타입 자동 추론. React Hook Form의 `zodResolver`로 폼 유효성 검사. API 응답 파싱에도 사용해 Supabase 스키마 변경을 즉시 감지.
**Setup:** `npm install zod @hookform/resolvers`

---

### ── D. 인증 & 보안

#### 11. @supabase/ssr ★★★ (필수)
**Why:** Next.js App Router에서 Supabase 인증 시 반드시 사용. 쿠키 기반 세션 관리. `@supabase/supabase-js`만 쓰면 서버 컴포넌트에서 인증 상태를 읽을 수 없음.
**Setup:**
```bash
npm install @supabase/supabase-js @supabase/ssr
```
`middleware.ts`에서 세션 갱신, `lib/supabase/server.ts`에서 서버 클라이언트 생성.

#### 12. next-safe-action ★★
**Why:** Server Actions에 Zod 스키마 검증 + 타입 안전성 + 에러 처리를 자동으로 추가. `useActionState`보다 훨씬 깔끔한 DX.
**Setup:** `npm install next-safe-action`

---

### ── E. API 타입 안전성

#### 13. openapi-typescript ★★
**Why:** 백엔드 FastAPI가 자동으로 생성하는 OpenAPI spec(`/openapi.json`)으로부터 TypeScript 타입을 자동 생성. 백엔드 스키마 변경 시 프론트엔드 타입도 자동으로 동기화됨. 수동으로 타입을 맞출 필요가 없어짐.
**Setup:**
```bash
npm install -D openapi-typescript
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts
```
CI에서 자동 재생성하도록 스크립트 추가.

---

### ── F. 테스팅

#### 14. Vitest ★★★ (필수, Jest 대신)
**Why:** Jest보다 10-20배 빠름. Next.js의 ESM 모듈을 별도 설정 없이 처리. Vite 생태계와 통합. `jsdom` 환경에서 React 컴포넌트 테스트 가능.
**Setup:**
```bash
npm install -D vitest @vitejs/plugin-react jsdom @vitest/coverage-v8
```
`vitest.config.ts`에 `environment: 'jsdom'` 설정.

#### 15. React Testing Library ★★★ (필수)
**Why:** 컴포넌트를 사용자 관점에서 테스트. 구현 세부사항이 아닌 DOM 동작을 검증. Vitest와 조합.
**Setup:** `npm install -D @testing-library/react @testing-library/user-event @testing-library/jest-dom`

#### 16. Playwright ★★★ (필수)
**Why:** 실제 브라우저에서 E2E 테스트. 인증 플로우, 라우팅, 폼 제출, API 응답 통합 시나리오를 검증. CI headless 실행 가능. Playwright MCP(아래)와 연동하면 Claude가 직접 브라우저를 조작해 테스트 시나리오를 검증할 수 있음.
**Setup:**
```bash
npm init playwright@latest
```

#### 17. MSW v2 (Mock Service Worker) ★★
**Why:** 네트워크 요청을 서비스 워커 수준에서 인터셉트해 모킹. Vitest와 Storybook 양쪽에서 동일한 mock handler를 재사용. 백엔드 없이 프론트엔드 개발 가능.
**Setup:**
```bash
npm install -D msw
npx msw init public/
```

#### 18. Storybook ★★
**Why:** 컴포넌트를 앱 없이 독립적으로 개발·문서화. MSW와 통합해 API 모킹 상태로 Story 작성. sub-agent가 컴포넌트 구현 시 Story 파일도 함께 생성하도록 강제하면 UI 품질 향상.
**Setup:** `npx storybook@latest init`

---

### ── G. DX & 코드 품질

#### 19. ESLint (next/core-web-vitals) ★★★
**Why:** Next.js 전용 규칙 포함. `@typescript-eslint`로 TypeScript 타입 기반 lint. 하네스 Gate 1에서 `--max-warnings 0`으로 실행.
**Setup:** `npx eslint --init` (Next.js 프로젝트 생성 시 자동 설정됨)

#### 20. @next/bundle-analyzer ★★
**Why:** 번들 크기를 시각화. 예상치 못한 거대 패키지를 조기에 발견. 성능 최적화에 필수.
**Setup:**
```bash
npm install -D @next/bundle-analyzer
```
`next.config.ts`:
```ts
const withBundleAnalyzer = require('@next/bundle-analyzer')({ enabled: process.env.ANALYZE === 'true' })
```

---

### ── H. AI 보조 개발 도구 ★★★ (핵심!)

#### 21. v0.dev by Vercel ★★★
**Why:** 텍스트 프롬프트 또는 스크린샷으로 shadcn/ui 기반 React 컴포넌트를 생성. 출력 코드가 이 프로젝트 스택(Next.js + shadcn + Tailwind)과 100% 호환. 디자인 작업을 Claude Code 하네스 안으로 흡수할 수 있는 가장 효과적인 방법.
**사용법:**
- v0.dev에서 UI를 생성 → 코드 복사 → 하네스를 통해 프로젝트에 통합
- 또는 `/spec <기능>` 커맨드에서 v0.dev 프롬프트를 같이 생성하도록 harness에 추가 가능
**URL:** https://v0.dev

#### 22. Vercel AI SDK (`ai` 패키지) ★★★
**Why:** 앱 자체에 AI 기능(챗봇, 스트리밍 응답, 구조화된 출력)을 추가할 때 필수. Anthropic Claude, OpenAI 등 멀티 프로바이더 지원. Next.js App Router의 스트리밍과 완벽 통합.
**Setup:**
```bash
npm install ai @ai-sdk/anthropic
```
Route Handler에서:
```ts
import { streamText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
export async function POST(req: Request) {
  const { messages } = await req.json()
  const result = streamText({ model: anthropic('claude-opus-4-7'), messages })
  return result.toDataStreamResponse()
}
```

#### 23. @vercel/speed-insights + @vercel/analytics ★★
**Why:** Web Vitals(LCP, CLS, INP) 실시간 추적. Core Web Vitals가 SEO와 직결. 코드 1줄로 설치.
**Setup:** `npm install @vercel/speed-insights @vercel/analytics` → layout.tsx에 `<SpeedInsights />` `<Analytics />` 추가.

---

## BACKEND — Python 3.11 + FastAPI

### ── A. 데이터 & ORM

#### 1. SQLModel ★★
**Why:** FastAPI 창시자(Sebastián Ramírez)가 만든 라이브러리. SQLAlchemy ORM + Pydantic v2를 통합. DB 모델과 API 스키마를 하나의 클래스로 정의 가능. 타입 중복 제거.
**Setup:** `pip install sqlmodel`

#### 2. Alembic ★★
**Why:** Supabase가 DB를 관리하더라도 마이그레이션 히스토리를 코드로 관리하면 협업과 롤백이 훨씬 안전. SQLModel과 자동 연동.
**Setup:** `pip install alembic` → `alembic init alembic`

---

### ── B. 인증 & 보안

#### 3. python-jose[cryptography] ★★★
**Why:** JWT 생성·검증. Supabase JWT 토큰 검증에 필수. RS256/HS256 모두 지원.
**Setup:** `pip install python-jose[cryptography]`

#### 4. passlib[bcrypt] ★★★
**Why:** 패스워드 해싱의 사실상 표준. bcrypt 알고리즘으로 timing attack 방어.
**Setup:** `pip install passlib[bcrypt]`

#### 5. slowapi ★★
**Why:** FastAPI용 rate limiting. Redis 또는 메모리 기반. 공개 엔드포인트에 필수.
**Setup:**
```bash
pip install slowapi
```
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/public")
@limiter.limit("10/minute")
async def public_endpoint(request: Request): ...
```

#### 6. bandit ★★
**Why:** 파이썬 코드의 보안 취약점 정적 분석. SQL injection, hardcoded secrets, unsafe deserialization 탐지. CI Gate에서 실행.
**Setup:** `pip install bandit` → `bandit -r app -ll`

---

### ── C. 백그라운드 작업

#### 7. ARQ ★★★
**Why:** Redis 기반 비동기 태스크 큐. Celery보다 훨씬 가볍고 Python async-native. FastAPI와 자연스럽게 통합. 이메일 발송, 데이터 처리, 알림 등 백그라운드 작업에 사용.
**Setup:**
```bash
pip install arq
```
Worker:
```python
async def send_email(ctx, to: str, subject: str): ...
class WorkerSettings:
    functions = [send_email]
    redis_settings = RedisSettings()
```

#### 8. APScheduler ★★
**Why:** cron-style 스케줄 작업. ARQ 불필요한 경량 주기 작업(DB 정리, 통계 집계 등)에 적합.
**Setup:** `pip install apscheduler`

---

### ── D. 관찰 가능성 & 모니터링

#### 9. Loguru ★★★
**Why:** Python 표준 logging을 완전히 대체. 구조화된 JSON 로그, 파일 rotation, 컬러 콘솔 출력. 설정 코드가 1줄.
**Setup:**
```bash
pip install loguru
```
```python
from loguru import logger
logger.add("logs/app.log", rotation="10 MB", serialize=True)
logger.info("Request received", path=request.url.path, user_id=user.id)
```

#### 10. sentry-sdk[fastapi] ★★★
**Why:** 프로덕션 에러 추적. 예외 발생 시 스택 트레이스, 요청 컨텍스트, 사용자 정보를 자동으로 캡처. FastAPI 전용 인티그레이션 제공.
**Setup:**
```bash
pip install "sentry-sdk[fastapi]"
```
```python
import sentry_sdk
sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
```

#### 11. prometheus-fastapi-instrumentator ★★
**Why:** FastAPI에 `/metrics` 엔드포인트를 자동으로 추가. 요청 수, 응답 시간, 에러율 등을 Prometheus/Grafana로 모니터링.
**Setup:**
```bash
pip install prometheus-fastapi-instrumentator
```
```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

---

### ── E. 테스팅

#### 12. pytest + pytest-asyncio ★★★ (필수)
**Why:** FastAPI async 엔드포인트 테스트에 필수. `asyncio_mode = "auto"` 설정으로 모든 테스트 함수에 `async def` 사용 가능.
**Setup:** `pip install pytest pytest-asyncio`

#### 13. httpx + ASGITransport ★★★ (필수)
**Why:** 실제 HTTP 요청 없이 FastAPI 앱 인스턴스에 직접 요청. 가장 신뢰도 높은 통합 테스트 방식.
**Setup:** `pip install httpx`
```python
# conftest.py
@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
```

#### 14. factory-boy + Faker ★★
**Why:** 테스트 데이터 생성 자동화. `UserFactory.create()` 한 줄로 현실적인 테스트 데이터 생성. 하드코딩된 픽스처 제거.
**Setup:** `pip install factory-boy faker`

#### 15. pytest-cov ★★★ (필수)
**Why:** 코드 커버리지 측정. 하네스 Gate 3에서 `--cov-fail-under=80`으로 80% 미달 시 커밋 차단.
**Setup:** `pip install pytest-cov`

#### 16. respx ★★
**Why:** `httpx` 기반 HTTP 호출 모킹. 외부 API(Supabase REST, 서드파티 서비스) 호출을 테스트 환경에서 인터셉트.
**Setup:** `pip install respx`

---

### ── F. DX & 코드 품질

#### 17. Ruff ★★★ (필수)
**Why:** flake8 + black + isort + pyupgrade를 단일 툴로 대체. Rust 기반으로 10-100배 빠름. `ruff check` (lint) + `ruff format` (format) 두 명령으로 전부 처리.
**Setup:**
```bash
pip install ruff
```
`pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "W", "F", "B", "I", "UP", "S"]  # security rules 포함
```

#### 18. mypy (strict) ★★★ (필수)
**Why:** 정적 타입 검사. `--strict` 모드는 모든 함수에 타입 어노테이션을 강제. 런타임 전에 타입 버그 차단.
**Setup:**
```bash
pip install mypy
```
`pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]
```

#### 19. pydantic-settings ★★★ (필수)
**Why:** `.env` 파일에서 환경 변수를 읽어 Pydantic 모델로 타입 검증. 잘못된 환경 변수 설정 시 앱 시작 단계에서 명확한 에러.
**Setup:** `pip install pydantic-settings`
```python
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    class Config: env_file = ".env"
settings = Settings()
```

#### 20. pre-commit ★★
**Why:** git commit 시 자동으로 ruff, mypy, bandit 실행. 나쁜 코드가 저장소에 들어오는 것을 방지.
**Setup:**
```bash
pip install pre-commit
```
`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks: [{ id: ruff, args: [--fix] }, { id: ruff-format }]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks: [{ id: mypy, args: [--strict] }]
```

---

## 테스트 보고 시스템 (Test Report System)

> 하네스 파이프라인에 통합됨. 테스트 실행 후 자동으로 HTML 리포트 생성 + PDF 변환.
> 파일명: `{XX테스트진행_YYYYMMDD.html/.pdf}` → `test-reports/` 디렉토리에 저장.

---

### 아키텍처 개요
```
Tests 실행 (JSON 출력)
  ↓
generate-test-report.py (Python)
  ↓ Chart.js 시각화 포함 HTML
html-to-pdf.js (Playwright)
  ↓
test-reports/프론트엔드테스트진행_YYYYMMDD.{html,pdf}
test-reports/백엔드테스트진행_YYYYMMDD.{html,pdf}
```

---

### 리포트 포함 데이터
| 섹션 | 내용 |
|------|------|
| 요약 카드 | 전체/통과/실패/건너뜀 수, 성공률, 평균 커버리지 |
| 도넛 차트 | 통과/실패/건너뜀 비율 시각화 |
| 가로 바 차트 | 파일별 커버리지 현황 (하위 12개 파일 강조) |
| 실패 테스트 | 오류 메시지 + 스택 트레이스 전체 표시 |
| 전체 테스트 표 | 이름/파일/시간, 실시간 검색 필터 내장 |

---

### 필요 도구 (추가 설치 항목)

#### 1. pytest-json-report ★★★ (백엔드 필수)
**Why:** pytest 결과를 구조화된 JSON으로 출력. `generate-test-report.py`가 이 JSON을 파싱해 리포트 생성.
**Setup:**
```bash
pip install pytest-json-report
```
사용법: `pytest --json-report --json-report-file=.test-results/be-test.json`

#### 2. pytest-cov (JSON 출력) ★★★ (백엔드 필수)
**Why:** 커버리지를 JSON으로 출력해 리포트에 파일별 커버리지 차트를 생성.
**Setup:**
```bash
pip install pytest-cov
```
사용법: `pytest --cov=app --cov-report=json:.test-results/be-coverage.json`

#### 3. Vitest JSON Reporter ★★★ (프론트엔드 필수)
**Why:** vitest 결과를 JSON으로 출력. 별도 설치 불필요 — vitest에 내장.
**Setup:** 추가 패키지 없음. vitest에 내장된 기능.
```bash
npx vitest run --reporter=json --outputFile=.test-results/fe-test.json \
  --coverage --coverage.reporter=json --coverage.reportsDirectory=.test-results/fe-coverage
```

#### 4. Jinja2 (선택 — 리포트 커스터마이징 시)
**Why:** 현재 리포트는 Python f-string으로 생성됨. 리포트 템플릿을 독립적으로 관리하고 싶을 때 Jinja2로 교체 권장.
**Setup:** `pip install jinja2`

#### 5. Playwright (PDF 변환용) — 프론트엔드에 이미 설치됨
**Why:** HTML → PDF 변환. Chromium headless로 정확한 렌더링. 이미 E2E 테스팅용으로 프론트엔드에 설치됨.
**Note:** `html-to-pdf.js`가 `frontend/node_modules/playwright`를 자동으로 찾음.
별도 설치 불필요 (프론트엔드 Playwright 설치 시 자동으로 사용 가능).

#### 6. Chart.js (CDN, 설치 불필요)
**Why:** 리포트 HTML에 CDN으로 인라인. 결과 분포 도넛 차트 + 커버리지 바 차트.
**Note:** 오프라인 환경에서 PDF가 필요한 경우 CDN 대신 로컬 번들로 교체 필요.
```bash
# 로컬 번들 대체 시:
npm install -D chart.js
# generate-test-report.py의 CDN URL을 로컬 경로로 교체
```

---

### 파일 명명 규칙
| 레이어 | 파일명 |
|--------|--------|
| 프론트엔드 | `프론트엔드테스트진행_YYYYMMDD.html/.pdf` |
| 백엔드 | `백엔드테스트진행_YYYYMMDD.html/.pdf` |
| 통합(미래) | `통합테스트진행_YYYYMMDD.html/.pdf` |

---

### 리포트 생성 시스템 구성 파일
| 파일 | 역할 |
|------|------|
| `scripts/generate-test-report.py` | JSON → HTML 변환기 (Chart.js 시각화 포함) |
| `scripts/html-to-pdf.js` | HTML → PDF 변환기 (Playwright) |
| `.claude/hooks/tdd-and-push.ps1` | 파이프라인 오케스트레이터 (게이트 + 리포트 + git) |
| `test-reports/` | 생성된 HTML/PDF 저장 (gitignore됨) |
| `.test-results/` | 중간 JSON 파일 (gitignore됨) |

---

## MCP SERVERS

> Claude Code에서 직접 도구처럼 사용할 수 있는 서버들.
> 설정: 프로젝트 루트 `.mcp.json` 또는 `~/.claude/settings.json`의 `mcpServers` 키.

---

### 🔴 Critical (반드시 설정)

#### 1. Supabase MCP
**Why:** Claude가 실제 DB 스키마를 보고 코드를 작성. 존재하지 않는 컬럼·테이블을 사용하는 코드 생성(환각) 방지. 마이그레이션 실행, 데이터 조회, 스키마 변경 직접 수행.
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest",
               "--supabase-url", "<SUPABASE_URL>",
               "--service-role-key", "<SERVICE_ROLE_KEY>"]
    }
  }
}
```

#### 2. Context7 MCP
**Why:** Claude의 학습 데이터 컷오프 이후 업데이트된 라이브러리 문서를 실시간으로 제공. Next.js 15, FastAPI 0.115, shadcn/ui 최신 API를 정확하게 사용. 코드 생성 품질 크게 향상.
```json
"context7": {
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp@latest"]
}
```

#### 3. Playwright MCP
**Why:** Claude가 실제 브라우저를 열어 UI를 조작하고 시각적으로 검증. 하네스 완료 후 Claude가 직접 "이 기능이 실제로 동작하는지" 확인 가능. 가장 강력한 QA 자동화.
```json
"playwright": {
  "command": "npx",
  "args": ["-y", "@playwright/mcp@latest"]
}
```

---

### 🟡 Important (강력 권장)

#### 4. GitHub MCP
**Why:** Claude가 PR 생성, 이슈 등록, 코드 리뷰 코멘트 게시, CI 상태 확인을 직접 수행. 하네스의 commit/push 이후 자동으로 PR을 만들고 리뷰어를 지정하는 워크플로우 구성 가능.
```json
"github": {
  "command": "npx",
  "args": ["-y", "@github/mcp-server@latest"],
  "env": { "GITHUB_TOKEN": "<GITHUB_PAT>" }
}
```

#### 5. Postgres MCP (Direct)
**Why:** Supabase MCP보다 로우레벨 SQL 쿼리 실행 필요 시. 복잡한 분석 쿼리, 인덱스 최적화, EXPLAIN ANALYZE 등.
```json
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "<POSTGRES_URL>"]
}
```

#### 6. Brave Search MCP
**Why:** Claude가 에러 메시지, 라이브러리 이슈, 최신 해결책을 직접 검색. 디버깅 시간 단축.
```json
"brave-search": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": { "BRAVE_API_KEY": "<BRAVE_API_KEY>" }
}
```

---

### 🟢 Situational (상황에 따라)

#### 7. Sentry MCP
**Why:** Claude가 프로덕션 에러를 직접 조회. "사용자가 에러 보고를 했다"고 하면 Claude가 Sentry에서 스택 트레이스를 읽고 바로 수정 코드를 제안.
```json
"sentry": {
  "command": "npx",
  "args": ["-y", "mcp-server-sentry@latest"],
  "env": { "SENTRY_AUTH_TOKEN": "<TOKEN>", "SENTRY_ORG": "<ORG>" }
}
```

#### 8. Vercel MCP
**Why:** 배포 트리거, 배포 로그 확인, 환경 변수 관리를 Claude가 직접 수행. 하네스에 `/deploy` 커맨드 추가 시 활용.
```json
"vercel": {
  "command": "npx",
  "args": ["-y", "@vercel/mcp-server@latest"],
  "env": { "VERCEL_TOKEN": "<TOKEN>" }
}
```

#### 9. Linear MCP
**Why:** 이슈 트래킹. 코드 리뷰에서 버그 발견 시 Claude가 자동으로 Linear 이슈를 생성.
```json
"linear": {
  "command": "npx",
  "args": ["-y", "@linear/mcp-server@latest"],
  "env": { "LINEAR_API_KEY": "<KEY>" }
}
```

---

## CLAUDE CODE CUSTOM COMMANDS (Skills)

> `.claude/commands/` 아래 마크다운 파일로 정의.

| 커맨드 | 파일 | 용도 | 상태 |
|--------|------|------|------|
| `/harness <task>` | `commands/harness.md` | 전체 FE+BE 개발 오케스트레이션 | ✅ 완성 |
| `/spec <feature>` | `commands/spec.md` | API 계약 + 기술 스펙 문서 생성 (Phase 0 독립 실행) | 추가 권장 |
| `/review [path]` | `commands/review.md` | 특정 파일/디렉토리 코드 리뷰 (리뷰 체크리스트 기반) | 추가 권장 |
| `/migrate <desc>` | `commands/migrate.md` | Supabase 마이그레이션 생성 + 적용 + rollback 스크립트 | 추가 권장 |
| `/debug <issue>` | `commands/debug.md` | 체계적 디버깅 세션 (5-why 방법론) | 추가 권장 |
| `/security` | `commands/security.md` | FE+BE 전체 보안 감사 (OWASP Top 10 기준) | 추가 권장 |
| `/perf` | `commands/perf.md` | 성능 프로파일링 (Lighthouse + backend profiling) | 필요 시 |
| `/deploy [env]` | `commands/deploy.md` | Vercel 배포 트리거 + 헬스체크 | 필요 시 |

---

## 설치 우선순위 요약

| 우선순위 | Frontend | Backend |
|---------|----------|---------|
| 즉시 | shadcn/ui, TanStack Query, Zustand, Zod, React Hook Form, @supabase/ssr, Vitest, RTL | FastAPI, Pydantic v2, Ruff, mypy, pytest-asyncio, httpx, loguru, pydantic-settings |
| 초기 2주 | Motion, Playwright, MSW, Storybook, next-safe-action, openapi-typescript | python-jose, passlib, slowapi, sentry-sdk, ARQ, factory-boy, pytest-cov |
| 필요 시 | Recharts/Tremor, nuqs, bundle-analyzer, Vercel AI SDK | SQLModel, Alembic, bandit, APScheduler, prometheus-instrumentator |
| MCP 즉시 | Supabase MCP, Context7 MCP, Playwright MCP | Supabase MCP, Context7 MCP |
| MCP 이후 | GitHub MCP, Brave Search MCP | GitHub MCP, Postgres MCP, Sentry MCP |
