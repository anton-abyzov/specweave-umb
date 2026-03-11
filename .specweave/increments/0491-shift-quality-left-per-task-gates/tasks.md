---
increment: 0491-shift-quality-left-per-task-gates
title: "Shift Quality Left — Per-Task Gates"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005]
  US-004: [T-006]
  US-005: [T-007, T-008]
  US-006: [T-009]
total_tasks: 9
completed_tasks: 9
---

# Tasks: Shift Quality Left — Per-Task Gates

## User Story: US-001 - Per-Task Review Gates in sw:do

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 2 completed

---

### T-001: Add Fresh Verification Iron Law to sw:do Step 6

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the sw:do SKILL.md Step 6 section is read
- **When** I inspect the section for completion gating instructions
- **Then** it contains the explicit statement "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE", instructions to run the task's test command before marking [x], fallback to project-level tests when no task test exists, and a rule that a failed test keeps the task marked [ ]

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/do/SKILL.md`
   - Verify Step 6 contains the literal string "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
   - Verify Step 6 instructs running the task's test command before marking [x]
   - Verify Step 6 describes fallback to project-level test command when no task-specific test exists
   - Verify Step 6 states that a failing test command keeps the task at [ ]
   - **Coverage Target**: 100% of iron law statements present

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/plugins/specweave/skills/do/SKILL.md` to locate Step 6
2. Insert an "Iron Law" preamble block at the start of Step 6 with the required statements
3. Ensure the language covers: run task test command → capture output → fail keeps task [ ] → project-level fallback when no test block

---

### T-002: Add Per-Task Review Gate (Step 6.5) to sw:do

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the sw:do SKILL.md is read after modifications
- **When** I inspect the section between Step 6 and Step 7
- **Then** a new Step 6.5 exists with: a `jq` command reading `quality.perTaskReview` from config.json, a team-lead detection check that skips the gate if active, spec-compliance sub-review instructions, code-quality diff review instructions, a fix-before-proceed rule, and a skip clause when config flag is absent or false

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/do/SKILL.md`
   - Verify a "Step 6.5" or equivalent heading exists between Step 6 and Step 7
   - Verify it references `quality.perTaskReview` config flag read via `jq` from `.specweave/config.json`
   - Verify it includes team-lead state detection with explicit skip clause (AC-US1-05)
   - Verify it describes Sub-review 1: spec-compliance per-AC check (AC-US1-01, AC-US1-02)
   - Verify it describes Sub-review 2: code-quality focused diff review (AC-US1-01, AC-US1-03)
   - Verify both reviews must pass before the implementer proceeds to the next task
   - Verify absent/false flag skips the gate entirely (AC-US1-04)
   - **Coverage Target**: 100% of gate logic statements present

**Implementation**:
1. After the Step 6 Iron Law block (added in T-001), insert a new "### Step 6.5: Per-Task Review Gate" section
2. Include: `jq -r '.quality.perTaskReview // false' .specweave/config.json` check
3. Include team-lead detection: check `~/.claude/teams/` directory existence; skip gate if directory has entries
4. Describe Sub-review 1: Spec-compliance — verify each relevant AC against the implementation diff
5. Describe Sub-review 2: Code-quality — focused review of only this task's diff
6. State: if either review finds issues, fix before marking [x] and before moving to next task
7. State: if flag is absent or false, skip the entire gate (backward compatible)

---

## User Story: US-002 - Adversarial Spec Reviewer in sw:grill

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 2 completed

---

### T-003: Add Phase 0 (Spec Compliance Interrogation) to sw:grill

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the sw:grill SKILL.md is read after modifications
- **When** I inspect the Grill Process section
- **Then** a "Phase 0: Spec Compliance Interrogation" section appears before Phase 1 (Context Gathering), is described as always-runs without opt-in, and contains: instructions to load spec.md, extract AC-US*-* IDs, run adversarial per-AC verification using "prove this AC is satisfied" framing, report findings with AC ID + expected behavior + actual behavior + pass/fail, detect scope creep, and reference acCompliance output

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/grill/SKILL.md`
   - Verify "Phase 0" heading exists before "Phase 1: Context Gathering" (AC-US2-05)
   - Verify Phase 0 contains no opt-in condition — it always runs (AC-US2-05)
   - Verify Phase 0 instructs loading spec.md and extracting AC-IDs by pattern `AC-US*-*` (AC-US2-01)
   - Verify adversarial framing "prove this AC is satisfied" or equivalent is present (AC-US2-01)
   - Verify finding format specifies: AC ID, expected behavior, actual behavior, pass/fail status (AC-US2-02)
   - Verify scope creep detection (functionality not traceable to any AC) is described (AC-US2-03)
   - Verify `acCompliance` output reference is present (links to T-004)
   - **Coverage Target**: 100% of Phase 0 required elements present

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/plugins/specweave/skills/grill/SKILL.md`
2. Locate the `## Grill Process` heading and the `### Phase 1: Context Gathering` line
3. Insert `### Phase 0: Spec Compliance Interrogation` section immediately before Phase 1
4. Write instructions: load spec.md → extract all AC-IDs matching `AC-US*-*` → for each AC run adversarial check
5. Write finding format: "AC ID | Expected | Actual | Status: pass/fail"
6. Write scope creep detection: flag any implementation functionality not traceable to a spec AC
7. State Phase 0 always runs before Phase 1 and is not opt-in

