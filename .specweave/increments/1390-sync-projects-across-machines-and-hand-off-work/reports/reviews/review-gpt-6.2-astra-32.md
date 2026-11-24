SHIP
Verdict: ship

| Prior finding | Disposition | Head evidence |
|---|---|---|
| T24R2-01: a marked takeover accepts an unlocked final checkpoint | Fixed. A marked request can launch only with a locked decision. An ordinary request can still use the same checkpoint. | `apps/server/src/handoff/handoffReviewLock.ts:332-338` converts `unlocked` to `refused` for marked requests. `apps/server/src/handoff/HandoffReceiver.ts:660-668,737-746` enforces that decision before changing the workspace and again before selecting the launch model. The lease and launch follow at `:802-825`. |

## Blocking findings

None. The round 3 delta preserves AC-40 on the reported path.

## Follow-up (non-blocking)

No new findings. The workspace-cleanup case from round 2 remains tracked separately.

## What I verified

Reviewed `anton-abyzov/specwithcode#690` at `738200021dd8a334d638fd9ff6bb5fa40ea8e992` against main `3c2173d49bdd525e24bf4f8b6b98d7d5cf32f525`. Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

- **Red evidence:** `gh run list --commit` returned no runs for the rewritten tests-only commit `4242d4fe234b73d7049ee0dce2d5a1936b3d2a34`. Its pre-rebase counterpart `ad2ebcd8ae8b862f8945f4e9bd5375a633c0ca3e` has the identical stable patch ID `68bf5c3b4ab2c7a42004ee85e7fbe11d9756de66`. [Server job 135611402444](https://github.com/anton-abyzov/specwithcode/actions/runs/44538604680/job/135611402444) failed on T24R2-01: `AssertionError: expected [ { …(11) } ] to have a length of +0 but got 1`. The overall run was cancelled; the server job failed, not cancelled.
- **Regression coverage:** `apps/server/src/handoff/handoffReviewLock.test.ts:870-902` calls the receiver with a marked request and an ordinary-titled, lockless checkpoint. It asserts zero launches, a 409 provider refusal, no thread, continuation or new epoch, then proves the same checkpoint launches once when unmarked.
- **Rebase:** Compared `apps/server/src/handoff/HandoffMoves.ts` directly with main, which includes T-19 and T-21. The onward refusal still precedes preparation and the hold (`:712-728`); launcher registration still precedes resend (`:599-606`). The post-interrupt read checks for a change in review status and releases the hold and resumes locally on failure (`:745-765`). Only after those checks does the sender build the marked request and dispatch it (`:781-790`). The fixture and its two consuming tests now name `v1.0.386`.
- **CI:** The pre-rebase fix passed `Checks` run `44540878100`. Exact-head [Checks run 44544285024](https://github.com/anton-abyzov/specwithcode/actions/runs/44544285024) was queued when inspected; the earlier pass does not replace that gate. `git diff --check` passed. No local checkout, build, install or test run.
