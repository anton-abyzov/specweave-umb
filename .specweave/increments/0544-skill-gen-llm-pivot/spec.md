---
increment: 0544-skill-gen-llm-pivot
title: >-
  Skill-Gen LLM Pivot: Replace Keyword Matching with LLM-Based Pattern
  Extraction
type: feature
priority: P0
status: completed
created: 2026-03-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Skill-Gen LLM Pivot: Replace Keyword Matching with LLM-Based Pattern Extraction

## Problem Statement

SignalCollector relies on 10 hardcoded keyword lists (PATTERN_CATEGORIES) to detect patterns in living docs. This approach produces false positives from generic keyword matches, misses novel or domain-specific patterns, has no specificity (every match is a bare category label), is biased toward web development terminology, generates fake confidence scores based on increment count rather than evidence breadth, triggers DriftDetector false positives on common PascalCase words, duplicates utility code across modules, lacks runtime validation of the signal store, and imposes a brutal cold start requiring 3+ increment closures before any suggestions appear.

## Goals

- Replace keyword matching with a single LLM call that discovers project-specific patterns with meaningful descriptions
- Fix confidence scoring to reflect actual evidence breadth (distinct source files) rather than increment count
- Eliminate DriftDetector false positives and return structured results instead of console.warn
- Extract duplicated utility code, add Zod validation, sanitize LLM output, and cap evidence arrays
- Provide an instant seed mode that bootstraps signals from existing living docs in one pass

## User Stories

### US-001: LLM-Based Pattern Extraction (P0)
**Project**: specweave
**As a** developer using skill-gen
**I want** pattern detection powered by an LLM rather than hardcoded keyword lists
**So that** detected patterns are meaningful, specific to my project, and not limited to web-dev terminology

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a project with living docs, when SignalCollector runs, then it calls the LLM via the existing `analyzeStructured` abstraction with a batched prompt containing doc content up to ~50K tokens
- [x] **AC-US1-02**: Given a successful LLM response, when patterns are parsed, then each pattern contains `category` (string), `name` (string), `description` (string), and `evidence` (string[]) fields matching the structured schema
- [x] **AC-US1-03**: Given the LLM discovers patterns, when categories are returned, then categories are dynamic strings discovered by the LLM (the PATTERN_CATEGORIES constant and `| string` escape hatch are removed)
- [x] **AC-US1-04**: Given the LLM is unavailable (no API key, network error, or provider failure), when SignalCollector runs, then it logs a warning message and skips pattern detection without throwing an error
- [x] **AC-US1-05**: Given living docs exceed ~50K tokens, when batching, then docs are chunked into multiple LLM calls each within the token budget and results are merged

---

### US-002: Accurate Confidence Scoring (P1)
**Project**: specweave
**As a** developer reviewing skill suggestions
**I want** confidence scores that reflect how many distinct source files contain evidence for a pattern
**So that** I can trust that high-confidence suggestions are genuinely widespread in my codebase

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a SignalEntry, when it is created or updated, then it tracks source file paths in a `uniqueSourceFiles` field (string array, optional, defaults to `[]`)
- [x] **AC-US2-02**: Given a pattern is detected in file A across 3 separate increment closures, when confidence is calculated, then the confidence reflects 1 distinct source file (not 3 occurrences)
- [x] **AC-US2-03**: Given the same pattern appears in files A, B, and C, when confidence is calculated, then confidence equals `distinctSourceFiles.length / threshold` (capped at 1.0)
- [x] **AC-US2-04**: Given an existing signal store without `uniqueSourceFiles` fields, when loaded, then missing fields default to `[]` and the store loads without error

---

### US-003: DriftDetector Improvement (P1)
**Project**: specweave
**As a** developer using drift detection
**I want** fewer false positives and structured return values from DriftDetector
**So that** drift reports are actionable and callers can programmatically handle results

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given common PascalCase words (TypeScript, JavaScript, SpecWeave, ReactComponent, NextJs, NodeModule, ErrorBoundary, and 25+ others), when DriftDetector checks for stale references, then these words are excluded from drift detection
- [x] **AC-US3-02**: Given DriftDetector.check() is called, when drift is found, then it returns `DriftResult[]` where each entry has `skillFile` (string), `staleRefs` (string[]), and `validRefs` (string[])
- [x] **AC-US3-03**: Given DriftDetector.check() is called, when drift is found, then it does not call `console.warn` directly (the caller controls output)

---

### US-004: Code Quality and Security (P1)
**Project**: specweave
**As a** maintainer of skill-gen
**I want** shared utilities extracted, runtime validation added, and LLM output sanitized
**So that** the codebase is DRY, resilient to malformed data, and safe from injection

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `collectMarkdownFiles()` is duplicated in signal-collector.ts and drift-detector.ts, when refactored, then both modules import a single shared implementation from utils.ts
- [x] **AC-US4-02**: Given `loadStore()`/`saveStore()` is duplicated in signal-collector.ts and suggestion-engine.ts, when refactored, then both modules import a single shared implementation from utils.ts
- [x] **AC-US4-03**: Given a signal store JSON file is loaded, when parsed, then it is validated against a Zod schema and malformed stores cause a logged warning plus a fresh empty store (not a crash)
- [x] **AC-US4-04**: Given the LLM returns pattern names or descriptions, when stored, then control characters are stripped and strings are truncated to 200 characters
- [x] **AC-US4-05**: Given a signal's evidence array, when new evidence is added, then the array is capped at 20 entries (oldest entries are evicted)