---

### T-004: Extend grill-report.json Schema with acCompliance Section

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the sw:grill SKILL.md is read after modifications
- **When** I inspect the report format / output schema section
- **Then** the grill-report.json example includes an `acCompliance` object with fields: `totalACs` (number), `passed` (number), `failed` (number), `scopeCreep` (array), and `results` (array of objects each with `acId`, `status`, `evidence` fields)

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/grill/SKILL.md`
   - Verify the grill-report.json JSON example contains an `acCompliance` key (AC-US2-04)
   - Verify `acCompliance.totalACs` is present as a numeric field
   - Verify `acCompliance.passed` is present as a numeric field
   - Verify `acCompliance.failed` is present as a numeric field
   - Verify `acCompliance.scopeCreep` is shown as an array
   - Verify `acCompliance.results` is shown as an array with entries containing `acId`, `status`, `evidence`
   - **Coverage Target**: 100% of schema fields documented

**Implementation**:
1. Locate the grill-report.json schema or example section in grill SKILL.md
2. Add `acCompliance` object to the JSON example with all required fields
3. Add a comment or description clarifying `status` values: "pass" or "fail"
4. Ensure the example shows at least one sample entry in `results` array

---

## User Story: US-003 - Systematic Debugging Skill

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Tasks**: 1 total, 1 completed

---

### T-005: Create sw:debug SKILL.md with 4-Phase Debugging Methodology

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Status**: [x] completed

**Test Plan**:
- **Given** a new file `plugins/specweave/skills/debug/SKILL.md` is created
- **When** I read the file
- **Then** it contains valid YAML frontmatter, 4 numbered phases covering evidence gathering / pattern analysis / hypothesis testing / fix implementation, an escalation protocol triggered after 3 failed fix attempts, a red flags list with the 4 minimum triggers, and an anti-rationalization table with 8 or more rows

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/debug/SKILL.md`
   - Verify YAML frontmatter contains `description`, `argument-hint`, `allowed-tools`, `context: fork` fields
   - Verify "Phase 1: Root Cause Investigation" section mentions error messages, stack traces, recent git changes, code paths, and reproduction (AC-US3-01)
   - Verify "Phase 2: Pattern Analysis" section mentions recurring patterns and hypothesis formulation (AC-US3-02)
   - Verify "Phase 3: Hypothesis Testing" section specifies a maximum of 3 hypotheses before escalation (AC-US3-03)
   - Verify "Phase 4: Implementation" section requires writing a regression test proving the bug is resolved (AC-US3-04)
   - Verify escalation protocol section states: after 3 consecutive failed fix attempts, STOP and present findings to user (AC-US3-05)
   - Verify red flags list includes at minimum: "quick fix for now", "skip the test", "one more attempt", "it works on my machine" (AC-US3-07)
   - Verify anti-rationalization table has 8 or more rows with excuse/rebuttal/why columns (AC-US3-06)
   - **Coverage Target**: 100% of AC-US3-01 through AC-US3-07 elements present

