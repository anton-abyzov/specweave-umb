# One review per finished feature, by another model family

Child of 1387. Split from 1398 on November 18, 2026, when Anton chose to deliver the first feature guide as designed (1398 D-11). Planned, not started. It does not gate the guide.

## Problem

Two rounds of hand runs for 1398 (`reports/e2e-run.md` and `reports/e2e-run-variant.md` in that increment) showed that a finished feature is reviewed, but not once and not always by another model family.

- **Two or three reviews for one feature.** With one request for the whole feature, the three runs recorded 2, 3 and 2 reviews. A review that said ship with findings made the worker add a task and ask for a second round. In two runs the coordinator then started another review or a "delivery verification" after the worker had closed.
- **A review by the builder's own family can close a feature.** `specweave review`'s default OpenAI reviewer runs `codex exec -m gpt-6.1-sol` (`repositories/anton-abyzov/specweave/src/core/review/reviewer.ts`). In one run Codex refused it ("The 'gpt-6.1-sol' model is not supported when using Codex with a ChatGPT account."), the worker fell back to a Claude reviewer for Claude-built work, and the increment closed, because an agent-written spec has no `## Review` section.
- **The automatic review misses work the coordinator hands out**, except when a message the person typed to the coordinator finishes after every task is done. Then it reviews the coordinator thread, and with the card's "Verify, review and close" request that makes two reviews.
- **The Board says little about reviews.** The open Done card names one reviewer even when several reviews are recorded, links no review thread, and its face says nothing about a review. A review thread is not linked to its increment.
- **A Planned card cannot be started from the card** when its planning thread is still linked, and the card's Start request covers only the first task.
- **A skipped automatic review is only logged**, and removing a project leaves its review override in settings.

## Scope

In: the review trigger for coordinator-launched work, one review per increment, the reviewer fallback in the CLI, what the Board shows about reviews, Start on a Planned card, the override left behind by a removed project.

Out: the first feature guide (1398), which ships first and reads whatever reviews were recorded. The default of "Review finished features", which stays off.

## Acceptance Criteria

- [ ] AC-01: The automatic review also covers work the coordinator hands out (1398 D-01, decided A). The text of 1398 AC-07 applies: a new predicate `runTakesAutoReview`, a `senderRunId` stamp on launches, a walk of at most 4 hops that ends at a person, `reviewOf: {threadId, incrementId}` on review threads, and the tests listed there.
- [ ] AC-02: One review per finished increment. When a ship verdict by another model family is already recorded for the increment at its current content, neither the automatic review, the closer nor the coordinator starts another. A review that asked for fixes may be followed by one more round on the fixed content, and the card shows it as the same review's second round.
- [ ] AC-03: `specweave review` never substitutes the author's own family silently. When the default reviewer of another family cannot run, the command names the reason, tries the next family in the configured order, and ends with a clear refusal when none can. The refusal of `gpt-6.1-sol` on a ChatGPT sign-in is reproduced first, and the report says whether it affects every ChatGPT sign-in or only an account at its limit.
- [ ] AC-04: A skipped review is said, not only logged (the text of 1398 AC-08).
- [ ] AC-05: The Board knows about reviews (1398 AC-09 and AC-10, rewritten for recorded reviews). The Done card lists every recorded review with model, family, verdict and a link to its thread when one exists, and a card whose review is finished asks only "Verify and close".
- [ ] AC-06: A Planned card offers Start even when its planning thread is linked, and Start asks for every task, not the first one.
- [ ] AC-07: Removing a project removes its entry in `projectSettingsOverrides`.
- [ ] AC-08: Muse Wonder Full 1.0 at Extra High reviews each PR at its head. Each PR is green, merged and released.

## Approach

Written when the increment starts. The server part follows 1398's old T-03 (`AdversarialReviewReactor.ts`, `AdversarialReviewService.ts`, `OrchestratorMcpService.ts`, `ProjectBoard.ts`). The CLI part is in `repositories/anton-abyzov/specweave/src/core/review/`.

## Decisions

### Asked
- D-01: the automatic review for coordinator work was decided A by Anton on November 18, 2026 (1398 D-01).
### Defaulted (change any before sw-do)
- D-02: a second review round after fixes counts as the same review.
### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

## Tasks

### T-01 Plan: turn the criteria into tasks with files and tests
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: grep -q "^### T-02" .specweave/increments/1418-one-review-per-finished-feature-by-another-model-family/spec.md
