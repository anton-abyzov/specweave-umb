# Architecture Plan: Shift Quality Left -- Per-Task Gates

## Increment: 0491-shift-quality-left-per-task-gates

## Overview

This increment modifies **SKILL.md markdown files only** (no runtime TypeScript). All changes live in `repositories/anton-abyzov/specweave/`. The architecture focuses on where new sections are inserted into existing SKILL.md files, how per-task review gates integrate with the sw:do workflow, the new sw:debug skill structure, and how anti-rationalization tables and fresh verification fit existing patterns.

## Architecture Decisions

### AD-1: Per-Task Review as Inline SKILL.md Sections (Not Hooks)

**Decision**: Implement per-task review gates as markdown instructions within sw:do's SKILL.md Step 6, not as PostToolUse hook scripts.

**Rationale**:
- The spec explicitly scopes this to "SKILL.md markdown only, no runtime code changes"
- Hook-based approaches (ADR-0200 Self-Validating Skills) require TypeScript runtime changes
- Inline instructions let the AI agent read and follow review protocol directly
- Config check (`quality.perTaskReview`) is a simple `jq` read from config.json, matching the existing `testMode` check pattern in Step 3

**Trade-off**: Relies on agent compliance with markdown instructions rather than enforced runtime gates. Acceptable because the entire skill system works this way -- every existing skill is "instructions the agent follows."

### AD-2: Phase 0 Prepends to Grill Without Renumbering

**Decision**: Insert a new "Phase 0: Spec Compliance Interrogation" before Phase 1 in sw:grill SKILL.md. Existing phases keep their numbers (1, 2, 3).

**Rationale**:
- The spec explicitly says: "Phase 0 must prepend to existing phases without renumbering"
- Phase 0 is semantically distinct -- it checks spec-level compliance before diving into code-level review
- Numbering it "Phase 0" makes the prerequisite relationship clear

### AD-3: sw:debug as Standalone Skill with Escalation Protocol

**Decision**: Create `plugins/specweave/skills/debug/SKILL.md` as a standalone skill invocable via `/sw:debug`. The skill is self-contained with 4 phases, anti-rationalization table, and an escalation protocol after 3 failed fix attempts.

**Rationale**:
- Follows existing skill directory pattern (one directory per skill, SKILL.md inside)
- Escalation protocol prevents infinite retry loops -- a pattern already established in tdd-cycle's "Failure Recovery" section
- The skill does not need hooks -- it is purely instructional markdown

### AD-4: Config Flag Under `quality` Namespace

**Decision**: The `quality.perTaskReview` config flag lives in a new `quality` namespace in config.json, separate from the existing `testing` namespace.

**Example config**:
```json
{
  "quality": {
    "perTaskReview": true
  }
}
```

**Rationale**:
- Avoids overloading `testing` namespace with non-test concerns
- Clear semantic separation: `testing.*` = test runner config, `quality.*` = review/compliance config
- Opt-in by default (absent = false), matching spec's backward compatibility requirement (AC-US1-04)

### AD-5: Anti-Rationalization Tables as Inline Markdown Tables

**Decision**: Embed anti-rationalization tables directly in each SKILL.md as standard markdown tables, not as external referenced files.

**Rationale**:
- Skills are read as single documents by AI agents -- external references add fragility
- Tables are small (8-10 rows) and contextually relevant to the skill they appear in
- Each skill gets its own tailored table (TDD excuses differ from grill excuses differ from debug excuses)

## Component Design

### Component 1: sw:do SKILL.md Modifications

**File**: `plugins/specweave/skills/do/SKILL.md`

**Changes**:

1. **Fresh Verification Iron Law** (added as preamble to Step 6)
   - Statement: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
   - Before marking any task `[x]`: run the task's test command and capture output
   - If no task-specific test: fall back to project-level test command
   - If test command fails: task stays `[ ]`, failure output presented for fixing

2. **New Step 6.5: Per-Task Review Gate** (inserted between Step 6 and Step 7)
   - Reads `quality.perTaskReview` from `.specweave/config.json` via `jq`
   - Checks for team-lead state (`~/.claude/teams/` directory presence); skips if active
   - After each task completion (inside Step 6 loop), before marking `[x]`:
     - Sub-review 1: Spec-compliance check (verify each relevant AC against implementation)
     - Sub-review 2: Code-quality focused diff review (review only the diff from this task)
   - If either review finds issues: fix before proceeding to next task
   - If config flag absent/false: skip entirely (backward compatible)