**Implementation**:
1. Create directory `repositories/anton-abyzov/specweave/plugins/specweave/skills/debug/`
2. Create `SKILL.md` with YAML frontmatter:
   - `description`: Systematic 4-phase debugging with escalation protocol
   - `argument-hint`: `<bug-description>`
   - `allowed-tools`: Read, Grep, Glob, Bash
   - `context`: fork
3. Write Phase 1: Root Cause Investigation — gather error messages, stack traces, run `git log --oneline -10`, identify affected code paths, reproduce the bug
4. Write Phase 2: Pattern Analysis — identify recurring patterns, check similar bugs in history, formulate ranked hypotheses (most likely first)
5. Write Phase 3: Hypothesis Testing — test each hypothesis with minimal targeted experiments, capture results, maximum 3 hypotheses before escalation
6. Write Phase 4: Implementation — implement the verified fix, write regression test, confirm no other tests broken
7. Write Escalation Protocol: after 3 failed fix attempts STOP — present "I have tried X, Y, Z — all failed" to user and question architectural assumptions
8. Write Red Flags section: "quick fix for now", "skip the test", "one more attempt", "it works on my machine", "probably not related", "let's ignore that for now" — each triggers immediate escalation
9. Write Anti-Rationalization Table (8 rows) matching plan.md Component 3 design

---

## User Story: US-004 - Fresh Verification Discipline in sw:do

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 1 total, 1 completed

**Note**: AC-US4-01 through AC-US4-03 are covered by T-001 (Iron Law in Step 6). This task validates that AC-US4-04 is explicitly satisfied (verbatim iron law text) and that all four ACs are traceable in the final file.

---

### T-006: Verify Iron Law Statement Completeness in sw:do

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** T-001 has been completed and sw:do SKILL.md is read
- **When** I search for the iron law statement and related instructions
- **Then** the exact phrase "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE" is present, the task-specific test run is described (AC-US4-01), the project-level fallback is described (AC-US4-02), and a failing test keeps the task at [ ] (AC-US4-03)

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/do/SKILL.md` after T-001
   - Verify exact phrase "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE" is present (AC-US4-04)
   - Verify instruction to run task's `**Test**:` block command and capture output before marking [x] (AC-US4-01)
   - Verify instruction: if no `**Test**:` block, run project-level test command as fallback (AC-US4-02)
   - Verify instruction: if test fails, task stays [ ] and failure output is presented (AC-US4-03)
   - **Coverage Target**: 100% of iron law elements explicitly stated

**Implementation**:
1. Read the sw:do SKILL.md after T-001 is complete
2. If the exact phrase "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE" is not verbatim present, edit the Iron Law block in Step 6 to include it
3. Confirm all four AC-US4 conditions are explicitly covered by the Iron Law block
4. Add any missing coverage to the Step 6 Iron Law block as needed

---

## User Story: US-005 - Anti-Rationalization Tables

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 2 total, 2 completed

---

### T-007: Add Anti-Rationalization Table to sw:tdd-cycle SKILL.md

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] completed

**Test Plan**:
- **Given** sw:tdd-cycle SKILL.md is read after modification
- **When** I inspect the section after "Anti-Patterns to Avoid" and before "Success Criteria"
- **Then** an anti-rationalization table is present with 8 or more rows including at minimum: "I'll test after" with rebuttal "Tests written after implementation pass immediately, proving nothing", "This is too simple to test" with a rebuttal, and "Just this once" with a rebuttal

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/tdd-cycle/SKILL.md`
   - Verify an anti-rationalization section (markdown table or structured list) exists after "Anti-Patterns to Avoid" (AC-US5-01)
   - Verify the section has 8 or more excuse/rebuttal entries (AC-US5-01)
   - Verify "I'll test after" entry with rebuttal "Tests written after implementation pass immediately, proving nothing" (AC-US5-02)
   - Verify "This is too simple to test" entry with a rebuttal (AC-US5-02)
   - Verify "Just this once" entry with a rebuttal (AC-US5-02)
   - **Coverage Target**: 100% of required entries present

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/plugins/specweave/skills/tdd-cycle/SKILL.md`
2. Locate insertion point: after `## Anti-Patterns to Avoid` section, before `## Success Criteria`
3. Insert a new `## Anti-Rationalization Table` section with a 3-column markdown table: `| Excuse | Rebuttal | Why It Matters |`
4. Add all 8 rows from plan.md Component 4:
   - "I'll test after" | "Tests written after implementation pass immediately, proving nothing" | ...
   - "This is too simple to test" | "Simple code breaks at integration boundaries..." | ...
   - "Just this once" | "Every 'just this once' becomes the new standard" | ...
   - Plus 5 additional rows from plan.md

