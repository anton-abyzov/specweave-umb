---
increment: 0517-sw-e2e-skill
title: "sw:e2e -- SpecWeave-Integrated Playwright E2E Skill"
total_tasks: 5
completed_tasks: 5
by_user_story:
  US-001: [T-001]
  US-002: [T-001]
  US-003: [T-002]
  US-004: [T-003, T-004, T-005]
---

# Tasks: sw:e2e -- SpecWeave-Integrated Playwright E2E Skill

## User Story: US-001 - Generate E2E Tests from Acceptance Criteria

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 1 total, 1 completed

### T-001: Write SKILL.md for sw:e2e

**User Story**: US-001, US-002
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** SKILL.md is written at `plugins/specweave/skills/e2e/SKILL.md`
- **When** any agent invokes `sw:e2e`
- **Then** the skill activates with correct frontmatter and all 8 sections are present (argument parsing, environment validation, AC extraction, generate mode, run mode, a11y mode, report schema, edge cases)

**Test Cases**:
1. **Manual / Eval**: `evals/evals.json` scenario "generate-from-spec"
   - Agent reads spec.md, extracts AC-IDs, creates one test file per user story
   - Each test title contains the AC-ID (AC-US1-03)
   - Playwright detection runs before generation (AC-US1-04, AC-US1-05)
   - **Coverage Target**: 100% of SKILL.md sections reachable from frontmatter
2. **Manual / Eval**: `evals/evals.json` scenario "run-and-report"
   - Agent runs `npx playwright test` via Bash and writes `e2e-report.json`
   - Report schema matches FR-002 with summary + results[] (AC-US2-02)
   - Failed test entry has acId + status:"fail" + error message (AC-US2-03)
   - Report with `summary.failed > 0` blocks Gate 2a (AC-US2-04)
   - Report with `summary.failed === 0` passes Gate 2a (AC-US2-05)

**Implementation**:
1. Create directory `repositories/anton-abyzov/specweave/plugins/specweave/skills/e2e/`
2. Write `SKILL.md` with frontmatter from FR-003 / D-006
3. Section 1 -- Argument Parsing: detect `--generate`, `--run`, `--a11y` and extract `<increment-id>`
4. Section 2 -- Environment Validation: Playwright detection per D-007 (config + package search, fail messages per AC-US1-04, AC-US1-05)
5. Section 3 -- AC Extraction Algorithm: grep spec.md for `- [[ x]] \*\*AC-(US\d+-\d+)\*\*:`, group by US-ID per D-003
6. Section 4 -- Generate Mode: one `.spec.ts` per US, one `test()` per AC with AC-ID in title (D-002); journey grouping for sequential ACs (AC-US1-02); stub with TODO for ACs lacking Given/When/Then
7. Section 5 -- Run Mode: `npx playwright test --reporter=json`, parse output, write `e2e-report.json` to `.specweave/increments/<id>/reports/`; map results back to AC-IDs via test title regex; unmapped tests filed under `"UNMAPPED"`
8. Section 6 -- A11y Mode: inject `@axe-core/playwright` scan after each primary assertion; attach violations to per-AC `a11y` field; standalone mode groups by page URL
9. Section 7 -- Report Schema Reference: embed FR-002 JSON schema
10. Section 8 -- Edge Cases: no ACs found, ACs without GWT, duplicate AC-IDs, test timeout, `--a11y` with `--generate` warning

---

## User Story: US-003 - Accessibility Auditing via --a11y Flag

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 1 completed

### T-002: Verify --a11y coverage in SKILL.md Section 6

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** Section 6 of SKILL.md covers the `--a11y` mode
- **When** an agent invokes `sw:e2e --a11y <increment-id>`
- **Then** each test page is scanned with `@axe-core/playwright`, violations are attached to per-AC result entries, and zero violations produce `{ violations: [], passes: N }`

**Test Cases**:
1. **Manual / Eval**: `evals/evals.json` scenario "a11y-scan"
   - Violations attached to `results[].a11y` for the relevant AC (AC-US3-02)
   - Standalone mode groups violations by page URL under top-level `a11y` (AC-US3-03)
   - Zero violations produce `{ violations: [], passes: N }` (AC-US3-04)
   - **Coverage Target**: All 4 a11y ACs covered by eval assertions

