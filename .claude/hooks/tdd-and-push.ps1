# tdd-and-push.ps1
# Multi-gate CI + automatic test report generation (HTML + PDF) + commit/push
# Pipeline: Lint → TypeCheck → Tests(JSON) → Build → Report → PDF → commit/push

param()

$ErrorActionPreference = "SilentlyContinue"
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$runStart    = Get-Date
$dateStamp   = Get-Date -Format "yyyyMMdd"
$runTs       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$resultsDir  = Join-Path $projectRoot ".test-results"
$reportsDir  = Join-Path $projectRoot "test-reports"

# Gate result tracking
$gates = @{}           # key = "layer:gate" → $true/$false
$overallPass = $true
$feTestJsonPath = Join-Path $resultsDir "fe-test.json"
$beCovJsonPath  = Join-Path $resultsDir "be-coverage.json"
$beTestJsonPath = Join-Path $resultsDir "be-test.json"
$feCovDir       = Join-Path $resultsDir "fe-coverage"

function Write-Banner([string]$msg, [string]$color = "Cyan") {
    Write-Host "`n$msg" -ForegroundColor $color
}

function Run-Gate([string]$key, [string]$label, [scriptblock]$cmd) {
    Write-Banner "  [GATE] $label" "Cyan"
    Set-Location $projectRoot
    & $cmd
    $ok = ($LASTEXITCODE -eq 0)
    $icon = if ($ok) { "✓" } else { "✗" }
    $color = if ($ok) { "Green" } else { "Red" }
    Write-Host "  [$icon] $label" -ForegroundColor $color
    $gates[$key] = $ok
    return $ok
}

