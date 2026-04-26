# Tasks: Studio Save default patch bump

## Overview

5 tasks across 3 phases (RED → GREEN → REFACTOR/verify). All work in `repositories/anton-abyzov/vskill/src/eval-ui/`. TDD discipline: every implementation task is preceded by a failing-test task.

**Test placement note (post-implementation refinement)**: T-001/T-002/T-003 originally specified a single `EditorPanel.handleSave.test.tsx` render-and-click test. During implementation we pivoted to two complementary suites that pin the same behaviour more durably: pure-helper tests in `src/eval-ui/src/utils/__tests__/computeSavePayload.test.ts` (6 cases) for the version-decision logic, plus a contract test in `src/eval-ui/src/pages/workspace/__tests__/WorkspaceContext.saveContent.test.tsx` (2 cases) for the `saveContent(contentOverride)` wiring. Together the 8 cases cover AC-US3-01..03 piecewise (helper → saveContent → api) without coupling the assertion to button-click rendering.

## Phase 1: TDD RED — write failing tests

### T-001: Add failing vitest case — Save auto-bumps patch when versions equal
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US3-01 | **Status**: [x] completed

**Description**: Add a test in `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.handleSave.test.tsx` (new file). Render `EditorPanel` with `savedContent` containing `version: "1.0.2"` and editor `content` identical (no manual bump). Mock the persist call. Modify body trivially to enable Save. Click Save. Assert the captured persist payload's frontmatter declares `version: "1.0.3"`.

**Test Plan** (Given/When/Then):
- **TC-001**: Given saved version 1.0.2 and editor version 1.0.2 with body modified, When Save is clicked, Then the persisted content's frontmatter version is "1.0.3".

Test must FAIL initially (current handleSave does not bump).

---

### T-002: Add failing vitest case — Save respects manual minor bump
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US3-02 | **Status**: [x] completed

**Description**: Render `EditorPanel` with `savedContent` at version `1.0.2`. Simulate the user clicking +minor (set editor content to declare `1.1.0`). Click Save. Assert persisted version is `1.1.0`.

**Test Plan**:
- **TC-002**: Given saved 1.0.2 and editor 1.1.0 (after user clicked +minor), When Save is clicked, Then the persisted version is "1.1.0" — NOT "1.1.1".

---

### T-003: Add failing vitest case — Save respects manual patch bump
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US3-03 | **Status**: [x] completed

**Description**: Same setup, but editor content declares `1.0.3` (user clicked +patch). Click Save. Assert persisted version is `1.0.3` (not `1.0.4`).

**Test Plan**:
- **TC-003**: Given saved 1.0.2 and editor 1.0.3 (after user clicked +patch), When Save is clicked, Then the persisted version is "1.0.3" — NOT "1.0.4".

---

## Phase 2: TDD GREEN — implement

### T-004: Extract bumpVersionInContent + modify handleSave
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Description**:
- In `EditorPanel.tsx`, extract the version parse-and-rewrite logic from `handleBump` (lines 167-180) into a pure helper `bumpVersionInContent(content: string, kind: "patch" | "minor" | "major"): string`. Add a sibling `extractFrontmatterVersion(content: string): string | null` that reads the `version:` line from the YAML frontmatter (used for the comparison).
- Refactor `handleBump` to call `bumpVersionInContent` + `setContent` (no behavior change).
- Modify `handleSave` (lines 143-161): before invoking `saveContent`, extract editor and saved versions; if both parse and are equal, compute `nextContent = bumpVersionInContent(content, "patch")`, call `setContent(nextContent)`, and pass `nextContent` to `saveContent`. Otherwise pass `content` unchanged. Existing `studio:content-saved` dispatch and `isDirty`/`saving` guards remain.

**Test**: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/EditorPanel.handleSave.test.tsx` — TC-001/002/003 all pass.

---

## Phase 3: REFACTOR + verify

### T-005: Run eval-ui suite + manual smoke
**User Story**: US-003 | **Satisfies ACs**: all | **Status**: [x] completed

**Description**:
- Run `npx vitest run` from `repositories/anton-abyzov/vskill/`. All eval-ui tests must be green; existing EditorPanel tests unchanged.
- Optionally rebuild the studio bundle and self-install (`npm run build:eval-ui` then `npx vskill@<local-build> studio`). Open a skill in the Edit tab, modify the body, click Save. Confirm the version badge increments by one patch and the preview pane refreshes.

**Test**: full vitest green; manual smoke confirms the user-reported behavior is fixed.
