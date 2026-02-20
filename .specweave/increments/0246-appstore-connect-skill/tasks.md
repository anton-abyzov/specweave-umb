# Tasks: 0246 App Store Connect CLI Skill

### T-001: Create SKILL.md with Step 0 (Auth & App Discovery)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given `asc` not installed → When skill runs → Then guides user through `brew install asc`
**Test**: Given `asc auth status` fails → When skill runs → Then walks through `asc auth login` setup

### T-002: Implement TestFlight mode (--testflight)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given valid IPA path → When `--testflight` mode → Then uploads build and distributes to beta groups
**Test**: Given build processing → When waiting → Then polls status until ready

### T-003: Implement Submit mode (--submit)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given ready build → When `--submit` mode → Then validates, creates version, submits for review

### T-004: Implement Status mode (--status)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given submitted app → When `--status` mode → Then shows current review status

### T-005: Implement Validate mode (--validate)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given app with metadata → When `--validate` mode → Then runs `asc validate --strict` and reports results

### T-006: Implement Metadata mode (--metadata)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given locale and description → When `--metadata` mode → Then updates App Store localizations

### T-007: Implement Builds mode (--builds)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given app with builds → When `--builds` mode → Then lists builds with version/platform filtering

### T-008: Implement Signing mode (--signing)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given app bundle ID → When `--signing` mode → Then fetches/creates certificates and profiles

### T-009: Implement Analytics mode (--analytics)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**Test**: Given valid auth → When `--analytics` mode → Then downloads sales reports

### T-010: Add Xcode Cloud and Notarization sections
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] completed
**Test**: Given Xcode Cloud workflow → When triggering → Then starts build and waits for completion

### T-011: Add Workflow automation section
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03 | **Status**: [x] completed
**Test**: Given `.asc/workflow.json` exists → When `asc workflow run` → Then executes multi-step sequence

### T-012: Update PLUGIN.md with appstore skill entry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given PLUGIN.md → When reading skills table → Then appstore skill is listed
