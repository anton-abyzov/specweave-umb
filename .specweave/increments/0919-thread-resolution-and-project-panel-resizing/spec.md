# 0919 Thread resolution and project panel resizing

## Problem
Resolved failed workers remain in Waiting on you. Empty state groups disappear. The project right panel has fixed columns and no drag handler.

## Scope
Local Studio lifecycle grouping, all state headings, persistent right-panel resizing, focused tests and headless browser evidence. No release or live account mutation.

## Acceptance Criteria
- [ ] AC-01: Resolving a failed or usage-limited worker moves it to Resolved and removes its waiting badge; reopening restores its actionable status. Pending approvals/input and running work remain visible.
- [ ] AC-02: All four state groups are visible with counts, including empty Resolved; legacy archived threads are included in Resolved.
- [ ] AC-03: Dragging the project divider changes panel width, persists across reload, clamps to available space, and preserves mobile/expanded modes.
- [ ] AC-04: Focused tests, production web build and headless browser checks pass; manual UI acceptance remains pending.

## Approach
Owned product worktree /Users/antonabyzov/Projects/github/studio-thread-resolution, branch codex/thread-resolution, origin/main base 4d6e30488. No existing active increment owns these files. Keep live approvals/input and runtime above settlement; settlement overrides historical failure. Extract column sizing into its own component to keep the workspace below 1500 lines. Reuse existing resize hooks. CLI 3.0.15 matches registry. Jev unavailable (no key). Browser headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never; no live stores or provider turns.

## Tasks
### T-01 Implement and verify lifecycle and divider
- AC: AC-01, AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/Projects/github/studio-thread-resolution/apps/web/src/studio/, /Users/antonabyzov/Projects/github/studio-thread-resolution/apps/web/src/components/studio/, /Users/antonabyzov/Projects/github/studio-thread-resolution/apps/web/tests/project-workspace/ | Test: focused lifecycle/shell/workspace tests, web production build and headless resolution-resize-check.mjs

### T-02 Unify legacy resolved history and restore details
- AC: AC-01, AC-04 | Files: /Users/antonabyzov/Projects/github/studio-resolved-details/apps/web/ | Test: focused lifecycle, shell, header, archived-shell and workspace tests; production web build; headless resolved-details check

Follow-up requested 2026-10-14: legacy archived project threads belong in Resolved with visible status and Reopen. Preserve history and storage; supply the selected archived shell to embedded detail reads, with live shells authoritative. Reopen clears both legacy archival and settlement. Isolated successor branch codex/resolved-details from 90f900a58; previous owner checkout remains untouched. Manual acceptance remains pending.
