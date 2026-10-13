# Cancel and close navigation audit

Read-only source audit, 2026-10-13. Product source baseline `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f`; relevant navigation files also match observed `origin/main` `2a66d765aebd53b113fad99224363d10a080af73`. SpecWeave installed and npm stable both 3.0.14. Hub, product AGENTS and existing 0901 owner/ledger inspected; no pickup, task claim, product edit, live session/API mutation or browser operation. This report is the only written artifact.

## Findings

### 1. Morning briefing drops its originating settings page

`apps/web/src/components/settings/GoogleAccountSettings.tsx:462-468` links to `/settings/scheduled-tasks` with only `template` and `projectId`. Settings scope middleware preserves scope query axes, but the originating URL is not recorded.

`apps/web/src/components/settings/ScheduledTasksSettings.tsx:339-342` handles all editor closure with `setEditor(null)` and `setTemplateDismissed(true)`. Therefore source behavior for Cancel, X, backdrop and dialog Escape is to remain on Scheduled tasks, not return to Google. A direct Cancel-to-home call was **not** found; that exact user-observed jump still needs a headless UI reproduction.

Relevant action paths:

| Action | Source | Current result |
| --- | --- | --- |
| Morning briefing | GoogleAccountSettings.tsx:462 | Navigates to Scheduled tasks and opens template |
| Cancel | ScheduledTasksSettings.tsx:1405 | DialogClose invokes common onClose |
| X | components/ui/dialog.tsx:107 | Same Base UI dialog close |
| Escape/backdrop | ScheduledTasksSettings.tsx:985-989 | Same onClose when not saving |
| Successful Save/Create | ScheduledTasksSettings.tsx:981 | Also calls the same onClose |

Expected dismissal: return to the actual originating internal URL, including its machine/project/checkout query and hash. Do not assume every template was opened from Google, and do not use browser history blindly for directly opened template URLs. A direct link with no origin should dismiss to the ordinary Scheduled tasks page, with the consumed template query removed.

Implementation caution: distinguish successful save from cancellation/dismissal if save should remain on the task list. The current single callback conflates both outcomes.

### 2. Template dismissal survives only in component memory

`ScheduledTasksSettings.tsx:258-261` stores a single `templateDismissed` boolean; closure does not remove `template`/`projectId` from the URL. Reload/remount of the dismissed URL reopens the draft. Conversely, changing the template project while the same component remains mounted can keep a new template suppressed by the old dismissal. Make dismissal consume the navigation request or key its state to that request, and test browser back/forward and direct-link reload.

### 3. Theme variant Escape can also leave Settings

`apps/web/src/components/settings/ThemeSettings.tsx:179-181` closes an open radial variant selector on Escape but does not prevent default or stop propagation. When no independent tooltip/popup consumes that event, `hooks/useNavigateBack.ts:25-34` then runs the page-level action. `routes/settings.tsx:115-116` supplies `useNavigateToMainApp`, which can jump to a project/chat or home. Consume Escape when it actually dismisses the open radial selector. This is a source-confirmed propagation path; no browser reproduction was run in this audit.

## Shared navigation mechanism

`components/sidebar/mainAppLocation.ts:5-13,20-25,32-34` deliberately excludes Settings, Usage and Pull Requests from remembered destinations. Its Back action returns to the last main-app href, or `/` for a utility-page launch. Settings Escape and the sidebar Back button (`components/sidebar/SidebarChrome.tsx:146-149`) both use it. Thus utility-to-utility launch context is unavailable to those actions.

`components/settings/SettingsSidebarNav.tsx:181-215` uses `replace: true` for category and search navigation. Replacing all dismissals with `window.history.back()` therefore cannot reliably reconstruct the initiating utility page. Prefer a shared, explicit internal origin carried by cross-page modal/setup launches; retain existing local-close behavior for ordinary overlays. Preserve full href and reject external/malformed return targets. Keep page-level Escape behind control-level dismissal; do not treat a closed select menu as a request to leave a dialog or page.

The ordinary `useNavigateBack` path used by Usage and Pull Requests already uses browser history with `/` only when no application history exists. Main-app href tracking already retains query/hash for the main-app destination; the missing part is utility-origin tracking, not string truncation in this helper.

## Cancel/close inventory and boundaries

Searched all web routes/hooks and component navigation references, including 65 files containing navigation/history APIs and the 16 files where navigation coexists with cancel/close callbacks. Followed settings handlers, shared dialog/menu primitives, utility page Escape, and selected native settings routes.

