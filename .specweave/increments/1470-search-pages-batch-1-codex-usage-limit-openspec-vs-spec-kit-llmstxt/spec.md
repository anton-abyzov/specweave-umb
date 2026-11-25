# 1470 Search pages batch 1: Codex usage limit, OpenSpec vs Spec Kit, llms.txt

## Problem

The October 28, 2026 keyword audit (1127, `reports/seo-audit-raw.md`) mapped measured searches to pages. 1127 shipped the compare hub, handoff.md and the switch guides. Pages it marked P0 or P1 still return 404 on November 24, 2026: `/docs/compare/openspec-vs-spec-kit` (P0), `/docs/compare/openspec-alternatives` (P0), `/docs/guides/codex-usage-limit` (P1, mirror of our strongest guide) and `/docs/guides/ai-coding-agent-orchestration` (P1). `specwithcode.com/llms.txt` redirects to `spec-weave.com/code/llms.txt`, which is a 404, so AI crawlers that start from the SpecWithCode domain find nothing. The owner approved a small first batch on November 24, 2026, on the condition that it makes sense (anymodel.org research follow-up).

## Scope

In: two new pages in `docs-site/docs/` (one SpecWithCode-led, one SpecWeave-led), their sidebar and compare-hub links, `static/llms.txt` entries, a new `static/code/llms.txt` for the SpecWithCode domain. Out: Russian translations (the whole `docs` section is English-only in `src/data/englishOnlyPaths.ts`; translating one guide needs a per-path exception plus canonical and hreflang work), a "Claude Code в России" page (owner decision, see Open), model-vs-model comparison pages (stale within weeks), Cloudflare rules, landing page layout.

## Acceptance Criteria

- [ ] AC-01: `https://spec-weave.com/docs/guides/codex-usage-limit/` returns 200 and covers how Codex plan limits work, how to check what is left and the ways to keep working, each vendor fact linked to a live OpenAI page fetched on or after November 24, 2026; it makes no savings claim and links the Claude Code usage limit guide both ways.
- [ ] AC-02: `https://spec-weave.com/docs/compare/openspec-vs-spec-kit/` returns 200 with a neutral comparison of OpenSpec and GitHub Spec Kit sourced from their own repositories or docs, with SpecWeave named as a third option and not as a winner; it is linked from the compare hub.
- [ ] AC-03: `npm run build` in `docs-site` passes, and `node scripts/verify-seo.mjs` (title 60 characters or fewer, description 160 or fewer) passes for both new pages.
- [ ] AC-04: `https://specwithcode.com/llms.txt` returns 200 text after redirects, describing SpecWithCode with links to its live pages; `https://spec-weave.com/llms.txt` lists both new pages. Every URL in both files answers 200.
- [ ] AC-05: Fresh-context review findings are resolved, the PR to `develop` merges green and the deploy is verified live.

## Approach

Worktree of `repositories/anton-abyzov/specweave` from `origin/develop`, branch `seo/search-pages-batch-1`. Follow the shape of `docs/guides/claude-code-usage-limit.md` and the existing compare pages (frontmatter `slug`, `keywords`, short title and description). Vendor facts are fetched live, never from memory: Codex plan and limit pages on openai.com and help.openai.com; OpenSpec and Spec Kit READMEs on GitHub. Brand rules: SpecWithCode is never called a fork, no savings claims, fallback claims state their condition (a compatible provider signed in plus the project rule). `static/code/llms.txt` follows the llmstxt.org format and the SpecWithCode section of `static/llms.txt`.

Rejected: an orchestration page in this batch (P1 but overlaps `/code` and the "How SpecWithCode works" tutorial; needs the /code layout owner); `openspec-alternatives` (P0, but a directory-style list beside the comparison would split one intent across two thin pages; do it in batch 2 once the comparison has impressions).

## Decisions

### Asked
- D-01 Open a small search-pages increment → yes, if it makes sense (owner, November 24, 2026).

### Defaulted (change any before sw-do)
- D-02 Batch is two pages plus llms.txt, chosen from 1127's measured map, not new keyword research.
- D-03 English only this batch; Russian needs the englishOnlyPaths change first.
- D-04 No model comparison pages: vendor lineups change monthly and the pages go stale and thin.

### Open
- D-05 "Claude Code в России": owner to confirm. Recommendation: do not build. Russia is not on Anthropic's supported-countries list (https://www.anthropic.com/supported-countries, effective November 12, 2026; it covers Claude.ai, Claude Code and the API and also people physically in an unsupported region), so an honest page can only say it is unsupported, and any how-to reads as advice to get around the region rule, which conflicts with Anthropic's terms and our brand rules.
- D-06 Batch 2 candidates (not built): `openspec-alternatives` (1127 P0), and "Claude Code with DeepSeek, GLM, Kimi or a local model" from the vendors' own Anthropic-compatible endpoints (honest answer to the demand anymodel.org sells into; needs the app's current provider code checked for any SpecWithCode claim).

## Tasks

### T-01 Codex usage limit guide
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specweave/docs-site/docs/guides/codex-usage-limit.md, repositories/anton-abyzov/specweave/docs-site/docs/guides/claude-code-usage-limit.md | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-02 OpenSpec vs Spec Kit comparison
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave/docs-site/docs/guides/openspec-vs-spec-kit.md, repositories/anton-abyzov/specweave/docs-site/docs/guides/compare.md | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-03 Sidebar links and both llms.txt files
- AC: AC-04 | Files: repositories/anton-abyzov/specweave/docs-site/sidebars.ts, repositories/anton-abyzov/specweave/docs-site/static/llms.txt, repositories/anton-abyzov/specweave/docs-site/static/code/llms.txt | Test: node repositories/anton-abyzov/specweave/docs-site/scripts/verify-seo.mjs

### T-04 Review, merge, verify live and close 1470
- AC: AC-05 | Files: .specweave/increments/1470-search-pages-batch-1-codex-usage-limit-openspec-vs-spec-kit-llmstxt/ | Test: curl -sfL https://specwithcode.com/llms.txt -o /dev/null && curl -sf https://spec-weave.com/docs/guides/codex-usage-limit/ -o /dev/null && curl -sf https://spec-weave.com/docs/compare/openspec-vs-spec-kit/ -o /dev/null
