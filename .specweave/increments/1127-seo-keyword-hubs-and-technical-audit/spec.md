# SEO keyword hubs and technical audit

## Problem

spec-weave.com, /code and verified-skill.com do not rank for measured high-volume terms ("claude code skills", "openspec" at 10K-100K US/month; "claude code handoff", "switch from claude code to" autocomplete). The 2026-10-28 audit (reports/seo-plan.md) found comparison pages buried in a collapsed sidebar, no /docs/compare/ hub (404), titles and descriptions over length, "Claude Code handoff" absent from its own page, no switch-to-OpenCode/Cursor or handoff.md pages, and verified-skill.com's /claude-code-skills hub unlinked from its nav.

## Scope

In: docs-site metadata, sidebar/navbar/footer links, new guide pages, llms.txt, verify-seo checks; vskill-platform nav links, /claude-code-skills schema and copy, new /agent-skills page, tests. Out: landing page layout (owned by the violet redesign thread), Cloudflare redirects and cache rules, Search Console actions, sitemap chunking, backlinks (reports/seo-plan.md section E).

## Acceptance Criteria

- [x] AC-01: docs-site has a /docs/compare/ hub linked from navbar, footer and an expanded sidebar category; comparison and switch guides have titles of 60 or fewer rendered characters and descriptions of 160 or fewer, enforced by verify-seo.mjs.
- [x] AC-02: New pages handoff.md, switch Claude Code to OpenCode, switch to Cursor exist with sourced vendor claims, and cross-tool-handoff targets "Claude Code handoff" in title and H1.
- [x] AC-03: verified-skill.com links /claude-code-skills from header and footer, the hub emits FAQPage and ItemList schema, and /agent-skills exists with tests passing.
- [x] AC-04: Both builds pass, a fresh-context review is resolved, PRs merge and deploys are verified live.

## Approach

Implement the audit plan PR 1 and PR 2 in worktrees ~/.specwithcode/m4/worktrees/{specweave,vskill-platform}/seo-keyword-hubs on branch seo/keyword-hubs-20261028. Do not touch src/pages/index.tsx or code.tsx layout; hand those link items (plan D2, D3, A6) to the violet redesign thread. No spec-weave.com "Claude Code skills" hub: it would compete with verified-skill.com, so link to it instead.

## Decisions

### Defaulted
- Base on develop/main, not the unmerged violet branch; rebase if it merges first.
- Skip switch-to-Pi until Pi's AGENTS.md and skills behaviour is verified.

## Tasks

### T-01 docs-site compare hub, metadata, links and new guides
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave/docs-site/ | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-02 verified-skill.com hub links, schema and agent-skills page
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/src/ | Test: npm --prefix repositories/anton-abyzov/vskill-platform test

### T-03 Verify and close 1127
- AC: AC-04 | Files: .specweave/increments/1127-seo-keyword-hubs-and-technical-audit/ | Test: specweave verify 1127
