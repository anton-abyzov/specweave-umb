---
increment: 0537-project-skill-gen-docs
generated: 2026-03-15
---

# Tasks: 0537 — Project-Specific Skill Generation + Public Docs Cross-References

## US-005: SkillGen Configuration Model

### T-001: Add SkillGenConfig type to src/core/config/types.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04
**Status**: [ ] Not Started
**Test**: Given `SkillGenConfig` is added to `src/core/config/types.ts` and `skillGen?: SkillGenConfig` is added to `SpecWeaveConfig`, when `npx tsc --noEmit` runs, then exit code is 0 with zero type errors; given a consumer constructs `{}` as `SkillGenConfig`, then all fields are optional and defaults (`detection: "on-close"`, `suggest: true`, `minSignalCount: 3`, `declinedSuggestions: []`, `maxSignals: 100`) are documented in JSDoc

---

### T-002: Create shared types for signal-gen subsystem
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [ ] Not Started
**Test**: Given `src/core/skill-gen/types.ts` is imported in a test file, when `SignalEntry` and `SignalStore` objects are constructed matching the full schema (id, pattern, category, description, incrementIds, firstSeen, lastSeen, confidence, evidence, suggested, declined, generated), then TypeScript compilation reports zero errors

---

## US-001: Signal Detection on Increment Closure

### T-003: Implement SignalCollector — initialise signals file on first run
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] Not Started
**Test**: Given `.specweave/state/skill-signals.json` does not exist and `.specweave/docs/internal/` is empty, when `SignalCollector.collect(incrementId)` is called, then the file is created with content `{"version":"1.0","signals":[]}` and the function resolves without throwing

---

### T-004: Implement SignalCollector — read living docs and extract patterns
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [ ] Not Started
**Test**: Given `.specweave/docs/internal/` contains a module overview markdown file with repeated error-handling patterns, when `collect(incrementId)` runs, then at least one signal is created or updated with `evidence` containing a file path from that directory and `category` matching the detected pattern family

---

### T-005: Implement SignalCollector — create new signal entry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [ ] Not Started
**Test**: Given a pattern is detected that has no matching category in `skill-signals.json`, when `collect("0001-test")` runs, then a new `SignalEntry` is appended with `incrementIds: ["0001-test"]`, `confidence: 0.3`, `suggested: false`, `declined: false`, `generated: false`, and ISO `firstSeen`/`lastSeen` timestamps

---

### T-006: Implement SignalCollector — update existing signal entry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [ ] Not Started
**Test**: Given a signal with `category: "error-handling"` already exists in `skill-signals.json` with `incrementIds: ["0001-x"]`, when `collect("0002-y")` detects the same category pattern, then `incrementIds` becomes `["0001-x", "0002-y"]`, `lastSeen` is refreshed, and no duplicate entry is created

---

### T-007: Implement SignalCollector — error isolation and corrupted file recovery
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [ ] Not Started
**Test**: Given `skill-signals.json` contains invalid JSON, when `collect(incrementId)` is called, then the corrupt file is backed up as `skill-signals.json.bak`, a fresh `{"version":"1.0","signals":[]}` is written, and the function resolves without throwing; given living docs are unreadable (mocked to throw), when `collect()` is called, then a warning is logged and the function resolves without throwing

---

### T-008: Implement SignalCollector — cap at maxSignals, prune lowest-confidence
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Status**: [ ] Not Started
**Test**: Given `skill-signals.json` already has 100 entries (all with varying confidence) and `maxSignals` is 100, when `collect()` detects a new pattern with confidence 0.9, then the signals array length stays at 100 and the lowest-confidence existing entry is removed to make room for the new one

---

### T-009: Write unit tests for SignalCollector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given `src/core/skill-gen/__tests__/signal-collector.test.ts` covers all branches (init, create, update, corrupted file, missing docs, cap), when `npx vitest run` executes, then all test cases pass with ≥95% branch coverage reported

---

## US-002: Suggestion Engine

