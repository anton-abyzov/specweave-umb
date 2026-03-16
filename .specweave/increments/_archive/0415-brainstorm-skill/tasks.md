---
increment: 0415-brainstorm-skill
title: "sw:brainstorm - Multi-Perspective Ideation Skill"
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005, T-006]
  US-003: [T-007, T-008, T-009, T-010, T-011, T-012]
---

## User Story: US-001 - Multi-Perspective Brainstorming Before Implementation

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, all completed

---

### T-001: [RED] Write tests for SKILL.md core (frontmatter, phases, depth, DOT, budgets)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the SKILL.md exists at `plugins/specweave/skills/brainstorm/SKILL.md`
- **When** unit tests are written to verify frontmatter, 5-phase flow, depth modes, DOT graph, and token budgets
- **Then** all tests initially run (RED phase - may pass since impl exists, verifying correctness)

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-skill-core.test.ts` (NEW FILE)
   - Frontmatter: context=fork, model=opus, description has keywords, argument-hint has --depth/--lens
   - Phases: all 5 phases defined in order (Frame, Diverge, Evaluate, Deepen, Output), each with description
   - Depth: quick=Frame+Evaluate, standard=Frame+Diverge+Evaluate+Output (default), deep=all 5
   - DOT graph: `digraph brainstorm` present, 7 nodes, depth-mode edge labels
   - Token budgets: Frame~500, Diverge~800, Evaluate~600, Deepen~1000, Output~400
   - **Coverage Target**: 90%

**Implementation**:
1. Create `tests/unit/skills/brainstorm-skill-core.test.ts`
2. Read SKILL.md via `fs.readFileSync` and parse frontmatter with regex
3. Write all test cases covering AC-US1-01 through AC-US1-05
4. Run tests: `npx vitest run tests/unit/skills/brainstorm-skill-core.test.ts`

---

### T-002: [GREEN] Verify and fix SKILL.md core tests pass

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** tests from T-001 exist
- **When** tests are run against existing SKILL.md
- **Then** all tests pass; if any fail, fix SKILL.md to match spec requirements

**Implementation**:
1. Run `npx vitest run tests/unit/skills/brainstorm-skill-core.test.ts`
2. Fix any failing tests by updating SKILL.md content
3. All tests green before proceeding

---

### T-003: [REFACTOR] Condense SKILL.md to ≤600 lines

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** SKILL.md is currently 721 lines (exceeds 600-line limit per ADR-0133)
- **When** progressive disclosure and concise formatting are applied
- **Then** SKILL.md is ≤600 lines while retaining all required content, and all T-001 tests still pass

**Implementation**:
1. Audit SKILL.md for verbose sections, redundant examples, excessive whitespace
2. Condense lens descriptions to 15-20 lines each (currently ~25-30)
3. Consolidate duplicate dispatch instructions across lenses
4. Remove redundant annotations and comments
5. Re-run `npx vitest run tests/unit/skills/brainstorm-skill-core.test.ts` to verify no regressions

---

## User Story: US-002 - Structured Ideation with Cognitive Frameworks

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, all completed

---

### T-004: [RED] Write tests for cognitive lenses and dispatch modes

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the SKILL.md defines 5 lenses with parallel/sequential dispatch
- **When** unit tests verify lens definitions and dispatch logic
- **Then** tests validate all lens facets, deep-mode parallel dispatch, and standard-mode sequential execution

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-lenses-dispatch.test.ts` (NEW FILE)
   - Lenses: exactly 5 defined (Default, Six Thinking Hats, SCAMPER, TRIZ, Adjacent Possible)
   - Six Hats: 6 facets (White, Red, Black, Yellow, Green, Blue)
   - SCAMPER: 7 operators (Substitute, Combine, Adapt, Modify, Put-to-other-uses, Eliminate, Reverse)
   - TRIZ: 3 facets (Inventive Principles, Contradiction Matrix, Ideal Final Result)
   - Adjacent Possible: single-facet lens
   - Default lens: used when no --lens flag
   - Deep mode: Agent() dispatch instructions for six-hats (6 agents) and SCAMPER (7 agents)
   - Deep mode: merge/collect step after parallel dispatch
   - Deep mode: per-facet output limit ("150 lines" or similar)
   - Standard mode: sequential execution, no Agent() calls
   - Quick mode: skips Diverge entirely
   - **Coverage Target**: 90%

**Implementation**:
1. Create `tests/unit/skills/brainstorm-lenses-dispatch.test.ts`
2. Parse SKILL.md content and test lens definitions and dispatch instructions
3. Run tests: `npx vitest run tests/unit/skills/brainstorm-lenses-dispatch.test.ts`

---

### T-005: [GREEN] Verify and fix lens/dispatch tests pass

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** tests from T-004 exist
- **When** tests are run against existing SKILL.md
- **Then** all tests pass; if any fail, fix SKILL.md content

**Implementation**:
1. Run `npx vitest run tests/unit/skills/brainstorm-lenses-dispatch.test.ts`
2. Fix any failing tests by updating SKILL.md lens or dispatch sections
3. All tests green before proceeding

---

### T-006: [REFACTOR] Verify SKILL.md total size after lens/dispatch fixes

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** SKILL.md may have been modified in T-005
- **When** line count is checked
- **Then** SKILL.md ≤600 lines (should already be fixed by T-003, verify no regression)

**Test Cases**:
1. **Unit**: Add to `tests/unit/skills/brainstorm-skill-core.test.ts`
   - testSkillMdUnder600Lines(): `lines.length <= 600`

**Implementation**:
1. Add line count test to brainstorm-skill-core.test.ts
2. Verify SKILL.md ≤600 lines
3. Run full test suite to confirm no regressions