---

### US-005: Instant Seed Mode (P1)
**Project**: specweave
**As a** developer adopting skill-gen on an existing project
**I want** to seed signal detection from all existing living docs in one pass
**So that** I get skill suggestions immediately without waiting for 3+ increment closures

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the `collectSeed()` method is called, when living docs exist, then all docs are scanned in a single batched LLM call and signals are created with `firstSeen` set to the current timestamp
- [x] **AC-US5-02**: Given signals already exist in the store, when `collectSeed()` runs, then existing signals are not duplicated (matched by category + name)
- [x] **AC-US5-03**: Given the `--seed` flag is passed to `/sw:skill-gen`, when invoked, then it calls `collectSeed()` instead of the regular incremental collection

---

### US-006: Real-World Validation Tests (P1)
**Project**: specweave
**As a** developer maintaining skill-gen
**I want** integration tests with realistic fixture docs and mocked LLM responses
**So that** regressions in the full pipeline are caught before release

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given a TypeScript project fixture (specweave-like docs), when the test runs with a mocked LLM response, then patterns like error-handling, testing, and architecture are detected
- [x] **AC-US6-02**: Given a Python ML project fixture, when the test runs with a mocked LLM response, then patterns like data-pipeline and model-training are detected (proving non-web-dev coverage)
- [x] **AC-US6-03**: Given an empty project fixture (no living docs), when the test runs, then the pipeline completes without error and returns zero signals with no LLM call made
- [x] **AC-US6-04**: Given any test scenario, when the full pipeline runs (signal detection, suggestion engine, store persistence), then the store contains the expected signals and suggestions

## Out of Scope

- Merging skill-gen signals with skill-memories system
- Pattern preview UI or interactive pattern selection
- Changing the SKILL.md user-facing interface or output format
- Real LLM integration tests in CI (manual/optional only)

## Technical Notes

### Dependencies
- Existing LLM abstraction: `src/core/llm/` (`loadLLMConfig`, `createProvider`, `analyzeStructured`)
- Zod ^4.1.13 (already in project dependencies)

### Constraints
- LLM batch prompt must stay within ~50K token budget per call
- `analyzeStructured` handles structured output validation; wrap in try/catch for resilience
- Backward-compatible: new `uniqueSourceFiles` field is optional with default `[]`

### Architecture Decisions
- **Batched summary over per-doc calls**: Concatenate all docs into one prompt (up to token budget) for a single Haiku call. Chunked fallback only when total exceeds budget. This minimizes latency and cost.
- **Skip + warn over degraded mode**: When LLM is unavailable, skip pattern detection entirely rather than falling back to keyword matching. Clean failure is better than misleading results.
- **analyzeStructured with schema**: Trust the provider's structured output capability but wrap in try/catch to handle malformed responses gracefully.

## Non-Functional Requirements

- **Performance**: Single LLM call completes pattern extraction for a typical project (< 50 living docs) in under 30 seconds
- **Security**: All LLM-returned strings are sanitized (control chars stripped, length capped at 200 chars) before persistence
- **Compatibility**: Existing signal stores load without migration; new fields default gracefully
- **Reliability**: LLM unavailability does not block increment closure or any other skill-gen functionality

## Edge Cases

- **No living docs**: `collectSeed()` and regular collection return zero signals, no LLM call made
- **LLM returns empty patterns array**: Treated as valid (no signals created), no warning
- **LLM returns duplicate patterns**: Deduplicate by category + name before storing
- **Malformed signal store on disk**: Zod validation fails, log warning, start with empty store
- **Token budget exceeded mid-doc**: Split at doc boundaries (never mid-document), chunk into separate calls
- **Evidence array already at cap**: Oldest entries evicted when new evidence arrives (FIFO)
- **`uniqueSourceFiles` contains duplicates**: Deduplicate on insert (use Set semantics)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| LLM returns low-quality or irrelevant patterns | 0.4 | 5 | 2.0 | Validate with integration tests using realistic fixtures; prompt engineering iteration |
| analyzeStructured schema mismatch with provider | 0.2 | 7 | 1.4 | try/catch wrapper, skip + warn on parse failure |
| Token budget estimation inaccurate | 0.3 | 4 | 1.2 | Conservative 50K limit with chunked fallback |
| Removing PATTERN_CATEGORIES breaks downstream consumers | 0.2 | 6 | 1.2 | Search codebase for all references before removal; categories become dynamic strings |

## Success Metrics

- **False positive rate**: < 10% of detected patterns are irrelevant (down from ~40% with keywords)
- **Domain coverage**: Integration tests prove detection of non-web patterns (ML, data pipelines)
- **Cold start elimination**: Seed mode produces actionable suggestions from first run
- **Code duplication**: Zero duplicated utility functions across skill-gen modules
- **Backward compatibility**: Existing signal stores load without error or migration