### T-010: Implement SuggestionEngine — qualifying filter and single suggestion output
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04, AC-US2-05
**Status**: [ ] Not Started
**Test**: Given `skillGen.suggest: true`, `minSignalCount: 3`, and two signals both with 4 increment IDs (confidence 0.8 and 0.5 respectively), when `SuggestionEngine.evaluate()` runs, then exactly one console line is printed containing the pattern name, increment count, and `/sw:skill-gen`, `suggested: true` is set only on the higher-confidence signal, and the lower-confidence signal is unchanged

---

### T-011: Implement SuggestionEngine — suggest=false suppresses output
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [ ] Not Started
**Test**: Given `skillGen.suggest: false` in config, when `SuggestionEngine.evaluate()` runs against a signals file with a qualifying pattern, then no console output is produced and no signal field is mutated

---

### T-012: Implement SuggestionEngine — declinedSuggestions config exclusion
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [ ] Not Started
**Test**: Given pattern ID `"error-handling-abc"` is in `skillGen.declinedSuggestions`, when `SuggestionEngine.evaluate()` runs with that pattern qualifying by count, then it is not printed as a suggestion; given a second pattern not in `declinedSuggestions` also qualifies, then only the second is suggested

---

### T-013: Write unit tests for SuggestionEngine
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] Not Started
**Test**: Given `src/core/skill-gen/__tests__/suggestion-engine.test.ts` covers all branches (suggest off, no qualifiers, single qualifier, multiple qualifiers, declinedSuggestions), when `npx vitest run` executes, then all test cases pass with ≥95% branch coverage

---

## US-003: Skill Generation Command

### T-014: Create plugins/specweave/skills/skill-gen/SKILL.md — display qualifying signals
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [ ] Not Started
**Test**: Given `skill-signals.json` has one signal with 4 increment IDs (declined: true), one with 4 increment IDs (declined: false), and one with 1 increment ID, when the user invokes `/sw:skill-gen`, then both 4-increment signals are displayed (declined status shown but pattern still listed), the 1-increment signal is absent, and if no signals meet the threshold a "no qualifying patterns found" message is shown

---

### T-015: Create skill-gen SKILL.md — delegate to skill-creator and write output
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given the skill-creator plugin exists at `~/.claude/plugins/cache/claude-plugins-official/skill-creator/` and the user selects a qualifying pattern, when skill-gen invokes skill-creator with pattern context (name, description, evidence, category), then the resulting SKILL.md is written to `.claude/skills/{pattern-slug}.md` and `generated: true` is set on the signal entry in `skill-signals.json`

---

### T-016: Create skill-gen SKILL.md — missing skill-creator error path
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [ ] Not Started
**Test**: Given the skill-creator plugin does not exist at the expected path, when the user invokes `/sw:skill-gen` and selects a pattern, then the skill prints an error message containing the missing path and installation instructions, and no SKILL.md is written to `.claude/skills/`

---

### T-017: Write evals.json for skill-gen skill
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [ ] Not Started
**Test**: Given `plugins/specweave/skills/skill-gen/evals/evals.json` is created following the pattern of `plugins/specweave/skills/e2e/evals/evals.json`, when the file is parsed as JSON, then it contains at least two eval scenarios (one for qualifying display, one for no-signals path) and all required schema fields are present without parse errors

---

## US-004: Drift Detection

### T-018: Implement DriftDetector — skip silently when no skills present
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [ ] Not Started
**Test**: Given `.claude/skills/` does not exist or is empty, when `DriftDetector.check()` runs, then no console output is produced and the function resolves without error

---

### T-019: Implement DriftDetector — detect stale module references and warn
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] Not Started
**Test**: Given `.claude/skills/my-skill.md` references module `OldModule` and `OldModule` does not appear in any current living docs analysis files, when `DriftDetector.check()` runs, then a console warning line is printed containing the skill filename and the stale reference `OldModule`; given a referenced module does still appear in analysis files, then no warning is printed for it

---

### T-020: Implement DriftDetector — error isolation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [ ] Not Started
**Test**: Given reading the living docs directory throws an error (mocked), when `DriftDetector.check()` is called, then the error is caught, a warning message is logged, and the function resolves without rethrowing

---

### T-021: Write unit tests for DriftDetector
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] Not Started
**Test**: Given `src/core/skill-gen/__tests__/drift-detector.test.ts` covers all branches (no skills, clean skills, stale refs, error path), when `npx vitest run` executes, then all test cases pass with ≥95% branch coverage

