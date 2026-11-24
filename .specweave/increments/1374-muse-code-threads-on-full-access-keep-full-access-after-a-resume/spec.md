# Muse Code threads on Full access keep full access after a resume

## Problem

On November 17, 2026 the EasyChamp coordinator (machine m4, Muse Code, `muse-wonder-1.0`, thread on Full access) could not launch a worker and told Anton:

> **Blockers:** Restart this coordinator session with approval prompts enabled (the launch flags are fixed for a running session), then say "continue".

It quoted two errors: `connect EPERM 127.0.0.1:8319 - Local (0.0.0.0:0)` and `tool denied: unsandboxed execution requires human approval, but approval prompts are disabled`. Anton answered "Yes, I enable and approve it." and got the same denial again.

The restart advice is the model's guess. No restart, setting or approval can fix it, because the app itself builds the state:

- The thread's Muse session `01a18649-9769-74f0-b347-385a64ffd481` was created on October 29, 2026. Its log commits the permission profile `:auto-review`: commands run in a sandbox with `local_command_network: proxy_only`, and an escalation needs an approval.
- `apps/server/src/provider/muse/MuseRuntime.ts:99` sends no `permissionProfile` when the thread is on Full access. On `session/resume` Muse then keeps the profile the session was created with.
- `MuseRuntime.ts:181` still switches the approval mode to `allowAll`, which turns approval prompts off.

