# Integrations settings in tabs: guided MCP add, built-in tools, device setup steps

## Problem

Anton, on M5 in Settings > Integrations (November 18, 2026, four screenshots):

1. "I want to add an MCP. At first, it's not really clear how I'm going to add it." The add form is raw config: Name, Command or URL, "Arguments, one per line", "Environment, KEY=value per line", two unticked checkboxes, Preview. There is no path for a known server such as Higgsfield, and no way to paste the link or command a vendor's page gives.
2. The empty state reads "No MCP declarations found in the inspected configuration files." It does not say what to do next.
3. Chrome and computer use are built into SpecWithCode, but the page never says so. The only explanation (`ComputerUseConnectionNote`) renders under a `computer-use` row, so it is invisible when the list is empty.
4. Scope is unclear. The page says "Applying settings on M5", the MCP section carries a second picker (the small "M5" tag, `ConnectionsLibrarySettings`), and the page mixes three scopes: agent access and Device hub are per machine, MCP is files on one machine, and the Browser preview, recording and link defaults are saved in this app window and ignore the header. With "All environments" picked, Device hub writes to every machine while MCP silently shows the first one.
5. Devices: with Device hub on, the page shows "Android SDK was not found. Install it with Android Studio or set ANDROID_HOME…" and raw lines such as "[apple-utils] Failed to run `xcrun simctl list devices --json`", with one Refresh button and no next step. "Agent device access" shows "Not installed" with a disabled switch and no reason. The iOS line said "Xcode is installed" above a failed `simctl`, so the diagnosis itself can be wrong.
6. "Think about creating a paginated view here." Integrations is one long scroll: agent access, MCP, eight browser and recording rows, Devices.

## Scope

In: Settings > Integrations in the web and desktop app. Four tabs, one scope line per tab, a new MCP servers tab (built-in block, server list, guided add with a catalog and paste box, the raw form as "Enter details by hand"), guided setup steps in Devices, structured device reason codes, layout that holds from 360 px to 1600 px, phrases for all shipped locales.

Out: the native iPhone and Android apps (they have no Integrations page; confirmed by search in `apps/mobile` and `apps/ios`). A remote catalog service. Managing MCP servers for providers that do not read a config file SpecWithCode can write. Any change to the Skills page (increment 1399 owns it; the two share the scope pattern in D-03). "SpecWithCode-managed connections" on the Project page keep their form; only the shared server list above them changes.

## Acceptance Criteria

Tabs and scope

- [ ] AC-01: Integrations has four tabs: "Agent access", "MCP servers", "Devices", "Preview and recording". Each has its own URL, and the sidebar item "Integrations" stays active on all of them.
- [ ] AC-02: Every existing `/settings/integrations#<anchor>` link and every settings-search result opens the tab that holds that row and scrolls to it.
- [ ] AC-03: The three per-machine tabs show one scope line, "Set up on <machine>", with the caption "Each machine keeps its own. Changes here only affect <machine>." There is one machine picker per page and none inside a section. "All environments" is not offered on these tabs. With one machine, the picker is plain text.
- [ ] AC-04: "Preview and recording" shows "Only in this app window" and no machine picker.
- [ ] AC-05: When the machine being set up is not the one the user is sitting at, the scope line says so ("You are on m4").
- [ ] AC-06: At a 560 px settings content width no tab needs more than two screens of scroll in its default state: the allowed-apps list collapses after four entries and the server catalog shows six entries until "Show all".

MCP servers

- [ ] AC-07: A "Built into SpecWithCode" block lists Chrome, Computer use, In-app browser and Simulators, each with one sentence, its live status on the selected machine and a link to where it is switched on. It states that these come with the app, work with every provider and are never added as MCP servers. It shows whether the server list is empty or not.
- [ ] AC-08: The empty state says "No MCP servers on <machine> yet" and points at the add box. The old sentence about "declarations" and "inspected configuration files" appears only under "About this list".
- [ ] AC-09: One paste box accepts a web address, a command line (`npx …`, `claude mcp add …`, `codex mcp add …`) or a JSON or TOML snippet and fills a readable summary: name, kind ("Web address" or "Runs on this machine"), and any secret values as masked fields. Unreadable input says what was expected and offers "Enter details by hand".
- [ ] AC-10: A catalog of known servers ships with the app (no network). Each entry shows name, one line, how sign-in works and any plan requirement, and adds with one click into the same summary. Higgsfield is in it. Every entry's address or command is checked against the vendor's own page and carries the date checked.
- [ ] AC-11: "Which AI tools get it" lists the tools installed on that machine, pre-ticked, and states in one line which threads will see the server and which will not (wording fixed by T-02).
- [ ] AC-12: The summary states "On <machine> only" and offers "Also add on" with the other machines. After saving, each machine shows its own result: "Added", "Offline, not added", "No access" or the error. Nothing is queued for an offline machine.
- [ ] AC-13: Every write still goes through the file-by-file review with masked values and Undo. After saving, the row never claims "Connected": it shows "Added" plus the sign-in step that T-02 proves, or the exact command to run when no in-app step exists.
- [ ] AC-14: Pasting or picking a server that duplicates a built-in tool (a Chrome or browser automation server, a computer-use server) shows "SpecWithCode already does this" with a link to the built-in, and "Add anyway".
- [ ] AC-15: The raw form remains as "Enter details by hand" with today's fields and validation. The by-tool matrix remains as "Compare by AI tool".
- [ ] AC-16: No lock or brain icon is used; secrets use the masked-field glyph. `retiredIcons.guard.test.ts` passes.

