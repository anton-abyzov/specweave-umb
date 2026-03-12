---
id: US-001
feature: FS-517
title: "Generate E2E Tests from Acceptance Criteria (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-001: Generate E2E Tests from Acceptance Criteria (P1)

**Feature**: [FS-517](./FEATURE.md)

**As a** developer
**I want** to generate Playwright E2E tests from my spec.md acceptance criteria
**So that** my tests are traceable to requirements without manual test-to-AC mapping

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a spec.md with AC entries in format `AC-USx-xx: Given/When/Then`, when `sw:e2e --generate <increment-id>` is invoked, then one `.spec.ts` test file is created per user story containing one test case per AC
- [x] **AC-US1-02**: Given ACs that form a natural user journey (e.g., sequential steps on the same page), when `sw:e2e --generate` runs, then those ACs are grouped into a single test with comments marking each AC-ID checkpoint
- [x] **AC-US1-03**: Given an AC with ID `AC-US1-01`, when a test is generated for it, then the test title contains the AC-ID (e.g., `test('AC-US1-01: user can see login form', ...)`)
- [x] **AC-US1-04**: Given a project with no `playwright.config.ts` but `@playwright/test` in package.json, when `sw:e2e --generate` runs, then the skill fails with a message instructing the user to create a Playwright config
- [x] **AC-US1-05**: Given a project with no `@playwright/test` in any package.json, when `sw:e2e --generate` runs, then the skill fails with a message instructing the user to install Playwright (`npm init playwright@latest`)

---

## Implementation

**Increment**: [0517-sw-e2e-skill](../../../../../increments/0517-sw-e2e-skill/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Write SKILL.md for sw:e2e
