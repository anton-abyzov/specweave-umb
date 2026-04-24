---
increment: 0694-cli-coverage-warp-amazonq-copilot-split
title: >-
  CLI coverage: add Warp + Amazon Q + split GitHub Copilot CLI/extension +
  isRemoteOnly flag
type: feature
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: CLI coverage: add Warp + Amazon Q + split GitHub Copilot CLI/extension + isRemoteOnly flag

## Overview

Three brand-new agentic terminals went GA in early 2026 (GitHub Copilot CLI standalone, Warp Agent Mode, Amazon Q Developer CLI), and four "agents" already in the vskill registry are actually web-only services with no local install path (Devin, bolt.new, v0, Replit). This increment:

1. Adds the three missing CLI adapters with verified install paths.
2. Splits the conflated `github-copilot` entry into `github-copilot-ext` (VS Code extension) and the new `copilot-cli` (standalone binary).
3. Introduces an `isRemoteOnly: true` flag and gates those four entries from local install flows so Studio shows them with a "Remote" badge instead of broken install actions.
4. Reconciles a Zed-registry mismatch — Zed exists in `specweave/src/adapters/registry.yaml` but is missing from `vskill/src/agents/agents-registry.ts`.

## User Stories

### US-001: GitHub Copilot CLI standalone adapter (P1)
**Project**: vskill

**As a** GitHub Copilot CLI user
**I want** vskill to install skills into the standalone `copilot` binary's config dir
**So that** my skills are picked up by the new CLI separately from the VS Code extension

**Acceptance Criteria**:
- [x] **AC-US1-01**: New registry entry `id: 'copilot-cli'` with `displayName: 'GitHub Copilot CLI'`, `localSkillsDir: '.copilot/skills'`, `globalSkillsDir: '~/.copilot/skills'`, `detectInstalled: 'which copilot'`, `parentCompany: 'GitHub (Microsoft)'`
- [x] **AC-US1-02**: Existing `github-copilot` entry renamed to `github-copilot-ext` with displayName "GitHub Copilot (VS Code)" — keeps `.github/copilot/skills` path
- [x] **AC-US1-03**: Install flow installs to the correct dir based on which agent is selected (verified via dry-run for both `copilot-cli` and `github-copilot-ext`)
- [x] **AC-US1-04**: Migration: anyone consuming the old `github-copilot` id still resolves via `getAgent()` alias (backward compat)

### US-002: Warp Agent Mode adapter (P1)
**Project**: vskill

**As a** Warp Terminal user
**I want** vskill to install skills for Warp's Agent Mode
**So that** my skills are available in Warp's terminal-agent workflow

**Acceptance Criteria**:
- [x] **AC-US2-01**: New registry entry `id: 'warp'` with `displayName: 'Warp'`, `parentCompany: 'Warp'`, `detectInstalled: 'which warp'`, paths verified against https://docs.warp.dev/agent-platform
- [x] **AC-US2-02**: `warp` agent appears in `AGENTS_REGISTRY` and is discoverable via `getAgent('warp')`
- [x] **AC-US2-03**: Install dry-run resolves to the correct skills dir for warp

### US-003: Amazon Q Developer CLI adapter (P1)
**Project**: vskill

**As an** AWS-using developer
**I want** vskill to install skills into Amazon Q Developer CLI's config
**So that** my skills are available in the `q` agentic terminal

**Acceptance Criteria**:
- [x] **AC-US3-01**: New registry entry `id: 'amazon-q-cli'` with `displayName: 'Amazon Q CLI'`, `parentCompany: 'AWS'`, `detectInstalled: 'which q'`, paths verified against https://github.com/aws/amazon-q-developer-cli
- [x] **AC-US3-02**: `amazon-q-cli` is discoverable + installable via `getAgent()`
- [x] **AC-US3-03**: Install dry-run resolves to the correct dir

### US-004: isRemoteOnly flag for web-only agents (P1)
**Project**: vskill

**As a** vskill user
**I want** web-only "agents" (Devin, bolt.new, v0, Replit) to be clearly marked and excluded from local install attempts
**So that** I don't see broken install actions for tools that have no local CLI

**Acceptance Criteria**:
- [x] **AC-US4-01**: `AgentDefinition` interface adds optional `isRemoteOnly?: boolean`
- [x] **AC-US4-02**: Devin / bolt.new / v0 / Replit registry entries set `isRemoteOnly: true`
- [x] **AC-US4-03**: New helper `getInstallableAgents()` returns agents where `isRemoteOnly !== true`
- [x] **AC-US4-04**: Studio AgentScopePicker (and popover) render a "Remote" badge for `isRemoteOnly` agents in install affordances
- [x] **AC-US4-05**: Install commands return a clear error if invoked on a remote-only agent

### US-005: Add Zed entry to vskill registry (P2)
**Project**: vskill

**As a** Zed user
**I want** vskill to recognize Zed as an installable agent
**So that** I can install skills for Zed's agent panel

**Acceptance Criteria**:
- [x] **AC-US5-01**: Registry entry `id: 'zed'` matches the schema in `repositories/anton-abyzov/specweave/src/adapters/registry.yaml` (`.zed/skills/` local dir, MCP supported)
- [x] **AC-US5-02**: Path verified against https://zed.dev/docs/ai/agent-panel

## Open Questions

- If `https://docs.warp.dev/agent-platform` or `https://github.com/aws/amazon-q-developer-cli` are unreachable at implementation time, fall back to documented community defaults (`~/.warp/skills`, `~/.aws/amazonq/skills`) and tag the registry entry with a `// VERIFY` comment.

## Out of Scope

- Removing `devin`, `bolt-new`, `v0`, `replit` entries — kept for catalog completeness; only flagged as remote-only.
- Updating the specweave adapters/registry.yaml to add Warp / Amazon Q / Copilot CLI — that's a separate effort against the specweave repo.
- vskill-platform `agent-branding.ts` featured-list update (T-014 marks NO-OP unless these new agents should be promoted to the homepage 10).
