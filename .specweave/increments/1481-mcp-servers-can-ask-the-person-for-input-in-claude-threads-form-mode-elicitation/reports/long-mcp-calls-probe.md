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
