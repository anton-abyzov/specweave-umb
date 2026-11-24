# MCP endpoint and MCP clients cap request and response size, with the dependency bumps from the m8ven scan

## Problem

m8ven.ai graded the app's server package C (score 60) on November 7, 2026, for one failing check: "5 high severity in production deps". Evidence: `~/.specwithcode/m4/scratch/2026-11-16-m8ven-scan/` (`score.json`, `osv.json`, the `GHSA-*.json` files, `page.html`).

None of the five is reachable in the shipped server (read at `origin/main` `21d74227e`):

- `@modelcontextprotocol/sdk` 1.29.0, four highs. The server's own `/mcp` endpoint is built on `effect/ai` (`apps/server/src/mcp/McpHttpServer.ts:1196-1202`), not on the SDK's HTTP server transports, task store, bearer middleware or OAuth client. The SDK is used only as a client in three places.
- `zod` 4.6.5, one high. The server imports zod nowhere; it runs inside the SDK when a client validates an answer.

The scan still points at four real gaps:

1. Four runtime pins have published fixes: `@modelcontextprotocol/sdk` 1.29.0, `zod` 4.6.5, `smol-toml` 1.8.0, `stream-json` 3.6.0. The dev toolchain pin `vite-plus` 1.0.0 has seven advisories of its own.
2. `/mcp` reads the whole request body with no limit. `HttpIncomingMessage.MaxBodySize` defaults to none, and ten other routes set it (`away/*`, `fleet/folderTransferRoute.ts`, `handoff/handoffRoute.ts`, `scheduledTasks/webhookRoute.ts` and others); `/mcp` does not.
3. Two of the three MCP clients read answers with no byte limit: stdio project connections (`project/connections/ProjectConnectionTransport.ts:81`, the SDK buffers stdout until a newline with no maximum) and Figma (`design/figma/FigmaDesktopMcpClient.ts:82`). Only the fleet client counts bytes (24 MiB, `fleet/RemoteStudioMcpClient.ts:91`), and its test never reaches the cap (it sends 5 MiB).
4. A byte limit alone does not bound memory. The SDK validates each answer with zod, which keeps one issue per invalid array element: a checker measured about 924 MB of heap for a 1 MB answer of `[0,0,0,...]` (`sdkmem.mjs`). zod 4.6.7 stops early only for arrays that declare a maximum, and the SDK's result arrays declare none.

A bump is not a one-line change here. `scripts/studio-toolchain/preservation-audit.mjs` requires `pnpm-lock.yaml` to equal the upstream lock plus the digest-pinned changes in `reviewed-lock-changes.json`. It refuses any server SDK version other than 1.29.0 (`:383-387`), has no way to drop a line pnpm pruned, and its test requires every upstream integrity to still be present.

Open question from the analysis: can a fleet address be plain HTTP on a LAN?

## Scope

In: the four runtime bumps and the vite-plus bump, the lock audit changes they need, a request body limit on `/mcp`, byte and element limits on the three MCP clients, and a written answer to the fleet address question.

Out:

- The copies of zod that other packages bring in (3.25.76 through `@cursor/sdk`, 4.4.3, 4.5.4). The server pin does not move them.
- The Pi extension's own client to our `/mcp` (`orchestration-v2/Adapters/piStudioMcpExtensionSource.ts`). It talks only to this server.
- An element limit on `/mcp` requests. This increment limits bytes there, as asked.
- The LAN path for folder copies (increment 1334).

## Acceptance Criteria

