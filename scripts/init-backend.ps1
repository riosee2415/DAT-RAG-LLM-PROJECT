# init-backend.ps1
# FastAPI backend full setup: venv → pip install → pyproject.toml

param([string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent))

$ErrorActionPreference = "Stop"
$be      = Join-Path $ProjectRoot "backend"
$venv    = Join-Path $be ".venv"
$pip     = Join-Path $venv "Scripts\pip.exe"
$python  = Join-Path $venv "Scripts\python.exe"

function Step([string]$msg) { Write-Host "`n[BE] $msg" -ForegroundColor Cyan }
function OK  { Write-Host "  ✓" -ForegroundColor Green }
function Skip([string]$why) { Write-Host "  → skip: $why" -ForegroundColor DarkGray }

Set-Location $be

# ── 0. Python check ────────────────────────────────────────────────────────────
Step "Python version check"
$v = python --version 2>&1
Write-Host "  $v" -ForegroundColor DarkGray

# ── 1. Virtual environment ─────────────────────────────────────────────────────
Step "Virtual environment (.venv)"
if (Test-Path $venv) {
    Skip ".venv already exists"
} else {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Error "venv creation failed"; exit 1 }
    OK
}

# ── 2. Upgrade pip ─────────────────────────────────────────────────────────────
Step "Upgrade pip"
& $pip install --upgrade pip --quiet
OK

# ── 3. Core packages ───────────────────────────────────────────────────────────
Step "FastAPI + Supabase + auth + tasks + monitoring"
& $pip install `
    "fastapi[all]" "uvicorn[standard]" `
    supabase `
    pydantic-settings python-dotenv `
    "python-jose[cryptography]" "passlib[bcrypt]" `
    slowapi arq apscheduler `
    loguru "sentry-sdk[fastapi]" `
    sqlmodel
if ($LASTEXITCODE -ne 0) { Write-Error "pip install (core) failed"; exit 1 }
OK

# ── 4. Dev / Test packages ─────────────────────────────────────────────────────
Step "ruff, mypy, pytest suite, factory-boy, bandit"
& $pip install `
    ruff mypy "pydantic[mypy]" `
    pytest pytest-asyncio httpx `
    "factory-boy" faker `
    pytest-cov pytest-json-report `
    respx `
    bandit `
    pre-commit
if ($LASTEXITCODE -ne 0) { Write-Error "pip install (dev) failed"; exit 1 }
OK

Write-Host "`n[BE] Backend setup complete." -ForegroundColor Green
