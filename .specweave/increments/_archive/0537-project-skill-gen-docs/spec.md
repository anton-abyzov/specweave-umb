---
increment: 0537-project-skill-gen-docs
title: Project-Specific Skill Generation + Public Docs Cross-References
type: feature
priority: P1
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Project-Specific Skill Generation + Public Docs Cross-References

## Problem Statement

SpecWeave already extracts rich project knowledge through living docs analysis (module graphs, API surfaces, ADRs, skill-memories). However, this knowledge stays locked inside markdown files -- it is never codified into reusable AI coding instructions. Teams repeatedly make the same corrections across increments without those patterns ever becoming permanent skills. Meanwhile, the 26 existing skills have no cross-references to their public documentation, making discoverability poor.

## Goals

- Automatically detect recurring patterns from living docs output when increments close
- Surface non-intrusive suggestions when patterns qualify (3+ independent increments)
- Provide an on-demand skill (`/sw:skill-gen`) that generates project-local SKILL.md files using the official Anthropic skill-creator workflow
- Detect drift between generated skills and current codebase state
- Add `## Resources` sections to all 26 existing SKILL.md files linking to their verified-skill.com docs pages
- Create a new public docs page documenting the skill generation feature

## User Stories

### US-001: Signal Detection on Increment Closure
**Project**: specweave
**As a** SpecWeave user
**I want** recurring patterns to be silently detected when increments close
**So that** the system builds awareness of my project's conventions without interrupting my workflow

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given an increment is closing via `LifecycleHookDispatcher.onIncrementDone()`, when living docs output exists at `.specweave/docs/internal/`, then the signal collector reads module overviews, API surface files, ADR directory, and skill-memories files
- [x] **AC-US1-02**: Given the collector identifies a pattern, when no matching signal exists in `.specweave/state/skill-signals.json`, then a new signal entry is created with fields: id, pattern, category, description, incrementIds, firstSeen, lastSeen, confidence, evidence, suggested, declined, generated
- [x] **AC-US1-03**: Given a pattern matches an existing signal by category slug, when the increment ID is not already in `incrementIds`, then the existing signal is updated with the new increment ID appended and `lastSeen` refreshed
- [x] **AC-US1-04**: Given `.specweave/state/skill-signals.json` does not exist, when the collector runs for the first time, then the file is created with `{"version": "1.0", "signals": []}`
- [x] **AC-US1-05**: Given the signal collector encounters an error (missing files, parse failure), when the error occurs, then it logs a warning and exits without blocking increment closure

---

### US-002: Suggestion Engine
**Project**: specweave
**As a** SpecWeave user
**I want** to see a brief suggestion when a pattern has been observed across 3+ increments
**So that** I know when a recurring convention is ready to be codified as a skill

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `skillGen.suggest` is `true` in config and a signal has `incrementIds.length >= skillGen.minSignalCount` and `declined` is false and `generated` is false, when increment closure completes signal collection, then exactly one suggestion is printed to console
- [x] **AC-US2-02**: Given a qualifying suggestion exists, when it is printed, then the format is a single console log line containing the pattern name, increment count, and the command `/sw:skill-gen`
- [x] **AC-US2-03**: Given `skillGen.suggest` is `false` in config, when increment closure completes, then no suggestion is printed
- [x] **AC-US2-04**: Given multiple patterns qualify, when the suggestion engine runs, then only the pattern with the highest confidence score is suggested (max 1 per closure)
- [x] **AC-US2-05**: Given a suggestion is printed, when the signal is updated, then `suggested` is set to `true` on that signal entry

---