- [ ] AC-01: `apps/server/package.json` pins `@modelcontextprotocol/sdk` 1.32.2, `zod` 4.6.7, `smol-toml` 1.9.1 and `stream-json` 3.9.0, the lock resolves the server to exactly those, and an OSV query of the server's runtime pins returns no advisory for the four packages.
- [ ] AC-02: The catalog pins `vite` and `vite-plus` at 1.6.0, and format check, lint, typecheck and the test suites pass under it.
- [ ] AC-03: The lock audit accepts the new lock and still refuses each of: a line with no reviewed change, a pruned line with no reviewed removal, a changed integrity, a removed registry record whose stated integrity differs from the lock's, and a server SDK version other than the reviewed one.
- [ ] AC-04: A `/mcp` request whose body is over the limit gets HTTP 413 and no tool runs, both when `Content-Length` declares it and when the body is streamed without one. A request with no valid credential still gets 401 before any body is read.
- [ ] AC-05: The largest legitimate `/mcp` request, one 2 MiB file chunk as base64, still succeeds.
- [ ] AC-06: A stdio project connection whose server writes more than the limit for one message, with or without a newline, fails that call with an error that says the answer was too large, and the child process is stopped. Nothing more is buffered.
- [ ] AC-07: A Figma answer over the byte limit fails the call with the same kind of error, and reading stops.
- [ ] AC-08: For all three clients, an answer with more JSON values than the limit fails that one request before the SDK validates it. A 1 MB answer of `[0,0,...]` raises heap by under 50 MB, measured with the checker's method and recorded in reports/.
- [ ] AC-09: The fleet client keeps its 24 MiB limit, and a test now sends more than 24 MiB and sees the read stop.
- [ ] AC-10: Answers of legitimate size still work in tests: a 200-tool list, an 8 MiB base64 screenshot from a fleet peer, and Figma variable definitions.
- [ ] AC-11: The fleet address answer is written in `docs/studio/security.md`, and the existing test that refuses `http://` fleet addresses still passes.

## Approach

Order: bumps and audit first (they change the installed SDK the client code is tested against), then the two limits, then review.

1. **Lock audit** (`scripts/studio-toolchain/preservation-audit.mjs`, its test). The baseline string at `:353` describes the upstream lock and stays. What changes:
   - A third reviewed op, `remove`, for a block pnpm pruned. It names the exact block; for a registry record it also names `package` and `integrity`, which must equal the record being removed. No other section rule loosens.
   - The server SDK check at `:383-387` reads the reviewed version from the reviewed changes to the server importer's SDK record instead of the literal 1.29.0, so a bump is refused unless the record carries it.
   - The test's "every upstream integrity is still present" becomes "present, or removed by a reviewed removal", and its list of added integrities is read from the record instead of four literals.
2. **Runtime bumps** (`apps/server/package.json`, `pnpm-lock.yaml`, `reviewed-lock-changes.json`, `LOCK_REVIEW_SHA256`). `stream-json` 3.9.0 needs `stream-chain` ^4.4.2. `apps/server/src/project/AgentSessionJson.ts` uses deep imports and an untyped runtime export (`jsonParser`); its tests decide whether the code needs a change. The reviewed entries are generated from the lock diff by a script kept in the PR, then read line by line.
3. **vite-plus 1.6.0** (`pnpm-workspace.yaml:55-56`, lock, record, `scripts/studio-toolchain/bootstrap-pnpmfile.cjs` and its test, which name 1.0.0). It brings vitest 5.1.0, oxlint 1.93 and oxfmt 0.78, so format and lint output can move; those fixes ship in the same PR as their own commit.
4. **`/mcp` body limit** (`apps/server/src/mcp/McpHttpServer.ts`). In the auth middleware, after the credential is admitted: refuse a `Content-Length` over the limit with 413, and provide `HttpIncomingMessage.MaxBodySize` around the handler, the idiom of `away/awayAccessRoute.ts:56-64`. The body is read once and cached, so the first read fixes the limit. A streamed overflow must also end as 413.
5. **Client limits** (new `apps/server/src/mcp/client/mcpResponseLimits.ts`, used by the three clients):
   - `cappedFetch`: the fleet client's byte counter, moved and shared with Figma.
   - `guardedTransport`: wraps any SDK transport and counts JSON values (array items plus object fields) in each incoming message, stopping at the limit. Over it, the message becomes a JSON-RPC error for that request id, so only that call fails and nothing reaches zod.
   - stdio: a byte counter on the child's stdout that tracks the bytes of the unfinished line; over the limit it closes the transport and fails pending calls.
6. **Fleet address answer**: no code change. One paragraph in `docs/studio/security.md`.

Rejected:

- Editing only the 1.29.0 literals. The lock would still fail the audit on every pruned line and on the upstream-integrity check.
- Keeping pruned records in the lock by hand. The next plain `pnpm install` drops them.
- A custom stdio transport that spawns the child itself. It would have to repeat the SDK's Windows spawn handling.
- Relying on zod 4.6.7 for memory. It only helps arrays with a declared maximum.
- An override that lifts every zod copy to 4.6.7. The audit refuses version overrides, and 3.x cannot move to 4.x.

