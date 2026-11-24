# 1325 adversarial review

Reviewer: GPT-6.1 Sol (Codex, xhigh), run on linux-mini, read-only. PR: https://github.com/anton-abyzov/specwithcode/pull/353

## Round 1 (head `ce251cddc`), November 13, 2026

| # | Severity | Finding | Response (commit `9b278d165`) |
|---|---|---|---|
| 1 | Blocker | `HandoffSecretsStep.tsx:70`: the auto-fill effect re-ticked every secret file after a remeasure or Copy again, including one the person unticked. | The step has no effect now. It is controlled through one `onChange(included, selected)` callback. `HandoffFolderCopy` keeps `secretsOut` (the files the person unticked) and derives `secretPaths` from the summary: the receivable files in repositories that are still copied, minus `secretsOut`. `AddToMachineDialog` works the same way. Test: "keeps an unticked secret file out through Change setup and a new measure". |
| 2 | Blocker | `HandoffFolderCopy.tsx:202`: the secrets opt-out was not persisted, so a reopened or reloaded copy went back to included. | `PendingCopy.secrets = { included, out }` is written when the copy starts and on every change, then restored in `resume`. Test: "keeps secrets left on the source when the dialog closes and reopens before Copy". |
| 3 | Should-fix | `ProjectMachineHandoff.tsx:833`: the Copy menu item overrode an unfinished Git handoff, which may already be published. | A saved Git pointer now takes precedence (`gitPending`). Test: "resumes an unfinished Git handoff on Git when the menu asks for a copy". I confirmed it fails without the fix. |
| 4 | Nit | `tests/composer-foot/main.tsx:180` still passed `onAdd`. | Changed to `onCopy`. |

Also removed: the footer's "Confirm sending the selected secret files" blocker. It can no longer occur.

Checks after the fixes: 696 web tests in 20 affected suites pass, the web typecheck has no new errors, and the `folder-copy`, `machine-folders` and `machine-handoff` headless fixtures pass.

## Round 2 (head `9b278d165`), November 13, 2026

Round 1's remeasure, reopen, Git-precedence and fixture fixes held up.

| # | Severity | Finding | Response (commit `9f3da3a7b`) |
|---|---|---|---|
| 1 | Blocker | `HandoffFolderCopy.tsx:913`: secrets sent before an approval was refused stayed staged when the person unticked them for the retry. | The current list is sent before every approval, including an empty list, which the contract defines as a withdrawal. Replace all does the same. Test: "withdraws secrets sent before a refused approval when they are unticked for the retry". |
| 2 | Should-fix | `HandoffFolderCopy.tsx:532`: the legacy one-click path read a stale `secretPaths` and left out secrets shown as included. | `summaryNow` ref; the paths are recomputed when they are sent. Tests: the one-click copy now sends the included files, or an empty list when the line is unticked. |
| 3 | Should-fix | `HandoffFolderCopy.tsx:891`: after Change setup and a close, the secrets choice was lost because the pointer was gone. | One `SecretsChoice` state. `CopyDraft.secrets` is written while no pointer exists, copied from a cancelled pointer and restored on fill. The pointer's `secrets` field is validated. Test: "keeps an unticked secret file out after Change setup, a close and a reopen". |

Checks: 699 tests pass in 20 affected suites, the web typecheck has no new errors, and lint shows only warnings that already exist on main. `HandoffFolderCopy.tsx` is 1498 lines.

## Round 3 (head `9f3da3a7b`), November 13, 2026

Round 2's retry withdrawal and draft persistence held up. The reviewer checked against an isolated copy of the source that an empty list clears staged secrets.

| # | Severity | Finding | Response (commit `bf4b24704`) |
|---|---|---|---|
| 1 | Blocker | `HandoffFolderCopy.tsx:905`: only the summary was read at send time. The choice, plan, skips and destination came from an older render, so a reopened one-click copy saved with `included: false` sent `.env`, and Copy again used the previous plan's skips. | `useLiveState` backs `summary` and `copy` with refs. `sendableSecrets` (the new module `handoffCopySecrets.ts`) takes the pointer's choice, the latest plan or repository draft, and the destination looked up by the pointer's machine. Test: "keeps a saved opt-out when a reopened one-click copy approves on its own". I confirmed it fails when the choice comes from render state. |
| 2 | Should-fix | `HandoffFolderCopyWatcher.tsx:268`: the background watcher approved one-click copies without sending the secrets. | `stageSecrets` sends the saved choice before the approval. `~/` files stay on the source because the destination's support for them is unknown there. If the send fails it returns "ask" and does not approve. Three watcher tests cover the included send, an empty list for an opt-out, and the failed send. |

