# Tasks — 0335: Auto-Loading Update, Discovery Skill & --all Flag

## Phase 1: Auto-Loading Update (specweave)

### T-001: Split plugin registries in llm-plugin-detector.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given SPECWEAVE_PLUGINS → When split → Then sw-* stay, migrated become VSKILL_PLUGINS

### T-002: Update Haiku detection prompt
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given prompt → When buildDetectionPrompt() → Then uses `frontend` not `sw-frontend`

### T-003: Update installPluginViaCli() for dual-source install
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given vskill plugin → When installPluginViaCli('frontend') → Then calls --repo path

### T-004: Update user-prompt-submit.sh shell hook
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given `frontend` plugin → When install branch → Then uses vskill --repo

### T-005: Tests for auto-loading changes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given helpers → When tested → Then isVskillPlugin/isSpecWeavePlugin correct

## Phase 2: --all Flag (vskill)

### T-006: Add --all flag to vskill install command
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given --repo --all → When run → Then all plugins installed

### T-007: Tests for --all flag
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given test suite → When tests run → Then --all flow covered

## Phase 3: Discovery Skill (vskill)

### T-008: Create scout plugin with discovery skill
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given scout skill → When installed → Then SKILL.md instructs search + install

### T-009: Update vskill marketplace.json
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test**: Given marketplace.json → When updated → Then scout entry exists

### T-010: Update submit-vskill.sh
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test**: Given script → When --dry-run → Then scout skill listed
