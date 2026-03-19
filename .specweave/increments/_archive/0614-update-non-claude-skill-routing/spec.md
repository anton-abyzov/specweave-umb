---
status: completed
---
# 0614: Fix update command to use canonical skill routing for non-Claude tools

## Problem

The `specweave update` command (update.ts lines 191-226) has an inline file-writing loop that copies skill content directly to every detected agent's `localSkillsDir`. This bypasses the canonical installer used by `init` and `install` commands, resulting in:

1. Non-Claude tools (OpenCode, Cursor, etc.) getting Claude-specific frontmatter fields they can't use
2. No canonical `.agents/skills/` directory update
3. No symlinks — full copies written everywhere
4. Screenshot evidence: OpenCode project has skill-creator in both `.claude/skills/` and `.agents/skills/` with identical 33KB SKILL.md files

## User Stories

### US-001: As a developer using OpenCode, I want `specweave update` to route skills correctly
**ACs:**
- [x] AC-US1-01: Update command uses `installSymlink()` from `canonical.ts` instead of inline file writes
- [x] AC-US1-02: Non-Claude agents get symlinks to canonical `.agents/skills/` dir with stripped content
- [x] AC-US1-03: Claude Code gets a direct copy with full frontmatter (preserving existing behavior)
- [x] AC-US1-04: Canonical `.agents/skills/` directory is updated during update (not just during init)

## Technical Context

- **Canonical installer**: `src/installer/canonical.ts` → `installSymlink()` (line 106), `installCopy()` (line 162)
- **Content stripping**: `src/installer/frontmatter.ts` → `stripClaudeFields()` (line 114)
- **Update command**: `src/commands/update.ts` → inline loop at lines 191-226
- **Reference implementation**: `src/core-skills/sync.ts` → `syncCoreSkills()` uses `installSymlink()` correctly
- **Install command**: `src/commands/add.ts` also uses the canonical approach
