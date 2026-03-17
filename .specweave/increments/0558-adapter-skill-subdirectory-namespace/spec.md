---
increment: 0558-adapter-skill-subdirectory-namespace
title: "Subdirectory-Based Skill Namespace for Non-Claude Adapters"
type: feature
priority: P1
status: active
created: 2026-03-17
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Subdirectory-Based Skill Namespace for Non-Claude Adapters

## Overview

Align specweave adapter skill compilation directories with the vskill agent registry's skills directory convention. Currently, several adapters (Cursor, Windsurf, Codex, Copilot, Cline, Continue, JetBrains, Amazon Q, Trae, Zed, Tabnine, Aider) write compiled skills to tool-specific "rules" directories (e.g., `.cursor/rules/`, `.windsurf/rules/`), while the vskill agent registry defines standard "skills" directories (e.g., `.cursor/skills/`, `.windsurf/skills/`). This mismatch means that skills installed via `specweave refresh-plugins` end up in different locations than skills installed via `vskill install`, breaking the unified `sw:` namespace.

The base class `writeSkillFiles()` already produces correct subdirectory structure (`{dir}/{pluginName}/{skillName}.md`). The change is to update each adapter's target directory from its current "rules" path to the standard "skills" path defined in the agent registry.

## User Stories

### US-001: Unified Skill Directory for All Adapters (P1)
**Project**: specweave

**As a** developer using a non-Claude AI coding tool (Cursor, Windsurf, etc.)
**I want** specweave-installed skills to appear in the same directory as vskill-installed skills
**So that** all my skills are discoverable in one location regardless of the installation method

**Acceptance Criteria**:
- [x] **AC-US1-01**: Cursor adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.cursor/skills` instead of `.cursor/rules`
- [x] **AC-US1-02**: Windsurf adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.windsurf/skills` instead of `.windsurf/rules`
- [x] **AC-US1-03**: Codex adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.codex/skills` instead of `.codex/rules`
- [x] **AC-US1-04**: Copilot adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.github/copilot/skills` instead of `.github/instructions`
- [x] **AC-US1-05**: Cline adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.cline/skills` instead of `.cline/rules`
- [x] **AC-US1-06**: Continue adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.continue/skills` instead of `.continue/rules`
- [x] **AC-US1-07**: JetBrains adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.junie/skills` instead of `.aiassistant/rules`
- [x] **AC-US1-08**: Amazon Q adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.amazonq/skills` instead of `.amazonq/rules`
- [x] **AC-US1-09**: Trae adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.trae/skills` instead of `.trae/rules`
- [x] **AC-US1-10**: Tabnine adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.tabnine/skills` instead of `.tabnine/guidelines`
- [x] **AC-US1-11**: Aider adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.aider/skills` instead of `.aider`
- [x] **AC-US1-12**: Zed adapter compilePlugin/unloadPlugin/getInstalledPlugins use `.zed/skills` instead of `.rules`

---

### US-002: Registry Documentation Alignment (P1)
**Project**: specweave

**As a** contributor reading adapter documentation
**I want** the adapter registry.yaml skill_dirs section to reflect the updated skills directories
**So that** documentation matches the actual implementation

**Acceptance Criteria**:
- [x] **AC-US2-01**: `registry.yaml` skill_dirs section maps each adapter to its updated skills directory
- [x] **AC-US2-02**: Adapter descriptions and comments reference the updated paths

---

### US-003: Adapter Tests Updated (P1)
**Project**: specweave

**As a** developer maintaining the adapter codebase
**I want** tests to verify skills are written to the correct skills directory
**So that** regressions are caught if someone changes a path back

**Acceptance Criteria**:
- [x] **AC-US3-01**: Existing adapter-base tests continue to pass (no base class changes needed)
- [x] **AC-US3-02**: Integration-style tests verify each adapter uses the registry-aligned skills directory

## Functional Requirements

### FR-001: Skills Directory Alignment
All non-Claude adapters must write compiled skills to the same directory path defined in the vskill agent registry (`localSkillsDir` field). This ensures that skills from both `specweave refresh-plugins` and `vskill install` are co-located.

### FR-002: Backward Compatibility
The install operation should create the target directory if it does not exist. No migration of existing "rules" directory content is required -- old rules directories can remain and will be manually cleaned by users.

### FR-003: SKILL.md Format Preserved
The subdirectory structure (`{pluginName}/{skillName}.md`) produced by `writeSkillFiles()` must be preserved. Only the root target directory changes.

## Success Criteria

- All 12 non-Claude adapters write to their agent registry-defined skills directory
- All adapter tests pass with updated paths
- Existing base class tests continue to pass (no base class changes needed)

## Out of Scope

- Migration of existing installed skills from old directories to new
- Changes to the Claude adapter (already uses `.claude/skills/`)
- Changes to the Generic adapter (uses `.agents/skills/`, which is correct)
- Changes to the Antigravity adapter (uses `.agent/skills/`, which matches its registry)
- Changes to the Gemini adapter (uses `.gemini/`, which is the Gemini config root)
- Changes to the OpenCode adapter (already uses `.opencode/skills/`)
- Changes to the Kimi adapter (already uses `.kimi/skills/`)
- Changes to vskill (already correct)
- Changes to `writeSkillFiles()` base class method (already correct)

## Dependencies

- vskill agents registry (`agents-registry.ts`) defines the canonical `localSkillsDir` for each agent
- AdapterBase `writeSkillFiles()`, `removeSkillFiles()`, `listInstalledPluginsInDir()` provide the underlying implementation
