# Manageable project overrides

## Problem

Project settings > General > Overrides cannot be managed. Anton clicked "Use app setting" and app-level "Manage" controls on November 6, 2026, saw nothing change, and could not tell what he had changed or undo it.

Evidence (read-only, November 6, 2026):

- `apps/web/src/components/settings/ProjectOverrides.tsx` lists one row per machine per key, so one setting overridden on three machines shows three rows.
- `projectOverrideRows.ts` `formatSettingValue` prints raw enum values (`auto_merge`, `pull_request`) and "3 items" for lists. A richer key-aware formatter already exists in `SettingInheritance.tsx` (`formatValue`) but Overrides does not use it.
- `useRunScopedPlan` (`useScopedSettings.ts`) toasts only on failure. A successful "Use app setting" silently removes the row; there is no confirmation and no undo.
- The app-scope inheritance popover (`SettingInheritance.tsx`, "Overridden by" > "Reset all") clears that key for every overriding project on the machine in one click, also with no confirmation or undo. On M4, "When a thread finishes" is overridden by 23 projects.
- The only edit path is "Use app setting". Changing an override's value means finding the setting elsewhere on the page.
- There is no settings change history. The only traces are `settings.json` mtimes and update backups.

What his clicks changed: M4 (`~/.specwithcode/m4/userdata/settings.json`) and Ministorm (`~/.specwithcode/ministorm/userdata/settings.json`) were both last written November 6 at 1:20:46 PM EST, in one project-scope write that added "Providers for the recommended model" (Devin, Copilot, Copilot 0889) to this project on both machines. Nothing was written on either machine after that, so his later clicks reverted nothing there. M1Max was not readable (no project binding there); his screenshot shows its "When a thread finishes: auto_merge" override still present.

### Environment > Repositories cannot be saved after a repo rename

Anton renamed `anton-abyzov/specwithcode-dev` to `anton-abyzov/specwithcode` and wanted the project's repository entry to follow. Evidence (`apps/web/src/components/studio/ProjectEnvironment.tsx`, `apps/server/src/project/ProjectEnvironmentPaths.ts`, `ProjectEnvironmentService.ts`):

- The entry's URL renders as read-only `<code>`; the only actions are Remove, Checkout path, Match existing checkout and Prepare checkout. Removing and re-adding loses the entry ID and its checkout path.
- He typed the new URL into Checkout path. The field has no client validation. On Save the server resolves `https://github.com/...` as a non-absolute path, files it under reason `outside`, and `requireEveryEntry` fails the whole save with "Repository checkout https://github.com/anton-abyzov/specwithcode.git is outside the project folder and its approved folders. Update or remove it in the project's Environment settings." in the dialog footer, which calls a URL a checkout, names no field and is far from the entry.
- `ProjectEnvironmentError` carries no entry ID, so the client cannot place the error.
- The server already detects a checkout whose origin differs from the entry (`status` → `mismatch`, reading `remote.origin.url`) but discards the origin, so the page cannot offer the fix. The shared checkout's origin is already `https://github.com/anton-abyzov/specwithcode.git`.
- Save itself accepts a changed URL on an existing entry ID (`ProjectService` → `normalizeProjectEnvironment` does not lock URLs), so editing needs no server permission change.

## Scope

In (repositories): editing an entry's URL in place, inline Checkout path validation, origin-mismatch detection with a one-click URL update, and save errors attached to the entry that caused them.

In: the project Overrides section (grouping, labels, values, inline edit, clear, confirmation, undo), confirmation and undo for the app-scope "Reset it / Reset all" override clear, and one shared key-aware value formatter. Out: a persisted settings audit log (follow-up), changing which keys may be overridden, and any change to which paths may be approved. The repositories work adds two optional, backward-compatible contract fields; the Overrides work changes no server or contract code.

## Acceptance Criteria

