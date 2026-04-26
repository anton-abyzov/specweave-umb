# Tasks: Studio skill detail — clickable GitHub source link

Strict TDD. Each implementation task is preceded by a failing-test task. No code lands without a test that fails before and passes after.

## Phase 1: Locate install-receipt write path

### T-001: Map install-receipt module
**Description**: Find the module(s) in `repositories/anton-abyzov/vskill/src/eval-server/` that read and write the install receipt JSON. The receipt is the same one that already records `installMethod: "copied" | "symlinked" | "authored"`. Confirm with `grep -rn "installMethod" src/eval-server/`.
**References**: AC-US4-01, AC-US4-02
**Status**: [x] Completed

## Phase 2: SkillInfo type extension

### T-002 (RED): Write failing test for `repoUrl` + `skillPath` on SkillInfo payload
**Description**: Add a Vitest case asserting that when an install receipt JSON contains `sourceRepoUrl` and `sourceSkillPath`, `buildSkillMetadata()` (or its existing test seam) returns a payload exposing `repoUrl` and `skillPath`. Add three parameterised cases: both fields, neither, partial.
**References**: AC-US4-03, FR-001, FR-003
**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/buildSkillMetadata.test.ts` (or nearest existing test file)
- **TC-001**: Given a receipt with `{ sourceRepoUrl: "https://github.com/x/y", sourceSkillPath: "skills/z" }`, when `buildSkillMetadata()` is called, then the returned payload has `repoUrl: "https://github.com/x/y"` and `skillPath: "skills/z"`.
- **TC-002**: Given a receipt with neither field, when called, then `repoUrl` and `skillPath` are `undefined`.
- **TC-003**: Given a receipt with only `sourceRepoUrl`, when called, then `repoUrl` is set and `skillPath` is `undefined`.
**Status**: [x] Completed

### T-003 (GREEN): Extend SkillInfo type and SkillMetadataFields
**Description**: Add `repoUrl?: string | null` and `skillPath?: string | null` to:
- `SkillInfo` in `src/eval-ui/src/types.ts` (lines 119-238)
- `SkillMetadataFields` (or whichever server-side type wraps the metadata) in `src/eval-server/api-routes.ts`
**References**: AC-US4-01, AC-US4-03, FR-001
**Status**: [x] Completed

### T-004 (GREEN): Wire receipt fields through buildSkillMetadata
**Description**: In `buildSkillMetadata()` (`src/eval-server/api-routes.ts` ~L755), read `sourceRepoUrl` and `sourceSkillPath` from the install-receipt JSON that's already loaded for `installMethod`, and emit them on the returned object as `repoUrl` and `skillPath`. Defensive read — missing fields produce `undefined`.
**References**: AC-US4-03, FR-003
**Status**: [x] Completed

## Phase 3: Install-receipt write path

### T-005 (RED): Write failing test for receipt-write persistence
**Description**: Add a test that the install-receipt write helper persists `sourceRepoUrl` and `sourceSkillPath` when the platform-source payload includes `repoUrl` and `skillPath`.
**References**: AC-US4-02, FR-002, FR-005
**Test Plan**:
- **File**: nearest existing test for the install-receipt module identified in T-001
- **TC-001**: Given a platform install payload `{ repoUrl: "...", skillPath: "..." }`, when the install-receipt write helper runs, then the persisted JSON contains `sourceRepoUrl` and `sourceSkillPath`.
- **TC-002**: Given a payload missing `repoUrl`, then the persisted JSON omits `sourceRepoUrl` (does not write `null` literal).
**Status**: [x] Completed

### T-006 (GREEN): Persist source fields in install-receipt write
**Description**: Update the install-receipt write helper (located in T-001) to capture `repoUrl` → `sourceRepoUrl` and `skillPath` → `sourceSkillPath` from the platform response.
**References**: AC-US4-02, FR-002, FR-005
**Status**: [x] Completed

## Phase 4: DetailHeader wiring

### T-007 (RED): Write failing test for source-file anchor on DetailHeader
**Description**: Add a Vitest + React Testing Library case to `DetailHeader.test.tsx` (or create one if missing) that renders DetailHeader with `skill = { ..., repoUrl: "https://github.com/x/y", skillPath: "skills/z" }` and asserts the byline contains an anchor with the correct href, target, and rel.
**References**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, FR-004
**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/DetailHeader.test.tsx`
- **TC-001 (US-001 anchor)**: Given a skill with `repoUrl="https://github.com/x/y"` and `skillPath="skills/z"`, when DetailHeader renders, then `data-testid="source-file-link"` is an `<a>` with `href="https://github.com/x/y/blob/HEAD/skills/z"`, `target="_blank"`, and `rel="noopener noreferrer"`.
- **TC-002 (US-001 label)**: same input, the anchor text content includes the last path segment `z` and the `↗` marker.
- **TC-003 (US-002 author link)**: AuthorLink anchor href equals the canonical repo root.
- **TC-004 (US-003 fallback)**: Given a skill with no `repoUrl` and no `homepage`, then `data-testid="source-file-copy"` (the copy-chip) is rendered, NOT `source-file-link`.
- **TC-005 (US-003 homepage fallback)**: Given a skill with `homepage="https://github.com/foo/bar"` and no `repoUrl`, then a `source-file-link` anchor is rendered with href derived from homepage (regression check).
**Status**: [x] Completed

