# Integrations settings in tabs: guided MCP add, built-in tools, device setup steps

## Problem

Anton, on M5 in Settings > Integrations (November 18, 2026, four screenshots):

1. "I want to add an MCP. At first, it's not really clear how I'm going to add it." The add form is raw config: Name, Command or URL, "Arguments, one per line", "Environment, KEY=value per line", two unticked checkboxes, Preview. There is no path for a known server such as Higgsfield, and no way to paste the link or command a vendor's page gives.
2. The empty state reads "No MCP declarations found in the inspected configuration files." It does not say what to do next.
3. Chrome and computer use are built into SpecWithCode, but the page never says so. The only explanation (`ComputerUseConnectionNote`) renders under a `computer-use` row, so it is invisible when the list is empty.
4. Scope is unclear. The page says "Applying settings on M5", the MCP section carries a second picker (the small "M5" tag, `ConnectionsLibrarySettings`), and the page mixes three scopes: agent access and Device hub are per machine, MCP is files on one machine, and the Browser preview, recording and link defaults are saved in this app window and ignore the header. With "All environments" picked, Device hub writes to every machine while MCP silently shows the first one.
5. Devices: with Device hub on, the page shows "Android SDK was not found. Install it with Android Studio or set ANDROID_HOME…" and raw lines such as "[apple-utils] Failed to run `xcrun simctl list devices --json`", with one Refresh button and no next step. "Agent device access" shows "Not installed" with a disabled switch and no reason. The iOS line said "Xcode is installed" above a failed `simctl`, so the diagnosis itself can be wrong.
6. "Think about creating a paginated view here." Integrations is one long scroll: agent access, MCP, ten browser and recording rows, Devices.

## Scope

In: Settings > Integrations in the web and desktop app. Four tabs, one scope line per tab, a new MCP servers tab (built-in block, server list, guided add with a catalog and paste box, the raw form as "Enter details by hand"), guided setup steps in Devices, structured device reason codes, layout that holds from 360 px to 1600 px, phrases for all shipped locales. The Project page's "Connections" section renders the same server panel, so it gets the new list and add flow too.