---

## Hook Wiring

### T-022: Wire signal collection + suggestion engine into LifecycleHookDispatcher.onIncrementDone()
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01
**Status**: [ ] Not Started
**Test**: Given a test calls `LifecycleHookDispatcher.onIncrementDone()` via `_bypassTestGuard` with living docs present in a temp directory, when the dispatcher runs, then `SignalCollector.collect` and `SuggestionEngine.evaluate` are each invoked once; given `SignalCollector.collect` throws, when the dispatcher runs, then the error does not propagate and increment closure completes normally

---

### T-023: Wire drift detection into LivingDocsSync.syncIncrement()
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [ ] Not Started
**Test**: Given a test stub of `LivingDocsSync.syncIncrement()` with `.claude/skills/` populated and living docs present, when `syncIncrement()` completes successfully, then `DriftDetector.check()` is called once; given `DriftDetector.check()` throws, when `syncIncrement()` runs, then the sync result is still returned successfully

---

## US-006: Public Documentation Page

### T-024: Create docs-site/docs/skills/extensible/skill-generation.md
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03
**Status**: [ ] Not Started
**Test**: Given `docs-site/docs/skills/extensible/skill-generation.md` is created with Docusaurus frontmatter and sections covering signal detection lifecycle, configuration options, `/sw:skill-gen` usage, drift detection, and the signal schema, when `npm run build` runs in `docs-site/`, then the build exits with code 0 and the output HTML contains all five topic headings

---

### T-025: Register skill-generation page in docs-site/sidebars.ts
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02
**Status**: [ ] Not Started
**Test**: Given `docs-site/sidebars.ts` is updated to include `"skills/extensible/skill-generation"` in the Skills section, when `npm run build` runs in `docs-site/`, then the build succeeds and the generated sidebar JSON includes the skill-generation entry

---

### T-026: Add skill-gen mention to project README
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [ ] Not Started
**Test**: Given `repositories/anton-abyzov/specweave/README.md` is updated with a reference in the Skills section, when the file is read, then it contains the text "skill-gen" and a link matching `https://verified-skill.com/docs/skills/extensible/skill-generation`

---

## US-007: Resources Sections for Existing Skills

### T-027: Audit all 26 SKILL.md files for existing ## Resources sections
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02
**Status**: [ ] Not Started
**Test**: Given all SKILL.md files under `plugins/specweave/skills/` are scanned, when the audit runs (grep or script), then a definitive list of files without `## Resources` is produced and no file with an existing section is marked for modification

---

### T-028: Add ## Resources sections to all 26 existing SKILL.md files
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02
**Status**: [ ] Not Started
**Test**: Given all 26 SKILL.md files are updated, when each file is read, then it contains exactly one `## Resources` section with a link matching `https://verified-skill.com/docs/skills/...` for that skill; given a file already had a `## Resources` section before the update, then after the update it contains that section exactly once with no duplication

---

### T-029: Add ## Resources section to skill-gen SKILL.md linking to new docs page
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03
**Status**: [ ] Not Started
**Test**: Given the skill-gen SKILL.md created in T-014/T-015 is complete, when the file is read, then it contains a `## Resources` section with a link to `https://verified-skill.com/docs/skills/extensible/skill-generation`

---

## Integration Verification

### T-030: Full pipeline integration test — signal detection through suggestion
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01
**Status**: [ ] Not Started
**Test**: Given a temporary project directory with mock living docs containing detectable patterns and `minSignalCount: 3`, when `onIncrementDone()` is called for three different increment IDs in sequence, then after the third call `skill-signals.json` has a signal with `incrementIds.length === 3` and a suggestion line was printed to console during that third call

---

### T-031: TypeScript compilation check — all new and modified files
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [ ] Not Started
**Test**: Given all new files in `src/core/skill-gen/` (types.ts, signal-collector.ts, suggestion-engine.ts, drift-detector.ts) and the updated `src/core/config/types.ts`, `LifecycleHookDispatcher.ts`, and `living-docs-sync.ts`, when `npx tsc --noEmit` runs from the specweave repo root, then exit code is 0 with zero type errors
