# Architecture Plan: Prevent Unwanted Agent Dot-Folders

## Overview

This is a focused bugfix across two layers in the vskill CLI. The `safeProjectRoot()` function in `add.ts` is a dead stub that always returns `process.cwd()`, ignoring the existing `findProjectRoot()` utility. The canonical installer in `canonical.ts` lacks boundary guards against path traversal and HOME directory pollution. The fix applies a two-layer defense: soft resolution in `safeProjectRoot()`, hard guards in `canonical.ts`.

## Architecture Decision: Two-Layer Defense

**Layer 1 (Soft) -- `safeProjectRoot()` in `add.ts`**
Best-effort project root resolution. Never throws, never logs. Falls back to `process.cwd()` when resolution fails or returns HOME. This is the "try to do the right thing" layer.

**Layer 2 (Hard) -- `canonical.ts` guards**
Throws on violations. Catches cases where a bad `projectRoot` value (from any caller, not just `safeProjectRoot()`) would create directories in dangerous locations. This is the "prevent damage" layer.

The two layers are independent -- either one can prevent the bug alone, but together they provide defense in depth.

## Component Changes

### 1. `src/commands/add.ts` -- Fix `safeProjectRoot()`

**Current state** (lines 845-847):
```typescript
function safeProjectRoot(_opts: { cwd?: boolean }): string {
  return process.cwd();
}
```

**Target state**:
```typescript
function safeProjectRoot(opts: { cwd?: boolean }): string {
  if (opts.cwd) return process.cwd();
  const root = findProjectRoot(process.cwd());
  if (root === null || root === os.homedir()) return process.cwd();
  return root;
}
```

**Changes required**:
- Add import: `import { findProjectRoot } from "../utils/project-root.js";`
- Replace stub body with the three-branch logic above
- Rename `_opts` to `opts` (no longer unused)

**Behavior matrix**:

| Condition | Result |
|---|---|
| `--cwd` flag set | `process.cwd()` directly (trust override) |
| `findProjectRoot()` returns valid dir (not HOME) | That directory |
| `findProjectRoot()` returns HOME | `process.cwd()` (HOME guard) |
| `findProjectRoot()` returns `null` | `process.cwd()` (no markers found) |

**Why HOME guard uses `===`**: The spec requires exact match against `os.homedir()`. A user whose cwd IS `$HOME` but `findProjectRoot` returns `null` should still get cwd -- the guard only fires when HOME has project markers and is returned as a found root.

### 2. `src/installer/canonical.ts` -- Add boundary guards

Two guards, both in functions that sit on the critical path for directory creation.

#### 2a. `resolveAgentSkillsDir()` -- Path traversal guard

Add a check after `join(opts.projectRoot, agent.localSkillsDir)` that the resolved path is still within `opts.projectRoot`. This catches `localSkillsDir` values containing `../` sequences that escape the project boundary.

```typescript
function resolveAgentSkillsDir(agent: AgentDefinition, opts: InstallOptions): string {
  if (opts.global) {
    return expandTilde(agent.globalSkillsDir);
  }
  const resolved = join(opts.projectRoot, agent.localSkillsDir);
  if (!resolved.startsWith(opts.projectRoot)) {
    throw new Error(
      `Agent "${agent.id}" localSkillsDir escapes project root: ${agent.localSkillsDir}`
    );
  }
  return resolved;
}
```

**Note**: `join()` normalizes `../` sequences, so `join("/a/b", "../../c")` yields `/c`. The `startsWith` check catches this. Global installs bypass this check since they use `expandTilde(agent.globalSkillsDir)`.

**Export required**: `resolveAgentSkillsDir` must be exported for direct unit testing. It has no side effects and the guard behavior is important enough to warrant direct tests.

#### 2b. `ensureCanonicalDir()` -- HOME directory guard

Add a check that `base === os.homedir()` for non-global installs.

```typescript
export function ensureCanonicalDir(base: string, global: boolean): string {
  if (global) {
    const dir = join(os.homedir(), ".agents", "skills");
    mkdirSync(dir, { recursive: true });
    return dir;
  }
  if (base === os.homedir()) {
    throw new Error(
      "Refusing to install project-scoped skills in HOME directory. Use --global or run from a project directory."
    );
  }
  const dir = join(base, ".agents", "skills");
  mkdirSync(dir, { recursive: true });
  return dir;
}
```

