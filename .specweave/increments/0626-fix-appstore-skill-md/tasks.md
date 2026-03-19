# Tasks: Fix appstore SKILL.md

## Phase 1: RED-LINE Fixes (broken functionality)

### T-001: Fix install commands
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test**: Given SKILL.md → When grepping `brew tap` → Then 0 matches. When grepping `asccli.sh/install` → Then URL is correct.

### T-002: Fix --app-id → --app globally
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given SKILL.md → When grepping `--app-id` → Then 0 matches.

### T-003: Fix --build-id → --build globally
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given SKILL.md → When grepping `--build-id` → Then 0 matches.

### T-004: Fix --file → --ipa in upload contexts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given SKILL.md → When grepping `--file` in upload/publish commands → Then all use `--ipa`.

### T-005: Fix asc apps → asc apps list, --workflow-name → --workflow-id
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given SKILL.md → When grepping `asc apps --output` → Then 0 matches. When grepping `--workflow-name` → Then 0 matches.

### T-006: Add $BUILD_ID and $VERSION_ID capture patterns
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given SKILL.md → When searching `BUILD_ID=` → Then capture exists before first `$BUILD_ID` usage. Same for `VERSION_ID=`.

## Phase 2: HIGH Priority (security/safety)

### T-007: Add --confirm to destructive operations
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given SKILL.md → When checking revoke, expire, submit, phased-release complete → Then all include `--confirm`.

### T-008: Add security warnings (certs, phased release, .p8, ASC_DEBUG, API role)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given SKILL.md → When searching "chmod 600" → Then .p8 warning exists. When searching "IRREVERSIBLE" → phased release warning exists.

### T-009: Add App Privacy and export compliance warnings
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07, AC-US3-08 | **Status**: [x] completed
**Test**: Given SKILL.md → When searching "App Privacy" → Then warning exists. When searching "export compliance" → Then note exists.

### T-010: Add rejection handling workflow
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given SKILL.md → When searching "REJECTION" → Then workflow section with check/fix/resubmit steps exists.

### T-011: Add rollback and emergency removal workflows
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given SKILL.md → When searching "ROLLBACK" → Then workflow exists. When searching "EMERGENCY" → Then removal workflow exists.

### T-012: Add vskill install section
**User Story**: US-005 | **Satisfies ACs**: AC-US5-08 | **Status**: [x] completed
**Test**: Given SKILL.md → When searching `vskill i` → Then install instructions exist with correct path.

## Phase 3: MEDIUM Priority (quality/completeness)

### T-013: Fix default menu, metadata namespace, version selection, draft check
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given SKILL.md → When counting menu options → Then 10 options exist.

### T-014: Fix related skills, split env vars, quote shell variables
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05, AC-US5-06, AC-US5-07 | **Status**: [x] completed
**Test**: Given SKILL.md → When checking Related Skills → Then no phantom skills. When checking env vars → Then split into secrets and config.
