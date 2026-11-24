# First feature walkthrough: turn SpecWeave on, ask for a feature, watch the Board, review, Done

Child of 1387. Added on November 18, 2026 at Anton's request. It is the sixth increment under 1387's one acceptance.

## Problem

Setup ends and the product's main loop is never shown: a plan, a card on the Board, the work, a review by another model, Done. Anton: "one of the onboarding tasks should also be mentioned ... it's also important to enable this review after the work is done ... click through a test project or whatever so that he understands. It should be in a logical order."

"Review finished features" is off by default and sits in Settings > Models > Review (`apps/web/src/components/settings/ModelTracksSettings.tsx:657`, `packages/contracts/src/adversarialReview.ts:64`). Off means nothing reviews a feature automatically. It is set per machine and each project can override it.

A walkthrough that simply narrated the six steps would not be true today. App paths are in `repositories/anton-abyzov/specwithcode` at `origin/main` `d65dffec9` (1386, 1392 and 1391 are merged there). The CLI checks were run with `specweave` 3.1.21 in `~/.specwithcode/m4/scratch/2026-11-18-first-feature-close/`.

- **The automatic review never runs for work the coordinator hands to a worker.** It needs a run whose prompt a person sent (`runStartedByPerson`, `apps/server/src/orchestration-v2/PromptSuggestionReactor.ts:83-87`, checked at `apps/server/src/review/AdversarialReviewReactor.ts:134`). Every launch by `delegate_task`, `create_threads` or `studio_thread_launch` sends the coordinator's `senderThreadId` (`apps/server/src/mcp/OrchestratorMcpService.ts:4511`, `:4773`), so that run never qualifies, even when the thread itself would pass the thread test (`PromptSuggestionReactor.ts:71-80`). Asking the coordinator is how most work starts, so today the switch does nothing for it.
- **With one model family ready there is no reviewer**, and the only trace is a log line (`AdversarialReviewReactor.ts:116`).
- **A new increment starts as `active`.** Its card appears in Active, never in Planned, unless it was created with `--planned` (checked with the CLI).
- **Nothing moves a card to Done by itself.** All tasks done puts it in In review (`apps/server/src/project/ProjectBoard.ts:266-285`). Done needs the increment closed, which today is the card's "Review and close" request (`apps/web/src/studio/projectBoardModel.ts:308-309`).
- **Closing fails in a bare project.** `specweave verify` stops with "no test commands configured" when the project has no test command. With `"test": "node --test"` in `package.json` it passes and `specweave complete` closes the increment (both reproduced).
- **A review thread is not linked to its increment** (`docs/studio/adversarial-review.md`), so nothing on the Board says a review ran. It is known as a review thread only by its title prefix (`apps/server/src/review/AdversarialReviewService.ts:51`).
- **The automatic review writes nothing into the increment.** `apps/server/src/review/incrementReview.ts` only reads recorded reviews, and the launch (`AdversarialReviewService.ts:212`) writes no report. A plan whose spec requires a review still needs a recorded one to close (`src/core/tasks/closure-gate.ts:119`, `:165` in the CLI).
- **The built-in Review list does not start with Muse Wonder Full yet.** At `d65dffec9` its first entry is `muse-wonder-1.0` at Extra High (`packages/contracts/src/modelTracks.ts:53`). PR 532 (increment 1339, open) changes it to `muse-wonder-full-1.0` at Extra High, Anton's rule of November 17, 2026. And the first entry is not always the reviewer: a model of the author's family is skipped (`packages/shared/src/adversarialReview.ts:319`).

## Scope

In: a guide of six steps, done by hand in a sample project the app makes; the changes that make each step true; where the guide is offered; its motion.

Out: the default of "Review finished features" for real projects, which stays off (D-02). SpecWeave setup and the Board's off state (1392, 1396). The Board's cards and groups (1391). The Models block and the review list editor (1393). Any fake or simulated agent in the product: the guide uses the person's own agents.

## Acceptance Criteria

### A. The sample project

