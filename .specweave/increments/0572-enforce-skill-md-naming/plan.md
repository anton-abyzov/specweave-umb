# Implementation Plan: Enforce SKILL.md naming at install time for non-Claude tools

## Overview

The `copyPluginFiltered()` function in `add.ts` copies `.md` files with their original filenames instead of renaming them to `SKILL.md` when they reside in a skill directory context. This causes non-Claude tools (Cursor, Windsurf, Cody, etc.) to fail skill activation because they expect the canonical `{skill-name}/SKILL.md` directory structure.

The fix has two layers:
1. **Root cause fix**: Patch `copyPluginFiltered()` to rename `.md` files to `SKILL.md` when copying into a skill directory
2. **Post-install enforcement**: Add a new `ensureSkillMdNaming()` function in `migrate.ts` that can be called after any install path to catch any remaining misnamed files

## Root Cause Analysis

```
Source plugin structure:        After copyPluginFiltered():
plugins/my-plugin/              target/my-plugin/
  skills/                         my-skill/
    my-skill/                       my-skill.md    <-- BUG: keeps original name
      my-skill.md                   agents/
      agents/                         helper.md
        helper.md
```

The bug is at `add.ts:660-667`. When `entry !== "SKILL.md"`, the file is copied verbatim via `copyFileSync`. There is no logic to detect that a `.md` file in a skill directory should be renamed to `SKILL.md`.

The `shouldSkipFromCommands()` filter at line 639 correctly identifies skill-internal `.md` files but only uses this information to skip/allow -- never to rename.

## Architecture

### Component: `ensureSkillMdNaming()` in `migrate.ts`

A new exported function alongside the existing `migrateStaleSkillFiles()`. Both share the same domain (file naming enforcement) and similar logic patterns.

```
ensureSkillMdNaming(skillsDir: string): NamingResult
```

**Behavior**: Walk one or two levels of `skillsDir`. For each subdirectory that contains a single `.md` file (not named `SKILL.md`) and no `SKILL.md`:
1. Read the `.md` file content
2. Run `ensureFrontmatter()` on it
3. Write as `SKILL.md` in the same directory
4. Delete the original file
5. Track renamed count

**Why this belongs in `migrate.ts`**: Same responsibility domain (enforcing canonical naming), same filesystem patterns, same dependency on `ensureFrontmatter`. Keeps the installer module cohesive.

**Return type**:

```typescript
export interface NamingResult {
  renamedCount: number;
  errors: string[];
}
```

### Component: Fix in `copyPluginFiltered()` in `add.ts`

Modify the `else` branch (line 665-666) to detect when a `.md` file is inside a skill directory and should be renamed to `SKILL.md`.

**Detection heuristic**: A `.md` file should be renamed to `SKILL.md` when:
1. The file is a `.md` file (not in an `agents/` subdirectory)
2. The file is inside a path that looks like a skill directory (i.e., `relBase` contains `skills/` or the parent was flattened from `skills/`)
3. No `SKILL.md` already exists for this entry

The simplest correct approach: treat any non-`SKILL.md` `.md` file in a skill directory the same way `SKILL.md` is treated -- read it, run `ensureFrontmatter()`, write as `SKILL.md`.

**Implementation**:

```
// In copyPluginFiltered, replace lines 661-667:
if (entry === "SKILL.md" || isSkillMdCandidate(entry, relPath)) {
  const raw = readFileSync(sourcePath, "utf-8");
  const skillName = basename(relBase || sourceDir);
  writeFileSync(join(targetDir, "SKILL.md"), ensureFrontmatter(raw, skillName), "utf-8");
} else {
  copyFileSync(sourcePath, join(targetDir, entry));
}
```

Where `isSkillMdCandidate` checks:
- File ends with `.md`
- File is not in an `agents/` subdirectory (those are agent files, not skill definitions)
- The relPath indicates we are inside a skill directory (e.g., `skills/{name}/` level)

