# SpecWeave ledger tools: claim, release and block for the thread that owns the increment

## Problem

Increment 1483 gave studio-code two read-only SpecWeave tools (`specweave_task_status`, `specweave_next_task`). To change a task's state an agent still runs `specweave task claim|release|block` in its shell, so a thread that has studio-code but a restricted shell (plan mode, an approval-required run, a provider whose shell policy drops SpecWeave's variables) cannot take or hand back a task at all.

The reviews that shaped 1483 drew the line for write tools. GPT-6.2 Sol (`06-critique-sol.md` item 3): `pickup` fetches and moves a Git ref, `task done` can run a command, auto-claim and commit, `verify` runs project commands and writes reports. Fable 5.2 (`08-fable-review.md` item 8): do not build the write tools as planned; the recommended ceiling is ledger-only with an ownership check. The owner approved that ceiling on November 26, 2026.

The same Fable reviewer saw a linux-mini thread list no `specweave_*` tools. Nobody has said why.

## Scope

In: three studio-code tools that append to one increment's ledger through the SpecWeave CLI's own ledger commands (`task claim`, `task release`, `task block`); an ownership check that ties each call to the calling thread's assigned increment inside its registered worktree; idempotent retries; a headless proof from Claude and Codex threads, and a Copilot attempt; the linux-mini finding.

Out: `task done`, `verify`, `pickup`, `skip` and any tool that runs a command, commits, pushes or fetches; changing who may call which tool beyond these three (the three open policy questions in 1483 `worker-access-fixes.md` stay open); relaxing 1483's D-02 (a thread without a worktree gets no SpecWeave tools); any skill.

## Acceptance Criteria

