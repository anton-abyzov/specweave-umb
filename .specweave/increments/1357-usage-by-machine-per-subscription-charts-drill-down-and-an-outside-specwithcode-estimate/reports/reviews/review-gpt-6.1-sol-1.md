<!-- specweave review: reviewer=gpt-6.1-sol model=gpt-6.1-sol family=openai author=claude depth=standard repo=. base=803d14d90eee3674a549aaa4518c116a254c7e59 head=2bf1188b0e2d75842ac658f99ba27997874b0bac at=2026-11-20T17:57:25.245Z -->
# Review: PR 795 Usage by machine
Verdict: fix first
Reviewer context: new session, GPT-6.1-Sol on Codex reviewing Claude-written work.
Reviewed commit: 2bf1188b0e2d75842ac658f99ba27997874b0bac
Scope: anton-abyzov/specwithcode, usage-by-machine against origin/main, 49 changed files.

## [high] packages/shared/src/usageOutsideEstimate.ts:360 Partial-hour boundaries include use outside the covered interval
Severity: important.
Trigger: readings at 00:00 = 0%, 00:30 = 10%, 01:00 = 10%; request the interval [00:30, 01:00), with no recorded use inside it and no silent holders. `spread` first puts the earlier 10-point gain in the 00:00 hourly bucket; the period loop then includes that whole bucket despite `coveredFromMs` being 00:30. Verified output is consumedPoints=10, outsidePoints=10, detected=true, confidence=high. The actual limit movement in the requested interval is zero. This can falsely attribute earlier use to use outside the machines. Partial reset hours and non-integral-hour local midnight boundaries are affected. Clip stretches to the requested interval before summing points, and handle recorded boundary hours consistently instead of treating whole buckets as interval totals.
Evidence: /srv/specwithcode/minisforum/scratch/review-pr795/reproduction.txt. Reproduction loads the actual estimator and forecast code, with the unused forecast account helper dependency stubbed.

## [high] packages/shared/src/usageMachineShareView.ts:252 Reset-window machine totals include pre-reset use on the same day
Severity: important.
Trigger: an account resets at 18:00; on that date a machine records $100 before 18:00 and $10 after it. `periodOf` correctly sets startMs to 18:00, but the merge receives only sinceDay/untilDay and periodEndMs. `mergeMachineShare` filters cells by day at packages/shared/src/usageMachineShare.ts:369, so the whole $110 daily cell survives. The reset-window bar, machine shares, drill-down and totals show $110 as use since reset instead of $10. The estimate separately starts at 18:00, and `measurePerPoint` then scales its outside points using the inflated whole-day total, further distorting the combined bar. Verified by tracing the period-to-merge-to-segments path; daily cells contain no timestamp with which to recover the correct split. Preserve enough intra-day data to apply the exact reset boundary, or explicitly present a calendar-day range rather than claiming exact since-reset totals.

## [medium] apps/server/src/usage/usageAccountSpans.ts:209 Distant readings bypass the current-account fallback
Severity: important.
Trigger: no recorded span covers a historical session, the driver history contains accounts A and B, its nearest reading is more than 12 hours away, and B is signed in now. The resolver immediately returns unknown at line 209, never reaching the current-account fallback at line 211. Verified direct call returns {accountKey:'unknown', rule:'unknown'} instead of B/current. This contradicts the specified attribution order and splits those sessions into an unknown subscription even when the fallback account is available. Let an ineligible reading fall through to the current account before returning unknown.
Evidence: /srv/specwithcode/minisforum/scratch/review-pr795/reproduction.txt.

## Checks and limits
No blocker-severity findings. The two high-severity correctness findings require fixes before shipping.
- Ran the requested pickup successfully in /srv/work/github/specweave-umb after the reviewed app checkout reported no matching increment.
- Focused test: packages/shared/src/usageOutsideEstimate.test.ts, 12 tests passed. No repo-wide tests, lint, typecheck or builds ran. No existing verification report was present in the increment reports directory, and no broad verify was run under the request's restrictions.
- Inspected estimator rate guards, reset detection, server SQL and transcript/turn exclusion, span lifecycle, source deduplication, silent-holder handling, fallback units, shared periods, web/mobile loading paths, email presentation and the added diagnostics:read RPC mapping. The positive calibration-ratio filter prevents a zero rate denominator; the RPC scope matches the usage-summary scope; named account emails go through maskEmail. No confirmed personal data added to the public diff was found in the privacy scan.
- No code under review was edited, and no commits, pushes, GitHub comments, browser sessions or live database reads were made. Head matched the GitHub PR when checked.
Nits: none.
