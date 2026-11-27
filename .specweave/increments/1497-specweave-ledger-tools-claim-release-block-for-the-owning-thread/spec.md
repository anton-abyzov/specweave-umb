# SpecWeave ledger tools: claim, release and block for the thread that owns the increment

## Problem

Increment 1483 gave studio-code two read-only SpecWeave tools (`specweave_task_status`, `specweave_next_task`). To change a task's state an agent still runs `specweave task claim|release|block` in its shell, and nothing checks that the increment is the thread's own: a shell claim lands in whatever ledger the agent points it at. studio-code already knows the calling thread, its registered worktree and the increment it was launched with or linked to, so it can offer the same three ledger moves with that check built in, for any provider, without a shell command.

The reviews that shaped 1483 drew the line for write tools. GPT-6.2 Sol (`06-critique-sol.md` item 3): `pickup` fetches and moves a Git ref, `task done` can run a command, auto-claim and commit, `verify` runs project commands and writes reports. Fable 5.2 (`08-fable-review.md` item 8): do not build the write tools as planned; the recommended ceiling is ledger-only with an ownership check. The owner approved that ceiling on November 26, 2026.

The same Fable reviewer saw a linux-mini thread list no `specweave_*` tools. Nobody has said why.

## Scope

In: three studio-code tools that append to one increment's ledger through the SpecWeave CLI's own ledger commands (`task claim`, `task release`, `task block`); an ownership check that ties each call to the calling thread's assigned increment inside its registered worktree; idempotent retries; a headless proof from Claude and Codex threads, and a Copilot attempt; the linux-mini finding.

Out: `task done`, `verify`, `pickup`, `skip` and any tool that runs a command, commits, pushes or fetches; changing who may call which tool beyond these three (the three open policy questions in 1483 `worker-access-fixes.md` stay open); relaxing 1483's D-02 (a thread without a worktree gets no SpecWeave tools); any skill.

## Acceptance Criteria

- [ ] AC-01: Three tools, `specweave_task_claim`, `specweave_task_release` and `specweave_task_block` (with a required reason), change only the named increment's bookkeeping through `specweave task claim|release|block`. Each run is an argument array with `--no-commit` and `--json`, never `--force`, `--all-mine` or `--run`; only a validated increment, task id and reason reach it. No tool starts a shell, commits, pushes, fetches or moves a Git ref: a test with the real CLI on a scratch repository whose `.specweave/config.json` turns `git.autoCommitIncrement` and `git.autoPushIncrement` on shows HEAD, every ref and the index unchanged, and only that increment's `ledger.jsonl` and `metadata.json` changed.
- [ ] AC-02: A call is refused, with the reason in the refusal, unless all hold: the caller is a SpecWithCode thread with a live run in full-access mode (owner, D-13); its registered worktree exists and holds `.specweave/config.json`; the increment is the thread's assigned one (linked by hand, seeded at launch, bound by the thread's own ledger write or worktree branch) or one whose `spec.md` the thread wrote itself; and the increment folder and its `ledger.jsonl` and `metadata.json` resolve (real path) inside that worktree. A coordinator is held to the same rules with no bypass, and an outside MCP client is refused.
- [ ] AC-03: Retries are idempotent. Claiming a task the caller already holds succeeds and writes no ledger event; blocking a task the caller already blocked with the same reason, or releasing a task that nobody holds, does the same. A task another agent or another live thread holds is refused with the holder named (the ledger's `by`, and the thread when SpecWithCode knows it). Two calls at once on one increment cannot both write.
- [ ] AC-04: No `task_done`, `verify` or `pickup` tool exists, and this spec records why under Decisions.
- [ ] AC-05: The tools work from a Claude and a Codex thread with no per-provider setup: one headless live thread per provider claims, re-claims, blocks and releases a proof task, and the ledger shows exactly one event per change, written as the same agent id the thread's own shell gets from `specweave task whoami`. Copilot (ACP) is tried the same way and its result recorded either way. Evidence in `reports/provider-proof.md`.
- [ ] AC-06: No skill changes: `git diff --name-only origin/main` in the app repository lists no `skills/` or `SKILL.md` path, and no umbrella skill file changes.
- [ ] AC-07: `reports/linux-mini-tools.md` says, with evidence, why the linux-mini thread listed no `specweave_*` tools, and either the fix shipped here or why none is needed.

## Approach

All app code is in `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/`.

**Identity (`identity.ts`).** SpecWeave writes `by` as `SPECWEAVE_AGENT`, else `<SPECWEAVE_TOOL>@<host>` (`getAgentId`). SpecWithCode gives each thread's process `SPECWEAVE_TOOL` and `SPECWEAVE_STUDIO_THREAD_ID` (`specweaveAgentEnvironment`, `RuntimeInstructions.ts`). A write must be recorded as the same agent the thread's shell is, or the agent's own `specweave task done` would see the claim as someone else's. So the write runs with the caller's `specweaveAgentEnvironment`: the tool slug comes from the caller's provider instance the way the adapters pick it (`claudeAgent` is `claude`, `codex` is `codex`, `opencode`, `pi`, an ACP registry agent through `specweaveToolForAcpAgent`), and a provider whose slug is not known is refused rather than guessed. `SPECWEAVE_AGENT` and `SPECWEAVE_HOST` come from the provider instance's own environment settings when it sets them (the thread's shell gets them the same way) and otherwise from the server environment the agents inherit, and session ids are blanked so no session marker is written. The handler asks the CLI who it will write as (`task whoami --json` in the same environment) and compares holders against that.

