---
increment: 0665-obsidian-brain-skill-studio
title: Obsidian Brain Skill + Skill Studio Agent-Aware Extension
type: feature
priority: P1
status: completed
created: 2026-04-14T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Obsidian Brain Skill + Skill Studio Agent-Aware Extension

## Overview

Two workstreams in vskill:

**WS1 — obsidian-brain skill** (`plugins/personal/skills/obsidian-brain/`): Codifies the Karpathy LLM Wiki vault management pattern into a distributable, parametric SKILL.md. Three operations (ingest, query, lint), scheduled via CronCreate, with credential detection and filesystem-only fallback.

**WS2 — Skill Studio agent-aware extension** (`src/`): Extends the existing Skill Studio with agent-aware routing for multi-platform skill creation. Smart routing in existing prompts — not separate prompts per agent. The existing BODY_SYSTEM_PROMPT IS the Claude path; extension adds conditional agent-aware sections for non-Claude targets.

## User Stories

### US-001: Parametric Skill Definition (P1)
**Project**: vskill

**As a** vault owner
**I want** to install a parametric obsidian-brain skill that adapts to my vault layout
**So that** I can manage any Obsidian vault without editing the skill source

**Acceptance Criteria**:
- [x] **AC-US1-01**: SKILL.md exists at `plugins/personal/skills/obsidian-brain/SKILL.md`, under 500 lines, with frontmatter (description, allowed-tools including Read, Write, Glob, Grep, Bash, CronCreate)
- [x] **AC-US1-02**: SKILL.md references parametric config block (`vault_path`, `para_folders`, `wiki_dir`, `inbox_dir`, `log_file`, `index_file`) — no hardcoded personal paths in the distributable file
- [x] **AC-US1-03**: `references/` directory contains: `vault-schema.md` (3-layer architecture spec), `routing-rules.md` (PARA routing table), `wiki-format.md` (frontmatter types, naming, linking conventions), `cron-setup.md` (schedule config and pre-flight check)
- [x] **AC-US1-04**: `scripts/` directory contains: `detect-changes.sh` (inbox file count + recent modifications), `update-index.sh` (regenerate wiki/index.md from wiki pages), `lint-check.sh` (orphan detection, missing cross-refs, inbox backlog count)
- [x] **AC-US1-05**: `evals/evals.json` contains test cases covering each operation (ingest, query, lint) with expected behaviors
- [x] **AC-US1-06**: Zero credential content, zero personal routing rules, zero hardcoded paths appear in SKILL.md or any file under `obsidian-brain/`

---

### US-002: Inbox Ingestion with Credential Guard (P1)
**Project**: vskill

**As a** vault owner
**I want** new files in inbox to be ingested into wiki pages and routed to PARA folders with credential detection
**So that** knowledge is organized automatically and sensitive data never leaks into wiki

**Acceptance Criteria**:
- [x] **AC-US2-01**: Ingest operation reads files from configured `inbox_dir`, creates/updates wiki pages, updates related pages, updates `index.md`, appends to `log.md`, and moves originals to appropriate PARA folder per routing rules
- [x] **AC-US2-02**: Wiki pages created during ingest use correct frontmatter format (type: entity|concept|source|synthesis|map, title field), wikilink cross-references, and naming convention (slugified, sources get YYYY-MM-DD prefix)
- [x] **AC-US2-03**: Log entries follow format `YYYY-MM-DD HH:MM | PREFIX | page | details` with correct prefixes (+page, ~page, >ingest, @link)
- [x] **AC-US2-04**: Credential detection: when content contains passwords, API keys, tokens, or secrets, the skill STOPS ingestion for that file, routes it to the configured credentials folder, and logs a warning — never creates a wiki page from credential content
- [x] **AC-US2-05**: Source files are never modified during ingest — only read, then moved to PARA destination

---

### US-003: Cross-cutting Query Synthesis (P1)
**Project**: vskill

**As a** vault owner
**I want** to query across the vault for synthesized answers spanning multiple notes
**So that** I can leverage my knowledge base for complex questions without manual searching