- [ ] AC-01: "Try a first feature" makes a sample project through `projects.createNew` with a new optional `sample: "first-feature"`. It is a Git repository with a first commit, named "First feature" (numbered when taken), holding one page (`index.html`, `style.css`), a `package.json` whose `test` script is `node --test`, one passing test, and a README. It is created with SpecWeave off. That is the one exception to 1396 D-02, because turning SpecWeave on is the guide's first step. A server says it can with `firstFeatureSample: true` in `serverConfig`, beside `specweaveSetUp` (`packages/contracts/src/server.ts:876`). Without that key the client shows no offer and never sends `sample`. The project record keeps `sample: "first-feature"`, which no person can set (AC-12).
- [ ] AC-02: The offer says what it costs before the press: "About 10 minutes. Your agents build one small feature and another model reviews it, on your own plans." With no agent ready it reads "Sign in an agent first" and opens Settings > Providers.

### B. The guide

- [ ] AC-03: The sample project's window shows the guide: six knots on one thread (the stage bar of 1387), the current step's one sentence and one action, and "Leave the guide". It is not modal and blocks nothing. Left, it comes back from the project's menu. Only two things are stored, on the server in the project record: `firstFeatureGuide.started` and `firstFeatureGuide.ended` (`left` or `finished`). They travel in the project payload the window already reads, next to the SpecWeave state of 1396 AC-12, so another device shows the same guide. Everything else is read from live state.
- [ ] AC-04: A step is done when the app sees it, never because the guide was pressed. In order:
  1. **Turn SpecWeave on.** "This project has no plans or board yet. Turn SpecWeave on." The action "Show me" opens the Board tab and rings its "Set up SpecWeave" button (1396 AC-11). Done when the project's state is `on` (1396 AC-01).
  2. **Ask for a small feature.** "Ask for a small feature. A plan comes back as a card." The action "Write it for me" puts this in the coordinator's composer through `onAsk`, and the person presses Send: "Plan a dark mode switch for this page as a planned increment with no Review section, then stop and tell me." Done when the Board has a card.
  3. **Watch it start.** While the card is in Planned: "Read the plan, then press Start on its card." Done when the card is in Active or further.
  4. **Turn on review.** "While it works, turn on review of finished features." The step holds the real switch, writing this project's override, and the line "Reviewer: {model}". The model is what `resolveReviewer` (`packages/shared/src/adversarialReview.ts`) returns for this project with the working thread's model as the author, so it is the first ready model of another family than the one doing the work, never simply the first entry. Before a worker exists the author is the first entry of the Daily list. When it returns none, the step shows the no-reviewer state of AC-06. "Change" opens 1393's editor. Done when the setting resolves to on for this project.
  5. **See the review.** "When every task is done, a model from another family reviews the work in its own thread." The automatic review starts only when a run of a thread bound to the increment by claim, link or branch (`AdversarialReviewReactor.ts:53`) completes with every task done (`:61`), and review is on at that moment. While tasks are open the step reads "Waiting for the work to finish: {done} of {total} tasks." Once a review thread exists (AC-09) the action is "Open the review". If every task is done and no review exists after 2 minutes, the step offers "Review it now" (AC-06). Done when a review of this increment has finished, whether it started by itself or by hand.
  6. **Done.** "Read the review, then press Review and close on the card." Done when the card is in Done.
- [ ] AC-05: The end. After step 6 the guide reads "That is the loop: plan, board, work, review, done." with two actions: "Review finished features in all projects on this Mac", which turns the machine's switch on and says that each review uses the reviewer's plan, and "Remove the sample project", which removes it from SpecWithCode and leaves the folder on disk. Neither is pre-selected.
- [ ] AC-06: Nothing in the guide can strand a person.
  - Steps complete in any order. A step whose state goes back is current again.
  - If the worker builds without waiting (the card appears in Active), step 3 completes at once.
  - If the work finishes before review was turned on, nothing starts by itself, because the trigger is a run completing (`AdversarialReviewReactor.ts:171`). Step 5 then offers "Review it now" at once, which starts the existing by-hand adversarial review of the working thread. That review sets the card's `review` like an automatic one (AC-09), so step 5 completes on this path too.
  - If the working thread is not bound to the increment, the automatic review cannot find it. Step 5 says so in one line and offers "Review it now".
  - With no model from a second family, step 4 reads "No reviewer yet. A review needs a model from a second family, such as Codex or Muse Code." with "Add one" (Settings > Providers) and "Go on without a review", which marks steps 4 and 5 as skipped.
  - A failed setup, a missing Node.js and a limit show the states of 1396 AC-05 and the thread's own message. The guide then says "Waiting on this step" and names where to look.
  - Every step has "Skip this step". A skipped knot is drawn hollow with a dash, not as done.

