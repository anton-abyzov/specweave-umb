# Change a thread's model on iPhone

## Problem

Anton, November 17, 2026: "on mobile, I cannot change a model for the personal assistant." Screenshot: `~/Downloads/Screenshot 2026-11-17 at 17.04.56.png` (Percy thread on m1, chip "Grok 4.7 · Medium").

The native iPhone app (`apps/ios`) has no way to change any thread's model, Percy's or a code thread's. Its composer chip opens `ModelOptionsMenu` (`apps/ios/SWCKit/Sources/SWCFeatures/Chat/ModelOptionsMenu.swift:19-59` at `017c7f12e`), which offers only the current model's trait controls and Access; the model name is just the section title (line 21). `ChatView.send()` (`apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift:1112-1113`) only lays option drafts over the thread's own selection, so a message can never name another model. The menu has been this way since PR #106; it is a missing feature, not a regression, and not specific to the assistant.

The server already runs a message on the model its `message.dispatch` names (`apps/server/src/orchestration-v2/Orchestrator.ts:6030`), the path web and the Expo client use. No server change is needed.

## Scope

In: a model list in the iPhone composer's options menu, sent with the next message; fixture and tests. Out: server changes; the chip's placement and Artifacts (1273, which lists the same two files; this keeps `chat.model-options` and `ModelOptionsUITests`); an iOS release (the "macOS icon and iOS release gap" thread, 1380, ships 0.1.8/46 and carries this).

## Acceptance Criteria

- [x] AC-01: The options menu on a thread has a Model row listing the models of every provider on the thread's machine that is enabled, installed and ready, grouped by provider, with the thread's model checked. The thread's own model stays listed when its provider is not ready.
- [x] AC-02: Picking a model changes the chip to that model and shows the pending dot. Its option controls are the picked model's own, starting from that model's defaults; the old model's options are never sent with it.
- [x] AC-03: The next message is dispatched with the picked model's selection (plus any options chosen after the pick); the draft clears on send and comes back if the send fails. Picking the thread's own model again clears the pick.
- [x] AC-04: The chip shows when a thread has more than one model to choose from, even if its model takes no options.

## Approach

`SWCSync/ModelChoices.swift` (new): `ModelChoice` built from `ServerProviderSummary` in `ShellSummaries.threadSummary`; `ThreadSummary` gains `modelChoices` and `modelSelection`. `Router.modelDrafts` holds the pick; `ChatView` derives the chip label, traits and send selection from it; `ModelOptionsMenu` adds a nested Model submenu (provider submenus when there are several). `FixtureEngine` gives threads three choices and applies a sent model.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Cross-provider picks are offered. The phone's wire has no session capabilities, and every server adapter reports `supportsProviderSwitchingViaHandoff: true`, so the Expo client's lock would never apply; the server hands the conversation over at the next turn.
- D-02 A pick starts with no options (machine defaults) rather than mapping the old model's options.
### Open
- none

## Tasks

### T-01 Model list in the iPhone options menu
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/ModelChoices.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ModelOptionsMenu.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ModelChoicesTests.swift, repositories/anton-abyzov/specwithcode/apps/ios/UITests/ModelOptionsUITests.swift | Test: cd repositories/anton-abyzov/specwithcode/apps/ios && make test-core && Tools/sim.sh test -only-testing:SpecWithCodeUITests/ModelOptionsUITests

### T-02 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1382-change-a-threads-model-on-iphone/reports/ | Test: specweave verify 1382-change-a-threads-model-on-iphone

## Proof limits

- Fixture and unit tests only; the phone sending a message that a real machine runs on a different provider is not exercised here. Anton checks it on the Duo after 0.1.8/46.
