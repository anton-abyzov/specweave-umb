---
increment: 0517-sw-e2e-skill
title: 'sw:e2e -- SpecWeave-Integrated Playwright E2E Skill'
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: sw:e2e -- SpecWeave-Integrated Playwright E2E Skill

## Problem Statement

The SpecWeave team-lead testing agent references `testing:e2e` which does not exist, leaving E2E test generation and execution as a manual gap. There is no automated bridge between spec.md acceptance criteria and Playwright tests, and sw:done Gate 2a runs Playwright directly without structured AC-mapped reporting. Accessibility auditing also requires a separate (nonexistent) `testing:accessibility` plugin.

## Goals

- Provide a single skill (`sw:e2e`) that generates, runs, and reports on Playwright E2E tests traced to spec.md ACs
- Replace the nonexistent `testing:e2e` reference so team-lead testing agents have a working skill to invoke
- Absorb accessibility auditing (axe-core via Playwright) so a separate plugin is unnecessary
- Produce `e2e-report.json` consumed by sw:done Gate 2a for automated pass/fail gating

## User Stories

### US-001: Generate E2E Tests from Acceptance Criteria (P1)
**Project**: specweave

**As a** developer
**I want** to generate Playwright E2E tests from my spec.md acceptance criteria
**So that** my tests are traceable to requirements without manual test-to-AC mapping

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a spec.md with AC entries in format `AC-USx-xx: Given/When/Then`, when `sw:e2e --generate <increment-id>` is invoked, then one `.spec.ts` test file is created per user story containing one test case per AC
- [x] **AC-US1-02**: Given ACs that form a natural user journey (e.g., sequential steps on the same page), when `sw:e2e --generate` runs, then those ACs are grouped into a single test with comments marking each AC-ID checkpoint
- [x] **AC-US1-03**: Given an AC with ID `AC-US1-01`, when a test is generated for it, then the test title contains the AC-ID (e.g., `test('AC-US1-01: user can see login form', ...)`)
- [x] **AC-US1-04**: Given a project with no `playwright.config.ts` but `@playwright/test` in package.json, when `sw:e2e --generate` runs, then the skill fails with a message instructing the user to create a Playwright config
- [x] **AC-US1-05**: Given a project with no `@playwright/test` in any package.json, when `sw:e2e --generate` runs, then the skill fails with a message instructing the user to install Playwright (`npm init playwright@latest`)

---

### US-002: Run E2E Tests and Produce AC-Mapped Report (P1)
**Project**: specweave

**As a** developer
**I want** to run E2E tests and get a structured report mapped to AC-IDs
**So that** I know which acceptance criteria pass or fail without manually cross-referencing test output

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given generated E2E tests exist, when `sw:e2e --run <increment-id>` is invoked, then Playwright executes all tests using the project's `playwright.config.ts`
- [x] **AC-US2-02**: Given test execution completes, when results are collected, then `e2e-report.json` is written to `.specweave/increments/<id>/reports/` with schema: `{ incrementId, timestamp, mode, playwrightConfig, summary: { total, passed, failed, skipped }, results: [{ acId, testFile, status, duration, error }] }`
- [x] **AC-US2-03**: Given a test mapped to `AC-US1-01` fails, when the report is generated, then `results[]` contains an entry with `acId: "AC-US1-01"`, `status: "fail"`, and `error` containing the failure message
- [x] **AC-US2-04**: Given `e2e-report.json` exists with `summary.failed > 0`, when sw:done Gate 2a reads the report, then Gate 2a blocks increment closure
- [x] **AC-US2-05**: Given `e2e-report.json` exists with `summary.failed === 0`, when sw:done Gate 2a reads the report, then Gate 2a passes

---

### US-003: Accessibility Auditing via --a11y Flag (P2)
**Project**: specweave

**As a** developer
**I want** accessibility auditing integrated into my E2E test runs
**So that** I catch WCAG violations without needing a separate accessibility plugin

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `sw:e2e --a11y <increment-id>` is invoked, when tests run, then each test page is scanned with `@axe-core/playwright` after the primary assertion
- [x] **AC-US3-02**: Given an axe violation is found on a page tested by `AC-US1-01`, when the report is generated, then the violation is attached to the `AC-US1-01` result entry under an `a11y` field
- [x] **AC-US3-03**: Given `--a11y` is used in standalone mode (no specific AC context), when violations are found, then they are grouped by page URL in the report's top-level `a11y` field
- [x] **AC-US3-04**: Given axe finds zero violations, when the report is generated, then the `a11y` field shows `{ violations: [], passes: N }` where N is the count of passed axe rules

---

### US-004: Team-Lead Testing Agent Integration (P1)
**Project**: specweave

