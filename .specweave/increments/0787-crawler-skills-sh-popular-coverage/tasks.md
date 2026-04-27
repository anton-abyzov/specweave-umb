---
increment: 0787-crawler-skills-sh-popular-coverage
title: "Fix skills.sh crawler popular-skills coverage"
---

# Tasks: Fix skills.sh crawler popular-skills coverage

### T-001: Change default startPage from 1 to 0 + adjust resume condition
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given a fresh crawler run with no checkpoint, When `crawl()` executes, Then the first fetched URL is `https://skills.sh/api/skills/all-time/0` and `result.startedFromPage === 0`.

### T-002: Extract page-fetch body into `fetchAndSubmitPage(page, ctx)` helper
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given the existing skills-sh test fixtures, When the loop is refactored, Then all existing tests still pass without modification.

### T-003: Add page-0 backfill when existing checkpoint has lastPage>=1
**User Story**: US-001, US-003 | **AC**: AC-US1-03, AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given a checkpoint `{lastPage: 5}` (no `backfilledPage0`), When `crawl()` runs, Then it fetches page 0 once before resuming from page 6, logs `[skills-sh] one-shot page-0 backfill`, and writes `{lastPage: 5, backfilledPage0: true, ...}` after.

### T-004: Add `candidateSkillPaths(skillId)` helper + emit `skillPathCandidates` per submission
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given skillId `vercel-react-best-practices`, When `candidateSkillPaths()` is called, Then it returns the vendor-prefixed candidate list including `skills/react-best-practices/SKILL.md`. Given skillId `frontend-design` (no vendor prefix), Then it returns a shorter list without duplicate stripped entries.

### T-005: Extend bulk/route.ts Phase-2.5 to walk skillPathCandidates
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a bulk submission with `skillPath="skills/vercel-react-best-practices/SKILL.md"` (404) and `skillPathCandidates` containing `"skills/react-best-practices/SKILL.md"` (200), When the route processes it, Then the submission is accepted and the persisted `skillPath` is the resolved candidate. Given no `skillPathCandidates`, Then behavior is identical to before.

### T-006: Update __tests__/skills-sh.test.js
**User Story**: US-001, US-002, US-003 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given the existing in-process HTTP mock setup, When tests run, Then assertions cover: (a) default startPage 0; (b) page-0 backfill on existing checkpoint; (c) `candidateSkillPaths` correctness; (d) `skillPathCandidates` is included in the bulk submission body.

### T-007: Add vitest unit test for bulk route multi-candidate fallback
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a mocked `checkSkillMdExists` returning 404 for the first candidate and 200 for the second, When the bulk route processes a submission with `skillPathCandidates`, Then the resolved path is the second candidate.

### T-008: Add /coverage endpoint to crawl-worker server.js + scheduler getter
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given a crawl-worker with a recent skills-sh run, When `GET /coverage` is called, Then it returns `{ skillsShTotal: <number>, lastSkillsShRunAt: <ISO>, lastSampledAt: <ISO> }`.

### T-009: Document /coverage in crawl-worker/README.md
**User Story**: US-004 | **AC**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given `crawl-worker/README.md` after the change, When grepped for `/coverage`, Then a paragraph describes the endpoint, response shape, and use.

### T-010: Run all tests + manual prod smoke
**User Story**: US-001..US-004 | **AC**: All | **Status**: [x] completed
**Test Plan**: `node --test crawl-worker/__tests__/skills-sh.test.js` passes; `pnpm vitest run src/app/api/v1/submissions/bulk` passes; manual curl against prod bulk endpoint with vercel-react-best-practices candidates returns submitted status.