### C. What has to change so the steps are true

- [ ] AC-07: The automatic review also covers work the coordinator hands out (D-01).
  - One new predicate, `runTakesAutoReview`, lives in `AdversarialReviewReactor.ts`. `threadTakesPromptSuggestions` and `runStartedByPerson` in `PromptSuggestionReactor.ts` are not edited, and a test asserts prompt suggestions fire for exactly the runs they fire for today.
  - A run qualifies as today, or when its launch chain ends at a person. The launch tools stamp a new optional `senderRunId` beside `senderThreadId` (`OrchestratorMcpService.ts:4511`, `:4773`). The walk goes from the finished run's first message to the sending thread and that run, at most 4 hops, and stops on a thread it has seen. It qualifies only when every thread in the chain is in the same project, has no `origin` and is not a review thread, and the last run passes `runStartedByPerson` (no `scheduledTaskId`, no `senderThreadId`). A message without `senderRunId`, a run that cannot be read and a fifth hop all mean no review.
  - A review thread is known by a stored mark, not by its title. The review launch writes `reviewOf: {threadId, incrementId}` on the thread it creates, and `isAdversarialReviewThread` (`AdversarialReviewService.ts:51`) reads the mark first and the title prefix only for threads made before this change. A renamed review thread never starts a review.
  - It stays one review per increment (`autoReviewCommandId`, `AdversarialReviewReactor.ts:87`).
  - Tests: a person's thread reviews as today; a coordinator's worker reviews; routine, then coordinator, then worker does not; a worker launched from another project's coordinator does not; a renamed review thread does not; a chain of five hops does not; two workers that finish one increment start one review; prompt suggestions are unchanged.
- [ ] AC-08: A skipped review is said, not only logged. When the automatic review finds no reviewer, the thread that finished gets one line, "No automatic review: no model from another family is ready.", with the reason for each model tried, the wording the by-hand path already uses. It is said once per increment.
- [ ] AC-09: The Board knows a review ran. A card in `projects.board` gains an optional `review: {threadId, state}` with `state` `running` or `finished`. It is set from the newest thread whose `reviewOf.incrementId` (AC-07) is this increment, so an automatic review and a by-hand one count alike, and `state` is that thread's latest run. `ProjectBoard.ts` gets the list of review threads as an input and stays a pure function. Clients that do not know it ignore it. The guide's steps 5 and 6 read it. The card's own look is 1391's and is not changed here.
- [ ] AC-10: One review per feature in the guide, by a stated route.
  - The guide's request asks for a plan "with no Review section" (AC-04 step 2). A fresh project's default asks for none (reproduced: `specweave complete` closes with a warning only).
  - For a card whose `review.state` is `finished`, the card's request reads "Verify and close increment NNNN. Its review is in the thread {title}." in place of "Verify, review and close increment NNNN." (`projectBoardModel.ts:309`). No second review is asked for.
  - If the agent's spec carries a required review anyway, closing stops on the CLI's own message. Step 6 then shows it under "Waiting on this step" with "Skip this step". T-02 records which policy each of the three specs carried, and one required review in three runs is a stop under AC-15.

### D. Where it is offered

- [ ] AC-11: Never a stage of first-run setup, and nothing in setup changes. The Overview page shows one card, "Build a first feature", until it is done or dismissed, and the command palette has "First feature guide". 1387's walker and its fixture are not changed here. This increment's fixture shows the Overview with the card and asserts the card's title and its one action.
- [ ] AC-12: One sample project per machine at a time. "The sample" is a project on this machine whose record has `sample: "first-feature"` and whose guide has not ended. While one exists the offer reads "Continue your first feature" and opens it. Renaming it changes nothing. Removing it from SpecWithCode ends it: its folder stays, its threads go the way any removed project's threads go, and the offer is back. After the guide finished, the offer is gone for good, and "First feature guide" in the command palette can still make a new sample.

