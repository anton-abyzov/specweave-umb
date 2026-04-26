# Plan: Restore Source-Skill Delete Button on Detail Header

## Approach

Add a trash button to `NewDetailHeader` mirroring `LegacyDetailHeader`'s implementation. Reuse the existing `studio:request-delete` event bus so App.tsx's existing listener (line 376-383) handles the rest — ConfirmDialog open, `usePendingDeletion` buffering, optimistic hide, undo, commit.

## Single-file change

`repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`:

1. In the `NewDetailHeader` Row 2 layout (skill name + VersionBadge), wrap the right-side cluster so the VersionBadge and a new trash button live side-by-side.
2. Render the trash button only when `skill.origin === "source"`.
3. Click handler dispatches `new CustomEvent("studio:request-delete", { detail: { skill: { ...minimal SkillInfo shape... } } })` — same minimal shape used at `LegacyDetailHeader` line 414-432.
4. Style: copy the legacy hover transition (text-tertiary → red), padding 4, borderRadius 4, transparent background.

## What does NOT change

- `RightPanel.tsx` continues to call `DetailHeader({ skill })`.
- `App.tsx` listener and ConfirmDialog wiring are untouched.
- `LegacyDetailHeader` stays as-is for `SkillWorkspaceInner`.
- Server-side `DELETE /api/skills/:plugin/:skill` route is unchanged.

## Verification

Manual:
1. `cd repositories/anton-abyzov/vskill && npm run build` (or studio rebuild).
2. `npx vskill studio` in a project with at least one source-authored skill.
3. Confirm trash button appears on the detail card for a source skill.
4. Confirm it does NOT appear for an installed skill.
5. Click trash → ConfirmDialog opens → confirm → 10s undo banner → commit → skill removed.
6. `tsc --noEmit` clean.

## Risks

- None substantive. Single render-only addition; no API or hook contract changes.