### US-003: Skill Generation Command
**Project**: specweave
**As a** SpecWeave user
**I want** an on-demand `/sw:skill-gen` skill that generates project-local SKILL.md files
**So that** I can codify detected patterns into permanent AI coding instructions

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the user invokes `/sw:skill-gen`, when signals exist in `skill-signals.json`, then all signals with `incrementIds.length >= minSignalCount` are displayed regardless of `declined` status
- [x] **AC-US3-02**: Given the user selects a pattern via natural language response, when generation starts, then the skill invokes the Anthropic skill-creator plugin at `~/.claude/plugins/cache/claude-plugins-official/skill-creator/` to build the SKILL.md with evals, benchmarks, and description optimization
- [x] **AC-US3-03**: Given skill generation completes, when the SKILL.md is written, then it is placed in `.claude/skills/` (project-local directory)
- [x] **AC-US3-04**: Given a skill is successfully generated, when the signal is updated, then `generated` is set to `true` on that signal entry
- [x] **AC-US3-05**: Given no signals meet the minimum count threshold, when `/sw:skill-gen` is invoked, then a message indicates no qualifying patterns were found

---

### US-004: Drift Detection
**Project**: specweave
**As a** SpecWeave user
**I want** existing project-local skills to be checked for staleness during living docs sync
**So that** I am warned when skills reference modules or APIs that no longer exist

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `.claude/skills/*.md` files exist and living docs sync runs via `living-docs-sync.ts`, when the drift detector compares skill content against current analysis output, then it identifies references to modules, files, or API surfaces that no longer appear in the analysis
- [x] **AC-US4-02**: Given drift is detected in one or more skills, when the check completes, then a console warning is printed listing each stale skill and what references are outdated
- [x] **AC-US4-03**: Given drift detection encounters an error, when the error occurs, then it logs the error and does not block living docs sync completion
- [x] **AC-US4-04**: Given no `.claude/skills/*.md` files exist, when living docs sync runs, then drift detection is skipped silently

---

### US-005: SkillGen Configuration Model
**Project**: specweave
**As a** SpecWeave user
**I want** skill generation behavior to be configurable via `config.json`
**So that** I can control detection, suggestion frequency, and declined patterns

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a fresh project, when `skillGen` is absent from `config.json`, then defaults are applied: `detection: "on-close"`, `suggest: true`, `minSignalCount: 3`, `declinedSuggestions: []`
- [x] **AC-US5-02**: Given `skillGen.minSignalCount` is set to 5, when signal collection runs, then only patterns observed in 5+ increments qualify for suggestion and display in `/sw:skill-gen`
- [x] **AC-US5-03**: Given a pattern ID is in `skillGen.declinedSuggestions`, when the suggestion engine evaluates that pattern, then it is permanently excluded from console suggestions but still visible in `/sw:skill-gen`
- [x] **AC-US5-04**: Given the `SkillGenConfig` type is added to `src/core/config/types.ts`, when TypeScript compilation runs, then there are zero type errors

---

### US-006: Public Documentation Page
**Project**: specweave
**As a** potential SpecWeave user
**I want** a docs page explaining the skill generation feature
**So that** I can understand how to use pattern detection and skill codification

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the file `docs-site/docs/skills/extensible/skill-generation.md` is created, when the Docusaurus site builds, then the page renders without errors at the expected URL path
- [x] **AC-US6-02**: Given the docs page exists, when `docs-site/sidebars.ts` is checked, then the page is registered in the Skills section sidebar
- [x] **AC-US6-03**: Given the docs page content, when reviewed, then it covers: signal detection lifecycle, configuration options, `/sw:skill-gen` usage, drift detection, and the signal schema
- [x] **AC-US6-04**: Given the project README, when the Skills section is checked, then skill-gen is mentioned with a link to the docs page

---

### US-007: Resources Section for Existing Skills
**Project**: specweave
**As a** SpecWeave skill user
**I want** each SKILL.md to link to its public documentation
**So that** I can quickly find detailed docs for any skill I am using

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given all 26 SKILL.md files in `plugins/specweave/skills/`, when a `## Resources` section is appended to each, then each section contains a link to the corresponding page on verified-skill.com
- [x] **AC-US7-02**: Given a SKILL.md already has a `## Resources` section, when the update runs, then existing content is preserved and not duplicated
- [x] **AC-US7-03**: Given the new skill-gen SKILL.md (from US-003), when it is generated, then its `## Resources` section links to the new docs page created in US-006

