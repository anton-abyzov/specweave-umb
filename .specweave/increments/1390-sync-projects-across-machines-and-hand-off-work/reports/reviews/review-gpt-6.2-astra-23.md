FIX FIRST
Verdict: fix first

Reviewed: `anton-abyzov/specwithcode#690` at `b19c465fb0554403a8dc6bea249420199f554bb3`. Increment `1390`, task `T-24`. Fresh cross-family review by `gpt-6.2-astra` (OpenAI) of Claude-authored code. Scope: 30 changed files; 6 high-severity blockers and 3 non-blocking follow-ups.

## Blocking findings

### 1. [high] Takeover launches an unlocked review after its final reviewer check refuses

`apps/server/src/handoff/HandoffReceiver.ts:730-734,831` (gates 1 and 3). The source requests Claude, the author's family. The receiver initially has Claude and the permitted OpenAI reviewer, so its takeover check passes at lines 604-618. While it prepares the workspace, the OpenAI sign-in is disabled. The second provider read now returns `refused`. Unlike preflight, takeover treats that result as `unlocked`: it uses the original Claude request and omits the routing marker. The real launcher passes that selection to the first message (`apps/server/src/orchestration-v2/ThreadLaunchService.ts:1337`). An idle continuation also loses the marker.

**Minimal fix:** Handle `refused` explicitly before recording the lease or launching. Only `unlocked` may use the ordinary request. Test a registry that changes from both families to Claude-only between the two decisions; assert the refusal, no launch and no continuation lease.

### 2. [high] A handed-off review can switch to the author's unlisted coordinator model

`apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:641-660` (gates 1 and 3). The worker accepts the resolver's result and adjusts options without checking that the **returned model** satisfies the lock. The exclusions cover only listed slugs (`packages/shared/src/reviewPolicy.ts:465-476`), while the coordinator fallback needs no catalog match (`packages/shared/src/providerFallback.ts:966-996`). For a review pinned to `gpt-5.5` after handoff, I ran the exact-head resolver with no permitted alternative and a ready Claude sign-in listing Sonnet. With the coordinator still configured for Opus on that sign-in, it returned `{ instanceId: 'claudeAgent', model: 'claude-opus-5-5' }`. The worker supplies that coordinator pick at `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:1783`. The policy predates this PR; accepting the result for a newly handed-off, marked review is the path T-24 enables.

**Minimal fix:** Filter the coordinator candidate by the review lock and positively validate the actual selection on every fallback command before dispatch. If no permitted pick remains, wait. Add the unlisted coordinator case to the receiver's second-pick test.

### 3. [high] A same-machine handoff turns an unknown reviewer family into “not a review”

`apps/server/src/handoff/handoffReviewLock.ts:111-114,248-254` (gate 3). An older `Adversarial review:` thread runs on an unclassified model with no routing. A manual handoff to **this machine** can request a different model (`apps/server/src/handoff/HandoffMoves.ts:793-802`). The source explicitly encodes `null` because `toSelf` is true. The receiver treats `null` as an ordinary thread and does not check the title. It can start the requested Claude model with no marker. This differs from the documented limitation that the review **stays**: the remote path refuses, but the self path creates an unlocked continuation.

**Minimal fix:** Return `null` only for `kind === "none"`. Refuse an unknown family on any operation that creates a continuation, including self. Test a title-only, unknown-family review with a same-machine model change; no continuation should launch.

### 4. [high] A cached capability allows a new review to be sent to a previous-release receiver

`apps/server/src/handoff/handoffPeers.ts:365-371,442-443,579-587` (gates 2 and 3). A paired machine advertises the capability, then restarts on `v1.0.383` at the same address within five minutes. A **new** manual review handoff passes `refuseUnlocked` using the cached answer and posts to the ordinary replication route. The previous release ignores the lock. Its preflight still speaks protocol 2 (`apps/server/src/handoff/handoffWire.ts:46,59-60`); the PR's own compatibility test demonstrates that its takeover starts the requested Claude model without routing (`apps/server/src/handoff/handoffReviewLock.test.ts:557-565`). This is not an old copy the sender could not retract. The cache authorizes a fresh transfer to a machine that no longer has the capability.

**Minimal fix:** Make authoritative review transfers require a live, lock-specific acknowledgment before sending the checkpoint or holding the source. Use a feature-specific operation that an older server cannot accept as an ordinary replication or takeover. The UI can keep its cache. Test one sender against the same peer identity before and after a downgrade without advancing the cache clock.