### E. Motion and reference

- [ ] AC-13: The guide moves inside 1387's motion system (its AC-32 to AC-34): CSS only, no new dependency. A knot ties when its step is done, the thread draws taut to the next knot, and the sentence follows 40 ms later. "Show me" rings its target twice and stops. Nothing loops, and with reduced motion every state is immediate.
- [ ] AC-14: `reports/onboarding-prototype.html` in 1387 (scene "First feature") is the reference for the guide's layout, wording and motion, including the states "No reviewer yet", "Review it now", "Skip this step" and "Leave the guide". The scene runs on timers; the order of events it shows is the app's: a review starts when the work finishes with review on, or from "Review it now", never from the switch alone. `reports/first-feature-loop.mp4` here is a short film of the loop for the docs and the site. Its generated artwork is used in that film only and is not shipped in the app.

### Gate, review, shipping

- [ ] AC-15: Proof first, with a kill rule. Before any code, the six steps are run three times by hand on M4 in a scratch copy of the sample project, with today's app, real agents and the by-hand review, and recorded in `reports/e2e-run.md`: minutes per step, what each run cost, where the agent left the script, and the answer to AC-10. If the median run is over 15 minutes, or any run needs a fix outside the six steps, or any agent-written spec required a review (AC-10), the hands-on guide does not ship as written: the result goes to Anton with a shorter variant. These runs cannot test AC-07, which does not exist yet. After the server PR merges, one more run on M4 with the automatic trigger is added to `reports/e2e-run.md` before the web PR merges, and T-10's run on M5 repeats it on the release. Lifted by Anton on November 18, 2026 (D-11): replaced by AC-25.
- [ ] AC-19: The three-step variant (D-10), proven before any code. It replaces the six steps of AC-04 and the proof of AC-15. AC-02, AC-03, AC-04, AC-06, AC-09, AC-10 and T-03 to T-10 are rewritten for it only after a "go" here, from what the runs show.
  - The steps. 1. **Turn SpecWeave on**, as in AC-04 step 1. 2. **Ask for it whole.** The person sends one request to the coordinator: "Build a dark mode switch for this page as a new increment with no Review section: plan it, do every task, then verify, review and close it." Nothing else is typed or pressed until the card is in Done. 3. **Read the review.** The person opens the one review of the feature.
  - The sample project has automatic review off for itself (a project override), so the only review is the one the request asks for.
  - The proof. The three steps are run three times by hand on M4 with today's app and real agents, each in a fresh throwaway project like T-02's, and recorded in `reports/e2e-run-variant.md`. `reports/e2e-run.md` is not edited.
  - The clock. Two times are stamped per run: the first press of step 1, and Send. The run ends when the card is in Done and one review has finished. The total is first press to that end; Send to that end is recorded beside it.
  - The machine. Before each run the 1-minute load average and `specweave-studio doctor`'s time to start an agent turn are recorded. A run starts only when the load is under 32 (two per core), waiting up to 20 minutes for that; a run started above it is marked "loaded". The report says "M4 at load N" and calls the machine quiet only for runs that met the number.
  - Per run the report names: the models that planned, built and reviewed; how the review was started and whether it is recorded in the increment; the review's thread; what the card shows in each column; plan usage before and after.
  - Go needs all of: a median total of 15:00 or less; no run over a 30-minute cap; no message typed and no button pressed between Send and Done in any run; exactly one finished review per run, by a model from another family than the builder's; the card in Done in every run. Anything else is a stop, and a second stop goes back to Anton with option C of D-10.
  - With only one model family ready no review can run, so the request must change. The runs do not test that; it is written when AC-06 is rewritten.
  - T-11 said stop on November 18, 2026. Anton lifted the go rule the same day (D-11): the three steps are built as written here, and section F holds their criteria.
