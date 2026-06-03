# Tasks: 0871 Plugin version sync

### T-001: RED — three-way version alignment guard test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**AC**: AC-US2-01
**Test Plan**: Given package.json 1.0.589 and plugin.json 1.0.586, When the alignment test runs, Then it FAILS reporting the drift (package.json vs plugin.json vs marketplace.json root + plugins[0]).

### T-002: GREEN — stamp script + fix current drift
**User Story**: US-001/US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US2-02
**Test Plan**: Given the new stamp-plugin-version.cjs, When run, Then plugin.json + marketplace.json (root + plugins[0]) = package.json version (1.0.589); re-running is a no-op; the guard test passes; `validate-versions.cjs` exits 0.

### T-003: Wire stamp + validate into every publish path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-02, AC-US1-03, AC-US1-04
**Test Plan**: Given package.json scripts, When `build` runs, Then it stamps; `prepublishOnly` runs validate:versions after rebuild; `version` lifecycle stamps + stages; bump-version.sh calls the script (no inline node -e). Simulate a drift (set plugin.json to a wrong version) → `npm run stamp:plugin-version` re-aligns and `validate:versions` exits 0.

### T-004: VERIFY — build + validate + suite green
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**AC**: AC-US2-03
**Test Plan**: Given the fix, When `npm run build` runs, Then it succeeds and plugin.json/marketplace.json are stamped to package.json version; `node scripts/validation/validate-versions.cjs` exits 0; `npx vitest run tests/unit/build/version-alignment.test.ts` passes.