- [ ] AC-01: Overrides shows one row per setting. Machines with the same project value are grouped on one line ("M1Max, Ministorm: Open PR and auto-merge"), and machines with different values get their own line. Each line shows the project value next to that machine's app value. No raw enum or ID appears: `auto_merge` reads "Open PR and auto-merge", `full-access` reads "Full access", and provider lists show provider names ("Devin, Copilot +1").
- [ ] AC-02: Each row has a direct edit control: a Select with the setting's options for enum and boolean keys, which writes the chosen value to every machine on that line, and "Edit" for list, model and object keys, which scrolls to and highlights the setting's own row on the project page. "Use app setting" stays, per line, and a per-row "Use app setting everywhere" covers all lines.
- [ ] AC-03: Every successful change shows a toast naming the setting, the machines and the before → after values, with an Undo action. The row stays visible for the session, marked "Now follows the app setting (Open PR) · Undo" or "Changed to Full access · Undo", instead of disappearing. Undo restores the exact previous raw values on each machine. A partial failure names the machines that saved and the ones that did not, and Undo covers only the saved ones.
- [ ] AC-04: The app-scope "Reset it / Reset all" in the inheritance popover asks for confirmation listing the number of projects and machines affected, then shows the same toast with Undo restoring every cleared project's value.
- [x] AC-05: Read-only machines or offline machines show the line with a disabled control and the reason in a tooltip. Light and dark at 1440px and 390px show no overflow, and every control is keyboard reachable. Focused unit tests cover grouping, labels, undo plans and partial failure; headless screenshots record before and after.

- [ ] AC-06: Each repository entry has Edit URL. It opens an inline field prefilled with the URL, validated as you type with the same rule as Add URL (credential-free HTTPS or SSH, no query or fragment, not a duplicate of another entry). Saving keeps the entry's ID and checkout path; Cancel restores the old URL. The entry shows "URL changed, unsaved" until Save.
- [ ] AC-07: The Checkout path field validates as you type. A value that parses as a repository URL (`https://`, `ssh://`, `git@host:`) shows "This is a folder path, not a URL." under the field, with "Use as repository URL" when the entry's URL is different. A relative path shows "Use an absolute folder path." Save is disabled while any entry has a field error, and the footer says which entry to fix.
- [ ] AC-08: When a saved checkout's `origin` differs from the entry's URL and the origin is a valid credential-free repository URL, the entry shows "This checkout's origin is <origin>" with "Update URL to <origin>". One click sets the draft URL (keeping ID and path); Save applies it, and the status turns to Ready. An origin that holds credentials or fails validation is never sent to the client.
- [x] AC-09: A save rejected for a folder or repository entry shows the server message under that entry, scrolls it into view and focuses its field; the footer shows only "1 entry needs attention". A URL typed as a checkout path gets a message that says so instead of "outside the project folder". Older servers without the entry ID keep today's footer error.

## Approach

### Repositories

7. `packages/contracts/src/projectEnvironment.ts`: optional `origin` on read-result repositories (sent only for `mismatch`, only when `projectRepositoryIdentity(origin)` is non-null), and optional `entry` `{ kind, repositoryId?, path }` on `ProjectEnvironmentError`. Both `optionalKey`, so mixed versions decode.
8. `ProjectEnvironmentService.ts`: `status` returns the origin it already reads; `read` passes it through.
9. `ProjectEnvironmentPaths.ts`: `requireEveryEntry` attaches `entry` to the error; `describeProjectEnvironmentProblem` says "is not a folder path" when the saved checkout path is not absolute or parses as a repository URL.
10. `ProjectEnvironment.tsx` plus a small `projectEnvironmentDraft.ts` (pure validation: `checkoutPathError`, `urlEditError`): Edit URL, inline field errors, Update URL from origin, per-entry save error. The settings dialog that owns Save (`ProjectWorkspaceSettings`) passes the structured error down and disables Save on field errors.

Rejected: auto-updating the URL when the origin changes. The URL is an approval; a click keeps the user in charge. Rejected: removing and re-adding the entry, which drops its ID and path.

### Overrides

1. `SettingInheritance.tsx`: move `formatValue` to `settingValueLabels.ts` as `formatSettingValueFor(key, value, providerLabel?)`, add the runtime-mode, limit-action and env-mode labels from `projectOverrideRows.ts` `VALUE_LABELS`, and provider-name lists. Both the popover and Overrides use it; `formatSettingValue` in `projectOverrideRows.ts` is deleted.
2. `projectOverrideRows.ts`: `groupProjectSettingOverrides` returns rows keyed by setting, each with lines grouped by (project value, app value) and the raw values kept for undo and edit.
3. `scopedSettings.ts`: `planProjectOverridesSet(environments, entries, set)` beside `planProjectOverridesClear`, both through the existing `projectOverrideChangeWrites`. An undo plan is a set of the previous raw values per entry.
4. `useScopedSettings.ts`: `useRunScopedPlan` returns the per-environment result and accepts an optional `success` message with an undo plan; `useClearProjectOverrides` and Overrides use it, so the popover reset gets the same undo.
5. `ProjectOverrides.tsx`: new row layout with inline Select (an options table for enum and boolean keys), Edit jump (`SettingsRow` gets `data-setting-keys` so the jump finds the row), per-line and per-row clear, and session "changed" state.
6. `SettingInheritance.tsx`: confirm before "Reset all".

