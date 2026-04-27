# Tasks: Studio detail — primary Install button + readability pass

**Increment**: 0784-studio-detail-install-button
**Test mode**: TDD (red → green → refactor)
**Project**: vskill-platform

## TDD discipline

For US-001, write failing tests FIRST in `__tests__/InstallPanel.test.tsx`, run them to confirm red, then implement in `InstallPanel.tsx` to turn them green. US-002 is purely visual; tests focus on inline-style values.

---

### T-001: Write failing tests for primary Install button (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-08 | **Status**: [x]

**Test Plan**:
- **Given** the InstallPanel renders with `skillName="anton/vskill/demo"`, `defaultVersion="1.0.0"`, `versions=[{version:"1.0.0",…}]`, **When** the component mounts, **Then** `getByTestId("studio-install-primary-button")` returns an enabled `<button>` with visible text "Install".
- **Given** the panel is mounted with a stubbed `navigator.clipboard.writeText`, **When** the user clicks the primary Install button, **Then** clipboard receives exactly `"vskill install anton/vskill/demo"`.
- **Given** the panel after a successful primary-button click, **When** the toast renders, **Then** a `role="status"` element contains text matching `/Run `vskill install/i`.
- **Given** the panel with `mockAuthFetch`, **When** the user clicks the primary Install button once, **Then** `mockAuthFetch` is called exactly once with `"/api/v1/studio/telemetry/install-copy"` and a `POST` body containing `skillName: "anton/vskill/demo"`.
- **Given** the panel rendered with `skillName="bad name with spaces"` (fails SAFE_NAME), **When** the component mounts, **Then** the primary Install button is `disabled` (or has `aria-disabled="true"`).
- **Given** the panel with both buttons present, **When** the user clicks the primary Install button THEN the Copy overlay button, **Then** clipboard is called twice and `mockAuthFetch` is called twice.

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx`

**Verification**: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` — all six new tests should FAIL (button does not exist yet).

---

### T-002: Implement Install button + shared action (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08 | **Status**: [x]

**Test Plan**:
- **Given** the failing tests from T-001, **When** I refactor `onCopy` → `runInstallAction` and add the primary Install button (Tailwind `bg-blue-600` style, `data-testid="studio-install-primary-button"`, `disabled={!safe}`) above the `TerminalBlock`, **Then** all six new tests pass without breaking the existing tests in the file.

**Implementation notes**:
- Rename the callback for clarity but keep behavior identical.
- Both buttons call the same `runInstallAction` reference.
- Blocked branch (`isBlocked && blockedEntry`) continues to short-circuit to `BlockedSkillView` before the button is rendered (AC-US1-06 holds by structural existing logic; assert in T-003 if a regression test is wanted, otherwise existing blocked tests already cover it).

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`

**Verification**: re-run the test command — all green.

---

### T-003: Readability swaps in InstallPanel + page (US-002)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x]

**Test Plan**:
- **Given** `page.tsx` and `InstallPanel.tsx` after the swaps, **When** I grep the files for `--text-faint`, **Then** only `bylineSep` retains it; every other informational label uses `--text-muted` or `--accent-teal`.
- **Given** a manual smoke render, **When** I color-pick the publisher prefix / version chip / byline / footer in DevTools (light theme), **Then** the foreground reads `#666666`.
- **Given** the "See all versions →" link, **When** rendered, **Then** its color matches `var(--accent-teal)`.

**Implementation notes**: pure inline-style changes — no behavior changes, no new tokens.

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/page.tsx` (lines 154, 161, 215, 265)
- `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx` (line 204)

**Verification**: visual check + grep:
```bash
cd repositories/anton-abyzov/vskill-platform
grep -n 'text-faint' src/app/studio/find/'[owner]'/'[repo]'/'[skill]'/page.tsx
# Expect ONE match: bylineSep
grep -n 'text-faint' src/app/studio/find/'[owner]'/'[repo]'/'[skill]'/InstallPanel.tsx
# Expect ZERO matches.
```

---

### T-004: Build / typecheck verification
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x]

**Test Plan**:
- **Given** the modified files, **When** I run `npm run typecheck` (or `npm run build`), **Then** there are no new TypeScript errors.

**Files**: n/a (verification only)

**Verification**:
```bash
cd repositories/anton-abyzov/vskill-platform
npx tsc --noEmit
```

---

### T-005: Smoke test in browser (manual via preview tools)
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01..06 | **Status**: [x]

**Test Plan**:
- **Given** `npm run dev` running on port 3000, **When** I navigate to `/studio/find/<owner>/<repo>/<skill>` for any seeded skill, **Then** the Install button is visible above the terminal block, click triggers a toast and one `install-copy` POST in the Network panel.

**Files**: n/a (verification only)

**Verification**: preview_start + preview tools per the verification workflow. Capture a screenshot.

---

## Total: 5 tasks | 2 user stories | 14 ACs covered