**CLI (`cli.ts`).** `runSpecweave` takes the environment per call: reads keep the fixed view agent, writes pass the caller's identity. The write commands are fixed: `task claim <T> <inc> --no-commit --json`, `task release <T> <inc> --no-commit --json`, `task block <T> <inc> --reason=<text> --no-commit --json` (`--json` also skips the CLI's start-up duplicate scan). SpecWeave 3.2 fixes a block reason's spacing as it writes it (runs of whitespace become one space and a space is added after `,` and `;`, never inside backtick code, URLs or paths); `reasonText.ts` is a copy of that rule. The tools send the reason already in that written form, so SpecWeave 3.1 (which only trims) and 3.2 store the same text, and a retry is the same reason only when its written form equals the recorded one exactly (or, for a block typed in a shell on 3.1, the trimmed text). A retry with other spacing appends nothing; any other difference, including spacing inside code, is a new block. On Windows an npm-installed `specweave` is a `.cmd` that runs through cmd.exe, so the write tools refuse to run there unless `specweave` resolves to a program that starts without a shell (D-12). The check runs before the call and again in `runSpecweave` for every write it spawns. `--workspace` stays, so the CLI never walks out of the worktree.

**Ownership (`ownership.ts`).** The thread's increment comes from `ThreadIncrementProgressService.read`, the same source as its plan card, restricted to the strong bindings (`manual`, `claim`, and `branch` only when the thread's branch is `inc/NNNN-*` for that increment; a written spec is reported as `claim`). The weak `name` and `checkpoint` bindings, and a `branch` binding found only because an old ledger line names the branch, do not count. The requested increment must equal the bound one (number or folder name). There is one copy to write: the bound copy when it lies inside the worktree (a nested SpecWeave folder included, its root read from the recorded path and required to hold that very folder, so a link to a same-named increment elsewhere is refused; a binding recorded inside the worktree that fails this check is refused, never swapped for the root copy). SpecWeave's binding file for the thread is read as well: when it puts this increment in a copy inside the worktree, the write goes to that copy or nowhere, so a nested copy that was removed or replaced is refused even where the progress reader has moved on to the root copy., else the copy at the worktree's own SpecWeave folder; a `folder` naming any other copy is refused. Then the paths, from 1483's `resolveCallerWorkspace` on: `.specweave`, `increments`, the increment folder and `.specweave/state` must be real folders (no link, not even one inside the worktree) inside the real worktree, and `ledger.jsonl`, `metadata.json`, `spec.md` and `state/active-increment.json` must be absent or plain files with one hard link and no leftover `<file>.tmp` (the CLI writes through that name). This closes 1483's open follow-up about an `increments` link into another checkout for writes. The paths are checked again under the lock just before the CLI runs. No check reads the caller's role.

**Handlers (`ledgerHandlers.ts`).** Each call takes a per-increment lock, folds state with `task list --json`, and decides:

| Tool | Already in the wanted state as the caller | Held by another agent or thread | Otherwise |
|---|---|---|---|
| claim | success, no event | refused, holder named | `task claim` |
| block | same reason: success, no event | refused, holder named | `task block` |
| release | open, done or skipped: success, no event | refused, holder named | `task release` |

