# Implementation Plan: sw:e2e -- SpecWeave-Integrated Playwright E2E Skill

## Overview

This increment delivers a SpecWeave skill (SKILL.md markdown file) that bridges spec.md acceptance criteria and Playwright E2E tests. The skill generates test files, runs them, produces an AC-mapped `e2e-report.json`, and integrates with sw:done Gate 2a. A secondary deliverable updates the team-lead testing agent to reference `sw:e2e` instead of the nonexistent `testing:e2e`. There is no application code -- all deliverables are markdown instructions and JSON.

## Architecture

### Deliverable Map

```
repositories/anton-abyzov/specweave/plugins/specweave/skills/
  e2e/
    SKILL.md              <-- Primary deliverable (skill definition)
    evals/
      evals.json          <-- Eval test cases (3-4 scenarios)
  team-lead/
    agents/
      testing.md          <-- Fix: testing:e2e --> sw:e2e
```

### SKILL.md Internal Structure

The SKILL.md follows the established SpecWeave skill pattern (frontmatter + sections). It is a set of instructions for an AI agent, NOT executable code. The agent reading SKILL.md will use Bash, Read, Write, Edit, Grep, and Glob tools to perform the work.

```
SKILL.md
  |-- Frontmatter (description, argument-hint, allowed-tools, context, model)
  |-- Section 1: Argument Parsing (mode detection: --generate | --run | --a11y)
  |-- Section 2: Environment Validation (Playwright detection)
  |-- Section 3: AC Extraction Algorithm (spec.md parsing)
  |-- Section 4: Generate Mode (test file creation)
  |-- Section 5: Run Mode (Playwright execution + report writing)
  |-- Section 6: A11y Mode (axe-core integration)
  |-- Section 7: Report Schema Reference
  |-- Section 8: Edge Cases and Error Handling
```

### Component Boundaries

**SKILL.md** is the sole runtime artifact. It contains procedural instructions that an AI agent follows. The agent itself calls Bash to run Playwright, Read/Grep to parse spec.md, and Write/Edit to produce test files and reports.

**evals.json** validates that the skill produces correct outputs for representative inputs. It is consumed by the vskill eval framework, not by the skill itself.

**testing.md** (team-lead agent) is a configuration fix -- one line change from `testing:e2e` to `sw:e2e`.

## Key Design Decisions

### D-001: Skill as Markdown Instructions (Not Code)

**Decision**: The skill is a SKILL.md file containing step-by-step instructions for an AI agent, consistent with all other SpecWeave skills (grill, done, validate, tdd-cycle).

**Rationale**: SpecWeave skills are agent prompts, not executable programs. The agent uses tools (Bash, Read, Write) to perform actions. This matches ADR-0015 (plugin system uses native Claude Code format) and every existing skill in the repo.

**Rejected alternative**: Creating a TypeScript CLI command (`specweave e2e`). This would require build infrastructure changes and is unnecessary -- the agent can orchestrate Playwright via Bash directly.

### D-002: One Test File Per User Story

**Decision**: `--generate` creates one `.spec.ts` file per user story (e.g., `e2e/us-001.spec.ts`), with one `test()` block per AC.

**Rationale**:
- Maps cleanly to the AC-ID namespace (`AC-US1-01` lives in `us-001.spec.ts`)
- Keeps files focused and readable
- Allows running a single user story's tests in isolation
- Matches the pattern: each AC gets a `test('AC-US1-01: description', ...)` call

**Edge case**: When ACs form a natural journey (e.g., login then navigate), they are grouped into a single `test()` with AC-ID checkpoint comments, per AC-US1-02.

### D-003: AC Extraction via Regex on spec.md

**Decision**: Parse spec.md for lines matching `- [ ] **AC-USx-xx**: ...` or `- [x] **AC-USx-xx**: ...` using grep/regex. Extract AC-ID, Given/When/Then text, and parent US-ID.

**Algorithm**:
```
1. Read .specweave/increments/<id>/spec.md
2. grep for pattern: /- \[[ x]\] \*\*AC-(US\d+-\d+)\*\*:\s*(.*)/
3. For each match:
   a. AC-ID = capture group 1 (e.g., "US1-01")
   b. Full AC-ID = "AC-" + capture group 1 (e.g., "AC-US1-01")
   c. Text = capture group 2 (the Given/When/Then description)
   d. Parent US = derived from AC-ID prefix (US1 -> US-001)
4. Group by parent US-ID
5. Return structured list: { usId, acId, text, hasGWT }[]
```

**Rationale**: This is the same pattern used by sw:grill Phase 0 (line 62-63 of grill/SKILL.md: `grep -oE 'AC-US[0-9]+-[0-9]+'`), sw:done Gate 0, and the bidirectional traceability system (ADR-0009). Reusing the same regex ensures consistency.

