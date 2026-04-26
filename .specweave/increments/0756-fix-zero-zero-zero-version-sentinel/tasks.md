# Tasks — 0756

### T-001: RED — failing test for `0.0.0` sentinel rejection
**Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given resolver input `{ registryCurrentVersion: "0.0.0", pluginVersion: "1.0.4" }` → When `resolveSkillVersion` runs → Then result is `{ version: "1.0.4", versionSource: "plugin" }` (not `0.0.0`).

### T-002: GREEN — `pick()` rejects `"0.0.0"` sentinel
**Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: All resolver tests pass; `pick("0.0.0")` returns `null`; explicit fallback chain proven via TC-008 (new) and TC-004 (existing).

### T-003: Update `StudioContext.tsx` final fallback `"0.0.0"` → `"1.0.0"`
**Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Existing StudioContext signature tests still pass; line 405 no longer emits `0.0.0` for any input.

### T-004: DB sanity script + run
**Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: `scripts/check-zero-versions.ts` returns 0 rows for both tables; codex skills present at `1.0.0`.

### T-005: Build vskill bundle and serve studio
**Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: `npm run build` succeeds; bundle contains the new resolver; `vskill studio` serves it on `localhost:3136`.

### T-006: Playwright screenshot evidence
**Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Playwright opens the codex plugin section, asserts none of the 3 codex skill rows shows `v0.0.0`, and captures `reports/studio-after-fix.png`.
