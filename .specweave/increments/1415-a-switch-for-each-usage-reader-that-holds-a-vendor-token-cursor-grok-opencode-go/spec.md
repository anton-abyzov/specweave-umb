# A switch for each usage reader that holds a vendor token: Cursor, Grok, OpenCode Go

Split out of 1411 on November 18, 2026, after its second review showed the switches are a design of their own (`.specweave/increments/1411-all-subscriptions-and-limits-in-one-place-what-is-left-when-it-resets-and-when-it-renews-for-every-provider/reports/reviews/review-muse-wonder-full-1.0-2.md`, finding N5). Builds after 1411, which gives a reader that is off a row on the board. Version 2: reviewed once, with 1411's third round (`reports/reviews/review-muse-wonder-full-1.0-1.md`, "fix first", 3 must-fix and 4 should-fix; answers in `reports/review-responses.md`). The fixes are applied here and not reviewed again.

## Problem

Three usage readers take a token the vendor's CLI stored and call an address the vendor does not document. App paths are in `repositories/anton-abyzov/specwithcode` at `origin/main` `c46e2efe5`.

- Cursor: the Keychain on a Mac, `auth.json` elsewhere, or `CURSOR_AUTH_TOKEN` (`apps/server/src/provider/cursorUsageLimits.ts:143-160`). Only the Keychain read has a switch, `cursorKeychainUsageEnabled`, off by default (`packages/contracts/src/settings.ts:2355-2357`), drawn only on a Mac (`apps/web/src/components/settings/UsageProviderSettings.tsx:148-162`). Cursor's account history reads the same login on a second path, with the same Mac-only switch (`apps/server/src/usage/UsageService.ts:752-784`).
- Grok: `auth.json` or `GROK_AUTH`, read without asking (`apps/server/src/provider/grokUsageLimits.ts:120-126`). The same read gives the account's email (`:136-157`).
- OpenCode Go: `auth.json`, `OPENCODE_AUTH_CONTENT` or `OPENCODE_API_KEY`, read without asking; a key stored in the file wins over the environment key (`apps/server/src/provider/openCodeUsageLimits.ts:55-68`). The account's identity is a fingerprint of that key (`:106-116`).

Anton, November 18, 2026, asked whether these readers stay: "Keep, each behind its own switch".

## Scope

In: a switch per reader per machine, off until the person turns it on; what each reader does with its switch off; what the board shows then; the way from that row to the switch.

Out: Copilot's reader (1411 D-05: it stays as it is). Claude's and Codex's readers, which use the CLI's own call. Any new read.

## Acceptance Criteria