| Surface | Source evidence | Assessment |
| --- | --- | --- |
| Scheduled New/Edit task opened locally | ScheduledTasksSettings.tsx:252,291,339 | Local close is correct; do not navigate back for ordinary list-launched edits |
| Scheduled webhook deliveries | ScheduledTasksSettings.tsx:547,586-588,684 | Local state close/Done; no route mutation |
| Provider/managed-account/setup dialogs | AddProviderInstanceDialog.tsx:671-678; AddCodexAccountDialog.tsx:88-89; ChatGptAccountPicker.tsx:36-37 | Cancel closes locally; wizard Back moves one step; preserve both semantics |
| Device host and SnapShot setup | DeviceHostEditor.tsx:50-51,214; DeviceHostsSettings.tsx:159; SnapShotSetupDialog.tsx:232-233,391 | Local close, with existing busy guards; no navigation defect found |
| Google own-client Cancel | GoogleAccountSettings.tsx:267 | Clears replacingClient locally; no navigation defect found |
| Theme editor/import and destructive confirmations | ThemeEditorHost.tsx:120-121; ThemeEditorPanel.tsx:1225,1249; ThemeImportDialog.tsx:421; ThemeSettings.tsx:963 | Local close/confirmation cancellation; do not replace with browser back |
| Model inline editors, keybinding recorders, license search | CustomModelEditor.tsx:296-300; ProviderModelsSection.tsx:622-626; KeybindingsSettings.tsx:747-752,1063-1068; OpenSourceLicenses.tsx:161-166 | Escape prevents default before local cancellation; page navigation correctly suppressed |
| Settings search, SSH suggestions | SettingsSidebarNav.tsx:220-227; ConnectionsSettings.tsx:2838-2841 | Explicitly consumes Escape; no duplicate navigation found |
| Base UI dialogs, menus and select-style overlays | components/ui/dialog.tsx; installed Base UI 1.5.0 floating-ui-react/hooks/useDismiss.js:96-117 | Standard dismissal prevents default and stops propagation. No evidence of generic dialog Escape leakage; do not blanket change primitives |
| Usage environment menu | UsagePage.test.tsx:131-148 | Existing component regression proves first Escape closes menu and second navigates back |
| Pull-request editors/panels | PullRequestMarkdownEditor.tsx:87-90; PullRequestReviewAnnotation.tsx:45-47; routes/_chat.pull-requests.tsx:1611-1618,2203 | Editor/sweep/panel Escape consumes before page navigation; no additional route defect found |
| Project settings overlay | ProjectWorkspace.tsx:1526 | onClose only clears local tab. Home navigation at 1532 follows successful project deletion, not Cancel |
| Global project settings deletion | ProjectSettingsPanel.tsx:363 | Home follows removal of last project member; not a cancel path |
| Account device sign-in dialog | account/SignInAnotherDeviceDialog.tsx:245 | Approval Cancel resets local approval. Separate explicit Connections action navigates; not a cancellation defect |
| Native mobile settings/editor pickers | mobile SettingsScheduledTasksRouteScreen.tsx:445-460,485; ScheduledTaskPickerScreens.tsx:91; settings/components/SettingsScreen.tsx:27 | Native goBack returns the previous screen; task drafts have a discard guard. No hard-coded home cancellation found in these paths |

Browser history shortcuts (`AppSidebarLayout.tsx:205`) are user-requested navigation, not modal dismissal. They should retain their history semantics rather than be rewritten as local Cancel. Similarly, toast dismissals, preview-tab close, provider installation cancellation and deleted-thread fallback are separate operations, not evidence of bad Cancel navigation.

## Focused verification matrix for implementation

1. Google settings with non-default machine/project scope and hash -> Morning briefing -> Cancel, X, Escape and backdrop: return to exact origin; no scheduled task or draft persisted.
2. A dropdown inside the template editor -> Escape: close dropdown only; second Escape closes editor to origin. Saving state must retain its existing dismissal guard.
3. Scheduled tasks -> local New/Edit -> cancel: remain on the list with original scope; successful Save behavior tested separately.
4. Direct template URL without stored origin -> dismiss: remain on plain Scheduled tasks; reload does not reopen a dismissed request. Back/forward must not resurrect stale local dismissal or suppress a new project template.
5. Settings provider/setup dialogs and inline editors -> cancel/Escape: retain page and scope. Theme radial selector Escape specifically must not navigate.
6. Utility page Back/Escape: verify intended main-app versus explicit origin contract, with query/hash, direct launch, and category/search replace navigation. Do not infer all callers should become browser-back.

No product tests or browser checks were executed; this report separates code-path evidence from runtime proof.
