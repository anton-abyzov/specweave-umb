# studio-code MCP tool surface: core tools up front, search hints, SpecWeave toolkit

## Problem

Every SpecWithCode thread gets all 171 studio-code tools, and Claude Code loads them all deferred. The six tools an agent needs on most turns (`ask_user`, `request_secret`, `studio_thread_send`, `delegate_task`, `studio_report_save`, `advisor`) cost a ToolSearch round trip each time, and the other 165 carry no search hint, so tool search matches them on name and description alone. Effect 4.0.1's `McpSchema.Tool` already has `_meta`; we set none.

Claude Code 2.1.331 sends `server/discover` before `initialize` to every HTTP MCP server, including studio-code (`research/07-live-probe.md`). Nobody had measured what that costs a thread.

Agents call SpecWeave by reading the sw-* skills and running the `specweave` CLI in a shell. Inside SpecWithCode the agent already has a studio-code connection that knows its thread and workspace, but there are no SpecWeave tools on it.

Nobody has listed which studio-code tools refuse a worker (non-coordinator) credential. A later per-role tool-list increment needs that list.

**Rescoped November 25, 2026** by the lead after an adversarial GPT-6.2 Sol critique of the plan: the SpecWeave toolkit is read-only here (`pickup --no-apply` still fetches and moves a Git ref, `task done` can run a command, auto-claim and commit, `verify` runs project commands and writes reports); `_meta` keys ship only where a measurement supports them; an access gap the audit finds is fixed at call time now.

## Scope

In: `anthropic/alwaysLoad` on the core tools a measurement supports, and `anthropic/searchHint` only if a live recall test shows a gain; the measurement itself (startup, time to first useful call, context cost) on the installed Claude Code CLI and the SDK's bundled CLI; the `server/discover` cost, measured; a read-only report of worker refusals, with a call-time fix for any tool a worker can call that it must not; a read-only `specweave` toolkit (`specweave_task_status`, `specweave_next_task`), listed only to threads whose registered worktree has `.specweave/`; a headless proof from Claude, Codex and Copilot.

Out: SpecWeave write tools (task done, verify, pickup; see Follow-ups), protocol 2026-07-28 and `server/discover` answering, per-role tool lists, the Tasks extension, skills served from the server, OAuth (`apps/server/src/auth/McpOAuth.ts` stays untouched), any change to a skill.

## Acceptance Criteria