**Acceptance Criteria**:
- [x] **AC-US3-01**: Query operation reads `index.md` to identify relevant pages, reads those pages, and produces a synthesized answer with source citations (wikilinks)
- [x] **AC-US3-02**: When a query produces a novel synthesis or comparison, the result is optionally filed as a new wiki page (type: synthesis) with proper frontmatter, cross-references, and log entry (`?query` prefix)
- [x] **AC-US3-03**: Query works with filesystem tools only (Read, Glob, Grep) — no dependency on Obsidian app or CLI being available

---

### US-004: Vault Lint Health Check (P1)
**Project**: vskill

**As a** vault owner
**I want** periodic health checks that catch organizational issues in my vault
**So that** I maintain wiki quality and catch problems before they compound

**Acceptance Criteria**:
- [x] **AC-US4-01**: Lint operation checks for: orphan wiki pages (not in index), missing concept pages (mentioned but not created), missing cross-references between related pages, inbox backlog exceeding threshold (default: 10 files)
- [x] **AC-US4-02**: Lint uses `scripts/lint-check.sh` for deterministic checks (file counts, orphan detection) and LLM analysis for semantic checks (contradictions, stale info)
- [x] **AC-US4-03**: Lint report outputs findings categorized by severity (error, warning, info) with actionable fix suggestions
- [x] **AC-US4-04**: Log entries for lint use `!lint` prefix with summary of findings

---

### US-005: Scheduled Autonomous Operation (P1)
**Project**: vskill

**As a** vault owner
**I want** the skill to run autonomously on a 4x/day schedule
**So that** my vault stays organized without manual intervention

**Acceptance Criteria**:
- [x] **AC-US5-01**: SKILL.md documents CronCreate setup for 4x/day scheduled runs (configurable interval in cron-setup.md reference)
- [x] **AC-US5-02**: Each scheduled run executes pre-flight check: verify vault path accessible, check inbox for new files, check last-run timestamp to avoid duplicate processing
- [x] **AC-US5-03**: No silent failures — every cron run logs its start, operations performed, and completion status to the vault log file; errors are logged with `!error` prefix
- [x] **AC-US5-04**: Scheduled runs prioritize: ingest first (if inbox has files), then lint (if threshold exceeded or weekly cadence), then index rebuild

---

### US-006: Agent Feature Filtering API (P2)
**Project**: vskill

**As a** skill creator
**I want** to filter agents by feature support and get creation profiles
**So that** I can target compatible agents when building cross-platform skills

**Acceptance Criteria**:
- [x] **AC-US6-01**: `agents-registry.ts` exports `filterAgentsByFeatures(features: Partial<FeatureSupport>): AgentDefinition[]` that returns agents matching all specified feature flags
- [x] **AC-US6-02**: `agents-registry.ts` exports `getAgentCreationProfile(agentId: string): AgentCreationProfile` that returns the agent's feature support, install paths, and generation guidance (what to strip/add for that agent)
- [x] **AC-US6-03**: AgentCreationProfile includes: `stripFields` (Claude-specific frontmatter to remove), `addGuidance` (agent-specific instructions to inject), `featureSupport` snapshot

---

### US-007: Agent-Aware Skill Generation (P1)
**Project**: vskill

**As a** skill creator
**I want** the skill generation prompt to adapt based on target agent
**So that** generated skills work correctly on non-Claude agents without hooks/MCP/slash commands

**Acceptance Criteria**:
- [x] **AC-US7-01**: When target agent is Claude Code (or unspecified), `BODY_SYSTEM_PROMPT` in `skill-create-routes.ts` remains unchanged — existing prompt IS the Claude-optimized path
- [x] **AC-US7-02**: When target agent is non-Claude, `BODY_SYSTEM_PROMPT` receives an appended agent-context section instructing the LLM to: avoid slash commands, avoid MCP tool references, avoid hooks, use only universally available tool patterns
- [x] **AC-US7-03**: Agent context is injected as a conditional section in the existing prompt — NOT a separate prompt template per agent
- [x] **AC-US7-04**: `/api/skills/generate` endpoint accepts optional `targetAgents: string[]` parameter; when provided, the generation uses agent-aware prompt augmentation

---

### US-008: Installed Agents Endpoint and Target Frontmatter (P2)
**Project**: vskill

**As a** Skill Studio user
**I want** an API to discover installed agents and filter skills by target agents
**So that** I can see which agents are available and create targeted skills