### Component: Post-install wiring in `add.ts` and `update.ts`

After each install completes, call `ensureSkillMdNaming()` on the installed directories as a safety net. This catches edge cases that `copyPluginFiltered` might miss (e.g., plugins installed via other mechanisms).

**Wiring points**:
1. `add.ts` line ~1158: After `copyPluginFiltered(pluginDir, cacheDir)` -- call `ensureSkillMdNaming` on the cacheDir
2. `add.ts` line ~1637-1640: After the skill install loop for GitHub plugins -- call `ensureSkillMdNaming` on each plugDir
3. `update.ts` line ~173: Already writes `SKILL.md` correctly, but add `ensureSkillMdNaming` after write as defense-in-depth

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **Testing**: Vitest with real filesystem (tmpdir pattern, matching existing migrate.test.ts)
- **Dependencies**: Reuses `ensureFrontmatter` from `./frontmatter.js`

## Implementation Phases

### Phase 1: ensureSkillMdNaming in migrate.ts

1. Add `NamingResult` interface
2. Implement `ensureSkillMdNaming()` function
3. Unit tests in `migrate.test.ts` covering:
   - Single misnamed `.md` file gets renamed to `SKILL.md`
   - File already named `SKILL.md` is left alone (no-op)
   - Nested namespaced directories (e.g., `sw/skill-name/`)
   - Multiple misnamed files in different skill directories
   - Files in `agents/` subdirectories are NOT renamed
   - Frontmatter is applied during rename
   - Empty directories are skipped

### Phase 2: Fix copyPluginFiltered

1. Add `isSkillMdCandidate()` helper function
2. Modify the `else` branch to rename `.md` files to `SKILL.md` when inside a skill directory
3. Update existing tests in `add.test.ts` to verify the rename behavior

### Phase 3: Wire enforcement after install

1. Import `ensureSkillMdNaming` in `add.ts`
2. Call after `copyPluginFiltered` in local plugin install path
3. Call after GitHub plugin install loop
4. Import and call in `update.ts` as defense-in-depth
5. Integration test: end-to-end install produces correct SKILL.md naming

## Testing Strategy

- **Unit tests**: Vitest with real tmpdir filesystem (matching existing pattern in migrate.test.ts)
- **Key scenarios**: misnamed .md rename, SKILL.md passthrough, agents/ exclusion, nested namespaces, frontmatter injection during rename
- **Integration**: Verify full install flow produces correct naming across all agent directories

## Technical Challenges

### Challenge 1: Detecting skill directory context in copyPluginFiltered

The flattening logic (`skills/` merging into parent) means `relBase` doesn't always clearly indicate "we are in a skill directory". After flattening, `relBase` still contains `skills/` but the target directory has been merged up.

**Solution**: Track a `inSkillsSubdir` flag based on the relPath structure. If `relPath` starts with `skills/` and depth is 2+ (meaning we are inside `skills/{name}/`), any `.md` file that isn't in `agents/` is a skill definition candidate.

**Risk**: Low. The `shouldSkipFromCommands` function already has this same detection logic at line 639 -- we mirror it.

### Challenge 2: Multiple .md files in a single skill directory

A skill directory might contain multiple `.md` files (e.g., `frontend-design.md` and `README.md`). We need to pick only the skill definition file to rename.

**Solution**: The `shouldSkipFromCommands` filter already skips `README.md` and `FRESHNESS.md`. Any `.md` file that passes the filter and is inside a skill directory (not `agents/`) is the skill definition. If multiple candidates exist, pick the one matching the directory name or the first alphabetically.

### Challenge 3: Backward compatibility

Existing plugins with correctly named `SKILL.md` files must continue to work identically.

**Solution**: The `entry === "SKILL.md"` check comes first in the conditional. The new `isSkillMdCandidate` logic only applies to the `else` branch, so correctly named files are handled by the existing path with zero behavioral change.
