# SpecWeave production verification — final deployed source

Verified after successful [Pages run34882131675](https://github.com/anton-abyzov/specweave/actions/runs/34882131675), source `5d9a91cb27f49a5ad9414d55dd3f96f6089a189c`, on 2026-09-14. All browser checks used explicit headless Chromium, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`.

## Product behavior: passed

The unchanged guarded production runner exited **0**: **18/18 page/device checks passed, zero JavaScript runtime errors, zero browser console errors**. It checks nine routes at desktop1440×1000 and mobile390×844: homepage, product, integrations, four current guides, and two historical-context guides.

Verified current headings and semantic copy, no horizontal overflow, Issues footer links, exact clipboard install command, mouse/keyboard example-board interaction, mobile menu open/close, integration disclosure, and generated artwork decoding at2048×1152. Artwork SHA-256 matches `3f84480b6f3b4b3d4e7e53c83ee4982b5e9047a67fe1a08ab87833e06ea13c5d`.

Evidence: `specweave-production-verification.json`, `specweave-production-browser.log`, and screenshots in `artifacts/production-specweave/`. Final mobile homepage screenshot was visually inspected. Request diagnostics retain navigation/context-close `ERR_ABORTED` events for analytics and prefetches; none were filtered, and no `ERR_FAILED` event remains.

## Edge fixes: confirmed in actual production

Additional read-only headless checks of hotfix and installation docs exited **0**:

- Both actual raw HTML responses returned200 with **zero email-protection anchors**; hydrated DOM also contains none.
- Each page contains **one edge-injected analytics beacon**, without the manual duplicate or email decoder.
- Both native same-origin analytics requests to `/cdn-cgi/rum?` returned **204**.
- **Zero console errors** in this independent edge check.

Evidence: `specweave-production-cloudflare-diagnosis.json` and its log. The unlinked `/cdn-cgi/l/email-protection` fallback itself still returns404; the fix prevents Cloudflare from introducing that invalid destination into the published documentation. No external-zone settings or test filters were changed by this reviewer.

## Full link crawl: one external endpoint unresolved

The unchanged full recursive `linkinator@8.1.0` command exited **1** after checking **654 links**. It reports only **2 occurrences of one URL**, `https://render.com/pricing`, with status0, referenced from trailing-slash variants of the deployment-platform guide. No owned route, canonical, source/edit link, or email-protection link failed. No filters or skips were added.

Evidence: `specweave-production-links.log`. Status0 means the check could not obtain an HTTP response; it is not an HTTP404 or proof the page was removed. The PR build and crawl for the same repair had passed in GitHub run34881875897, as reported by root; the local production crawl is recorded separately and is not represented as green.

A separate `curl` check also timed out connecting to `render.com:443` before receiving HTTP (exit28 after5seconds); see `render-pricing-head-check.log`. This corroborates external connectivity failure from this machine. It does not justify changing the destination or hiding the failure.

Previous failing production JSON/logs remain preserved under `*-b5e796882-first`. The original failures, diagnosis, and causal evidence are documented in `docs-pr-crawl-deployment-classification.md` and `specweave-production-beacon-causality.json`.
