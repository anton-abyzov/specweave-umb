# Security pass from the upstream review: approval scope, Always-allow key, installer, sign-in links, framing, DPoP, browser bumps

## Problem

The upstream triage of November 14, 2026 (`.specweave/increments/1346-t3-code-changes-since-november-2/reports/2026-11-15-t3-code-triage-november-2-to-november-14-2026-bb97f4-af68df.md`, section 1) found these gaps open in our tree at `013d05387`, each confirmed by a cross-family reviewer:

- An approved ACP request of any kind that maps to `command` lets the agent open client terminals. `AcpAdapterV2.ts:1290` maps every unlisted kind to `command`, so an approved `switch_mode` also grants terminals (`AcpClientPolicy.ts:310`).
- Pi "Always allow this session" is keyed on a summary cut at 4,000 characters, so two long calls that differ later share one grant (`piStudioMcpExtensionSource.ts:85`, `PiAdapterV2.ts:1227`).
- The ACP Registry installer runs `chmod 0o755` before checking that the real path is inside the install root, and resolves a uv agent from the user's PATH (`AcpRegistrySupport.ts:1968`, `:1340`).
- Provider sign-in links are opened without a scheme check (`providerSetup.ts:50`, `localApi.ts:30`, `ProviderAuthenticationSection.tsx:170`).
- The SPA HTML can be framed by another site (`http.ts:703`).
- A DPoP replay marker is written before the subject token is validated (`auth/http.ts:567`).
- A delegated agent blocked on a secret or a link is invisible on the phone (`agentAwareness.ts:61`).
- The ACP MCP stdio bridge never answers a server request that arrives before the tool result (`AcpMcpStdioBridge.ts:306`).
- The preview browser pins Chrome 156.0.8078.80 and the desktop app pins Electron 44.4.2.
- Desktop IPC handlers take no sender check (`DesktopIpc.ts:86`, `:160`). Hardening, not an exploit.

## Scope

In: hand ports of the listed upstream fixes onto our code, each with a test that fails before the fix, split into reviewable PRs. Out: the dependency audit and sections 3 and 4 of the report (another worker). Hardening rows S10 to S12 were added on November 14, 2026 after Anton's "yes, adopt all".

Release rule: none since November 15, 2026. The PRs that change permissions, auth or access (AC-01, AC-02, AC-06, AC-10, AC-15) merge like every other PR (current main, green required checks, a ship verdict from another model family at the exact head) and ship in the same release as the data-loss fixes of 1348. The earlier rule, that they wait for Anton's acceptance before any release, is superseded by D-06.

## Acceptance Criteria

- [x] AC-01: Only an approved request whose ACP tool kind is `execute` lets that agent create client terminals for the turn or session; an approved `switch_mode`, `other`, edit or read request does not.
- [x] AC-02: A Pi "Always allow this session" grant matches only a call with the same tool and the same full arguments; two calls that share the first 4,000 characters and differ later are asked separately.
- [x] AC-03: The ACP Registry installer changes file modes only after the staged command's real path is proven inside the extraction root, and a uv-installed agent is resolved only from the managed bin directory.
- [x] AC-04: A provider sign-in link opens only when it parses as `http:` or `https:`; the contract, `localApi` and the consent path that assigns `pending.location.href` all refuse anything else.
- [x] AC-05: SPA HTML responses carry a header that refuses framing by other origins; the desktop shell and `html_render` still work.
- [x] AC-06: A token request with an invalid or missing subject token writes no DPoP replay marker; a valid request still consumes its proof once and a replay is refused.
- [x] AC-07: A subagent thread waiting on a secret or a link raises the same owner notification as one waiting on an approval.
- [x] AC-08: The ACP MCP stdio bridge answers a server request (for example `ping`) that arrives before the tool result and still returns the result. If our MCP server never sends such requests mid-call, the task records that with evidence and adds the regression test only.
- [x] AC-09: The preview browser pins Chrome 157.0.8103.78 with sizes and hashes from our own downloads; the desktop app pins Electron 44.10.1; Linux packages carry no group or world write bits.
- [x] AC-10: Desktop IPC handlers answer only senders that are app windows (the main frame of every window in `appWindows`: the main window and project windows); a preview guest gets no reply. Picture-in-picture and the Mac permission helper never call these handlers (PiP only receives frames, the helper has its own channel with its own sender check), so nothing they do is refused.
- [x] AC-13: The secret request field is a real password input, still ignored by password managers (`SecretRequestCard.tsx:139`).
- [x] AC-14: MCP authentication runs in its own span that ends before the tool call; per-tool spans carry no arguments (`McpHttpServer.ts:239`).
- [x] AC-15: An idle MCP token expires after its idle limit even when the wall clock steps back and stays expired; a record restored after a restart is judged by wall time from its persisted `lastAliveAt` and is expired when the clock reads earlier than that (`McpSessionRegistry.ts:251`).
- [x] AC-11: Every port has a test that fails on the pre-fix code, recorded in `reports/red-green.md`; every PR has green CI and a ship verdict from another model family at its merged head.
- [x] AC-12: The public repository gains no mention of the upstream project in files, commits, branches or PR text; the MIT copyright line stays.

