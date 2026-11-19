# Plans and a board out of the box: SpecWeave when a project is made, when a plan is asked for, and on the Board

Child of 1387. It takes over 1387's AC-24 to AC-31 and adds the on-demand setup Anton asked for on November 18, 2026.

## Problem

A new user asks the coordinator for a plan and gets one the Board cannot show, and the button that should fix it fails. Anton hit all of it on M5 in "firstproject". The full record with evidence and the reproduction is `reports/firstproject-m5.md`. CLI paths are in `repositories/anton-abyzov/specweave` at `origin/develop`. App paths in the four bullets below are in `repositories/anton-abyzov/specwithcode` at `a23f3593f`, the build M5 ran, because they tell what happened. Since then 1392 (PR 570, `be3fee857`) and 1391 (PR 571) merged, and `origin/main` is `d65dffec9`: the paragraph "What is already fixed" says what that changed, and every AC cites `d65dffec9`. This increment builds on 1392 and repeats none of it: see "With 1392" under Approach.

- **What happened.** firstproject came in through first-run setup's import step as a plain folder with no Git (`apps/web/src/components/onboarding/ProjectsStep.tsx:261`). Nothing asked about SpecWeave. On November 18 Anton asked the coordinator to "create an increment". The coordinator passed `increment: "new"`, the server added "Plan it first: `specweave create-increment` ..." without checking the project (`apps/server/src/project/launchIncrement.ts:209`, the check is at `:282`), and the worker ran the CLI the app installs. The CLI wrote `.specweave/increments/0001-…` with `spec.md` and `plan.md` and no `config.json`. So it is a real SpecWeave folder in a project where SpecWeave was never set up, not a SpecWithCode plan.
- **Why the Board does not see it.** "SpecWeave is on" means `.specweave/config.json` exists at the project root or an umbrella above plans it (`isSpecweaveProject`, `apps/server/src/project/ThreadIncrementProgress.ts:231`). The Board and Project settings follow that. The thread header does not: the progress read lists increments from the folder first and asks the question afterwards (`apps/server/src/project/ThreadIncrementProgressService.ts:903`). Later launches also treat a bare `increments/` folder as on (`launchIncrement.ts:282`) and hand out the sizing rule that tells workers to run `create-increment` (`:118`). Half the app says on, half says off.
- **The fix button fails.** Anton pressed "Set up SpecWeave" on the Board. It refused: "SpecWeave needs a Git repository: this folder is not one. Run git init here first, then try again." (`apps/server/src/project/SpecweaveSetup.ts:173`). A person who was never told about Git has nowhere to go from there.
- **The CLI lets it happen.** `specweave create-increment` falls back to the current folder when no `config.json` is found (`src/cli/commands/create-increment.ts:110`, `src/utils/find-project-root.ts:190`). `get`, `sync`, `skills` and others refuse in that case. Any thread can run it directly, whatever the app checks, and 1392 leaves the CLI alone.
- **Who is asked about SpecWeave today.**

  | How the project arrives | Asked? |
  |---|---|
  | New project dialog | Yes, on by default, but the row is inside the Options group (`apps/web/src/components/CommandPalette.tsx:1079`, `apps/web/src/components/studio/ProjectCreation.tsx`) |
  | An agent creates it with `studio_project_create` | No. The tool has no SpecWeave argument (`apps/server/src/mcp/orchestratorFeatures.ts:14`), so it is always off |
  | Imported in first run, added, or cloned | No |
  | Setup failed when the project was made | A toast, once. Nothing is stored, and the project reads as off |