function Generate-Reports([string]$layer, [string]$testJson, [string]$covJson, [string]$label) {
    $htmlOut = Join-Path $reportsDir "${label}테스트진행_$dateStamp.html"
    $pdfOut  = Join-Path $reportsDir "${label}테스트진행_$dateStamp.pdf"

    if (-not (Test-Path $testJson)) {
        Write-Host "  [REPORT] 테스트 JSON 없음, 리포트 생략: $testJson" -ForegroundColor DarkGray
        return
    }

    Write-Banner "  [REPORT] HTML 리포트 생성 중..." "Magenta"
    $covArg = if ((Test-Path $covJson)) { "--coverage `"$covJson`"" } else { "" }
    $cmd = "python `"$projectRoot\scripts\generate-test-report.py`" --type $layer --test `"$testJson`" $covArg --output `"$htmlOut`""
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [REPORT] HTML 생성 실패 (테스트 JSON 파싱 오류)" -ForegroundColor Yellow
        return
    }
    Write-Host "  [REPORT] HTML → $htmlOut" -ForegroundColor Magenta

    Write-Banner "  [REPORT] PDF 변환 중..." "Magenta"
    node "$projectRoot\scripts\html-to-pdf.js" "$htmlOut" "$pdfOut"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [REPORT] PDF  → $pdfOut" -ForegroundColor Magenta
    } else {
        Write-Host "  [REPORT] PDF 변환 실패 (playwright 미설치 가능성 있음)" -ForegroundColor Yellow
        Write-Host "  [REPORT] HTML 파일은 브라우저에서 직접 열 수 있습니다." -ForegroundColor DarkGray
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# DETECT CHANGES
# ══════════════════════════════════════════════════════════════════════════════
Set-Location $projectRoot
$gitStatus = git status --porcelain 2>$null
if (-not $gitStatus) {
    Write-Host "[HARNESS] 변경 없음 — 파이프라인 건너뜀." -ForegroundColor DarkGray
    exit 0
}
$feChanged = [bool]($gitStatus | Where-Object { $_ -match "frontend/" })
$beChanged = [bool]($gitStatus | Where-Object { $_ -match "backend/"  })
if (-not $feChanged -and -not $beChanged) { exit 0 }

# Create output directories
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null

Write-Host "`n╔═══════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   HARNESS CI + REPORT PIPELINE START  ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Magenta

# ══════════════════════════════════════════════════════════════════════════════
# FRONTEND PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if ($feChanged) {
    $fePath = Join-Path $projectRoot "frontend"
    Write-Banner "`n── FRONTEND ────────────────────────────────────────────────────" "White"

    $ok = Run-Gate "fe:lint" "Lint (ESLint --max-warnings 0)" {
        Set-Location $fePath
        npx eslint src --ext .ts,.tsx --max-warnings 0 2>&1
    }

    if ($ok) {
        $ok = Run-Gate "fe:types" "TypeCheck (tsc --noEmit)" {
            Set-Location $fePath
            npx tsc --noEmit 2>&1
        }
    } else { $overallPass = $false }

    if ($ok) {
        # Tests: always run with JSON output so we can generate a report even on failure
        $ok = Run-Gate "fe:tests" "Tests (Vitest + coverage JSON)" {
            Set-Location $fePath
            npx vitest run `
                --reporter=verbose --reporter=json `
                "--outputFile=$feTestJsonPath" `
                --coverage `
                "--coverage.reporter=json" `
                "--coverage.reportsDirectory=$feCovDir" 2>&1
        }
        if (-not $ok) { $overallPass = $false }
    } else { $overallPass = $false }

    if ($ok) {
        $ok = Run-Gate "fe:build" "Build (next build)" {
            Set-Location $fePath
            npm run build 2>&1
        }
        if (-not $ok) { $overallPass = $false }
    }

    # Generate report regardless of pass/fail (always show results)
    $feCovJson = Join-Path $feCovDir "coverage-final.json"
    Generate-Reports "frontend" $feTestJsonPath $feCovJson "프론트엔드"
}

# ══════════════════════════════════════════════════════════════════════════════
# BACKEND PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if ($beChanged) {
    $bePath = Join-Path $projectRoot "backend"
    Write-Banner "`n── BACKEND ─────────────────────────────────────────────────────" "White"

    $ok = Run-Gate "be:lint" "Lint (Ruff)" {
        Set-Location $bePath
        ruff check app tests 2>&1
    }

    if ($ok) {
        $ok = Run-Gate "be:types" "TypeCheck (mypy --strict)" {
            Set-Location $bePath
            mypy app --strict 2>&1
        }
    } else { $overallPass = $false }

    if ($ok) {
        $ok = Run-Gate "be:tests" "Tests (pytest + coverage JSON)" {
            Set-Location $bePath
            python -m pytest `
                --tb=short `
                --json-report "--json-report-file=$beTestJsonPath" `
                --cov=app "--cov-report=json:$beCovJsonPath" `
                --cov-fail-under=80 2>&1
        }
        if (-not $ok) { $overallPass = $false }
    } else { $overallPass = $false }

    # Generate report regardless of pass/fail
    Generate-Reports "backend" $beTestJsonPath $beCovJsonPath "백엔드"
}

# ══════════════════════════════════════════════════════════════════════════════
# GATE SUMMARY TABLE
# ══════════════════════════════════════════════════════════════════════════════
$elapsed = [int]((Get-Date) - $runStart).TotalSeconds
Write-Banner "`n── Gate Summary ($($elapsed)s) ─────────────────────────────────────" "Cyan"

$groups = @{ "FRONTEND" = @("fe:lint","fe:types","fe:tests","fe:build"); "BACKEND" = @("be:lint","be:types","be:tests") }
foreach ($grp in $groups.Keys) {
    $hasAny = $groups[$grp] | Where-Object { $gates.ContainsKey($_) }
    if ($hasAny) {
        Write-Host "  $grp" -ForegroundColor White
        foreach ($key in $groups[$grp]) {
            if ($gates.ContainsKey($key)) {
                $icon  = if ($gates[$key]) { "✓" } else { "✗" }
                $color = if ($gates[$key]) { "Green" } else { "Red" }
                $name  = $key.Split(":")[1].ToUpper()
                Write-Host "    [$icon] $name" -ForegroundColor $color
            }
        }
    }
}

Write-Banner "`n── Test Reports ────────────────────────────────────────────────" "Magenta"
Get-ChildItem $reportsDir -Filter "*$dateStamp*" -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor Magenta }

if (-not $overallPass) {
    Write-Banner "`n[HARNESS] 하나 이상의 게이트 실패 — 커밋 중단.`n" "Red"
    Write-Host "[HARNESS] 위 리포트에서 실패 원인을 확인하세요.`n" -ForegroundColor Yellow
    exit 1
}

# ══════════════════════════════════════════════════════════════════════════════
# COMMIT & PUSH
# ══════════════════════════════════════════════════════════════════════════════
Set-Location $projectRoot
$commitTs = Get-Date -Format "yyyy-MM-ddTHH:mm"

if ($feChanged) {
    git add frontend/
    $staged = git diff --cached --name-only | Where-Object { $_ -match "^frontend/" }
    if ($staged) {
        git commit -m "feat(frontend): harness auto-commit $commitTs"
        git push origin web
        Write-Host "`n[HARNESS] frontend → branch 'web' pushed ✓" -ForegroundColor Green
    }
}

if ($beChanged) {
    git add backend/
    $staged = git diff --cached --name-only | Where-Object { $_ -match "^backend/" }
    if ($staged) {
        git commit -m "feat(backend): harness auto-commit $commitTs"
        git push origin ai
        Write-Host "[HARNESS] backend → branch 'ai' pushed ✓" -ForegroundColor Green
    }
}

Write-Banner "`n[HARNESS] 파이프라인 완료 ($($elapsed)s)`n" "Magenta"
exit 0
