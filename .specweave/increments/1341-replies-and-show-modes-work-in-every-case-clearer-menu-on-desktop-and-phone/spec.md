# Replies and Show modes: work in every case, clearer menu on desktop and phone

## Problem

The thread header control "Replies: Concise · Results only" holds two settings: how agents write (Replies: Concise or Detailed, per project) and what a conversation shows (Show: Results only, Folded steps or Everything, per device with a per-thread choice). The owner reported on November 14, 2026 that it does not work well, at least in the mobile apps, and asked to check every case and improve the layout.

Audit of `origin/main` at `a214dcc88` (November 14, 2026):

- **Menu layout (desktop and web).** Nine rows under three headings. The three Show levels are listed twice ("Show in this thread", "Show in every thread"), plus "Use default (…)". Descriptions appear in one list and not the other.
- **Narrow headers.** Below a 1040 px thread column or a 620 px top bar the label disappears, leaving an icon that says nothing about the current state. On a phone-width browser this is always the case, and touch has no tooltip.
- **Shortcut.** ⌥⌘O changes the level for every thread. In a thread that has its own level nothing changes on screen, yet the toast says "Show: …".
- **Naming.** The same setting is "Show" in the header, "Timeline detail" in Settings, the command palette and error toasts.
- **iOS.** Show can only be changed in Settings, under a card titled "Replies" (which is the other setting). The chat has no control and no per-thread choice. The reply style is neither shown nor changeable. Folding defects: a fold opened while a turn runs in Results only stays open after it settles (same fold id), an agent still at work is hidden inside a fold in Results only, and a transcript cached mid-run keeps a "Working" row forever.
- **Android.** Neither setting exists. Every conversation shows every step, thought and in-between message; the fold row is dead code. The reply style is neither shown nor changeable.
- **Reply style delivery.** `RuntimePolicy` resolves the project override for every thread (coordinator and worker alike) on the machine that runs it. Whether every provider adapter passes it on is unverified.

## Scope

In: the header menu and trigger on desktop and web, the shortcut, naming, the iOS and Android chat and settings controls, Android folding, the listed iOS folding defects, reply style on both phones, a check that every provider adapter receives the reply style, and before/after headless videos.

Out: syncing the Show level between devices (it stays per device), new Show levels, changing the instruction text agents receive, the React Native app in `apps/mobile`.

## Acceptance Criteria

- [ ] AC-01: The header menu has one list of the three Show levels, each with its description, and an "Applies to" choice (This thread / Every thread) when the header belongs to a thread. Choosing a level with "This thread" gives the thread its own level; with "Every thread" it sets the default and the thread follows it. Switching to "Every thread" drops the thread's own level; switching to "This thread" pins the level currently shown. The reply style section stays first, named for the project, read-only with a reason when the connection cannot change settings, "Mixed" when checkouts disagree.
- [ ] AC-02: The trigger always tells the state. Wide: "Concise · Results only" after the icon (or the Show level alone without a project). Narrow: the Show level alone. Narrowest: the icon with a marker when the thread has its own level. The accessible name always carries both values. The menu fits a 390 px wide window without horizontal scroll.
- [ ] AC-03: ⌥⌘O cycles what the open thread shows: the thread's own level when it has one, otherwise the default for every thread. The toast names which ("Show in this thread: …" or "Show: …"). Away from a thread it cycles the default.
- [ ] AC-04: Settings, the command palette and error toasts call the setting "Show" / "what threads show", with the same level names.
- [ ] AC-05: Every provider adapter that starts a turn passes the resolved reply style into its instructions, for coordinator and worker threads; a project override wins over the machine setting. A test fails if an adapter drops it.
- [ ] AC-06: iOS: the chat (thread and coordinator) has a Show menu with the three levels and This thread / Every thread, kept on the phone; Settings names the card for what it holds. The three folding defects are fixed and covered by tests.
- [ ] AC-07: Android: conversations fold by the same rule as iOS (`docs/transcript-detail.md`), default Folded steps, and the shared cases in `packages/shared/src/transcriptDetail.cases.json` pass. A fold opens and closes on tap. The chat (thread and coordinator) has a Show menu with the three levels and This thread / Every thread; Settings has the default.
- [ ] AC-08: iOS and Android show the project's reply style in the same menu and change it when the machine supports per-key project overrides and the phone may operate that machine; otherwise the row is read-only or absent, never a silent no-op.
- [ ] AC-09: Headless videos of each case, before (`origin/main`) and after, are saved under the increment's `reports/`: desktop and 390 px web through Playwright headless; iOS through the simulator; Android through the emulator, or the reason a platform could not be recorded.
- [ ] AC-10: `docs/transcript-detail.md` describes the menu, the shortcut and what each platform keeps.

