# Public release report independent review

Reviewed `docs-site/static/releases/2.1/index.html` read-only. No private filesystem paths, credential values/patterns, or unsupported material product claims were found. Published versions, test counts, the 48-location breakdown, optional integrations, and explicit limitations match the release evidence. The concise page links to relevant changes, releases, deployment history and product guides.

**Approved after one accessibility repair.** The original brand/date container `.top` was outside a landmark, producing one moderate `region` violation. The author changed it to a top-level semantic `<header class="top">`. An independent recheck passes all six desktop/mobile/narrow × closed/open axe audits with **zero violations of any severity**. No source changes were made by the reviewer.

## Headless verification

Chromium launched with explicit `headless=True`, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`. A disposable loopback HTTP server served the exact source HTML, with the existing production build supplying its relative-link destinations. No source or ledger changes, browser profiles, account actions, or model calls.

- 1440×1050, 390×844 and 320×720 viewports: zero horizontal overflow with disclosures closed and open; zero page errors.
- Skip link appears on keyboard focus and reaches main. All five hash destinations exist; navigation reaches the corresponding sections.
- Both native details controls are reached with Tab and open/close with Enter/Space. Open detail content is visible.
- Six unique internal routes return HTTP200 from the production build: home, product, dashboard guide, cross-tool handoff, integrations and dogfooding. This is local-build verification, not deployed SpecWeave-site verification.
- Axe WCAG2A/AA, WCAG2.1AA and best-practice checks ran in all six viewport/disclosure combinations; the initial `.top` finding is resolved in the recorded follow-up.
- Desktop and mobile screenshots were visually inspected. Layout, reading order and wrapping are coherent, with no clipped content.
- Fresh public reachability checks: Verified Skills home and `/studio` both return HTTP200, show their expected primary heading, and produce zero page errors. This is a bounded page-load check, not a repeat of the full production suite.

Evidence: `html-report-review.py`, `.json`, `.log`; screenshots under `artifacts/html-report-review/`.

Reviewed HTML SHA256: `97054ab4002038f2a98b161bf8eabea36f5f5dbed7428995ab6a476385e97d57`.

Follow-up evidence: `html-report-review-after.json`; final reviewed HTML SHA256 `f0f79fa98af77fed35f3a621ef4737175ed94575d6cedc0b4447d2e3ece736f4`. Original evidence is retained in `html-report-review-before.json`.

Prepared `html-report-production-check.py` for the exact public `/releases/2.1/` route. It verifies reviewed HTML bytes, desktop/mobile keyboard/hash behavior, no overflow/errors, and open/closed axe results. After deployment confirmation it passed against production; see `html-report-production-check.md` for the exact source comparison, disclosed Cloudflare insertion and four clean axe audits.