**Why exact `===`**: Per spec, this uses exact match. Subdirectories of HOME (every normal project) are fine. Only HOME itself is blocked for non-global installs.

### 3. `src/commands/add.test.ts` -- Update and expand tests

#### 3a. Update TC-012

Current TC-012 asserts `safeProjectRoot()` always returns `process.cwd()`. After the fix, when `findProjectRoot()` returns a valid project root, that root is used as `projectRoot` instead of cwd.

**Updated assertion**: When `mockFindProjectRoot` returns a directory different from cwd, `installSymlink` receives that directory as `projectRoot`.

#### 3b. New test cases in "addCommand smart project root resolution" block

1. **findProjectRoot integration**: Mock `findProjectRoot` to return `/home/user/project` while cwd is `/home/user/project/subdir`. Assert `projectRoot` is `/home/user/project`.
2. **null fallback**: Mock `findProjectRoot` to return `null`. Assert `projectRoot` is `process.cwd()`.
3. **HOME guard**: Mock `findProjectRoot` to return `os.homedir()`. Assert `projectRoot` is `process.cwd()`.
4. **--cwd bypass**: Set `{ cwd: true }`. Assert `projectRoot` is `process.cwd()` and `mockFindProjectRoot` was not called.

### 4. `src/installer/canonical.test.ts` -- Add boundary guard tests

#### 4a. `resolveAgentSkillsDir` tests

1. **Path traversal rejection**: Agent with `localSkillsDir: "../../etc"`, `projectRoot: "/home/user/project"`. Assert throws with "escapes project root".
2. **Normal path allowed**: Agent with `localSkillsDir: ".cursor/skills"`. Assert returns correct joined path.
3. **Global bypass**: Global install. Assert uses `globalSkillsDir` path, no traversal check.

#### 4b. `ensureCanonicalDir` HOME guard tests

1. **HOME rejection**: `ensureCanonicalDir(os.homedir(), false)`. Assert throws with HOME directory message.
2. **HOME subdirectory allowed**: `ensureCanonicalDir(join(tempDir, "project"), false)`. Assert creates directory.
3. **Global at HOME allowed**: `ensureCanonicalDir(os.homedir(), true)`. Assert no throw.

## Data Flow

```
User runs: vskill add owner/skill

addCommand()
  |
  v
safeProjectRoot(opts)              <-- Layer 1 (soft)
  |-- opts.cwd? --> process.cwd()
  |-- findProjectRoot(cwd)
  |     |-- returns valid dir (not HOME) --> use it
  |     |-- returns HOME --> process.cwd()
  |     |-- returns null --> process.cwd()
  v
projectRoot passed to installSymlink/installCopy
  |
  v
ensureCanonicalDir(base, global)   <-- Layer 2 (hard)
  |-- base === HOME && !global --> THROW
  |
resolveAgentSkillsDir(agent, opts)  <-- Layer 2 (hard)
  |-- resolved escapes projectRoot --> THROW
  |
  v
mkdirSync / writeFileSync (safe)
```

## Risk Assessment

**Low risk**. All changes are in internal functions with clear boundaries:

- `safeProjectRoot()` fallback behavior preserves backward compatibility -- worst case it returns `process.cwd()` (same as current stub)
- `ensureCanonicalDir()` HOME guard only fires on exact HOME match for non-global installs -- no false positives for normal project directories
- `resolveAgentSkillsDir()` traversal guard only fires on malicious/malformed `localSkillsDir` values -- legitimate agent definitions never use `../`

**No breaking changes**: The fix changes behavior only when `findProjectRoot()` finds a project root above cwd. Previously this was ignored (cwd was always used). Now the found root is used, which is the correct/intended behavior.

## Implementation Order

1. `src/commands/add.ts` -- add import + fix `safeProjectRoot()` body
2. `src/installer/canonical.ts` -- export `resolveAgentSkillsDir`, add both guards
3. `src/commands/add.test.ts` -- update TC-012, add new test cases
4. `src/installer/canonical.test.ts` -- add guard test cases
5. Run `npx vitest run` to verify all tests pass

## No Domain Skill Delegation Needed

This is a pure Node.js/TypeScript bugfix in an existing CLI codebase. No frontend, backend framework, or infrastructure skills are applicable. The changes are 4 files, under 30 lines of production code change total.
