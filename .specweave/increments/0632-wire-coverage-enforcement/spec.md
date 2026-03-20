---
increment: 0632-wire-coverage-enforcement
title: Wire coverage enforcement chain from config.json
type: feature
priority: P1
status: completed
---

# Spec: Wire Coverage Enforcement Chain

## Problem Statement

Coverage targets in `config.json` (`testing.coverageTargets`) are informational — three independent systems enforce their own hardcoded values instead:
1. **vitest.config.ts**: Hardcoded at 38%/46%/33%/38% (regression gates)
2. **completion-validator.ts**: Coverage failures go to `warnings` (non-blocking)
3. **quality-gate-decider.ts**: Hardcoded fail=60%, concerns=80%

This means changing `config.json` has no real effect on enforcement.

## User Stories

### US-001: Dynamic vitest coverage thresholds
**Project**: specweave

**As a** project maintainer
**I want** vitest.config.ts to read coverage thresholds from config.json
**So that** I can control build-gate thresholds from one place

**Acceptance Criteria**:
- [x] **AC-US1-01**: vitest.config.ts reads `testing.coverageTargets.unit` from `.specweave/config.json`
- [x] **AC-US1-02**: Falls back to hardcoded regression values (38/46/33/38) when config.json missing or invalid
- [x] **AC-US1-03**: No specweave core imports — uses plain `fs.readFileSync` + `JSON.parse`

### US-002: Blocking coverage enforcement in sw:done
**Project**: specweave

**As a** developer
**I want** coverage failures to block increment closure
**So that** low-coverage code cannot be shipped without explicit opt-out

**Acceptance Criteria**:
- [x] **AC-US2-01**: completion-validator reads `coverageTargets` from config.json (not just metadata single number)
- [x] **AC-US2-02**: Coverage below target produces an error (blocking), not a warning
- [x] **AC-US2-03**: Skip conditions preserved: `coverageTarget === 0` or `testMode === 'none'` bypasses enforcement

### US-003: Config-driven quality gate thresholds
**Project**: specweave

**As a** project maintainer
**I want** quality-gate-decider to read fail/concern thresholds from config
**So that** quality standards are configurable per project

**Acceptance Criteria**:
- [x] **AC-US3-01**: qa-runner.ts reads config and passes thresholds to QualityGateDecider constructor
- [x] **AC-US3-02**: Falls back to DEFAULT_THRESHOLDS when config has no quality gate overrides

### US-004: Lower type defaults to match smart defaults
**Project**: specweave

**As a** new user
**I want** default coverage targets to be achievable (80/70/100)
**So that** enforcement gates don't fail immediately on a fresh project

**Acceptance Criteria**:
- [x] **AC-US4-01**: `types.ts` defaultConfig coverageTargets changed from 95/90/100 to 80/70/100
- [x] **AC-US4-02**: `defaultCoverageTarget` changed from 90 to 80
