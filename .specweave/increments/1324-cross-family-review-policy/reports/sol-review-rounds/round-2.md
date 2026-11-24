# Review: 1324 Cross-family review policy (round 2)
Verdict: fix first · risk: high · 56 changed files · 6 findings (2 high, 4 medium)

Reviewed heads: SpecWeave `5e3d1c3e5f37f8089a8406dbfd99dc39401dc675`; SpecWithCode `617947aabc5038ab01ec1b90f74aae9bc45295a1`. Reviewer: GPT-6.1 Sol (Codex on linux-mini), November 13, 2026.

All 143 requested app tests passed on the merged head. All eight review entries survived in all eight catalogs. SpecWeave build and unit suites were not rerun; source probes reproduced the failures below.

## [high] specweave src/core/tasks/closure-gate.ts:236 Literal pathspecs silently disable content checks for supported globs

With task Files `src/core/review/*.ts` and a ship review at `5006fc084`, the gate returned `[]` although four matching files changed. Fix: expand globs or pass them as ordinary pathspecs.

## [high] specwithcode apps/server/src/orchestration-v2/MachineLimitHandoff.ts:419 The review lock is lost after machine handoff

Replication does not carry `routing.reviewFamily`; a review moved to machine B can fall back to Claude there. Fix: carry the lock or refuse destinations that cannot keep it.

## [medium] specwithcode packages/shared/src/reviewPolicy.ts:354 Family-only recovery ignores a pinned reviewer model

A policy pinned to `openai (gpt-6.1-sol)` persisted only the family; quota recovery could switch to `gpt-6-luna`. Fix: persist and enforce the model pin.

## [medium] specwithcode packages/shared/src/reviewPolicy.ts:302 Repository derivation still disagrees with CLI ownership

Registered checkouts outside `repositories/<org>/<repo>` resolved to `.`; `**Files**:` fields were ignored. Fix: use registered repositories and the CLI's ownership rules.

## [medium] specweave src/core/tasks/closure-gate.ts:138 Strict closure still uses the old filesystem chronology

`reviewNotices` sorted by mtime and turned an older fix-first into an error after the policy gate accepted a newer ship. Fix: one ordering, one judge.

## [medium] specweave src/core/review/policy.ts:79 Parsing destroys underscore aliases before normalization

`Reviewer: openai (gpt_6_1_sol)` became `gpt61sol`. Fix: strip only enclosing Markdown marks.