**Insertion points** (preserving existing structure):
- Step 6 gets an "Iron Law" preamble block before the task loop instructions
- New Step 6.5 is added after Step 6 and before Step 7: Handle Blockers
- Step 8 gets reinforced language referencing the iron law

### Component 2: sw:grill SKILL.md Modifications

**File**: `plugins/specweave/skills/grill/SKILL.md`

**Changes**:

1. **Phase 0: Spec Compliance Interrogation** (new section before Phase 1)
   - Always runs (not opt-in); executes before Phase 1: Context Gathering
   - Loads spec.md, extracts all ACs by pattern-matching `AC-US*-*`
   - For each AC: adversarial verification ("prove this AC is satisfied -- show the code")
   - Flags unsatisfied ACs with: AC ID, expected behavior, actual behavior, pass/fail
   - Detects scope creep: functionality not traceable to any AC
   - Results feed into grill-report.json `acCompliance` section

2. **grill-report.json schema extension**
   - Add `acCompliance` object:
     ```json
     {
       "acCompliance": {
         "totalACs": 0,
         "passed": 0,
         "failed": 0,
         "scopeCreep": [],
         "results": [
           { "acId": "AC-US1-01", "status": "pass|fail", "evidence": "..." }
         ]
       }
     }
     ```

3. **Anti-Rationalization Table** (new section after "Common Issues I Find")
   - 6+ entries: "Close enough to the spec" -> "Close enough ships bugs", "We can fix it later" -> rebuttal, "The tests pass" -> "Tests prove what was tested, not what should have been tested", plus 3+ more

**Insertion points**:
- Phase 0 goes in "Grill Process" section, right after the `## Grill Process` heading, before `### Phase 1: Context Gathering`
- Anti-rationalization table goes after `## Common Issues I Find` section, before `## Remember`
- Report format section gets the `acCompliance` field added to the JSON example

### Component 3: New sw:debug SKILL.md

**File**: `plugins/specweave/skills/debug/SKILL.md` (new file, new directory)

**Frontmatter**:
```yaml
---
description: Systematic 4-phase debugging with escalation protocol. Use when encountering difficult bugs, repeated test failures, or production issues. Invoked via "/sw:debug <bug-description>".
argument-hint: "<bug-description>"
allowed-tools: Read, Grep, Glob, Bash
context: fork
---
```

**4 Phases**:
1. **Phase 1: Root Cause Investigation** -- Systematically gather evidence: error messages, stack traces, recent git changes (`git log --oneline -10`), affected code paths, reproduce the bug
2. **Phase 2: Pattern Analysis** -- Identify recurring patterns, check if similar bugs exist in codebase history, formulate ranked hypotheses (most likely first)
3. **Phase 3: Hypothesis Testing** -- Test each hypothesis with minimal, targeted experiments. Capture results. If hypothesis disproved, move to next. Maximum 3 hypotheses before escalation
4. **Phase 4: Implementation** -- Implement the verified fix, write a regression test proving the bug is resolved, verify no other tests broken

**Escalation Protocol** (AC-US3-05):
- After 3 consecutive failed fix attempts: STOP
- Question the architectural assumptions
- Present findings to user with "I have tried X, Y, Z -- all failed. This suggests the problem may be structural."

**Red Flags** (AC-US3-07, trigger immediate escalation):
- "quick fix for now"
- "skip the test"
- "one more attempt"
- "it works on my machine"
- "probably not related"
- "let's ignore that for now"

**Anti-Rationalization Table** (AC-US3-06, 8+ entries):

| Excuse | Rebuttal | Why It Matters |
|--------|----------|----------------|
| "Quick fix for now" | Quick fixes become permanent. Fix it right or document the debt. | Shortcuts compound into systemic fragility |
| "Skip the test" | The test is proof the fix works. Without it, you are guessing. | Untested fixes have a 40%+ regression rate |
| "One more attempt" | If 3 attempts failed, the approach is wrong, not the execution. | Definition of insanity applies to debugging too |
| "It works on my machine" | Production is not your machine. Reproduce in the target environment. | Environment differences cause 30% of bugs |
| "Probably not related" | Investigate before dismissing. Assumptions kill debugging. | "Probably" is not evidence |
| "Let's ignore that for now" | If it is visible during debugging, it is relevant until proven otherwise. | Side effects are often the root cause |
| "The error message is misleading" | Error messages are data. Read them literally before interpreting. | Misread error messages waste hours |
| "I just need to restart" | Restarts mask the bug. Find why it broke. | Masked bugs return at the worst time |

