# Dictation keeps earlier text and long lists keep their scroll position

## Problem

The owner, November 28, 2026, on the iPhone ("Anton's iPhone", the Duo): while dictating into a chat, a pause sometimes erases the message that was already there. Dictation must only add. Second complaint: in long lists (threads, model picker, machine and project choosers, the sidebar) the list jumps back to the top while scrolling down to pick something. Screenshots: `/Users/anton/Downloads/IMG_0922.PNG` to `IMG_0927.PNG` (coordinator chat with the composer mic, the Wispr Flow keyboard, the coordinator Settings sheet with the Machines list).

How dictation works today, per platform:

| Platform | Path | Erases? |
|---|---|---|
| iPhone app, composer mic | Apple `SFSpeechRecognizer`, streaming partial results; each partial replaced everything after the draft as it was when the mic started | Yes: after a pause the recognizer starts its transcript over, and the earlier words were replaced by the new phrase |
| iPhone app, keyboard mic (Apple, Wispr Flow) | the keyboard types into the composer `TextField` | The field was disabled on "Connecting…" / "Machine unavailable", which closed the keyboard mid-dictation |
| Mac and Linux desktop | one utterance at a time (Apple speech helper, whisper.cpp), inserted at the caret | A selection was replaced by the next phrase |
| Windows desktop, browsers, mobile web | no in-app mic; the OS keyboard writes into the composer | No app-side replace found |
| Android/Expo app | record, then transcribe the clip once | Not affected by pauses; selection replace is a deliberate, tested design there (left as is) |

## Scope

In: iPhone composer dictation (state machine, recognizer task, cursor, editable field while blocked), desktop dictation insertion, long-list scroll fixes found by the audit on iPhone and desktop/web. Out: coordinator and machine switching and the phone's model choice (worker "Phone machine switching and remote connection reliability"), the Expo app's selection behaviour.

## Acceptance Criteria

- [x] AC-01: On the iPhone, words said before a pause stay in the draft when the recognizer starts a new phrase; text that was in the draft before dictation, and edits made while listening, are never replaced.
- [x] AC-02: On the iPhone, dictation writes at the cursor (after a selection), the mic is offered with text in the draft, and the field stays editable while sending is blocked.
- [x] AC-03: On the desktop, a dictated phrase goes after a selection and never replaces it.
- [x] AC-04: Long lists on the iPhone and desktop keep their scroll position while scrolling and picking, including when live data refreshes.
- [x] AC-05: Shipped: PR merged green, app release requested, TestFlight build with the iPhone changes, proof screenshots or recording.

## Approach

iPhone: `SpeechDictation` keeps a prefix and suffix around the phrase being heard; a phrase settles on `isFinal` or end-of-utterance metadata; a partial that is a new phrase (shorter, shares at most a word or two at the start) settles the previous one; repeated words of a settled phrase are stripped; an edit made while listening wins. `AppleSpeechEngine` starts a new recognition task when one ends. Ground truth for the recognizer's behaviour across a pause is recorded on m4 (no Xcode on M5).

Desktop: `insertDictatedText` and `ChatComposer.insertDictation` insert at the end of the selection.

Lists (audit November 28, 2026): iPhone drawer unmounts on close and lost its scroll and folds; a cold-start restore closed a drawer the person opened; project rows were keyed by the leading machine copy. Web sidebar search reset its highlight and scrolled to the top on live reorders; the composer model picker remounted when the layout flipped while open; load balancing closed the machine chooser; project menus re-sorted while open. Android palette scrolled to top on live reorders. Not changed here (in the phone worker's area, flagged to it): iPhone OrchestratorSwitcher and machine menus rebuilt while open, the coordinator Settings Machines card.

Recognizer ground truth (m4, November 28, 2026): on-device recognition returns the first phrase with end-of-utterance metadata and `isFinal == false`, then starts over ("And"); server recognition stays cumulative. Traces on m4: `~/.specwithcode/m4/evidence/1518/recognizer-local.log`, `recognizer-remote.log`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Dictation never replaces a selection on the desktop either (the owner: "we should never erase it").
- D-02 The iPhone mic stays visible with text in the draft, so a message can be dictated in parts.
- D-03 A blocked composer (offline, connecting) keeps typing and dictation on; only Send is blocked.
### Open
- none

## Tasks

### T-01 iPhone dictation only adds
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Support/SpeechDictation.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Support/DictationText.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/Weave/Components/ComposerBar.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCFeaturesTests/DictationTests.swift | Test: on m4, `cd repositories/anton-abyzov/specwithcode/apps/ios/SWCKit && swift test --filter DictationTests`

### T-02 Desktop dictation adds after a selection
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/VoiceDictation.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/VoiceDictation.test.tsx | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/VoiceDictation.test.tsx`

### T-03 Long lists keep their scroll position
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/DrawerView.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCFeaturesTests/ListScrollTests.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCFeaturesTests/LastOpenedTests.swift, repositories/anton-abyzov/specwithcode/apps/web/src/components/Sidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebarSearchHighlight.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/DraftMachinePicker.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/DraftHeroHeadline.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/hooks/useHeldOrder.ts, repositories/anton-abyzov/specwithcode/apps/mobile/src/features/keyboard/CommandPalette.tsx | Test: web related files (31 files) plus `sidebarSearchHighlight.test.ts`, `useHeldOrder.test.ts`; on m4 `swift test --filter "ListScrollTests|LastOpenedTests"` and simulator screenshots of the drawer before and after reopening

### T-04 Ship
- AC: AC-05 | Files: none | Test: PR checks green, `bash scripts/release/request-release.sh --by "<thread>"`, TestFlight build listed in App Store Connect
