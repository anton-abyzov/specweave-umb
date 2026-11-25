# studio-code MCP tool surface: core tools up front, search hints, SpecWeave toolkit

## Problem

Every SpecWithCode thread gets all 171 studio-code tools, and Claude Code loads them all deferred. The six tools an agent needs on most turns (`ask_user`, `request_secret`, `studio_thread_send`, `delegate_task`, `studio_report_save`, `advisor`) cost a ToolSearch round trip each time, and the other 165 carry no search hint, so tool search matches them on name and description alone. Effect 4.0.1's `McpSchema.Tool` already has `_meta`; we set none.

Claude Code 2.1.331 sends `server/discover` before `initialize` to every HTTP MCP server, including studio-code (`research/07-live-probe.md`). Nobody had measured what that costs a thread.

Agents call SpecWeave by reading the sw-* skills and running the `specweave` CLI in a shell. Inside SpecWithCode the agent already has a studio-code connection that knows its thread and workspace, but there are no SpecWeave tools on it.

Nobody has listed which studio-code tools refuse a worker (non-coordinator) credential. A later per-role tool-list increment needs that list.

## Scope

In: `_meta` hints on every studio-code tool; the `server/discover` cost, measured; a read-only report of worker refusals; a `specweave` toolkit on studio-code with four tools, listed only to threads whose workspace has `.specweave/`; a headless proof from Claude, Codex and Copilot.

Out: protocol 2026-07-28 and `server/discover` answering (brainstorm B-AC-03 to B-AC-06), per-role tool lists, the Tasks extension, skills served from the server, OAuth (`apps/server/src/auth/McpOAuth.ts` stays untouched), any change to a skill.

## Acceptance Criteria

- [ ] AC-01: Six tools carry `_meta["anthropic/alwaysLoad"]: true` (`ask_user`, `request_secret`, `studio_thread_send`, `delegate_task`, `studio_report_save`, `advisor`); every other tool carries `_meta["anthropic/searchHint"]` built from its toolkit name. A test asserts both appear in `tools/list` `_meta` for every registered tool. No Effect patch or bump.
- [ ] AC-02: What Claude Code's `server/discover` probe costs a Claude thread's studio-code connection (thread start to first studio-code tool list) is measured; if studio-code answers it slower than an immediate JSON-RPC "method not found", it is made to answer at once. Before/after numbers are in `reports/`.
- [ ] AC-03: A read-only report in `reports/` lists, for each studio-code tool, whether a worker (non-coordinator) credential is refused today when calling it. No behaviour change.
- [ ] AC-04: Toolkit `apps/server/src/mcp/toolkits/specweave/` adds `specweave_pickup` (next task), `specweave_task_status` (an increment's tasks and states), `specweave_task_done` (mark a task done with an evidence string) and `specweave_verify` (run verify for an increment, return the result). They wrap the installed `specweave` CLI and return structured JSON. They are listed only when the calling thread's workspace has `.specweave/`, and refused otherwise. They run in the caller's own workspace (its worktree when it has one, never the project's shared checkout) and refuse a folder outside it. Long verify runs send progress notifications and stop the process when the call is cancelled.
- [ ] AC-05: The SpecWeave tools work from a Claude, a Codex and a Copilot (ACP) thread with no per-provider configuration, through the existing studio-code injection. One headless call per provider proves it; results in `reports/`.
- [ ] AC-06: No skill is changed or deprecated in this increment.

## Approach

**AC-01.** New module `apps/server/src/mcp/McpToolMeta.ts`: the always-load set, a toolkit-key to search-hint table, a tool-name to toolkit-key lookup built from the toolkit definitions, and `withToolMeta`, a registration wrapper (same shape as `withAdvertisedSchemas`) that sets `_meta` on each tool as it is added. `McpHttpServer.ts` gets hook lines only: `toolkitRegistration` and `imageToolRegistration` apply the wrapper, so hand-registered image tools are covered too. Test against the full `layer`: every listed tool has exactly one of the two keys, and the six names exist.

**AC-02.** Measured on M5 with a logging proxy between Claude Code 2.1.331 (`claude -p`, Haiku 5.5) and the live studio-code endpoint, 6 runs passing the server's own answer through and 5 runs where the proxy answers `server/discover` itself with -32601. studio-code already answers in about 3 ms (HTTP 400, JSON-RPC -32022 "Unsupported protocol version", from Effect's runtime before any tool code), and Claude Code falls back to `initialize` within about 6 ms. Spawn to tool list: 188 ms median against 198 ms for the -32601 control. No code change is needed; the report records both runs.

**AC-03.** Read-only analysis of the access declarations (`McpToolAccess.ts`, `threadAccess.ts`, `workGrantAccess.ts`) and handler checks, one row per tool with file:line, diffed against the 171 names from a live `tools/list`.