- [ ] AC-16: No code before Anton accepts. The gate is the line "Accepted by Anton on <date>" in 1387's spec, with D-01 and D-02 answered here.
- [ ] AC-17: Strings go through `t` or `tx` with entries in de, es, fr, ja, ko, pt, ru and zh. `docs/user/` gains "Your first feature", and `docs/studio/adversarial-review.md` says what AC-07 changed. CHANGELOG Unreleased has the entries. Muse Wonder Full 1.0 at Extra High, with full access, reviews each PR at its head. Each PR is green, merged and released, and the guide is then run once on M5.
- [ ] AC-18: The reviewer named at step 4, the review thread's line under the card, and the providers named in the no-reviewer sentence carry their marks through `ProviderLogo` (1387 AC-44). The mark follows the reviewer the app really picked, so it changes with the name. The fixture asserts the reviewer's brand by `[data-provider-logo]` in light and dark. Under section F the reviewers are the ones listed at step 3.

### F. The three-step guide as delivered (D-11)

These replace AC-02, the six knots of AC-03, AC-04, AC-06, the knot count of AC-13, the scene of AC-14, and the gates of AC-15 and AC-19. AC-07 to AC-10 moved to increment 1418. AC-01, AC-05, AC-11, AC-12, AC-16, AC-17 and AC-18 stand, read with three steps.

- [ ] AC-20: The offer names no time, because no time was measured on a quiet Mac: "Your agents plan and build one small feature and another model reviews it, on your own plans." With no agent ready it reads "Sign in an agent first" and opens Settings > Providers.
- [ ] AC-21: The sample project is created with its own "Review finished features automatically" set to off (a project override), so the only reviews are the ones the request asks for. Removing the sample removes that override.
  - Added November 18, 2026, found while building the server side: AC-05 lets a person remove the finished sample, and a removed project is sent to no client, so the window could not know the guide was ever finished and AC-12's "gone for good" would be lost. The server therefore says `firstFeatureFinished: true` in `serverConfig`, beside `firstFeatureSample`, when any project record on this machine, removed ones included, has `sample: "first-feature"` and a guide that ended `finished`. The offer reads that key. The command palette entry stays.
  - Known limit, accepted in review (November 18, 2026): the key is read when a window loads its config. Windows that share storage with the one that finished learn it at once through its finished-here flag. A window on another origin or browser profile can show the offer again until it reloads, and pressing it there makes a new sample.
- [ ] AC-22: The guide has three knots on one thread, the current step's one sentence and one action, and "Leave the guide". It is not modal. What is stored is AC-03's two facts; everything else is read from live state. A step is done when the app sees it:
  1. **Turn SpecWeave on.** As AC-04 step 1: "Show me" opens the Board tab and rings "Set up SpecWeave" (1396 AC-11). Done when the project's state is `on`.
  2. **Ask for it whole.** "Ask for the whole feature in one request. Your agents plan it, build it, review it and close it." "Write it for me" puts this in the coordinator's composer through `onAsk`, and the person presses Send: "Build a dark mode switch for this page as a new increment with no Review section: plan it, do every task, then verify, review and close it." While it runs the step reads the card's place from `projects.board`: "Planning", "Working: {done} of {total} tasks", "In review", and "Fixing what the review found" when the card goes from In review back to Active. It always offers "Open the thread". Done when the card is in Done.
  3. **Read the review.** "Open the review" opens the Done card. The step lists every recorded review of the increment with the reviewer's name, its mark and the verdict, newest first. A card in `projects.board` gains an optional `reviews: [{model, family, author, verdict, at}]`, read from the increment's recorded reviews; clients that do not know it ignore it. When no listed review is by another family than its author's, the step says so in one line: "Reviewed by {model}, the same family that built it." Done when the person opens the card from this step.
- [ ] AC-23: Nothing in the guide can strand a person.
  - Steps complete in any order, and a step whose state goes back is current again.
  - With no model of a second family ready, "Write it for me" writes the request ending "then verify and close it." and step 3 reads "No review ran. A review needs a model from a second family, such as Codex or Muse Code." with "Add one" (Settings > Providers).
  - A failed setup, a missing Node.js and a limit show the states of 1396 AC-05 and the thread's own message. The guide then says "Waiting on this step" and names where to look.
  - Every step has "Skip this step". A skipped knot is drawn hollow with a dash, not as done.