## Approach

Web first (the control the owner showed), then the two phones in parallel, then evidence.

- `TimelineDetailMenu.tsx`: one Show radio list plus an "Applies to" radio pair; state derives from the existing `timelineDetail` and `threadTimelineDetail` client settings, so no stored shape changes. Trigger text in three tiers by container query (`shell.css` for the project header, classes for `ChatHeader`).
- `timelineDetail.ts`: `useTimelineDetailShortcut` reads the open thread from the route and cycles its own level when it has one.
- Naming in `SettingsPanels.tsx`, `CommandPalette.tsx`, toasts.
- Server: a test over every adapter's turn input for `responseStyle`; fix any adapter that drops it.
- iOS: `ThreadDetailStore` (UserDefaults, capped like the web's 300), Show section in the thread menu and the coordinator header, reply style through `server.updateSettings` with `projectSettingsOverrideChanges`. Fold ids differ for the running fold; running agents stay outside folds; a stale session is not "running".
- Android: port `TranscriptFolding` to `sync`, run the shared cases, wire `FoldRow` taps, a `DropdownMenu` section in the chat top bar, a Settings card, the same reply style call.
- Rejected: a segmented control in the trigger (too wide for a header); syncing Show across devices (a phone wants less than a desktop); one global shortcut that also flips the thread to "own" (surprising).
- Risk: phone work cannot be proven on hardware here; simulator and emulator recordings plus unit tests are the evidence, recorded as a proof limit.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 ⌥⌘O follows the open thread's scope (own level if it has one, else the default) → yes.
- D-02 Show stays per device; phones get their own per-thread choice → yes.
- D-03 Phones change the reply style only on machines reporting `projectSettingsOverrideChanges` → yes; older machines show it read-only.
- D-04 Trigger drops the "Replies:" prefix; the icon and accessible name carry it → yes.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-1.0)
- Depth: deep
- Required: yes

## Tasks

### T-01 Before videos and baseline
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/timeline-detail/record.mjs | Test: ls .specweave/increments/1341-replies-and-show-modes-work-in-every-case-clearer-menu-on-desktop-and-phone/reports/before/web-1280.webm .specweave/increments/1341-replies-and-show-modes-work-in-every-case-clearer-menu-on-desktop-and-phone/reports/before/web-390.webm

### T-02 Web menu, trigger, shortcut and naming
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/TimelineDetailMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/TimelineDetailMenu.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/timelineDetail.ts, repositories/anton-abyzov/specwithcode/apps/web/src/timelineDetail.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/shell.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/timeline-detail/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/timeline-detail/main.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/TimelineDetailMenu.test.tsx src/timelineDetail.test.ts

### T-03 Reply style reaches every adapter
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/responseStyleDelivery.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/responseStyleDelivery.test.ts

### T-04 iOS Show menu, per-thread level, fold fixes, reply style
- AC: AC-06, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests | Test: cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test --filter "TranscriptFolding|TranscriptDetailCases|ThreadDetail|ReplyStyle"

### T-05 Android folding, Show menu, settings, reply style
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/android/sync, repositories/anton-abyzov/specwithcode/apps/android/wire, repositories/anton-abyzov/specwithcode/apps/android/app | Test: cd repositories/anton-abyzov/specwithcode/apps/android && ./gradlew :wire:test :sync:test :app:testDebugUnitTest

### T-06 After videos, docs
- AC: AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/docs/transcript-detail.md, repositories/anton-abyzov/specwithcode/apps/web/tests/timeline-detail/README.md | Test: ls .specweave/increments/1341-replies-and-show-modes-work-in-every-case-clearer-menu-on-desktop-and-phone/reports/after/web-1280.webm .specweave/increments/1341-replies-and-show-modes-work-in-every-case-clearer-menu-on-desktop-and-phone/reports/after/web-390.webm

### T-07 Verify and close 1341
- AC: AC-01 | Files: .specweave/increments/1341-replies-and-show-modes-work-in-every-case-clearer-menu-on-desktop-and-phone/reports | Test: cd repositories/anton-abyzov/specwithcode && node scripts/studio-brand-audit.mjs