- [ ] AC-01: Settings gain `grokUsageEnabled` and `openCodeGoUsageEnabled`, per machine, off by default, beside the existing `cursorKeychainUsageEnabled`, whose stored value and meaning are kept. The new fields are defined in a new contracts file that `settings.ts` (2,901 lines) only imports.
- [ ] AC-02: With its switch off and no vendor token in the environment, a reader returns before it opens any file or Keychain item, Grok's configuration files included (`apps/server/src/provider/grokUsageLimits.ts:102-119`), by the table "What each reader does" below. A token the person put in the environment for that vendor is read without the switch, since setting it is the consent, except where the table says otherwise. Cursor's account history obeys the same switch on every platform: with it off, the scan reads no Keychain item and no `auth.json` and returns today's off message and its `enableCursorKeychain` action (`UsageService.ts:752-767`); the cases that already skip the login (`:748-751`) are unchanged. The order of checks in each reader: causes that exist today and need no login read come first and keep their own reading (OpenCode disabled or on an external server, `apps/server/src/provider/openCodeUsageLimits.ts:40`; Cursor with only `CURSOR_API_KEY`, `cursorUsageLimits.ts:151-152`; Grok with `XAI_API_KEY`, `grokUsageLimits.ts:77`), then a vendor token in the environment, then the switch. Tests cover every cell and that order.
- [ ] AC-03: A reader that is off publishes the shape Cursor's off state has today: `unavailable` with the existing reason `unsupported`, the message "Usage reading is off for <vendor> on this machine." and a new optional flag `readerOff`, beside the existing `unmetered` (`packages/contracts/src/providerUsageLimits.ts:131`). No new reason is added. Cursor's present text ("Enable Cursor account usage in SpecWithCode to read its Keychain login.", `cursorUsageLimits.ts:164-168`) changes to this one and its tests with it. Bars read earlier are replaced, not kept (`apps/server/src/provider/providerUsageLimits.ts:383-400`). The model picker shows the message as "unreported" and the pooled Limits view stays silent, as they do for Cursor's off state today; both are intended.
- [ ] AC-04: No identity is kept while a reader is off and no vendor token is in the environment: Grok's row then has no email and OpenCode Go's no fingerprint, and the app cannot notice that the Grok account changed (`apps/server/src/provider/subscriptionIdentity.ts:59-66`). With a token in the environment the reader runs and identity is published as today. Resets that happen while a reader is off are not seen and not filled in afterwards. The renewal day, price and reset history saved under the account's key stay stored and show again when the switch is turned on and the same account is read; a test turns a switch off and on and finds the day. A different account read after that gets its own key.
- [ ] AC-05: The three switches are in Settings > Providers, in the usage block (`apps/web/src/components/settings/ProviderSettingsPanel.tsx:1350-1357`), on every platform, each with one sentence on what it reads: "Reads Cursor's sign-in from the Keychain to show your account history and plan limits" on a Mac and "from Cursor's login file" elsewhere; "Reads Grok's login file to ask xAI for your usage. With it off, SpecWithCode does not know which Grok account this is"; "Reads OpenCode's login file to ask OpenCode for your Go usage".
- [ ] AC-06: On the Subscriptions board, a row whose reading carries `readerOff` (1411 AC-01 draws it in `NoReadingRow.tsx`) shows that message, the vendor's usage link when one is known, and "Show it here", which opens Settings > Providers on that row's machine with the switch in view. A row that is `unsupported` for another cause does not offer it. Settings search finds each switch by name on every platform: the Cursor entry loses `macProviderSettingsOnly` and each of the three gets a `targetId` (`apps/web/src/components/settings/settingsSearch.ts:891-897`, `:58`).
- [ ] AC-07: On the update that brings this, Grok and OpenCode Go stop being read until switched on, and so does Cursor, limits and account history both, on Windows, on Linux and on a Mac whose Cursor CLI keeps its login in a file (`AGENT_CLI_CREDENTIAL_STORE=file`, `cursorUsageLimits.ts:162-194`). The release notes say so.
- [ ] AC-08: Shipped in a released build after an independent Extra High review and green Checks, with headless screenshots of the three switches and of a row that is off, from a new fixture built like `apps/web/tests/subscription-resets/`, with fictional data.

### What each reader does (AC-02)

| Reader | Switch on | Switch off, vendor token in the environment | Switch off, no such token |
|---|---|---|---|
| Cursor | As today | `CURSOR_AUTH_TOKEN` is used (`cursorUsageLimits.ts:149`) | Off. No Keychain and no `auth.json` read, on any platform |
| Grok | As today | `GROK_AUTH` is used (`grokUsageLimits.ts:120-121`) | Off. No `auth.json` read, so no email either |
| OpenCode Go | As today | `OPENCODE_AUTH_CONTENT` is used, since it replaces the file (`openCodeUsageLimits.ts:57`). `OPENCODE_API_KEY` alone does not turn it on: OpenCode prefers a key stored in the file, and reading the file to find out is the read the switch forbids | Off. No `auth.json` read |

## Approach

Each reader takes its switch as an input, the way Cursor's does (`apps/server/src/provider/Drivers/CursorDriver.ts:233-238`), and returns the off reading before it touches a file. The settings fields and the three sentences live in new files; `packages/client-runtime/src/state/server.ts` (1,493 lines) and `ProviderSettingsPanel.tsx` (1,450 lines) get at most a call line each, and `settingsSearch.ts` (1,692 lines, already over the limit) entries only and no logic.

Grok's switch gates the whole of `readGrokAccount`. That read has one caller, which only adds the email and the limits to a snapshot that is already signed in (`apps/server/src/provider/Drivers/GrokDriver.ts:149-157`); sign-in state and the model list come from the CLI's own commands (`apps/server/src/provider/GrokProvider.ts:403`, `:469-470`) and do not change.

Risks: these readers call addresses the vendors do not document and may stop working at any time; a row then says "Could not read limits", as today. With Grok's switch off the app shows a signed-in Grok with no email and cannot tell one Grok account from another.

Rejected: keeping the last identity a reader published while it is off (a stale account on the board after the person signs in to another); a new `unavailable` reason (a wire change every client must tolerate); one switch for all three.

## Decisions

### Asked
- D-01 Readers that hold the vendor's token → Anton, November 18, 2026: "Keep, each behind its own switch". He was told Grok and OpenCode Go go off on update.

### Defaulted (change any before sw-do)
- D-02 A vendor token in the environment counts as consent, except `OPENCODE_API_KEY` alone.
- D-03 No identity is kept while a reader is off.
- D-04 Cursor's switch now also covers its login file, for limits and account history: Windows, Linux and a Mac with a file login go off on update too. He was told about Grok and OpenCode Go, not about this; the report of November 18, 2026 says so.
- D-05 The off state reuses the reason `unsupported` with a message and an optional flag, as `unmetered` does.