- [ ] AC-24: Motion is AC-13's with three knots. The scene "First feature" in 1387's `reports/onboarding-prototype.html` is updated to the three steps and stays the reference for layout, wording and motion.
- [ ] AC-25: The gate is code, not a timed proof. Unit tests cover the step logic, the fixture shows every state in light and dark, and an end-to-end run with the fake agent goes from the offer to a sample project, through the three steps, to a card in Done whose recorded review step 3 lists. Muse Wonder Full 1.0 at Extra High reviews each PR at its head. After the release one real run on M4 is recorded in `reports/e2e-run-released.md` with its times and reviews, for Anton's own review. It has no kill rule.

## Approach

### Why hands-on, and why these six steps

Anton asked for a real click-through in a test project, in the order plan, board, work, review, done. A film or a fake run would teach the names and not the presses. The guide therefore watches real state: it has no state machine of its own that could disagree with the app.

The order differs from Anton's list in one detail. The request asks for a plan as a planned increment and stops, so the card is first seen in Planned and the person starts it from the card. Without that the card would appear in Active at once and "watch it move" would have nothing to show. If the agent builds anyway, the guide goes on (AC-06).

### Order of work

1. T-02, the proof by hand. It can stop the increment.
   - It said stop on November 18, 2026. T-11 is the next gate: the three-step variant, timed three times. T-03 to T-10 are re-cut for the variant after a go, and none starts before that.
2. Server PR (T-03, T-04): the review trigger, the skipped-review line, the `review` field, the sample scaffold, the guide's two stored facts.
3. Web PR (T-05 to T-07): the guide, the offer, the motion and its checks.
4. T-08 to T-10: the end-to-end test, text, review, the run on M5, close.

1392 and 1391 are merged (`d65dffec9`). It lands after 1396 and 1393, and its reviewer line is right for Anton's rule only after PR 532: step 1 uses 1396's Board state and setup, step 3 and step 6 use 1391's card actions, step 4 uses 1393's review list and editor.

### Rejected

- A stage in first-run setup. Setup stays four stages, and this takes ten minutes and real usage.
- A simulated run with a fake agent. It would look right and teach nothing about waiting, limits or reading a review.
- Turning review on for the whole machine at step 4. It spends another plan's usage in every project. The person is offered it at the end, in words.
- Sample project with SpecWeave already on. Step 1 would be a picture, not a press.
- Telling people to type in a plain thread so today's trigger fires. The coordinator is where the product tells them to ask.

### Risks

- AC-07 changes when reviews start, for everyone who has the switch on. It is opt-in per machine or project, once per increment, and asked as D-01.
- The run depends on agents following a request ("plan it as planned, then stop"). AC-15 measures that before anything is built, and AC-06 covers the agent that does not.
- 1396 and 1393 must land first, and PR 532 for the reviewer default. The guide's server PR does not depend on them and can go earlier.
- The film is a reference. If it and the built guide disagree, the prototype wins.

## Decisions

### Asked
- D-01, for Anton: should the automatic review also run for work the coordinator hands to a worker? Recommended **A. Yes.** Today "Review finished features" only works when you type in the working thread yourself, so it misses most work, and the guide's step 5 would never happen. B. Leave the trigger as it is and have the guide ask in a plain thread. A costs one more review run per finished increment in every project that has the switch on, on the reviewer's plan, on top of any recorded `specweave review` that project's plans already require. **Decided November 18, 2026: A.** Under D-10 the guide no longer depends on this, and with it on the closer's review would make two. It stays decided and is built off the guide's path, in increment 1418.
- D-02, for Anton: what the guide's switch turns on. Recommended **A. The sample project only, and the last screen offers one press for all projects on this Mac.** B. The whole machine at step 4. **Decided November 18, 2026: A.** Changed by D-10: the guide has no switch step, and the sample project turns automatic review off for itself so that one review runs, the one the request asks for. What is left of A is the end screen's offer, "Review finished features in all projects on this Mac". Anton was told this on November 18, 2026 and can object before any screen is built.
- D-10, for Anton, asked November 18, 2026: T-02 ended in "stop" (`reports/e2e-run.md`). The three runs on M4 took 21:08, over 60:00 and 23:02, so the median is 23:02 against the 15-minute rule, and every run needed a fix outside the six steps. By AC-15 the guide does not ship as written, and T-03 to T-10 do not start until this is answered. Recommended **A. The three-step variant: turn SpecWeave on, ask for the feature whole in one request, read the one review. It is timed three times on a quiet Mac before any web code, and the offer names no time until one is measured.** B. Keep six steps and first fix what broke them: Start on a Planned card, a Start request that covers every task, and a way to start the review by hand. C. Drop the guide and keep only those fixes. **Decided November 18, 2026: A.** His words: "1. Do what is recommended. yes".
  - What the runs showed against this spec: the automatic review already runs for coordinator work when the person's next message to the coordinator finishes after every task is done, so the Problem's "never runs" is too strong and D-01, AC-07 and AC-10 need rewriting for one review, not two. A Planned card whose planning thread is linked offers "Open thread" and no Start, so D-06 cannot be done as written. "About 10 minutes" (AC-02) is not supported.