- [ ] AC-01: Three tools, `specweave_task_claim`, `specweave_task_release` and `specweave_task_block` (with a required reason), change only the named increment's bookkeeping through `specweave task claim|release|block`. Each run is an argument array with `--no-commit` and `--json`, never `--force`, `--all-mine` or `--run`; only a validated increment, task id and reason reach it. No tool starts a shell, commits, pushes, fetches or moves a Git ref: a test with the real CLI on a scratch repository whose `.specweave/config.json` turns `git.autoCommitIncrement` and `git.autoPushIncrement` on shows HEAD, every ref and the index unchanged, and only that increment's `ledger.jsonl` and `metadata.json` changed.
- [ ] AC-02: A call is refused, with the reason in the refusal, unless all hold: the caller is a SpecWithCode thread with a live run; its registered worktree exists and holds `.specweave/config.json`; the increment is the thread's assigned one (linked by hand, seeded at launch, bound by the thread's own ledger write or worktree branch) or one whose `spec.md` the thread wrote itself; and the increment folder and its `ledger.jsonl` and `metadata.json` resolve (real path) inside that worktree. A coordinator is held to the same rules with no bypass, and an outside MCP client is refused.
- [ ] AC-03: Retries are idempotent. Claiming a task the caller already holds succeeds and writes no ledger event; blocking a task the caller already blocked with the same reason, or releasing a task that nobody holds, does the same. A task another agent or another live thread holds is refused with the holder named (the ledger's `by`, and the thread when SpecWithCode knows it). Two calls at once on one increment cannot both write.
- [ ] AC-04: No `task_done`, `verify` or `pickup` tool exists, and this spec records why under Decisions.
- [ ] AC-05: The tools work from a Claude and a Codex thread with no per-provider setup: one headless live thread per provider claims, re-claims, blocks and releases a proof task, and the ledger shows exactly one event per change, written as the same agent id the thread's own shell gets from `specweave task whoami`. Copilot (ACP) is tried the same way and its result recorded either way. Evidence in `reports/provider-proof.md`.
- [ ] AC-06: No skill changes: `git diff --name-only origin/main` in the app repository lists no `skills/` or `SKILL.md` path, and no umbrella skill file changes.
- [ ] AC-07: `reports/linux-mini-tools.md` says, with evidence, why the linux-mini thread listed no `specweave_*` tools, and either the fix shipped here or why none is needed.

## Approach

All app code is in `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/`.

**Identity (`identity.ts`).** SpecWeave writes `by` as `SPECWEAVE_AGENT`, else `<SPECWEAVE_TOOL>@<host>` (`getAgentId`). SpecWithCode gives each thread's process `SPECWEAVE_TOOL` and `SPECWEAVE_STUDIO_THREAD_ID` (`specweaveAgentEnvironment`, `RuntimeInstructions.ts`). A write must be recorded as the same agent the thread's shell is, or the agent's own `specweave task done` would see the claim as someone else's. So the write runs with the caller's `specweaveAgentEnvironment`: the tool slug comes from the caller's provider instance the way the adapters pick it (`claudeAgent` is `claude`, `codex` is `codex`, `opencode`, `pi`, an ACP registry agent through `specweaveToolForAcpAgent`), and a provider whose slug is not known is refused rather than guessed. `SPECWEAVE_AGENT` is left to the server environment the agents inherit, and session ids are blanked so no session marker is written. The handler asks the CLI who it will write as (`task whoami --json` in the same environment) and compares holders against that.

**CLI (`cli.ts`).** `runSpecweave` takes the environment per call: reads keep the fixed view agent, writes pass the caller's identity. The write commands are fixed: `task claim <T> <inc> --no-commit --json`, `task release <T> <inc> --no-commit`, `task block <T> <inc> --reason=<text> --no-commit`. `--workspace` stays, so the CLI never walks out of the worktree.

**Ownership (`ownership.ts`).** The thread's increment comes from `ThreadIncrementProgressService.read`, the same source as its plan card, restricted to the strong bindings (`manual`, `claim`, `branch`; a written spec is reported as `claim`). The weak `name` and `checkpoint` bindings do not count. The requested increment must equal the bound one (number or folder name). Then the worktree from 1483's `resolveCallerWorkspace` and real paths: the increment folder, `ledger.jsonl` and `metadata.json` must lie inside the real worktree, which closes 1483's open follow-up about an `increments` link into another checkout for writes. No check reads the caller's role.

**Handlers (`ledgerHandlers.ts`).** Each call takes a per-increment lock, folds state with `task list --json`, and decides:

| Tool | Already in the wanted state as the caller | Held by another agent or thread | Otherwise |
|---|---|---|---|
| claim | success, no event | refused, holder named | `task claim` |
| block | same reason: success, no event | refused, holder named | `task block` |
| release | open, done or skipped: success, no event | refused, holder named | `task release` |

"Another thread" covers two threads that share an agent id (two Claude threads on one machine, or a delegated child in its parent's checkout): another live thread of the project whose SpecWeave binding file names this worktree, increment and task, with the claim's time, holds it. The CLI's own checks (earliest live claim wins, Files overlap, unmet dependencies, template tasks) stay in force and their refusals pass through. Results carry `changed`, the task's state after the call, the agent id and the command that ran (or null).

**Access.** The tools are `actsAsCaller` (a thread with a live run; read-only clients and advisor threads refused), `Tool.Readonly` false, and stay off `claudeReadOnlyMcpTools.ts`, so Claude plan mode asks before a call. Listing follows 1483: only where the worktree holds `.specweave/`.

**Side effects, stated.** Besides `ledger.jsonl`, the CLI's claim moves `metadata.json` from planned to active and refreshes `metadata.repositories`, every append touches `metadata.updated`, and SpecWeave writes the caller's binding file `~/.specweave/studio/threads/<thread>.json` (outside the repository; that is what the plan card follows). Nothing else.

**Proof (AC-05).** After the release is installed on M5, a Claude, a Codex and a Copilot thread are each launched with `increment` set to this one, in a worktree that holds it, and work one proof task (T-09): claim, claim again, block, block again, release. Their replies and the ledger lines go in `reports/provider-proof.md`.

Risks: the binding-file check names a thread only for the claim it last made; an earlier claim by a sibling thread with the same agent id reads as the caller's own (the CLI would treat it the same way). A Claude thread in plan mode is asked before each call; that is intended.

## Decisions

### Asked
- D-01 Write tools ceiling → ledger only (claim, release, block) with an ownership check, no done, verify or pickup (owner, November 26, 2026).

### Defaulted (change any before sw-do)
- D-02 Why no `task_done`, `verify` or `pickup` tool → `pickup` fetches and moves a Git ref, `task done` can run a command (`--run`), auto-claim and commit, `verify` runs the project's commands and writes reports (Sol review, item 3; Fable review, item 8). Agents keep the CLI for those under their own permission mode, where the provider's approvals apply.
- D-03 Assigned increment → manual link, launch seed, the thread's own ledger write or `inc/NNNN-*` branch, or a spec the thread wrote; never a number in the title or a session checkpoint.
- D-04 Identity → the caller's own SpecWeave agent id (`<tool>@<host>`), not a per-thread id, so the agent's shell and the tools agree on who holds a task. A provider with no known slug is refused.
- D-05 `skip` is left out: it is terminal and finishes tasks, closer to `done` than to a claim.
- D-06 The real-CLI test runs where a `specweave` command is installed and is skipped elsewhere (CI has none today); the run on M5 is recorded in `reports/`.

### Open
- none

## Tasks

### T-01 Write identity and the CLI write runner
- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/identity.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/identity.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/cli.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/specweave/identity.test.ts

### T-02 Ownership check
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/ownership.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/ownership.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/specweave/ownership.test.ts

### T-03 The three ledger tools, idempotent, through the full layer
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/ledgerHandlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/ledgerHandlers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/fullLayer.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpFullLayer.testkit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/studioReadOnlyTools.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/specweave apps/server/src/mcp/studioReadOnlyTools.test.ts

### T-04 Real CLI: no commit, push or ref change
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/realCli.test.ts, .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/reports/real-cli.md | Test: test -s .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/reports/real-cli.md

### T-05 Record why there is no done, verify or pickup tool
- AC: AC-04 | Files: .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/spec.md | Test: grep -q "D-02 Why no" .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/spec.md

### T-06 Live proof from Claude, Codex and Copilot threads
- AC: AC-05 | Files: .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/reports/provider-proof.md | Test: test -s .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/reports/provider-proof.md

### T-07 No skill changed
- AC: AC-06 | Files: none | Test: cd repositories/anton-abyzov/specwithcode && test -z "$(git diff --name-only origin/main -- '*skills*' '*SKILL.md')"

### T-08 Why linux-mini listed no SpecWeave tools
- AC: AC-07 | Files: .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/reports/linux-mini-tools.md | Test: test -s .specweave/increments/1497-specweave-ledger-tools-claim-release-block-for-the-owning-thread/reports/linux-mini-tools.md

### T-09 Proof task for the provider threads
- AC: AC-05 | Files: none | Test: true
