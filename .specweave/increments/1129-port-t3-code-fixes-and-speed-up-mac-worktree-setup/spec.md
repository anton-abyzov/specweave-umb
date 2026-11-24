# Port T3 Code fixes and speed up Mac worktree setup

## Problem

Theo's 2026-10-28 posts claim thread and worktree setup runs about 8x faster on a cheap Linux PC than on a Mac, and announce "t3os" (a Linux distro tuned for agents). Upstream T3 Code also landed 286 commits since our last comparison (1118, base c4d5950268). A triage of the 142 relevant ones (reports/triage.md) found 62 medium or high value fixes we lack. Measured on the M4: a worktree of our repo writes 31,240 files (70% are .repos reference trees) plus 254k node_modules files, parallel worktree launches can fail on the shared .git/config lock, setup stage timings are thrown away, and the worktrees root is open to Spotlight. A GitHub repository selector like "evil.com#.ghe.com/o/r" can send the user's GitHub token to another host.

## Scope

In: the S/M clear wins listed in Tasks. Out: owner-gated items (fleet access for outside clients, link-a-machine, MCP mode limit header, pairing links, cloudflared pin, GitHub app sign-in), large ports (bounded history pages, composer redesign, triage in palette, MCP action-tool merge, Linux cgroup scopes), Time Machine exclusion (would drop uncommitted work from backups), and changing the setup shell (breaks nvm users).

## Acceptance Criteria

- [ ] AC-01: Parallel worktree launches on one repo do not fail on a locked .git/config; config writes retry and are serialized per repo.
- [ ] AC-02: Each finished worktree setup logs one structured line with per-stage durations (fetch, checkout, submodules, setup script).
- [ ] AC-03: On macOS the worktrees root gets a .metadata_never_index marker (best effort, never fails startup).
- [ ] AC-04: GitHub credentials are only looked up and sent for valid hostnames; malformed hosts in repository selectors are refused.
- [ ] AC-05: MCP tools advertise compact input schemas, and the tool list shrinks.
- [ ] AC-06: Codex fixes: shadow homes share writer locks, a killed app-server recovers, stale usage limits are not replayed.
- [ ] AC-07: Orchestration fixes: threads settle when a watched PR merges, hung delegated stops are bounded, no duplicate queued messages, subagent questions remain owned by their child thread without duplicate parent request cards; parent attention may link the actionable child, interrupted Claude context survives revert.
- [ ] AC-08: Web fixes: file preview wrap toggles stay local, markdown previews hide YAML frontmatter, chat tables open at full size.

## Approach

Port each upstream commit onto our renamed code (port notes in reports/triage.md), one task per area so files do not overlap. Upstream hashes are cited in each commit body. Branch claude/project-thread-upt198 in specweave-studio, one PR.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Spotlight marker only, no Time Machine exclusion → keeps uncommitted worktree work in backups.
- D-02 Setup scripts keep the interactive login shell → measured 6.5s cost is from the owner's ~/.zshrc; recommended as a user tip instead.
- D-03 Preserve #883/#899 live child-question visibility: this fork does not copy child requests into the parent shell. Keep aggregateProjectAttention linking the original child question; do not apply upstream 975b3dc568 to hide it. Verified against 7e32514e7a and packages/client-runtime/src/state/projectAttention.ts/tests.
### Open
- none

## Tasks

### T-01 Worktree config lock, stage timings, Spotlight marker
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/GitVcsDriverCore.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/WorktreeSetupTracker.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/config.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/git.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/GitVcsDriver.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/git/GitWorkflowService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/sourceControl/GitHubCli.ts, and focused tests for these files | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && node node_modules/vite-plus/bin/vp test run apps/server/src/vcs apps/server/src/project/WorktreeSetupTracker

### T-02 GitHub token host check
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/sourceControl/GitHubCredentials.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/sourceControl/GitHubCli.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && node node_modules/vite-plus/bin/vp test run apps/server/src/sourceControl

### T-03 Compact MCP schemas
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/advertisedJsonSchema.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/McpHttpServer.ts, and focused MCP schema tests | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/advertisedJsonSchema apps/server/src/mcp/McpHttpServer

### T-04 Codex fixes
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/codexUsageLimits.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/Drivers/CodexHomeLayout.ts, repositories/anton-abyzov/specweave-studio/packages/effect-codex-app-server/src, and focused usage-limit/home-layout tests | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/Codex

### T-05 Orchestration fixes
- AC: AC-07 | Files: repositories/anton-abyzov/specweave-studio/packages/shared/src/orchestrationV2PendingBackgroundWork.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src, repositories/anton-abyzov/specweave-studio/apps/web/src/session-logic.ts, repositories/anton-abyzov/specweave-studio/apps/mobile/src/lib/threadActivity.ts, and focused session logic/thread activity tests | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && node node_modules/vite-plus/bin/vp test run packages/shared/src/orchestrationV2PendingBackgroundWork apps/server/src/orchestration-v2 packages/client-runtime/src

### T-06 Web fixes
- AC: AC-08 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/files, repositories/anton-abyzov/specweave-studio/apps/web/src/components/MarkdownTable.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/index.css, repositories/anton-abyzov/specweave-studio/apps/web/src/components/ChatMarkdown.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/lib/markdownFrontmatter.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/settingsSearch.ts, and focused tests/fixtures for these files | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && node node_modules/vite-plus/bin/vp test run apps/web/src/components/files apps/web/src/components/MarkdownTable

### T-07 Verify and close 1129
- AC: AC-01, AC-08 | Files: .specweave/increments/1129-port-t3-code-fixes-and-speed-up-mac-worktree-setup/reports/verify.md, repositories/anton-abyzov/specweave-studio/CHANGELOG.md, repositories/anton-abyzov/specweave-studio/UPSTREAM.md | Test: specweave verify 1129-port-t3-code-fixes-and-speed-up-mac-worktree-setup

### T-08 Repair exact-head CI typecheck diagnostics
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/advertisedJsonSchema.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/McpToolListSchemas.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/t3os-upt198 && bash scripts/studio-verify/typecheck-gate.sh --package apps/server --jobs 1
