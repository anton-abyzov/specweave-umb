# Verify — 1481-mcp-servers-can-ask-the-person-for-input-in-claude-threads-form-mode-elicitation

PASS · 2026-11-26T06:44:52.704Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (10s)

```
test_absent_and_idempotent (__main__.SafetyTests.test_absent_and_idempotent) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests.test_dirty_and_untracked_preserved) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests.test_existing_empty_and_atomic_race_preserved) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests.test_final_readback_detects_descendant_and_staging) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests.test_incomplete_runtime_and_release_never_pass) ... ok
test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts (__main__.SafetyTests.test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests.test_missing_or_diverged_upstream_is_preserved) ... ok
test_new_and_legacy_clones_fetch_and_track_future_feature (__main__.SafetyTests.test_new_and_legacy_clones_fetch_and_track_future_feature) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests.test_offline_bundle_and_bad_digest) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests.test_remote_drift_preserves_old_checkout) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests.test_scoped_transport_preserves_identity_and_rejects_redirects) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests.test_unpushed_commit_preserved) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests.test_unsafe_paths_urls_and_symlinks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 9.597s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.234s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.076s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (585s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD c283af4dae against origin/main (merge base c66946d3c7); logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T//studio-pr-gate.dhoRxc
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          2
typecheck                                    pass         34
fleet                                        pass        195
apps/chrome-extension                        pass          1
apps/desktop                                 pass         16
apps/marketing                               pass          0
apps/mobile                                  pass         16
apps/web                                     pass        237
infra/relay                                  pass         14
oxlint-plugin-studio                         pass          7
packages/client-runtime                      pass         13
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          0
packages/shared                              pass         12
packages/ssh                                 pass          8
packages/tailscale                           pass          1
scripts                                      pass         22
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 585s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (620s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.2BgL5OGpxr

Running the server suite as 6 shards; logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.2BgL5OGpxr
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0         405    238    3052        0
2      0         584    252    3606        0
3      0         620    254    3286        0
4      0       529.8    254    3303        0
5      0       572.3    254    3981        0
6      0       584.2    255    3476        0
Server shards: passed in 620s
```

- Working directory: . (explicit)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (9s)

```
test_absent_and_idempotent (__main__.SafetyTests.test_absent_and_idempotent) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests.test_dirty_and_untracked_preserved) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests.test_existing_empty_and_atomic_race_preserved) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests.test_final_readback_detects_descendant_and_staging) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests.test_incomplete_runtime_and_release_never_pass) ... ok
test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts (__main__.SafetyTests.test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests.test_missing_or_diverged_upstream_is_preserved) ... ok
test_new_and_legacy_clones_fetch_and_track_future_feature (__main__.SafetyTests.test_new_and_legacy_clones_fetch_and_track_future_feature) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests.test_offline_bundle_and_bad_digest) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests.test_remote_drift_preserves_old_checkout) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests.test_scoped_transport_preserves_identity_and_rejects_redirects) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests.test_unpushed_commit_preserved) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests.test_unsafe_paths_urls_and_symlinks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 8.613s

OK
```

- Working directory: . (explicit)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.239s

OK
```

- Working directory: . (explicit)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.082s

OK
recorded
```

## Acceptance criteria