## Approach

One app worktree. Ports are written in parallel on an integration branch with one owner per file, then each PR branch is cut from `origin/main` by cherry-pick. Upstream diffs are read from `~/.specwithcode/m4/scratch/2026-11-14-t3-upstream-review/t3code`; lane evidence in `~/.specwithcode/m4/scratch/2026-11-14-t3-upstream-review/out/`.

PRs: (1) ACP approval scope, (2) Pi Always-allow key, (3) DPoP marker order, (4) desktop IPC sender check, (5) installer, sign-in link and framing, (6) subagent secret and link waits, (7) Chrome and Electron bumps. AC-08 travels with the ACP protocol PR of 1348 because it shares files.

Risks: the IPC guard must trust all of `appWindows` (`ElectronWindow.ts:126`), not the main window. The Electron bump needs a desktop smoke on macOS; Windows and Linux are covered by CI packaging only.

## Review
- Reviewer: google (gemini-4-neon)
- Depth: deep
- Required: yes

## Decisions

### Asked
- D-01 Which changes wait for Anton before release → permissions, auth and access: AC-01, AC-02, AC-06 (user, November 14, 2026). AC-10 is treated the same because it changes who may call desktop IPC. Superseded by D-06.
- D-06 Do the permission and auth PRs merge with the rest → yes. Asked whether "merge everything" includes the permission and auth PRs, with the recommendation to merge them with the rest once green and reviewed, Anton answered on November 15, 2026: "yes, it includes it, yes do as recommended". PRs 448, 449, 450, 451 and the ACP approval scope PR merge on the same bar as the others and ship in the same release; no separate acceptance step. The "Do not merge yet" line is removed from each PR when it merges.
- D-07 Which model reviews → Gemini 4 Neon on Copilot Enterprise (`acpRegistry_copilot`, `gemini-4-neon`, effort high), then GPT-6.2 Sol. Anton, November 20, 2026: "Make sure for all tasks, switch the adversarial model to something else, for example, GPT 6.2 Sol. Or maybe actually use a Gemini Neon model that is released today from the GitHub Enterprise." The `## Review` line was `meta` until November 22, 2026; the ten Muse reviews of November 15 and the Sol reviews of PR 452 stay as PR evidence, and the follow-up PRs and the closing review run on Neon.
- D-08 Electron 44.10.1 against the lockfile audit → a dedicated PR that bumps the pin and adds reviewed entries for exactly this replacement to `scripts/studio-toolchain/reviewed-lock-changes.json`, merged with a merge commit so the named lock commit stays on main. This was the recommended option; taken on November 22, 2026 under Anton's standing approval of that day: "Do use all recommended. Where you wanted me to ask, just use recommended. That's my confirmed approach." 44.10.1 stays the target (AC-09); 44.11.5 was published on November 19, 2026 and is left for a later bump.
### Defaulted (change any before sw-do)
- D-02 Held PRs stay unmerged until Anton accepts. Any thread may request a release at any time and a release takes all of main, so a merged PR could ship before acceptance. Superseded by D-06 on November 15, 2026.
- D-03 Reviewer is Meta Muse (user's preference). If Muse cannot run, the review waits; no same-family substitute. Superseded by D-07 on November 22, 2026.
- D-04 MCP token records restored after a restart have no monotonic reading: judge them by wall time from `lastAliveAt`, and treat a clock that reads earlier than `lastAliveAt` as expired (fail closed). No longer held (D-06); the rule is stated in the PR body.
- D-05 Upstream commit ids are recorded only in this umbrella increment, not in the app repository's `UPSTREAM.md`, because the user asked that the public repository gain no mention of the upstream project.
- D-09 PRs 449, 450 and 473 were merged on November 15, 2026 at heads whose last review said "fix first", and the ACP approval scope (AC-01) was never opened as a PR. Found on November 22, 2026. Each gap ships as a follow-up PR from current main with its own red and green run and a Neon ship verdict at the merged head: AC-01 with the 473 grant-scope finding, the replay check before the exchange (AC-06), and expiry stored across restarts (AC-15). T-01, T-03 and T-12 count as done only when their follow-up is merged.
- D-10 Only fail-open findings block a merge (Anton's review-loop rule of November 19, 2026); fail-closed leftovers are written into the PR text and listed in `reports/red-green.md`.
- D-11 The closing review at app main `649ce5cf52ee` (November 22, 2026) found one leftover of PR 812 that had been listed as fail-closed to be fail-open: the key retirement fallback of a failed revocation write ran outside the write lock, so an expired token could work after a restart. It shipped as follow-up PR 815 (merge commit `214245559e31`, ship verdict at its merged head), and the increment closes on a second closing review at that commit.
### Open
- none

## Tasks

### T-01 ACP approval scope: only an approved execute request grants client terminals
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpClientPolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpClientPolicy.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/provider/acp/AcpClientPolicy

### T-02 Pi Always-allow keyed on the full call
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/piStudioMcpExtensionSource.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/PiAdapterV2.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/orchestration-v2/Adapters/piStudioMcpExtensionSource src/orchestration-v2/Adapters/PiAdapterV2

### T-03 DPoP proof checked before any marker is written
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/dpop.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/auth

### T-04 Desktop IPC answers only app windows
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/DesktopIpc.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/electron/ElectronWindow.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/ipc

### T-05 Registry installer, sign-in link scheme and frame header
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistrySupport.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/providerSetup.ts, repositories/anton-abyzov/specwithcode/apps/web/src/localApi.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderAuthenticationSection.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/http.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/provider/acp/AcpRegistrySupport src/http

### T-06 Subagent secret and link waits notify the owner
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/agentAwareness.ts, repositories/anton-abyzov/specwithcode/apps/server/src/relay/AgentAwarenessRelay.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && npx vp test run src/agentAwareness

### T-07 Chrome 157 and Electron 44.10.1
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/preview/PreviewBrowser.ts, repositories/anton-abyzov/specwithcode/apps/desktop/package.json, repositories/anton-abyzov/specwithcode/pnpm-lock.yaml | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/preview/PreviewBrowser

### T-08 ACP MCP bridge answers interleaved server requests
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/mcp/AcpMcpStdioBridge

### T-11 Secret field is a password input; MCP auth span ends before the tool call
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/SecretRequestCard.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/mcp/McpHttpServer

### T-12 MCP token expiry survives a clock step back
- AC: AC-15 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpSessionRegistry.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpSessionRegistry.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/mcp/McpSessionRegistry

### T-09 Red-green evidence, reviews and merge of every PR
- AC: AC-11, AC-12 | Files: .specweave/increments/1347-upstream-security-pass/reports/red-green.md | Test: test -s .specweave/increments/1347-upstream-security-pass/reports/red-green.md

### T-10 Verify and close 1347
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15 | Files: .specweave/increments/1347-upstream-security-pass/ | Test: specweave verify 1347