- [ ] AC-01: `_meta["anthropic/alwaysLoad"]: true` is set only on the tools, from `ask_user`, `request_secret`, `studio_thread_send`, `delegate_task`, `studio_report_save` and `advisor`, whose measured first-use friction supports it; `_meta["anthropic/searchHint"]` ships only if a live recall test shows better recall under a rule fixed before the runs. Startup, time to first useful call and context cost are measured on the installed Claude Code CLI and the SDK's bundled CLI, in `reports/`. A test reads a real HTTP `tools/list` response from the full server layer, so tools added through the normal `registerToolkit` path are covered, and asserts the keys on exactly the chosen set. Provider bridges that re-serve the tool list are checked. No Effect patch or bump.
- [ ] AC-02: What Claude Code's `server/discover` probe costs a Claude thread's studio-code connection (thread start to first studio-code tool list) is measured; if studio-code answers it slower than an immediate JSON-RPC "method not found", it is made to answer at once. Before/after numbers are in `reports/`.
- [ ] AC-03: A report in `reports/` lists, for each studio-code tool, whether a worker (non-coordinator) credential is refused today when calling it. Where it finds a tool a worker can call that a stated rule (a tool description or recorded decision) says it must not, that call-time check is fixed with a refusal test; a "must not" that would be new policy goes to the owner. Role-filtered listings wait.
- [ ] AC-04: Toolkit `apps/server/src/mcp/toolkits/specweave/` adds two read-only tools: `specweave_task_status` (an increment's tasks and states, `specweave task list --json`) and `specweave_next_task` (a local-only view of the next task, `specweave task next --json`: no fetch, no ref update, no claim, no write). They read files in the calling thread's registered worktree only and refuse a thread without one and any folder outside it. They are listed only when that worktree has `.specweave/`, and refused otherwise. A snapshot test on a scratch worktree shows the CLI commands they run change no file and no Git ref.
- [ ] AC-05: The SpecWeave tools work from a Claude, a Codex and a Copilot (ACP) thread with no per-provider configuration, through the existing studio-code injection. One headless call per provider proves it; results in `reports/`.
- [ ] AC-06: No skill is changed or deprecated in this increment.

## Approach

**AC-01.** `apps/server/src/mcp/McpToolMeta.ts` holds the chosen always-load set (and hints, if kept) and a registration wrapper that sets `_meta` as each tool is added; `McpHttpServer.ts` applies it in `toolkitRegistration` and `imageToolRegistration`, so every tool passes through it. The measurement uses a logging proxy in front of the live endpoint that injects `_meta` per condition and stubs every `tools/call` (no real card, delegation or message), with Claude Code 2.1.331 and the SDK's bundled CLI. Bridges: Claude, Cursor and ACP agents (Copilot) connect to studio-code over HTTP themselves; only Pi's extension (`piStudioMcpExtensionSource.ts`) re-serves the list, and Pi does not read `anthropic/*` keys.

**AC-02.** Measured on M5 with a logging proxy between Claude Code 2.1.331 (`claude -p`, Haiku 5.5) and the live studio-code endpoint, 6 runs passing the server's own answer through and 5 runs where the proxy answers `server/discover` itself with -32601. studio-code already answers in about 3 ms (HTTP 400, JSON-RPC -32022 "Unsupported protocol version", from Effect's runtime before any tool code), and Claude Code falls back to `initialize` within about 6 ms. Spawn to tool list: 188 ms median against 198 ms for the -32601 control. No code change is needed; the report records both runs.

