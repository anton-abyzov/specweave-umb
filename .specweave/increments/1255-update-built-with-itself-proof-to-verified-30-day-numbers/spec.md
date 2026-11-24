# Update Built with itself proof to verified 30-day numbers

## Problem

specwithcode.com (spec-weave.com/code/) still says "367 pull requests ... October 2026" in the "Built with itself" section, the "Built with itself" card and the home page list. The SpecWithCode README (anton-abyzov/specwithcode PR #32) now carries verified numbers for October 9 to November 7, 2026, so the site is stale and smaller than the truth, and its thread-count stats (167, 2,473) are no longer backed by a current count.

## Scope

In: the stats and source note in `BuiltWithItself.tsx`, the card in `code.tsx`, the home page line in `index.tsx`, the matching messages in all 8 locale `code.json` files, a "See the specs" link to the public increments folder. Out: the screenshot, the merged-PR list, other pages.

## Acceptance Criteria

- [ ] AC-01: The /code "Built with itself" section shows 302 increments (215 completed) and 1,393 merged pull requests (169 release PRs) as headline stats, plus "418+" scoped as a floor of thread-linked PRs (204 threads: 278 Claude Code, 127 Codex, 13 GitHub Copilot) for October 9 to November 7, 2026; no "367", "167" or "2,473" stats remain and nothing claims every change was made in SpecWithCode.
- [ ] AC-02: The section and the "Built with itself" card link "See the specs" to https://github.com/anton-abyzov/specweave-umb/tree/main/.specweave/increments, and the card keeps a link to the source repository.
- [ ] AC-03: All 8 locales (de, es, fr, ja, ko, pt-BR, ru, zh-CN) carry natural translations of the new strings, and English copy has no em dashes.
- [ ] AC-04: The docs-site landing tests and a docs-site build pass, the change merges to develop, and the live https://spec-weave.com/code/ shows 302 and 1,393 (headless check).

## Approach

Keep the existing translation ids where the meaning stays (`builtWithItself.stat.prs`, `builtWithItself.statsSource`, `code.more.builtWithItself.body`, `home.builtWith.specwithcode`), add `builtWithItself.stat.specs`, `builtWithItself.stat.threadLinked`, `builtWithItself.specsLink`, `code.more.builtWithItself.sourceLink`, and drop `stat.threads` and `stat.allThreads` from every locale. The card's main link becomes "See the specs"; the source repository link moves inline into the card text. A test in `code-landing.test.ts` pins the numbers and the specs URL.

## Decisions

### Asked
- none (numbers and wording scope given by the user)
### Defaulted (change any before sw-do)
- D-01 the unverified 167 and 2,473 thread stats are removed rather than kept → removed
### Open
- none

## Tasks

### T-01 New numbers, links and translations on the landing pages
- AC: AC-01, AC-02, AC-03 | Files: docs-site/src/components/code/BuiltWithItself.tsx, docs-site/src/pages/code.tsx, docs-site/src/pages/index.tsx, docs-site/i18n/*/code.json, docs-site/src/__tests__/code-landing.test.ts | Test: cd repositories/anton-abyzov/specweave/docs-site && npx vitest run src/__tests__/code-landing.test.ts

### T-02 Build, merge and live check
- AC: AC-04 | Files: docs-site | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build
