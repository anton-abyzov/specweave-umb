# Tasks — 0362: Validate npm Package Ownership

**Total tasks**: 7 | **Completed**: 0

---

### T-001: Add npmPackageVerified to Prisma schema
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Priority**: P0
**Test**: Given Skill model → When migration runs → Then `npmPackageVerified Boolean @default(false)` exists

### T-002: Add normalizeNpmRepoUrl helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Priority**: P0
**Test**: Given npm registry URL formats (git+https, git://, SSH, github:) → When normalized → Then returns canonical GitHub URL

### T-003: Add npm registry fetcher and verification to enrichment
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [ ] pending
**Priority**: P0
**Test**: Given skill with unverified npmPackage → When enrichment runs → Then verifies ownership via registry

### T-004: Filter stats by npmPackageVerified
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [ ] pending
**Priority**: P0
**Test**: Given stats computation → When querying npm metrics → Then WHERE includes npmPackageVerified = true

### T-005: Add verification to admin bulk enrich
**User Story**: US-001 | **Satisfies ACs**: AC-US1-09 | **Status**: [ ] pending
**Priority**: P1
**Test**: Given admin enrich endpoint → When processing skills → Then verifies npm ownership

### T-006: Add tests for all verification scenarios
**User Story**: US-001 | **Satisfies ACs**: AC-US1-10 | **Status**: [ ] pending
**Priority**: P0
**Test**: repo-utils tests + enrichment tests + stats tests all pass

### T-007: Deploy and verify
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 through AC-US1-10 | **Status**: [ ] pending
**Priority**: P0
**Test**: Given deployed app → When checking stats → Then only verified npm packages shown
