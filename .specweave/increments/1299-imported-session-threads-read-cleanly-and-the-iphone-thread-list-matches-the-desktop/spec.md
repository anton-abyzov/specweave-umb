# Imported session threads read cleanly and the iPhone thread list matches the desktop

## Problem

Anton reported (November 11, 2026) from Elena's M2, a new install: the project's thread list is full of odd threads, the desktop and the iPhone show different lists, and the rows are hard to read. Photos: `reports/before-desktop.png`, `reports/before-iphone.png`.

What the photos show for the project `fitness-coach`:

| Surface | Sections | Rows |
|---|---|---|
| Desktop Threads panel | Idle 1, Resolved 12 | Idle: "In-progress tasks inventory" (Claude Code · Opus 5.5, 10m). Resolved: `<wake reason="mention" current-time="2026-10-30T04:18:…`, `<environment_context>` three times, `<wake reason="mention" current-time="2026-10-18T02:23:…`, all "28m" |
| iPhone Threads screen | Resolved (12) only | The same 12 rows, each three lines: title, "Claude · Claude Opus 5.5", "SYN1-MAC-AABYZOVEXT · 28m". No Idle section |

Causes found on November 11, 2026:

| Question | Finding | Evidence |
|---|---|---|
| Who created the 12 threads? | The welcome wizard, not the coordinator. When a folder is added in the wizard, it imports that folder's Claude Code and Codex sessions from the last 30 days (up to 100) as resolved threads. Asking the coordinator "what work is left" created only the one Idle thread, a subagent it spawned. | `apps/web/src/components/onboarding/WelcomeWizard.tsx:1425`; `apps/server/src/project/AgentSessionImporter.ts:179`; `apps/server/src/project/AgentSessionScanner.ts:90,100` |
| Why are the titles markup? | A session without a Claude-written title is named after the first line of its first user message. Codex writes its setup block (`<environment_context>`) as a user message, and automated Claude sessions start with a harness line (`<wake reason="mention" …>`). Two tests pin this behavior. | `AgentSessionScanner.ts:545-551`; `AgentSessionScanner.test.ts:3185,3225` |
| Why were automated sessions imported at all? | The scanner imports any session with one user-role record. A session a bot woke, with no line a person typed, counts. | `AgentSessionScanner.ts:539` |
| Why "28m" on a session from October 18? | The row age comes from the thread's update time, which the importer sets from the transcript file's modification time, not from the last message in it. On a machine whose `~/.claude` and `~/.codex` were just copied, every file is "new". To confirm in T-01. | `AgentSessionScanner.ts:343,554` |
| Why does the iPhone label differ? | The iPhone prints the provider's catalog name and the model's catalog name ("Claude · Claude Opus 5.5"). The desktop names the harness and drops the repeated maker ("Claude Code · Opus 5.5"). The iPhone also prints the raw host name on its own line. | `apps/ios/SWCKit/Sources/SWCSync/ThreadIdentity.swift:33-45`; `apps/web/src/studio/shellModel.ts:60-160`; `apps/ios/SWCKit/Sources/SWCFeatures/Overview/ProjectOverviewView.swift:122` |
| Why is the Idle row missing on the iPhone? | The phone in the photo runs the App Store build, 0.1.5 (November 7). That build hides every subagent thread, including one the coordinator spawned. The desktop lists those. The fix is #103 (`c0c1f5dd20`, November 9), part of 0.1.6, which has been in App Store review since November 9 and is not live. On main the two list rules agree (1,019 real threads, 0 differences). | `reports/repro.md`; `asc versions list --app 6824245458` |

## Scope

In: session import (which sessions, their titles, their times); a one-time repair of threads already imported; the iPhone thread row and its labels; one shared list fixture that the desktop rule and the iPhone rule must both satisfy; getting the phone build that lists coordinator threads into the App Store (0.1.6 is stuck in review; a newer build replaces it); a desktop release and an iPhone release.

Out: joining machines across Connect accounts (owned by the "Cross-account machine connect (Elena's M2)" thread); the Android app; redesigning the desktop Threads panel; importing sessions outside the wizard.