**AC-03.** Read-only analysis of the access declarations (`McpToolAccess.ts`, `threadAccess.ts`, `workGrantAccess.ts`) and handler checks, one row per tool with file:line, diffed against the 171 names from a live `tools/list`. The candidates it leaves open (`studio_model_preference`, `studio_project_connection_call`, a worker changing the coordinator's thread) are judged against stated rules; a fix goes in the tool's handler with a test.

**AC-04.** `apps/server/src/mcp/toolkits/specweave/`:

- `tools.ts`: two tools, inputs `increment` (number or folder name, strict pattern) and an optional `folder` inside the worktree. Fixed argument lists; nothing from the caller reaches the CLI but the validated increment.
- `workspace.ts`: the caller's registered worktree (`thread.worktreePath`), real path; a thread without one, or whose worktree is missing, is refused, never given the project folder. `folder` must resolve inside it and hold `.specweave/`.
- `cli.ts`: resolves `specweave` like an agent's shell does, runs it through `ProcessRunner` with an argument array, `--workspace <root>`, `NO_COLOR`, a timeout and an output cap.
- `handlers.ts`: both tools read as the caller (`readsAsCaller`). `next_task` runs with SpecWithCode's own SpecWeave identity, so the caller's live claims are returned beside it (from `task list`) instead of being matched to the caller.
- Listing: `apps/server/src/mcp/McpToolVisibility.ts` rewrites a `tools/list` response after auth to drop `specweave_*` unless the caller is a thread whose registered worktree has `.specweave/`; any lookup failure hides them.
- Both join the read-only allowlist (`claudeReadOnlyMcpTools.ts`).

**AC-05.** After the release is installed on M5 (installing restarts this thread's host), one live headless thread each on Claude, Codex and Copilot calls `specweave_task_status` for this increment, and the reply is saved. Copilot cannot be checked on an isolated server (ACP agents show unavailable there), so the proof uses live threads.

**AC-06.** `git diff --name-only origin/main -- '*skills*' '*SKILL.md'` is empty in the app repository, and no umbrella skill file changes.

Risks: the `tools/list` rewrite parses each list response (about 170 tools, tens of KB) on the server. A Claude thread in plan mode can call the two SpecWeave tools without approval; both run read-only CLI commands.

## Follow-ups

- **SpecWeave write tools** (`task_done`, `verify`, `pickup`), a later increment, gated on: the calling thread's registered worktree; its assigned increment and task; the task's current claim held by that thread; the thread's execution permissions (no plan mode, no approval-required run without approval); verify through the heavy-checks gate (`specweave-studio checks run`); no arbitrary commands (`--cmd`, `--run` never passed); idempotent retries (a repeated done with the same evidence is a no-op).
- Role-filtered tool listings.
- From the delta review of `fd1d0d3fe` (both low, accepted at merge):
  - Links inside `.specweave/` are not checked. `workspace.ts` real-paths only the `.specweave` entry, so an `increments` link into another checkout is still read. Real-path the files the CLI reads, or have the CLI refuse links out of `--workspace`.
  - The `tools/list` pre-check in `McpToolVisibility.ts` misses a method written with a JSON-escaped slash (`tools\/list`), so such a list goes out unfiltered. The handlers still refuse the call. Fix: also parse a body that contains a backslash.
- Run the real `specweave task list|next` in CI against a scratch worktree, so a CLI release that adds a write fails a test.

## Decisions

### Asked
- D-01 Scope and ACs → given by the owner in the task (November 24, 2026); rescoped by the lead (November 25, 2026): read-only toolkit, measured `_meta`, access fixes now.
### Defaulted (change any before sw-do)
- D-02 The SpecWeave tools read only the thread's registered worktree; a thread with no worktree (a project without "Use worktrees") is refused rather than given the project folder → default, the lead's wording; it can be relaxed later.
- D-03 AC-02 needs no code change: studio-code already answers `server/discover` in about 3 ms with a modern error, and Claude Code falls back at once → default.
- D-04 `specweave_next_task` reports the CLI's next task for SpecWithCode's identity plus the live claims, instead of impersonating the caller's SpecWeave agent id → default.
- D-05 AC-05 is proven after the release is installed on M5, with live threads → default.
### Open
- none

## Tasks

### T-01 Always-load (and hint) `_meta` on the measured set
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolMeta.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolMeta.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpFullLayer.testkit.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/McpToolMeta.test.ts

### T-02 Measure the server/discover probe
- AC: AC-02 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/discover-probe.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/discover-probe.md

### T-03 Worker refusal report
- AC: AC-03 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/worker-refusal-matrix.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/worker-refusal-matrix.md

### T-04 Read-only SpecWeave toolkit
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/workspace.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/cli.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/handlers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/workspace.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/claudeReadOnlyMcpTools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/studioReadOnlyTools.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/specweave

### T-05 List the SpecWeave tools only in SpecWeave worktrees
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolVisibility.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolVisibility.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpFullLayer.testkit.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/McpToolVisibility.test.ts

### T-06 Claude, Codex and Copilot call the SpecWeave tools
- AC: AC-05 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/provider-proof.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/provider-proof.md

### T-07 No skill changed
- AC: AC-06 | Files: none | Test: cd repositories/anton-abyzov/specwithcode && test -z "$(git diff --name-only origin/main -- '*skills*' '*SKILL.md')"

### T-08 Measure tool search: alwaysLoad friction and hint recall
- AC: AC-01 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/tool-search.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/tool-search.md

### T-09 Fix worker access gaps the audit found
- AC: AC-03 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/worker-access-fixes.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/worker-access-fixes.md

### T-10 Prove the CLI commands are read-only
- AC: AC-04 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/specweave-read-only.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/specweave-read-only.md
