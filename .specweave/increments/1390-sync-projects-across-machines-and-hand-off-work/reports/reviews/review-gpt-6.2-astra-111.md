<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=9b1949d17f2e81891fe862d4e0ba86c9a8060f7a at=2026-11-20T03:15:02.158Z -->
# Review: 1390 AC-45 worker routine admission
Verdict: fix first

Reviewer context: fresh session. The delta changes only a comment. The 60-second default and per-check override match `apps/server/src/scheduledTasks/ScheduledTaskCheck.ts:17,36`. No code change is requested.

## [high] The PR body still equates refusing admission with preventing process start

The second Change bullet says that once a handoff is recorded the source “starts no command check for it.” If the consult admits the check, then the handoff is recorded during workspace access, the process can start afterward. `apps/server/src/scheduledTasks/ScheduledTaskService.ts:1019-1035` and the body's Known limits both describe this exception. Replace the guarantee with “a consult that observes the recorded handoff refuses the run before starting its check.” The window itself is accepted.

## [medium] A gate without `continuedOn` does not necessarily return `here`

The third Change bullet says such a gate “still means `here`.” Only the continuation lookup defaults to `here`; `apps/server/src/handoff/HandoffTurnGate.ts:76-87` still calls `check`, and a non-null refusal returns `wait`. Qualify the sentence to describe the lookup rather than the admission result.