Checks: 702 tests pass in 20 affected suites, the web typecheck has no new errors, and `HandoffFolderCopy.tsx` is 1500 lines. CI was green on `9f3da3a7b`.

## Round 4 (head `bf4b24704`), November 13, 2026

Round 3's send-time reads and the watcher's secret staging held up.

| # | Severity | Finding | Response (commit `ea8742738`) |
|---|---|---|---|
| 1 | Blocker | `HandoffFolderCopyWatcher.tsx:247`: while the watcher awaited the source summary, a reopened dialog could untick secrets; the old request still sent `.env` from the captured pointer and approved, because `stopped` was checked only afterward. | `stageSecrets` re-reads the pointer after the summary and gives up (settle returns "ask", no approval) when the watcher stopped, the summary is missing or the operation changed. The choice and destination come from the re-read pointer. It checks `stopped` again after the send, and `settle` checks it right before the approval. Test: "leaves secrets and the approval to a reopened dialog while the source summary is in flight". I confirmed it fails without the fix. |

Checks: 229 tests pass in the 15 copy-flow suites, and the web typecheck has no new errors.

## Round 5 (head `ea8742738`), November 13, 2026

Round 4's fix held up: returning "ask" after unmount shows no stale toast and calls no completion callback, and the dialog withdraws earlier staged secrets with its current list before approving.

| # | Severity | Finding | Response (commit `0f6afb0c6`) |
|---|---|---|---|
| 1 | Should-fix | `HandoffFolderCopyWatcher.tsx:286`: after `await decide()`, the clone path wrote the captured pointer even after unmount, which could erase a reopened dialog's secrets exclusions or replace a newer operation's pointer. | After the await it re-reads the pointer, returns "ask" when the watcher stopped or the operation changed, and merges `cloneDecided: true` into the current pointer. Test: "keeps a reopened dialog's secrets choice when the clone choice answers after unmount". I confirmed it fails without the fix. |

Checks: 230 tests pass in the 15 copy-flow suites, and the web typecheck has no new errors.

## Round 6 (head `0f6afb0c6`), November 13, 2026

Round 5's clone-choice fix held up.

| # | Severity | Finding | Response (commit `1fbddf9a3`) |
|---|---|---|---|
| 1 | Should-fix | `HandoffFolderCopyWatcher.tsx:299`: dropping a stale Replace all wrote the captured pointer after awaiting the status, which could undo a secrets exclusion or newer copy that another tab saved. | It re-reads the pointer and removes `replaceAll` from the current value only while it is the same operation. Test: "drops a stale Replace all without undoing a secrets choice another tab saved meanwhile". |
| 2 | Should-fix | `HandoffFolderCopyWatcher.tsx:341`: a delayed cancelled status removed the pointer even when another tab had started a newer copy. | It removes the pointer only when the operation matches. Test: "keeps a newer copy another tab saved while a closed copy's status was in flight". |

I confirmed both tests fail without the fixes. Checks: 232 tests pass in the 15 copy-flow suites, and the web typecheck has no new errors.

## Round 7 (head `1fbddf9a3`), November 13, 2026

Both round 6 fixes held up. No pointer write still uses state captured before an await.

| # | Severity | Finding | Response (commit `e3966b774`) |
|---|---|---|---|
| 1 | High | `HandoffFolderCopyWatcher.tsx:267`: while `copySecrets` was pending, another tab could untick secrets for the same copy, and the watcher then approved with the earlier staged `.env`. | After the send it re-reads the pointer and approves only when the watcher is still running, the copy is the same and the saved secrets choice is the one it sent. Otherwise the copy waits for the person, whose dialog sends its own list before approving. Test: "does not approve when another tab unticks secrets while they are being sent". I confirmed it fails without the fix. |

Checks: 233 tests pass in the 15 copy-flow suites, and the web typecheck has no new errors.

## Round 8 (head `e3966b774`), November 13, 2026

Round 7's post-send check held up.