The result is a sandboxed shell that cannot reach `127.0.0.1:8319` (the app's own tool endpoint) and cannot ask to leave the sandbox. Every SpecWithCode tool call fails, so a coordinator cannot delegate. The same denials are in that session's log from October 29, so it has been broken since its first day. Run 872 was a freshly started Muse host, which proves a restart does not help.

Reproduced on Muse Code 1.4.23 with the app's own call sequence (`reports/muse-probe-result.json`): a session stored as `:auto-review` and driven with `allowAll` prints exactly both errors; resuming the same session from a new host with `permissionProfile: ":unrestricted"` commits the new profile and the same command prints `node ok 200`.

A session started today with `allowAll` and no profile already resolves to `:unrestricted`, so only resumed sessions with an older stored profile are affected: sessions created by an older Muse Code, and threads that were switched from Supervised (`:ask-me`) to Full access.

This is not the gap closed by increment 1369 (a newly installed CLI is picked up without a restart). That was provider detection; this is the permission state of one resumed session.

A second, smaller problem made the report misleading: when the terminal bridge `acp-mcp-call` cannot connect it dies with a stack trace (`AcpMcpBridgeError: fetch failed`), so the agent invents a cause and a remedy.

## Scope

In: Muse sessions on Full access always select the `:unrestricted` profile at start and at resume; a host that refuses that profile keeps today's behaviour; the terminal bridge names a sandbox-blocked connection in one line with the real remedy.

Out: attaching the app's tools to Muse natively. Muse 1.4.23 grants `sessionMcp` but starts session MCP servers only on a host run with `--trust-workspace` (`reports/muse-probe-result.json`, "native tools"). Trusting a workspace also loads its skills, rules and permission hooks, so it is the owner's decision (Open, D-03). Also out: Supervised threads, which already select `:ask-me` at resume and raise an approval card.

## Acceptance Criteria

- [ ] AC-01: A Muse session started on Full access sends `permissionProfile: ":unrestricted"` with `approvalMode: "allowAll"`, on both the configured (`session/start` command) and the plain (SDK `startSession`) path.
- [ ] AC-02: A Muse session resumed on Full access sends `permissionProfile: ":unrestricted"` on every `session/resume` it makes, so a session stored with `:auto-review` or `:ask-me` is re-committed as unrestricted.
- [ ] AC-03: A Supervised (`approval-required`) Muse session still sends `:ask-me` and `promptUnmatched` at start and resume, and still refuses a host that reports a reviewer other than a person.
- [ ] AC-04: When the host rejects the Full access profile with reason `permission_profile_unknown`, `permission_profile_unavailable` or `permission_profile_ephemeral_fixed`, the session opens without a profile, as it does today. Any other rejection still fails the open. The third reason comes from an ephemeral host, which refuses any profile pick (`@muse-code/sdk` 1.4.11, `msp.d.ts`, `session/start` `permissionProfile`); without the fallback a Full access thread could not open there at all.
- [ ] AC-05: When the host reports the committed permission state and it is not `:unrestricted` after the profile was accepted, the open fails with a message that names Full access, instead of running a sandboxed session silently.
- [ ] AC-06: `acp-mcp-call` that cannot connect because the operating system refused the connection (`EPERM` or `EACCES`) exits 1 and prints one line saying the agent's sandbox blocked the connection to SpecWithCode on this machine, that restarting does not help, and that Full access or approving the unsandboxed call does. Other failures print one line with the cause. No stack trace in either case.
- [ ] AC-07: On the released build (the 1.0.334 service archive on a private server, real Muse Code 1.4.23), a thread whose Muse session was stored with another profile and is then on Full access completes a SpecWithCode tool call (`studio_thread_list`) from the agent's shell with no click: the command exits 0 and its output holds this thread's own entry. The release before it (1.0.333) fails the same command (exit 1) in the same script.

## Approach

1. `apps/server/src/provider/muse/MuseRequests.ts`: add `MUSE_FULL_ACCESS_PROFILE = ":unrestricted"`, `museProfileRefused(error)` (an `MspError` `commandRejected` whose `data.reason` is one of the two profile reasons) and `museRequireProfile(session, profile)`, which keeps the human-reviewer check for `:ask-me` and adds the `:unrestricted` check for Full access. Both checks pass when the host does not report the state: `permissionState` is served only to clients that ask for the experimental surface, which also turns on `admission/*` and 20 other notifications, so this increment does not ask for it.
2. `apps/server/src/provider/muse/MuseRuntime.ts`: the profile is `:unrestricted` for Full access and `:ask-me` otherwise. `open` runs once with the profile; on `museProfileRefused` in Full access it runs again without one and skips the state check.
3. `apps/server/src/mcp/AcpMcpStdioBridge.ts`: `acp-mcp-call` catches a failed call and writes one line; a small exported function turns the error into that line so it is testable.
4. Tests first, in `MuseRuntime.test.ts`, `MuseRequests.test.ts` and a new `AcpMcpStdioBridge.callFailure.test.ts`.

Rejected: `muse serve --disable-sandbox` (host-wide, and unnecessary: the profile is per session and can be re-selected at resume). Starting a new session when the stored profile differs (loses the Muse-side conversation; the resume pick works). Asking for the experimental API to read the state back (changes the notification surface for every Muse thread).

Risk: an older Muse host that ignores an unknown `permissionProfile` member keeps today's behaviour; one that rejects it is covered by AC-04.

## Proof limits

- The released-build criterion was first written for the installed service on m4 and a session stored as `:auto-review`. m4's service still ran 1.0.329 when this closed: it installs an update only after no session has worked for 10 minutes. The check therefore ran the released 1.0.334 archive on a private server, with a session stored as `:ask-me`.
- The `:auto-review` to `:unrestricted` transition on the real CLI is covered at the PR head by `reports/task-T-01-live-runtime.json`; the merged source for those files is the same.
- Not done: a turn in the EasyChamp coordinator itself (Muse session `01a18649-9769-74f0-b347-385a64ffd481`) on 1.0.334. Nothing here shows that thread repaired. What the code should do there, once m4 runs 1.0.334: its next message resumes that session with `:unrestricted`, and the session log gains a second `permission_profile_committed` line. That is the check to make then.
- The full server suite did not run in the verification copy: `specweave-studio checks copy` refused because `~/.specwithcode/m4/verify/specwithcode` held another session's uncommitted `scripts/release/*.sh` edits. A first local run in the thread's own worktree at `bdc69db77` was stopped by the 60-minute background limit with 563 test files passed and none failed. The merge relied on CI's server shards 1/3 to 3/3 at that head, and came before any local full run ended. Closure verify then ran the PR gate (its own server stage off) and the whole server suite in 6 shards under the heavy-check gate, and both passed (`reports/verify.md`). Its first run failed one test, `scripts/linux-update-helper.test.ts`, only because this worktree was checked out under umask 077 and the helper was `0700` on disk; with the checked-in mode restored (`chmod 755`) it passed.
- `permission_profile_ephemeral_fixed` was in the code's fallback list from the first commit but the runtime test opened a session only for the other two reasons, and AC-04 named only two. The closing review caught both. AC-04 now names all three and PR 530 (test only) runs the third at start and resume.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Full access on Muse means the `:unrestricted` profile → yes. It is what a new Full access session already gets today (no profile plus `allowAll` resolves to `:unrestricted` on Muse 1.4.23), and it matches Full access on Claude Code and Codex.
- D-02 A host that refuses `:unrestricted` → open without a profile and log a warning, not a failed thread.
### Open
- D-03 Run Muse session hosts with `--trust-workspace` so the app's tools attach natively (no terminal bridge, no approval card per tool call on Supervised threads). It also loads the project's Muse skills, rules and permission hooks. Owner's call; not in this increment.

## Tasks

### T-01 Full access selects the unrestricted profile at start and resume
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseRequests.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseRuntime.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseRuntime.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseRequests.test.ts | Test: from `apps/server`, `node ../../node_modules/vite-plus/bin/vp test run src/provider/muse`

### T-02 The terminal bridge names a blocked connection
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.callFailure.test.ts | Test: from `apps/server`, `node ../../node_modules/vite-plus/bin/vp test run src/mcp/AcpMcpStdioBridge.callFailure.test.ts`

### T-03 Review, merge and release
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseRuntime.ts | Test: PR 527 checks green at the reviewed head (server shards 1/3 to 3/3, typecheck); cross-family review `Verdict: ship`; `bash scripts/release/request-release.sh --released <merge commit>` exits 0

### T-04 Released-build check on a stale session
- AC: AC-07 | Files: .specweave/increments/1374-muse-code-threads-on-full-access-keep-full-access-after-a-resume/reports/installed-check.md | Test: `node reports/released-check/released-check.mjs <unpacked 1.0.334> <work dir> --tool-call --expect fixed` exits 0 and `... <unpacked 1.0.333> <work dir> --tool-call --expect broken` exits 0; results in `reports/released-check/strict-334-tool.json` and `strict-333-tool.json`
