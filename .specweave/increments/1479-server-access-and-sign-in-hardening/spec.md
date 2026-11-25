# 1479 Server access and sign-in hardening

Wave 1, group A of [1474](../1474-t3-code-changes-since-november-14-the-last-open-copy/spec.md). Brief: `1474/reports/wave1-brief.md`; lane notes in `1474/reports/lanes/`. Upstream shas appear only in this umbrella increment, never in the app repository.

## Problem

The November 14 to 25 review of the last open T3 Code copy found sign-in, session and server-surface defects that our server still has:

- "Revoke other clients" ends sessions but leaves unspent pairing codes usable, and a sign-in or MCP OAuth code redeemed right after the revoke still gets a fresh session.
- A client holding only `settings:write` can save project scripts that the host runs on worktree creation.
- Secret names are joined into file paths unchecked, and relay-signed `jti` and nonce values become secret names. A 0-byte persisted signing secret is used as an empty HMAC key.
- An offline `auth session revoke` leaves a Connect device trusted. MCP OAuth accepts a resource ending in `#`. On shutdown the Connect account token goes to whatever relay URL is stored.
- No default request-body limit on unauthenticated routes; signed URLs are written to request logs when the debug logger is on; `/mcp` serves browser `Origin` requests and answers CORS preflights; headless serve prints a token over plain HTTP with no warning; the HTML render's `<meta>` scans are quadratic.
- Windows cleanup and kill paths run `ping`, `cmd`, `taskkill` and `powershell` by bare name; the MCP launch checks a worktree's realpath but starts in the caller's spelling; atomic saves reset file modes and never sync; the local device hub accepts any local process.

## Scope

In: the rows in the table below, inside group A's files (`apps/server/src/auth/*`, `cloud/*`, `cli/auth.ts`, `cli/uninstall.ts`, `device/*`, `server.ts`, `http.ts`, `startupAccess.ts`, `atomicWrite.ts`, `mcp/McpHttpServer.ts`, `mcp/toolkits/project/*`, `htmlRender/headlessChrome.ts`, `process/ownedProcessTree.ts`, `packages/contracts/src/settings.ts`, `packages/shared/src/htmlRender.ts`, the mode-limit check in `orchestration-v2/Orchestrator.ts`, and their tests).

Out: anything that adds or loosens an auth path (held: `dd512d86c5`, pairing-link sessions renewing with the device key). A new relay scope (needs web and mobile files and changes what older machines hold). Fixes in files other groups own; those are listed in the report with `path:line`.

| Row | Our code | AC |
|---|---|---|
| `cc2e4c1704` revoke-all races sign-ins in progress | `apps/server/src/auth/EnvironmentAuth.ts:1446`, `McpOAuth.ts:481` | AC-01, AC-02 |
| `ebf7b9a4c5` revoke-all also revokes unspent pairing codes | `EnvironmentAuth.ts:1550` | AC-01 |
| `55b14ac51d` offline CLI revoke untrusts the Connect device | `apps/server/src/cli/auth.ts:374` | AC-03 |
| `6a510c4894` MCP OAuth resource with an empty fragment | `McpOAuth.ts:160` | AC-04 |
| `0bd581b078` empty persisted secret regenerated | `ServerSecretStore.ts:303` | AC-05 |
| `6f05fbf45f` secret names stay in the secrets folder | `ServerSecretStore.ts:197`, `cloud/CloudLink.ts:1700`, `:1806` | AC-06 |
| `bba3918e3c` project scripts need operate scope | `packages/contracts/src/settings.ts:2852` | AC-07 |
| `a941ab544d` relay token only to the configured relay | `cloud/CloudLink.ts:1400`; scope half already ours at `packages/contracts/src/auth.ts:224-244`, `cloud/http.ts:142`, `:148` | AC-08 |
| `6b45d90047` remote clients with relay config can link | not applicable: ours never added the caller-origin check it relaxes (`CloudLink.ts:777`) | none |
| `2dd323463a` 1 MiB default body limit, linear tag scans | `apps/server/src/server.ts:1167`, `packages/shared/src/htmlRender.ts:656` | AC-09, AC-10 |
| `c57ccdaf52` signed URLs out of request logs | `apps/server/src/http.ts:474` | AC-11 |
| `6c0032d655` `/mcp` refuses browser origins | `apps/server/src/mcp/McpHttpServer.ts:423`, `http.ts:334` | AC-12 |
| `b6ac2449f1` plain-HTTP serve warning | `apps/server/src/startupAccess.ts:122` | AC-13 |
| `4c679a21e7` inline HTML renders cannot scroll the chat | `packages/shared/src/htmlRender.ts:634` | AC-14 |
| `667116eee9` Windows uninstall from System32 | `apps/server/src/cli/uninstall.ts:211` | AC-15 |
| `e3b79cd0bf` Windows tools by absolute path; launch in the validated worktree | `htmlRender/headlessChrome.ts:291`, `process/ownedProcessTree.ts:1009`, `cloud/bootService.ts:599`, `mcp/toolkits/project/handlers.ts:371` | AC-15, AC-16 |
| `eb62a37150` atomic saves keep modes and sync | `apps/server/src/atomicWrite.ts:56` | AC-17 |
| `0d6fe2141a` mode limit follows the running turn (unverified) | `orchestration-v2/Orchestrator.ts:13568` | AC-18 |
| `844d491ff8` device hub requires a token | `apps/server/src/device/LocalDeviceHost.ts:670` | AC-19 |
| `fa5fde4bea` forwarded address from loopback peers (settle by test) | `apps/server/src/auth/utils.ts:215` | AC-20 |