| # | Severity | Finding | Response (commit `77b862724`) |
|---|---|---|---|
| 1 | High | `HandoffFolderCopyWatcher.tsx:313`: a Replace all left running in one tab was approved by its watcher from the stale `replaceAll` it read before awaiting the status, with `.env` still staged, although another tab's review had unticked secrets. | `settle` re-reads the pointer first and acts on the current one. Every approval, Replace all included, first checks that the pointer still has the same copy, the same Replace all flag and the same secrets choice. In the dialog, changing the secrets choice clears a pending Replace all, because its staged list is now stale. Tests: "does not approve a Replace all after another tab changes the secrets choice" (fails without the fix) and "clears another tab's Replace all when the review here changes the secrets choice". |

Checks: 235 tests pass in the 15 copy-flow suites, the web typecheck has no new errors, and `HandoffFolderCopy.tsx` stays at 1500 lines.

## Round 9 (head `77b862724`), November 13, 2026

Round 8's pointer recheck held up.

| # | Severity | Finding | Response (commit `ba74b218a`) |
|---|---|---|---|
| 1 | High | `HandoffFolderCopyWatcher.tsx:259`: tab A's delayed secrets send could land after tab B unticked secrets, staged an empty list and approved, which put `.env` back on the source's list. | When A's send returns and the pointer changed meanwhile, A sends the current choice again right away and never approves. It does this even after it stopped, because a stale list must not stay on the source. The corrective send leaves `~/` files out, so it can only send fewer secrets than were chosen, never more. Test: "puts the current choice back and does not approve when another tab unticks secrets mid-send". I confirmed it fails without the fix. |

Server follow-up (out of scope here, because 1325 excludes server and wire changes): staged secrets carry no revision, so two senders can still interleave at the source within one round trip. The same race exists today between two open dialogs on main. The fix is a revisioned `copySecrets` bound to the approval.

Checks: 235 tests pass in the 15 copy-flow suites, and the web typecheck has no new errors.

## Round 10 (head `ba74b218a`), November 13, 2026

Round 9's corrective send held up.

| # | Severity | Finding | Response (commit `1afe272e2`) |
|---|---|---|---|
| 1 | High | `HandoffFolderCopyWatcher.tsx:256`: a copy started before this update saves no secrets choice and had secrets left out. After the update, the watcher read the missing choice as "include all", staged `.env` and approved. | `pendingSecrets(saved)` reads a missing choice as "left on the source". Every copy started since this change saves its choice, so a missing one means an older copy. The watcher and the dialog both use it. A fresh setup with no saved copy still defaults to included, shown on screen before Copy. Test: "keeps secrets on the source for a one-click copy saved before the choice existed". I confirmed it fails without the fix. |

Checks: 236 tests pass in the 15 copy-flow suites, the web typecheck has no new errors, and `HandoffFolderCopy.tsx` is 1498 lines.

## Round 11 (head `1afe272e2`), November 14, 2026

No remaining correctness findings. Round 10's fix holds. A draft saved before this update opens on setup with "Secrets included" visible and needs a new Copy click. Add to Machine jobs keep their own saved list, and Git-only sends no secret files. The reviewer ran six focused watcher checks in memory, and all passed.

Open follow-up, out of scope here: give `copySecrets` a revision bound to the approval (server and wire), so two concurrent senders cannot interleave at the source.

## Outcome

PR 353 was merged on November 13, 2026 as `48dd3b8c1` (squash), at head `1afe272e2` with required CI green. The first CI attempt failed in `mergedCloneSweep.test.ts` (server, unrelated: `ENOENT ... .git/objects/maintenance.lock`), and a full rerun passed. A release was requested with `request-release.sh`: run https://github.com/anton-abyzov/specwithcode/actions/runs/43535843341. `request-release.sh --released 48dd3b8c1` confirms it shipped in v1.0.292.

## Verdict

Verdict: ship. Round 11 (GPT-6.1 Sol, Codex, xhigh, on linux-mini) found no remaining correctness issue at the merged head `1afe272e2`. The only open item is the out-of-scope `copySecrets` revision follow-up above.

Local verify, November 14, 2026: server shards green from an agent shell after PR 369 (`a4c104b52`); `verify:pr` failed once only on the `2099` timestamp flake in `scripts/studio-fleet/test-update-apply.py`, fixed in PR 372.

## Close review after the passing verify

November 14, 2026, Sonnet 5.5, read-only, against `reports/verify.json` `ok: true` (all five commands exit 0, server shards included; 8 of 8 ACs). PR 353 (`48dd3b8c1`) is on main; the 8 later commits touch no task, handoff, copy or secrets file. Rounds 1 to 10 each have a fix and a test; round 11 found nothing. The `copySecrets` approval revision stays an out-of-scope follow-up.

Verdict: ship.
