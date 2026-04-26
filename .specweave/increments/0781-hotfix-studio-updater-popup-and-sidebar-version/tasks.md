# Tasks — 0781 hotfix

### T-001: Extend version-resolver with `preferInstalled` mode
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Test**: Given `preferInstalled: true` + `installedCurrentVersion: "1.0.2"` + `frontmatterVersion: "1.0.3"` → When `resolveSkillVersion` runs → Then output is `{ version: "1.0.2", versionSource: "registry" }`. Given `preferInstalled: false` and same inputs → returns `1.0.3` / `frontmatter`.

### T-002: Wire `preferInstalled` from `normalizeSkillInfo` + `mergeUpdatesIntoSkills`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test**: Given a SkillInfo payload with `origin: "installed"`, `version: "1.0.3"`, `currentVersion: "1.0.2"` → When `normalizeSkillInfo` runs → Then `resolvedVersion === "1.0.2"`.

### T-003: Add `SkillRow` test for installed-version preference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: Given a row mounted with `origin: "installed"` + `resolvedVersion: "1.0.2"` → Then the rendered badge text contains `1.0.2`. With `origin: "own"` + `resolvedVersion: "1.0.3"` → Then the badge contains `1.0.3`.

### T-004: Widen UpdateDropdown to 440px
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given `UpdateDropdown` mounted with one update row whose `name` is `anton-abyzov/greet-anton-abyzov` → When measuring the rendered popover root `style.width` → Then it is at least `440`. The inline Update button's `textContent.trim()` is exactly `Update`.

### T-005: Remove platform-degraded banner + props from UpdateDropdown
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given `UpdateDropdown` mounted with any inputs → Then `querySelector('[data-testid="update-dropdown-platform-degraded-banner"]')` is null. The component's TS prop type does NOT include `platformDegraded`/`platformReason`.

### T-006: Stop passing degraded props from UpdateBell
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: `tsc --noEmit` succeeds for UpdateBell.tsx after removing the two props from the JSX site (no unused-symbol warnings).

### T-007: Delete obsolete UpdateDropdown-degraded-banner test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: File `UpdateDropdown-degraded-banner.test.tsx` is removed; no other test imports it.

### T-008: Add `formatDiffSummary` helper + apply in VersionHistoryPanel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: `formatDiffSummary("0 files") === "Metadata-only release — no file changes"`. `formatDiffSummary("0 Files") === "Metadata-only release — no file changes"`. `formatDiffSummary("Synced SKILL.md") === "Synced SKILL.md"`. `formatDiffSummary(null) === ""`.

### T-009: Add plugin-context chip to DetailHeader for plugin-bundled skills
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given a SkillInfo with `pluginName: "mobile"`, `pluginVersion: "2.3.2"` → When DetailHeader renders → Then a `data-testid="detail-header-plugin-chip"` element exists with text `from mobile@2.3.2`. Given `pluginName: null` → no chip.

### T-010: Run `npx vitest run` for the eval-ui suite, fix any unrelated regressions, commit
**User Story**: ALL | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: All vitest specs in `src/eval-ui` pass.
