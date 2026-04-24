---
increment: 0692-remove-dead-mockgetskillbyname-wiring
title: Remove dead getSkillByName mock wiring from versions route test
type: bug
priority: P3
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 100
---

# Feature: Remove dead `getSkillByName` mock wiring from versions route test

## Problem Statement

During 0681 closure, two independent reviewers (code-review F-001 and grill) flagged dead mock wiring in `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts`:

- The file declares `const mockGetSkillByName = vi.hoisted(() => vi.fn());` (L15)
- The file mocks `@/lib/data` via `vi.mock("@/lib/data", () => ({ getSkillByName: mockGetSkillByName }));` (L27-29)
- `beforeEach` initializes it: `mockGetSkillByName.mockResolvedValue(SKILL);` (L96)
- Two 404 tests call `mockGetSkillByName.mockResolvedValue(null);` (L142, L183)

But the route implementation at `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts:14-15` no longer imports or calls `getSkillByName` — it queries `db.skill.findUnique` directly. Both 404 tests already drive the not-found branch via `mockDb.skill.findUnique.mockResolvedValueOnce(null)` on the adjacent line.

0681 intentionally left this dead code in place to keep its scope minimal (narrowest hotfix: add the missing `skill.findUnique` mock). This increment closes that loose end.

## Interview Coverage

Single-file deletion-only test-hygiene cleanup. Covered categories:

- **architecture**: N/A — test-file edit only, no source change
- **integrations**: N/A — no integrations touched
- **ui-ux**: N/A — no UI
- **performance**: N/A — no runtime impact
- **security**: N/A — no security surface touched
- **edge-cases**: Covered by AC-US1-03 (suite stays 11/11) and AC-US1-04 (pure deletion, verified by `git diff`)

## User Stories

### US-001: Remove dead `getSkillByName` mock wiring
**Project**: vskill-platform

**As a** vskill-platform developer reading the versions route test file,
**I want** the test to mock only what the code under test actually uses,
**So that** the file is an honest contract and future refactors don't waste time wiring up phantom dependencies.

**Acceptance Criteria**:
- [x] **AC-US1-01**: All 5 identified dead-code occurrences are removed from `route.test.ts` exactly as specified (L15 hoisted declaration, L27-29 `vi.mock("@/lib/data", ...)` block, L96 beforeEach assignment, L142 and L183 `mockResolvedValue(null)` calls). No other lines are modified.
- [x] **AC-US1-02**: After edits, `grep -c "getSkillByName\|@/lib/data" route.test.ts` returns `0` — no reference to either identifier remains anywhere in the test file.
- [x] **AC-US1-03**: `npx vitest run` on the target file returns 11 passed / 0 failed — identical to the post-0681 baseline.
- [x] **AC-US1-04**: `git diff` on the test file shows only deletions (lines prefixed `-`, plus consequential blank-line adjustments). Zero added lines of content.