Devices

- [ ] AC-17: Each platform reports a reason code as well as text: iOS `not_mac`, `xcode_missing`, `xcode_not_selected`, `xcode_setup_unfinished`, `ios_runtime_missing`; Android `android_studio_missing`, `android_sdk_missing`, `android_tools_missing` (with the missing parts), `android_avd_missing`. A machine on an older version, which sends text only, shows that text and Check again.
- [ ] AC-18: Each code shows one step: a title, one sentence, one primary button and "Check again". Buttons: Open App Store (Xcode), Open Xcode, Open Android Studio, Get Android Studio (download page), Choose SDK folder. The iOS line never says "Xcode is installed" unless the stricter probe in `iosSimulatorSupport.ts` passed.
- [ ] AC-19: A step's button acts on the machine being set up. From another machine the label names it ("Open App Store on M5"). Where that machine cannot open a window, or the session lacks the right, the step says "Do this on M5" and offers Copy link.
- [ ] AC-20: The server opens only a fixed list of named targets; the client never sends a URL or path to open.
- [ ] AC-21: "Choose SDK folder" saves the folder for that machine in SpecWithCode settings and the Android check uses it. No shell profile is edited.
- [ ] AC-22: Raw tool output shows only under "Details" for that platform.
- [ ] AC-23: "Agent device access" shows why it is unavailable ("Needs a working simulator first", "Turn on Device hub first") and, when its tools are missing, an "Install" button that uses the existing tool-update path. "Not installed" alone never shows.

Layout and language

- [ ] AC-24: A headless check at 360, 390, 560, 728, 1100 and 1600 px, light and dark, reports no element wider than its container, no clipped button label and no text under 12 px, in English and in German and Russian.
- [ ] AC-25: All new copy has phrases in every shipped locale.

Delivery

- [ ] AC-26: Anton accepts the mockup before any app code is written.
- [ ] AC-27: Released through `scripts/release/request-release.sh`; the released build shows the tabs, the MCP add of one catalog entry and one device step on M5.

## Approach

Order: mockup and acceptance, the sign-in spike, a no-behaviour split of the page file, tabs and scope, MCP tab, device codes and steps, phrases, release.

Files (from the umbrella root, under `repositories/anton-abyzov/specwithcode/`):

- `apps/web/src/components/settings/IntegrationsSettings.tsx` is 1,639 lines, over the 1,500 limit. Split first into `integrations/AgentAccessTab.tsx`, `integrations/McpServersTab.tsx`, `integrations/DevicesTab.tsx`, `integrations/PreviewRecordingTab.tsx` and `integrations/IntegrationsTabs.tsx`.
- Routes: `apps/web/src/routes/settings.integrations.tsx` becomes a layout with child routes `access`, `mcp`, `devices`, `preview`; the bare path redirects by hash. `settingsPageScope.ts` adds the three machine tabs to `SETTINGS_SINGLE_MACHINE_PATHS` and the preview tab to `SETTINGS_DEVICE_ONLY_PATHS`. `settingsSearch.ts` entries point at the tab paths. `isSettingsNavItemActive` already matches child paths.
- Scope line: `SettingsScopeSentence.tsx` gains the "Set up on" wording, the caption and the "You are on" note for single-machine pages. `ConnectionsLibrarySettings.tsx` loses its picker and follows the page's machine; in a project scope with several checkouts the page line carries the checkout choice.
- MCP: `connections/NativeConnectionsPanel.tsx` (list, empty state, add entry points), new `connections/BuiltInToolsBlock.tsx`, `connections/ServerPaste.ts` (pure parser with tests), `connections/serverCatalog.ts` (bundled list), `connections/AddServerFlow.tsx`; `ConnectionEditor.tsx` stays as the by-hand form; `ConnectionMatrix.tsx` stays behind "Compare by AI tool". "Also add on" calls the existing `nativeConnectionApply` per machine from the client; no contract change.
- Devices: `packages/contracts` adds an optional `code` and `missing` to a platform's availability; `apps/server/src/device/LocalDeviceHost.ts` returns codes from `platformReason`, reusing `iosSimulatorSupport.ts`; a new guarded RPC opens a named setup target on the server's machine; a per-machine setting holds the Android SDK folder; `apps/web/src/components/device/DeviceSetup.tsx` maps codes to steps and is shared by the settings tab and the setup wizard.
- Phrases: `apps/web/src/i18n/phrases/*.ts`.

Key decisions