**Estimated size**: ~200-250 lines.

### Component 4: sw:tdd-cycle SKILL.md Modifications

**File**: `plugins/specweave/skills/tdd-cycle/SKILL.md`

**Changes**:

1. **Anti-Rationalization Table** (new section after "Anti-Patterns to Avoid", before "Success Criteria")
   - 8+ entries with TDD-specific excuses and rebuttals

| Excuse | Rebuttal | Why It Matters |
|--------|----------|----------------|
| "I'll test after" | Tests written after implementation pass immediately, proving nothing | Post-hoc tests validate your code, not your logic |
| "This is too simple to test" | Simple code breaks at integration boundaries. Test the contract. | "Too simple" is the #1 excuse for untested bugs |
| "Just this once" | Every "just this once" becomes the new standard | Exceptions erode discipline permanently |
| "The test is too hard to write" | Hard-to-test code is a design smell. Refactor first. | Testability IS quality |
| "I know it works" | You know it works now. Tests prove it keeps working. | Confidence without evidence is recklessness |
| "Tests slow me down" | Tests slow you down now. Bugs slow you down forever. | A 2-minute test saves a 2-hour debug session |
| "I'll refactor the tests later" | Test tech debt compounds faster than code tech debt | Unreliable tests are worse than no tests |
| "The mock is too complex" | Complex mocks mean tightly coupled code. Decouple first. | Mock complexity mirrors design complexity |

**Insertion point**: After the "Anti-Patterns to Avoid" section (line ~188), before "Success Criteria" section.

### Component 5: Documentation Updates

**Files**:

1. **`docs-site/docs/reference/skills.md`** -- Add sw:debug to the Quality & Testing skills table with description and usage example
2. **`docs-site/docs/guides/youtube-tutorial-script.md`** -- Add a section covering quality-left features (per-task gates, adversarial grill Phase 0, sw:debug skill)
3. **`CHANGELOG.md`** -- Add version entry documenting all 5 features: per-task review gates, adversarial spec reviewer, sw:debug skill, fresh verification discipline, anti-rationalization tables

## Data Flow

```
config.json                    sw:do SKILL.md
  quality.perTaskReview ──────► Step 6.5 reads flag via jq
         │                         │
         │ (if true + no           ▼
         │  team-lead)    ┌─────────────────────┐
         │                │ Per-Task Review Gate │
         │                │  1. Spec-compliance  │
         │                │  2. Code-quality     │
         │                └─────────────────────┘
         │                         │
         │ (if false/absent        │ (issues found?)
         │  or team-lead active)   │
         ▼                         ▼
    Skip gate entirely       Fix before [x] mark

sw:grill SKILL.md
  Phase 0 (always) ──► acCompliance in grill-report.json
  Phase 1-3 (unchanged) ──► findings in grill-report.json
```

## File Change Summary

| File | Action | Lines Added |
|------|--------|-------------|
| `plugins/specweave/skills/do/SKILL.md` | Modify | ~70 |
| `plugins/specweave/skills/grill/SKILL.md` | Modify | ~90 |
| `plugins/specweave/skills/tdd-cycle/SKILL.md` | Modify | ~30 |
| `plugins/specweave/skills/debug/SKILL.md` | Create | ~220 |
| `docs-site/docs/reference/skills.md` | Modify | ~12 |
| `docs-site/docs/guides/youtube-tutorial-script.md` | Modify | ~25 |
| `CHANGELOG.md` | Modify | ~15 |

**Total**: 7 files, ~460 lines added, 0 lines of runtime code.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Per-task review adds latency to sw:do | Opt-in via config flag; skipped when absent (AC-US1-04) |
| Agent may rationalize skipping anti-rationalization tables | Tables are inline, prominent, and grill Phase 0 adversarially checks compliance |
| Phase 0 may duplicate per-task review findings | Defense-in-depth: per-task catches drift early, Phase 0 catches anything that slipped through |
| Team-lead mode conflict with per-task review | Explicit skip when team-lead detected (AC-US1-05) |
| Fresh verification may slow simple non-code tasks | Only applies to tasks with test blocks; documentation-only tasks naturally have no test command |

## Skill Chaining Recommendation

No domain skills needed. This increment is pure markdown editing within the SpecWeave plugin directory. No frontend, backend, or infrastructure skills are required. The implementer reads each target SKILL.md, inserts sections at the specified insertion points, creates the new debug skill, and updates documentation.
