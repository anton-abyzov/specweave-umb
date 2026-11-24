# Integrations guided MCP add, device setup steps, phrases and release

Split from 1402 on November 24, 2026, during the Board triage. Anton answered "do recommended, yes!" to the proposal to split 1402's unstarted tasks into a new increment so the delivered part can close. 1402 delivered the mockup, the sign-in test, the page split, the four tabs, the MCP server list and the device reason codes (specwithcode #594, #597, #600, #603, #606; v1.0.357 to v1.0.406). This increment holds the rest, unchanged in wording. AC numbers keep 1402's, so earlier reviews and the accepted mockup (`.specweave/increments/1402-integrations-settings-in-tabs-guided-mcp-add-built-in-tools-device-setup-steps/`, 1402 D-01) still map.

## Problem

1402's Problem items 1, 5 and 6 are only partly solved: the MCP tab lists servers but still adds them through the raw form, the Devices tab has reason codes but no guided steps, and the new copy has no layout gate or release check. See 1402's Problem for Anton's words of November 18, 2026.

## Scope

In: the guided add (paste box, catalog, tools and other machines), device setup steps with open-on-machine and the SDK folder, phrases and the layout gate, the release and installed check. Out: everything 1402 delivered; 1402's Out list still applies.

## Acceptance Criteria

- [ ] AC-13: One paste box accepts a web address, a command line (`npx …`, `claude mcp add …`, `codex mcp add …`) or a JSON or TOML settings block, and fills a readable summary: name, kind ("Web address" or "Program on this machine"), and secret values as masked fields. Input it cannot use (SSE servers, tool-only keys, a command-line flag outside the accepted list for that CLI, unreadable text) is refused with the reason, naming the flag or key, and "Enter details by hand".
- [ ] AC-14: For a program server the summary says: "This is a program. It will run on each machine you tick, with your account's rights."
- [ ] AC-15: A catalog of known servers ships with the app (no network). Each entry has a name, one line, how sign-in works, any plan requirement, the vendor page it was checked against and the date. One click opens the same summary. A server already on the machine shows "Added" instead of "Add". Higgsfield is in it.
- [ ] AC-16: "Which AI tools get it" lists the tools on that machine. Tools that can run this kind of server are pre-ticked; a tool SpecWithCode cannot write this kind for is unticked and disabled with the reason ("SpecWithCode cannot add web addresses to Claude Desktop"). One line says a thread sees the server when the tool it runs on is ticked; anything more specific waits for T-02. A second line says other AI tools appear once they are installed on that machine, which answers why only Codex and Claude Code show on a fresh machine.
- [ ] AC-17: The summary names where the server goes ("On M5 only", or "On M5 and m4" once ticked) and offers "Also add on" with the other machines, all unticked to start. A machine that is offline, on a version that cannot preview, or where this sign-in cannot change files is listed disabled with its reason, and no preview or write is ever sent to it. Review shows each ticked machine's own files, or that machine's reason it cannot be added, before Save. After Save each ticked machine shows its own result and its own Undo. Nothing is queued for an offline machine.
- [ ] AC-18: Every write goes through the file-by-file review with masked values. A machine on a version that cannot preview does not offer the guided add; it says "Update SpecWithCode on <machine> to add servers from here."
- [ ] AC-19: After saving, the row says "Added" and never "Connected" or "Needs sign-in": SpecWithCode cannot see sign-in state. A "Sign in once" step shows what T-02 proves: an in-app button if one works, otherwise the exact command per tool with Copy, built from the server's final name (`claude mcp login <name>`, `codex mcp login <name>`).
- [ ] AC-20: Pasting or picking a server that overlaps a built-in tool shows "This overlaps with something built in", says in one sentence what the built-in does and what the server adds, links to the built-in, and offers "Add anyway".
- [ ] AC-25: Each code shows one step from the table under Approach: a title, one sentence, the in-app path where one exists, one primary action and "Check again", which always runs a fresh check. The iOS line never says "Xcode is installed" unless Xcode.app was found and its `simctl` answered.
- [ ] AC-26: An action runs on the machine being set up. From another machine the label names it ("Open App Store on M5"). Where that machine cannot open a window, or the sign-in lacks the right, the step reads "Do this on M5" with a Copy link button in place of the action. "Choose SDK folder" from another machine uses the app's folder browser for that machine.
- [ ] AC-27: The server opens only a fixed list of named targets; the client never sends a URL or path to open.
- [ ] AC-28: "Choose SDK folder" saves the folder for that machine in SpecWithCode settings and the Android check uses it. No shell profile is edited.
- [ ] AC-29: Raw tool output shows only under "Details" for that platform.
- [ ] AC-30: "Agent device access" keeps today's switch rules in the settings tab and the setup wizard. Beside it: "Turn on Device hub first" when the hub is off; "Turning this on installs its tools" in place of "Not installed" when its tools are missing. When no simulator is ready, a line under the row says agents cannot use a device until one is set up. With Device hub off, the simulator steps are replaced by one line, "Turn on Device hub to set up simulators.", and the remaining rows stay.
- [ ] AC-31: A headless check at 360, 390, 560, 728, 1100 and 1600 px, light and dark, in English, German and Russian, reports: no element wider than its container, no clipped label, no text under 12 px, text contrast of at least 4.5 to 1, buttons and links in rows at least 32 px tall, and every control reachable and operable by keyboard. Disabled controls are exempt from the contrast and reach checks, must carry the real disabled state so Enter and Space do nothing, and are the only exemption. The same check asserts the AC-09 height budget.
- [ ] AC-32: All new copy has phrases in every shipped locale.
- [ ] AC-34: Released through `scripts/release/request-release.sh`; the released build shows the tabs, the add of one catalog entry and one device step on M5.

