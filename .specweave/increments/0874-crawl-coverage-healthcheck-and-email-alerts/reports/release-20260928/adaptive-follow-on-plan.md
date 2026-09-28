# 0874 follow-on: resumable adaptive search

PR74 stays frozen at9f2b9795. Initial deployment keeps SHARD_BISECT off and verifies an honest seven-root sweep; it does not satisfy the breadth AC.

Ownership refreshed at16:53Z: no live Claude process has a SpecWeave checkout cwd; original product planning/source files are clean; no ledger claims exist in the original0874/0875 directories;0875 is completed. Isolated0874 evidence claims T024/025/026 belong to this lane. This is a fresh owner check, not an inference from old timestamps. Recheck before any implementation and use a new branch/worktree based on approved main, not the frozen release branch.

## Proposed scope and files

Existing0874 T027, AC-US3-05/06 and AC-US4-01. Files: `crawl-worker/lib/adaptive-search-plan.js` (new), `crawl-worker/sources/github-sharded.js`, `crawl-worker/lib/source-result.js`, `crawl-worker/scheduler.js`, their focused `crawl-worker/__tests__` files, and `crawl-worker/DEPLOY-NOTES.md`. `lib/search-windows.js` remains the tested splitting primitive; no rewrite of other crawler sources or credential plumbing.

## State and algorithm

Persist one versioned checkpoint with phase `planning` or `crawling`, canonical configuration signature (query roots, normalized mode, ranges, cap and max depth), stable sweep ID, pending range stack with depth, accumulated leaf plan/counts, terminal capped-leaf count, completed probe count, crawl position and accepted discovery keys. Preserve atomic temp+rename writes; a planning checkpoint must not expire while it is making bounded progress. Legacy completed leaf checkpoints remain readable. Configuration mismatch must be explicit, not silently reuse a coarse seven-root plan as adaptive evidence.

For planning, take the next pending range without removing it, perform one authenticated count probe with a request timeout, derive children or a leaf, then atomically persist the updated queue and counters. A process failure before persistence repeats only a read-only probe; after persistence it resumes the exact remaining queue. No skill submissions occur during this phase. Do not re-probe the root a second time as the current expansion helper does.

Bound each invocation by a conservative wall-clock deadline and request budget below the scheduler's120-minute timeout. Check deadline before every probe/page and before rate-limit waiting; if the next wait exceeds the remaining budget, persist and return `completed:false`, `phase`, progress and retryAt. Scheduler understands continuation distinctly from completion, retains the same sweep ID, does not emit a dead-man success for planning/partial progress, and honors a bounded continuation delay rather than the full normal sweep cooldown. Errors preserve the next pending range and continue through existing error/backoff counters. Neither partial nor failed work can become a clean sweep.

For crawling, use the same deadline and persist after accepted flushes. Never mark the shard/page advanced until all discovered items have an intake acceptance or durable retry receipt. On failed flush, preserve replayable discovery keys using the reviewed PR74 rollback invariant. Existing known-key cache prevents resubmitting durable accepted work after a crash/replay. Completion requires the pending plan queue empty and every leaf drained with zero lost items.

Single-byte/max-depth leaves whose reported count remains above1000 are retained but counted as capped. A completed retrieval pass is not a claim of exhaustive coverage: emit `coverageComplete:false` and capped-leaf counts/omitted lower bound, and keep breadth acceptance gated if the plan cannot meet it. Do not invent another ignored GitHub dimension or discard these leaves.

## Required regression proof

1. Stop after each possible probe boundary and resume; exact same leaves as uninterrupted expansion, no gaps/overlap, no dropped pending ranges.
2. Crash before/after atomic checkpoint, expired rate-limit budget,401/403/429/5xx/network failure; no false completion or lost progress.
3. Old coarse checkpoint versus new adaptive configuration; explicit migration/mismatch behavior and no coarse-plan-as-full-breadth claim.
4. Partial crawl/intake flush failures followed by restart; all unaccepted items replay, accepted items avoid duplicate submission, no checkpoint advance on loss.
5. Scheduler partial results retain continuation status and never ping dead-man success; completed sweep counters reflect the whole sweep without double-counting resumed prefixes.
6. Singleton capped ranges/max depth and restart preserve the truthful incomplete-coverage signal.
7. Bounded local HTTP fake GitHub+intake integration proves planning and crawling continuation across fresh process restarts. Live verification uses the approved existing VM3 token and preserved source-owned scheduler, after a separate independent review/deployment.
