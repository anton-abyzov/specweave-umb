# Cross-family review policy: set in spec.md, enforced at closure, shown on the plan card

## Problem

Anton wants code written by one model family reviewed by another (Claude-written code by OpenAI GPT-6.1 Sol, deep; OpenAI-written code by Claude Opus). The parts exist but nothing ties them together, so it does not happen:

- The app has an "Adversarial review" setting (1237): app default plus project override, reviewer order, depth, an off-by-default auto switch. On the M4 the order is Claude Opus 5.5, Sol via Copilot (copilot-0889), Muse Wonder. Only the thread menu action and the auto switch read it. `delegate_task` ignores it: `role: "review"` only adds "load sw-review" to the prompt, so a coordinator brief that says "reviewer: Sonnet 5.5" gets a Claude review of Claude code (PR 345, November 13, 2026).
- SpecWeave has `specweave review` (Codex `gpt-6.1-sol` for Claude-written work) and `review.crossModel`, but the umbrella config sets neither, and the closure gate accepts any `reports/review*.md` that says `Verdict: ship`. It never checks the reviewer's family against the author's, never checks which commit was reviewed, and spec.md has no way to ask for a stronger review on a complex feature.
- Of 39 increments completed since 1250, 17 have a review file, none has a `specweave review` record by an OpenAI model, and 2 mention Sol or Codex at all.
- Codex on the M4 and M1 (one account) is at 100% until December 5, 2026; linux-mini's Codex (another account) is at 3% with `gpt-6.1-sol`. Nothing tells the coordinator that, so reviews quietly fall back to Claude.

## Scope

In:
- A review policy with three layers: app default and project override (existing app settings), and a `## Review` section in an increment's spec.md that names the reviewer family or model, its depth, and whether a review is required to close.
- SpecWeave: the policy parser, `specweave review` honoring it, `specweave review --record` to stamp a review written in any tool (app thread, Codex, Claude Code) with model, family, author and reviewed commit, and a closure gate that, when the policy requires it, accepts only a `ship` review by the required family whose reviewed code matches the code being closed.
- App: `delegate_task` with `taskClass: "review"` (or `role: "review"`) and no model picks a cross-family reviewer from the project's reviewer order and the spec's policy, says which one and why each better one was skipped, refuses rather than substitutes when the required family has no reviewer, and flags a named same-family model. The plan card shows "Reviewed by GPT-6.1 Sol at 3f9a2c1" or "OpenAI review required".
- Skills: sw-review, sw-done, sw-increment and sw-grill-me name the policy and the record step.

Out: cross-machine reviewer launch (the refusal names machines is a follow-up; the coordinator can pass `machine` today); changing the Settings UI layout; posting findings to GitHub; mobile clients (they ignore the new optional field).

## Acceptance Criteria

