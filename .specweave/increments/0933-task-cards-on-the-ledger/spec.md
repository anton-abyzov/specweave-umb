# 0933 Task cards on the ledger

## Problem

Measured over 20B tokens of transcripts (plan: https://claude.ai/artifact/Hto9NvYYpvDDFuGo5SwwxF), the increment files cost about 2% of tokens; the cost is context. What is missing is not cheaper documents but a readable record: the owner wants each thread to show a short checklist, one line per step in the right tense with a link to the PR, report, artifact or spec behind it, the way Claude Projects threads do. Today the ledger (specweave src/core/tasks/ledger.ts) holds only `t, e, by, at, note, evidence`; SpecWithCode's fold drops evidence on purpose (apps/server/src/mods/SpecweaveProgress.ts:225), the contract task has no link (packages/contracts/src/threadIncrementProgress.ts:34-42), StepRow renders plain text (apps/web/src/components/chat/ThreadPlanCard.tsx:57-101), and only 3 threads are bound to an increment. `specweave verify` passes with an empty command list (9 of 29 verify.json, umbrella config has no `testing.commands`). Living docs on completion produce "User Stories: 0" for every 3.0 spec yet gate the GitHub and ADO closure (LifecycleHookDispatcher.ts:190-216). The ledger is written after the fact (36% of done events under a minute after the claim; 0930 shipped PR #348 with no ledger line), which is acceptable for a receipt only if the receipt carries a link.

## Scope

In: two optional ledger keys (`line`, `link`), fold-time card state with link derivation, `specweave card` commands and `cards --md`, pickup printing the checklist, verify refusing an empty command list, branch-keyed cards for spec-less work, living docs decoupled from the GitHub/ADO closure for specs without user stories, the SpecWithCode contract, fold and StepRow link, binding by branch, a shared fold fixture, backfill of 0930 and 0931. Out: a new store, renaming task ids, any change to spec.md format, work on ChatView.tsx.

## Acceptance Criteria

- [ ] AC-01: A ledger event may carry `line` (max 100 chars) and `link`; `formatLedgerLine` and `parseLedger` keep them, older lines without them still parse, and an unknown key is still ignored.
- [ ] AC-02: `foldLedger` exposes per task `card: { state: todo|doing|waiting|done|skipped, line, link }` where line falls back to the task title and link falls back to a PR URL, `log:` path or `HEAD <sha>` found in the evidence, in that order.
- [ ] AC-03: `specweave task claim|done|block` accept `--line` and `--link`; `specweave card add|start|done|wait|list` exist as thin aliases; `specweave cards --md` prints a header line, a blank line, then one `✓ / ✱ / ○ text (link)` line per card in ledger order.
- [ ] AC-04: `specweave pickup` prints the card checklist before the next task; the latest notes follow it.
- [ ] AC-05: `specweave verify` exits 1 with "no test commands configured" when the command list is empty, unless `--reason` is given; the umbrella `.specweave/config.json` has `testing.commands` from its Commands table.
- [ ] AC-06: `specweave card add "<text>"` on a branch with no bound increment appends to `.specweave/cards/<branch-slug>.jsonl` with ids `C-NN`; `specweave complete` refuses an increment whose spec.md has no ACs unless `--reason` is given.
- [ ] AC-07: `onIncrementDone` runs the GitHub and ADO closure even when living docs sync is skipped; living docs sync is skipped with one log line when the spec has no user stories.
- [ ] AC-08: SpecWithCode `ThreadIncrementTask` carries `line` and `link` (https URLs, or paths inside the increment directory after realpath), the server fold fills them, StepRow renders the line as a link, done rows read in the past tense and the current row is emphasised; a done row without a link shows "unverified".
- [ ] AC-09: A thread whose worktree branch matches an increment's `inc/NNNN` branch or whose ledger names the branch is bound to it without a claim file.
- [ ] AC-10: One JSON fixture of ledger lines and expected cards is run by specweave's ledger tests and by SpecWithCode's SpecweaveProgress tests.
- [ ] AC-11: 0930 and 0931 have ledger lines whose cards link PR #348 and PR #2081.

## Approach

specweave first (worktree off develop, one PR), SpecWithCode second (worktree off main, one PR), fixture shared by path `repositories/anton-abyzov/specweave/tests/fixtures/cards/fold-fixture.json` and copied into the Studio repo by a test that fails when the copies differ. In specweave: `LedgerEvent` gains the two optional fields; `deriveLink(evidence)` lives next to `foldLedger`; `card.ts` is under 300 lines and calls into task.ts; `pickup.ts describeFocus` prints `renderChecklist(cards)` first. Studio: contract, `SpecweaveProgress.ts` sanitises links (https github.com, claude.ai, or realpath inside the increment dir), `ThreadIncrementProgress.ts` passes them through, `threadPlanProgress.ts` maps `line ?? title` and `href`, StepRow renders an anchor using the existing onOpenPath for paths. Rejected: a new event type (older CLIs reject unknown `e`); a cards store outside the ledger (two sources of truth). Risk: tense derivation from English titles is unreliable, so the CLI never rewrites titles; agents write `--line` or get the title as is.

## Decisions

- D-01 Spec-less cards live in a branch-keyed file, not in a numbered increment (numbering churn; the branch is the one key every tool shares).
- D-02 `card done` does not call `gh pr view`; agents pass `--link`, and the fold derives one from evidence otherwise.
- D-03 Living docs stay available for specs with user stories; they are skipped, not removed, for 3.0 specs.

## Open questions

- none

## Tasks

### T-01 Ledger fields and card fold
- AC: AC-01, AC-02, AC-10 | Files: repositories/anton-abyzov/specweave/src/core/tasks/ledger.ts, repositories/anton-abyzov/specweave/src/core/tasks/cards.ts, repositories/anton-abyzov/specweave/tests/fixtures/cards/fold-fixture.json, repositories/anton-abyzov/specweave/tests/unit/core/tasks/cards.test.ts, repositories/anton-abyzov/specweave/tests/unit/core/tasks/ledger.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/tasks/cards.test.ts tests/unit/core/tasks/ledger.test.ts

### T-02 card commands, task flags, cards --md, pickup
- AC: AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specweave/src/cli/commands/task.ts, repositories/anton-abyzov/specweave/src/cli/commands/card.ts, repositories/anton-abyzov/specweave/src/core/session/pickup.ts, repositories/anton-abyzov/specweave/src/core/tasks/branch-cards.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/tests/unit/cli/commands/card.test.ts, repositories/anton-abyzov/specweave/tests/unit/core/session/pickup.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/cli/commands/card.test.ts tests/unit/core/session/pickup.test.ts

### T-03 verify and complete gates, living docs decoupled
- AC: AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specweave/src/core/tasks/verify-runner.ts, repositories/anton-abyzov/specweave/src/cli/commands/status-commands.ts, repositories/anton-abyzov/specweave/src/core/lifecycle/LifecycleHookDispatcher.ts, repositories/anton-abyzov/specweave/tests/unit/core/tasks/verify-runner.test.ts, repositories/anton-abyzov/specweave/tests/unit/core/lifecycle/LifecycleHookDispatcher.test.ts, .specweave/config.json | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/tasks/verify-runner.test.ts tests/unit/core/lifecycle/LifecycleHookDispatcher.test.ts

### T-04 Skills and docs for cards
- AC: AC-03 | Files: repositories/anton-abyzov/specweave/skills/sw-do/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-handoff/SKILL.md, repositories/anton-abyzov/specweave/src/cli/helpers/init/instruction-file-writer.ts, repositories/anton-abyzov/specweave/docs-site/docs/, repositories/anton-abyzov/specweave/CHANGELOG.md | Test: cd repositories/anton-abyzov/specweave && npm run lint:standalone-skills && npm run lint:docs-refs

### T-05 SpecWithCode contract, fold and card links
- AC: AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specweave-studio/packages/contracts/src/threadIncrementProgress.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mods/SpecweaveProgress.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ThreadIncrementProgress.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/studio-thread-binding.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/studio/threadPlanProgress.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ThreadPlanCard.tsx, repositories/anton-abyzov/specweave-studio/apps/server/src/mods/__tests__/SpecweaveProgress.cards.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/studio/threadPlanProgress.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && npx vitest run apps/server/src/mods/__tests__/SpecweaveProgress.cards.test.ts apps/web/src/studio/threadPlanProgress.test.ts

### T-06 Backfill 0930 and 0931
- AC: AC-11 | Files: .specweave/increments/0930-computer-use-permission-guidance/ledger.jsonl, .specweave/increments/0931-weave-design-system-across-the-three-sites/ledger.jsonl | Test: specweave cards 0930 --md | grep -q 'pull/348' && specweave cards 0931 --md | grep -q 'pull/2081'
