# Tasks — 0371: Auto-populate npm packages

### T-001: Add extractNpmPackageName utility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given valid package.json with name "my-pkg" → When extractNpmPackageName called → Then returns "my-pkg"
**Test**: Given package.json with private:true → When called → Then returns null
**Test**: Given invalid npm name → When called → Then returns null
**Note**: Function already existed in `src/lib/scanner/dependency-analyzer.ts`. Added 214-char max length validation.

### T-002: Wire extraction into processSubmission and publishSkill
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test**: Given submission with package.json containing name → When processed → Then Skill record has npmPackage set
**Note**: Already wired in `process-submission.ts` — vendor, fast-approve, tier2-pass, and tier2-fallback paths all pass npmPackageName to publishSkill.

### T-003: Create npm-backfill admin endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given skills with null npmPackage → When POST /admin/npm-backfill → Then skills updated with extracted npm names

### T-004: Add unit tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: extractNpmPackageName test suite covers valid, scoped, private, missing, invalid cases (19 tests)