---

## User Story: US-003 - Persistent Brainstorm Documents with Increment Handoff

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-08, AC-US3-09
**Tasks**: 6 total, all completed

---

### T-007: [RED] Write tests for SKILL.md persistence (output, state, handoff, keywords)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-09
**Status**: [x] completed

**Test Plan**:
- **Given** SKILL.md defines output doc structure, state file schema, handoff protocol, and auto-activation keywords
- **When** tests verify these sections exist with required content
- **Then** all persistence and handoff requirements are validated

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-persistence.test.ts` (NEW FILE)
   - Output: save path `.specweave/docs/brainstorms/` specified, doc sections listed (Problem Frame, Approaches, Evaluation Matrix, Deep Dives, Idea Tree, Next Steps), filename has date+slug placeholders
   - State: path `.specweave/state/brainstorm-` specified, schema fields (sessionId, topic, lens, depth, startedAt, phases), "check state file" resume instruction, per-facet status tracking
   - Handoff: `sw:increment` invocation pattern, trigger phrases ("proceed to increment"), `## Background` convention
   - Auto-activation: description contains "brainstorm", "explore ideas", "think through", "what if", "ideate", "diverge"
   - **Coverage Target**: 90%

**Implementation**:
1. Create `tests/unit/skills/brainstorm-persistence.test.ts`
2. Parse SKILL.md and verify output, state, handoff, and keyword sections
3. Run tests: `npx vitest run tests/unit/skills/brainstorm-persistence.test.ts`

---

### T-008: [GREEN] Verify and fix persistence tests pass

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-09
**Status**: [x] completed

**Test Plan**:
- **Given** tests from T-007 exist
- **When** tests are run against existing SKILL.md
- **Then** all tests pass; fix SKILL.md if any fail

**Implementation**:
1. Run `npx vitest run tests/unit/skills/brainstorm-persistence.test.ts`
2. Fix any failures by updating SKILL.md content
3. All tests green before proceeding

---

### T-009: [RED] Write tests for plugin metadata and source code changes

**User Story**: US-003
**Satisfies ACs**: AC-US3-04, AC-US3-05, AC-US3-06
**Status**: [x] completed

**Test Plan**:
- **Given** plugin PLUGIN.md files and TypeScript source files have been updated
- **When** tests verify the changes
- **Then** brainstorm is registered, old skill is deprecated, and source references are updated

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-integration.test.ts` (NEW FILE)
   - PLUGIN.md: brainstorm row exists in `plugins/specweave/PLUGIN.md` with "cognitive" keyword
   - Deprecation: `plugins/specweave-docs/PLUGIN.md` has "DEPRECATED" on spec-driven-brainstorming row, mentions `sw:brainstorm`
   - claude-md-generator: `src/adapters/claude-md-generator.ts` has 'brainstorm' (not 'spec-driven-brainstorming') in filter list and activation map
   - agents-md-generator: `src/adapters/agents-md-generator.ts` has 'brainstorm' in activation map
   - llm-plugin-detector: `src/core/lazy-loading/llm-plugin-detector.ts` does NOT contain 'docs:brainstorming'
   - generate-skills-index: `src/utils/generate-skills-index.ts` has 'brainstorm' in ORCHESTRATION category
   - **Coverage Target**: 90%

**Implementation**:
1. Create `tests/unit/skills/brainstorm-integration.test.ts`
2. Read each target file and assert required strings present/absent
3. Run tests: `npx vitest run tests/unit/skills/brainstorm-integration.test.ts`

---

### T-010: [GREEN] Verify and fix integration tests pass

**User Story**: US-003
**Satisfies ACs**: AC-US3-04, AC-US3-05, AC-US3-06
**Status**: [x] completed

**Test Plan**:
- **Given** tests from T-009 exist
- **When** tests are run against existing source files
- **Then** all tests pass; fix any source files if needed

**Implementation**:
1. Run `npx vitest run tests/unit/skills/brainstorm-integration.test.ts`
2. Fix any failures
3. All tests green

---

### T-011: [RED] Write tests for template and docs-site changes

**User Story**: US-003
**Satisfies ACs**: AC-US3-07, AC-US3-08
**Status**: [x] completed

**Test Plan**:
- **Given** CLAUDE.md template and docs-site files have been updated
- **When** tests verify brainstorm references
- **Then** template has brainstorm routing note, skills.md lists sw:brainstorm, planning.md has brainstorm step

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-docs.test.ts` (NEW FILE)
   - Template: `src/templates/CLAUDE.md.template` has `sw:brainstorm` routing note near "brainstorm" opt-out
   - Skills ref: `docs-site/docs/reference/skills.md` has `sw:brainstorm` in table, usage examples, 3+ activation keywords
   - Planning: `docs-site/docs/workflows/planning.md` references brainstorm as pre-increment step, marked optional
   - **Coverage Target**: 85%

**Implementation**:
1. Create `tests/unit/skills/brainstorm-docs.test.ts`
2. Read each file and verify required content
3. Run tests: `npx vitest run tests/unit/skills/brainstorm-docs.test.ts`

---

### T-012: [GREEN] Verify and fix docs tests pass

**User Story**: US-003
**Satisfies ACs**: AC-US3-07, AC-US3-08
**Status**: [x] completed

**Test Plan**:
- **Given** tests from T-011 exist
- **When** tests are run against existing docs files
- **Then** all tests pass; fix any docs if needed

**Implementation**:
1. Run `npx vitest run tests/unit/skills/brainstorm-docs.test.ts`
2. Fix any failures
3. All tests green
4. Run full test suite: `npx vitest run` to verify no regressions across all brainstorm test files