**As a** team-lead testing agent
**I want** to invoke `sw:e2e` to handle E2E test suites
**So that** E2E testing integrates into parallel team development without requiring a nonexistent `testing:e2e` plugin

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the team-lead testing agent invokes `Skill({ skill: "sw:e2e", args: "--generate <increment-id>" })`, when the skill loads, then it reads the master spec from the increment path and generates tests
- [x] **AC-US4-02**: Given the team-lead testing agent invokes `Skill({ skill: "sw:e2e", args: "--run <increment-id>" })`, when tests complete, then `e2e-report.json` is written and the skill outputs a summary of pass/fail counts
- [x] **AC-US4-03**: Given sw:done invokes `Skill({ skill: "sw:e2e", args: "--run <increment-id>" })` during Gate 2a, when the skill completes, then Gate 2a reads `e2e-report.json` from the increment's `reports/` subfolder for pass/fail determination
- [x] **AC-US4-04**: Given the SKILL.md is placed at `plugins/specweave/skills/e2e/SKILL.md`, when any agent invokes `sw:e2e`, then the skill activates with correct frontmatter (description, argument-hint, allowed-tools, context, model)
- [x] **AC-US4-05**: Given an `evals.json` exists at `plugins/specweave/skills/e2e/evals/evals.json`, when skill quality is evaluated, then 3-4 eval scenarios validate generate, run, and a11y modes

## Functional Requirements

### FR-001: AC Parsing from spec.md
The skill parses spec.md for lines matching `- [x] **AC-USx-xx**: ...` using regex. It extracts AC-ID, the Given/When/Then text, and the parent US-ID. The parser must handle both checked `[x]` and unchecked `[ ]` ACs.

### FR-002: e2e-report.json Schema
```json
{
  "incrementId": "string",
  "timestamp": "ISO-8601",
  "mode": "run | generate | a11y",
  "playwrightConfig": "path/to/playwright.config.ts",
  "summary": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
  },
  "results": [
    {
      "acId": "AC-US1-01",
      "testFile": "e2e/us-001.spec.ts",
      "status": "pass | fail | skip",
      "duration": 1234,
      "error": null,
      "a11y": {
        "violations": [],
        "passes": 0
      }
    }
  ],
  "a11y": {
    "violations": [],
    "passes": 0
  }
}
```

### FR-003: SKILL.md Frontmatter
```yaml
---
description: Generate, run, and report Playwright E2E tests traced to spec.md acceptance criteria. Supports accessibility auditing via --a11y.
argument-hint: "--generate|--run|--a11y <increment-id>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
context: fork
model: sonnet
---
```

### FR-004: Playwright Detection
1. Search for `playwright.config.ts` or `playwright.config.js` in the project root and common locations
2. Search for `@playwright/test` in `package.json` dependencies
3. If config missing but package present: fail with "Playwright is installed but no config found. Run `npx playwright init` to create playwright.config.ts"
4. If both missing: fail with "Playwright is not installed. Run `npm init playwright@latest` to set up E2E testing"

## Out of Scope

- Writing application code (this skill generates test files only)
- Cypress support (Playwright only for this increment)
- Visual regression testing (screenshot comparison)
- Test data seeding or fixture management beyond what Playwright provides
- CI/CD pipeline configuration for running tests
- Auto-scaffolding Playwright config or installing browsers

## Non-Functional Requirements

- **Deliverable size**: SKILL.md under 800 lines, evals.json with 3-4 scenarios
- **Compatibility**: Works with Playwright v1.30+ and any project that has spec.md with AC entries

## Edge Cases

- spec.md with no ACs: Skill outputs "No acceptance criteria found in spec.md -- nothing to generate" and exits cleanly
- ACs without Given/When/Then format: Skill generates a test stub with a TODO comment noting the AC text
- Duplicate AC-IDs in spec.md: Skill warns but generates tests for all, appending a suffix to duplicates
- Playwright test timeout: Reported as `status: "fail"` with `error: "Test timed out after Xms"`
- Mixed --a11y with --generate: Only --run and --a11y can combine; --generate ignores --a11y flag with a warning

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| AC text too vague for meaningful test generation | 0.4 | 5 | 2.0 | Generate test stubs with TODOs; skill documents both patterns |
| Playwright version incompatibility with axe-core | 0.2 | 4 | 0.8 | Pin compatible version ranges in generated test imports |
| Gate 2a report format changes break consumption | 0.1 | 7 | 0.7 | Define schema in FR-002; sw:done reads with fallback handling |

## Technical Notes

- Target path: `repositories/anton-abyzov/specweave/plugins/specweave/skills/e2e/SKILL.md`
- Evals path: `repositories/anton-abyzov/specweave/plugins/specweave/skills/e2e/evals/evals.json`
- The team-lead testing agent file (`agents/testing.md`) references `testing:e2e` -- update it to reference `sw:e2e`
- sw:done Gate 2a currently runs Playwright directly -- update to invoke `sw:e2e --run` instead
- The skill reads spec.md from `.specweave/increments/<id>/spec.md` and writes tests to the project's `e2e/` directory
- Report output: `.specweave/increments/<id>/reports/e2e-report.json`

## Success Metrics

- Team-lead testing agent can invoke `sw:e2e` without errors (replacing nonexistent `testing:e2e`)
- 100% of spec.md ACs appear as mapped entries in `e2e-report.json`
- sw:done Gate 2a consumes `e2e-report.json` for pass/fail instead of running Playwright directly
- All 3-4 eval scenarios in `evals.json` pass validation
