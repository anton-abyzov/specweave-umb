# Tasks — 0312-repos-umbrella-badge

## US-001: Umbrella-managed badge for sub-repos

### T-001: Add isUmbrellaManaged to RepoInfo interface
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test**: Given RepoInfo type → When inspected → Then it includes `isUmbrellaManaged?: boolean`
- Add `isUmbrellaManaged?: boolean` to `RepoInfo` in `types.ts`, `dashboard-server.ts`, and `ReposPage.tsx`

### T-002: Detect umbrella-managed repos in scanRepositories
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test**: Given umbrella project with `.specweave/` at root and sub-repos without own `.specweave/` → When scanRepositories runs → Then sub-repos have `isUmbrellaManaged: true`
- In `scanRepositories()`, after building repos array, check `fs.existsSync(path.join(projectRoot, '.specweave'))`. If true, iterate repos and set `isUmbrellaManaged: true` where `hasSpecweave` is false.

### T-003: Update badge rendering for 3 states
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-02
**Test**: Given repo with `isUmbrellaManaged: true` → When rendered → Then badge shows "via umbrella" with info variant
- Check if Badge.tsx has an "info" variant, add if needed
- Update badge logic in ReposPage.tsx: hasSpecweave → "SpecWeave" (success), isUmbrellaManaged → "via umbrella" (info), else → "No SpecWeave" (default)

### T-004: Update KPI count to include umbrella-managed repos
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-03
**Test**: Given 1 repo with hasSpecweave and 2 with isUmbrellaManaged → When KPI renders → Then "With SpecWeave" shows 3
- Update the filter logic for the "With SpecWeave" KPI to count `hasSpecweave || isUmbrellaManaged`