### 5. [high] A requested model is counted as proof that an empty receiver catalog offers it

`apps/server/src/handoff/handoffReviewLock.ts:265-278` (gate 1). During manual preflight or takeover, an installed, signed-in provider with the requested instance ID and `models: []` is credited with `[wanted.model]`. If the stored model is `gpt-5.5`, a receiver without any advertised OpenAI model consequently passes as a permitted destination. The ordinary preflight cannot catch this: it skips model membership for an empty list (`apps/server/src/handoff/handoffPreflight.ts:95-105`). The exact-head arrival function returned `locked`, not `refused`, for that input. This can move the source off its reviewer even if the destination subsequently fails to open the requested model.

**Minimal fix:** An empty catalog is not positive evidence for a locked review. Require an advertised permitted model or an explicit provider confirmation; otherwise return the no-permitted-reviewer sentence. Leave ordinary handoffs unchanged. Cover both manual preflight and takeover.

### 6. [high] A same-model continuation can silently lower policy-required effort

`apps/server/src/handoff/handoffReviewLock.ts:128-136,189-192,317-319` (gate 1). Review depth is translated to reviewer options at delegation (`apps/server/src/mcp/OrchestratorMcpService.ts:3671-3677`). A saved machine target may carry its own options. On an exact model and instance match the sender keeps that target, and the receiver prefers its options over the lock. With a carried `gpt-5.5` review at `high` and a request for the same model at `low`, the exact-head function returned `reasoningEffort: low`. An empty requested option list also suppresses the carried effort. On later switches, an option-bearing fallback similarly wins, and the failed-to-open branch returns before the effort helper (`apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:535-543,651-660`). This is not the known limitation about switching to a *different* model.

**Minimal fix:** Make the carried effort authoritative for the same compatible model and merge unrelated destination options separately. Apply that rule to both normal and failed-to-open fallback commands. Test a conflicting saved effort on arrival and a same-model fallback on another sign-in.

## Follow-up (non-blocking)

1. **Medium, legacy copies:** A previous-release sender cannot identify a routing-only review with an ordinary title; a previous-release receiver can still continue a copy it already held. `apps/server/src/handoff/handoffReviewLock.ts:248-254` and `apps/server/src/handoff/handoffReviewLock.previousRelease.test.fixture.ts:246-257`. These compatibility limits are distinct from finding 4.
2. **Medium, model portability:** A permitted alias that is not a listed slug can be skipped, and a switch to a different reviewer model may use that model's default effort. `apps/server/src/handoff/handoffReviewLock.ts:267-276,319-325`. Neither is needed to reproduce finding 6.
3. **Low, test coverage:** The sender test for choosing the usable sign-in among several permitted sign-ins supplies a stand-in `usable` predicate (`apps/server/src/handoff/handoffReviewLock.test.ts:654-675`). Add a sweep-level case when that selection changes again. The fixture pin and existing file sizes are not release findings.

## What I verified

- Read AC-40, T-24 and the accepted EC2-04 amendment on umbrella `origin/main`. Matched the PR head via GitHub and read code from that Git object, not the moving worktree.
- Traced marker creation, replication, incoming-state persistence, the candidate row, manual and self takeover, initial thread/message dispatch, and the provider worker's second pick. The ordinary two-family, author-only and cold previous-release cases have meaningful assertions. In particular, removing routing changes the second pick to Claude in `apps/server/src/handoff/handoffReviewLock.test.ts:475-500`. The cold old-peer test checks **zero** replication POSTs, with an ordinary thread as a positive control (`apps/server/src/handoff/handoffPeers.test.ts:328-338`).
- Ran three focused checks against exact-head production selection functions in memory from scratch, without a build or install. Observed the author-family fallback in finding 2, the positive empty-catalog decision in finding 5 and the effort downgrade in finding 6. Findings 1, 3 and 4 were verified by tracing the actual decision and launch paths; no live two-machine test was run.
- Exact-head GitHub Actions `Checks` run `44519840166` passed the package gate, three server shards, two web shards, typecheck and overall PR gate. `git diff --check` passed. Commit `468b28e6e` added tests before the implementation; the separate worker red-server and red-web output files were not present when reviewed. CI success is not evidence that the cases above passed. No source was changed.
