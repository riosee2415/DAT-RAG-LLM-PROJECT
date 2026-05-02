# init-frontend.ps1
# Next.js frontend full setup: create-next-app → packages → shadcn/ui → Playwright

param([string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent))

$ErrorActionPreference = "Stop"
$fe = Join-Path $ProjectRoot "frontend"

function Step([string]$msg) { Write-Host "`n[FE] $msg" -ForegroundColor Cyan }
function OK  { Write-Host "  ✓" -ForegroundColor Green }
function Skip([string]$why) { Write-Host "  → skip: $why" -ForegroundColor DarkGray }

Set-Location $ProjectRoot

# ── 1. create-next-app ─────────────────────────────────────────────────────────
Step "create-next-app@latest"
if (Test-Path (Join-Path $fe "package.json")) {
    Skip "frontend/package.json already exists"
} else {
    npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git --use-npm
    if ($LASTEXITCODE -ne 0) { Write-Error "create-next-app failed"; exit 1 }
    OK
}

Set-Location $fe

# ── 2. Core runtime dependencies ──────────────────────────────────────────────
Step "core: TanStack Query, Zustand, Zod, RHF, Supabase, nuqs, motion, AI SDK"
npm install @tanstack/react-query @tanstack/react-query-devtools zustand react-hook-form @hookform/resolvers zod @supabase/supabase-js @supabase/ssr nuqs next-safe-action motion ai @ai-sdk/anthropic @vercel/speed-insights @vercel/analytics
if ($LASTEXITCODE -ne 0) { Write-Error "npm install (core) failed"; exit 1 }
OK

# ── 3. Dev dependencies ────────────────────────────────────────────────────────
Step "dev: Vitest, RTL, MSW, bundle-analyzer, openapi-typescript"
npm install -D vitest "@vitejs/plugin-react" "@vitest/coverage-v8" jsdom "@testing-library/react" "@testing-library/user-event" "@testing-library/jest-dom" msw "@next/bundle-analyzer" openapi-typescript
if ($LASTEXITCODE -ne 0) { Write-Error "npm install (dev) failed"; exit 1 }
OK

# ── 4. Playwright ──────────────────────────────────────────────────────────────
Step "Playwright (E2E + PDF export)"
npm install -D playwright
if ($LASTEXITCODE -ne 0) { Write-Error "npm install playwright failed"; exit 1 }
npx playwright install chromium --with-deps
OK

# ── 5. shadcn/ui ──────────────────────────────────────────────────────────────
Step "shadcn/ui init"
npx shadcn@latest init -d -y 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  shadcn init returned non-zero, checking if components.json exists..." -ForegroundColor Yellow
    if (-not (Test-Path "components.json")) { Write-Error "shadcn init failed"; exit 1 }
}
OK

Step "shadcn/ui components"
npx shadcn@latest add button input label textarea form card badge avatar dialog alert-dialog sheet tabs table dropdown-menu toast toaster tooltip separator scroll-area skeleton progress switch checkbox radio-group select -y
OK

Write-Host "`n[FE] Frontend setup complete." -ForegroundColor Green
