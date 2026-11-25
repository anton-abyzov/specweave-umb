# Long MCP calls in Claude threads (AC-06)

November 25, 2026 (UTC), on M5. All four calls returned inline. None moved to a background task or hit an idle timeout, so no environment pin was added.

## Results

| CLI | Held | Call sent (UTC) | Result (UTC) | Tool result | System events |
|---|---|---|---|---|---|
| Installed `claude` 2.1.331 | 3 min | 04:44:51 | 04:47:52 | `held 180 s` | `init`, `thinking_tokens` |
| SDK bundled 2.1.276 | 3 min | 04:44:52 | 04:47:54 | `held 180 s` | `init`, `thinking_tokens` |
| Installed `claude` 2.1.331 | 7 min | 04:44:52 | 04:51:54 | `held 420 s` | `init`, `thinking_tokens` |
| SDK bundled 2.1.276 | 7 min | 04:44:52 | 04:51:55 | `held 420 s` | `init`, `thinking_tokens` |

"Inline" means the tool result in the model's stream is the server's own text, received once the hold ended. The runs show no `task_started` or other background-task event and no idle-timeout error.

These held calls are quiet calls: the stand-in sends no progress notifications and no bytes until the result. Studio-code attaches to Claude threads over HTTP (`ClaudeAdapterV2.ts:1395-1402`), and this probe uses the same HTTP path, so it extends the earlier stdio probe (`research/07-live-probe.md`) to the transport studio-code actually uses. This check is independent of the form card and does not gate its merge (AC-06).

## Cancellation

A 5-minute hold, with the query's `AbortController` aborted 30 s (second run) or 45 s (first run) after the hold started:

| CLI | Run | Abort to query end | Server saw the cancel | After the cancel |
|---|---|---|---|---|
| Installed `claude` 2.1.331 | 05:51:41 UTC | 2 s ("Claude Code process aborted by user") | yes, connection closed and the tool's abort signal fired 2 s after the abort | nothing |
| SDK bundled 2.1.276 | 05:51:40 UTC | 2 s | yes, 2 s after the abort | it reconnected (`server/discover`, `initialize`) and sent the same `tools/call` again; that call was cut 0.2 s later when the process ended |

The first run (05:45:52 UTC, 45 s) ended the same way, 2 s after the abort, but the probe exited before it could log the server side.

Finding: during shutdown after an abort, the bundled CLI 2.1.276 can re-send a tool call it was cancelling. A tool with side effects could then start a second time and be cut off mid-way. The installed 2.1.331 did not do this. Threads on the bundled CLI keep this risk until the SDK is bumped, which is out of scope here. This was seen in the one bundled run whose server side was logged.

Scripts: `probe-cancel.mjs` (args: seconds, CLI, label, seconds before abort). Logs: `run-cancel-*.log` and `run-cancel2-*.log`, all in `/Users/anton/.specwithcode/m4/scratch/2026-11-25-1481/probe/`.

## How it ran

- Agent SDK `@anthropic-ai/claude-agent-sdk` 0.3.276 `query()` with model `haiku`, once with its bundled CLI and once with `pathToClaudeCodeExecutable` set to `/Users/anton/.local/bin/claude`.
- The server entry has the shape the app gives studio-code: `type: "http"`, `timeout: 65 * 60 * 1000` (`CLAUDE_STUDIO_MCP_TOOL_TIMEOUT_MS`) and `Authorization: "${PROBE_MCP_AUTHORIZATION}"`, filled from the session `env`.
- `env` is this thread's own process environment plus that header variable.
- The server is a local stand-in (D-05): `@modelcontextprotocol/sdk` 1.32.2 Streamable HTTP, stateless, `enableJsonResponse: true`. Its `hold` tool sleeps for the requested seconds and then answers. Like studio-code's Effect `McpServer`, it sends one JSON body when the call completes and no bytes before that.
- Script and logs: `/Users/anton/.specwithcode/m4/scratch/2026-11-25-1481/probe/probe.mjs` and `run-180-bundled.log`, `run-180-claude.log`, `run-420-bundled.log`, `run-420-claude.log` in the same folder.

## Proof limits

- This was a stand-in server, not the live studio-code server, so no live app or database was touched. The transport behaviour that matters, a silent connection until one JSON body arrives, is the same.
- The environment was this agent thread's. A thread started by the app passes a similar but not identical `env`.
- Calls longer than 7 minutes were not measured. Above 65 minutes the entry's own `timeout` ends the call by design.
- An MCP server's own request timeout applies to its `elicitation/create` request (the TypeScript MCP SDK default is 60 s), and the app cannot change it. A server that keeps that default cancels a form after 60 s, whatever the person does.