## Acceptance Criteria

- [ ] AC-01: An imported session's title is the first line a person typed. Setup and harness blocks (`<environment_context>`, `<wake …>`, `<system-reminder>`, `<user_instructions>`, `# AGENTS.md instructions`, other leading tag blocks) never become a title, and are not shown as the session's first message.
- [ ] AC-02: A session with no line a person typed (a bot wake-up, a setup-only rollout) is not imported. The wizard's count reports it as skipped.
- [ ] AC-03: An imported thread's age is the time of the last message in its transcript, so a session from October 18 reads "3w", not the minutes since the import.
- [ ] AC-04: After the update, threads imported earlier whose title is markup are retitled by the same rule, once, without the user doing anything. Threads a person renamed keep their title. Imported threads with no typed line are archived, not deleted.
- [ ] AC-05: The iPhone row reads as the desktop row does: "Claude Code · Opus 5.5" under the title, the age at the right. A quiet thread on the project's only machine takes two lines. A third line appears only when it says something: the machine by its short name when the project has more than one machine (or the thread runs on another one), plan progress, a failure, or what the thread waits for. No line wraps into the next.
- [ ] AC-06: Every thread the desktop Threads panel lists for a project is on the iPhone Threads screen, in the same group (Needs you, Working, Offline, Idle, Resolved). One fixture snapshot is checked by both the web test and the Swift test, and it includes Elena's case: a fresh project, imported Claude Code and Codex threads and one idle thread the coordinator started.
- [ ] AC-07: Headless captures show the desktop panel and the iPhone screen (simulator) on that fixture, light and dark, before and after.
- [ ] AC-08: Shipped: PR reviewed and green, merged; desktop released on all platforms through the release thread; iPhone build installed on Anton's iPhone and submitted to the App Store.

## Approach

### Import (server)

`apps/server/src/project/AgentSessionScanner.ts`:

- A new pure helper, `humanPromptText(text)`, strips leading setup blocks from a user message: a leading `<tag …>…</tag>` block, a lone opening tag line with attributes (`<wake reason="mention" …>`) and the `# AGENTS.md instructions for …` block. It returns what a person typed, or "" when nothing is left. It only strips at the start, so a typed prompt that quotes markup later is untouched.
- The title comes from the first user message with non-empty `humanPromptText`. A session with none returns null (not imported). Imported messages keep their text, except a first message that is only setup, which is dropped.
- `updatedAt` is the last retained message's timestamp when the transcript has one, else the file time.
- The two tests that expect `<environment_context>` as a title change to expect the typed line; new cases cover the wake line, setup-only sessions and a typed prompt that starts with a real tag-like word.

### Repair (server)

A one-time startup pass in `apps/server/src/project/AgentSessionImporter.ts` (`repairImportedThreadTitles`), recorded with a marker so it runs once per machine:

- For each thread with `historyOrigin: "v1_import"` whose stored title starts with `<` or `# AGENTS.md`: read its stored messages, apply `humanPromptText`, and dispatch the normal rename command. No typed line: archive it.
- A title a person set is never markup, so the start-of-title check is the guard; nothing else is touched.
- It goes through commands, never the database files.

### iPhone

- `ThreadIdentity`: port `providerShortLabel` and `modelLabel` (harness name, no repeated maker), with the same test table as `shellModel.test.ts`.
- `ProjectOverviewView.row`: two lines. Line 1 title; line 2 "Claude Code · Opus 5.5" plus the short machine name when `machines.count > 1`; age trailing, before the status marks. `shortMachineName` ported.
- A title that is still markup (an older desktop) shows as "Imported session".
- The missing Idle row needs no new rule: main already lists a coordinator's workers (#103). It needs that build in the App Store, and the parity fixture below so the lists cannot drift again.
- `ShellSnapshot` decodes its threads one by one, so one unreadable thread no longer drops the whole list (`SWCWire/Shell.swift:27`). No real thread fails today; this is a guard.

### Parity fixture