- D-11, for Anton, asked November 18, 2026: T-11 ended in "stop" (`reports/e2e-run-variant.md`), the second stop, so by AC-19 it comes back to him. One request reached Done with nothing typed in all three runs (4:40, 21:04 and 12:44 from the first press), but no run had exactly one review: 2, 3 and 2 were recorded. Run 1 closed on a same-family review after the Codex reviewer was refused, and its review by another family finished at 28:08, so the median is 12:44 only if that first review counts and 21:04 if it does not. Runs 2 and 3 started at 5-minute loads of 134 and 208. A. Drop the guide and ship the fixes the two rounds found (option C of D-10, the rule as accepted). Recommended **B. A light version, which changes that rule: "Try a first feature" makes the sample project and puts the one request in the composer, ready to send. No step tracker, no time named, no "one review" promise. The same fixes ship with it.** C. Ship the fixes, then time the three steps a third time on a quiet Mac, not before November 20, 2026.
  - The fixes under every option: `specweave review` must not fall back to the builder's own family when the Codex reviewer is refused on a ChatGPT sign-in; a coordinator must not start a second review after a recorded ship by another family; the Done card lists every recorded review with a link to its thread; a Planned card gets Start, and Start covers every task; removing a project drops its settings override.
  - **Decided November 18, 2026 by Anton, in his own words, not as A, B or C:** "Maybe you could deliver it as it is, and I'm going to do a review in a day or two or something like this. Just check that everything is correct from the code perspective, and explain in short what the circumstance is." The three-step guide is built as AC-19 describes it, with the same request sentence. The kill rule of AC-15 and the go rule of AC-19 are lifted by him, and no third timing round runs. The gate is code checks (AC-25). Section F holds the criteria. The fixes above and AC-07 to AC-10 move to increment 1418 and do not gate the guide. `specweave complete` waits for Anton's own review of the delivered guide.
