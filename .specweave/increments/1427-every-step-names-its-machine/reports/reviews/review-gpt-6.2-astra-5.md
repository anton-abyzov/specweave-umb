<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=ac0d303db80b8d7e8706716414c774e4c5dbc590 at=2026-11-19T23:23:51.894Z -->
# Review: 1427 T-02, window and coordinator machine labels
Verdict: ship

Reviewer context: fresh cross-family review of `anton-abyzov/specwithcode#760`, base `33a53f50ed5a817071d513f1e77531394441384b`, head `ac0d303db80b8d7e8706716414c774e4c5dbc590`. Static review of Git objects only. No checkout, build or tests.

The change does not redirect an update, thread action or link operation. Three non-blocking follow-ups remain.

## [medium] Follow-up: a relay can keep naming the previous runner

`apps/web/src/components/studio/CoordinatorConversation.tsx:525` gets the sender from `linkWorkers`. The equality check at lines 185–194 ignores execution machine ID and label. When only execution moves from M5 to M6, line 309 retains the old shell, so even a new relay can still say M5. Resolve the sender from the live worker map instead. The stale name is not passed to the click handler.

## [medium] Follow-up: a remote sender can lose its name entirely

`apps/web/src/components/studio/ProjectWorkspaceSurface.tsx:1972` passes only the shown environment’s workers in `workers`; remote workers arrive separately. The sender lookup at `apps/web/src/components/studio/CoordinatorConversation.tsx:526` never searches that separate list. A sender present only there falls back to “Message from a thread” at line 1306. The fixture passes the remote shell directly to the formatter, bypassing this lookup.

## [low] Follow-up: the fixture does not cover the AC-09 card

`apps/web/tests/coordinator-menu/main.tsx:92–124` renders messages, a source, a chip and a relay, but no action card. The four viewport/theme combinations therefore cannot establish that the card names its machine. Add a representative card and assert its visible machine label.

## Action and identity checks

- **Window versus coordinator:** `apps/web/src/components/sidebar/SidebarWindowMachine.tsx:39–41` resolves the window ID and fallback from the same environment. `apps/web/src/components/studio/ProjectWorkspaceSurface.tsx:315` and `:1814` use the shown project's environment for the tag. `apps/web/src/components/studio/CoordinatorConversation.tsx:280` and `:326` likewise pair the reply's coordinator ID with its own environment label. `apps/web/src/components/studio/OrchestratorSwitcher.tsx:281` compares each listed row with the window ID, not the selected project.
- **Thread versus source:** Live chips pass the thread shell to the location helper; `packages/contracts/src/threadExecution.ts:169–174` resolves execution from the explicit runner or the serving environment. A handoff can show owner → runner. `apps/web/src/components/studio/CoordinatorReplySources.tsx:32–43` names the source environment and passes the original source thread and environment IDs on click; the unavailable guard remains in place.
- **Restart and update:** `apps/web/src/components/sidebar/SidebarChrome.tsx:179–188` passes the window name for display. In `apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx:403` the existing restart handler still uses `window.desktopBridge`. Neither the display name nor the selected coordinator chooses the update target.
- **Extractions:** `apps/web/src/components/studio/CoordinatorWorking.tsx:6–22` preserves the one-second timer, cleanup, status and elapsed time. `apps/web/src/components/studio/CoordinatorMachineTag.tsx:26–51` preserves the remote-only condition and changes the visible text and tooltip, not navigation or access.
- **Link dialog:** `apps/web/src/components/studio/ProjectLinkDialog.tsx:632–636` still maps the radio choice to the kept side; line 541 still gates the button on readiness and calls `link()`. The description and consent copy changed, not the selection, payload or operation.
