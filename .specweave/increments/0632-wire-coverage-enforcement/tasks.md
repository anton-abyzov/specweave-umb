# Tasks: Wire Coverage Enforcement Chain

## Domain 1: Build Config

### T-001: Lower type defaults to 80/70/100
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**AC**: AC-US4-01, AC-US4-02
**Test Plan**: Given default config loaded → When reading coverageTargets → Then unit=80, integration=70, e2e=100, defaultCoverageTarget=80

### T-002: Wire vitest.config.ts to read from config.json
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03
**Test Plan**: Given .specweave/config.json with unit=80 → When vitest loads → Then thresholds are 80/80/80/80. Given no config.json → When vitest loads → Then fallback to 38/46/33/38

## Domain 2: Completion Validation

### T-003: Make completion-validator read coverage from config.json
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**AC**: AC-US2-01
**Test Plan**: Given config.json with coverageTargets → When validateCompletion runs → Then uses config targets instead of metadata single number

### T-004: Move coverage failures from warnings to errors (blocking)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**AC**: AC-US2-02, AC-US2-03
**Test Plan**: Given coverage 50% and target 80% → When validateCompletion → Then errors array contains coverage failure AND isValid=false. Given testMode='none' → When validateCompletion → Then coverage skipped, isValid not affected

## Domain 3: Quality Gates

### T-005: Wire qa-runner to pass config thresholds to QualityGateDecider
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02
**Test Plan**: Given config with qualityGates.thresholds → When runQA → Then decider uses config thresholds. Given no config thresholds → When runQA → Then decider uses DEFAULT_THRESHOLDS

### T-006: Add quality-gate-decider unit tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**AC**: AC-US3-01
**Test Plan**: Given custom thresholds → When QualityGateDecider.decide() → Then uses custom values for fail/concern assessment

## Domain 4: Verification

### T-007: Run full test suite to verify no regressions
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: all | **Status**: [x] completed
**Test Plan**: Given all changes applied → When `npx vitest run` → Then all tests pass
