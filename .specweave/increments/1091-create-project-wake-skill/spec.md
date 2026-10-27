# Create project wake skill

## Problem

After a SpecWithCode update or restart, Anton sees project threads that were working and are now idle, interrupted or failed. Automatic continuation (`continueThreadsAfterServerUpdate`, PRs #467, #608, #638, #750) covers only runs cut off with cause `service_update`, under 24 hours old and still the thread's latest run. Everything else waits for a person: runs that failed when an update closed their stream before #638, holds released without a restart, runs older than 24 hours, delegated results that never relayed to their parent, and finished work that was never verified and closed. On October 27, 2026 the project listed 28 non-settled interrupted, failed or running threads, several from October 23-25.

There is no one command that sweeps a project, decides which of those threads should continue, which need a handoff, and which only need closing.

## Scope

In: a vskill skill `project-wake` (`/project-wake`) in `anton-abyzov/vskill` under `plugins/productivity/skills/project-wake/`, created and published through the Skill Studio UI to verified-skill.com, installed globally on the M4 for Claude Code after SpecWithCode 1.0.100 ships, and verified from a coordinator composer.

Out: changes to SpecWithCode continuation code, slash/catalog/composer code (owned by the Rethink SpecWeave skills and DDD thread), SpecWeave `sw-*` skills, any release dispatch or service restart, periodic or automatic invocation.

## Acceptance Criteria

- [ ] AC-01: `SKILL.md` instructs a coordinator to enumerate every thread of the current project with `studio_thread_list` (all pages until `nextCursor` is null, archived excluded by default), and to report `partial` or unavailable machines as unknown, never as dead.
- [ ] AC-02: For each thread it classifies the latest run (running, interrupted by update/restart, failed by update drain, stopped by a person, waiting on a question or approval, finished but not closed, finished and closed) from `studio_thread_read` evidence, and keeps the original owner.
- [ ] AC-03: It resumes only update- or restart-interrupted work on the thread's own provider when that provider is signed in and has quota, using `studio_thread_send` to the original thread; it never resumes a person's Stop, cancel or hold, never starts a second executor or watcher on a thread that is already running or queued, and never switches to paid or API-billed fallback or raises permissions.
- [ ] AC-04: When the home provider is out of quota or the machine is gone, it hands off only through existing machinery (`studio_thread_migrate`, `studio_handoff_ready_list`, `studio_thread_continue_here`) where already authorized, else lists the thread as blocked with the reset time.
- [ ] AC-05: For work whose tasks are all done it routes closure (verify, fresh-context review, complete) to the owning worker; it never self-attests closure and never treats source or CI as installed proof.
- [ ] AC-06: It ends with one table: thread, state found, action taken, and what still needs the user.
- [ ] AC-07: `vskill scan` passes on the skill with no secrets; the skill is published through Skill Studio and readable on verified-skill.com.
- [ ] AC-08: After SpecWithCode 1.0.100 is installed on the M4, `vskill install --global` puts the skill in the global Claude Code and Codex skill folders, and `/project-wake` appears in and runs from a project coordinator composer (syntax per the skills consolidation owner).

## Approach

1. Write `plugins/productivity/skills/project-wake/SKILL.md` (and an eval file) on a branch of the vskill repo; one short skill, no scripts: the MCP tools are the mechanism.
2. Merge it to `main` through a PR, then open Skill Studio (`vskill studio`) headless on the vskill checkout and publish through the Publish drawer. Reconcile any earlier submission first.
3. When the release owner reports 1.0.100 installed, `vskill install anton-abyzov/vskill/project-wake --global --agent claude-code --agent codex` (it reads SKILL.md from GitHub main; a non-interactive install without `--agent` picks Claude Code only), then check the composer `/` list and run it once in a coordinator.

Rejected: a SpecWithCode server feature (bigger, and automatic continuation already exists); a SpecWeave `sw-` skill (it orchestrates SpecWithCode threads, not increments); scheduled invocation (user wants manual).

Risk: the coordinator composer may list only certain skill sources; the composer research decides the install target.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Name → `project-wake`, command `/project-wake` (coordinator recommendation; short, says what it does).
- D-02 Install scope → global on the M4 for every detected agent (`vskill install --global`), so Claude Code (`~/.claude/skills`) and Codex coordinators (`~/.agents/skills`, `~/.codex/skills`) both have it. Anton's coordinator runs Codex GPT-6.1-Sol (skills owner thread, October 27, 2026).
- D-04 Model invocation stays enabled → a typed `/project-wake` in a coordinator reaches the model as text after the prepended project context, and Codex reaches skills by mention; the description is narrowed to explicit requests instead.
- D-03 Home → `anton-abyzov/vskill` `plugins/productivity`, next to Anton's other personal skills.
### Open
- none

## Tasks

### T-01 Write the project-wake skill
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: vskill `plugins/productivity/skills/project-wake/SKILL.md`, `plugins/productivity/skills/project-wake/evals/evals.json` | Test: `vskill scan plugins/productivity/skills/project-wake/SKILL.md`

### T-02 Merge and publish through Skill Studio
- AC: AC-07 | Files: vskill PR | Test: `vskill find project-wake` lists `anton-abyzov/vskill/project-wake`

### T-03 Install globally after 1.0.100 and verify the coordinator slash command
- AC: AC-08 | Files: none | Test: `ls ~/.claude/skills/project-wake/SKILL.md ~/.agents/skills/project-wake/SKILL.md` and a coordinator run of `/project-wake`
- Expected per installed build (1093 owner, October 27, 2026). Without specwithcode-dev #881 (1.0.99, 1.0.100): the `/` row reads `/skill:Project Wake` and a pick inserts `$project-wake`; typed `/project-wake` runs in a Claude coordinator, is plain text in Codex. With #881: the row reads `$project-wake` with a "Personal" badge; typed `/project-wake` runs in Claude and in Codex. `~/.claude/skills` plus `~/.agents/skills` covers Claude Code, Codex and Copilot.

### T-04 Verify and close 1091
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: `specweave verify 1091-create-project-wake-skill`
