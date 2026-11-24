# Tab accepts suggested next prompt

## Problem

After a reply, the Codex app shows a greyed-out suggested next prompt in the empty input box, and Tab fills it in. SpecWithCode shows nothing, so the owner retypes the obvious follow-up ("run the tests", "commit and open a PR") after every turn. Nothing in specwithcode-dev handles suggestions today (`git grep -i prompt_suggestion` is empty). Claude's Agent SDK already predicts the next prompt (`Options.promptSuggestions`, a `prompt_suggestion` message after `result`), and we drop it. The Codex app-server protocol (codex-cli 0.162) has no suggestion API; the Codex app gets its suggestions from ChatGPT's own backend, so Codex and every other provider need a suggestion we generate ourselves.

## Scope

In: one suggestion per finished run, stored on the run so it survives reload and reaches every client; Claude's native suggestion; a generated fallback (the text-generation model) for every provider whose turn ends without one, Claude's first turn included; ghost text in the empty desktop/web composer with Tab to accept and Escape to dismiss; a tap-to-fill chip above the iPhone composer; a machine setting (Suggested prompts: all providers / native only / off).

Out: the Expo app (not distributed); suggestions for subagent child threads, wake and restart-continuation runs, failed or interrupted runs; multiple suggestions or a list.

## Acceptance Criteria

- [ ] AC-01: A run that finishes with a suggestion records `promptSuggestion {text, source}` on that run through its own `run.prompt-suggested` event; a later run snapshot never erases it, and only the thread's latest completed run takes one.
- [ ] AC-02: Claude threads ask the SDK for prompt suggestions and the suggestion that arrives after `result` lands on the run that just finished.
- [ ] AC-03: When a top-level run completes without a native suggestion (any provider), the server generates one with the text-generation model within a short timeout; failures, refusals and empty answers leave the run without one and never surface an error.
- [ ] AC-04: The Suggested prompts setting (default all providers) turns the fallback off ("native only") or every suggestion off ("off").
- [ ] AC-05: On desktop/web, when the thread is idle and the composer is empty, the latest run's suggestion shows as grey ghost text with a Tab hint; Tab fills it in with the cursor at the end, typing hides it, Escape dismisses it for that run, and menus, Shift+Tab plan toggle and list indent keep working.
- [ ] AC-06: On iPhone, the same suggestion shows as a chip above the empty idle composer; tapping fills the draft.

## Approach

Storage: an optional `promptSuggestion` field on `OrchestrationV2Run` written only by a new `run.prompt-suggested` domain event (mirrors `run.background-work-cancelled`: its own event so a stale run snapshot cannot regress lifecycle state, `json_set` in ProjectionStore, `keepRecordedRunField` and `preserveRunRecordedFields` on `run.updated`). Written through a new internal command `run.prompt-suggestion.record` so it runs under the thread lock and the handler drops it unless the run is the latest run and completed. Older web and iOS clients ignore the unknown event type.

Sources: `PromptSuggestionOffers` (a `Context.Reference` queue like `ProviderContinuationRequests`, shared through `ProviderOrchestrationAdapterInfrastructure`) carries Claude's SDK suggestion from the adapter (`promptSuggestions: true`, a branch before the idle `activeTurn` check, keyed to the last finished turn). `PromptSuggestionReactor` (server.ts, like `HandoffModeReactor`) drains offers and watches `run.updated` completions; for runs without a native suggestion it waits briefly for Claude's, then calls a new optional `TextGeneration.generatePromptSuggestion` (built once in `TextGenerationOperations.fromRunner`, forwarded by CodexManaged and OpenCode) with the last user and assistant messages and the project's text-generation model.

Clients: web derives the latest run's suggestion in ChatView and passes it to ChatComposer, which gates it (idle, empty draft, no pending input/approval) and renders it in the Tiptap editor's placeholder slot; Tab accept goes after the menu branch in `onComposerCommandKey`. iOS decodes the new Run field and event, and ComposerBar shows a chip.

Rejected: a persisted thread field (about 10 mirrored touch points and thread-shell churn every turn); a client-only ephemeral event (lost on reload, which is the main case: opening a finished thread later); a new adapter event arm (every exhaustive adapter-event switch would change).

Risk: per-turn generation cost; kept small by the cheap text-generation model, top-level human-started runs only, one at a time per thread, and the setting.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Fallback default: on for all providers, using the global/project text-generation model (the cheap one), not the thread's own model.
- D-02 Phone: iPhone app gets a tap-to-fill chip (no Tab on phones); the Expo app is skipped because it is not distributed.
- D-03 Claude's native suggestion is preferred; the fallback waits up to 8 seconds for it.
### Open
- none

## Tasks

### T-01 Store suggestions on runs
- AC: AC-01 | Files: packages/contracts/src/orchestrationV2.ts, apps/server/src/orchestration-v2/ProjectionStore.ts, apps/server/src/orchestration-v2/Orchestrator.ts, packages/client-runtime/src/state/orchestrationV2Projection.ts, apps/server/src/orchestration-v2/PromptSuggestionRecord.test.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/PromptSuggestionRecord.test.ts

### T-02 Claude native suggestions and generated fallback
- AC: AC-02, AC-03, AC-04 | Files: apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, apps/server/src/orchestration-v2/PromptSuggestionOffers.ts, apps/server/src/orchestration-v2/PromptSuggestionReactor.ts, apps/server/src/textGeneration/*, packages/contracts/src/settings.ts, apps/server/src/server.ts | Test: pnpm --dir apps/server exec vp test run src/orchestration-v2/PromptSuggestionReactor.test.ts src/textGeneration/TextGenerationPrompts.test.ts

### T-03 Ghost text and Tab accept in the desktop composer
- AC: AC-05 | Files: apps/web/src/components/ComposerPromptEditorTiptap.tsx, apps/web/src/components/chat/ChatComposer.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/components/chat/composerGhostSuggestion.ts, apps/web/tests/ghost-suggestion/* | Test: node apps/web/tests/ghost-suggestion/verify.mjs (headless)

### T-04 Suggestion chip on iPhone
- AC: AC-06 | Files: apps/ios/SWCKit/Sources/SWCWire/*, apps/ios/SWCKit/Sources/SWCSync/*, apps/ios/SWCKit/Sources/Weave/Components/ComposerBar.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift | Test: swift test --package-path apps/ios/SWCKit --filter PromptSuggestion

### T-05 Settings row for Suggested prompts
- AC: AC-04 | Files: apps/web/src/components/settings/* | Test: pnpm --dir apps/web exec vp test run (settings row test)

### T-06 Verify and close 1216
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1216