**Acceptance Criteria**:
- [x] **AC-US8-01**: New `GET /api/agents/installed` endpoint in `api-routes.ts` returns detected installed agents with their feature support, using `detectInstalledAgents()` from agents-registry
- [x] **AC-US8-02**: Response includes both installed and known-but-not-installed agents, with `installed: boolean` flag for each
- [x] **AC-US8-03**: `frontmatter.ts` supports optional `target-agents` field in SKILL.md frontmatter — a comma-separated list of agent IDs the skill is designed for
- [x] **AC-US8-04**: When `target-agents` is present, `canonical.ts` install logic uses it to determine which agent directories receive the skill (instead of installing to all detected agents)

---

### US-009: Agent Selection UI in Skill Studio (P2)
**Project**: vskill

**As a** skill creator
**I want** to select target agents in the Skill Studio UI with feature compatibility indicators
**So that** I can visually understand which agents support my skill's features and target accordingly

**Acceptance Criteria**:
- [x] **AC-US9-01**: `CreateSkillPage.tsx` includes an agent selection section with checkboxes for each known agent, grouped by universal vs non-universal
- [x] **AC-US9-02**: Each agent checkbox shows feature compatibility indicators (icons/badges) for: slash commands, hooks, MCP, custom system prompt — green if supported, gray if not
- [x] **AC-US9-03**: Selected agents are passed as `targetAgents` to the `/api/skills/generate` endpoint and written as `target-agents` frontmatter in the generated SKILL.md
- [x] **AC-US9-04**: Agent list is populated from `GET /api/agents/installed` endpoint, with installed agents visually distinguished from non-installed ones

## Functional Requirements

### FR-001: Filesystem-Only Fallback
The obsidian-brain skill must work entirely with filesystem tools (Read, Write, Glob, Grep, Bash). No dependency on Obsidian app, Obsidian CLI, or Obsidian Sync. The vault is a folder of markdown files.

### FR-002: Obsidian Sync Compatibility
No git operations on the vault directory. Obsidian Sync handles synchronization — the skill must not create `.git/`, run `git init`, or interfere with sync state.

### FR-003: Smart Routing, Not Separate Prompts
Agent-aware skill generation uses conditional augmentation of the existing BODY_SYSTEM_PROMPT. One prompt, conditionally extended — not a prompt-per-agent architecture.

### FR-004: SKILL.md Format Compliance
The obsidian-brain SKILL.md follows the agentskills.io standard format already used in vskill — YAML frontmatter + markdown body. No custom format invention.

### FR-005: Wiki Page Size Limit
Wiki pages created by ingest must stay under 1500 lines. If content exceeds this, split into multiple pages with cross-references.

## Success Criteria

- obsidian-brain skill installs via `vskill install` and processes the vault (6,700+ notes, 153 wiki pages, 14 inbox files) without errors
- Ingest clears inbox backlog, producing properly formatted wiki pages with correct routing
- Lint detects known issues (orphan pages, missing cross-refs) with zero false negatives on test vault
- CronCreate schedule runs 4x/day with zero silent failures over a 48-hour test period
- Agent-aware generation produces valid SKILL.md for at least 3 non-Claude agents (Cursor, Codex, Cline) that omits Claude-specific features
- GET /api/agents/installed returns correct installed/not-installed status for all 49 registered agents

## Out of Scope

- Obsidian plugin development (this is a CLI skill, not an Obsidian plugin)
- Vault migration or restructuring (skill works with existing structure)
- Multi-vault management (one vault per skill instance)
- Agent-specific eval benchmarks (evals test skill content, not agent runtime)
- New agent registrations (uses existing 49-agent registry)
- Separate prompt templates per agent (uses conditional augmentation only)
- Fork or rebrand of Skill Studio (extension of existing system)

## Dependencies

- vskill agents-registry.ts (49 agents, feature detection) — exists
- vskill installer/frontmatter.ts (stripClaudeFields, ensureFrontmatter) — exists
- vskill installer/canonical.ts (symlink/copy install) — exists
- vskill eval-server (skill-create-routes.ts, api-routes.ts) — exists
- vskill eval-ui (CreateSkillPage.tsx, workspace components) — exists
- Obsidian vault at configurable path — exists
- CronCreate tool availability in Claude Code — exists
