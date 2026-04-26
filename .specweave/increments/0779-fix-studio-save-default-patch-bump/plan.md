# Implementation Plan: Studio Save default patch bump

## Overview

Single-file fix to `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/EditorPanel.tsx`. `handleSave()` is augmented to compare the editor's frontmatter version against the last-saved version. If equal, it bumps the patch in the content string before persisting. If the editor version is already strictly higher (user pressed a bump button), it persists as-is. No backend or wire-format change.

## Design

### Components

- **`EditorPanel.tsx`**.
  - Existing helpers: `handleSave` (lines 143-161), `handleBump` (lines 167-180), `saveContent` (from WorkspaceContext).
  - Extract a pure helper `bumpVersionInContent(content: string, kind: "patch"|"minor"|"major"): string` from the existing `handleBump` body so we can apply the bump synchronously without round-tripping through React state. `handleBump` becomes a thin wrapper that calls the helper + `setContent`.
  - Modified `handleSave`:
    1. Parse editor version from `content` (textarea value) and saved version from `savedContent`.
    2. If both are valid and equal, compute `nextContent = bumpVersionInContent(content, "patch")` and call `saveContent(nextContent)` plus `setContent(nextContent)` to keep the textarea in sync.
    3. Else call `saveContent(content)` unchanged.
  - The existing `studio:content-saved` event continues to fire after `saveContent` resolves — no refresh-wiring change.

### Data Model

No schema change. The editor operates on raw SKILL.md text with YAML frontmatter; the version field is the only thing this fix touches, and only in the auto-bump branch.

### API Contracts

No change. `POST /api/skills/:plugin/:skill/apply-improvement` continues to receive a content string; it already accepts higher-or-equal versions and auto-bumps when needed (we simply stop relying on its auto-bump because the frontend now bumps explicitly when needed).

## Technology Stack

- **Frontend**: React + Vite + TypeScript (vskill eval-ui).
- **Tests**: vitest + React Testing Library.

## Rationale

**Architecture Decisions**:

- **Bump on the client, not the server.** The user perceives the version change in the UI immediately after Save. Bumping client-side keeps the `studio:content-saved` event carrying the correct version without an extra round-trip. The backend's auto-bump remains as a safety net.
- **Strict-equal gate, not "always bump".** "Always bump on Save" would erase a user's deliberate `+minor` or `+major`. Comparing editor vs last-saved is the minimum logic that preserves user intent.
- **Synchronous helper, not React-state await.** Extracting `bumpVersionInContent` lets `handleSave` compute the next content string directly and pass it to `saveContent` in the same call. Avoids React state batching pitfalls and keeps the test surface small (the helper is a pure function).
- **No new module.** The helper lives next to `handleBump` in `EditorPanel.tsx` for cohesion. If the file grows large, extract later.

## Implementation Phases

### Phase 1: TDD RED
Write three failing vitest cases covering the auto-bump-on-clean path and the two respect-manual paths.

### Phase 2: TDD GREEN
Extract the pure helper, modify `handleSave` to implement the editor-vs-saved version comparison and conditional auto-bump.

### Phase 3: REFACTOR + manual verify
- Run the eval-ui vitest suite.
- Self-install per project convention: `npx vskill@<local-build> studio` and reproduce — open a skill, edit a body line, click Save → confirm the version badge increments and preview refreshes.

## Testing Strategy

- **Unit/component (vitest + RTL)**: render `EditorPanel` with a controlled `savedContent` and initial `content`. Mock `saveContent` via the WorkspaceContext provider override (or mock the `api.applyImprovement` module). Click Save and inspect the captured payload's frontmatter version.
- **No new e2e**. Manual smoke is sufficient.

## Technical Challenges

### Challenge 1: Where does `handleBump` live and how does it write back?

**Solution**: read the file before patching to confirm. Likely sets local React state on a controlled textarea. Extract a pure `bumpVersionInContent` helper from `handleBump` body so both call paths share parsing/writing logic.
**Risk**: if `handleBump` is more than ~30 lines and tightly coupled to component state, the extraction is the bigger change. Mitigated by writing a unit test for the helper before refactoring.

### Challenge 2: Last-saved version source of truth

**Solution**: the panel already tracks `isDirty` by comparing editor content to `savedContent`. Use `savedContent`'s frontmatter version as the comparator.
**Risk**: if `savedContent` is null/empty on first edit, the version comparison falls through to "save as-is". Acceptable — first save shouldn't synthesize a bump from nothing.

### Challenge 3: React state batching

**Solution**: by computing `nextContent` synchronously and passing it directly to `saveContent(nextContent)`, we sidestep batching entirely. Also call `setContent(nextContent)` so the textarea reflects the bump on success.
