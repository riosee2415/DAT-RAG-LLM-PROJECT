#!/usr/bin/env node
/**
 * html-to-pdf.js
 * Playwright로 로컬 HTML 리포트를 PDF로 변환.
 * Usage: node scripts/html-to-pdf.js <input.html> [output.pdf]
 *
 * 요구사항: 프론트엔드 node_modules에 playwright 설치되어 있어야 함.
 * (npm install -D playwright → npx playwright install chromium)
 */

const path = require('path')
const fs   = require('fs')

async function main() {
  const htmlArg = process.argv[2]
  if (!htmlArg) {
    console.error('[pdf] Usage: node html-to-pdf.js <input.html> [output.pdf]')
    process.exit(1)
  }

  const htmlPath = path.resolve(htmlArg)
  if (!fs.existsSync(htmlPath)) {
    console.error(`[pdf] File not found: ${htmlPath}`)
    process.exit(1)
  }

  const pdfPath = process.argv[3]
    ? path.resolve(process.argv[3])
    : htmlPath.replace(/\.html$/i, '.pdf')

  // Resolve playwright from frontend or root node_modules
  let chromium
  const candidates = [
    path.join(__dirname, '..', 'frontend', 'node_modules', 'playwright'),
    path.join(__dirname, '..', 'node_modules', 'playwright'),
  ]
  for (const p of candidates) {
    if (fs.existsSync(p)) { chromium = require(p).chromium; break }
  }
  if (!chromium) {
    console.error('[pdf] playwright not found. Run: cd frontend && npm install -D playwright && npx playwright install chromium')
    process.exit(1)
  }

  const browser = await chromium.launch({ headless: true })
  const page    = await browser.newPage()

  // file:// URI — works for local HTML with CDN resources
  const fileUri = 'file:///' + htmlPath.replace(/\\/g, '/')
  await page.goto(fileUri, { waitUntil: 'networkidle', timeout: 30_000 })

  // Wait for Chart.js to finish rendering
  await page.waitForTimeout(1200)

  await page.pdf({
    path: pdfPath,
    format: 'A4',
    landscape: false,
    printBackground: true,
    margin: { top: '1.5cm', right: '1.5cm', bottom: '1.5cm', left: '1.5cm' },
    displayHeaderFooter: true,
    headerTemplate: `<div style="font-size:9px;color:#94a3b8;width:100%;text-align:right;padding-right:1.5cm">Harness Test Report</div>`,
    footerTemplate: `<div style="font-size:9px;color:#94a3b8;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
  })

  await browser.close()
  console.log(`[pdf] PDF → ${pdfPath}`)
}

main().catch(e => {
  console.error('[pdf] ERROR:', e.message)
  process.exit(1)
})