### Open
None. H1 (what else depends on Grok's read) is answered in Approach: nothing but the email and the limits.

## Review

Muse Wonder Full 1.0 at Extra High, November 18, 2026, with 1411's round 3: "fix first", 3 must-fix (Cursor's second reader, untasked screenshots, the open H1) and 4 should-fix. Every finding was checked at `c46e2efe5` and answered in `reports/review-responses.md`; this version applies them and has not been reviewed again. The build's own review reads the code.

## Tasks

File tags: [exists] at `c46e2efe5`, [1411 T-NN] created by that task, [new] created here.

### T-01 The two new settings
- AC: AC-01 | Files: packages/contracts/src/usageReaderSettings.ts [new], packages/contracts/src/usageReaderSettings.test.ts [new], packages/contracts/src/settings.ts [exists], packages/contracts/src/providerUsageLimits.ts [exists], packages/contracts/src/providerUsageLimits.test.ts [exists] | Test: cd repositories/anton-abyzov/specwithcode && vp test run packages/contracts/src/usageReaderSettings.test.ts packages/contracts/src/providerUsageLimits.test.ts

### T-02 Each reader obeys its switch
- AC: AC-02, AC-03 | Files: apps/server/src/provider/cursorUsageLimits.ts [exists], apps/server/src/provider/cursorUsageLimits.test.ts [exists], apps/server/src/provider/grokUsageLimits.ts [exists], apps/server/src/provider/GrokProvider.test.ts [exists], apps/server/src/provider/openCodeUsageLimits.ts [exists], apps/server/src/provider/OpenCodeProvider.test.ts [exists], apps/server/src/provider/Drivers/CursorDriver.ts [exists], apps/server/src/provider/Drivers/GrokDriver.ts [exists], apps/server/src/provider/Drivers/OpenCodeDriver.ts [exists], apps/server/src/usage/UsageService.ts [exists], apps/server/src/usage/UsageService.test.ts [exists] | Test: cd repositories/anton-abyzov/specwithcode && vp test run apps/server/src/provider/cursorUsageLimits.test.ts apps/server/src/provider/GrokProvider.test.ts apps/server/src/provider/OpenCodeProvider.test.ts apps/server/src/usage/UsageService.test.ts

### T-03 The switches in Settings, the row that is off and the way between them
- AC: AC-04, AC-05, AC-06 | Files: apps/web/src/components/settings/UsageReaderSwitches.tsx [new], apps/web/src/components/settings/UsageReaderSwitches.test.tsx [new], apps/web/src/components/settings/UsageProviderSettings.tsx [exists], apps/web/src/components/settings/UsageProviderSettings.test.tsx [exists], apps/web/src/components/settings/ProviderSettingsPanel.tsx [exists], apps/web/src/components/settings/settingsSearch.ts [exists], packages/client-runtime/src/state/server.ts [exists], apps/web/src/components/usage/subscriptions/NoReadingRow.tsx [1411 T-01], apps/web/src/components/usage/subscriptions/NoReadingRow.test.tsx [1411 T-01], apps/web/src/components/usage/subscriptions/subscriptionRows.test.ts [exists], apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx [exists], apps/web/src/components/usage/subscriptions/SubscriptionsView.test.tsx [exists] | Test: cd repositories/anton-abyzov/specwithcode/apps/web && vp test run src/components/settings/UsageReaderSwitches.test.tsx src/components/settings/UsageProviderSettings.test.tsx src/components/usage/subscriptions/NoReadingRow.test.tsx src/components/usage/subscriptions/subscriptionRows.test.ts src/components/usage/subscriptions/SubscriptionsView.test.tsx

### T-04 Release notes, screenshots, review and close 1415
- AC: AC-07, AC-08 | Files: apps/web/tests/usage-reader-switches/index.html [new], apps/web/tests/usage-reader-switches/main.tsx [new], apps/web/tests/usage-reader-switches/fixture.css [new], apps/web/tests/usage-reader-switches/vite.config.ts [new], apps/web/tests/usage-reader-switches/verify.mjs [new], .specweave/increments/1415-a-switch-for-each-usage-reader-that-holds-a-vendor-token-cursor-grok-opencode-go/reports/acceptance.md | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/usage-reader-switches/vite.config.ts && node apps/web/tests/usage-reader-switches/verify.mjs "$PWD/../../../.specweave/increments/1415-a-switch-for-each-usage-reader-that-holds-a-vendor-token-cursor-grok-opencode-go/reports/screenshots"
