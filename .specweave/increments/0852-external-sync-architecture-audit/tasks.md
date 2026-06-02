# Tasks: External Sync Architecture Audit and Hardening

### T-001: Map Analytics and External Sync Runtime
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan** (BDD):
- Given the SpecWeave repo and accepted sync ADRs -> When runtime entry points are inspected -> Then the report names actual command paths, provider paths, and architecture drift.

### T-002: Run Secret-Safe Credential Audit
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given repository files and Obsidian credential-note paths -> When token-like patterns are scanned -> Then only redacted file/variable findings are recorded.

### T-003: Fix Confirmed Sync Routing and Credential Defects
**User Story**: US-001, US-002
**Satisfies ACs**: AC-US1-03, AC-US2-02, AC-US3-01
**Status**: [x] completed

**Test Plan** (BDD):
- Given an umbrella spec with per-US `**Project**: vskill` and global GitHub defaults -> When `sync-progress` syncs GitHub ACs -> Then it routes to the child repo target.
- Given ADO is configured and only `AZURE_DEVOPS_PAT` is present -> When `sync-health` runs -> Then it calls the ADO health check with that PAT.

### T-004: Run Local Verification Gates
**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [x] completed

**Test Plan** (BDD):
- Given fixes are complete -> When build, unit, integration, e2e, coverage, and Playwright gates run -> Then pass/fail/skips are recorded with exact commands.

### T-005: Produce Architecture Report and Release Status
**User Story**: US-001, US-002, US-003
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-03, AC-US3-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given audit, fixes, and tests are complete -> When the report is written -> Then it is saved under `reports/`, contains no secrets, and states release/push/deploy status truthfully.