- Tabs sit inside the page, not as four sidebar entries: the sidebar already lists 21 pages.
- The add writes config files only; the snapshot's `runtime` is `"unverified"`. The UI therefore says "Added", never "Connected", until T-02 shows a sign-in that can be checked.
- One-click install is limited to device access tools, where the update path exists. Xcode, runtimes and Android Studio open the right place and recheck.
- The catalog is a file in the app, reviewed like code, because an entry is a command a user will run.

Rejected

- Keeping "All environments" on Integrations as a write scope: it is the source of the confusion in item 4.
- A wizard dialog for the add: the page keeps context (built-in block, existing servers) and the flow is three short parts on one card.
- Editing the shell profile to set `ANDROID_HOME`.

Risks

- Browser sign-in for a web-address server may not complete inside non-interactive threads. T-02 decides the copy and whether a "Sign in" button ships; the fallback is the exact command to run in a terminal.
- Higgsfield's own page gives Claude Code a CLI and skills route and gives the MCP address for connectors and other clients, and needs a paid plan. The entry states both.
- Which providers read which lists is unverified for Muse Code, Grok and Devin (T-02).
- The hash redirect must keep `settingsEntryScope.test.ts`, `settingsScopeNavigation.test.ts` and `settingsSearch.test.ts` green.

## Decisions

### Asked
- D-01 Build order and look: Anton accepts the mockup first (his instruction, November 18, 2026). Pending his answer on the mockup.

### Defaulted (change any before sw-do)
- D-02 Four tabs inside Integrations instead of new sidebar entries.
- D-03 Shared per-machine pattern with Skills (sent to the Skills thread, increment 1399): the word "machine", "Set up on <machine>", one picker, no "All machines" write scope, "Also add on" with a per-machine result, the chips "On this machine", "Needs sign-in", "Offline".
- D-04 Catalog starts with a short checked list (Higgsfield, GitHub, Linear, Notion, Sentry, Figma, Context7, Playwright); entries that fail the vendor check are dropped, not guessed.
- D-05 The Android SDK folder is a SpecWithCode setting per machine.

### Open
- O-01 Sign-in for web-address servers inside Claude Code and Codex threads (T-02).
- O-02 Whether Muse Code, Grok and Devin threads see servers added here (T-02).

## Review

Mockup and spec: adversarial review by Muse Wonderful (`muse-wonder-full-1.0`) at xhigh before Anton sees it. Code: independent review from another model family before merge.

## Tasks

### T-01 Mockup, layout check, adversarial review, Anton's acceptance
- AC: AC-26 | Files: .specweave/increments/1402-integrations-settings-in-tabs-guided-mcp-add-built-in-tools-device-setup-steps/reports/integrations-mockup.html | Test: headless overflow sweep of the mockup at 360, 390, 560, 728, 1100 and 1600 px in light and dark reports 0 findings, and Anton's accept is recorded under D-01

### T-02 Spike: sign-in and reach of an added server
- AC: AC-11, AC-13 | Files: .specweave/increments/1402-integrations-settings-in-tabs-guided-mcp-add-built-in-tools-device-setup-steps/reports/sign-in-spike.md | Test: the report shows, for one web-address server, a Claude Code thread and a Codex thread calling a tool after sign-in, or the exact failure, and lists which providers read which list

### T-03 Split the Integrations page file with no behaviour change
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IntegrationsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/integrations/ | Test: `specweave-studio checks run -- pnpm --dir apps/web vitest run src/components/settings` passes and every file is under 1,500 lines

### T-04 Tabs, routes, deep links and the scope line
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/routes/settings.integrations.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsPageScope.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsScopeSentence.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ConnectionsLibrarySettings.tsx | Test: route tests open each old hash link and land on the right tab; a headless run shows one picker and the caption on each tab

### T-05 MCP servers tab: built-in block, list, empty state
- AC: AC-07, AC-08, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/connections/ | Test: component tests for the empty and filled states; the retired-icons guard passes

### T-06 Guided add: paste box, catalog, tools, other machines
- AC: AC-09, AC-10, AC-11, AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/connections/ | Test: parser unit tests for a web address, three command forms, JSON and TOML; a headless run adds a fixture server to two fixture machines and shows a result per machine

### T-07 Device reason codes
- AC: AC-17 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/, repositories/anton-abyzov/specwithcode/apps/server/src/device/LocalDeviceHost.ts | Test: `LocalDeviceHost.test.ts` covers each code; a snapshot without codes still decodes

### T-08 Device setup steps, open on the machine, SDK folder, details
- AC: AC-18, AC-19, AC-20, AC-21, AC-22, AC-23 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/device/DeviceSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/integrations/DevicesTab.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/device/ | Test: component tests per code, local and remote; a server test refuses an unlisted target

### T-09 Phrases and layout gate
- AC: AC-24, AC-25 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/, repositories/anton-abyzov/specwithcode/apps/web/tests/integrations-layout/ | Test: the headless layout check passes at all six widths in three languages

### T-10 Release and installed check
- AC: AC-27 | Files: none | Test: `bash scripts/release/request-release.sh --by "<thread>"`, then a headless check of the released build on M5
