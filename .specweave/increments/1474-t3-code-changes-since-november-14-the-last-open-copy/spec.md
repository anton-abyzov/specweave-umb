# 1474 T3 Code changes since November 14, the last open copy

## Problem

On November 24, 2026 at 19:52 UTC Theo posted that T3 Code's source closes "tonight" (https://x.com/theo/status/2125316769858683312). The last full review of upstream ended at `v0.1.10-nightly.20261114.4709` (increment 1346). Since then upstream shipped 2,131 non-merge commits up to `main` `4065801a00` (tag `v0.1.12-nightly.20261124.5209` is its nearest nightly), including security and privacy fixes with plain `fix(...)` titles. If the repository closes, this is the last copy we can read, and every fix we have not ported is lost to us.

## Scope

In: an archive of the last open copy for the records; a verdict for every commit since the last sync point (applies, already-have, planned elsewhere, skip) with our `path:line`; a saved report; planning and coordinating the implementation in follow-up increments, security first; the sync-point memory.

Out: the code changes themselves. They live in the wave 1 security increments and the wave 2 bug, speed and feature increments this one launches (listed in Approach), each with its own spec, tests, PRs and review.

## Acceptance Criteria

- [ ] AC-01: `~/.specwithcode/m4/evidence/t3-code/v0.1.12-nightly.20261124.5209/` holds a source tarball of the tag and of `main` `4065801a00`, a full-history bundle that passes `git bundle verify`, the commit log and file log since `v0.1.10-nightly.20261114.4709`, the release notes since November 14, the MIT license text and `SHA256SUMS`; a second copy of the bundle is on m4.
- [ ] AC-02: `reports/all-changes.tsv` has exactly one row for each of the 2,131 commits in the range, each with a class, a verdict and, for applies and already-have, our `path:line`.
- [ ] AC-03: A report with the summary, every security row and the implementation plan is saved in `reports/`.
- [ ] AC-04: Every security row with verdict applies is owned by a wave 1 increment (or by 1349, 1434 or 1450 where those already own the file), and every held row names the decision it waits on.
- [ ] AC-05: The wave 1 increments are merged, or each open one is listed with its state, and a release is requested for what merged.
- [ ] AC-06: The wave 2 increments are launched after wave 1, each owning a disjoint set of files.
- [ ] AC-07: Project memory "T3 sync point" names `4065801a00` as the new full sync point.

## Approach

Triage ran in 11 read-only lanes on M5 (9 by area and date, 2 security lanes selected by path and keyword over 548 commits). Lane files, the brief and the merge script are in `reports/lanes/`. The merge keeps an area lane's applies unless a security lane read the diff and cited our code as already fixed; disagreements are in `reports/contested.tsv`.

Ports follow the standing rule (project memory "t3 upstream port policy", 1347 D-05): rewrite in our own code, no upstream history, no upstream names in the public repository's files, commits, branches or PR text; upstream shas appear only in this umbrella increment. MIT notices stay as they are.

Wave 1, security (74 candidate rows), four increments with disjoint files:

- A, server access and sign-in (M5): `apps/server/src/auth`, `cloud`, `cli/auth.ts`, `cli/uninstall.ts`, `device`, `server.ts`, `http.ts`, `startupAccess.ts`, `atomicWrite.ts`, `mcp/McpHttpServer.ts`, `mcp/toolkits/project`, `htmlRender/headlessChrome.ts`, `packages/contracts/src/settings.ts`, `packages/shared/src/htmlRender.ts`, and the mode-limit check in `orchestration-v2/Orchestrator.ts`.
- B, agent approvals, provider isolation and analytics privacy (M5): `orchestration-v2/Adapters`, `provider/`, `textGeneration`, `ProviderTurnStartService.ts`, `ProviderEventIngestor.ts`, `telemetry`, `packages/effect-acp`, `apps/web/src/session-logic.ts`.
- C, repository, pull request, asset and preview-browser safety (m4): `sourceControl`, `project/`, `pullRequest`, `assets`, `scheduledTasks`, `preview`, `ProjectionStore.ts`, `packages/shared/src/git.ts`, `packages/contracts/src/assets.ts`.
- D, desktop preview consent, client pairing guards and relay privacy (M5): `apps/desktop`, the web Push action and terminal cursor, `packages/client-runtime/src/connection`, `packages/shared/src/hostClassification.ts`, Android pairing input, `infra/relay`.

Wave 2, after wave 1 merges (560 rows, of which many are small): orchestration core and MCP tools (84), provider adapters (105), server git, projects, terminals, files, preview, PRs and CLI (138), web chat and composer (53), other web (87), desktop, SSH, client runtime, shared, relay and phones (93).

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Security tightenings in auth and access merge on the 1347 D-06 bar (green required checks, a cross-family ship verdict at the exact head) under the owner's November 22 rule to take recommended options. Anything that adds or loosens an auth path waits for the owner: `dd512d86c5` (pairing-link sessions renew with the device key). Each tightening's AC names what must keep working (uploads and folder copy under a body limit, the browser extension under the `/mcp` origin rule, older fleet machines and phones under scope changes, the pick preload under `contextIsolation`).
- D-02 A security row whose exploit is not shown by a failing test is recorded as "not reproduced" with the test kept, not shipped as a speculative change. Unverified rows `32653fe18c`, `1adc05b844`, `fe1f1a5732`, `82af3cf2c3`, `42a5aade84`, `fa5fde4bea` and `0d6fe2141a` are settled this way.
- D-03 The 14 rows marked planned-1450 stay with 1450; the settle-and-wake rows `2c3d3b4501` and `d4d54658f9` go to 1349; `dbee5a0af0` goes to 1434. Their owners add ACs when they start.
- D-04 The relay rows ship through the relay's own release track, not the app release. Deleting relay data when Clerk deletes a user needs a Clerk webhook signing secret only the owner can create.
- D-05 Reviews run on Gemini 4 Neon (Copilot Enterprise) when it has quota, else GPT-6.2 Sol, never Grok (project memory, November 20). Only fail-open findings block a merge (1347 D-10).
- D-06 The 16 commits upstream pushed after `4065801a00` while this ran are archived and listed, judged by title only, for the next audit.

### Open
- none

## Tasks

### T-01 Archive the last open copy
- AC: AC-01 | Files: .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/archive.md | Test: test -s .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/archive.md

### T-02 Verdict for every commit
- AC: AC-02 | Files: .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/all-changes.tsv, .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/all-changes.md, .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/lanes/ | Test: test "$(tail -n +2 .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/all-changes.tsv | cut -f1 | sort -u | wc -l | tr -d ' ')" = 2131

### T-03 Save the report
- AC: AC-03 | Files: .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/2026-11-25-t3-code-triage-november-14-to-25-2026-the-last-o-c74c40-c6ed90.md | Test: test -s .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/2026-11-25-t3-code-triage-november-14-to-25-2026-the-last-o-c74c40-c6ed90.md

### T-04 Launch and land wave 1
- AC: AC-04, AC-05 | Files: .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/waves.md | Test: test -s .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/waves.md

### T-05 Launch wave 2
- AC: AC-06 | Files: .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/waves.md | Test: grep -q "Wave 2" .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/waves.md

### T-06 Move the sync point
- AC: AC-07 | Files: .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/archive.md | Test: grep -q 4065801a00 .specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/archive.md

Verify and close 1474.