Out: the native iPhone and Android apps (they have no Integrations page; confirmed by search in `apps/mobile` and `apps/ios`). A remote catalog service. The scope sentence on other settings pages (Providers, Models and the rest keep today's wording). Any change to the Skills page (increment 1399 owns it; the two share the pattern in D-03). The "SpecWithCode-managed connections" form on the Project page.

## Acceptance Criteria

Tabs and scope

- [ ] AC-01: Integrations has four tabs: "Agent access", "MCP servers", "Devices", "Preview and recording". Each has its own URL, the sidebar item "Integrations" stays active on all of them, and the tab strip follows the tab keyboard pattern (arrow keys move, each tab names its panel).
- [ ] AC-02: Every existing `/settings/integrations#<anchor>` link and every settings-search result opens the tab that holds that row and scrolls to it.
- [ ] AC-03: On the three per-machine tabs the scope line reads "Set up on <machine>" with the caption "Each machine keeps its own. Changes here only affect <machine>." There is one machine picker per page and none inside a section. "All environments" is not offered. With one machine the name is plain text. The new wording applies to these tabs only.
- [ ] AC-04: "Preview and recording" shows "Only in this app window" and no machine picker. In the browser client, where these settings do not exist, the tab shows "Only available in the desktop app" as today.
- [ ] AC-05: When the machine being set up is not the one the user is sitting at, the scope line says so ("You are on m4").
- [ ] AC-06: The Integrations tabs never take a project scope (the route already drops it). Rows a project can override say "Projects can override it" and the override stays on the Project page.
- [ ] AC-07: Every row that exists today exists in exactly one tab: Agent access holds Agent browser access, Agent computer access with its permissions and allowed apps, Browser profile for agents, and a link to the Chrome page; Preview and recording holds the browser profile manager, viewport, zoom, appearance, frame rate, key presses, mouse presses, link target and floating preview; Devices holds Device hub, simulator setup, Agent device access with its allowed devices, the simulator limit, tool updates and device hosts.
- [ ] AC-08: Machine states: an offline machine shows one card ("M5 is offline. Its settings show when it reconnects.") in place of the tab's rows; a sign-in without the right to change settings shows the rows disabled under one line that says so; a row locked by team rules keeps today's message.
- [ ] AC-09: At a 560 × 800 px viewport each tab's default state is at most 1,800 px tall: allowed apps and allowed devices collapse after four entries, the catalog shows six entries until "Show all", and the profile manager and device hosts open on demand.

MCP servers

- [ ] AC-10: A "Built into SpecWithCode" block lists Chrome, Computer use, In-app browser and Simulators, each with one sentence, its live status on the selected machine ("On", "Off", "Paired", "Needs setup", "Mac only") and a link to where it is set up: Chrome to the Chrome page with the same machine, Computer use and In-app browser to Agent access, Simulators to Devices. It says these are part of the app and are never added as MCP servers. It shows whether or not the list is empty.
- [ ] AC-11: The server list is the default view of today's data, one row per server name: its kind, the tools that have it, and "Off" when it is turned off everywhere. "Turn off", "Turn on" and "Remove" act on every tool that has it: one combined review lists each tool's file, and the result shows each tool with its own Undo. Entries that come from a plugin, a project folder or a tool SpecWithCode cannot write show where they come from and keep today's actions. The Plugins section, copy between tools and "Add to all" stay under "Compare by AI tool", which is today's matrix unchanged. A search field shows above eight servers. "Compare by AI tool" is offered whether or not the list is empty. On the Project page the same list marks entries that come from the project's folder as "This project", and the guided add there writes the same user-level entries as on this tab and says "Added for every project on <machine>".
- [ ] AC-12: The empty state says "No MCP servers on <machine> yet" and points at the add box. The sentence about "declarations" and "inspected configuration files" appears only under "About this list".
- [ ] AC-13: One paste box accepts a web address, a command line (`npx …`, `claude mcp add …`, `codex mcp add …`) or a JSON or TOML settings block, and fills a readable summary: name, kind ("Web address" or "Program on this machine"), and secret values as masked fields. Input it cannot use (SSE servers, tool-only keys, a command-line flag outside the accepted list for that CLI, unreadable text) is refused with the reason, naming the flag or key, and "Enter details by hand".
- [ ] AC-14: For a program server the summary says: "This is a program. It will run on each machine you tick, with your account's rights."
- [ ] AC-15: A catalog of known servers ships with the app (no network). Each entry has a name, one line, how sign-in works, any plan requirement, the vendor page it was checked against and the date. One click opens the same summary. A server already on the machine shows "Added" instead of "Add". Higgsfield is in it.
- [ ] AC-16: "Which AI tools get it" lists the tools on that machine. Tools that can run this kind of server are pre-ticked; a tool SpecWithCode cannot write this kind for is unticked and disabled with the reason ("SpecWithCode cannot add web addresses to Claude Desktop"). One line says a thread sees the server when the tool it runs on is ticked; anything more specific waits for T-02. A second line says other AI tools appear once they are installed on that machine, which answers why only Codex and Claude Code show on a fresh machine.
- [ ] AC-17: The summary names where the server goes ("On M5 only", or "On M5 and m4" once ticked) and offers "Also add on" with the other machines, all unticked to start. A machine that is offline, on a version that cannot preview, or where this sign-in cannot change files is listed disabled with its reason, and no preview or write is ever sent to it. Review shows each ticked machine's own files, or that machine's reason it cannot be added, before Save. After Save each ticked machine shows its own result and its own Undo. Nothing is queued for an offline machine.
- [ ] AC-18: Every write goes through the file-by-file review with masked values. A machine on a version that cannot preview does not offer the guided add; it says "Update SpecWithCode on <machine> to add servers from here."
- [ ] AC-19: After saving, the row says "Added" and never "Connected" or "Needs sign-in": SpecWithCode cannot see sign-in state. A "Sign in once" step shows what T-02 proves: an in-app button if one works, otherwise the exact command per tool with Copy, built from the server's final name (`claude mcp login <name>`, `codex mcp login <name>`).
- [ ] AC-20: Pasting or picking a server that overlaps a built-in tool shows "This overlaps with something built in", says in one sentence what the built-in does and what the server adds, links to the built-in, and offers "Add anyway".
- [ ] AC-21: The raw form remains as "Enter details by hand" with today's fields and validation.
- [ ] AC-22: No lock or brain icon is used; secrets use the masked-field glyph. `retiredIcons.guard.test.ts` passes.

Devices

- [ ] AC-23: Setup steps describe the selected machine's own host only. Remote device hosts keep their status in the Device hosts list and never change the steps or the "Ready" state shown for the machine.
- [ ] AC-24: Each platform reports a reason code as well as text, produced on the server: iOS `not_mac`, `xcode_missing`, `xcode_not_selected`, `xcode_setup_unfinished`, `ios_runtime_missing`, `ios_simulator_missing`; Android `android_studio_missing`, `android_sdk_missing`, `android_tools_missing` (with the missing parts), `android_avd_missing`. A machine on an older version, which sends text only, shows that text and Check again.
- [ ] AC-25: Each code shows one step from the table under Approach: a title, one sentence, the in-app path where one exists, one primary action and "Check again", which always runs a fresh check. The iOS line never says "Xcode is installed" unless Xcode.app was found and its `simctl` answered.
- [ ] AC-26: An action runs on the machine being set up. From another machine the label names it ("Open App Store on M5"). Where that machine cannot open a window, or the sign-in lacks the right, the step reads "Do this on M5" with a Copy link button in place of the action. "Choose SDK folder" from another machine uses the app's folder browser for that machine.
- [ ] AC-27: The server opens only a fixed list of named targets; the client never sends a URL or path to open.
- [ ] AC-28: "Choose SDK folder" saves the folder for that machine in SpecWithCode settings and the Android check uses it. No shell profile is edited.
- [ ] AC-29: Raw tool output shows only under "Details" for that platform.
- [ ] AC-30: "Agent device access" keeps today's switch rules in the settings tab and the setup wizard. Beside it: "Turn on Device hub first" when the hub is off; "Turning this on installs its tools" in place of "Not installed" when its tools are missing. When no simulator is ready, a line under the row says agents cannot use a device until one is set up. With Device hub off, the simulator steps are replaced by one line, "Turn on Device hub to set up simulators.", and the remaining rows stay.

Layout, access and language

- [ ] AC-31: A headless check at 360, 390, 560, 728, 1100 and 1600 px, light and dark, in English, German and Russian, reports: no element wider than its container, no clipped label, no text under 12 px, text contrast of at least 4.5 to 1, buttons and links in rows at least 32 px tall, and every control reachable and operable by keyboard. Disabled controls are exempt from the contrast and reach checks, must carry the real disabled state so Enter and Space do nothing, and are the only exemption. The same check asserts the AC-09 height budget.
- [ ] AC-32: All new copy has phrases in every shipped locale.

Delivery

- [ ] AC-33: Anton accepts the mockup before any app code is written.
- [ ] AC-34: Released through `scripts/release/request-release.sh`; the released build shows the tabs, the add of one catalog entry and one device step on M5.

## Approach

Order: mockup and acceptance, the sign-in test, a no-behaviour split of the page file, tabs and scope, MCP tab, device codes and steps, phrases, release.

Files (from the umbrella root, under `repositories/anton-abyzov/specwithcode/`):

- `apps/web/src/components/settings/IntegrationsSettings.tsx` is 1,639 lines, over the 1,500 limit. Split first into `integrations/AgentAccessTab.tsx`, `integrations/McpServersTab.tsx`, `integrations/DevicesTab.tsx`, `integrations/PreviewRecordingTab.tsx`, `integrations/BrowserProfilesSetting.tsx` and `integrations/IntegrationsTabs.tsx`. The Agent access rows render from `ProjectDefaultsSettings.tsx` (category "integrations"); that file keeps them and the tab mounts it.
- Routes: `apps/web/src/routes/settings.integrations.tsx` becomes a layout with child routes `access`, `mcp`, `devices`, `preview` (the generated `routeTree.gen.ts` changes with it); the bare path redirects by hash. `settingsPageScope.ts` adds the three machine tabs to `SETTINGS_SINGLE_MACHINE_PATHS` and the preview tab to `SETTINGS_DEVICE_ONLY_PATHS`. `settingsSearch.ts` entries point at the tab paths.
- Scope line: `SettingsScopeSentence.tsx` gets an Integrations variant ("Set up on", caption, "You are on"); other pages keep their sentence. `ConnectionsLibrarySettings.tsx` loses its picker and follows the page's machine.
- MCP: `connections/NativeConnectionsPanel.tsx` (list, empty state, add entry points, older-machine message), new `connections/BuiltInToolsBlock.tsx`, `connections/ServerList.tsx`, `connections/serverPaste.ts` (pure parser with tests), `connections/serverCatalog.ts` (bundled list), `connections/AddServerFlow.tsx`; `ConnectionEditor.tsx` stays as the by-hand form; `ConnectionMatrix.tsx` stays behind "Compare by AI tool". Which tools can run a kind comes from the same rule the writer uses (`toolEntry` in `NativeConnectionEdit.ts`), shared through contracts so the client and server cannot disagree. "Also add on" calls the existing `nativeConnectionApply` with `preview` per machine, then per machine on Save.
- Devices: `packages/contracts` adds an optional `code` and `missing` to a platform's availability, a named setup target, and a per-machine Android SDK folder setting. `apps/server/src/device/LocalDeviceHost.ts` returns codes from these checks: Xcode.app present, the selected developer folder, `simctl` answering, `simctl list runtimes` against devices, Android Studio present (per operating system: the app bundle on macOS, the install folder or `studio.sh` on Linux, Program Files on Windows), the SDK parts it already inspects, and `avdmanager list avd`. Where Android Studio cannot be detected either way, the SDK step offers both "Get Android Studio" and "Choose SDK folder". "Check again" bypasses the ten-minute cache in `iosSimulatorSupport.ts`. A guarded RPC opens a named setup target on the server's machine. `apps/web/src/components/device/DeviceSetup.tsx` maps codes to steps for the local host only and is shared by the settings tab and the setup wizard.
- List actions across tools: the client previews each tool's entry with the existing single-entry apply, shows one combined review, then applies per entry and keeps each change id for its own Undo. No contract change.
- Phrases: `apps/web/src/i18n/phrases/*.ts`.

Device steps

| Code | Title | Sentence and path | Action |
|---|---|---|---|
| `not_mac` | iOS Simulator needs a Mac | Use a Mac from your machines as a device host. | Add a Mac as a device host |
| `xcode_missing` | Install Xcode | The iOS Simulator comes with Xcode, a free download from the App Store. | Open App Store |
| `xcode_not_selected` | Point the developer tools at Xcode | Xcode is installed, but the command line tools are selected instead. Run `sudo xcode-select -s /Applications/Xcode.app` in Terminal. | Copy command |
| `xcode_setup_unfinished` | Open Xcode once | Xcode has to finish installing its parts and ask you to accept its license. | Open Xcode |
| `ios_runtime_missing` | Add an iOS Simulator | Xcode > Settings > Components > iOS > Get | Open Xcode |
| `ios_simulator_missing` | Create a simulator | Xcode > Window > Devices and Simulators > Simulators > + | Open Xcode |
| `android_studio_missing` | Install Android Studio | The emulator comes with Android Studio, a free download from Google. Run it once and finish its setup. | Get Android Studio |
| `android_sdk_missing` | Tell SpecWithCode where the Android SDK is | Android Studio is installed, but its SDK was not found in the usual place. | Choose SDK folder |
| `android_tools_missing` | Add the missing SDK tools | Lists the missing parts. Android Studio > Settings > Languages & Frameworks > Android SDK > SDK Tools | Open Android Studio |
| `android_avd_missing` | Create a virtual device | Android Studio > More Actions > Virtual Device Manager > + | Open Android Studio |

Key decisions

- Tabs sit inside the page, not as four sidebar entries: the sidebar already lists 21 pages.
- The add writes config files only; the snapshot's `runtime` is `"unverified"`. The UI says "Added" and shows sign-in as a step, never as a state.
- One-click install is limited to device access tools, where the update path exists. Xcode, runtimes and Android Studio open the right place and recheck.
- The catalog is a file in the app, reviewed like code, because an entry is a command a user will run.

Rejected

- Keeping "All environments" on Integrations as a write scope: it is the source of the confusion in item 4.
- A wizard dialog for the add: the page keeps context (built-in block, existing servers) and the flow is three short parts on one card.
- Editing the shell profile to set `ANDROID_HOME`.
- A flat server list that replaces the matrix: copy between tools, plugins and per-tool states need it.

Risks

- Browser sign-in for a web-address server may not complete inside non-interactive threads. Both CLIs have a sign-in command (`claude mcp login <name>` in Claude Code 2.1.302, `codex mcp login <name>` in Codex 0.162.1, checked on m4). T-02 decides whether a "Sign in" button that runs it on the machine ships; the mockup draws the fallback (commands with Copy).
- Higgsfield's own page gives Claude Code a CLI and skills route and gives the MCP address for connectors and other clients, and needs a paid plan. The entry states both.
- Which providers' threads see a server is unverified beyond Claude Code and Codex (T-02).
- The hash redirect must keep `settingsEntryScope.test.ts`, `settingsScopeNavigation.test.ts` and `settingsSearch.test.ts` green.

## Decisions

### Asked
- D-01 Build order and look: Anton accepts the mockup first (his instruction, November 18, 2026). Pending his answer on the mockup.

### Defaulted (change any before sw-do)
- D-02 Four tabs inside Integrations instead of new sidebar entries.
- D-03 Shared per-machine pattern with Skills (sent to the Skills thread, increment 1399): the word "machine", "Set up on <machine>", one picker, no "All machines" write scope, "Also add on" with a per-machine result.
- D-04 Catalog starts with a short checked list (Higgsfield, GitHub, Linear, Notion, Sentry, Figma, Context7). No browser-automation server is in it. Entries that fail the vendor check are dropped, not guessed.
- D-05 The Android SDK folder is a SpecWithCode setting per machine.
- D-06 The sign-in test (T-02) runs after acceptance because it changes config on a machine and signs in to a vendor account; the mockup shows the state that needs no proof.

### Open
- O-01 Sign-in for web-address servers inside Claude Code and Codex threads (T-02).
- O-02 Which other providers' threads see servers added here (T-02).

## Review

Mockup and spec: adversarial review by Muse Wonderful (`muse-wonder-full-1.0`) at xhigh before Anton sees it. Round 1 (November 18, 2026): fix first, 7 high and 11 medium findings. Round 2: fix first, 1 high, 8 medium and 3 low. Both are answered in this revision; see `reports/review-muse-wonder-full-1.0.md`, `reports/reviews/review-muse-wonder-full-1.0-2.md` and `reports/review-response.md`. Code: independent review from another model family before merge.

## Tasks

### T-01 Mockup, layout check, adversarial review, Anton's acceptance
- AC: AC-33 | Files: .specweave/increments/1402-integrations-settings-in-tabs-guided-mcp-add-built-in-tools-device-setup-steps/reports/integrations-mockup.html | Test: the headless audit of the mockup at 360, 390, 560, 728, 1100 and 1600 px in light and dark reports 0 findings for overflow, clipping, text size, contrast, target height and keyboard reach, and Anton's accept is recorded under D-01

### T-02 Test sign-in and reach of an added server
- AC: AC-16, AC-19 | Files: .specweave/increments/1402-integrations-settings-in-tabs-guided-mcp-add-built-in-tools-device-setup-steps/reports/sign-in-test.md | Test: the report shows, for one web-address server, a Claude Code thread and a Codex thread calling a tool after sign-in, or the exact failure, and lists which providers read which list; the AC-16 and AC-19 strings are fixed from it

### T-03 Split the Integrations page file with no behaviour change
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/IntegrationsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/integrations/, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectDefaultsSettings.tsx | Test: from `apps/web`, `IntegrationsSettings.test.tsx` and `IntegrationsSettings.logic.test.ts` pass unchanged and every file is under 1,500 lines

### T-04 Tabs, routes, deep links, scope line and machine states
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/routes/settings.integrations.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/settings.integrations.access.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/settings.integrations.mcp.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/settings.integrations.devices.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/settings.integrations.preview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectDefaultsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routeTree.gen.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsPageScope.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsScopeSentence.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ConnectionsLibrarySettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/integrations/ | Test: `settingsEntryScope.test.ts`, `settingsScopeNavigation.test.ts` and `settingsSearch.test.ts` pass with a case per old hash link; a component test per machine state; Providers and Models scope sentence snapshots unchanged

### T-05 MCP servers tab: built-in block, server list, empty state
- AC: AC-10, AC-11, AC-12, AC-21, AC-22 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/connections/, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectConnections.tsx | Test: component tests for empty, filled, plugin-provided and off entries on the settings tab and the Project page; a case per built-in status (On, Off, Paired, Needs setup, Mac only); a two-tool Turn off that shows one review and an Undo per tool; `NativeConnectionsPanel.test.tsx` and `ConnectionMatrix.test.tsx` pass; the retired-icons guard passes

### T-06 Guided add: paste box, catalog, tools, other machines
- AC: AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/connections/, repositories/anton-abyzov/specwithcode/packages/contracts/src/nativeConnections.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/connections/NativeConnectionEdit.ts | Test: parser unit tests for a web address, three command forms, JSON, TOML, a refused SSE block, one refused flag per CLI and a name that overlaps a built-in; snapshot tests of the sign-in command per tool for a renamed server; a fixture where an old-version second machine and a no-write second machine receive no call before or after Save, and a refused machine is shown in Review; a catalog test that every entry has a checked date and source page; a test that the client's tool-capability table equals the writer's; a headless run that adds a fixture server to two fixture machines, shows each machine's files before Save and a result and Undo per machine; a component test for the older-machine message and for the AC-16 line

### T-07 Device reason codes on the server
- AC: AC-23, AC-24 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/, repositories/anton-abyzov/specwithcode/apps/server/src/device/LocalDeviceHost.ts, repositories/anton-abyzov/specwithcode/apps/server/src/device/iosSimulatorSupport.ts | Test: `LocalDeviceHost.test.ts` has a fixture per code; a forced recheck ignores a cached "no"; a snapshot without codes still decodes

### T-08 Device setup steps, open on the machine, SDK folder, details
- AC: AC-25, AC-26, AC-27, AC-28, AC-29, AC-30 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/, repositories/anton-abyzov/specwithcode/apps/web/src/components/device/DeviceSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/integrations/DevicesTab.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/device/ | Test: component tests per code for local, remote and cannot-open; a server test refuses an unlisted target; a test that a remote host's status never changes the machine's steps

### T-09 Phrases and layout gate
- AC: AC-31, AC-32 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/, repositories/anton-abyzov/specwithcode/apps/web/tests/integrations-layout/ | Test: the headless layout check passes at all six widths in three languages with the contrast, target and keyboard checks, and asserts each tab is at most 1,800 px tall at 560 × 800

### T-10 Release and installed check
- AC: AC-34 | Files: none | Test: `bash scripts/release/request-release.sh --by "<thread>"`, then a headless check of the released build on M5
