# SpecWeave production verification — ready, not executed

Initially prepared against `048751d3c986f5c28686ef1464b90deddb755637` after root review of the six current/historical guide updates. Runtime assertions are unchanged. The runner now requires `SPECWEAVE_DEPLOYED_SOURCE` to be the full 40-character source SHA from the successful Pages workflow. **Wait for root to supply that confirmed deployment SHA and run before executing.** No request to old production and no browser launch was made during preparation. Node syntax validation and both deployment guards passed.

`verify-specweave-production.cjs` adapts the existing `docs-site/scripts/continuity-e2e.cjs` and reuses its actual clipboard, keyboard board, integration disclosure and mobile navigation checks. It loads the existing Playwright dependency from the release worktree; it does not edit repository source or install dependencies.

Coverage: homepage, product, integrations and the six updated guide routes, each at desktop 1440×1000 and mobile 390×844. Assertions cover HTTP 200, deployed headings and semantic copy, no horizontal overflow, updated Issues footer, actual copy-button interaction and exact command, keyboard/mouse example-card interaction, integration disclosure and mobile navigation. It records/fails runtime JavaScript errors and browser console errors. Network failures are recorded separately for diagnosis.

The generated artwork must decode at 2048×1152, return `image/webp`, and match the shipped SHA-256 `3f84480b6f3b4b3d4e7e53c83ee4982b5e9047a67fe1a08ab87833e06ea13c5d`.

## Execute after deployment confirmation

From the umbrella root, run the browser verification:

```bash
VERIFY_DEPLOYED_SPECWEAVE=1 SPECWEAVE_DEPLOYED_SOURCE="$confirmed_pages_source_sha" PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node .specweave/increments/0877-portable-intent-product-redesign/reports/verify-specweave-production.cjs > .specweave/increments/0877-portable-intent-product-redesign/reports/specweave-production-browser.log 2>&1
```

Then run the **unchanged full recursive link checker** against production. Only the base URL differs from CI; do not add filters or skips:

```bash
PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npx --yes linkinator@8.1.0 https://spec-weave.com --recurse --verbosity error --skip "github.com/anton-abyzov/specweave/edit" > .specweave/increments/0877-portable-intent-product-redesign/reports/specweave-production-links.log 2>&1
```

Set `confirmed_pages_source_sha` only from root's successful deployment confirmation. The source SHA is recorded as deployment metadata; browser content and the artwork hash are verified separately. Run both commands even if one fails; preserve each exit status and distinguish local navigation defects from external provider failures. The production runner refuses execution unless `VERIFY_DEPLOYED_SPECWEAVE=1` and a lowercase 40-hex `SPECWEAVE_DEPLOYED_SOURCE` are supplied. It always launches with explicit `headless: true`; no personal browser, UI mode, Inspector or visible report is used.

## Evidence destinations

- `reports/specweave-production-verification.json`: source identity, artwork hash, 18 route/device results, runtime/console errors and request failures.
- `reports/specweave-production-browser.log`: concise run result and any failure.
- `reports/specweave-production-links.log`: unmodified full link-checker output.
- `reports/artifacts/production-specweave/`: desktop/mobile screenshots for every route (full page on marketing routes, viewport screenshots on guides).

The current release checkout is `/tmp/specweave-0877-root`. Set `SPECWEAVE_VERIFY_REPO` only if that checkout moves; the target production origin remains fixed to `https://spec-weave.com`.
