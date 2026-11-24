<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=1299942461c4fdecf3bbcde814c7a86167a00500 at=2026-11-19T15:35:15.038Z -->
FIX FIRST
Verdict: fix first

Reviewed `1299942461c4fdecf3bbcde814c7a86167a00500`, the fetched head of `anton-abyzov/specwithcode#705`. One high finding remains on the new automatic-progress path. Citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at that commit.

## High · finding 4 · AC-47: a second automatic handoff can go unseen

Two projects start automatic handoffs between polls. `apps/web/src/components/handoff/handOffProgress.logic.ts:249` selects one group, but lines 264–266 mark **both** seen. The dialog displays only the selected group (`apps/web/src/components/handoff/HandOffProgress.tsx:575–580`); pressing Done closes it without showing the other. The same loss occurs if a new handoff arrives while progress is already open: lines 510–514 mark it seen before checking whether it can open.

Reproduced against the reviewed Git object in memory: after an empty baseline, a poll with pending groups B and A returned `{"firstShown":"B","markedSeen":["B","A"],"nextShown":null}`. A's progress never opens, even though its transfer is still pending. Keep the current dialog in place, but queue unseen groups or show them together. Test two groups in one poll and a second arrival before dismissal; both must be displayed exactly once.

## Round 1 dispositions

| Finding | Disposition at the reviewed head |
|---|---|
| 1 · mixed batch | Closed. `apps/server/src/handoff/HandoffTransferStore.ts:458–464` includes retained siblings. If storage has already dropped one, `apps/web/src/components/handoff/handOffProgress.logic.ts:198,126,321` marks the list incomplete, suppresses “All” and explains why. |
| 2 · wrong window | Closed. `apps/web/src/components/handoff/HandOffMachineDialog.tsx:626–635,539,235–241` sends a request-specific batch ID, selects only matching progress and keeps the request error visible. `apps/server/src/handoff/HandoffTransferRunner.ts:936–948` persists the ID on each new record. |
| 3 · stale Resume here | Closed. `apps/web/src/components/handoff/HandOffProgress.tsx:387–390` sends the row identity. `apps/server/src/handoff/HandoffTransferRunner.ts:1026–1032` checks the open operation inside the thread lock before changing its state. |
| 4 · automatic and no-move view | Partial. A single fresh automatic group opens without a click (`apps/web/src/components/handoff/HandOffMachineDialog.tsx:111`); overlapping starts fail as above. The typed no-record entry and its view exist at `apps/web/src/components/handoff/HandOffProgress.tsx:455–462,488–489,552–560`. Its caller belongs to T-13. |
| 7 · `/away` | Closed. `apps/web/src/studio/useComposerAppCommands.ts:53–63` selects machine scope for `/away` and project scope for `/handoff` in a thread. The chat and coordinator fallback paths call it at `apps/web/src/components/ChatView.tsx:12521` and `apps/web/src/components/studio/CoordinatorComposer.tsx:73`. |

**Previous follow-ups:** The description key is present in all eight catalogs and translated at both menu call sites (`apps/web/src/components/chat/ChatComposer.tsx:3076`, `apps/web/src/components/studio/CoordinatorSlashMenu.tsx:48`). EC2-09 tests both directions against the v1.0.383 snapshot field list, not the current snapshot decoder twice (`apps/web/src/components/handoff/handoffMode383.fixture.ts:22`, `apps/web/src/components/handoff/handOffProgress.logic.test.ts:488–504`). Explicit and implicit single-thread selection now exclude outdated peers, and each update action retains its own peer and preflight result (`apps/web/src/components/handoff/HandOffThreadDialog.tsx:389,408–411,503–520`).

## Red evidence and scope

Checked `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t12/red-log-round-1.md` against both tests-only commits. Seven of eight blobs match `30abdbab0` exactly. The logged runner blob `2bc1ab7d7` became `591df8c77` on rebase; their only difference is an unrelated 57-line replay test. The regression assertions are unchanged. The sole blob in `1308d5024` matches `9653b0120` exactly. The earlier series' range-diff shows rebase context in the first patch and exact matches for the other two.

Behavioral reds show the missing stayed row, server-generated rather than requested batch ID, hidden request error, stale release changing `handing-off` to `active`, missing German catalog key, and the coordinator `/away` command leaving the dialog request null. Missing-export errors for the new helpers and the command-test setup are **not** behavioral reds. In particular, the three reds at `1308d5024` do not exercise two undelivered groups. The worker reports 585 web and 77 server tests passing after rebase; those suites were not rerun here. `git diff --check` passed.

Findings 5 and 6 remain open by design for T-10 in `anton-abyzov/specwithcode#702`. The no-move caller stays with T-13 in `anton-abyzov/specwithcode#715`. Neither affected this verdict.
