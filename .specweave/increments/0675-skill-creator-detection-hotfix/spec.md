---
increment: 0675-skill-creator-detection-hotfix
title: >-
  Hotfix: isSkillCreatorInstalled() misses localSkillsDir and marketplace
  installs
type: hotfix
priority: P1
status: completed
created: 2026-04-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Hotfix: `isSkillCreatorInstalled()` Misses Common Install Locations

## Overview

`npx vskill studio` (Skill Studio web UI) renders a yellow **"Skill Creator not installed"** banner in the left panel even when `skill-creator` IS installed on disk. The shared detection utility `isSkillCreatorInstalled()` misses two common install locations. This hotfix widens detection so the banner reflects reality.

## Problem Statement

`src/utils/skill-creator-detection.ts::isSkillCreatorInstalled(projectRoot?)` powers the Studio widget (via `GET /api/skill-creator-status`) and the `vskill eval serve` CLI boot-time check. Today it only probes:

1. `~/.agents/skills/skill-creator`
2. `{projectRoot}/.agents/skills/skill-creator` — hardcoded `.agents/skills/` segment
3. Each agent's **`globalSkillsDir`** (e.g., `~/.claude/skills/skill-creator`)
4. Each agent's **`pluginCacheDir`** tree (Claude Code = `~/.claude/plugins/cache/{mkt}/{plugin}/`)

This misses:

- **Project-local agent installs**: `{projectRoot}/{agent.localSkillsDir}/skill-creator/` — e.g., `{projectRoot}/.claude/skills/skill-creator/`, `{projectRoot}/.cursor/skills/skill-creator/`. Every `AgentDefinition` carries a `localSkillsDir` field, but the detection function never consults it.
- **Marketplace-synced skills**: `~/.claude/plugins/marketplaces/{marketplace}/plugins/{plugin}/skills/skill-creator/`. This is where `claude plugin marketplace add` materializes SKILL.md content; structurally different from the plugin-install `cache/` tree.

**Reproducer (current codebase):**

```
$ ls /Users/antonabyzov/Projects/github/specweave-umb/.claude/skills/skill-creator/
SKILL.md  scripts  ...
$ npx vskill studio
# Left panel shows: "Skill Creator not installed"
```

The `.claude/skills/skill-creator/` path IS a valid Claude Code skill location (matches `agents-registry.ts` `localSkillsDir: '.claude/skills'` for `claude-code`), but step 2 only checks the hardcoded `.agents/skills/` variant.

## Goals

- `isSkillCreatorInstalled(projectRoot)` returns `true` when `skill-creator/` exists under any registered agent's `localSkillsDir` below `projectRoot`.
- `isSkillCreatorInstalled()` returns `true` when a marketplace-synced `skill-creator` SKILL.md exists in Claude Code's `~/.claude/plugins/marketplaces/` tree.
- Zero regressions in the 4 existing detection paths.
- `vskill eval serve` boot-time check benefits — it currently drops `projectRoot`, defeating step 2 and the new step 2b.
- Strict TDD: failing tests written first, full existing suite stays green.

## Non-Goals

- No changes to Studio UI copy, wording, or layout.
- No `skill-builder` recommendation logic (tracked in 0670-skill-builder-universal once the skill-builder SKILL.md ships).
- No re-architecture of `AGENTS_REGISTRY` — only one new optional field added.
- No parsing of `~/.claude/plugins/installed_plugins.json` — on-disk presence is authoritative for Studio's purposes.

## User Stories

### US-001: Detect Project-Local Agent-Native Installs (P1)
**Project**: vskill

**As a** developer who installed `skill-creator` into the project via `vskill install` or `claude plugin install` (landing at `{projectRoot}/.claude/skills/skill-creator/` or the equivalent agent-native path)
**I want** Skill Studio to recognize the install and show the green "installed" state
**So that** I am not told to run an install command for a skill I already have

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a sandbox directory `tmp` with `tmp/.claude/skills/skill-creator/` on disk and no other skill-creator instances anywhere, when `isSkillCreatorInstalled(tmp)` is called, then it returns `true`.
- [x] **AC-US1-02**: Given a sandbox `tmp` with `tmp/.cursor/skills/skill-creator/` and nothing else, when `isSkillCreatorInstalled(tmp)` is called, then it returns `true` (proves the fix is generic across all registered agents, not hardcoded to Claude Code).
- [x] **AC-US1-03**: Given a sandbox `tmp` with `tmp/.opencode/skills/skill-creator/` and nothing else, when `isSkillCreatorInstalled(tmp)` is called, then it returns `true`.
- [x] **AC-US1-04**: Given `projectRoot` is `undefined` (global-scope detection only) and no global install exists, when `isSkillCreatorInstalled()` is called, then it returns `false` — the new local-scope branch must be guarded by `if (projectRoot)` and never fabricate a projectRoot.
- [x] **AC-US1-05**: The loop scanning `AGENTS_REGISTRY` iterates `agent.localSkillsDir` (not hardcoded strings) so adding a new agent to the registry auto-expands detection.
- [x] **AC-US1-06**: `checkSkillCreator()` at `src/commands/eval/serve.ts:27-47` passes the already-resolved `root` argument to `isSkillCreatorInstalled()`. The call is currently `isSkillCreatorInstalled()` (no args) — update to `isSkillCreatorInstalled(root)`.

### US-002: Detect Marketplace-Synced Claude Code Installs (P1)
**Project**: vskill

