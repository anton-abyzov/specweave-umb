---
id: US-002
feature: FS-517
title: "Run E2E Tests and Produce AC-Mapped Report (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-002: Run E2E Tests and Produce AC-Mapped Report (P1)

**Feature**: [FS-517](./FEATURE.md)

**As a** developer
**I want** to run E2E tests and get a structured report mapped to AC-IDs
**So that** I know which acceptance criteria pass or fail without manually cross-referencing test output

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given generated E2E tests exist, when `sw:e2e --run <increment-id>` is invoked, then Playwright executes all tests using the project's `playwright.config.ts`
- [x] **AC-US2-02**: Given test execution completes, when results are collected, then `e2e-report.json` is written to `.specweave/increments/<id>/reports/` with schema: `{ incrementId, timestamp, mode, playwrightConfig, summary: { total, passed, failed, skipped }, results: [{ acId, testFile, status, duration, error }] }`
- [x] **AC-US2-03**: Given a test mapped to `AC-US1-01` fails, when the report is generated, then `results[]` contains an entry with `acId: "AC-US1-01"`, `status: "fail"`, and `error` containing the failure message
- [x] **AC-US2-04**: Given `e2e-report.json` exists with `summary.failed > 0`, when sw:done Gate 2a reads the report, then Gate 2a blocks increment closure
- [x] **AC-US2-05**: Given `e2e-report.json` exists with `summary.failed === 0`, when sw:done Gate 2a reads the report, then Gate 2a passes

---

## Implementation

**Increment**: [0517-sw-e2e-skill](../../../../../increments/0517-sw-e2e-skill/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Write SKILL.md for sw:e2e