- **The Board with SpecWeave off** is one paragraph and a button behind a second confirmation (`apps/web/src/components/studio/shell/BoardPane.tsx:137`, `apps/web/src/components/studio/ProjectSpecweaveSetting.tsx:102-107`). An empty board tells the user to type `specweave create-increment` (`BoardPane.tsx:421`).
- **What is already fixed at `d65dffec9`.** 1392: an empty folder picked in setup becomes a Git project, the Board's button sets up Git too ("Set up Git and SpecWeave"), and `"new"` or `"none"` in a project without a config gets `SPECWEAVE_OFF_NEW_BRIEF` or `SPECWEAVE_OFF_BRIEF` and a warning instead of the `create-increment` line (`apps/server/src/project/launchIncrement.ts:130`). 1391: the Board with cards has five groups and a denser card. **Still true:** a bare `increments/` folder counts as on for later launches (`hasIncrements`, `launchIncrement.ts:299`), the header and the Board disagree, nobody is asked before a worker starts, and the Board's off state and its empty sentence are unchanged (`BoardPane.tsx:172`, `:572`).
- **What already works.** The app installs its own `specweave` and Node.js for agents (`apps/server/src/machineTools/specweaveTool.ts`), and setup finds them (`apps/server/src/project/nodeToolDirs.ts:89`). Running `git init` and then `specweave init --quick --adapter claude` over the M5 state writes `config.json`, keeps the plan and commits nothing (reproduced on M4).

## Scope

In:
- One answer to "is SpecWeave on here", with a third value for the half state.
- Launches and the CLI stop planting increments where SpecWeave is not set up.
- Setup on demand: a card in the thread when a plan is asked for, one press, and the result on the Board.
- Setup that cannot dead-end: no Git, the half state, a missing Node.js, a failure that is remembered.
- The Board's off, unfinished, failed and empty states, with an example board.
- Every way a project arrives says what it does about SpecWeave.

Out:
- The Board's own design (1338). Only its states without cards change.
- Turning SpecWeave on in an existing folder without a press (D-01).
- SpecWithCode's own project plan for projects that stay off. It is not changed.
- Removing SpecWeave from a project.

## Acceptance Criteria

### A. One answer

