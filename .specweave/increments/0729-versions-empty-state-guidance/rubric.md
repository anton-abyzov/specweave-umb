---
increment: 0729-versions-empty-state-guidance
title: "Versions tab empty-state guidance"
generated: "2026-04-25"
source: auto-generated
version: "1.0"
status: graded
---

# Quality Rubric — 0729

| ID | Criterion | Evaluator | Result |
|---|---|---|---|
| R-01 | AC-US1-01: Source skill + empty versions renders explanatory text + "Submit on verified-skill.com" CTA | sw:grill | [x] PASS — VersionHistoryPanel.tsx:188-219 renders LocalEmptyState with copy + CTA when origin === "source" |
| R-02 | AC-US1-02: Installed skill + empty versions keeps legacy "No version history available" message, no CTA | sw:grill | [x] PASS — VersionHistoryPanel.tsx:221-230 returns InstalledEmptyState with no submit affordance |
| R-03 | AC-US1-03: CTA href = `https://verified-skill.com/submit?repo=<encoded>` (or bare `/submit` when no URL); target=_blank + rel=noopener noreferrer | sw:grill | [x] PASS — buildSubmitUrl() at submit-url.ts encodes valid GitHub URLs and falls back defensively; CTA in panel applies target/rel correctly |
| R-04 | AC-US1-04: Stable `data-testid` selectors for both branches (`versions-empty-state-local` / `versions-empty-state-installed`) | sw:grill | [x] PASS — both data-testid values present in source; verified by 5 passing tests |
| R-05 | All new tests pass (T-001..T-005) | sw:grill | [x] PASS — 11/11 new tests green; full eval-ui suite 1471/1471 |
| R-06 | Production build succeeds | sw:grill | [x] PASS — `vite build` completes; no 0729-related typecheck errors |
| R-07 | No scope creep beyond spec | sw:grill | [x] PASS — only files in plan.md modified; SKILL.md frontmatter bump is a smoke-test prereq named in T-005 |
