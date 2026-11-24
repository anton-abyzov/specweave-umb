# Independent review: T31 strict documentation links

Reviewed the 22-file uncommitted diff in `/tmp/specweave-0877-root` against `048751d3c986f5c28686ef1464b90deddb755637` on 2026-09-14. This reviewer did not author T31. No source edits made during review.

## Findings raised and resolved

1. **P2 — Do not represent an overview as the missing implementation guide.** `docs-site/docs/skills/extensible/extensible-skills.md:30` changes the implementation-guide link into a link to the page containing it. The entire destination is a short index and quick-reference table; it does not contain the promised getting-started instructions, architecture, examples, memory format, or FAQ. The same unavailable-guide claim occurs in `docs-site/docs/skills/extensible/index.md:29` and `docs-site/docs/skills/extensible/extensible-skills-standard.md:15,148`. The existing redirect explains the alias, but a successful route does not establish equivalent content. Retain a clearly labeled unpublished historical reference or use an honest overview label; remove the self-link and false availability claims.
2. **P2 — The canonical quickstart is not MCP Tool Search documentation.** `docs-site/docs/guides/lazy-plugin-loading.md:233` labels `/docs/getting-started` as “MCP Tool Search” and describes deferred loading. The current destination documents installation, the work board, increments, handoff, and verification; it contains no MCP Tool Search guidance. The earlier alias and fragment do not justify presenting the replacement as that feature. Use a plain historical reference or an independently verified relevant destination.

## Verified strengths and evidence

- `onBrokenLinks: 'throw'` restores the build gate; neither link-checking implementation nor dependencies change. Existing `onBrokenMarkdownLinks: 'warn'` is unchanged.
- `_page-template.md` is an authoring stub (literal “Page Title”, “Section 1”, and `related-page-1.md` placeholders). `draft: true` correctly excludes it; no generated template HTML exists in the production output.
- Navbar test updates retain the maximum-four constraint and require each of the four current destinations. This is stronger than the prior label-only assertions. Footer now verifies the exact GitHub Issues URL; unrelated assertions remain.
- Independently ran the two changed test files and unchanged strict-config test: **14 tests passed across 3 files**. Full output: `docs-strict-links-review-tests.log`.
- Inspected the real production build output and root's `docs-strict-build.log`: static generation succeeded, with no broken-link warning. Eight canonical entrypoint HTML files exist: getting started, academy, compliance standards, living documentation, skill development guidelines, extensible-skills overview, product, integrations.
- No test skips, deleted tests, weakened checker, dependency changes, or additional invented redirects in the reviewed diff.

## Re-verification and approval

The author corrected both findings before approval. The extensibility overview no longer links to itself or promises an available implementation guide; the index and standard accurately label the overview and unavailable historical implementation/Reflect material. The lazy-loading page now labels the real installation destination “Getting Started”. This reviewer inspected the complete corrected 22-file diff; no additional findings.

Independently ran the final production build after those corrections: **exit 0, no broken-link or broken-anchor warning** (`docs-strict-review-final-build.log`). The 14 focused tests had passed; their source and configuration were unchanged by the prose corrections. `git diff --check` passed.

Ran `verify-docs-strict-links.cjs` against that exact static output using explicit headless Chromium, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`: **12 canonical routes returned HTTP 200 with expected real headings; zero page errors; the unpublished authoring template returned HTTP 404**. Assertions also prove the overview has no article self-link, the missing-guide notice is visible on desktop and mobile, and the lazy-loading link has the honest label. Browser and local server closed after the check. Full evidence: `docs-strict-links-headless.json`, `docs-strict-links-headless.log`, and screenshots under `artifacts/docs-strict-links/`. Mobile screenshot visually inspected.

**Approved for commit and integration.** This review does not claim the inherited full docs test suite is green or that the website is deployed. No production or visible browser used.
