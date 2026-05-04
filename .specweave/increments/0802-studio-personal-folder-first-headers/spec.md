---
increment: 0802-studio-personal-folder-first-headers
title: >-
  Studio sidebar — Personal section uses folder name + tool sublabel (parity
  with Project)
type: bug
priority: P2
status: completed
created: 2026-04-29T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Personal section header uses folder name (parity with Project)

## Overview

Inside `AVAILABLE`, the **Project** sub-section groups skills by the on-disk folder that contains them — e.g. `<repo>/.claude/skills/*` → header `.CLAUDE`. The **Personal** sub-section groups by the agent registry id instead — e.g. `~/.claude/skills/*` → header `CLAUDE-CODE`. Both sources are conceptually the same `.claude/` tool dir, but the labels differ. This makes the sidebar feel inconsistent and hides the fact that personal skills also live in a `.claude` directory on disk.

## Bug Reproduction

1. Open `vskill studio` (http://localhost:3113/?tab=edit) in any project.
2. Expand `AVAILABLE`.
3. Observe **PROJECT** subsection: inner header reads `.CLAUDE (4)` (folder).
4. Observe **PERSONAL** subsection: inner header reads `CLAUDE-CODE (12)` (agent id).
5. Expected: both render the on-disk folder (`.CLAUDE`) with a small sublabel "Claude Code" identifying the tool.

## Root Cause

| File | Line | Issue |
|---|---|---|
| `src/eval/skill-scanner.ts` | ~427 | Global/personal scan calls `scanSkillsDir(agent.id, globalDir, …)` — uses agent registry id as the synthetic plugin label. |
| `src/eval/skill-scanner.ts` | ~309 | Project scan walks `<root>/<plugin>/skills/<skill>` — uses real folder name as plugin label. |
| `src/eval-ui/src/components/PluginGroup.tsx` | 55 | Renders `plugin` directly with no tool subtitle, so the only differentiator is the label string. |
| `src/eval-ui/src/types.ts` | — | `SkillInfo` has no `pluginDisplay` field, so the friendly tool name has nowhere to ride. |

## User Stories

### US-001: Personal sub-section header shows the folder name (P2)
**Project**: vskill

**As a** Studio user,
**I want** the Personal sub-section to show the on-disk folder name (e.g. `.CLAUDE`)
**So that** Project and Personal use the same labeling and I can map the header back to a real path on disk.

**Acceptance Criteria**:
- [x] **AC-US1-01**: For Claude Code with `globalSkillsDir = ~/.claude/skills`, every skill in `AVAILABLE > PERSONAL` has `plugin = ".claude"` (basename of `dirname(globalSkillsDir)`), so the header renders `.CLAUDE (n)` instead of `CLAUDE-CODE (n)`.
- [x] **AC-US1-02**: The change is symmetric across agents — Cursor (`~/.cursor/skills`) renders `.CURSOR`, Codex (`~/.codex/skills`) renders `.CODEX`, etc., derived from the registry's `globalSkillsDir`.
- [x] **AC-US1-03**: When `dirname(globalSkillsDir)` resolves to a generic directory whose basename is not a tool-prefixed dot folder (e.g. `~/.config/agents/skills` for Amp/Kimi → basename `agents`), the scanner falls back to `agent.id` — never emits an empty or `agents` header.

### US-002: A small "Claude Code" sublabel identifies the tool (P2)
**Project**: vskill

**As a** Studio user,
**I want** the agent's display name shown as a small caption under the folder header
**So that** I know which AI tool the folder belongs to without having to remember the convention.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `SkillInfo` carries an optional `pluginDisplay?: string` field set to the agent's `displayName` (e.g. `"Claude Code"`) for personal-scope skills.
- [x] **AC-US2-02**: Project-scope skills also receive `pluginDisplay` when the folder name maps to a known agent prefix (e.g. `.claude` → "Claude Code", `.cursor` → "Cursor"), via the same registry lookup that powers `agentIdForLocalPrefix`.
- [x] **AC-US2-03**: `PluginGroup` renders `pluginDisplay` as a small caption (font-size 9px, lighter color) directly below the uppercased plugin label. Hidden when `pluginDisplay` is absent so unknown plugin folders stay clean.
- [x] **AC-US2-04**: When `pluginDisplay`, lower-cased, equals the plugin folder name with a leading `.` stripped (e.g. plugin `.cursor` + display `Cursor`), the sublabel still renders — readers shouldn't have to know the convention. The only suppression is exact-match-after-casefold (rare).

### US-003: Existing tests stay green; new tests lock the contract (P2)
**Project**: vskill

**As a** developer maintaining the scanner + sidebar,
**I want** the new contract covered by tests at both layers
**So that** a future scanner refactor can't silently revert to the registry-id label.

**Acceptance Criteria**:
- [x] **AC-US3-01**: A scanner unit test feeds a fixture home with `~/.claude/skills/foo` and asserts the emitted skill has `plugin === ".claude"` and `pluginDisplay === "Claude Code"`.
- [x] **AC-US3-02**: A scanner unit test feeds a fixture home with `~/.config/agents/skills/foo` (Amp/Kimi case) and asserts the fallback path: `plugin === agent.id`.
- [x] **AC-US3-03**: A `PluginGroup.test.tsx` test asserts the sublabel renders when `pluginDisplay` is set and is omitted when absent.
- [x] **AC-US3-04**: All other scanner tests, sidebar tests, and Studio Playwright specs continue to pass without modification beyond updating the 1–2 fixtures that hard-coded `plugin: "claude-code"`.

## Out of Scope

- Reorganizing the `AVAILABLE` group structure itself (Project / Personal / Plugin headers stay).
- Changing how plugin scope (third sub-section) labels its rows — plugins already have proper names.
- Renaming `agent.id` strings in `AGENTS_REGISTRY`.
- Touching the breadcrumb at the top of the detail panel — that's increment 0801's territory.