10/10 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | The `approval_request` turn item of an `mcp-elicitation` request gains one optional `elicitation` object with `serverName`, `mode`, `message` and `requestedSchema`. Codex requests that do not fill it keep today's panel unchanged. In a Claude thread, an `elicitation/create` in form mode from any MCP server the thread loads reaches the person as a card titled "<server> asks for input", showing the message and the fields of `requestedSchema`: string (with the `email`, `uri`, `date` and `date-time` formats and min and max length), number and integer (with minimum and maximum), boolean, single-select (`enum`, `enum` with `enumNames`, or `oneOf` of `const` and `title`) and multi-select arrays (`items.enum` or `items.anyOf`, with min and max items). Defaults are pre-filled and required fields are enforced. **Submit**, **Decline** and **Cancel** answer `accept` with `content`, `decline` and `cancel`. The server re-validates submitted content against the schema; a schema the card cannot show (unknown type, nested object, over the size limit) answers `cancel` and the thread notes "<server> asked for input in a form SpecWithCode can't show yet; it was cancelled." |
| AC-02 | x (tasks) | met | The handler is the SDK's `onElicitation` option, built in the new `apps/server/src/provider/ClaudeMcpElicitation.ts`. `ClaudeAdapterV2.ts` gains only the option wiring and the response hook (at most 15 lines). When the SDK `signal` aborts (turn interrupted, thread stopped), the card closes as cancelled and the call answers `cancel`; nothing waits forever. |
| AC-03 | x (tasks) | met | Every Claude MCP form needs the person, including a form with no fields. Its card advertises no `accept` option (Submit lives on the form), and `isConfirmOnlyElicitation` (`FullAccessApprovals.ts:86-90`, which treats any `accept` option as confirm-only) returns false for any item that carries `elicitation`. The orchestrator's `runtime-request.respond`, which every route passes through (the person's client over the WebSocket, the agent tool, Full access, relays and internal cancels), refuses an accept on a Claude form that carries `answeredByThreadId` ("Only the user can answer this form. Wait for their answer.") or carries no `answers` ("Submit this form from its card in the thread."). Decline and Cancel stay open to every route, so Stop, settle and dismiss still close a card. Codex confirm-only elicitations keep 0936 AC-03. |
| AC-04 | x (tasks) | met | No agent can answer an elicitation card: `studio_pending_request_respond` (`apps/server/src/mcp/toolkits/thread/handlers.ts:412-420`) refuses it with "Only the user can answer an approval card. Wait for their answer.", as it refuses a Gmail send, and the orchestrator refuses it again (AC-03). `studio_thread_send` `answersRequestIds` does not close it. One terminal response only: when two machines answer the same card at once, the first wins and the second is told "This form was already answered."; a card closed by Stop or the timeout answers "This form was closed.". While the card is open the thread's pending request is a person-answered `mcp-elicitation`, so it reads "Waiting on you" and is listed under Needs you through the existing mapping (`packages/client-runtime/src/state/models.ts`, `AWAITING_PERSON_BY_REQUEST_KIND`); the Blocked row and the alert placement of `decision_alert_on_both_machines` follow from that pending request with no new code. An app update that interrupts a stale card (0936 AC-05) cancels the tool call; the form is not shown again after the restart. |
| AC-05 | x (tasks) | met | A URL-mode request answers `decline`, visibly: the thread notes "<server> wanted to open a link in your browser. SpecWithCode doesn't open MCP sign-in links yet; finish it from the tool's own terminal." The URL is neither shown as a link nor opened, and no card appears. |
| AC-06 | x (tasks) | met | A probe recorded in the increment's `reports/` runs an HTTP MCP tool call held for 3 minutes and for 7 minutes through the Agent SDK with the exact server entry and environment a Claude thread gives studio-code (`type: "http"`, `timeout` 65 minutes, the thread's `env`; studio-code attaches over HTTP, `ClaudeAdapterV2.ts:1395-1402`), on the installed CLI 2.1.331 and on the SDK's bundled CLI. The held calls send no progress (a quiet call), and a cancellation run aborts a held call mid-way. Each held call returns inline, not moved to a background task and not cut by an idle timeout; the cancelled call ends promptly. This check is independent of the form card and does not block its merge. If one fails, the studio-code session environment sets `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS=0` and a `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` above `CLAUDE_STUDIO_MCP_TOOL_TIMEOUT_MS`, the probe passes, and the report states that these variables also apply to the user's own MCP servers in Claude threads. |
| AC-07 | x (tasks) | met | The new `apps/web/src/components/chat/McpElicitationForm.tsx` renders the card. `ComposerPendingApprovalPanel.tsx` routes an approval that carries `elicitation.requestedSchema` in form mode to it. Requests without it (today's Codex cards) keep the current panel and actions. `ChatComposer.tsx` and `ChatView.tsx` gain hook lines only (at most 15 each). |
| AC-09 | x (tasks) | met | Answers are checked and kept private. On an accept, the orchestrator validates `answers` against the card's bounded schema (D-04) with the shared validator before the request resolves; answers that do not fit are refused with the first field's reason ("<field title>: Required.") and the card stays open. The resolved request in events and projections, and the effect that carries the answer, store only a redacted summary (each answered field's key with "[redacted]"), never the values (`Orchestrator.ts` copied answers into the resolved request, `Orchestrator.ts:9054-9060` on the base). The raw answers reach the Claude adapter through an in-process hand-off that is dropped when the card closes. The server's message is shown as plain text (no Markdown, no links) under the server's name. A form whose field key or title asks for a password, passcode, token, API key, private key, PIN, one-time code or similar is never shown: it answers `decline` and the thread notes "<server> asked for a password or secret ("<field>"). SpecWithCode doesn't send those through forms, so it was declined." Tests cover Stop, the 30-minute timeout and two answers at once. |
| AC-10 | x (tasks) | met | Hooks: the SDK runs `Elicitation` hooks before `onElicitation`, and a hook that answers wins. The app installs no `Elicitation` or `ElicitationResult` hook (a test pins the hook events in the options the adapter opens the query with). A hook in the user's or project's own Claude settings (`settingSources` user, project and local) can still answer first; that is the user's configuration and is noted here and in the module header. |
| AC-08 | x (tasks) | met | Unattended threads: when the thread was not created by the person (a delegated worker, a routine's thread) or the turn is a routine run, the card still appears under Needs you; if nobody answers within 30 minutes it closes as cancelled, the tool call gets `cancel`, and the thread notes "No one answered <server>'s question in 30 minutes; it was cancelled." The 30 minutes is one named constant, `UNATTENDED_MCP_ELICITATION_TIMEOUT_MS`. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@anton-m5max-proled | unset SPECWEAVE_STUDIO_THREAD_ID CLAUDECODE CLAUDE_CODE_SES… |  |
| T-02 | done | claude@anton-m5max-proled | unset SPECWEAVE_STUDIO_THREAD_ID CLAUDECODE CLAUDE_CODE_SES… |  |
| T-03 | done | claude@anton-m5max-proled | unset SPECWEAVE_STUDIO_THREAD_ID CLAUDECODE CLAUDE_CODE_SES… |  |
| T-04 | done | claude@anton-m5max-proled | unset SPECWEAVE_STUDIO_THREAD_ID CLAUDECODE CLAUDE_CODE_SES… |  |
| T-05 | done | claude@anton-m5max-proled | test -s .specweave/increments/1481-mcp-servers-can-ask-the-… |  |
| T-06 | done | claude@anton-m5max-proled | test -s .specweave/increments/1481-mcp-servers-can-ask-the-… |  |
| T-07 | done | claude@anton-m5max-proled | unset SPECWEAVE_STUDIO_THREAD_ID CLAUDECODE CLAUDE_CODE_SES… |  |
| T-08 | done | claude@anton-m5max-proled | grep -q Cancellation .specweave/increments/1481-mcp-servers… |  |

8/8 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