**Implementation**:
1. Review T-001 Section 6 (A11y Mode) covers all four AC-US3-xx criteria
2. If any AC-US3-xx criterion is missing, edit SKILL.md Section 6 to add the missing instruction
3. Mark complete only after all four AC-US3-xx are explicitly addressed in SKILL.md

---

## User Story: US-004 - Team-Lead Testing Agent Integration

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 3 total, 1 completed

### T-003: Write evals/evals.json

**User Story**: US-004
**Satisfies ACs**: AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** `evals/evals.json` is placed at `plugins/specweave/skills/e2e/evals/evals.json`
- **When** the vskill eval framework reads it
- **Then** 4 scenarios validate generate, run, a11y, and no-playwright-detected modes

**Test Cases**:
1. **Structural**: File exists at correct path with valid JSON
   - 4 scenarios present: "generate-from-spec", "run-and-report", "a11y-scan", "no-playwright-detected"
   - Each scenario has `prompt`, `assertions[]`, and `tags[]` fields
   - **Coverage Target**: 100% of skill modes covered by at least one eval

**Implementation**:
1. Create directory `repositories/anton-abyzov/specweave/plugins/specweave/skills/e2e/evals/`
2. Write `evals.json` with 4 scenarios matching the eval design in plan.md:
   - Scenario 1 "generate-from-spec": reads spec.md, extracts ACs, creates per-US test files, checks Playwright config
   - Scenario 2 "run-and-report": runs Playwright, writes e2e-report.json with correct schema, maps AC-IDs
   - Scenario 3 "a11y-scan": includes axe-core scan, attaches violations to AC results, zero-violation format
   - Scenario 4 "no-playwright-detected": detects missing Playwright, outputs error, does NOT write files

---

### T-004: Fix testing.md references (testing:e2e -> sw:e2e)

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `testing:e2e` is replaced with `sw:e2e` in `team-lead/agents/testing.md`
- **When** a team-lead testing agent follows the testing.md instructions
- **Then** the agent invokes `Skill({ skill: "sw:e2e" })` (which exists) instead of the nonexistent `testing:e2e`

**Test Cases**:
1. **Grep check**: `grep "testing:e2e" repositories/anton-abyzov/specweave/plugins/specweave/skills/team-lead/agents/testing.md` returns no results
   - **Coverage Target**: 100% of `testing:e2e` references replaced

**Implementation**:
1. Edit `repositories/anton-abyzov/specweave/plugins/specweave/skills/team-lead/agents/testing.md`
2. Replace `Skill({ skill: "testing:e2e" })` with `Skill({ skill: "sw:e2e" })`
3. Update any surrounding comment text that references `testing:e2e` by name

---

### T-005: Clean ghost testing plugin cache and refresh plugins

**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** ghost `testing:e2e` references are removed from cache and plugins are refreshed
- **When** any agent invokes `sw:e2e`
- **Then** the skill activates with correct frontmatter and no stale `testing:e2e` references survive in cache

**Test Cases**:
1. **Grep check**: `grep -r "testing:e2e" ~/.claude/plugins/cache/` returns no results after refresh
2. **Structural**: `~/.claude/plugins/cache/specweave/sw/1.0.0/skills/e2e/SKILL.md` exists after refresh
   - **Coverage Target**: Cache matches source after refresh

**Implementation**:
1. Edit `/Users/antonabyzov/.claude/plugins/cache/specweave/sw/1.0.0/skills/team-lead/agents/testing.md` -- replace `testing:e2e` with `sw:e2e`
2. Edit `/Users/antonabyzov/.claude/plugins/cache/specweave/sw/1.0.0/skills/team-lead/SKILL.md` -- replace all `testing:e2e` references with `sw:e2e`
3. Edit `/Users/antonabyzov/.claude/plugins/cache/specweave/sw/1.0.0/skills/team-build/SKILL.md` -- replace `testing:e2e` reference with `sw:e2e`
4. Run `specweave refresh-plugins` from `/Users/antonabyzov/Projects/github/specweave-umb/` to sync source to cache
5. Verify: `grep -r "testing:e2e" ~/.claude/plugins/cache/` returns no output
6. Verify: `ls ~/.claude/plugins/cache/specweave/sw/1.0.0/skills/e2e/SKILL.md` succeeds
