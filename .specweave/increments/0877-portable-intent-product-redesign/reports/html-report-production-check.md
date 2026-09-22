# Public release report production verification

**Passed** at `https://spec-weave.com/releases/2.1/` after confirmed Pages deployment run `34882131675`, source `5d9a91cb27f49a5ad9414d55dd3f96f6089a189c`.

Explicitly headless Chromium verified desktop 1440×1050 and mobile 390×844. Both return HTTP200, render the intended primary heading and banner landmark, expose the skip link on Tab, reach all four section hash anchors, and open/close both disclosures using Enter/Space. There is no horizontal overflow with disclosures closed/open and no page errors. All **four axe audits pass with zero violations** across WCAG2A/AA, WCAG2.1AA and best-practice rules.

## Source and delivered bytes

- Reviewed source SHA256: `f0f79fa98af77fed35f3a621ef4737175ed94575d6cedc0b4447d2e3ece736f4` (11,793 bytes).
- Raw delivered SHA256: `96c4da4463f882a138194e9c541688e71a23e96295a71bb0da0b02754f8f3b4f` (12,160 bytes), identical in both browser cases.
- The initial strict raw-byte check correctly detected an additional delivery-layer script. A direct diff showed **exactly one Cloudflare analytics script** inserted immediately before the closing body tag. After removing only that specifically identified insertion, the delivered bytes exactly equal the reviewed source. No other normalization, whitespace rewrite or content substitution is allowed by the checker.
- The initial deployment response `Last-Modified` was `Mon, 14 Sep 2026 18:26:09 GMT`. Raw response HTML is retained beside the screenshots.

This is verified source identity with a disclosed CDN insertion, not a claim of raw byte equality. The first failed assertion is retained in `html-report-production-check-initial.log`. A separate non-browser HTTP probe returned403; the explicit headless browser received200 and completed the checks.

Evidence: `html-report-production-check.py`, `.json`, `.log`; screenshots and raw responses under `artifacts/html-report-review/production-*`. No source changes, account operations, or model calls.

Final deployment replay: both viewport cases and all four axe audits pass again. The accompanying10-second console/network observation is clean while open; see `html-report-console-check.json`. All owned review browser/server processes exited normally; none remain.