"Another thread" covers two threads that share an agent id (two Claude threads on one machine, or a delegated child in its parent's checkout). With no other live thread in the checkout a hold under the caller's id is the caller's. Otherwise it needs proof: these tools wrote that hold for a thread (kept in memory by increment folder, task and claim time), or a thread's SpecWeave binding file names this worktree, increment, task and time. Without proof the call is refused and the checkout's threads are named, so one thread never takes or releases a sibling's task. Siblings are the project's live threads whose recorded or real worktree path is the caller's (an alias with another name counts); when that list cannot be read the call is refused rather than treated as empty. The CLI's own checks (earliest live claim wins, Files overlap, unmet dependencies, template tasks) stay in force and their refusals pass through. Results carry `changed`, the task's state after the call, the agent id and the command that ran (or null).

**Access.** Only a thread in full-access mode, during one of its own turns, may call them (D-13). The thread must have an active run, and both its saved runtime mode and the mode its running turn started with (`startedModes` on the run's active attempt) must be full-access: a mode switched mid-turn reaches the provider only on the next turn, so a turn started sandboxed stays refused, and a mode that cannot be read is refused. A call between turns is refused too. The tools are `actsAsCaller` (read-only clients and advisor threads refused), `Tool.Readonly` false, and stay off `claudeReadOnlyMcpTools.ts`, so Claude plan mode asks before a call. Listing follows 1483: only where the worktree holds `.specweave/`.

**Side effects, stated.** Besides `ledger.jsonl`, the CLI's claim moves `metadata.json` from planned to active and refreshes `metadata.repositories`, every append touches `metadata.updated`, and SpecWeave writes the caller's binding file `~/.specweave/studio/threads/<thread>.json` (outside the repository; that is what the plan card follows). Nothing else.

**Proof (AC-05).** After the release is installed on M5, a Claude, a Codex and a Copilot thread are each launched in full-access mode with `increment` set to this one, in a worktree that holds it, and work one proof task (T-09): claim, claim again, block, block again, release. Their replies and the ledger lines go in `reports/provider-proof.md`.

Risks: the CLI opens names and follows links, so the check narrows but cannot close the moment between the last check and the CLI's own write: a process that swaps a file in exactly that moment (in practice the thread's own shell, in its own worktree) could still redirect one write (D-10). After a server restart the in-memory record is gone, so in a checkout shared by several threads an older hold the binding files no longer name is refused until its holder uses the shell; a single-thread checkout is not affected. A Claude thread in plan mode is asked before each call; that is intended.

## Decisions

### Asked
- D-01 Write tools ceiling → ledger only (claim, release, block) with an ownership check, no done, verify or pickup (owner, November 26, 2026).
- D-13 Which threads may call them → only threads in full-access mode (owner, November 27, 2026, on review round 2). The server writes with more reach than a sandboxed agent has and the CLI follows links when it opens files, so a sandboxed agent racing its own worktree could reach past its sandbox through the server (D-10). A full-access agent can already write anywhere, so the race gives it nothing. Other threads are refused and pointed at `specweave task claim|release|block` in their shell.

### Defaulted (change any before sw-do)
- D-02 Why no `task_done`, `verify` or `pickup` tool → `pickup` fetches and moves a Git ref, `task done` can run a command (`--run`), auto-claim and commit, `verify` runs the project's commands and writes reports (Sol review, item 3; Fable review, item 8). Agents keep the CLI for those under their own permission mode, where the provider's approvals apply.
- D-03 Assigned increment → manual link, launch seed, the thread's own ledger write or `inc/NNNN-*` branch, or a spec the thread wrote; never a number in the title or a session checkpoint.
- D-04 Identity → the caller's own SpecWeave agent id (`<tool>@<host>`), not a per-thread id, so the agent's shell and the tools agree on who holds a task. A provider with no known slug is refused.
- D-05 `skip` is left out: it is terminal and finishes tasks, closer to `done` than to a claim.
- D-06 The real-CLI test runs where a `specweave` command is installed and is skipped elsewhere (CI has none today); the run on M5 is recorded in `reports/`.
- D-07 Approval modes → the write tools are not on the read-only lists (`claudeReadOnlyMcpTools.ts`, `STUDIO_READ_ONLY_TOOLS`), so each provider's own approval rule applies to them like any other change: Claude plan mode asks, an ACP permission request follows the thread's policy (`acpRequestDisposition`), a Codex MCP approval follows the thread's runtime mode.
- D-08 Two threads, one agent id → a hold counts as the caller's only with proof when another live thread shares the checkout (Approach); otherwise refused.
- D-09 A SpecWeave binding file counts as an assignment without a matching ledger event (review round 1, finding 3, declined in part). The launch seed has no event by design, and the file is written only by the CLI with the thread's own `SPECWEAVE_STUDIO_THREAD_ID` or by the launch. Forging it means setting another thread's id in a shell that can already write any ledger directly, and the forged binding only lets that other thread write inside its own worktree. The `branch` part of the finding is fixed (inc/NNNN branches only).
- D-10 Residual race, recorded (review round 1, finding 1; round 2 finding 3), and made harmless by D-13. Closing it fully needs the CLI to open its files without following links (`O_NOFOLLOW`, a temporary file created exclusively); that is a SpecWeave change (Follow-ups). Here: no link anywhere on the write paths, no second hard link, no leftover temporary file, checked again under the lock just before the write.
- D-11 Threads of other projects registered on the same checkout are not counted as siblings (review round 1, finding 4, in part). A worktree belongs to the project that made it; a second project registration of the same folder is not a setup SpecWithCode creates.
- D-12 Windows → the write tools never start a shell: when `specweave` resolves to a `.cmd` or `.bat` (an npm install) they refuse and point at the shell command (review round 1 finding 6, round 2 finding 5). Running the CLI's Node entry point directly from the shim is left for later; the read-only tools keep 1483's behaviour.

### Open
- none

## Follow-ups
- SpecWeave: write `ledger.jsonl`, `metadata.json`, `spec.md` and the state file without following links (open with `O_NOFOLLOW`, create the `.tmp` file exclusively in the verified folder), so the write tools' path check holds through the write itself (D-10).

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