**Edge cases**:
- No ACs found: exit with "No acceptance criteria found in spec.md"
- ACs without Given/When/Then: generate test stub with TODO comment
- Duplicate AC-IDs: warn, append `-dup1` suffix to test name

### D-004: e2e-report.json Schema

**Decision**: The report follows the schema defined in FR-002 of spec.md:

```
e2e-report.json
  incrementId       string     -- Increment ID
  timestamp         ISO-8601   -- When the run completed
  mode              enum       -- "run" | "generate" | "a11y"
  playwrightConfig  string     -- Path to playwright.config.ts used
  summary
    total           number     -- Total test count
    passed          number     -- Passed count
    failed          number     -- Failed count
    skipped         number     -- Skipped count
  results[]
    acId            string     -- AC-ID (e.g., "AC-US1-01")
    testFile        string     -- Relative path to test file
    status          enum       -- "pass" | "fail" | "skip"
    duration        number     -- Milliseconds
    error           string|null -- Failure message or null
    a11y            object|null -- Only present with --a11y flag
      violations    array      -- axe violation objects
      passes        number     -- Count of passed axe rules
  a11y              object|null -- Top-level, standalone a11y results
    violations      array
    passes          number
```

**Report location**: `.specweave/increments/<id>/reports/e2e-report.json`

**Rationale**: This schema is specified in spec.md FR-002 and referenced by AC-US2-02. The `results[]` array has one entry per AC, enabling direct AC-to-test-status mapping. The `a11y` field is optional (only populated with `--a11y`).

### D-005: Gate 2a Integration Strategy

**Decision**: The sw:done SKILL.md Gate 2a currently says "Detect playwright/cypress configs... If found, run them." The integration point is for Gate 2a to invoke `Skill({ skill: "sw:e2e", args: "--run <increment-id>" })` and then read `e2e-report.json` for pass/fail determination.

**How it works**:
1. Gate 2a detects Playwright config (existing behavior)
2. Instead of running `npx playwright test` directly, it invokes `sw:e2e --run <id>`
3. `sw:e2e --run` executes Playwright, parses results, writes `e2e-report.json`
4. Gate 2a reads `e2e-report.json`: if `summary.failed > 0`, block closure
5. If `e2e-report.json` is missing after invocation, Gate 2a fails with error