- D-12, for Anton, asked November 19, 2026: who does AC-25's one real run on M4. A finished guide removes the "Build a first feature" card from that machine's Overview for good (`serverConfig.firstFeatureFinished` counts every project row, deleted ones too), and Muse and Codex were out, so an agent run that night would have spent his offer and reviewed without them. **Decided November 19, 2026: "My own review is the run".** No agent runs the guide on M4. When Anton tries it there, the lead writes `reports/e2e-run-released.md` from that run's threads: the app version, times per step and the reviews recorded. T-10 and `specweave complete` wait for that run and his review, as D-11 already says.
- D-13 (November 19, 2026, about 12:45 AM Eastern, replaces D-12): Anton answered "you do it myself" in the lead's thread and confirmed on a card, "Yes, you run it", after being told the Overview card goes away on this Mac for good. An agent runs the guide once on M4's installed app (1.0.374; PR 659's end-action wrap is in 1.0.375, not installed) with Muse and Codex out, and records it in `reports/e2e-run-released.md`. The sample project is left in place for his review. T-10 and `specweave complete` still wait for his review (D-11).

### Defaulted (change any before sw-do)
- D-03: Real agents on the person's own plans. No simulated run.
- D-04: The sample project starts with SpecWeave off, the one exception to 1396 D-02.
- D-05: The feature is a dark mode switch on a one-page sample with one test.
- D-06: The plan is asked for as a planned increment and started from its card.
- D-07: The reviewer shown is the one the app would really pick for this work: the first ready model of the Review list from another family than the worker's. No model name is written into the guide, and this increment changes no list. Muse Wonder Full 1.0 at Extra High becomes the built-in first entry with PR 532 (1339); until that merges the built-in first entry is Muse Wonder 1.0 at Extra High. The prototype shows Muse Wonder Full 1.0 as the example for a Claude-built feature on a machine where Muse Code is ready.
- D-08: The guide is offered on the Overview page and in the command palette, never in setup.
- D-09: Generated artwork is used in the film only.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

## Tasks

### T-01 Acceptance: 1387 is accepted and D-01, D-02 are answered
- AC: AC-16 | Files: none | Test: grep -q "Accepted by Anton on" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/spec.md

### T-02 Run the six steps by hand three times and decide go or stop
- AC: AC-10, AC-15 | Files: none | Test: grep -Eq "^Verdict: (go|stop)" .specweave/increments/1398-first-feature-walkthrough-turn-specweave-on-ask-for-a-feature-watch-the-board-review-done/reports/e2e-run.md

### T-11 Run the three-step variant by hand three times and decide go or stop
- AC: AC-19 | Files: none | Test: grep -Eq "^Verdict: (go|stop)" .specweave/increments/1398-first-feature-walkthrough-turn-specweave-on-ask-for-a-feature-watch-the-board-review-done/reports/e2e-run-variant.md

### T-03 Moved to increment 1418: review of coordinator work and the Board's review field
- AC: AC-07, AC-08, AC-09, AC-10 | Files: none | Test: test -f .specweave/increments/1418-one-review-per-finished-feature-by-another-model-family/spec.md

### T-04 Server: the sample project, the guide's two stored facts, review off for the sample, recorded reviews on the card
- AC: AC-01, AC-03, AC-12, AC-21, AC-22 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/firstFeatureSample.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/firstFeatureSample.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ManagedProjectFolders.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ManagedProjectFolders.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoard.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoard.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/incrementReview.ts, repositories/anton-abyzov/specwithcode/apps/server/src/review/incrementReview.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/project.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspace.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectBoard.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/firstFeatureSample.test.ts src/project/ManagedProjectFolders.test.ts src/project/ProjectBoard.test.ts src/review/incrementReview.test.ts

### T-05 Web: the guide, its three steps read from real state, and the end
- AC: AC-05, AC-18, AC-22, AC-23 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/FirstFeatureGuide.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/FirstFeatureGuide.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/firstFeature.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/firstFeature.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectMoreMenu.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/firstFeature

### T-06 Web: the offer on the Overview page and in the command palette
- AC: AC-11, AC-12, AC-20 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/FirstFeatureOffer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/FirstFeatureOffer.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/project/firstFeatureSample.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/firstFeatureSample.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/firstFeature/FirstFeatureOffer.test.tsx

### T-07 Motion for the guide, its fixture checks, and the prototype scene
- AC: AC-24 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/index.css, repositories/anton-abyzov/specwithcode/apps/web/tests/first-feature/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/first-feature/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/first-feature/verify.mjs

### T-08 End to end with the fake agent: sample project, three steps, a card in Done with its review listed
- AC: AC-22, AC-25 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-projects/first-feature.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/first-feature.test.mjs | Test: cd repositories/anton-abyzov/specwithcode && node --test scripts/studio-projects/first-feature.test.mjs

### T-09 Translations, docs and the changelog
- AC: AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/i18n.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/firstFeature/FirstFeatureGuide.host.test.tsx, repositories/anton-abyzov/specwithcode/docs/user/first-feature.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: grep -qi "first feature" repositories/anton-abyzov/specwithcode/docs/user/first-feature.md

### T-10 Review each PR, ship, record one real run on the release, verify; close after Anton's review
- AC: AC-17, AC-25 | Files: none | Test: specweave verify 1398-first-feature-walkthrough-turn-specweave-on-ask-for-a-feature-watch-the-board-review-done
