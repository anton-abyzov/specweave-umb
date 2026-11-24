FIX FIRST
Verdict: fix first

Reviewed `3e8359cec9f91a5e28186c51787d4cb2b6526183` in `anton-abyzov/specwithcode#705`, against `13badcb7944321e740765e766b79f682bb1078f8`. A two-thread batch with one thread left behind can say **“All 1 on Desk.”** This was reproduced from the reviewed Git objects, not inferred from a screenshot.

| AC | Change | Test and limit of its evidence | Red before fix |
|---|---|---|---|
| 17 | Project and machine scopes share one dialog; only running candidates are listed. | Machine-dialog tests cover scope, empty state and preflight; not queued, idle or unsaved work. | Unverified |
| 22 | Picker marks destinations needing an update, but gives no per-provider quota comparison. | Result and dialog tests cover disabled destinations, not shared accounts or unknown usage. | Unverified |
| 23 | Sent and uncertain records show Wait, not Resume here. | Logic and runner tests distinguish unsent from sent holds. They do not prove the source badge and Bring back flow. | Unverified |
| 29 | `/handoff` opens project scope; `/away` still opens Away. | Composer command tests cover parsing; parsing does not prove which dialog opens. | Unverified |
| 30 | Web catalogs, iOS sheet and agent-facing descriptions changed. | Retired-phrase checks cover old words, not all new strings. | Unverified |
| 39 | Presentational view chooses the earliest reset or Reset unknown. | Logic and render tests inject the inputs; no production caller supplies them. | Unverified |
| 47 | Transfer rows drive counts, bar and actions. | Logic and render tests cover mixed outcomes with complete input. They miss a partially retained batch and competing attempts. | Unverified |

## Blocking findings

Paths below are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at the reviewed commit.

1. **High · AC-47 · A mixed batch becomes an all-arrived batch.** `apps/server/src/handoff/HandoffTransferStore.ts:452` caps finished **records**, not batches. `apps/web/src/components/handoff/handOffProgress.logic.ts:182` uses the full operation list only for sorting; lines 118–124 take the surviving rows as the entire denominator. Reproduction: one thread stayed, one was ready on Desk, then 39 unrelated operations finished. The snapshot retained the batch and the ready row but not the stayed row. The formatter returned `All 1 on Desk` instead of `2 of 2 finished: 1 ready, 1 stayed`. Retain complete displayed groups, or explicitly mark incomplete history and suppress the all-arrived claim. Test the store and summary together.

2. **High · AC-47 · Another handoff can stand in for the one just requested.** `apps/web/src/components/handoff/HandOffMachineDialog.tsx:528–534` matches any newly observed operation on a selected thread. It checks neither batch ID nor destination. If this window requests Desk and another window wins a handoff of the same thread to Mini before the next poll, Mini’s progress replaces this form. Even if the Desk request fails, its error at line 628 is hidden by the progress branch at line 221. Correlate progress with the submitted operation or batch, and test two windows targeting different machines.

3. **High · AC-23/47 · A stale “Resume here” can release a different transfer.** `apps/web/src/components/handoff/HandOffProgress.tsx:382–385` sends only the thread ID, although the row has an operation ID. `apps/server/src/handoff/HandoffMoves.ts:1027` resolves the thread’s *current* open transfer. If the displayed hold ended in another window and a later batch has a pending record for that thread, pressing the old button can mark the later, unsent transfer Stayed. The view then checks the old operation at line 391. Send the operation ID and condition the release on that exact record still being held. A stale action should change neither record.

4. **High · AC-39/47 · Automatic progress requires a click, and no-move progress is unreachable.** `apps/web/src/components/chat/LimitHandoffCandidates.tsx:154–157` opens progress only on click and only if a record exists. On a first exhaustion with no eligible machine there is no move record. Even with a record, the production view at `apps/web/src/components/handoff/HandOffProgress.tsx:368–377` never supplies `trackOut`. Someone waiting for the earliest reset cannot see it; someone whose thread moved automatically does not get the common progress view on start. Wire the view to the automatic decision, including the no-transfer case. The reset scheduler itself belongs to T-13.

5. **High · AC-17 · Eligible non-running work is absent.** `apps/web/src/components/handoff/HandOffMachineDialog.tsx:443–455` builds the entire list from running handoff candidates, and line 253 renders only Running. A project with a single idle thread waiting for its next message, no active checkpoint and no running thread gets an empty list. Its owner cannot select that thread to arrive Ready. Consume the plan’s groups, including untickable Stays with reasons. The accepted amendment removed coordinator and routine rows, not waiting, queued, unsaved or project-folder work.

6. **High · AC-22 · The manual picker omits the information needed to choose a destination.** `apps/web/src/components/handoff/HandOffMachineDialog.tsx:237–242` passes reachability options, not usage by provider. An online Desk on the source’s depleted account and an online Mini on a different account can both appear available with no indication that only Mini adds usage. Render the per-provider comparison, including the unknown case, without disallowing manual selection.

7. **High · AC-29 · `/away` invokes the wrong workflow.** `apps/web/src/studio/useComposerAppCommands.ts:115–119` sends `/away` directly to `requestAway`. Typing it opens the legacy Away form, not Hand off with “Every project on this machine.” Route `/away` to machine-wide Hand off and assert the resulting dialog and scope. No edit to the large palette component is required for this fix.

## Follow-up (non-blocking)

- **AC-30:** `apps/web/src/studio/composerAppCommands.ts:42` introduces the visible description `Hand off work to another machine`; the key is absent from all eight web catalogs. Add it and test the command description in a non-English locale.
- **Compatibility evidence:** `apps/web/src/components/handoff/handOffProgress.logic.test.ts:32` constructs the old decoder from a current import. Decoding the new payload with an empty schema does not demonstrate old-window/new-server snapshot handling. Preserve a genuinely version-pinned snapshot decoder or fixture for that direction, per EC2-09.
- **Single-thread update action:** `apps/web/src/components/handoff/HandOffThreadDialog.tsx:404–405` remembers an outdated destination, but lines 380–385 can keep an explicitly selected disabled ID. For an implicitly selected destination, switching to the next peer also replaces the preflight results used for the update action at lines 495–501. Keep the affected machine’s update action attached to its own row and test both selection paths.

## What I verified

- Fetched the PR and confirmed its head. Inspected only the three requested commits as changes; read existing callers and record semantics as context. Checked T-12’s Files and Test, its seven ACs, the November 19, 2026 amendments, the design guidelines and the eight catalogs. No new user-facing `Studio` product name found in the changed web components or iOS sheet.
- Exercised the reviewed store projection, grouping and formatter in memory with the 41-record example above. The original batch still named both operations; the formatter saw only `ready`. `git diff --check` passed.
- **Assertion-level red could not be confirmed.** The supplied scratch directory contained two screenshots and their capture script, not a red test log or worker notes. `347df47f1` adds the logic and its tests together; `b4f29650a` changes tests and production code together; `3e8359cec` formats phrase lists. None is a tests-only commit. A render or a reported green run is not evidence that a pre-fix assertion failed.
- No checkout, installation, build, full suite, commit or PR comment. The known stack conflict and missing CI run were not used to determine the verdict.