Rejected: a server-side settings history. It is the right long-term answer to "what did I change last week" but needs a contract and storage change; logged as a follow-up. Rejected: a modal editor per key; 55 keys already have their own rows on the page, so Edit reuses them.

Risk: a machine whose server lacks `projectSettingsOverrideChanges` gets a whole-map patch built from the client's snapshot; undo uses the same path, so it is no worse than today.

Mockup: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1250-manageable-project-overrides/mockup.html`

## Decisions

### Asked
- D-00 Design (Overrides and Repositories mockups) → approved by Anton, November 6, 2026
### Defaulted (change any before sw-do)
- D-01 Undo lives in the toast and in the row's session marker; no persisted history in this increment.
- D-02 Inline Select writes to every machine on that line; per-machine edits come from expanding a grouped line.
- D-04 Origin-based URL update is a one-click draft change, never automatic.
- D-05 A URL in Checkout path offers "Use as repository URL" rather than silently moving it.
- D-03 App-scope "Reset all" gains a confirmation; single "Reset it" does not, it gets the undo toast only.
### Open
- none

## Tasks

App paths are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev`. Implementation waits for "1250 may branch" from 1254 (Grok install fails on M1). After merge: leave the checkout clean on main and send "your turn" to the Project settings hotkey thread.

### T-01 Shared value labels and grouped override rows
- AC: AC-01 | Files: apps/web/src/components/settings/settingValueLabels.ts, apps/web/src/components/settings/projectOverrideRows.ts, apps/web/src/components/settings/projectOverrideRows.test.ts, apps/web/src/components/settings/SettingInheritance.tsx | Test: from apps/web run node ../../node_modules/vite-plus/bin/vp test run src/components/settings/projectOverrideRows.test.ts

### T-02 Set and undo plans with success feedback
- AC: AC-03, AC-04 | Files: apps/web/src/components/settings/scopedSettings.ts, apps/web/src/components/settings/scopedSettings.test.ts, apps/web/src/components/settings/useScopedSettings.ts, apps/web/src/components/settings/SettingInheritance.tsx | Test: from apps/web run node ../../node_modules/vite-plus/bin/vp test run src/components/settings/scopedSettings.test.ts src/components/settings/SettingInheritance.test.ts

### T-03 Overrides section redesign
- AC: AC-02, AC-03, AC-05 | Files: apps/web/src/components/settings/ProjectOverrides.tsx, apps/web/src/components/settings/ProjectOverrides.test.tsx, apps/web/src/components/settings/settingsLayout.tsx | Test: from apps/web run node ../../node_modules/vite-plus/bin/vp test run src/components/settings/ProjectOverrides.test.tsx

### T-04 Repository origin and entry-scoped save errors (server and contract)
- AC: AC-08, AC-09 | Files: packages/contracts/src/projectEnvironment.ts, apps/server/src/project/ProjectEnvironmentService.ts, apps/server/src/project/ProjectEnvironmentService.test.ts, apps/server/src/project/ProjectEnvironmentPaths.ts, apps/server/src/project/ProjectEnvironmentPaths.test.ts | Test: from apps/server run node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectEnvironmentService.test.ts src/project/ProjectEnvironmentPaths.test.ts; covers origin returned only for a valid credential-free mismatch, a credentialed origin withheld, and an error naming the repository entry for a URL typed as a path

### T-05 Editable repository entries in Environment
- AC: AC-06, AC-07, AC-08, AC-09 | Files: apps/web/src/components/studio/ProjectEnvironment.tsx, apps/web/src/components/studio/projectEnvironmentDraft.ts, apps/web/src/components/studio/projectEnvironmentDraft.test.ts, apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx | Test: from apps/web run node ../../node_modules/vite-plus/bin/vp test run src/components/studio/projectEnvironmentDraft.test.ts src/components/studio/ProjectWorkspaceSettings.test.tsx; replays Anton's case: URL typed into Checkout path shows the inline error and blocks Save, Edit URL keeps ID and path, Update URL from origin, and a server rejection lands under its entry

### T-06 Verify and close 1250
- AC: AC-05, AC-09 | Files: .specweave/increments/1250-manageable-project-overrides/ | Test: headless before/after screenshots at 1440px and 390px, light and dark; typecheck; specweave verify 1250-manageable-project-overrides
