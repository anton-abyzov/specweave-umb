# Implementation Plan: Subdirectory-Based Skill Namespace for Non-Claude Adapters

## Overview

This is a targeted refactoring of 12 adapter files in the specweave repo. Each adapter's `compilePlugin()`, `unloadPlugin()`, and `getInstalledPlugins()` methods reference a "rules" directory that must be changed to the "skills" directory matching the vskill agent registry. The `registry.yaml` documentation file also needs updating. No base class changes, no vskill changes, no new files needed.

## Architecture

### Components to Modify

All files are in `repositories/anton-abyzov/specweave/src/adapters/`:

| Adapter | File | Current Dir | Target Dir | Registry Match |
|---------|------|-------------|------------|----------------|
| Cursor | `cursor/adapter.ts` | `.cursor/rules` | `.cursor/skills` | cursor |
| Windsurf | `windsurf/adapter.ts` | `.windsurf/rules` | `.windsurf/skills` | windsurf |
| Codex | `codex/adapter.ts` | `.codex/rules` | `.codex/skills` | codex |
| Copilot | `copilot/adapter.ts` | `.github/instructions` | `.github/copilot/skills` | github-copilot |
| Cline | `cline/adapter.ts` | `.cline/rules` | `.cline/skills` | cline |
| Continue | `continue/adapter.ts` | `.continue/rules` | `.continue/skills` | continue |
| JetBrains | `jetbrains/adapter.ts` | `.aiassistant/rules` | `.junie/skills` | junie |
| Amazon Q | `amazonq/adapter.ts` | `.amazonq/rules` | `.amazonq/skills` | (no registry entry, use convention) |
| Trae | `trae/adapter.ts` | `.trae/rules` | `.trae/skills` | trae |
| Tabnine | `tabnine/adapter.ts` | `.tabnine/guidelines` | `.tabnine/skills` | tabnine |
| Aider | `aider/adapter.ts` | `.aider` | `.aider/skills` | aider |
| Zed | `zed/adapter.ts` | `.rules` | `.zed/skills` | (no registry entry, use convention) |

### Components NOT Modified

- `adapter-base.ts` -- `writeSkillFiles()` already uses subdirectory structure
- `adapter-interface.ts` -- interface unchanged
- `claude/adapter.ts` -- already uses `.claude/skills/`
- `generic/adapter.ts` -- uses `.agents/skills/` which is correct
- `antigravity/adapter.ts` -- uses `.agent/skills/` which matches registry
- `gemini/adapter.ts` -- uses `.gemini/` as root config dir
- `opencode/adapter.ts` -- already uses `.opencode/skills`
- `kimi/adapter.ts` -- already uses `.kimi/skills`

### Data Model

No data model changes. The file structure produced remains:
```
{skillsDir}/{pluginName}/{skillName}{suffix}
```
e.g., `.cursor/skills/sw/increment.md`

## Technology Stack

- **Language**: TypeScript
- **Testing**: Vitest
- **Changes**: String constant updates only -- no logic changes

**Architecture Decisions**:
- **AD-001: Use agent registry paths directly** -- Rather than inventing new paths, we align with the vskill agent registry `localSkillsDir` values. This ensures future changes to the registry automatically define the correct path.
- **AD-002: No migration** -- Old "rules" directories are left in place. Users can manually clean them. This avoids complexity and risk of data loss.
- **AD-003: Copilot uses .github/copilot/skills** -- The vskill registry defines `.github/copilot/skills` for github-copilot agent. The previous `.github/instructions` was a Copilot-specific convention but doesn't match the universal skill format.

## Implementation Phases

### Phase 1: Update All 12 Adapter Files
Change directory constants in `compilePlugin()`, `unloadPlugin()`, `getInstalledPlugins()`, plus any comments, descriptions, and `install()` directory creation.

### Phase 2: Update registry.yaml
Update the `skill_dirs` mapping and any descriptions that reference old paths.

### Phase 3: Run Tests
Run existing tests to verify nothing breaks. The adapter-base.test.ts tests use a TestAdapter with injectable paths, so they should pass unchanged.

## Testing Strategy

- Run `npx vitest run` in the specweave repo to verify existing tests pass
- The adapter-base.test.ts tests verify `writeSkillFiles()`, `removeSkillFiles()`, and `listInstalledPluginsInDir()` -- these test the base class behavior, not specific adapter paths
- No new test files needed since the change is purely directory constant updates
- Manual verification: inspect each adapter file to confirm the path matches the vskill registry

## Technical Challenges

### Challenge 1: Copilot file suffix
**Problem**: Copilot used `.instructions.md` suffix with `.github/instructions/`. Moving to `.github/copilot/skills/` means the suffix should change to `.md` for consistency.
**Decision**: Keep `.instructions.md` suffix -- it's a Copilot convention that makes files discoverable by Copilot's instruction system. The suffix is independent of the directory.

### Challenge 2: JetBrains path change
**Problem**: JetBrains adapter used `.aiassistant/rules` but the vskill registry defines `.junie/skills` for the junie agent.
**Decision**: Use `.junie/skills` to match the registry. JetBrains Junie is the current AI coding agent from JetBrains.

### Challenge 3: Zed has no registry entry
**Problem**: Zed is not in the vskill agent registry but had `.rules` as its skills dir.
**Decision**: Use `.zed/skills` following the convention of `.<toolname>/skills`.