**As a** developer who synced the Anthropic skills marketplace via `claude plugin marketplace add` (materializing SKILL.md content at `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/`)
**I want** Skill Studio to recognize the synced copy as an install
**So that** the banner matches what Claude Code itself considers available

**Acceptance Criteria**:
- [x] **AC-US2-01**: `AgentDefinition` in `src/agents/agents-registry.ts` has a new optional field `pluginMarketplaceDir?: string` with a JSDoc line explaining its difference from `pluginCacheDir` (marketplaces hold marketplace sources under `{dir}/{marketplace}/plugins/`; cache holds installed plugins under `{dir}/{marketplace}/{plugin}/`).
- [x] **AC-US2-02**: The `claude-code` entry in `AGENTS_REGISTRY` has `pluginMarketplaceDir: '~/.claude/plugins/marketplaces'` populated.
- [x] **AC-US2-03**: Given a mocked `homedir()` = `tmp` with `tmp/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/` on disk and nothing else, when `isSkillCreatorInstalled()` is called, then it returns `true`.
- [x] **AC-US2-04**: Given a mocked `homedir()` = `tmp` with `tmp/.claude/plugins/marketplaces/some-other-marketplace/plugins/nothing-related/` on disk (marketplace exists but skill-creator does not), when `isSkillCreatorInstalled()` is called, then it returns `false` — the walker must look for a plugin whose name contains `skill-creator`, not merely presence of any marketplace directory.
- [x] **AC-US2-05**: No other agent (cursor, opencode, etc.) has `pluginMarketplaceDir` set — marketplaces are a Claude Code concept. Introducing the field for Claude Code only is intentional and forward-compatible.

### US-003: Preserve Existing Detection Paths (P1)
**Project**: vskill

**As a** maintainer
**I want** every existing detection path to keep working
**So that** adding the two new paths does not regress users currently detected correctly

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a mocked `homedir()` = `tmp` with `tmp/.agents/skills/skill-creator/` on disk (path 1, global canonical), when `isSkillCreatorInstalled()` is called, then it returns `true`.
- [x] **AC-US3-02**: Given a sandbox `proj` with `proj/.agents/skills/skill-creator/` on disk (path 2, project canonical), when `isSkillCreatorInstalled(proj)` is called, then it returns `true`.
- [x] **AC-US3-03**: Given a mocked `homedir()` = `tmp` with `tmp/.claude/skills/skill-creator/` on disk (path 3, via claude-code `globalSkillsDir`), when `isSkillCreatorInstalled()` is called, then it returns `true`.
- [x] **AC-US3-04**: Given a mocked `homedir()` = `tmp` with `tmp/.claude/plugins/cache/foo-marketplace/skill-creator-plugin/` on disk (path 4, via claude-code `pluginCacheDir`), when `isSkillCreatorInstalled()` is called, then it returns `true`.
- [x] **AC-US3-05**: Given a completely empty sandbox (no home skills, no project skills, no caches, no marketplaces), when `isSkillCreatorInstalled(projectRoot)` is called, then it returns `false`.

### US-004: Tests (P1)
**Project**: vskill

**As a** CI gatekeeper
**I want** a focused Vitest file covering all six detection branches
**So that** future refactors cannot silently regress any path

**Acceptance Criteria**:
- [x] **AC-US4-01**: New test file at `src/utils/__tests__/skill-creator-detection.test.ts` exists.
- [x] **AC-US4-02**: Tests use `mkdtempSync(join(tmpdir(), "vskill-skd-"))` sandboxes with `beforeEach/afterEach` cleanup via `rmSync(..., { recursive: true, force: true })` — same pattern as `src/lockfile/project-root.test.ts:1-61`.
- [x] **AC-US4-03**: `homedir()` is mocked via `vi.hoisted` + `vi.mock("node:os", ...)` so the global canonical path and agent `globalSkillsDir`/`pluginCacheDir`/`pluginMarketplaceDir` paths can be driven by fixtures inside the sandbox.
- [x] **AC-US4-04**: One test case per AC (AC-US1-01 through AC-US3-05, one case per AC). Each test creates exactly the fixture it needs and asserts the expected `true`/`false` outcome.
- [x] **AC-US4-05**: Running `npx vitest run src/utils/__tests__/skill-creator-detection.test.ts` reports all tests passing after the GREEN step. Before the implementation lands (test file only), at least AC-US1-01, AC-US1-02, and AC-US2-03 must FAIL — this is the RED gate.
- [x] **AC-US4-06**: Full suite (`npx vitest run`) stays green — no regressions in eval-server, eval-ui, or command tests.

## Success Criteria

- Reproducer clears: opening `npx vskill studio` from `/Users/antonabyzov/Projects/github/specweave-umb/` shows the green "Skill Creator installed" banner.
- `curl http://localhost:{PORT}/api/skill-creator-status` returns `{"installed": true}` when the project-local install exists.
- `npx vitest run src/utils/__tests__/skill-creator-detection.test.ts` all tests passing.
- `npx vitest run` full suite stays green.
- `npx tsc --noEmit` reports 0 errors.

## Out of Scope (Follow-ups)

- Skill-builder UI recommendation in LeftPanel → handled by increment 0670-skill-builder-universal (new AC under US-002 once skill-builder SKILL.md ships).
- Wording refresh / redesign of the "Skill Creator" widget copy → owned by increment 0674-vskill-studio-redesign.
- Parsing of `~/.claude/plugins/installed_plugins.json` to detect active-but-not-materialized plugins → unnecessary; on-disk presence is authoritative for Studio's purposes.
