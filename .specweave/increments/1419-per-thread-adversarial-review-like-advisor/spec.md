# Per-thread adversarial review, the way Advisor works

## Problem

Anton, November 18, 2026, 6:40 PM: "Make sure that our adversarial review is fully compliant with the approach of the advisor." His screenshot shows the Advisor group in the composer's options menu: a one-line description, then "Follow project (off)", "On" and "Off".

Adversarial review has no such row. It is set only per project or machine, by "Review finished features automatically" (`adversarialReview.autoOnFeatureComplete`, off by default). A thread cannot turn review on or off for itself.

Where the two differ today (main `7b3290956`):

| | Advisor | Adversarial review |
|---|---|---|
| Project and machine setting | `advisor.enabled`, saved field by field | `adversarialReview.autoOnFeatureComplete`, the whole key overridden per project |
| Per-thread choice | `advisorMode` on the thread (`thread.advisor-mode.set`), null follows the project | none |
| Composer menu | Advisor group, description plus Follow project (on/off), On, Off | none |
| Capability flag | `advisor` | none |
| Who it applies to | any thread except an advisor child | only threads a person started that are not subagents, automated or reviews (`threadTakesAutoReview`, `runStartedByPerson`) |
| Time-cost note | the settings switch only (PR 644) | the settings switches only (PR 644) |

## Scope

In:
- the thread's own review choice: contract, command, orchestrator, projection, subagent strip, capability, client command, menu row;
- the reactor honours the choice;
- a time-cost info button on both menu groups (Advisor and Adversarial review).

Out:
- review coverage for coordinator-handed work when the thread follows the project (1418 AC-01);
- one review per increment across rounds (1418 AC-02);
- changing how the review settings key is stored (whole key compared with Advisor's field by field);
- phone apps, whose shell decoders ignore unknown fields (checked in the tolerance tests).

## Acceptance Criteria

- [x] AC-01: A thread carries `reviewMode` (`"on" | "off" | null`, absent or null follows the project), set by `thread.review-mode.set`. It is published as `thread.metadata-updated`, so older clients still read the stream, and it is stored on the thread and its shell. A subagent child does not inherit it, and a review thread or an advisor child ignores the command. The server advertises the capability `threadReviewMode`.
- [x] AC-02: The automatic review reads the finishing thread's own choice first. "Off" never starts a review. "On" starts one when the thread's increment is finished, even when the project is off, and also on a delegated thread or a run the person did not type, the same way Advisor's On works on any thread. Following the project keeps today's rules. Review threads, advisor children, archived or deleted threads, weak (`name`) bindings and the one-review-per-increment dedupe stay as they are. The 6-second recheck reads the thread, project and settings again, so Off or an archive set in that window still holds.
- [x] AC-03: The composer's options menu shows an "Adversarial review" group right after Advisor, the same way. It has a one-line description ("Has a model from another family review this thread's work when its feature is finished."), then "Follow project (on)" or "Follow project (off)", "On" and "Off". It appears where the server has the capability, and not on an advisor or review thread. The menu-only trigger opens for either group.
- [x] AC-04: Each menu group has an info button named "How much longer work takes with {group}". Hovering it shows the same measured time note as the settings switches (PR 644). Opening it neither closes the menu nor picks a choice. All new phrases are in all 8 catalogs.
- [x] AC-05: Muse Wonder Full 1.0 at Extra High reviews the PR at its head. The PR is green, merged with a merge commit and released. A headless screenshot shows the menu with both groups and an open note.

## Approach

- Contracts:
  - `ThreadReviewMode` goes in `adversarialReview.ts`;
  - `reviewMode` goes on the thread and shell schemas in `orchestrationV2.ts`;
  - the command goes in the client command union;
  - `threadReviewMode` goes in `environment.ts` capabilities.
- Shared: `threadReviewState(mode, settings)` and `ADVERSARIAL_REVIEW_TITLE_PREFIX` move into `packages/shared/src/adversarialReview.ts`. The server re-exports the prefix.
- Server:
  - `Orchestrator.ts`: same cases as `thread.advisor-mode.set`;
  - `ProjectionStore.ts`: both spreads;
  - `SubagentProjection.ts`: strip;
  - `OrchestratorScenario.ts`;
  - `ServerEnvironment.ts`: capability;
  - `AdversarialReviewReactor.ts`: the choice before the project switch, plus the gates "On" skips.
- Client runtime: `setThreadReviewMode` in `commands.ts`, and `setReviewMode` with an optimistic patch in `threadCommands.ts`.
- Web:
  - `ThreadAdvisorMenu.tsx` renders the Review group after Advisor, inside the same lazy module, so TraitsPicker's four sites and the fixture owners do not change;
  - `threadAdvisorAvailability.ts` covers either row;
  - the trigger label stays "Advisor" when only Advisor shows;
  - the info button is a small tooltip on `../ui/tooltip`, not `PolicyTooltip`, because `settingsLayout` would pull router and scope stores into the lazy chunk;
  - the advisor fixture `mocks.tsx` gets the command and capability.
- Risk: a tooltip inside a Base UI menu. If hovering closes the menu or selects a choice, fall back to a muted second line and say so.

## Decisions

### Asked
- D-01: Make review per-thread like Advisor (Anton, November 18, 2026). The coordinator's reading is the default: same place, same three choices, same description style, same storage, plus the time tooltip on each.
### Defaulted (change any before sw-do)
- D-02: The thread whose run finishes the increment decides. Its own choice wins; otherwise the project's setting applies.
- D-03: An explicit "On" works on delegated threads and on runs a person did not type, the same as Advisor's On. "Follow project" keeps today's person-only rule until 1418 AC-01.
- D-04: PR 644 (the settings-switch notes) had already merged when the menu request arrived, so this is a second PR.
- D-05: Round 1 review follow-ups left out of this increment: a delegated thread's On reviews with that thread's model as the author (1418 owns attribution of delegated work); the menu's info button is hover-only, while the same note stays focusable beside the Settings switches; the menu-only trigger keeps the name "Advisor", since the Advisor row shows wherever the review row does; a manual review start ignores Off, as it ignored the project switch.
### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

## Tasks

### T-01 Contracts, shared rule and capability
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/adversarialReview.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/adversarialReview.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/contracts/src/adversarialReview.test.ts packages/shared/src/adversarialReview.test.ts

### T-02 Server: command, projection, subagent strip and reactor
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/SubagentProjection.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/testkit/OrchestratorScenario.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/AdversarialReviewReactor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/AdversarialReviewService.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Orchestrator.reviewMode.test.ts apps/server/src/review/AdversarialReviewReactor.test.ts

### T-03 Client command and composer menu rows with the time note
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/operations/commands.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/threadCommands.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/threadAdvisorAvailability.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/advisor | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/ThreadAdvisorMenu.test.tsx src/i18n/i18n.test.ts

### T-04 Review, merge, release and the headless screenshot
- AC: AC-05 | Files: none | Test: gh pr view --repo anton-abyzov/specwithcode --json state --jq .state | grep -q MERGED
