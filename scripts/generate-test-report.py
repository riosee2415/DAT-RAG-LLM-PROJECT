#!/usr/bin/env python3
"""
generate-test-report.py
JSON 테스트 결과 → 차트 포함 HTML 리포트 생성기.
지원 포맷: vitest (frontend), pytest-json-report (backend)
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# ─── Parsers ──────────────────────────────────────────────────────────────────

def parse_vitest(data: dict) -> dict:
    tests = []
    for suite in data.get("testResults", []):
        file_path = suite.get("testFilePath", "")
        for t in suite.get("assertionResults", []):
            status = t.get("status", "unknown")
            tests.append({
                "name": t.get("fullName") or " > ".join(
                    (t.get("ancestorTitles") or []) + [t.get("title", "")]
                ),
                "file": file_path,
                "status": status,
                "duration_ms": t.get("duration") or 0,
                "error": (t.get("failureMessages") or [""])[0] if status == "failed" else None,
            })
    total_ms = sum(t["duration_ms"] for t in tests)
    return {
        "total": data.get("numTotalTests", len(tests)),
        "passed": data.get("numPassedTests", sum(1 for t in tests if t["status"] == "passed")),
        "failed": data.get("numFailedTests", sum(1 for t in tests if t["status"] == "failed")),
        "skipped": data.get("numPendingTests", sum(1 for t in tests if t["status"] == "pending")),
        "duration_s": round(total_ms / 1000, 2),
        "tests": tests,
    }


def parse_pytest(data: dict) -> dict:
    summary = data.get("summary", {})
    tests = []
    for t in data.get("tests", []):
        outcome = t.get("outcome", "unknown")
        longrepr = None
        if outcome == "failed":
            call = t.get("call", {})
            longrepr = call.get("longrepr") or call.get("crash", {}).get("message")
        tests.append({
            "name": t.get("nodeid", ""),
            "file": t.get("nodeid", "").split("::")[0],
            "status": outcome,
            "duration_ms": round((t.get("duration") or 0) * 1000, 1),
            "error": str(longrepr)[:600] if longrepr else None,
        })
    return {
        "total": summary.get("total", len(tests)),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "skipped": summary.get("skipped", 0),
        "duration_s": round(data.get("duration") or 0, 2),
        "tests": tests,
    }


def parse_coverage(coverage_path: str) -> list[dict]:
    try:
        raw = json.loads(Path(coverage_path).read_text(encoding="utf-8"))
    except Exception:
        return []

    files: list[dict] = []

    # Istanbul / v8 format: { "path": { "s": {...}, "b": {...}, ... } }
    if any(isinstance(v, dict) and "s" in v for v in raw.values()):
        for fpath, fdata in raw.items():
            stmts = fdata.get("s", {})
            if not stmts:
                continue
            covered = sum(1 for v in stmts.values() if v > 0)
            total = len(stmts)
            pct = round(covered / total * 100, 1) if total else 0
            files.append({"file": Path(fpath).name, "pct": pct, "covered": covered, "total": total})

    # pytest-cov JSON format: { "files": { "path": { "summary": {...} } } }
    elif "files" in raw:
        for fpath, fdata in raw["files"].items():
            s = fdata.get("summary", {})
            files.append({
                "file": Path(fpath).name,
                "pct": round(s.get("percent_covered", 0), 1),
                "covered": s.get("covered_lines", 0),
                "total": s.get("num_statements", 0),
            })

    return sorted(files, key=lambda x: x["pct"])  # ascending for chart (worst first)


# ─── HTML Renderer ────────────────────────────────────────────────────────────

def _status_icon(status: str) -> str:
    return {"passed": "✅", "failed": "❌", "skipped": "⏭️", "pending": "⏭️"}.get(status, "❓")


def _bar_color(pct: float) -> str:
    if pct >= 80:
        return "#22c55e"
    if pct >= 60:
        return "#f59e0b"
    return "#ef4444"


def render_html(report: dict, coverage: list[dict], test_type: str, run_ts: str) -> str:
    passed = report["passed"]
    failed = report["failed"]
    skipped = report["skipped"]
    total = report["total"]
    duration = report["duration_s"]
    rate = round(passed / total * 100, 1) if total else 0
    status_color = "#22c55e" if failed == 0 else "#ef4444"
    label = "프론트엔드" if test_type == "frontend" else "백엔드"
    avg_cov = round(sum(f["pct"] for f in coverage) / len(coverage), 1) if coverage else None

    # ── test rows ──────────────────────────────────────────────────────────────
    test_rows = ""
    for t in report["tests"]:
        dur = f"{t['duration_ms']}ms"
        err_block = ""
        if t["error"]:
            err_block = (
                f'<div style="margin-top:4px;padding:6px 8px;background:#fff1f2;'
                f'border-radius:4px;font-size:11px;color:#ef4444;white-space:pre-wrap;'
                f'word-break:break-all;font-family:monospace">{t["error"][:500]}</div>'
            )
        row_bg = "background:#fff5f5" if t["status"] == "failed" else ""
        test_rows += (
            f'<tr style="{row_bg}">'
            f'<td style="font-size:16px;text-align:center">{_status_icon(t["status"])}</td>'
            f'<td style="font-size:12px;word-break:break-all">{t["name"]}{err_block}</td>'
            f'<td style="font-size:11px;color:#94a3b8;white-space:nowrap">{Path(t["file"]).name}</td>'
            f'<td style="font-size:11px;color:#64748b;white-space:nowrap">{dur}</td>'
            f'</tr>'
        )

    # ── coverage rows ──────────────────────────────────────────────────────────
    cov_rows = ""
    for f in sorted(coverage, key=lambda x: -x["pct"])[:20]:
        bc = _bar_color(f["pct"])
        cov_rows += (
            f'<tr>'
            f'<td style="font-size:12px">{f["file"]}</td>'
            f'<td>'
            f'<div style="display:flex;align-items:center;gap:8px">'
            f'<div style="flex:1;background:#e2e8f0;border-radius:4px;height:8px">'
            f'<div style="width:{f["pct"]}%;background:{bc};height:8px;border-radius:4px"></div>'
            f'</div>'
            f'<span style="font-size:12px;font-weight:700;color:{bc};width:42px;text-align:right">{f["pct"]}%</span>'
            f'</div>'
            f'</td>'
            f'<td style="font-size:11px;color:#94a3b8">{f["covered"]}/{f["total"]}</td>'
            f'</tr>'
        )

    # ── failed tests detail ─────────────────────────────────────────────────────
    failed_section = ""
    if failed:
        rows = "".join(
            f'<tr>'
            f'<td style="font-weight:600;color:#ef4444;font-size:12px;word-break:break-all">{t["name"]}</td>'
            f'<td style="font-size:11px;color:#94a3b8">{Path(t["file"]).name}</td>'
            f'<td><pre style="font-size:11px;color:#ef4444;white-space:pre-wrap;margin:0">{t["error"] or ""}</pre></td>'
            f'</tr>'
            for t in report["tests"] if t["status"] == "failed"
        )
        failed_section = f"""
  <div class="section">
    <h2 style="color:#ef4444">❌ 실패 테스트 ({failed}건)</h2>
    <table><thead><tr><th>테스트명</th><th>파일</th><th>오류 내용</th></tr></thead><tbody>{rows}</tbody></table>
  </div>"""

    # ── chart data ──────────────────────────────────────────────────────────────
    cov_top = sorted(coverage, key=lambda x: x["pct"])[:12]
    chart_json = json.dumps({
        "passed": passed, "failed": failed, "skipped": skipped,
        "cov_labels": [f["file"] for f in cov_top],
        "cov_values": [f["pct"] for f in cov_top],
        "cov_colors": [_bar_color(f["pct"]) for f in cov_top],
    })

    # ── avg cov card ────────────────────────────────────────────────────────────
    cov_card = (
        f'<div class="card" style="border-top:3px solid {_bar_color(avg_cov)}">'
        f'<div class="label">평균 커버리지</div>'
        f'<div class="value" style="color:{_bar_color(avg_cov)}">{avg_cov}%</div>'
        f'</div>'
    ) if avg_cov is not None else ""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{label} 테스트 리포트 — {run_ts}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #f1f5f9; color: #0f172a; font-size: 14px; }}
.container {{ max-width: 1280px; margin: 0 auto; padding: 40px 24px; }}
.header {{ border-left: 5px solid {status_color}; padding: 0 0 0 20px; margin-bottom: 36px; }}
.header h1 {{ font-size: 26px; font-weight: 800; letter-spacing: -.02em; }}
.header .meta {{ color: #64748b; margin-top: 6px; font-size: 13px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }}
.card {{ background: #fff; border-radius: 14px; padding: 20px 24px;
         box-shadow: 0 1px 4px rgba(0,0,0,.06); border-top: 3px solid #e2e8f0; }}
.label {{ font-size: 11px; text-transform: uppercase; letter-spacing: .08em;
          color: #94a3b8; font-weight: 700; margin-bottom: 8px; }}
.value {{ font-size: 36px; font-weight: 800; line-height: 1; }}
.charts {{ display: grid; grid-template-columns: 260px 1fr; gap: 20px; margin-bottom: 28px; }}
.chart-box {{ background: #fff; border-radius: 14px; padding: 24px;
              box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
.chart-box h3 {{ font-size: 11px; text-transform: uppercase; letter-spacing: .08em;
                 color: #94a3b8; font-weight: 700; margin-bottom: 20px; }}
.section {{ background: #fff; border-radius: 14px; padding: 24px 28px;
            box-shadow: 0 1px 4px rgba(0,0,0,.06); margin-bottom: 24px; }}
.section h2 {{ font-size: 15px; font-weight: 700; margin-bottom: 18px;
               display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
.search {{ margin-left: auto; padding: 7px 14px; border: 1.5px solid #e2e8f0;
           border-radius: 8px; font-size: 13px; outline: none; width: 260px;
           transition: border-color .15s; }}
.search:focus {{ border-color: #6366f1; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ text-align: left; padding: 10px 14px; background: #f8fafc;
      font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
      color: #94a3b8; font-weight: 700; border-bottom: 1px solid #e2e8f0; }}
td {{ padding: 10px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
tr:last-child td {{ border-bottom: none; }}
.footer {{ text-align: center; font-size: 12px; color: #94a3b8; padding: 24px 0 0; }}
@media print {{
  body {{ background: #fff; }}
  .container {{ padding: 16px; }}
  .search {{ display: none; }}
}}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>{label} 테스트 리포트</h1>
    <div class="meta">
      실행일시: {run_ts} &nbsp;·&nbsp; 소요시간: {duration}s
      &nbsp;·&nbsp; 상태: {'<span style="color:#22c55e;font-weight:700">ALL PASSED ✅</span>' if not failed else f'<span style="color:#ef4444;font-weight:700">{failed}개 실패 ❌</span>'}
    </div>
  </div>

  <div class="cards">
    <div class="card" style="border-top-color:#6366f1">
      <div class="label">전체</div>
      <div class="value" style="color:#6366f1">{total}</div>
    </div>
    <div class="card" style="border-top-color:#22c55e">
      <div class="label">통과</div>
      <div class="value" style="color:#22c55e">{passed}</div>
    </div>
    <div class="card" style="border-top-color:#ef4444">
      <div class="label">실패</div>
      <div class="value" style="color:#ef4444">{failed}</div>
    </div>
    <div class="card" style="border-top-color:#f59e0b">
      <div class="label">건너뜀</div>
      <div class="value" style="color:#f59e0b">{skipped}</div>
    </div>
    <div class="card" style="border-top-color:{status_color}">
      <div class="label">성공률</div>
      <div class="value" style="color:{status_color}">{rate}%</div>
    </div>
    {cov_card}
  </div>

  <div class="charts">
    <div class="chart-box">
      <h3>결과 분포</h3>
      <canvas id="donut" height="210"></canvas>
    </div>
    <div class="chart-box">
      <h3>커버리지 현황 (하위 12개)</h3>
      {'<canvas id="cov" height="210"></canvas>' if coverage else '<p style="color:#94a3b8;text-align:center;padding:80px 0;font-size:13px">커버리지 데이터 없음</p>'}
    </div>
  </div>

{failed_section}

  {'<div class="section"><h2>📊 파일별 커버리지</h2><table><thead><tr><th>파일</th><th>커버리지</th><th>구문 수</th></tr></thead><tbody>' + cov_rows + '</tbody></table></div>' if coverage else ''}

  <div class="section">
    <h2>
      🧪 전체 테스트 ({total}건)
      <input class="search" id="q" type="text" placeholder="테스트명 또는 파일 검색…">
    </h2>
    <table>
      <thead>
        <tr>
          <th style="width:36px"></th>
          <th>테스트명</th>
          <th style="width:180px">파일</th>
          <th style="width:70px">시간</th>
        </tr>
      </thead>
      <tbody id="tbody">{test_rows}</tbody>
    </table>
  </div>

  <div class="footer">
    Harness Test Reporter &nbsp;·&nbsp; 생성: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
  </div>
</div>

<script>
(function() {{
  const d = {chart_json};

  // Donut
  new Chart(document.getElementById('donut'), {{
    type: 'doughnut',
    data: {{
      labels: ['통과', '실패', '건너뜀'],
      datasets: [{{
        data: [d.passed, d.failed, d.skipped],
        backgroundColor: ['#22c55e', '#ef4444', '#f59e0b'],
        borderWidth: 0, hoverOffset: 4
      }}]
    }},
    options: {{
      plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 12 }}, padding: 16 }} }} }},
      cutout: '68%', animation: {{ duration: 600 }}
    }}
  }});

  // Coverage bar
  const covCtx = document.getElementById('cov');
  if (covCtx && d.cov_labels.length) {{
    new Chart(covCtx, {{
      type: 'bar',
      data: {{
        labels: d.cov_labels,
        datasets: [{{
          label: '커버리지 %',
          data: d.cov_values,
          backgroundColor: d.cov_colors,
          borderRadius: 4,
        }}]
      }},
      options: {{
        indexAxis: 'y',
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ min: 0, max: 100, ticks: {{ callback: v => v + '%', font: {{ size: 11 }} }} }},
          y: {{ ticks: {{ font: {{ size: 11 }} }} }}
        }},
        animation: {{ duration: 600 }}
      }}
    }});
  }}

  // Search / filter
  const q = document.getElementById('q');
  const rows = document.querySelectorAll('#tbody tr');
  q.addEventListener('input', function() {{
    const kw = this.value.toLowerCase();
    rows.forEach(r => {{
      r.style.display = r.textContent.toLowerCase().includes(kw) ? '' : 'none';
    }});
  }});
}})();
</script>
</body>
</html>"""


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Harness test report generator")
    ap.add_argument("--type", choices=["frontend", "backend"], required=True)
    ap.add_argument("--test", required=True, help="Path to JSON test results")
    ap.add_argument("--coverage", default=None, help="Path to coverage JSON (optional)")
    ap.add_argument("--output", required=True, help="Output HTML file path")
    args = ap.parse_args()

    test_path = Path(args.test)
    if not test_path.exists():
        print(f"[reporter] ERROR: test results not found: {test_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(test_path.read_text(encoding="utf-8"))

    # Auto-detect format
    if "testResults" in data or "numTotalTests" in data:
        report = parse_vitest(data)
    elif "tests" in data and "summary" in data:
        report = parse_pytest(data)
    else:
        print("[reporter] ERROR: unrecognised test JSON format", file=sys.stderr)
        sys.exit(1)

    coverage: list[dict] = []
    if args.coverage:
        cov_path = Path(args.coverage)
        if cov_path.exists():
            coverage = parse_coverage(args.coverage)
        else:
            print(f"[reporter] WARNING: coverage file not found: {cov_path}", file=sys.stderr)

    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = render_html(report, coverage, args.type, run_ts)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[reporter] HTML → {out}  (passed={report['passed']}, failed={report['failed']}, total={report['total']})")


if __name__ == "__main__":
    main()