## Acceptance Criteria

- [ ] AC-01: After "Revoke other clients", a pairing code or MCP approval code minted before it fails to exchange, and a browser-session or token exchange whose credential was spent before the revoke but whose session is issued after it is refused. The caller's own session, a desktop-bootstrap exchange started after the revoke, and a pairing code minted after the revoke all still work.
- [ ] AC-02: An MCP OAuth authorization code minted before a revoke-all is refused with `invalid_grant` at the token endpoint; one minted after it is exchanged.
- [ ] AC-03: `auth session revoke <id>` with the server stopped revokes the session and, when it is bound to a Connect device key, every session on that key and the device's trust, as the live path does. A session with no Connect binding is revoked as before.
- [ ] AC-04: An MCP OAuth `resource` that contains `#` (including a bare trailing `#`) is refused; the exact resource and one with a trailing slash still match.
- [ ] AC-05: A 0-byte persisted random secret is replaced by a new one of the requested length, once, even under concurrent reads; a non-empty secret is returned unchanged.
- [ ] AC-06: `get`, `set`, `create`, `getOrCreateRandom` and `remove` refuse a secret name containing `/`, `\`, NUL, or equal to `.`/`..`, and nothing is written outside the secrets folder. Cloud replay markers use a SHA-256 hex of the proof's `jti` and nonce, so a `jti` of `../x` stays inside the folder and a replayed proof is still refused.
- [ ] AC-07: A settings patch that sets `defaultProjectScripts`, a non-null `projectScriptOverrides` entry, or `projectSettingsOverrides.*.defaultProjectScripts` requires `orchestration:operate` in addition to `settings:write`; other settings patches require what they did.
- [ ] AC-08: At shutdown the managed tunnel is released only when the stored relay URL is the configured one, with redirects refused; otherwise no request is sent and shutdown continues. A session with standard client scopes gets 403 on `relayConfig` and `linkProof` (regression; already ours).
- [ ] AC-09: Every API route (the environment HTTP API, which includes the unauthenticated `/oauth/token`, `/oauth/mcp/*` and `/api/auth/*` routes) reads at most 1 MiB of body: a 2 MiB POST with a declared length gets 413 before it is read, and a chunked one stops being read at 1 MiB. Small API bodies still reach their handler. Raw routes (attachment upload, folder copy, handoff, webhook, OTLP traces, MCP and the rest) are untouched and keep their own limits; a raw route served beside the API still accepts 2 MiB.
- [ ] AC-10: The HTML render bootstrap's `<meta>` scans run in linear time: 200 KB of `<meta a` with no `>` is injected in under 50 ms, and existing charset and viewport detection is unchanged.
- [ ] AC-11: With the request logger on, webhook, asset and attachment-upload requests log no URL (their tokens never reach the log); other requests still log.
- [ ] AC-12: A request to `/mcp` carrying an `Origin` header gets 403 before authentication, and `/mcp` gets no CORS headers or preflight answer. A bearer request with no `Origin` is still served, and the browser extension and desktop app (which do not call `/mcp`) are unaffected; other routes keep their CORS.
- [ ] AC-13: `formatHeadlessServeOutput` adds a plain-HTTP warning when the connection string's host is not loopback, and none for `127.0.0.1`, `localhost` or `::1`.
- [ ] AC-14: A render loaded with the contain-scroll fragment flag replaces `scrollIntoView` with one that scrolls only scrollers inside the page; without the flag the native method is untouched. The web frame that sets the flag is another group's file (report).
- [ ] AC-15: On Windows, uninstall cleanup runs `%SystemRoot%\System32\cmd.exe` and `PING.EXE` by absolute path with cwd System32 and passes the runtime folder through the environment, not the command text; `taskkill` and `powershell` in group A's files run from System32 by absolute path.
- [ ] AC-16: An MCP launch into an existing worktree starts in the registered worktree path that passed the check, not the caller's spelling (a symlink to it); a non-worktree path is still refused.
- [ ] AC-17: An atomic save keeps the replaced file's mode (`0600` stays `0600`, `0644` stays `0644`) with owner read and write always kept (`0000` becomes `0600`), creates a missing file as `0600`, syncs the data before the rename and the folder after it (a folder sync that the platform refuses is ignored); Windows behaviour is unchanged.
- [ ] AC-18: A mode-limited sender steering into a turn started above its limit is refused; settled by a test, recorded as not reproduced if today's check already refuses it.
- [ ] AC-19: The local device hub starts with a token, and our proxy and hub calls send it; a request to the hub without it is refused. The embedded dashboard, its WebSockets and device actions keep working through our proxy, and the token never reaches a log.
- [ ] AC-20: A request from a loopback peer carrying `X-Forwarded-For` records the socket address in client metadata (regression; already stricter than upstream).

## Approach

Each row: a test that fails on today's `origin/main`, then the fix; red and green go in `reports/red-green.md`. One commit per row so PRs split cleanly. Four PRs from `origin/main`:

1. Sign-in, sessions and Connect secrets: AC-01 to AC-08, AC-20 (`auth/*`, `cli/auth.ts`, `cloud/*`, `settings.ts`).
2. HTTP surface: AC-09 to AC-14 (`server.ts`, `http.ts`, `McpHttpServer.ts`, `startupAccess.ts`, `htmlRender.ts`).
3. Local tools and files: AC-15 to AC-18 (`uninstall.ts`, a new System32 helper, `headlessChrome.ts`, `ownedProcessTree.ts`, `cloud/bootService.ts`, `cloud/runtimeVersionRetention.ts`, project handlers, `atomicWrite.ts`, `Orchestrator.ts`).
4. Device hub token: AC-19 (`device/*`), last.

Revoke race: a revocation counter in a new `auth/revocationEpoch.ts`. The three sign-in completions (browser session, token exchange, MCP code redeem) read it when they start and issue only under the shared lock with the counter unchanged; revoke-all bumps it under that lock, then revokes sessions and unspent links. `issueSession` (CLI and internal) is not gated. New logic goes in new files: `EnvironmentAuth.ts`, `CloudLink.ts`, `server.ts`, `settings.ts` and `Orchestrator.ts` are already over 1,500 lines.

Risks: the body limit could clamp a route that reads more than 1 MiB through `arrayBuffer`/`json` (surveyed: OTLP proxy gets its own limit; uploads stream). The `/mcp` Origin rule breaks any browser-based MCP client; ours have none. Device hub with a token may refuse framing unless `--frame-ancestor` is passed; checked against the installed 0.15.3 hub before coding.

## Decisions

### Asked
- none (the launch message and brief settle scope)
### Defaulted (change any before sw-do)
- D-01 Increment number 1479, not 1475: `1475-install-a-specwithcode-page-as-a-desktop-app` already exists in the `artifact-install-as-app` worktree and the CLI refuses the id.
- D-02 Relay configuration keeps `relay:write`, which is already administrative-only in ours; no new scope (needs web and mobile files and older machines would lose it).
- D-03 Revoke-all revokes every unspent pairing link, including Connect-bound and fleet ones and the startup pairing link: "every other way in" ends.
- D-04 Scroll containment is gated by a fragment flag, as the web frame will set it; file preview and fullscreen keep native behaviour.
### Open
- none

## Tasks

### T-01 Revoke-all ends unspent codes and in-flight sign-ins
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/revocationEpoch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/McpOAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/revokeOthers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/revocationEpoch.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/McpOAuth.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/revokeOthers.test.ts apps/server/src/auth/revocationEpoch.test.ts apps/server/src/auth/McpOAuth.test.ts

### T-02 Offline CLI session revoke untrusts the Connect device
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/cli/auth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/auth.revoke.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/ConnectPhoneRevocation.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/cli/auth.revoke.test.ts

### T-03 MCP OAuth resource fragment, forwarded address regression
- AC: AC-04, AC-20 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/McpOAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/McpOAuth.resource.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/utils.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/McpOAuth.resource.test.ts apps/server/src/auth/utils.test.ts

### T-04 Secret store: names, empty secrets, replay marker names
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/ServerSecretStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/ServerSecretStore.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/cloudReplayMarkers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/cloudReplayMarkers.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/ServerSecretStore.test.ts apps/server/src/cloud/cloudReplayMarkers.test.ts

### T-05 Project scripts need operate scope
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settingsScopes.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/contracts/src/settingsScopes.test.ts

### T-06 Relay token only to the configured relay
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.lifecycle.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/http.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/cloud/CloudLink.lifecycle.test.ts apps/server/src/cloud/http.test.ts

### T-07 Default body limit and linear tag scans
- AC: AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/httpBodyLimit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/httpBodyLimit.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/htmlRender.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/htmlRender.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/httpBodyLimit.test.ts packages/shared/src/htmlRender.test.ts

### T-08 Signed URLs out of request logs; `/mcp` refuses browser origins
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/http.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.origin.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/http.test.ts apps/server/src/mcp/McpHttpServer.origin.test.ts

### T-09 Plain-HTTP serve warning
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/startupAccess.ts, repositories/anton-abyzov/specwithcode/apps/server/src/startupAccess.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/startupAccess.test.ts

### T-10 Contained scrollIntoView behind a fragment flag
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/htmlRender.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/htmlRender.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/htmlRender.test.ts

### T-11 Windows tools by absolute path; launch in the validated worktree
- AC: AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/process/windowsSystemTools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/process/windowsSystemTools.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/uninstall.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/uninstall.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/headlessChrome.ts, repositories/anton-abyzov/specwithcode/apps/server/src/process/ownedProcessTree.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/bootService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/runtimeVersionRetention.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/MachineHardwareIdentity.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/bootService.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/process/windowsSystemTools.test.ts apps/server/src/cli/uninstall.test.ts apps/server/src/mcp/toolkits/project/handlers.test.ts

### T-12 Atomic saves keep modes and sync
- AC: AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/atomicWrite.ts, repositories/anton-abyzov/specwithcode/apps/server/src/atomicWrite.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/telemetry/Identify.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/atomicWrite.test.ts

### T-13 Mode limit against the running turn (settle by test)
- AC: AC-18 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.modeLimitSteer.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Orchestrator.modeLimitSteer.test.ts

### T-14 Device hub requires a token
- AC: AC-19 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/device/LocalDeviceHost.ts, repositories/anton-abyzov/specwithcode/apps/server/src/device/DeviceHubProxy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/device/hubToken.ts, repositories/anton-abyzov/specwithcode/apps/server/src/device/hubToken.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/device/hubToken.test.ts apps/server/src/device/DeviceHubProxy.test.ts

Verify and close 1479.