**Note**: The actual sw:done SKILL.md update to reference sw:e2e is OUT OF SCOPE for this increment per spec.md ("sw:done Gate 2a currently runs Playwright directly -- update to invoke sw:e2e --run instead" is listed in Technical Notes as context, but the spec's deliverables are limited to: SKILL.md, evals.json, and testing.md fix). However, the SKILL.md must be designed so that Gate 2a CAN consume its output. If the team decides to update sw:done in a follow-up increment, the contract is ready.

### D-006: Frontmatter Configuration

```yaml
---
description: Generate, run, and report Playwright E2E tests traced to spec.md acceptance criteria. Supports accessibility auditing via --a11y.
argument-hint: "--generate|--run|--a11y <increment-id>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
context: fork
model: sonnet
---
```

**Rationale**:
- `context: fork` -- matches grill skill pattern; E2E operations are long-running and should not pollute the caller's context
- `model: sonnet` -- test generation and report parsing do not require opus-level reasoning; sonnet is sufficient and more cost-effective
- `allowed-tools` -- Read/Grep/Glob for spec.md parsing, Bash for Playwright execution, Write/Edit for test file and report generation

### D-007: Playwright Detection Strategy

**Decision**: Before any operation, validate the environment:

```
1. Search for playwright.config.ts or playwright.config.js:
   - Project root
   - repositories/*/* (monorepo pattern)
   - packages/*/  (workspace pattern)

2. Search for @playwright/test in package.json:
   - Same locations as above

3. Decision matrix:
   Config found + Package found  --> Proceed (use found config path)
   Config missing + Package found --> FAIL: "Playwright installed but no config. Run npx playwright init"
   Config missing + Package missing --> FAIL: "Playwright not installed. Run npm init playwright@latest"
   Config found + Package missing --> Proceed with warning (global install)
```

**Rationale**: Matches FR-004 exactly. The search order accounts for monorepo structures common in SpecWeave umbrella projects.

## Implementation Phases

### Phase 1: SKILL.md Core (US-001, US-002, US-004)

Write the SKILL.md file with all sections. This is the bulk of the work:

1. Frontmatter per D-006
2. Argument parsing section (3 modes: `--generate`, `--run`, `--a11y`)
3. Playwright detection section per D-007
4. AC extraction algorithm per D-003
5. Generate mode: test file creation per D-002
6. Run mode: Playwright execution, result parsing, report writing per D-004
7. Edge cases section per spec.md Edge Cases

### Phase 2: Accessibility Extension (US-003)

Add the `--a11y` section to SKILL.md:

1. Instructions for injecting `@axe-core/playwright` scan after each test's primary assertion
2. Violation attachment to per-AC result entries
3. Standalone a11y mode (no specific AC context)
4. Report schema extension (a11y field)

### Phase 3: Integration Artifacts (US-004)

1. Create `evals/evals.json` with 4 eval scenarios
2. Update `team-lead/agents/testing.md` to reference `sw:e2e`

## Eval Design

The evals.json will contain 4 scenarios that validate the skill's core behaviors:

### Eval 1: "generate-from-spec" (US-001)

**Prompt**: "Generate E2E tests for increment 0042-auth-flow. The spec has 3 user stories with 8 ACs total."

**Assertions**:
- Reads spec.md from the increment path
- Extracts AC-IDs using regex
- Creates one test file per user story
- Each test title contains the AC-ID
- Checks for Playwright config before generating

### Eval 2: "run-and-report" (US-002)

**Prompt**: "Run E2E tests for increment 0042-auth-flow and produce the report."

**Assertions**:
- Runs `npx playwright test` via Bash
- Writes `e2e-report.json` to reports/ directory
- Report contains `summary` with pass/fail counts
- Report contains `results[]` with AC-ID mapping
- Failed tests include error messages

### Eval 3: "a11y-scan" (US-003)

**Prompt**: "Run E2E tests with accessibility auditing for increment 0042-auth-flow."

**Assertions**:
- Includes `@axe-core/playwright` scan instructions
- Violations attached to per-AC results under `a11y` field
- Top-level `a11y` field present in report
- Zero violations produce `{ violations: [], passes: N }`

### Eval 4: "no-playwright-detected" (Edge Case)

**Prompt**: "Generate E2E tests for increment 0099-new-feature."

**Assertions**:
- Detects missing Playwright config/package
- Outputs clear error message with installation instructions
- Does NOT generate test files
- Does NOT write e2e-report.json

## Testing Strategy

This is a skill (markdown instructions), not code. Testing is done via evals:

1. **evals.json** -- 4 scenarios with boolean assertions per the vskill eval framework pattern (matching github-sync evals structure)
2. **Manual validation** -- Invoke `sw:e2e --generate` and `sw:e2e --run` on a real increment with Playwright tests to verify end-to-end flow
3. **Gate 2a contract test** -- Verify that `e2e-report.json` written by `sw:e2e --run` is readable by sw:done's Gate 2a logic (report exists, summary.failed checked)

## Technical Challenges

### Challenge 1: Playwright Output Parsing

**Problem**: Playwright's JSON reporter output format varies by version and configuration. The skill must parse test results and map them back to AC-IDs embedded in test titles.

**Solution**: Use Playwright's built-in `--reporter=json` flag which outputs a stable JSON format. Parse the JSON output to extract test titles (which contain AC-IDs), status, duration, and errors. The AC-ID is extracted from the test title using the same regex pattern used during generation.

**Risk**: Low. Playwright's JSON reporter format has been stable since v1.30+.

### Challenge 2: Test File Path Discovery

**Problem**: When running tests, the skill needs to know where generated test files are located. The project may have a custom `testDir` in playwright.config.ts.

**Solution**: Read `playwright.config.ts` to extract the `testDir` setting. Default to `e2e/` if not specified. The generate mode writes to this directory; the run mode reads from it.

**Risk**: Low. The skill controls both generation and execution paths.

### Challenge 3: AC-ID to Test Mapping on Run

**Problem**: When running pre-existing tests (not generated by the skill), test titles may not contain AC-IDs, making AC mapping impossible.

**Solution**: The skill only maps ACs it can find in test titles. Tests without AC-IDs in their titles are reported under a synthetic `"UNMAPPED"` AC-ID in the results array. The report's `summary` counts include all tests regardless of mapping.

**Risk**: Medium. Users who write tests manually may not include AC-IDs. The SKILL.md should document the naming convention requirement.

## Dependencies

None. This increment creates new files only. The testing.md fix is a single-line edit to an existing file.

## Relevant ADRs

- **ADR-0009**: Bidirectional Task-AC Traceability Links -- the AC extraction algorithm reuses the same traceability patterns
- **ADR-0015**: Hybrid Plugin System -- skill placement follows native Claude Code plugin structure
- **ADR-0021**: PM Agent Enforcement -- pattern for CLI-based validation in agent workflows (analogous to Playwright detection)
