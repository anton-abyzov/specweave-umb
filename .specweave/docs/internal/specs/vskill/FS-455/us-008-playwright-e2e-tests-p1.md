---
id: US-008
feature: FS-455
title: "Playwright E2E Tests (P1)"
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
tldr: "**As a** contributor to vskill."
project: vskill
external:
  github:
    issue: 24
    url: https://github.com/anton-abyzov/vskill/issues/24
---

# US-008: Playwright E2E Tests (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** contributor to vskill
**I want** Playwright E2E tests covering all major UI workflows
**So that** UI regressions are caught automatically

---

## Acceptance Criteria

- [x] **AC-US8-01**: Given the E2E test suite, when Playwright runs, then all tests use `page.route()` to intercept LLM API calls and return deterministic mock responses (no real LLM calls)
- [x] **AC-US8-02**: Given a test fixture with sample plugins/skills/evals, when E2E tests run, then they cover: skill browsing, eval case CRUD (create, edit, delete), and assertion inline editing
- [x] **AC-US8-03**: Given mock LLM responses, when E2E tests exercise the benchmark flow, then they verify: progress display during run, final results rendering, and history file creation
- [x] **AC-US8-04**: Given mock comparator responses, when E2E tests exercise the comparison flow, then they verify: side-by-side display, content/structure scores, and verdict rendering
- [x] **AC-US8-05**: Given E2E tests run in CI, when `npx playwright test` executes, then all tests pass with the eval server started programmatically (no manual server start required)

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-015**: Create Playwright test fixtures and server setup
- [x] **T-016**: Write Playwright E2E tests for all major UI workflows