`packages/contracts/fixtures/thread-list-parity.json`: a shell snapshot (fictional names) plus the expected groups per project. `apps/web/src/studio/threadListParity.test.ts` runs the desktop rule over it; `apps/ios/SWCKit/Tests/SWCSyncTests/ThreadListParityTests.swift` runs the iPhone rule. Either side drifting fails its own test.

### Risks

- Stripping too much: a person whose prompt is a pasted XML block gets "Imported session" as the title. Accepted; the message text is unchanged.
- The repair archives bot sessions. They stay in the archive and can be restored.
- 0.1.6 is in App Store review. Submitting a newer build means cancelling that submission first; the review clock restarts.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Bot-only sessions are not imported, and ones already imported are archived (reversible: restore from the archive).
- D-02 Markup titles are repaired on the server once, and the iPhone also hides markup titles from older desktops.
- D-03 The iPhone row follows the desktop's wording instead of the catalog's names.
- D-04 The iPhone ships as 0.1.7: the 0.1.6 submission in review is cancelled and replaced, so users get one update with both fixes.

### Open
- none

- D-05: The repair of earlier imports is its own start-up step (`ImportedThreadTitleRepair.ts`, one registration line in `server.ts`), not part of the importer. It reads the first typed line from the thread's stored messages, renames with a fixed command id per thread so a second start does nothing, and archives a thread with no typed line.
- D-06: The shared list cases live in `packages/shared/src/threadList.cases.json`, next to `transcriptDetail.cases.json`, which web and iPhone tests already share the same way. The server checks the title cases too, so the iPhone's "Imported session" fallback and the server's rename agree on what counts as markup.
- D-07: The simulator capture of a two-machine project showed the machine name wrapping the model line and cutting the status. The machine and status moved to their own single line (a `note` on the shared row component), so AC-05 reads "two lines when quiet, a third only when it says something" instead of "two lines per row".

## Tasks

### T-01 Reproduce Elena's state and name the cause of the missing Idle row
- AC: AC-06 | Files: .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/repro.md | Test: test -s .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/repro.md

### T-02 Import: typed-line titles, skip bot sessions, real times
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/AgentSessionScanner.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/AgentSessionScanner.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/AgentSessionPrompt.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/AgentSessionPrompt.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/AgentSessionScanner.test.ts src/project/AgentSessionPrompt.test.ts

### T-03 Repair threads imported earlier
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ImportedThreadTitleRepair.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ImportedThreadTitleRepair.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/server.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ImportedThreadTitleRepair.test.ts

### T-04 iPhone row and labels
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ThreadIdentity.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ThreadTitle.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Overview/ProjectOverviewView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCSyncTests/ThreadIdentityTests.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCFeaturesTests/FleetRowTests.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/docs/thread-list-parity.md, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/Weave/Components/WeaveRow.swift | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit && DEVELOPER_DIR=/Applications/Xcode-27.2.app swift test --filter "ThreadIdentityTests|FleetRowTests|ScreenLogicTests"

### T-05 One list fixture for desktop and iPhone, and a snapshot that survives one unreadable thread
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/threadList.cases.json, repositories/anton-abyzov/specwithcode-dev/packages/shared/package.json, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadListCases.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCFeaturesTests/ThreadListCasesTests.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCWire/Shell.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCWireTests/ToleranceTests.swift | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/threadListCases.test.ts && cd ../ios/SWCKit && DEVELOPER_DIR=/Applications/Xcode-27.2.app swift test --filter "ThreadListCasesTests|ToleranceTests"

### T-06 Captures before and after
- AC: AC-07 | Files: .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/after-desktop-light.png, .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/after-iphone-light.png, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/UITests/ThreadListParityUITests.swift, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-row-meta/main.tsx | Test: test -s .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/after-desktop-light.png && test -s .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/after-iphone-light.png

### T-07 Ship: PR, desktop release, iPhone install and App Store
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/project.yml, repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md | Test: asc versions list --app 6824245458 --output json | grep -q '"0.1.7"'

### T-08 Verify and close 1299
- AC: AC-08 | Files: .specweave/increments/1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop/reports/verify.md | Test: specweave verify 1299-imported-session-threads-read-cleanly-and-the-iphone-thread-list-matches-the-desktop