## Approach

As in 1402's Approach (files, MCP and Devices bullets, risks), from the umbrella root under `repositories/anton-abyzov/specwithcode/`. The device steps table:

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

## Decisions

### Asked
- D-01 (1402 D-01): Anton accepted the mockup November 18, 2026 ("Accept, build it"), including dropping "All environments" on Integrations.
- D-02: split from 1402 → Anton, November 24, 2026: "do recommended, yes!"
### Defaulted (change any before sw-do)
- D-03 (1402 D-04): the catalog starts with a short checked list (Higgsfield, GitHub, Linear, Notion, Sentry, Figma, Context7); entries that fail the vendor check are dropped.
- D-04 (1402 D-05): the Android SDK folder is a SpecWithCode setting per machine.
### Open
- none

## Review

- Reviewer: cross-family, by the project's reviewer order at the time of each PR (Gemini 4 Neon first, GPT-6.2 Sol second, never Grok).
- Depth: deep
- Required: yes

## Tasks

### T-01 Guided add: paste box, catalog, tools, other machines (1402 T-06)
- AC: AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/connections/, repositories/anton-abyzov/specwithcode/packages/contracts/src/nativeConnections.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/connections/NativeConnectionEdit.ts | Test: parser unit tests for a web address, three command forms, JSON, TOML, a refused SSE block, one refused flag per CLI and a name that overlaps a built-in; snapshot tests of the sign-in command per tool for a renamed server; a fixture where an old-version second machine and a no-write second machine receive no call before or after Save, and a refused machine is shown in Review; a catalog test that every entry has a checked date and source page; a test that the client's tool-capability table equals the writer's; a headless run that adds a fixture server to two fixture machines, shows each machine's files before Save and a result and Undo per machine; a component test for the older-machine message and for the AC-16 line

### T-02 Device setup steps, open on the machine, SDK folder, details (1402 T-08)
- AC: AC-25, AC-26, AC-27, AC-28, AC-29, AC-30 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/, repositories/anton-abyzov/specwithcode/apps/web/src/components/device/DeviceSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/integrations/DevicesTab.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/device/ | Test: component tests per code for local, remote and cannot-open; a server test refuses an unlisted target; a test that a remote host's status never changes the machine's steps

### T-03 Phrases and layout gate (1402 T-09)
- AC: AC-31, AC-32 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/, repositories/anton-abyzov/specwithcode/apps/web/tests/integrations-layout/ | Test: the headless layout check passes at all six widths in three languages with the contrast, target and keyboard checks, and asserts each tab is at most 1,800 px tall at 560 × 800

### T-04 Release and installed check (1402 T-10)
- AC: AC-34 | Files: none | Test: `bash scripts/release/request-release.sh --by "<thread>"`, then a headless check of the released build on M5
