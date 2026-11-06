# 1211 Answer worker questions from the coordinator

## Problem
The supplied photo shows the oly coordinator on M3 beside Walk through Olympus training. Anton replied in the coordinator authorizing Agree clicks. The coordinator says it forwarded permission, but the worker still asks whether he personally reviewed the course. The photo does not prove a lost message: permission and a factual attestation differ. Independently, the app injects an unconditional rule that a go-ahead in the coordinator never answers worker questions. That needless location requirement forces users to repeat answers.

## Scope
In: remove the coordinator-only location restriction, forward identifiable answers verbatim with provenance, clarify ambiguous destinations without inventing answers, retain worker evaluation and native permission controls, test the forwarding API with coordinator-origin answers.
Out: automatically choose question options, certify personal understanding, change provider approval controls, run Olympus training, release the app, or redesign cross-thread question outcome state.

## Acceptance Criteria
- [ ] AC-01: Coordinator context instructs forwarding an identifiable user answer to its owning worker without requiring the user to repeat it there.
- [ ] AC-02: A coordinator-origin answer reaches the worker unchanged as user-authored text with routing provenance and stable retry identity; agent-authored text cannot masquerade as a user answer.
- [ ] AC-03: Coordinator context preserves ambiguity handling, worker evaluation, personal factual declarations and native permission controls instead of treating every go-ahead as an answer.
- [ ] AC-04: Evidence distinguishes the photographed pending attestation from the verified process defect; fresh review and required CI pass before merge, with no release.

## Approach
Change the coordinator role in apps/server/src/project/ProjectWorkspaceService.ts. Remove the contradictory blanket refusal and reuse studio_thread_send forwardMessageId, whose implementation already preserves local provenance and idempotency. Keep this a routing instruction rather than automatically mapping free text to a question option. Add role coverage and direct coordinator-message cases to the existing MCP forwarding regression. Update the agent-instruction documentation and retain screenshot analysis in reports. Live M3 history is unavailable without its project/thread identifier; the coordinator confirmed no discovery tool is available and directed work to continue from the photo without training actions.

## Decisions
### Defaulted
- D-01: Users may answer in either conversation. The coordinator routes their words; the worker decides whether they answer its actual question.
- D-02: Permission to click does not itself assert personal review or understanding. Do not auto-select an attestation option.
- D-03: Preserve native approval mechanisms and Stop holds. Do not broadcast ambiguous replies to several workers.
### Open
- None for implementation. Full historical delivery verification needs the M3 oly projectId or worker thread link; report as unverified evidence.

## Tasks
### T-01 Forward coordinator answers and cover provenance
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/project/ProjectWorkspaceService.test.ts, apps/server/src/mcp/OrchestratorMcpService.activity.test.ts, docs/internals/agent-instructions.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/coordinator-answers/apps/server && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectWorkspaceService.test.ts src/mcp/OrchestratorMcpService.activity.test.ts

### T-02 Verify review and merge evidence
- AC: AC-04 | Files: reports/coordinator-answers.md | Test: gh pr view --repo anton-abyzov/specwithcode-dev --json state,mergeCommit,statusCheckRollup

## Completion
Verify and close 1211.
