# /claude_init — Full Project Initialization

Zero questions. Fully autonomous. Execute every phase sequentially.
If a step fails, report the error and stop — do not skip.

---

## Phase 0 — Prerequisites Check

Run each check. If any fail, stop and report exactly which is missing.

```powershell
node --version          # must be 18+
npm --version
python --version        # must be 3.11+
git --version
```

---

## Phase 1 — Git Init

```powershell
git init
git checkout -b main 2>$null; if ($LASTEXITCODE -ne 0) { Write-Host "main branch already exists" }
```

---

## Phase 2 — Frontend Setup (runs ~5 min)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\init-frontend.ps1
```

---

## Phase 3 — Backend Setup (runs ~3 min)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\init-backend.ps1
```

---

## Phase 4 — Create Config Files

Use the Write tool to create each file with exactly the content below.

### 4-1. `frontend/vitest.config.ts`
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: '../.test-results/fe-coverage',
      exclude: ['node_modules/', '.next/', 'src/components/ui/', '*.config.*'],
    },
  },
  resolve: {
    alias: { '@': resolve(__dirname, './src') },
  },
})
```

### 4-2. `frontend/src/test/setup.ts`
```typescript
import '@testing-library/jest-dom'
```

### 4-3. `frontend/playwright.config.ts`
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['html'], ['json', { outputFile: '../.test-results/playwright.json' }]],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### 4-4. `frontend/.env.local.example`
```
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4-5. `frontend/src/types/api.ts`
```typescript
// Shared API contract types — kept in sync with backend/app/schemas/api.py
// Auto-regenerate: npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts

export interface HealthResponse {
  status: string
}
```

### 4-6. `frontend/src/lib/supabase/client.ts`
```typescript
import { createBrowserClient } from '@supabase/ssr'

export const createClient = () =>
  createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
```

### 4-7. `frontend/src/lib/supabase/server.ts`
```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export const createClient = async () => {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        },
      },
    }
  )
}
```

### 4-8. `frontend/src/middleware.ts`  
(Note: create this at `frontend/src/middleware.ts`)
```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  await supabase.auth.getUser()
  return supabaseResponse
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

### 4-9. `frontend/src/app/providers.tsx`
```typescript
'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60 * 1000 } },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### 4-10. `backend/pyproject.toml`
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "B", "I", "UP", "S", "N", "ANN"]
ignore = ["ANN101", "ANN102"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "ANN"]

[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["tests.*", "alembic.*"]
disallow_untyped_defs = false
ignore_errors = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "app/main.py"]

[tool.coverage.report]
fail_under = 80
```

### 4-11. `backend/app/__init__.py`
```python
```
(empty file)

### 4-12. `backend/app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

### 4-13. `backend/app/core/__init__.py`
```python
```
(empty file)

### 4-14. `backend/app/core/config.py`
```python
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "SB Seminar API"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
```

### 4-15. `backend/app/core/dependencies.py`
```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, str]:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return {"user_id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e
```

### 4-16. `backend/app/routers/__init__.py`
```python
```
(empty)

### 4-17. `backend/app/services/__init__.py`
```python
```
(empty)

### 4-18. `backend/app/schemas/__init__.py`
```python
```
(empty)

### 4-19. `backend/app/schemas/api.py`
```python
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
```

### 4-20. `backend/app/db/__init__.py`
```python
```
(empty)

### 4-21. `backend/app/db/client.py`
```python
from supabase import AsyncClient, acreate_client

from app.core.config import settings

_client: AsyncClient | None = None


async def get_supabase() -> AsyncClient:
    global _client
    if _client is None:
        _client = await acreate_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _client
```

### 4-22. `backend/app/workers/__init__.py`
```python
```
(empty)

### 4-23. `backend/tests/__init__.py`
```python
```
(empty)

### 4-24. `backend/tests/conftest.py`
```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
```

### 4-25. `backend/.env.example`
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### 4-26. `backend/tests/test_health.py`
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

---

## Phase 5 — MCP Configuration

Write `.mcp.json` at project root:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

Note in output: Supabase MCP, GitHub MCP, Brave Search MCP require API keys.
Add them to `.mcp.json` following `deco_skill.md` MCP section when keys are available.

---

## Phase 6 — Git Branches & Initial Commit

```powershell
git add -A
git commit -m "chore: initial project setup via /claude_init"
git checkout -b web
git checkout -b ai
git checkout main
```

Output:
```
Branches created: main (default), web (frontend), ai (backend)
```

---

## Phase 7 — Verification

Run the following quick checks:

```powershell
# Frontend type check
Set-Location frontend
npx tsc --noEmit
Set-Location ..

# Backend syntax check
$pip = "backend\.venv\Scripts\pip.exe"
& "backend\.venv\Scripts\python.exe" -c "from app.main import app; print('OK')"
```

---

## Phase 8 — Summary Output

Print ONLY this block. No other text.

```
╔══════════════════════════════════════════════════════╗
║            /claude_init COMPLETE                     ║
╚══════════════════════════════════════════════════════╝

Frontend   : frontend/          (Next.js + shadcn/ui + Vitest + Playwright)
Backend    : backend/           (FastAPI + .venv + pytest)
MCP        : .mcp.json          (Context7 + Playwright — keys needed for others)
Branches   : main | web | ai

Next steps:
  1. Copy frontend/.env.local.example → frontend/.env.local  (add Supabase keys)
  2. Copy backend/.env.example        → backend/.env          (add Supabase keys)
  3. Add API keys to .mcp.json        (see deco_skill.md MCP section)
  4. Run: /harness <your first task>
```
