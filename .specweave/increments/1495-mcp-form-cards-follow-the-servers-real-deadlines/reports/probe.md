# 1495 probe: a current MCP server against the bundled Claude Code

Run on November 28, 2026 on M5, from 02:20 to 02:46 EST. Log timestamps are UTC. Everything lives in `/Users/anton/.specwithcode/m4/scratch/2026-11-27-1495/probe/`, outside every repository.

## Setup

- **Server:** `/Users/anton/.specwithcode/m4/scratch/2026-11-27-1495/probe/server.mjs` runs on `@modelcontextprotocol/server` 2.4.0 (the v2 line, MCP 2026-07-28), with `@modelcontextprotocol/node` 2.1.2 and zod 4.
  - stdio is served by `serveStdio` and the modern HTTP leg by `createMcpHandler(..., { legacy: "reject" })`.
  - `LEGACY=1` answers `server/discover` with `-32601`, so the client falls back to 2025-11-25. On HTTP that leg is a sessionful `NodeStreamableHTTPServerTransport`, so a held `elicitation/create` can be answered.
  - Every raw frame in and out is logged to `runs/<run>/server.jsonl`.
- **Tools:**
  - `confirm_delete`: a form. On the modern era it returns `input_required` with a sealed `requestState` that lasts 10 minutes, as GitHub's does. On the legacy era it holds the call on `elicitInput`.
  - `open_link`: a URL request. On the modern era it uses `inputRequired.elicitUrl`. On the legacy era it throws `UrlElicitationRequiredError`, error `-32042`, with a new `elicitationId` on every attempt.
  - `task_confirm`: a Tasks-extension job. The server answers `resultType: "task"`, then `input_required` with `inputRequests`, then waits for `tasks/update`. The SDK has no task store, so this part is written by hand from the Tasks spec. Without the extension in the call's own capabilities, the server answers `-32021`.
  - `slow_wait`: a plain long call.
- **Driver:** `/Users/anton/.specwithcode/m4/scratch/2026-11-27-1495/probe/drive.mjs` calls `query()` from `@anthropic-ai/claude-agent-sdk` 0.3.332 on its bundled CLI **2.1.332**, the version the app ships since v1.0.448.
  - It passes the options the app passes: `settingSources: ["user","project","local"]`, `bypassPermissions` with `allowDangerouslySkipPermissions`, `includePartialMessages`, and MCP servers passed in by the caller.
  - Its `onElicitation` logs each full `ElicitationRequest`, `options.requestId`, and when `options.signal` aborts. It then answers after `DELAY_MS`, or never.
  - The installed CLI 2.1.331 is the comparison (`CLI=installed`).
- **Card evidence:** "what the card shows" is derived. The requests captured here have the same fields on every path (`serverName`, `message`, `mode`, `requestedSchema`, or `url` and `elicitationId`). The app's module turns those fields into the card unchanged, and the module and adapter tests feed it the captured shapes. No live app was driven.

## Tasks on the SDK entrypoint

**Tasks on the SDK entrypoint: no.** Claude Code 2.1.332 advertises `io.modelcontextprotocol/tasks` in `server/discover` and `tools/list`, but leaves it out of the capabilities it sends on `tools/call`. A server may only start a task when the call itself carries the extension, so the probe's `task_confirm` answered `-32021`. Claude reported "Missing required client capability". No `tasks/get` or `tasks/update` was ever sent.

```
server/discover {"roots":{"listChanged":true},"elicitation":{"form":{},"url":{}},"extensions":{"io.modelcontextprotocol/tasks":{}}}
tools/list      {"roots":{"listChanged":true},"elicitation":{"form":{},"url":{}},"extensions":{"io.modelcontextprotocol/tasks":{}}}
tools/call      {"roots":{"listChanged":true},"elicitation":{"form":{},"url":{}}}
```

The result is the same through the SDK on 2.1.332 (`runs/task-stdio`), through the SDK on the installed 2.1.331 (`runs/task-installed`), and through plain `claude -p` on the bundled 2.1.332 binary (`runs/task-cli-p`). So Tasks are off for every entrypoint on this account, not only the SDK's.

The 2.1.332 binary shows the gate: MCP Tasks are on only when `CLAUDE_CODE_DISABLE_MCP_TASKS` is unset and the remote feature flag `tengu_glowing_lark` is on. The flag's local default is a user-type check, also off on a remote session. Which user type the check names is not readable from the minified code. A `tasks/update` question therefore cannot reach a Claude thread's card today.

## What reaches the card

| Path | Wire (seen at the server) | What `onElicitation` gets | Retries | Result for the model |
|---|---|---|---|---|
| Modern form, `input_required` (stdio and HTTP) | `tools/call` returns `resultType: "input_required"` with `inputRequests.confirm` (`elicitation/create`, form) and `requestState`. The CLI fulfils it and calls `tools/call` again with `inputResponses` and the same `requestState`. | `{serverName:"probe", message, mode:"form", requestedSchema}`, the same shape as a legacy form | none | the server's second result |
| Legacy form, held `elicitation/create` (stdio and HTTP) | `elicitation/create` while `tools/call` stays open | same shape | none | the server's result |
| Modern URL, `elicitUrl` | `input_required` with a URL `elicitation/create`, **no** `elicitationId` | `{mode:"url", url, message}` | one retry that carries the answer | the server's result. A decline arrives as `{action:"decline"}`. |
| Legacy URL, `-32042` | `tools/call` error `-32042` with `data.elicitations[]` | `{mode:"url", url, message, elicitationId}` | **accept:** 3 retries of `tools/call`, each a new request id with a new `elicitationId` and URL from the server, then the error goes to the model ("URL elicitation required"). **decline:** no retry. | decline: "URL elicitation was declined by the user. The tool "open_link" could not complete because it requires the user to open a URL." |
| Task, `tasks/update` | never offered, see above | nothing | n/a | `-32021` |