---

### T-008: Add Anti-Rationalization Table to sw:grill SKILL.md

**User Story**: US-005
**Satisfies ACs**: AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** sw:grill SKILL.md is read after modification
- **When** I inspect the section after "Common Issues I Find" and before "Remember"
- **Then** an anti-rationalization table is present with 6 or more rows including at minimum: "Close enough to the spec" with rebuttal "Close enough ships bugs", "We can fix it later" with a rebuttal, and "The tests pass" with a rebuttal

**Test Cases**:
1. **Structural**: Read `plugins/specweave/skills/grill/SKILL.md`
   - Verify an anti-rationalization section exists after the `## Common Issues I Find` section (AC-US5-03)
   - Verify the section has 6 or more excuse/rebuttal entries (AC-US5-03)
   - Verify "Close enough to the spec" entry with rebuttal "Close enough ships bugs" (AC-US5-04)
   - Verify "We can fix it later" entry with a rebuttal (AC-US5-04)
   - Verify "The tests pass" entry with a rebuttal (AC-US5-04)
   - **Coverage Target**: 100% of required entries present

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/plugins/specweave/skills/grill/SKILL.md`
2. Locate insertion point: after `## Common Issues I Find` section (line ~311), before `## Remember` (line ~343)
3. Insert a new `## Anti-Rationalization Table` section with a 3-column markdown table
4. Add 6+ rows from plan.md Component 2:
   - "Close enough to the spec" | "Close enough ships bugs" | ...
   - "We can fix it later" | rebuttal | ...
   - "The tests pass" | "Tests prove what was tested, not what should have been tested" | ...
   - Plus 3+ additional rows from plan.md

---

## User Story: US-006 - Public Docs and Changelog Updates

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Tasks**: 1 total, 1 completed

---

### T-009: Update skills.md Reference, Tutorial Script, and CHANGELOG

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** the three documentation files are read after modification
- **When** I inspect each file for required new content
- **Then**: skills.md Quality & Testing section contains sw:debug with description and usage; youtube-tutorial-script.md contains a section on quality-left features covering per-task gates, adversarial grill Phase 0, and sw:debug; CHANGELOG.md contains an entry documenting all 5 features from this increment

**Test Cases**:
1. **Structural**: Read `docs-site/docs/reference/skills.md`
   - Verify sw:debug appears in the Quality & Testing section (AC-US6-01)
   - Verify sw:debug entry includes a description and usage guidance `/sw:debug <bug-description>` (AC-US6-01)

2. **Structural**: Read `docs-site/docs/guides/youtube-tutorial-script.md`
   - Verify a section on quality-left features is present (AC-US6-02)
   - Verify per-task review gates are mentioned (AC-US6-02)
   - Verify adversarial grill Phase 0 is mentioned (AC-US6-02)
   - Verify sw:debug skill is mentioned (AC-US6-02)

3. **Structural**: Read `CHANGELOG.md` in specweave repo root
   - Verify a new version entry exists with all 5 features: per-task review gates, adversarial spec reviewer, sw:debug skill, fresh verification discipline, anti-rationalization tables (AC-US6-03)
   - **Coverage Target**: 100% of required features documented across 3 files

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/docs-site/docs/reference/skills.md`, locate the Quality & Testing skills section, add sw:debug entry with description and `/sw:debug <bug-description>` usage example
2. Read `repositories/anton-abyzov/specweave/docs-site/docs/guides/youtube-tutorial-script.md`, add a new section covering quality-left features (per-task gates, grill Phase 0, sw:debug)
3. Read `repositories/anton-abyzov/specweave/CHANGELOG.md`, prepend a new version entry documenting all 5 features from this increment with brief descriptions
