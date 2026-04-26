# Tasks: Restore Source-Skill Delete Button on Detail Header

## T-001: Add trash button to NewDetailHeader for source skills
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

Mirror `LegacyDetailHeader` lines 400-456 inside `NewDetailHeader`. Place button in the Row 2 right-side cluster next to `VersionBadge`. Gate render on `skill.origin === "source"`. Dispatch `studio:request-delete` on click.

**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`

## T-002: Manual verification in vskill studio
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

Start `vskill studio`, select a source-authored skill, confirm button visible + click flow works (ConfirmDialog → 10s undo → commit). Select an installed skill, confirm button absent.

## T-003: tsc clean
**User Story**: US-001 | **AC**: All | **Status**: [x] completed

Run `npx tsc --noEmit` in the vskill repo; ensure no new errors introduced.
