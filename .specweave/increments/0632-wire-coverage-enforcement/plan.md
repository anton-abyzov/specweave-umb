# Implementation Plan: Wire Coverage Enforcement Chain

## Architecture Decision

Wire `config.json` as single source of truth for coverage thresholds. Three consumers read from it with graceful fallbacks.

## Components

### 1. vitest.config.ts — Dynamic threshold loader
- Add `loadCoverageThresholds()` using `fs.readFileSync('.specweave/config.json')`
- Map `coverageTargets.unit` to all 4 vitest metrics (lines/functions/branches/statements)
- Try/catch fallback to current hardcoded regression values
- Zero specweave core imports (keeps vitest config standalone)

### 2. completion-validator.ts — Blocking enforcement
- Read `testing.coverageTargets` from config.json via existing config utilities
- Replace single `coverageTarget` from metadata with per-level targets from config
- Move coverage failure from `warnings.push()` to `errors.push()` (blocking)
- Preserve skip conditions: `coverageTarget === 0`, `testMode === 'none'`

### 3. qa-runner.ts — Config-driven quality gates
- Load config at start of `runQA()`
- Pass `config.qualityGates?.thresholds ?? DEFAULT_THRESHOLDS` to `QualityGateDecider` constructor
- Constructor already accepts optional thresholds — just wire it through

### 4. types.ts — Lower defaults
- `defaultCoverageTarget`: 90 → 80
- `coverageTargets`: 95/90/100 → 80/70/100

## Files Modified

| File | Change |
|------|--------|
| `vitest.config.ts` | Add `loadCoverageThresholds()`, use in config |
| `src/core/increment/completion-validator.ts` | Config read + warnings→errors |
| `src/core/qa/qa-runner.ts` | Wire config thresholds to decider |
| `src/core/config/types.ts` | Lower default values |
| `tests/unit/core/qa/quality-gate-decider.test.ts` | NEW: custom threshold tests |

## Risk Mitigation

- vitest fallback ensures build doesn't break if config.json absent
- completion-validator skip conditions prevent false failures for `testMode: 'none'`
- quality-gate-decider keeps DEFAULT_THRESHOLDS as fallback