- [ ] AC-01: `resolveReviewPolicy` reads spec.md `## Review` (`Reviewer: cross-family | openai | claude | google | xai | meta | <model id>`, `Depth: standard | deep`, `Required: yes | no`) over `.specweave/config.json` `review.policy` over `review.crossModel` (required, cross-family) over the default (cross-family, standard, not required), and reports which layer set each field.
- [ ] AC-02: `specweave review` uses the policy's reviewer family or model and depth (deep runs Codex at `xhigh`); its record header carries reviewer, model, family, author, depth, repository and reviewed commit. `specweave review --record <file> --model <id> [--head <sha>]` writes the same record for a review done elsewhere, takes the verdict from the file, and refuses a file with no verdict line.
- [ ] AC-03: With a required policy, `specweave complete` (and verify's strict-close preview) refuses unless, for every repository that holds task Files, the newest record matching the policy says ship, follows verification, and its reviewed commit has the same content as that repository's HEAD for the task Files; the error names the required family, the newest review found (model, family, commit) and the next command. Without a required policy, behavior is unchanged.
- [ ] AC-04: `delegate_task` with `taskClass: "review"` or `role: "review"` and no model picks the first available reviewer of another family than the author (the calling thread's model), in the spec policy's family when it names one, from the project's reviewer order; the result's `review` field names the reviewer, the author family and each skipped entry with its reason. When no reviewer of the required family can run, it fails with those reasons and starts nothing. A named model of the author's family runs as asked and the result carries a same-family warning.
- [ ] AC-05: The plan card shows the newest review record ("Reviewed by GPT-6.1 Sol at 3f9a2c1 · ship", "· fix first") and, when the policy requires a review and none matches, "OpenAI review required"; the server reads it from the increment's reports and spec without a CLI, in all 8 catalogs.
- [ ] AC-06: sw-review, sw-done, sw-increment and sw-grill-me document `## Review`, recommend `Required: yes` with a deep cross-family reviewer for complex features (auth, payments, migrations, multi-repo, over ~1k lines), and end every review with `specweave review --record`.

## Approach

Chosen design (option A of two, mockups in `reports/review-policy-options.html`): the policy lives in the spec and SpecWeave enforces it at closure; the app routes and shows it. Option B (an app-owned review stage that stores verdicts in the app database and gates the app's Close action) was rejected: closure from the CLI, Codex or Claude Code outside the app would bypass it, and the policy would not travel with the increment.

Policy format (spec.md, parsed identically by SpecWeave and the app):

```markdown
## Review
- Reviewer: openai (gpt-6.1-sol)
- Depth: deep
- Required: yes
```

Model family by id: `gpt|o[0-9]|codex` openai, `claude|opus|sonnet|haiku|fable` claude, `gemini` google, `grok` xai, `muse` meta. `cross-family` means any family other than the author's.

SpecWeave (`repositories/anton-abyzov/specweave`, branch from develop):
1. `src/core/review/policy.ts`: `parseReviewSection`, `resolveReviewPolicy(projectRoot, incrementDir)`, `familyOfModel`. `ReviewConfiguration.policy` in `config/types.ts`.
2. `src/core/review/record.ts`: header write/parse (`<!-- specweave review: reviewer=… model=… family=… author=… depth=… repo=… head=… at=… -->`), `incrementRepoPaths` (task Files grouped by repository, `.specweave/` excluded), shared by `review.ts` and the gate. `reviewer.ts` picks by policy family and applies depth.
3. `src/cli/commands/review.ts`: policy line, `--record`, `--model`, `--head`, `--repo`.
4. `src/core/tasks/closure-gate.ts`: required-policy check per repository: matching family/model, verdict ship, after verify, `git diff --quiet <head> HEAD -- <paths>` in that repository (a squash-merged PR has the same content).

App (`repositories/anton-abyzov/specwithcode`, branch from main):
5. `packages/shared/src/reviewPolicy.ts`: the same parser and family map (no SpecWeave dependency in the app).
6. `apps/server/src/review/reviewDelegation.ts`: pure `reviewDelegationTarget` over `resolveReviewer` (author family skip, policy family filter, skip reasons); `OrchestratorMcpService.delegateTask` calls it before auto routing for review tasks; contract `review` field on the delegate result; tool description.
7. `ThreadIncrementProgress.ts` reads the newest record and the spec policy into an optional `review` field; `ThreadPlanCard.tsx` shows it beside "verify passed"; phrases in all 8 catalogs.

Risks: agents self-report the reviewer model in `--record` (the app shows its own thread model; a mismatch is visible); squash merges that also touch the reviewed files after review correctly fail the content check and need a re-review.

## Decisions

### Asked
- D-01 Where the review policy lives and who enforces it → option A, spec.md + SpecWeave closure gate, app routes and shows (coordinator brief, November 13, 2026: "set explicitly per increment in spec.md … enforced where it matters: the verify/closure gate").
### Defaulted (change any before sw-do)
- D-02 Default policy stays not-required; only `Required: yes` in a spec or `review.policy.required`/`review.crossModel` in config makes the gate strict → no change for existing increments (reversible).
- D-03 The author is the calling thread's model in the app and the ledger's finishing tool in SpecWeave → the closest data each side has.
- D-04 No cross-machine launch in this increment; the refusal text tells the coordinator to pass `machine` → follow-up.
### Open
- none

## Review
- Reviewer: openai (gpt-6.1-sol)
- Depth: deep
- Required: yes

## Tasks

### T-01 Review policy parser and resolution in SpecWeave
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/src/core/review/policy.ts, repositories/anton-abyzov/specweave/src/core/config/types.ts, repositories/anton-abyzov/specweave/tests/unit/review/policy.test.ts | Test: npx vitest run tests/unit/review/policy.test.ts

### T-02 Review records, policy-aware specweave review and --record
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/src/core/review/record.ts, repositories/anton-abyzov/specweave/src/core/review/reviewer.ts, repositories/anton-abyzov/specweave/src/core/review/brief.ts, repositories/anton-abyzov/specweave/src/cli/commands/review.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/scripts/completions/, repositories/anton-abyzov/specweave/tests/unit/review/review-policy-gate.test.ts | Test: npx vitest run tests/unit/review/review-policy-gate.test.ts tests/unit/review/review.test.ts

### T-03 Closure gate enforces a required policy per repository
- AC: AC-03 | Files: repositories/anton-abyzov/specweave/src/core/tasks/closure-gate.ts | Test: npx vitest run tests/unit/review/review-policy-gate.test.ts && npm run build && npx vitest run tests/integration/strict-close.test.ts

### T-04 Skills name the policy and the record step
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/skills/sw-review/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-done/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-increment/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-grill-me/SKILL.md, repositories/anton-abyzov/specweave/plugins/specweave/skills/, repositories/anton-abyzov/specweave/CHANGELOG.md | Test: grep -q "Required: yes" skills/sw-increment/SKILL.md && grep -q "specweave review --record" skills/sw-review/SKILL.md && grep -q "## Review" skills/sw-done/SKILL.md && grep -qi "who reviews it" skills/sw-grill-me/SKILL.md && node scripts/build/generate-skills.mjs --check

### T-05 delegate_task routes reviews to another family
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/reviewPolicy.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/reviewPolicy.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/apps/server/src/review/reviewDelegation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/reviewDelegation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpTaskRouting.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/tools.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestratorMcp.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/taskRouting.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/MachineLimitHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/unopenableFallback.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/MachineLimitHandoff.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/reviewPolicy.test.ts apps/server/src/review/reviewDelegation.test.ts apps/server/src/mcp/OrchestratorMcpTaskRouting.test.ts apps/server/src/mcp/OrchestratorMcpDelegateTask.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts apps/server/src/orchestration-v2/MachineLimitHandoff.test.ts

### T-06 Plan card shows who reviewed which commit
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/threadIncrementProgress.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgress.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/incrementReview.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/incrementReview.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadPlanCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadPlanReview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadPlanReview.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/review/incrementReview.test.ts apps/server/src/project/ThreadIncrementProgress.test.ts && cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/ThreadPlanReview.test.tsx src/i18n/i18n.test.ts

### T-07 Verify and close 1324
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1324-cross-family-review-policy
