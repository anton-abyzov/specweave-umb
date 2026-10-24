# Open all limits as an app-wide sheet

## Problem

On October 23, 2026 Anton clicked "All limits and accounts" in the composer usage popover ("Limits by machine"). It navigated to the `/usage` route, which replaced the coordinator and right panes with a full page. The sidebar stayed live, and the project and thread he was on were gone until he navigated back. Settings opens as a centered sheet over the dimmed app, and he expected the same here. Screenshots are in `~/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-…-b0a52738….png` and `…-9ea1ab88….png`.

## Scope

In:
- The popover link opens Usage > Limits in the same sheet shell as Settings, over the whole window including the sidebar.
- The route and the project or thread underneath stay mounted.
- Escape and the close button close the sheet, and focus returns to the usage chip.

Out:
- The sidebar's Usage entry and the command palette keep the `/usage` page.
- No change to usage, limits or routing data.
- No second dashboard: the sheet renders the existing `UsagePage` body.

## Acceptance Criteria

- [ ] AC-01: Clicking "All limits and accounts" in the usage popover opens a modal sheet (`role="dialog"`, labelled "Usage", everything outside it inert) that covers the whole window, sidebar included. The pathname does not change.
- [ ] AC-02: The sheet opens on the Limits tab with all environments in view. It does not overwrite the saved Usage page metric preference unless the user switches tabs inside the sheet. Changing the tab or the environment scope inside the sheet keeps that state until the sheet closes.
- [ ] AC-03: Escape (when no inner control consumes it), the close button and a click on the dimmed area close the sheet, and focus returns to the usage chip. Escape with a pinned day clears the pin first. Escape never navigates back.
- [ ] AC-04: Settings still renders through the same shell, with unchanged behaviour (existing SettingsDialog tests pass).
- [ ] AC-05: Headless before and after screenshots in `~/.specwithcode/m4/evidence/usage-limits-overlay-20261023/` show the page replacing the panes before the fix and the sheet over the intact layout after it.

## Approach

- `apps/web/src/components/ui/app-sheet.tsx` (new): the Settings sheet shell, extracted from `SettingsDialog.tsx`. It keeps the backdrop, the viewport, deferred Escape, close-on-backdrop and the no-drag regions, with an optional nav column and a title. `SettingsDialog` becomes a thin wrapper, so Settings output does not change.
- `apps/web/src/components/usage/UsagePage.tsx` gains a `variant: "page" | "sheet"`:
  - In sheet mode it renders without `SidebarInset` or `WorkspacePageHeader`, and its top bar goes in the sheet header.
  - `initialMetric` sets the opening tab without saving it.
  - Escape clears a pinned day, otherwise it closes the sheet.
- `apps/web/src/components/usage/UsageSheet.tsx` (new): `openUsageSheet()` (a zustand request store, like `ThreadMoveDialog`) and a `UsageSheetHost` mounted in `__root.tsx` next to the other dialog hosts. Focus returns to the element remembered by the existing opener tracker (`readSettingsOpener`/`restoreSettingsFocus`).
- `ProjectUsageIndicator.tsx`: the footer `<Link to="/usage">` becomes a button that closes the popover and calls `openUsageSheet({ metric: "limits" })`. PR #637 (1025) rewrites this file into `MachineLimitsPanel`. Whichever lands second swaps its Link for the same one-line call.
- Rejected: turning `/usage` into a Settings-style route. It would unmount the project or thread underneath, as Settings does today, and change every Usage entry point.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: Only the popover link opens the sheet; the sidebar's Usage entry stays a page. This is reversible: other entry points can call `openUsageSheet()`.
- D-02: The sheet opens on all environments, which matches the popover's every-machine list.

### Open
- none

## Tasks

### T-01 Shared sheet shell and Usage sheet variant
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/ui/app-sheet.tsx, apps/web/src/components/settings/SettingsDialog.tsx, apps/web/src/components/usage/UsagePage.tsx, apps/web/src/components/usage/UsageSheet.tsx, apps/web/src/routes/__root.tsx | Test: `npx vp test run --project unit src/components/usage src/components/settings/SettingsDialog` (apps/web)

### T-02 Popover opens the sheet
- AC: AC-01, AC-03 | Files: apps/web/src/components/studio/shell/ProjectUsageIndicator.tsx, apps/web/src/components/studio/shell/ProjectUsageIndicator.test.tsx | Test: `npx vp test run --project unit src/components/studio/shell/ProjectUsageIndicator` (apps/web)

### T-03 Headless before/after evidence
- AC: AC-05 | Files: ~/.specwithcode/m4/evidence/usage-limits-overlay-20261023/ | Test: headless Playwright capture script in the evidence folder

### T-04 Draft PR with green checks
- AC: AC-01..AC-05 | Files: PR on anton-abyzov/specwithcode-dev | Test: `gh pr checks <n>`

### T-05 Installed acceptance after the next release
- AC: AC-01, AC-03 | Files: evidence folder | Test: headless capture of the installed app after a release that contains the PR

### Verify and close 1029
