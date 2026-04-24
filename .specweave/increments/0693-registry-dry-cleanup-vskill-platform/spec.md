---
increment: 0693-registry-dry-cleanup-vskill-platform
title: "Registry DRY: deprecate AGENT_CONFIG_PREFIXES duplicates"
type: refactor
priority: P1
project: vskill-platform
---

# 0693 — Registry DRY: deprecate AGENT_CONFIG_PREFIXES duplicates

## Problem

The canonical agent-config-prefix mapping lives in `vskill/src/agents/agents-registry.ts` (`AGENTS_REGISTRY`, 49 agents). Three separate copies of an `AGENT_CONFIG_PREFIXES` array (27 hardcoded prefixes) exist in vskill-platform, plus an `EXTRA_CONFIG_DIRS` constant in vskill itself that mixes registry-derived dirs with ad-hoc non-agent dirs (`.specweave`, `.vscode`, `.idea`, `.zed`, `.devcontainer`, `.github`, `.agents`, `.agent`).

Adding a new agent to AGENTS_REGISTRY today requires manually updating 4 places. Drift is inevitable.

## Goals

1. Single source of truth for agent prefixes (canonical: `AGENTS_REGISTRY`)
2. Co-locate non-agent config dirs with the agents registry (one audit point)
3. Allow plain-JS crawl-worker code to consume the registry without a TS toolchain

## Non-Goals

- Restructuring AGENTS_REGISTRY internals
- Changing the AgentDefinition shape
- Touching vskill UI/server code (eval-ui, eval-server)

## User Stories

### US-001: Crawler imports prefix list from canonical registry
**Project**: vskill-platform
**As a** vskill-platform crawler maintainer
**I want** the agent-prefix list to come from a single source of truth
**So that** adding a new agent in vskill auto-flows to the crawler without copy-paste

**Acceptance Criteria**:
- [x] **AC-US1-01**: `vskill-platform/src/lib/skill-path-validation.ts` no longer hardcodes `AGENT_CONFIG_PREFIXES`; imports/derives from a shared source
- [x] **AC-US1-02**: `vskill-platform/crawl-worker/sources/queue-processor.js` no longer hardcodes the prefix list
- [x] **AC-US1-03**: `vskill-platform/crawl-worker/lib/repo-files.js` no longer hardcodes the prefix list
- [x] **AC-US1-04**: All 3 files reference a single canonical export (e.g., a generated `agents.json`)

### US-002: NON_AGENT_CONFIG_DIRS co-located with registry
**Project**: vskill
**As a** vskill skill-scanner maintainer
**I want** non-agent config dirs (`.specweave`, `.vscode`, `.idea`, `.zed`, `.devcontainer`, `.github`, `.agents`, `.agent`) co-located with the agents registry
**So that** there's one audit point for all known config directories

**Acceptance Criteria**:
- [x] **AC-US2-01**: `vskill/src/agents/agents-registry.ts` exports `NON_AGENT_CONFIG_DIRS` containing the current 8 entries
- [x] **AC-US2-02**: `vskill/src/eval/skill-scanner.ts` imports `NON_AGENT_CONFIG_DIRS` from the registry instead of defining `EXTRA_CONFIG_DIRS` locally
- [x] **AC-US2-03**: Existing skill-scanner tests still pass

### US-003: Build-step JSON manifest for crawler consumption
**Project**: vskill-platform
**As a** vskill-platform crawler (plain JS)
**I want** to consume the registry without needing TypeScript imports
**So that** the JS workers stay simple and don't need a TS toolchain

**Acceptance Criteria**:
- [x] **AC-US3-01**: A build script (in vskill) emits `agents.json` containing the prefix list and `nonAgentConfigDirs`
- [x] **AC-US3-02**: Crawler files load from this JSON at startup, NOT a hardcoded array
- [x] **AC-US3-03**: Build script is wired into vskill's existing build pipeline; vskill-platform copies via prebuild

## Out of Scope

- Migrating to a published npm package for the registry (future)
- Auto-generating AgentDefinition from frontmatter scanning