### T-008 (GREEN): Pass `repoUrl` and `skillPath` from skill into AuthorLink + SourceFileLink
**Description**: Update `DetailHeader.tsx` lines 195-200 to pass `skill.repoUrl ?? skill.homepage ?? null` and `skill.skillPath ?? null` into both AuthorLink (repoUrl prop) and SourceFileLink (repoUrl + skillPath props).
**References**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, AC-US3-02, FR-004
**Status**: [x] Completed

## Phase 5: Refactor + full test sweep

### T-009 (REFACTOR): Run all eval-ui + eval-server tests
**Description**: Run `npm test` (or the package's test script) for both eval-ui and eval-server. Fix any drift the type changes cause. Verify no regression in the existing `SourceFileLink` and `AuthorLink` tests.
**References**: AC-US3-01, AC-US3-02, NFR-003
**Status**: [x] Completed

## Phase 6: Build + release

### T-010: Build eval-ui bundle
**Description**: Run the eval-ui build script so the new component code is in the pre-built bundle that eval-server serves. Confirm via `git status` that the bundled artifact (e.g. `dist/`, `eval-ui/dist/`) is regenerated.
**References**: AC-US1-03, SC-003
**Status**: [x] Completed

### T-011: Bump vskill patch version
**Description**: Bump `repositories/anton-abyzov/vskill/package.json` version (patch). Update CHANGELOG if one exists.
**References**: AC-US1-03, SC-003
**Status**: [x] Completed

### T-012: Publish to npm
**Description**: Run the package's release script (or `npm publish`). Confirm the published version appears on npmjs registry.
**References**: AC-US1-03, SC-003
**Status**: [x] Completed

## Phase 7: Self-verification

### T-013: Self-verify in real Studio session
**Description**: Run `npx vskill@<new-version> studio` from a temporary directory in the user's project. Use Claude_Preview MCP tools (`preview_start`, `preview_snapshot`, `preview_click`, `preview_screenshot`) to confirm:
  1. For an installed platform skill (one whose receipt has `sourceRepoUrl`): the source-file anchor is visible in the detail header byline.
  2. Click opens the GitHub blob URL in a new tab (assert via snapshot or by reading network/console events).
  3. For `greet-anton` (authored, no provenance): the copy-chip path still renders, no broken anchor.
**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US3-01, SC-001, SC-002, SC-003
**Test Plan**:
- **TC-001**: Given a freshly-`npx`-installed studio session, when navigating to an installed platform skill detail page, then `data-testid="source-file-link"` is present and clickable.
- **TC-002**: Given the same session, when navigating to `greet-anton`, then `data-testid="source-file-copy"` is present (no `source-file-link`).
**Status**: [x] Completed
