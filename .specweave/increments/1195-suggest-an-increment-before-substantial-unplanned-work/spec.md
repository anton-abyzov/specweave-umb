# Suggest an increment before substantial unplanned work

This is the current spec for how SpecWithCode threads and SpecWeave increments connect. It consolidates 0996 (bindings and the opt-in edit guard) and 1001 (launch increments, inheritance, the unplanned notice and its Dismiss) with the change below. Read this one first; those two stay as history.

## Problem

On November 2, 2026 an EasyChamp worker ("PS23 playoff bracket how-to") deployed a new API build to production, added a swap endpoint and merged console PR #539 with no increment. Nothing suggested one before the code changed; the only signal was the plan card afterwards ("Changed code without an increment").

Root cause, from the thread's own record:

1. The coordinator launched it for a read-only question ("how to create ps23.soccer playoffs brackets?", "Change nothing") with `increment: "none"`, which is correct for a question. The brief it appends, `If you change code, run \`specweave small-fix "<why>"\` first.`, offers only the small-fix path.
2. Later user follow-ups ("What to do next?") were forwarded to the same worker and turned the question into feature work and a deploy. Nothing re-evaluates the need for an increment when a thread's scope grows: the launch brief is read once, and the worker's per-turn project context only covers working an increment it already has.
3. EasyChamp has no `planning.requireIncrement`, so SpecWeave's edit guard is `off` there (its default) and gives no reminder. The umbrella uses `remind`, but even there a session that ran `small-fix` once counts as planned for the rest of the session.
4. The SpecWeave template that projects get says "Recommended for features, not required; to skip one run small-fix", which reads as permission to skip an increment for a feature.

## Current behaviour (consolidated)

- Identity: every SpecWithCode spawn site exports `SPECWEAVE_STUDIO_THREAD_ID`, `SPECWEAVE_TOOL` and `SPECWEAVE_MODEL` (Codex through `shell_environment_policy.set.*`), so SpecWeave ledger writes bind the right thread in `~/.specweave/studio/threads/<thread>.json`.
- Launch: `delegate_task`, `create_threads` and `studio_thread_launch` take `increment` (NNNN, folder, "new" or "none"). A found increment seeds the binding and the brief names its spec; "new" asks the worker to plan first with `create-increment`; "none" records nothing. With no ref a worker inherits its caller's claim or branch binding (never a coordinator's). Under `enforce` a coordinator without `increment` is refused; under `remind` it gets a warning.
- After the fact: threads whose completed, not rolled-back file changes touched code with no increment, small-fix or "none" link are listed as unplanned. The plan card offers Link increment and No increment needed; the notice is neutral, hideable per project and dismissible per thread on this device.
- Edit guard (SpecWeave, `planning.requireIncrement`): `off` by default; `remind` adds one note per session; `enforce` denies until `create-increment`, `task claim` or `small-fix`.
- Increments stay recommended, not required (Anton, October 23, 2026). `enforce` is a team opt-in.

## Scope

In: a sizing rule in the "none" and no-increment launch briefs, in the worker's per-turn project context and in the launch-tool instruction, so a worker plans an increment before substantial work, including when a follow-up widens a question into a build; the same rule in SpecWeave's project template; pointers from 0996 and 1001 to this spec.

Out: turning on `remind` or `enforce` for projects that have not chosen it; a plugin-wide edit hook (rejected in 1001); the model judging scope on the server; changing the after-the-fact notice.

## Acceptance Criteria

- [ ] AC-01: The "none" launch brief keeps the small-fix path for a small change and tells the worker that work growing past a small fix (a new endpoint or command, a schema or data change, a deploy or release, or edits across several files), including when a later message turns a question into a build, is planned first with `specweave create-increment "<title>"` and spec.md before code changes.
- [ ] AC-02: A worker launched in a SpecWeave project with no increment passed or inherited gets a brief with the same sizing rule, under every `requireIncrement` mode, and the existing `remind`/`enforce` warnings still apply.
- [ ] AC-03: The launch-tool instruction tells a coordinator to pass "new" for feature work and "none" only for questions, reviews or a small fix.
- [ ] AC-04: In a SpecWeave project, every worker turn's project context carries the sizing rule for a thread with no increment, so a follow-up that widens the work gets the suggestion before code changes; outside a SpecWeave project the line is absent.
- [ ] AC-05: SpecWeave's `AGENTS.md.template` says `small-fix` is for a change too small to plan, and that work which grows past it gets an increment before more code changes, still recommended, not required.
- [ ] AC-06: 0996 and 1001 specs point to this spec as the current one.

## Approach

App (`anton-abyzov/specwithcode-dev`, worktree `worktrees/increment-suggest`, branch `feat/increment-suggest-before-work`): `launchIncrement.ts` gains one `INCREMENT_SIZING_RULE` sentence reused by `NO_INCREMENT_BRIEF` and a new `UNPLANNED_BRIEF`, returned from the no-ref path when no increment is inherited; `INCREMENT_LAUNCH_INSTRUCTION` names when to pass "new" or "none". `ProjectWorkspaceService.ts` adds the rule to the worker role when `specweave === true`.

SpecWeave (`anton-abyzov/specweave`): one line in `src/templates/AGENTS.md.template`.

Rejected: defaulting the edit guard to `remind` for every project (reverses the user's opt-in choice and reaches users who did not ask); having the coordinator re-brief a forwarded follow-up (the coordinator forwards follow-ups unchanged by rule, and the worker already sees the per-turn context).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Suggest, never enforce → the rule is guidance in briefs and context; increments stay recommended (Anton, October 23, 2026, D-07 of 1001).
- D-02 Where the suggestion lives → worker brief and per-turn project context, not a new hook, because follow-ups never re-read the launch brief.
### Open
- none

## Tasks

### T-01 Sizing rule in launch briefs and the launch instruction
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/project/launchIncrement.ts, apps/server/src/project/launchIncrement.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/worktrees/increment-suggest && node node_modules/vite-plus/bin/vp test run apps/server/src/project/launchIncrement.test.ts

### T-02 Sizing rule in the worker's per-turn project context
- AC: AC-04 | Files: apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/project/ProjectWorkspaceService.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/worktrees/increment-suggest && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectWorkspaceService.test.ts

### T-03 SpecWeave template wording
- AC: AC-05 | Files: src/templates/AGENTS.md.template | Test: grep -q "too small to plan" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/src/templates/AGENTS.md.template

### T-04 Point older specs here
- AC: AC-06 | Files: .specweave/increments/0996-plan-timeline-forecasts-and-required-increments/spec.md, .specweave/increments/1001-connect-specwithcode-launches-to-increments/spec.md | Test: grep -l "1195" .specweave/increments/0996-plan-timeline-forecasts-and-required-increments/spec.md .specweave/increments/1001-connect-specwithcode-launches-to-increments/spec.md

### T-05 Verify and close 1195
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1195