- [ ] AC-01: `specweaveState(workspaceRoot)` in `ThreadIncrementProgress.ts` returns `on` (today's `isSpecweaveProject`), `unfinished` (the root holds `.specweave/increments` with at least one increment folder, no `config.json`, and no umbrella above plans it) or `off`. `isSpecweaveProject` becomes `state === "on"`. The workspace read (`apps/server/src/project/ProjectWorkspaceService.ts:549`), the thread-progress read (`ThreadIncrementProgressService.ts:903`) and launch (`launchIncrement.ts:282`) all call it. A table test covers: config at root; umbrella above; increments without config; an empty `.specweave`; a `config.json` that is a link; a personal assistant.
- [ ] AC-02: The workspace snapshot (`packages/contracts/src/projectWorkspace.ts:219`) and the thread-progress result (`packages/contracts/src/threadIncrementProgress.ts:222`) gain an optional `specweaveState` beside today's `specweave` boolean. With `unfinished` the snapshot also carries the count and the first three titles of the increments found. A client that gets no `specweaveState` behaves as today. `studio_project_read` returns the state too.

### B. No plan is planted where SpecWeave is not set up

- [ ] AC-03: `resolveLaunchIncrement`, in a project whose state is `off` or `unfinished`. 1392 already stops the `create-increment` brief for `"new"` and `"none"` when there is no config: the worker is launched with `SPECWEAVE_OFF_BRIEF` and the caller gets a warning. This AC goes further for `"new"`, and covers the omitted and inherited cases 1392 does not touch:
  - `"new"` appends no line, starts no thread, and returns `needsSpecweave` (AC-06) in place of 1392's warning. Once the user has answered "Plan without it" (AC-07), `"new"` behaves as 1392 left it: the worker starts with `SPECWEAVE_OFF_NEW_BRIEF` and plans in its reply.
  - An explicit `NNNN` that exists in an `unfinished` project still resolves, so work on it can go on, and the result carries: "SpecWeave setup is unfinished in this project. The Board cannot show this increment until the user finishes setup." The same call raises the card of AC-05 without waiting for it.
  - `"none"` keeps 1392's `SPECWEAVE_OFF_BRIEF`. An omitted `increment` and an inherited one append no `specweave` command. The `hasIncrements` test at `launchIncrement.ts:299` is gone, so `UNPLANNED_BRIEF` and its sizing rule are given only when the state is `on`.
  - Tests cover each of the three states against `"new"`, `NNNN`, `"none"` and omitted.
- [ ] AC-04: The CLI refuses. `specweave create-increment` run where no `.specweave/config.json` is found at or above the folder, or with a `--project-root` that has none, exits non-zero, writes nothing, and prints: "This folder is not set up for SpecWeave. Run `specweave init` here first. In SpecWithCode, press Set up SpecWeave on the project's Board tab." Inside an umbrella's member repository it works as today. The app's installed CLI moves to that release (`apps/server/src/provision/manifest.ts`, `SPECWEAVE_VERSION`). AC-01 stays, because older CLIs are on people's machines.

### C. Setup on demand

- [ ] AC-05: The card. A thread can show one "Set up SpecWeave" card, built like the access-request card (`apps/server/src/access/AccessRequests.ts`, `apps/web/src/components/chat/AccessRequestCard.tsx`).
  - Heading: "Set up SpecWeave to plan this".
  - Text: "A plan is a short spec with tasks, kept in your repository. It also puts this project's work on a board."
  - "What it adds" opens the list: `.specweave/`, agent skills in `.claude/` and `.agents/`, sections in AGENTS.md and CLAUDE.md, rules in .gitignore and .gitattributes. "The new files are left for you to review and commit."
  - In a folder without Git one more sentence shows before the press: "This folder is not a Git repository yet, so this also starts one here." The button then reads "Set up Git and SpecWeave", the label 1392 gives the Board's setup row, read from the same `gitRepository` hint.
  - Buttons: "Set up SpecWeave" and "Plan without it".
  - States, exactly: Asking; Setting up; On, with "Open the Board"; Failed, with the reason and Retry; Node.js missing, with the reason and "Install Node.js" (`requestMachineToolInstall`); Not allowed, with the reason (the window's access lacks the write scope, or team rules); Declined.
  - One card per project is open at a time. A second request returns the open one.
- [ ] AC-06: Who raises it.
  - `delegate_task`, `create_threads` and `studio_thread_launch` called with `increment: "new"` in a project that is `off` or `unfinished`. The result is `{ launched: false, needs: "specweave" }` with: "SpecWeave is not set up in this project. The user has a card to set it up. End your turn; their answer wakes you."
  - A new tool, `request_specweave_setup`, for an agent whose user asks for a plan, a spec or an increment, and for a worker the CLI refused (AC-04). In a project that is `on` it raises nothing and says so.
  - The orchestration line (`apps/server/src/provider/StudioOrchestrationInstructions.ts:24`) and the three tools' descriptions say: in a project without SpecWeave, when the user asks for a plan, a spec or an increment, call `request_specweave_setup` and end your turn; never run `specweave create-increment` there.
- [ ] AC-07: The answers.
  - "Set up SpecWeave" runs AC-08. On success the card reads On and the thread is woken with: "SpecWeave is set up in this project. Plan the work now: launch it with increment \"new\"."
  - "Plan without it" is stored for the project on the server and wakes the thread with: "The user chose to plan without SpecWeave. Create no increment. Plan the work in your reply before you edit code.", the same home 1392's `SPECWEAVE_OFF_NEW_BRIEF` names. After that no launch raises the card in that project. The Board tab keeps its offer, and `request_specweave_setup` with `askedByUser: true` raises it again.
  - Two facts are stored per project on the server, and no others. `specweaveDeclined` is set by the card's "Plan without it", the Board's "Not now" (AC-11) and the composer line's dismiss (AC-18). While it is set, launches do not raise the card, the composer line does not show, and the Board's off state stays with its button and without "Not now". A successful setup clears it. `specweaveAdviceSeen` is set by any of the composer line's three actions, and its only effect is that the line never returns.
  - A card left unanswered blocks nothing else in the thread and stays answerable.
- [ ] AC-08: Setup that cannot dead-end (`SpecweaveSetup.ts`, `projects.specweaveSetUp`).
  - A folder that is not a Git repository: 1392 owns this. Its `initGit: true` runs `git init`, then `specweave init`, stages nothing, and tries one empty first commit so branches and worktrees have a base. This increment adds no second Git path. The card sends the same flag, and only after showing the sentence of AC-05.
  - A folder inside another repository is refused as 1392 leaves it, and the card shows that reason in its Failed state.
  - Over `unfinished`, the increments already there are kept (1392 AC-05). The test here writes one, runs setup, and asserts the state turns `on` and the snapshot lists it.
  - It uses the `specweave` the app installed, then one on the person's PATH, then `npx` (today's order in `nodeToolDirs.ts`), and Node.js missing still offers the install.
  - A failure is stored for the project on the server with its reason and whether Node.js is missing, is returned in the workspace snapshot, and is cleared by the next success. This also covers a setup that failed when the project was made.
- [ ] AC-09: The result is on the Board. After a successful setup the workspace snapshot is read again, and the Board tab shows its cards within 5 s without a reload, including increments that were written before setup. An increment made after it appears at the Board's next refresh (`BoardPane.tsx:183`).
- [ ] AC-10: End to end, as a test with the offline fake agent: a plain folder with no Git is added as a project; the coordinator is asked for an increment; a launch with `"new"` returns `needs: "specweave"` and the card shows; "Set up Git and SpecWeave" is pressed; the relaunch creates an increment; the Board lists it. No `.specweave` exists before the press.

### D. The Board and the thread

- [ ] AC-11: Board tab, state `off`. It replaces "Start a board for this project" (`BoardPane.tsx:172`, found by its text), which 1391 left untouched for this increment. Heading "See this project's work as a board", the sentence "Plans each piece of work as a short spec with tasks in your repository, and gives the project a board.", the list of AC-05, "Set up SpecWeave" and "Not now". The list is visible before the press, so one press runs setup. Project settings keeps its two steps. The states are those of AC-05. "Not now" sets `specweaveDeclined` (AC-07): the card stops coming up at launches, and this state stays here with its button.
- [ ] AC-12: Board tab, state `unfinished`. Heading "{n} plans here are not on the board yet". Text: "They were written before SpecWeave was set up in this project. Finish setup and they show as cards." The first three titles are listed. The button reads "Finish setup", or "Set up Git and finish" in a folder without Git. Same states.
- [ ] AC-13: Thread. Where a thread shows its increment (`apps/web/src/components/ChatView.tsx`, `apps/web/src/components/studio/ProjectThreadCards.tsx`) and the project is `unfinished`, the increment label carries "Not on the board yet", and pressing it opens the Board tab's unfinished state. In a project that is `on` nothing changes.
- [ ] AC-14: Example board, beside the explainer of AC-11.
  - It renders the real `BoardCard` from a sample module under `src/` (4 to 6 cards shaped like `apps/web/tests/project-board/mocks.tsx`, with a fixed `now`), is `inert` and `aria-hidden`, and carries the word "Example" on the board itself.
  - Groups and card anatomy are the real board's after 1391, which is merged: the same group sections (`BoardGroupSection.tsx`, `data-group`) and the same `BoardCard`, rendered without `onAsk`, so a sample card has no request button. The pane's own measure decides the layout (`data-layout="columns"` or `"stack"`, `BoardPane.tsx:576`): Planned, Active, In review, Done side by side, and 1391's stacked order otherwise. A card in Done shows no meter and no count, as on the real board. No sample card is blocked, so no Blocked group shows, and no sample card passes `stateLabel`.
  - It plays once when first seen: one card moves from Planned to Active (a working thread appears), to In review (its pull request appears), to Done. Every card sits in the column its evidence says.
  - It never loops, waits while the tab is hidden, and is a still last frame under reduced motion and whenever the board is stacked.
- [ ] AC-15: A board that is `on` with no increments (`BoardPane.tsx:572`) reads "No work planned yet." with "Plan the first piece of work", which puts a planning request in the coordinator's composer through `onAsk`. The `specweave create-increment` hint goes away.

### E. Every way a project arrives

- [ ] AC-16: New project dialog. "Use SpecWeave" shows above the Options group for a code project (the group was never collapsed; wording fixed November 18, 2026), on by default as today, with the sentence of AC-11. What it adds stays behind its disclosure. Where the server cannot set it up (`serverConfig.specweaveSetUp` is not true, `CommandPalette.tsx:1088`) the row shows off and reads "This machine's SpecWithCode is too old to set it up." instead of vanishing.
- [ ] AC-17: `studio_project_create` takes `specweave`. It defaults to true for a new code project in a new folder and is ignored for an existing folder and for a personal assistant, as the dialog does. The result says "SpecWeave set up" or why not. An older machine that does not know the argument is told so in the result (`apps/server/src/mcp/toolkits/project/createOnMachine.ts`).
- [ ] AC-18: An existing folder is advised once and never changed without a press. A project that was imported, added or cloned and is `off` shows one line above the coordinator's composer at its first open: "Plan this project's work on a board.", with "Set up SpecWeave", "See the board" and a dismiss. Any of the three sets `specweaveAdviceSeen` and the line never returns; the dismiss also sets `specweaveDeclined` (AC-07). It is chosen by one function together with the Full access recommendation, which wins when both apply (`apps/web/src/components/chat/ChatComposer.tsx:1436`). It takes no focus and covers nothing.
- [ ] AC-22: First-run setup gets no SpecWeave step. An empty folder picked on its Projects step is a new project: since 1392 it is created through `projects.createNew` as a Git repository with starter files, but without SpecWeave (`ProjectsStep.tsx` on PR 570 sends no `specweave`). Under D-02 its row shows one checked box, "Start with SpecWeave, for plans and a board", and the create call sends `specweave` as the box stands. A folder that has files gets no box and is bound as it is, as 1392 keeps it. Where the server cannot set SpecWeave up, there is no box. A setup that fails there is soft: the project is still created and the failure is stored (AC-08). The box adds no step and no gate, so 1387's walker passes unchanged; a fixture case covers an empty folder with the box on and off.

### Text, gate, review, shipping

- [ ] AC-19: Strings follow each surface's practice on the day. `docs/user/` gains a page on plans and the board: what SpecWeave adds, the card, the three states, a folder without Git. CHANGELOG Unreleased has the entries, in both repositories.
- [ ] AC-20: No code before Anton accepts. The gate is the line "Accepted by Anton on <date>" in 1387's spec, with D-01 and D-02 answered here.
- [x] AC-21: Muse Wonder Full 1.0 at Extra High, with full access, reviews each PR at its head. Every finding is fixed or answered in `reports/reviews/`. Each PR is green, merged and released, and the scenario of AC-10 is then run once by hand on M5, in a plain folder with at least one file and no Git that is added as an existing folder (D-11; amended November 18, 2026, the first wording said "in firstproject on M5"). The press was Anton's; on November 18, 2026 he handed it to the increment's lead ("do it yourself on m5!"), so the request is typed and the card pressed through the M5 app's own pages, headless, with a sign-in made for the check and revoked after it (D-12).

## Approach

### The scenario

1. The user asks for a plan, a spec or an increment.
2. If the project is `on`, nothing changes from today.
3. If it is `off` or `unfinished`, no thread starts and no file is written. A card appears in the same thread, and the coordinator says in one line that a plan needs one press.
4. "Set up SpecWeave" runs setup with the CLI the app already installed. In a folder without Git it starts Git too and says so first.
5. The coordinator is woken, launches the work, and the worker creates the increment. The thread shows it, and the Board shows the same card.
6. "Plan without it" is remembered. The coordinator plans with SpecWithCode's own plan, and no card is raised again by a launch.

The same setup, with the same states, is on the Board tab, in the line above the composer, and in Project settings.

### Order of work

0. **1392 and 1391 are merged** (`be3fee857`, and PR 571 at `d65dffec9`; 1391's follow-up PR 580 touches only `boardNoteText` and the fold-follow). Both app PRs here start from `origin/main` after them.
1. **CLI PR** (T-02), in `repositories/anton-abyzov/specweave`. Released first, then the app's pinned version moves.
2. **App PR 1, server** (T-03 to T-05): the state, the launch gate, setup, the card's request, the tool.
3. **App PR 2, web** (T-06 to T-09): the card, the Board states, the example board, the thread label, the dialog row, the composer line.
4. T-10 to T-12: the end-to-end test, text, review, the run on M5, close.

### Rejected

- Setting it up automatically when a plan is asked for. See D-01.
- Making the half state count as on. The Board would then read a project with no config, no skills and no agent rules, and every other SpecWeave feature would have to guess.
- Deleting the stray `.specweave/increments` folder. It holds the user's plan.
- A SpecWeave stage in first-run setup. Setup is per machine and SpecWeave is per repository, and there may be no project yet.
- An example board drawn by hand. It would drift from the real cards.
- Only fixing the app. A thread can run the CLI directly.

### Risks

- The CLI change is a behaviour change for anyone who relied on `create-increment` without `init`. Its message names the fix, and the test suite of the CLI runs before release.
- Starting Git in a user's folder is a real change. It happens only on a press that says so, and none of the user's files are committed (1392 makes one empty first commit).
- The card depends on agents calling a launch with `"new"` or the new tool. A worker that ignores both and runs the CLI is stopped by AC-04, and one on an older CLI is caught by the `unfinished` state.
- This increment touches one first-run file, `ProjectsStep.tsx` (AC-22), after 1392 and inside 1387's walker contract. Its other PRs can ship in any order with 1387's.

### With 1392

1392 ("Set up Git and SpecWeave in one click for new projects", PR 570, merged as `be3fee857`) came out of the same evening on M5 and fixes the dead end directly. What it ships, and what is left for this increment:

| | 1392 ships | This increment adds |
|---|---|---|
| Empty folder picked in first-run setup | Created as a Git repository with starter files and a first commit. SpecWeave stays off. | The checked box, so it starts with SpecWeave (AC-22, D-02) |
| Setup in a folder without Git | `initGit`, the `gitRepository` hint, the Board row's button "Set up Git and SpecWeave" | The same press from a card in the thread (AC-05), and a failure that is remembered (AC-08) |
| `increment: "new"` with SpecWeave off | The worker plans in its reply, and the caller gets a warning that points at the Board | No launch; the user gets a card, and the plan becomes an increment after one press (AC-03, AC-06) |
| A plan written before setup | Shows on the Board after setup | Is counted and named before setup: the `unfinished` state, the Board's text, the thread label (AC-01, AC-12, AC-13) |
| The CLI | Not changed | `create-increment` refuses without a config (AC-04) |
| Explaining SpecWeave | Not changed | The Board's explainer and example board, the dialog row, `studio_project_create`, the line above the composer (AC-11, AC-14 to AC-18) |

If 1392 changes before it merges, T-03 and T-04 are re-read against what merged, not against this table.

### With 1391

1391 redesigns the Board with cards on it: five groups (Blocked, Active, In review, Planned, Done) that fold, a denser card, a machine legend. It is merged (PR 571, `d65dffec9`). It left the off state (`BoardPane.tsx:172`) and the zero-increments sentence (`:572`) to this increment. The example board of AC-14 renders 1391's real groups and card, so it follows them without a rule of its own. In the fixture, 1391 owns the board pages of `apps/web/tests/project-board/verify.mjs`, with their group order, counts and 44 captures, and this increment changes only its `setup` page and the checks of that page.

## Decisions

### Asked
- D-01, for Anton: a plan is asked for in a project without SpecWeave. Recommended **A. Ask once with a card: "Set up SpecWeave" or "Plan without it".** B. Set it up without asking and say so in the thread. A is recommended because setup writes into a repository the user owns: `.specweave/`, skills in `.claude/` and `.agents/`, sections in AGENTS.md and CLAUDE.md, and in a folder without Git it has to start Git. That should be one press, not a surprise. With D-02 the card only ever shows in folders that existed before SpecWithCode. **Decided November 18, 2026: A.**
- D-02, for Anton: the default for new projects. Recommended **A. On by default for every new code project, whether it is made in the New project dialog, by an agent, or by picking an empty folder in first-run setup, and never automatic for a folder that already has files.** B. Also turn it on when a folder is imported, added or cloned. Under A a project made the way firstproject was would have started with Git and SpecWeave. **Decided November 18, 2026: A.**

### Defaulted (change any before sw-do)
- D-03: In a folder without Git the press also runs `git init`, after saying so. The alternative is to tell the user to run it, which is where Anton got stuck.
- D-04: "Plan without it" and "Not now" are remembered per project, on the server, so every device agrees.
- D-05: `create-increment` refuses without `config.json`. It does not run `init` itself.
- D-06: The half state is named `unfinished` and offered as "Finish setup". Nothing is deleted or moved.
- D-07: First-run setup has no SpecWeave step. The one thing it shows is the checked box on an empty folder's row (AC-22).
- D-08, settled by the increment's lead on November 18, 2026: the card is kept per project on the server and shown through the workspace snapshot, with one new call, `projects.specweaveAnswer`, for "Plan without it", "Not now" and the composer line. That call reuses an existing access scope that a window without file-write access holds; a new scope would go to Anton. A real timeline item was weighed and left out, because it adds about 20 files across the orchestration layer and the phone app. T-05's Files are widened for it.
- D-09, same day: `--project-root` prints the AC-04 message too, so `bin/specweave.js` joins T-02's Files and one CLI release is enough.
- D-10, same day: the launch tools keep AC-06's result, `{ launched: false, needs: "specweave" }`, and do not turn it into a tool error. An error reaches the agent as a bad request and invites a retry without a plan.
- D-11, same day: the M5 hand run moves from firstproject to a new plain folder on M5. firstproject got Git and `config.json` at 5:02 AM EST on November 18, 2026, when 1392's check pressed the Board's "Set up Git and SpecWeave" there (`.specweave/increments/1392-set-up-git-and-specweave-in-one-click-for-new-projects/reports/m5-verification.md`; read back on M5 the same evening: one empty commit `297070b`, `config.json` from 5:02:39). A request there now plans 0002 with no card, so it would not show AC-10, and the folder is not stripped to bring the old state back. The new folder holds one file and no Git and is added as an existing folder, because a project made in New project gets SpecWeave by default (D-02, A). Its coordinator runs on Codex while Claude on M5 is at its limit (until about 9 PM Eastern on November 19, 2026): a launch with `"new"` answers `model_unavailable` before `needs: "specweave"` when no model can be routed.
- D-12, same day: the M5 run is made by an agent, not by hand. Anton was given the four steps and answered "do it yourself on m5!". A worker on M5 drives the released app's pages in a headless browser: it types the request to the `plain-notes` coordinator, presses "Set up Git and SpecWeave" on the card, and reads the Board and the folder back. Nothing is called over RPC in place of a press. The record is `reports/m5-plain-notes-run.md`.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

Rounds 1 and 2 were on 1387 before the split. Their findings on this part and the answers are in 1387's `reports/reviews/review-r2-responses.md`.

## Tasks

### T-01 Acceptance: 1387 is accepted and D-01, D-02 are answered
- AC: AC-20 | Files: none | Test: grep -q "Accepted by Anton on" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/spec.md

### T-02 CLI: create-increment refuses a folder that was never set up
- AC: AC-04 | Files: repositories/anton-abyzov/specweave/src/cli/commands/create-increment.ts, repositories/anton-abyzov/specweave/tests/unit/cli/commands/create-increment-no-config.test.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/CHANGELOG.md | Test: cd repositories/anton-abyzov/specweave && npx vitest run --config vitest.unit.config.ts tests/unit/cli/commands/create-increment-no-config.test.ts tests/unit/cli/commands/create-increment.test.ts

### T-03 Server: one state, in the snapshot, and the launch gate
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgress.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgress.state.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgressService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/launchIncrement.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/launchIncrement.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspace.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/threadIncrementProgress.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ThreadIncrementProgress.state.test.ts src/project/launchIncrement.test.ts

### T-04 Server: setup keeps what is there and remembers a failure, on top of 1392's Git step
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ManagedProjectFolders.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspaceRpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspace.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provision/manifest.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/SpecweaveSetup.test.ts

### T-05 Server: the setup card's request, the tool, the launch tools, the wake-ups
- AC: AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetupRequests.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetupRequests.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/requestSpecweaveSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/requestSpecweaveSetup.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/specweaveSetupRequest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspaceRpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestratorMcp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/SpecweaveSetupRequests.test.ts src/mcp/toolkits/orchestrator/requestSpecweaveSetup.test.ts

### T-06 Web: the card in the thread, with its seven states
- AC: AC-05, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/SpecweaveSetupCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/SpecweaveSetupCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/specweaveSetup.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/specweaveSetup.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/SpecweaveSetupCard.test.tsx src/components/studio/specweaveSetup.logic.test.ts

### T-07 Web: Board tab off, unfinished and failed, with the example board, on top of 1391
- AC: AC-11, AC-12, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardSetup.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardExample.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/boardExample.sample.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/board.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectSpecweaveSetting.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell && node tests/project-board/verify.mjs

### T-08 Web: the thread label, the empty board, and the one line above the composer
- AC: AC-13, AC-15, AC-18 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectThreadCards.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/SpecweaveOffer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/SpecweaveOffer.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/composerNotice.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/composerNotice.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AccessRecommendation.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/SpecweaveOffer.test.tsx src/components/chat/composerNotice.logic.test.ts src/components/studio/shell/BoardPane.test.tsx

### T-09 The dialog row, the first-run box for an empty folder, and the agent tool's argument
- AC: AC-16, AC-17, AC-22 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ProjectsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.import.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectCreation.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/hooks/useNewProject.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/project-folder-choice/verify.mjs, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/createOnMachine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/createOnMachine.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/orchestratorFeatures.ts | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/project-folder-choice/verify.mjs && cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/mcp/toolkits/project/createOnMachine.test.ts && cd ../web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding/WelcomeWizard.import.test.tsx

### T-10 End to end with the fake agent: plain folder, ask for an increment, one press, a card on the Board
- AC: AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-projects/specweave-on-demand.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/specweave-on-demand.test.mjs | Test: cd repositories/anton-abyzov/specwithcode && node --test scripts/studio-projects/specweave-on-demand.test.mjs

### T-11 Docs and the changelogs
- AC: AC-19 | Files: repositories/anton-abyzov/specwithcode/docs/user/plans-and-board.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: grep -q "Set up SpecWeave" repositories/anton-abyzov/specwithcode/docs/user/plans-and-board.md

### T-12 Review each PR, ship, run the scenario on M5 (D-11), verify and close
- AC: AC-21 | Files: none | Test: specweave verify 1396-plans-and-a-board-out-of-the-box-specweave-when-a-project-is-made-when-a-plan-is-asked-for-and-on-the-board