**AC-04.** New folder `apps/server/src/mcp/toolkits/specweave/`:

- `tools.ts`: four tools. Inputs: `increment` (number or folder name, strict pattern), `task` (`T-NN`), `evidence` (up to 4,000 characters), an optional `folder` inside the workspace, and `timeoutMinutes` for verify. No `--cmd`, `--run` or `--force` is ever passed.
- `workspace.ts`: the caller's workspace by the same rule the session cwd uses (`RuntimePolicy.ts`: the thread's worktree when it has one, else the project folder). A recorded worktree that is missing is refused, never swapped for the project folder. Real paths only. `folder` must resolve inside the workspace and hold `.specweave/`.
- `cli.ts`: resolves `specweave` the way `SpecweaveSetup.ts` does (PATH plus the usual install folders), runs it through `ProcessRunner` with an argument array, `--workspace <root>`, `NO_COLOR`, a timeout and an output cap. Interrupting the call kills the process group (Effect's spawner kills `-pid`). Each result is one envelope: `ok`, `exitCode`, `command`, `workspace`, `data` (the CLI's JSON), `text` (capped). Long strings are cut.
- `handlers.ts`: `specweave_pickup` and `specweave_task_status` read as the caller (`readsAsCaller`); `specweave_task_done` and `specweave_verify` act as the caller (`actsAsCaller`: a thread caller with a live run, never a read-only client). Verify sends `notifications/progress` for each output line batch when the call carries a progress token. A spike on the real transport showed progress frames arrive live over SSE (3, 404, 806 ms, then the result) and a dropped connection interrupts the handler.
- Listing: a new `apps/server/src/mcp/McpToolVisibility.ts` rewrites a `tools/list` JSON response after auth to drop the `specweave_*` tools when the caller is not a thread whose workspace has `.specweave/`. It fails closed: any lookup failure hides them. One hook line in the auth middleware.
- `specweave_pickup` and `specweave_task_status` join the read-only allowlist (`claudeReadOnlyMcpTools.ts`); the other two do not.

**AC-05.** After the release is installed on M5 (installing restarts this thread's host), one live headless thread each on Claude, Codex and Copilot calls `specweave_task_status` for this increment, and the reply is saved. Copilot cannot be checked on an isolated server (ACP agents show unavailable there), so the proof uses live threads.

**AC-06.** `git diff --stat origin/main -- '*skills*'` is empty in the app repository, and no umbrella skill file changes.

Risks: the `tools/list` rewrite parses each list response (about 170 tools, tens of KB) on the server. A Claude thread in plan mode can call the two read-only SpecWeave tools without approval; both run read-only CLI commands.

## Decisions

### Asked
- D-01 Scope and ACs → given by the owner in the task (November 24, 2026).
### Defaulted (change any before sw-do)
- D-02 The workspace is the thread's worktree when it has one, else the project folder, matching the session cwd rule. A thread with no worktree in a project without worktrees uses the project folder, because that is its own working folder → default.
- D-03 AC-02 needs no code change: studio-code already answers `server/discover` in about 3 ms with a modern error, and Claude Code falls back at once → default.
- D-04 `specweave_pickup` never applies a handoff (`--no-apply`): applying writes files into the checkout, which a read tool must not do → default.
- D-05 `specweave_verify` runs the project's configured commands only; it does not take the machine-wide heavy-checks gate, the same as an agent running `specweave verify` in its shell → default.
- D-06 AC-05 is proven after the release is installed on M5, with live threads → default.
### Open
- none

## Tasks

### T-01 Always-load and search-hint `_meta` on every tool
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolMeta.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolMeta.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/McpToolMeta.test.ts

### T-02 Measure the server/discover probe
- AC: AC-02 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/discover-probe.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/discover-probe.md

### T-03 Worker refusal report
- AC: AC-03 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/worker-refusal-matrix.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/worker-refusal-matrix.md

### T-04 SpecWeave toolkit
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/workspace.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/cli.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/handlers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/specweave/workspace.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/claudeReadOnlyMcpTools.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/specweave

### T-05 List the SpecWeave tools only in SpecWeave workspaces
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolVisibility.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolVisibility.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/McpToolVisibility.test.ts

### T-06 Claude, Codex and Copilot call the SpecWeave tools
- AC: AC-05 | Files: .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/provider-proof.md | Test: test -s .specweave/increments/1483-studio-code-mcp-tool-surface-core-tools-up-front-search-hints-specweave-toolkit/reports/provider-proof.md

### T-07 No skill changed
- AC: AC-06 | Files: none | Test: cd repositories/anton-abyzov/specwithcode && test -z "$(git diff --name-only origin/main -- '*skills*' '*SKILL.md')"
