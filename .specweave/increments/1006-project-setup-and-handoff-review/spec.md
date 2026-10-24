# Project setup and handoff review

## Problem

The user asked for one review of every way a project starts and moves in SpecWithCode: a fresh install with no machines, a project from a local folder, a project cloned from a GitHub URL, connecting another machine to an existing small project, and handing a thread off to continue elsewhere. Each piece shipped in its own increment (0948-0951, 0966, 0967, 0969, 0979, #584 version check, #590 umbrella copy), and their evidence is scattered and of mixed strength: 0967's 77-check receipt is in-process peers before PR #550, 0966's two-server check predates later handoff fixes, and the related lanes have been idle and quota-failed since October 21. Nobody has walked the whole path end to end on the shipped 1.0.74 build with reproducible steps and screenshots, and earlier reports blur three different actions: viewing another machine's orchestrator, adding/linking/copying a project, and moving a thread's execution.

## Scope

In: an acceptance review of the shipped SpecWithCode 1.0.74 (installed binary and tag `v1.0.74`, `b0d364a90`) on disposable fixtures: isolated servers with their own `--base-dir`, scratch folders under `~/.specwithcode/m4/scratch/setup-handoff-review-20261023/`, a small public GitHub repository for cloning, a model-free agent for continuation turns; read-only observation of the real fleet; a step-by-step report with screenshots and a pass/fail/unverified verdict per scenario; small reversible fixes when a scenario cannot run, routed to the current owner when larger.

Out: granting worker access on any real machine, provisioning or credential changes, moving or archiving real projects or threads, physical two-Mac acceptance (needs a user grant), unsupported provider-cloud execution, a release unless a fix warrants one (then only through the sole release owner).

## Acceptance Criteria

- [ ] AC-01: A fresh isolated server on the installed 1.0.74 binary, with no projects and no machines, shows a usable first-run state: an empty project list with a way to add a project, and Settings > Connections with zero machines and an "Add a machine" path; headless screenshots and the server's own machine list prove it.
- [ ] AC-02: On that server a project created from a local folder records that folder as its workspace root, and a thread started in it runs with that folder as its working directory; a missing folder is refused with a clear message.
- [ ] AC-03: A project created from a GitHub URL clones a real public repository into the chosen folder, registers that clone, and a thread there sees the cloned files; an existing destination folder and an invalid URL each give a clear refusal.
- [ ] AC-04: With two isolated servers acting as two machines, an existing small project is connected to the second machine through the shipped path (Run on > add to machine, Link, or Copy files), and the destination records its own workspace root holding the project's files and shared project identity; view switching alone changes nothing on either machine.
- [ ] AC-05: Between the same two servers a thread is handed off and continues: the destination runs a new turn in its own workspace root with the handoff context, the source stops owning the thread, and a completed or user-stopped thread is not restarted.
- [ ] AC-06: Unavailable states are honest: an offline or unreachable machine, a machine without a worker grant, an incompatible version and a refused destination each show a specific reason instead of an empty list or a silent stand-in.
- [ ] AC-07: The real fleet is observed read-only (machine list, grant status, versions where readable); unreachable or ungranted machines are reported as unknown, and no grant, pairing, project or thread changes.
- [ ] AC-08: A step-by-step report with screenshots gives each scenario a pass, fail or unverified verdict, names its evidence class (source, unit, fixture, two-local-server, installed, real two-machine), exact versions and commits, defects found with their fix or owner, and the gates that remain.

## Approach

Build nothing new first. Reuse the shipped harnesses in `specwithcode-dev` at `v1.0.74` (`scripts/studio-logical-projects/`, `scripts/studio-fleet/add-to-machine-live.mjs`, `scripts/studio-folder-transfer/`, `scripts/verify-handoff-mode/`, `scripts/studio-workspaces/verify-installed.mjs`, `apps/web/tests/*` fixtures) and point them at the installed binary where they allow it; otherwise run the installed `specweave-studio serve --base-dir <scratch>` directly and drive it over its RPC/MCP surface, with headless Chromium (`headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`) for screenshots. Continuation turns use the model-free agent (`link-launch-agent.mjs`) so no account is billed.

Worktree: `~/.specwithcode/m4/worktrees/setup-handoff-review` (detached at `v1.0.74`). Evidence: `.specweave/increments/1006-project-setup-and-handoff-review/reports/`. Every server binds loopback on a free port with its own base dir; every process is stopped by its PID.

Risks: harnesses that require source builds or Tailscale proxies; the live service on this Mac must not be touched (no restart, no `statev2.sqlite` reads); PR #571 (0967 gaps) is open and conflicting, so handoff findings it already covers are routed there, not reimplemented.

## Decisions

### Asked
- none (the review request authorizes testing and routine reversible fixes)
### Defaulted (change any before sw-do)
- D-01 Build under test → installed 1.0.74 binary first, tag `v1.0.74` source harnesses second; `origin/main` (`252be2eb4`) only to check whether a finding is already fixed.
- D-02 Clone target → a tiny public repository (`https://github.com/octocat/Hello-World`); no private repositories or credentials.
- D-03 Real fleet → read-only; every machine without a grant is reported unverified, not provisioned.
- D-04 Handoff defects already listed in PR #571 → routed to that PR's owner, not duplicated.
### Open
- none

## Tasks

### T-01 Reconcile owners and map harnesses
- AC: AC-07 | Files: reports/owners.md | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/owners.md

### T-02 Fresh install, no machines
- AC: AC-01 | Files: reports/fresh/ | Test: ls .specweave/increments/1006-project-setup-and-handoff-review/reports/fresh/*.png

### T-03 Local folder project
- AC: AC-02 | Files: reports/local-folder/ | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/local-folder/result.json

### T-04 GitHub URL clone
- AC: AC-03 | Files: reports/clone/ | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/clone/result.json

### T-05 Connect a second machine to an existing project
- AC: AC-04 | Files: reports/connect/ | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/connect/result.json

### T-06 Thread handoff and continuation
- AC: AC-05 | Files: reports/handoff/ | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/handoff/result.json

### T-07 Unavailable and error states, real fleet read-only
- AC: AC-06, AC-07 | Files: reports/errors/, reports/fleet/ | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/errors/result.json

### T-08 Scenario report
- AC: AC-08 | Files: reports/setup-handoff-review.html | Test: test -s .specweave/increments/1006-project-setup-and-handoff-review/reports/setup-handoff-review.html

### T-10 Review and harden existing PR 644 harness labels
- AC: AC-08 | Files: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/.worktrees/fix-two-orchestrators-labels/scripts/studio-logical-projects/two-orchestrators.mjs, reports/astra-checkpoint.md | Test: node --check /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/.worktrees/fix-two-orchestrators-labels/scripts/studio-logical-projects/two-orchestrators.mjs

### T-11 Replace direct database fixture access and verify real clicks
- AC: AC-04, AC-08 | Files: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/.worktrees/fix-two-orchestrators-labels/scripts/studio-logical-projects/two-orchestrators.mjs, reports/safe-harness/ | Test: node --check /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/.worktrees/fix-two-orchestrators-labels/scripts/studio-logical-projects/two-orchestrators.mjs

### T-09 Verify and close 1006
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: specweave verify 1006