## Out of Scope

- Automatic skill generation without user confirmation (always requires `/sw:skill-gen` invocation)
- Cross-project signal aggregation across different SpecWeave workspaces
- Remote/cloud-based signal storage -- signals are local to the project
- Modifying existing skill behavior -- only adding `## Resources` sections
- Creating new per-skill docs pages for existing 26 skills -- linking to existing pages only
- Real-time pattern detection during implementation (only on increment closure)

## Non-Functional Requirements

- **Performance**: Signal collection adds less than 2 seconds to increment closure time
- **Compatibility**: Works on macOS, Linux, and Windows path formats; ESM-only with `.js` extensions on all imports
- **Reliability**: All new hooks are error-isolated -- failures in signal collection, suggestion, or drift detection never block the parent operation
- **Maintainability**: Signal schema is versioned (`version: "1.0"`) to allow future migrations

## Edge Cases

- **Empty living docs**: If `.specweave/docs/internal/` has no analysis output, signal collector exits silently with no signals created
- **Corrupted signals file**: If `skill-signals.json` cannot be parsed, collector backs up the file as `skill-signals.json.bak` and creates a fresh one
- **No skill-creator plugin**: If the Anthropic skill-creator plugin is not installed at the expected path, `/sw:skill-gen` prints an error message with installation instructions
- **Concurrent closures**: Last-write-wins for `skill-signals.json` -- acceptable because signal data is additive and re-detected on next closure
- **Skills referencing deleted modules**: Drift detection warns but does not modify or delete any skill files

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Signal collector produces false positives | 0.4 | 3 | 1.2 | Require minimum 3 increments + confidence threshold; user always confirms via `/sw:skill-gen` |
| Skill-creator plugin API changes | 0.2 | 6 | 1.2 | Wrap invocation in try/catch with version check; degrade gracefully |
| Large projects produce too many signals | 0.3 | 4 | 1.2 | Cap signals file at 100 entries, prune lowest-confidence when exceeded |
| Drift detection false warnings | 0.5 | 2 | 1.0 | Non-blocking warnings only; users learn to ignore or tune |

## Technical Notes

### Dependencies
- `src/core/hooks/LifecycleHookDispatcher.ts` -- signal collector + suggestion engine wired into `onIncrementDone()`
- `src/core/living-docs/living-docs-sync.ts` -- drift detector wired into sync pipeline
- `src/core/config/types.ts` -- `SkillGenConfig` interface
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/` -- Anthropic's official skill-creator plugin
- `.specweave/docs/internal/` -- living docs analysis markdown output (module overviews, API surfaces, ADRs, skill-memories)

### Constraints
- All TypeScript imports must use `.js` extensions (ESM with `--moduleResolution nodenext`)
- Signal matching uses semantic category slugs, not exact library name strings
- `/sw:skill-gen` is a Claude Code skill (SKILL.md), not a CLI command
- Docs site is Docusaurus 3, deployed via Cloudflare Pages on push to main

### Architecture Decisions
- Signal collector reads markdown output files from living docs, not in-memory types, to stay decoupled from the analyzer internals
- Last-write-wins concurrency for signals file -- simplicity over correctness given additive data nature
- Declined suggestions are permanent per pattern ID; users clear via config or bypass via `/sw:skill-gen` direct invocation
- Drift detection is warn-only and error-isolated to avoid disrupting the living docs sync pipeline

## Success Metrics

- Signal detection runs successfully on 95%+ of increment closures without errors
- At least 1 skill suggestion surfaces within the first 10 increment closures on a project with recurring patterns
- Generated SKILL.md files pass the skill-creator's own eval/benchmark suite
- All 26 existing SKILL.md files have `## Resources` sections linking to verified-skill.com
- New docs page is accessible and renders correctly on verified-skill.com