Risks:

- vite-plus 1.0.0 to 1.6.0 moves the whole toolchain. If format or lint churn is wide, it is still one commit, but it is the part most likely to hold the PR.
- The lock audit is a supply-chain guard. Every loosening here is narrow and has a refusal test (AC-03).
- A lock-record PR must merge with a merge commit: a squash drops the commit the record names and release stage 1 fails.
- A limit set too low breaks real use. Each number below sits above the largest legitimate size found in the code.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 `/mcp` request limit: 8 MiB. The largest legitimate request is about 2.8 MB (a 2 MiB file chunk as base64), and 8 MiB is what the ACP bridge already allows for the same messages (`mcp/AcpMcpOverAcpBridge.ts:11`). Reversible.
- D-02 Client byte limits: fleet stays 24 MiB per answer, Figma gets the same 24 MiB, stdio gets 8 MiB per message. Project connection output is already cut to 262,144 characters after the read. Reversible.
- D-03 Element limit: 100,000 JSON values per message, for all three clients. A 262,144-character answer can hold at most about 131,000 values, and real tool lists and results are far below that. Reversible.
- D-04 Over a limit, the one request fails with a "too large" error; for stdio byte overflow the connection is also closed, because the stream cannot be resynchronised.
- D-05 The lock audit gains a `remove` op instead of a wider "upgrade" op, so each dropped line stays visible in the record.
- D-06 Fleet addresses: a fleet address cannot be plain HTTP, on a LAN or anywhere. `fleet/fleetOrigin.ts:40-68` accepts only `https:` to a `*.ts.net` name or a SpecWithCode Connect address, the fleet file refuses anything else (`studioFleet.ts:140-144`), and `fleetOrigin.test.ts:38-39` pins it. A plain bearer token crosses tailnet addresses, so plain HTTP would put it on the wire in clear text. The LAN copy path in 1334 uses a pinned TLS certificate for the same reason. No change.

### Open
- none

## Review

Reviewer: muse, model muse-wonder-1.0, effort xhigh, adversarial, security lens, until "Verdict: ship" at the PR's exact head.

## Tasks

### T-01 Lock audit accepts a reviewed removal and a reviewed SDK version
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/preservation-audit.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/preservation-audit.test.mjs | Test: cd repositories/anton-abyzov/specwithcode/scripts && node --test studio-toolchain/preservation-audit.test.mjs

### T-02 Runtime dependency bumps
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/package.json, repositories/anton-abyzov/specwithcode/pnpm-lock.yaml, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/reviewed-lock-changes.json, repositories/anton-abyzov/specwithcode/apps/server/src/project/AgentSessionJson.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/project/AgentSessionJson.test.ts src/project/connections src/fleet/RemoteStudioMcpClient.test.ts src/design/figma

### T-03 vite-plus 1.6.0
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/pnpm-workspace.yaml, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/bootstrap-pnpmfile.cjs, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/bootstrap-pnpmfile.test.mjs | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/studio-verify/pr-gate.sh --base origin/main

### T-04 Request body limit on /mcp
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.bodyLimit.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/mcp/McpHttpServer.bodyLimit.test.ts src/mcp/McpHttpServer.test.ts

### T-05 Byte and element limits on the MCP clients
- AC: AC-06, AC-07, AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/client/mcpResponseLimits.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/client/mcpResponseLimits.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteStudioMcpClient.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteStudioMcpClient.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fakeStudioMcp.testkit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/design/figma/FigmaDesktopMcpClient.ts, repositories/anton-abyzov/specwithcode/apps/server/src/design/figma/FigmaDesktopMcpClient.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/connections/ProjectConnectionTransport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/connections/ProjectConnectionTransport.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/connections/stdioFixture.testkit.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/mcp/client src/fleet/RemoteStudioMcpClient.test.ts src/design/figma src/project/connections

### T-06 Fleet address answer in the security doc
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode/docs/studio/security.md | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/fleetOrigin.test.ts

### T-07 Review, merge, release, verify and close 1367
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released HEAD