Notes for the card:

- `ElicitationRequest` carries **no tool use id**. The CLI does send `claudecode/toolUseId` to the server in `tools/call` `_meta` (legacy era), but not to the SDK host. Each `-32042` retry also comes with a new `options.requestId` and, here, a new `elicitationId` (`runs/url32042-accept`: `5ca81bda…`/`elicit-1-…`, `17b3c7e5…`/`elicit-2-…`, `c4bd3ffa…`/`elicit-3-…`). Neither one names the call. The app's turn has the running tool call (`mcp__probe__open_link`, `toolu_014y…`), so AC-04 keys the URL notice by the single running `mcp__<server>__*` call and falls back to the server plus the turn.
- The app declines URL mode today, and a decline is never retried, so one call shows one notice already. The key matters once 1498 accepts.
- On a modern server, `input_required` is invisible to the host: the CLI does the round trip. The card needs nothing new for it.

## Deadlines

All rows use `confirm_delete`, with no `timeout` in the MCP config.

| Run | Era, transport | Answer | Outcome |
|---|---|---|---|
| `dl-stdio-legacy-none`, `dl-http-legacy-none`, `-6m`, `-11m` | legacy held call, the server SDK's default timeout | none / 6 / 11 min | The **server** gives up at **60 s**. It sends `notifications/cancelled` ("SdkError: Request timed out"), the SDK aborts `onElicitation` at 59.99 s, and the tool fails with "Request timed out". A later answer never arrives. |
| `dl2-http-legacy-ka-6m`, `-11m`; `dl2-stdio-legacy-11m` | legacy held call, server waits 20 min, SSE keepalive every 15 s (SDK default) | 6 / 11 min | **Works** at 6 and at 11 minutes over HTTP, and at 11 minutes over stdio. |
| `dl2-http-legacy-ka-none` | same | none | no abort through 16 minutes, when the probe's 18-minute cutoff ended the run; only a `tool_progress` heartbeat every 30 s |
| `dl2-http-legacy-noka-6m` | legacy held call, 20-min server wait, **no** keepalive | 6 min | Claude Code drops the call's SSE stream and the standalone GET stream together, about **356 s** after the call opened, and reconnects GET. The answer at 360 s still reaches the server, but the result is lost. About 95 s later the model gets: `MCP server "probe" transport dropped mid-call; response for tool "confirm_delete" was lost`. |
| `dl2-http-legacy-noka-none` | same | none | the same stream drop at about 356 s. The SDK aborts `onElicitation` at **450 s** and the server gets `cancel`. |
| `dl-http-modern-6m` | modern `input_required` over HTTP | 6 min | **Works.** The retry carries the answer and a 360 s-old `requestState`. |
| `dl-http-modern-11m` | same | 11 min | The client still sends it. The probe's 10-minute `requestState` has expired, so the server refuses: "requestState expired or invalid (age 660049 ms)". This is the GitHub-style deadline. |
| `dl-http-modern-none`, `dl-stdio-modern-none` | modern | none | no abort through 17.5 minutes, when the probe's cutoff ended the run. The client never gives up on its own, and only the heartbeat runs. |

The real deadlines, shortest first:

1. **60 s**, the MCP TypeScript SDK's default request timeout for a held `elicitation/create` (`DEFAULT_REQUEST_TIMEOUT_MSEC = 6e4`). The server signals it, the SDK aborts, and the card can close with a notice. This case is AC-02.
2. **About 356 s**, Claude Code's HTTP stream drop when nothing arrives (no keepalive). Nothing signals it in time: the answer is lost, and the abort comes about 95 s later.
3. **10 minutes**, a server's own `requestState` lifetime (GitHub's, mirrored by the probe). Nothing signals it at all: a modern request waits forever on the client.

**The unattended timeout is set by the shortest deadline nothing signals: the HTTP stream drop at about 356 s.** `UNATTENDED_MCP_ELICITATION_TIMEOUT_MS` becomes 5 minutes, and the notice says "in 5 minutes". The 60 s server timeout is shorter, but it arrives as the SDK's abort, which now closes the card with "`<server>` stopped waiting for an answer." A cut to 60 s would cancel cards on modern servers that wait 10 minutes. On the timeout the server gets `cancel` (unchanged, `ClaudeMcpElicitation.ts`).

## Abort cause

The abort carries no cause: every `elicitation-abort` in the runs above, from a server's cancel, a stream drop or a CLI exit, has the reason `AbortError: This operation was aborted`.

`crash.sh` (November 28) kills the CLI with a form pending, once with SIGKILL and once with SIGTERM. The SDK aborts `onElicitation`, and 2 ms later the output ends with "Claude Code process terminated by signal SIGKILL" or "exited with code 143". The app's 2 s wait for its own mark after an abort covers that gap by a wide margin.

## Proof limits

- One account and one machine (M5, macOS). The `tengu_glowing_lark` flag is remote, so another account could see Tasks on.
- The probe server is the TypeScript SDK. GitHub's server is Go, so its legacy timeout may differ from 60 s. Its 10-minute `requestState` is taken from the 1493 research, not measured against GitHub.
- No live app thread was driven. The card content is derived as described above.
- The HTTP drop was measured without keepalives only on the legacy leg. A modern request has no open stream while the person answers, so the drop cannot hit it.
