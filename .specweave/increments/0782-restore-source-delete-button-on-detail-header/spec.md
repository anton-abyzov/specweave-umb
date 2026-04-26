---
increment: 0782-restore-source-delete-button-on-detail-header
title: Restore Source-Skill Delete Button on Detail Header
type: bug
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: 'off'
coverage_target: 0
---

# Feature: Restore Source-Skill Delete Button on Detail Header

## Overview

Studio's detail-card header lost the trash/Delete button when `NewDetailHeader` (T-026, commit `0e1b736`) replaced the legacy header in `RightPanel`. The legacy button still exists in `LegacyDetailHeader` ([DetailHeader.tsx:400-456](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx)), but `RightPanel` calls the new shape (`{ skill }`) and never the legacy shape, so the button is invisible for every source-authored skill in the studio. The 0780 increment added an Uninstall button on the read-only banner for `origin === "installed"` skills but did not restore the source-skill Delete affordance.

The right-click → Delete path on the sidebar still works (via `useContextMenuState.ts` → `studio:request-delete`), so no data flow is broken — only the prominent header button is missing.

**Out of scope**: changes to the installed-skill Uninstall flow (0780), context-menu Delete entry (already works), plugin-level uninstall (PluginActionMenu, separate concern).

## User Stories

### US-001: Trash button visible on source-authored skill detail card
**Project**: vskill

**As a** user viewing a skill I authored in the studio
**I want** a Delete trash button on the detail card header
**So that** I can remove the skill from the studio without dropping to the sidebar context menu

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the selected skill has `origin === "source"`, `NewDetailHeader` renders a trash button in the top-right of the card (next to the version badge).
- [x] **AC-US1-02**: When the selected skill has `origin === "installed"`, the trash button is NOT rendered. Installed skills continue to surface the 0780 Uninstall button on the read-only banner.
- [x] **AC-US1-03**: Click → dispatches `studio:request-delete` CustomEvent with `{ detail: { skill: <SkillInfo-shape> } }`. The existing App.tsx listener opens ConfirmDialog and applies the 10s `usePendingDeletion` undo buffer — no new wiring required.
- [x] **AC-US1-04**: Button has `aria-label="Delete skill"` and `data-testid="detail-header-delete"`. Hover color shifts from `var(--text-tertiary)` to `var(--red)` to match the legacy header's affordance.

## Non-Functional Requirements

- **Reversibility**: Delete continues to route through the existing trash flow (OS Trash via `DELETE /api/skills/:plugin/:skill`) — recoverable, not hard `rm -rf`.
- **Accessibility**: aria-label + visible focus ring inherited from button defaults.
- **Test mode**: Manual verification only (`vskill studio` → select source skill → click trash → confirm). No new automated tests; existing context-menu Delete tests already cover the dispatch path.

## Out of Scope

- Installed-skill Uninstall flow (0780 owns).
- Context-menu Delete entry (already works).
- Plugin uninstall via PluginActionMenu (separate concern).
- Refactoring `LegacyDetailHeader` (still in use by `SkillWorkspaceInner`).

## References

- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx:78-288` — `NewDetailHeader` (target for the new button)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx:400-456` — `LegacyDetailHeader` trash button (template to mirror)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx:531,664` — call sites passing `{ skill }`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx:376-383` — `studio:request-delete` listener (no changes needed)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useContextMenuState.ts:54-59` — sidebar Delete dispatch (parity)
