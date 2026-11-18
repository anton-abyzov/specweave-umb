# Models by role in first-run setup: show the fitted tracks

Child of 1387. It takes over 1387's AC-04 to AC-07.

## Problem

A new install gets its model tracks silently (`packages/contracts/src/modelTracks.ts:40-58`: `daily`, `complex` and `review`, each an ordered list). First-run setup never shows which model does the everyday work, which takes the hard tasks and which reviews. On November 16 and 17, 2026 threads fell back to `muse-wonder-1.0` for regular work, and nobody could have seen that coming from setup. That fallback fault is being fixed in open PR 532 (increment 1339).

Two review rounds rejected the first design, which printed three predictions ("starts on", "reviewed by", "if a limit hits") by calling runtime functions. Those functions need a task, a tier, usage and limit state that setup does not have (`packages/shared/src/modelLanes.ts:422`, `packages/shared/src/adversarialReview.ts:274`, `packages/shared/src/providerFallback.ts:630`), so the lines could be wrong. This design predicts nothing. It shows the lists the machine will use, in order. Paths are in `repositories/anton-abyzov/specwithcode` at `origin/main` `d65dffec9`; the files cited here did not change since the first pin, `a23f3593f`.

## Scope

In: a Models block in the Agents step that shows the three tracks (everyday work, hard tasks, review) fitted to the agents that are ready, and opens the existing editor.

Out: fallback logic (PR 532, 1339). Any change to the tracks, their defaults or Settings > Models. Any line that predicts what happens at a limit beyond PR 532's own rule.

## Acceptance Criteria

- [ ] AC-01: Under each machine's agent rows a Models block shows the three tracks, named as Settings > Models names them.
  - The block and the editor in Settings read their three lists from one shared function, extracted from `apps/web/src/components/settings/ModelTracksSettings.tsx`. For the first two tracks that is `effectiveModelLanes(lanes, providers)` (`packages/shared/src/modelTracks.ts:214`) over that machine's saved lanes and its agents that are ready on the step. For Review it is the reviewer order the editor shows: the saved one, else the built-in Review track fitted to those agents (`defaultTrackSelections`, `:162`).
  - Each line lists its models in order: the first three by name, then "+{n} more". The first is marked "first".
  - The block has no rule of its own. One test asserts that, for given lanes and ready providers, the block and the editor show the same lists.
- [ ] AC-02: One sentence sits under the three lines: "A thread starts on the first model of its list and moves down it when that model runs out." It ships only after PR 532 has merged, and a test built on PR 532's exported resolver (`packages/shared/src/regularTrack.ts`) asserts, for the built-in tracks and every subset of {Claude Code, Codex, Muse Code, Gemini CLI, Copilot} being ready, that every model the resolver can return for everyday work is in the first line. If PR 532 ships a different rule, the sentence is rewritten to that rule or dropped.
- [ ] AC-03: With one model family ready, the Review line reads "No reviewer yet. A review needs a model from a second family, such as Codex or Muse Code." Its "Add one" moves focus to the first agent row that is not ready. The line never names a model of the first list's family.
- [ ] AC-04: An empty first list (no agent ready) reads "Ready once an agent is signed in." The block updates within 2 s of an agent's sign-in changing on the step.
- [ ] AC-05: "Change" opens the existing editor (`apps/web/src/components/settings/ModelTracksSettings.tsx:569`) in a dialog, inside `SettingsScopeProvider` with `singleEnvironment` and a search fixed to that machine, never a project (`apps/web/src/components/settings/SettingsScopeContext.tsx:111`), and with `sources={false}`. Saving writes what Settings > Models writes for that machine. Without Change nothing is stored.
- [ ] AC-06: The block adds no step and no gate. Passing Agents on its neutral control saves no model list (1387 AC-03), and 1387's walker passes unchanged.
- [ ] AC-07: No code before Anton accepts. The gate is the line "Accepted by Anton on <date>" in 1387's spec.
- [ ] AC-08: Strings go through `t` or `tx` with entries in de, es, fr, ja, ko, pt, ru and zh. `docs/user/welcome-wizard.md` and CHANGELOG Unreleased say what the block shows. Muse Wonder Full 1.0 at Extra High reviews the PR at its head. The PR is green, merged and released.
- [ ] AC-09: Every model in the three lists, and every provider named in the empty and one-family sentences, carries its provider's mark through `ProviderLogo` (1387 AC-44): the Claude mark for Claude models, the OpenAI mark for Codex and GPT models, the Meta mark for Muse models. The logic test returns a brand for every row, and the fixture asserts `[data-provider-logo]` with that brand in light and dark.

## Approach

One PR, after 1387's PR B (it edits `AgentsStep.tsx`, which PR B's walker attributes also touch) and after PR 532.

- `firstRunModels.logic.ts` maps the two function results to three display lines. It holds no model names and no fallback rule.
- `ModelsBlock.tsx` renders them and hosts the dialog.
- The picture beside the Agents step in 1387's prototype (work passing to review and back) stays as the illustration. Its three text lines are replaced by the three lists.

Rejected: printing what `resolveLaneRouting`, `resolveReviewer` and `describeFallbackOrder` return. They need inputs setup does not have, and two review rounds showed the output can disagree with the runtime. Rejected: a separate Models stage. Most people press nothing here.

Risk: PR 532 is open. AC-02 and the release wait for it; AC-01, AC-03, AC-04 and AC-05 do not.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: The block shows lists, not predictions.
- D-02: The track names are whatever Settings > Models shows, read from the same strings.
- D-03: It ships after PR 532, so the one sentence about running out is true.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

Rounds 1 and 2 were on 1387 before the split. Their findings on Models and the answers are in 1387's `reports/reviews/`.

## Tasks

### T-01 Acceptance, and PR 532 merged
- AC: AC-07 | Files: none | Test: grep -q "Accepted by Anton on" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/spec.md && test "$(gh pr view 532 --repo anton-abyzov/specwithcode --json state -q .state)" = MERGED

### T-02 The Models block: three lists, the empty and one-family states, Change
- AC: AC-01, AC-03, AC-04, AC-05, AC-06, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/firstRunModels.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/firstRunModels.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ModelsBlock.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ModelsBlock.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AgentsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/onboarding/firstRunModels.logic.test.ts src/components/onboarding/ModelsBlock.test.tsx src/components/settings

### T-03 The sentence about running out, proven against PR 532's resolver
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/firstRunModels.fallback.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ModelsBlock.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/onboarding/firstRunModels.fallback.test.ts

### T-04 Translations, docs, changelog, review, ship, verify and close
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/en.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/zh.ts, repositories/anton-abyzov/specwithcode/docs/user/welcome-wizard.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: specweave verify 1393-models-by-role-in-first-run-setup-show-the-fitted-tracks
