---
increment: 0584-skill-versioning
type: architecture
status: proposed
created: 2026-03-19
---

# Architecture: Skill Versioning for Verified Skills

## 1. Overview

This plan adds versioning primitives to vskill: full-file deterministic hashing, frontmatter version extraction, auto-patch bumping, ghost file cleanup, and backward-compatible lockfile migration. All changes are internal to the vskill CLI -- no server-side or API changes required.

## 2. Architecture Decisions

### AD-1: Hash Algorithm Change (12-char truncated -> 64-char full SHA-256)

**Current**: `computeSha()` in `source-fetcher.ts` produces `sha256(content).hex.slice(0,12)` -- 12 hex chars from SKILL.md content only.

**New**: Full 64-char SHA-256 hex over all files. The hash is a deterministic fingerprint used for change detection. Full 64 chars avoid collisions across multi-file skills and align with standard tooling (git, npm, docker all use full hashes).

**Backward compatibility**: Old 12-char hashes in existing lockfiles will mismatch on first `vskill update`, triggering a one-time re-download. This is correct behavior -- it bootstraps the new hash and file manifest for all existing entries.

### AD-2: Hash Normalization Strategy

Deterministic hashing requires content normalization before hashing:

1. **CRLF -> LF** -- Windows checkouts may have CRLF; normalize to LF so the hash is OS-independent.
2. **BOM trim** -- Remove UTF-8 BOM prefix (`\uFEFF`) if present.
3. **No trailing whitespace normalization** -- Only CRLF and BOM are normalized. Trailing whitespace is content.

This reuses the same normalization logic already in `ensureFrontmatter()` (line 69 of `frontmatter.ts`).

### AD-3: Deterministic Multi-File Hash Format

```
sort files by path (case-sensitive, ascending)
for each file:
  append "relative/path\0normalized-content\n"
SHA-256 the concatenated buffer -> 64 hex chars
```

The `\0` (null byte) separator between path and content prevents ambiguity (e.g., a file named `"a\ncontent"` vs file `"a"` with content `"content"`). The trailing `\n` acts as a record terminator.

### AD-4: Version Resolution Priority

1. **Server-provided version** (from registry API `SkillDetail.version`) -- highest priority when available
2. **Frontmatter `version:` field** -- used when server version is absent (GitHub sources, local sources)
3. **Auto-increment patch** -- when neither server nor frontmatter provides a version and the hash changed
4. **Default `1.0.0`** -- for first-time installs with no version information

Frontmatter acts as advisory: skill authors declare intent, but the registry can override (e.g., for coordinated version bumps across a plugin).

### AD-5: Lockfile Schema Extension (Non-Breaking)

Add optional `files?: string[]` to `SkillLockEntry`. Existing entries without `files` continue to work -- ghost file cleanup is skipped when `files` is undefined (safe fallback per AC-US6-03).

No lockfile `version` field bump needed. The schema is additive (new optional field), and `VskillLock.version` stays at `1`.

## 3. Component Design

### 3.1 New Module: `src/utils/version.ts`

Pure utility functions with no side effects or I/O.

```typescript
// Parses YAML frontmatter for `version:` field.
// Validates against semver pattern (X.Y.Z, optional pre-release/build).
// Returns undefined for missing or invalid values.
extractFrontmatterVersion(content: string): string | undefined

// Increments patch: "1.2.3" -> "1.2.4".
// If input is invalid semver, returns "1.0.1".
bumpPatch(version: string): string

// Implements the priority chain from AD-4.
resolveVersion(opts: {
  serverVersion?: string;
  frontmatterVersion?: string;
  currentVersion?: string;
  hashChanged: boolean;
  isFirstInstall: boolean;
}): string
```

### 3.2 Modified Module: `src/updater/source-fetcher.ts`

**FetchResult changes**:

```typescript
export interface FetchResult {
  content: string;                    // SKILL.md content (backward compat)
  version: string;
  sha: string;                        // Now 64-char full hex
  tier: string;
  files?: Record<string, string>;     // NEW: path -> content map (all files)
}
```

**computeSha() changes** -- overloaded to accept single string or files map:

```typescript
function computeSha(content: string): string;
function computeSha(files: Record<string, string>): string;
function computeSha(input: string | Record<string, string>): string {
  const h = createHash("sha256");
  if (typeof input === "string") {
    h.update(normalizeContent(input));
  } else {
    const sorted = Object.keys(input).sort();
    for (const path of sorted) {
      h.update(`${path}\0${normalizeContent(input[path])}\n`);
    }
  }
  return h.digest("hex"); // full 64 chars
}
```

**Fetch function changes**:
- `fetchGitHubFlat()` -- discover and fetch `agents/*.md` via tree API, populate `files` map
- `fetchPlugin()` -- already fetches multiple files; refactor to populate `files` map instead of concatenating content
- `fetchRegistry()` -- server returns single content; `files` contains `{"SKILL.md": content}`

**New helper**: `normalizeContent(content: string): string` -- strips BOM, normalizes CRLF to LF.

### 3.3 Modified Module: `src/lockfile/types.ts`

```typescript
export interface SkillLockEntry {
  version: string;
  sha: string;             // Now 64 chars (was 12)
  tier: string;
  installedAt: string;
  source: string;
  marketplace?: string;
  pluginDir?: boolean;
  scope?: "user" | "project";
  installedPath?: string;
  files?: string[];         // NEW: sorted list of relative file paths
}
```

### 3.4 New Module: `src/lockfile/migration.ts`

Runs on lockfile read. Called from `readLockfile()` in `lockfile.ts`.

```typescript
// Migrates a single entry:
// - version "" or "0.0.0" -> "1.0.0"
// - files: left as undefined if not present
// Returns new object (does not mutate input)
migrateLockEntry(entry: SkillLockEntry): SkillLockEntry

// Iterates all entries, applies migrateLockEntry.
// Does NOT write to disk (caller decides when to persist).
migrateLock(lock: VskillLock): VskillLock
```

Read-time migration only. Disk is updated when the next `writeLockfile()` call happens (during install or update), not eagerly on read. This avoids unexpected file modifications for read-only operations like `vskill list`.

### 3.5 Modified Module: `src/commands/update.ts`

Key changes:

1. **Hash comparison** (line ~137): `result.sha` (64 chars) vs `entry.sha`. Old 12-char vs new 64-char values never match, so the first update after upgrade triggers a re-download naturally.

2. **Version resolution** (new, after hash comparison): Call `resolveVersion()` with frontmatter from fetched content, server version from `result.version`, and current `entry.version`.

3. **Ghost file cleanup** (new, before writing new files): Compare `entry.files` (old manifest) with new file paths. Delete files in old but not in new. Only runs when `entry.files` is defined (migration safety per AC-US6-03).

4. **Multi-file write** (replaces single SKILL.md write): When `result.files` is present, write all files. When absent, write only SKILL.md (backward compat).

5. **Lockfile entry update**: Include `files` array (sorted paths from result).

### 3.6 Modified Module: `src/commands/add.ts`

Key changes:

1. **SHA computation**: All six call sites computing `createHash("sha256")...slice(0, 12)` switch to `computeSha()`. When multi-file context is available, pass the files map.

2. **Lockfile entry**: Include `files` array when writing to lockfile.

3. **Version**: Use `extractFrontmatterVersion()` from fetched content, fall back to `"1.0.0"` for first install.

## 4. Data Flow

### Install Flow (add.ts)
```
fetch content (single or multi-file)
  |
  v
computeSha(files) -> 64-char hex
  |
  v
extractFrontmatterVersion(SKILL.md content)
  |
  v
resolveVersion(server, frontmatter, null, false, isFirstInstall=true)
  |
  v
write files to agent dirs via installSymlink/installCopy
  |
  v
lockfile entry: { version, sha, files: [...sorted paths] }
```

### Update Flow (update.ts)
```
read lockfile entry (with migration applied on read)
  |
  v
fetchFromSource() -> FetchResult { content, sha, files, version }
  |
  v
sha === entry.sha? -> skip ("already up to date")
  |
  v (sha differs)
extractFrontmatterVersion(SKILL.md content)
  |
  v
resolveVersion(server, frontmatter, entry.version, hashChanged=true, false)
  |
  v
ghost file cleanup: diff entry.files vs new files, delete removed
  |
  v
write new files to agent dirs
  |
  v
lockfile entry: { version, sha, files: [...sorted paths] }
```

## 5. Ghost File Cleanup

```typescript
function cleanupGhostFiles(
  skillDir: string,
  oldFiles: string[] | undefined,
  newFiles: string[],
): string[] {
  if (!oldFiles) return []; // pre-migration entry: safe fallback
  const newSet = new Set(newFiles);
  const removed: string[] = [];
  for (const f of oldFiles) {
    if (!newSet.has(f)) {
      const fullPath = join(skillDir, f);
      try { unlinkSync(fullPath); removed.push(f); } catch { /* already gone */ }
    }
  }
  // Clean up empty directories left behind
  for (const f of removed) {
    const dir = dirname(join(skillDir, f));
    try { rmdirSync(dir); } catch { /* not empty or already gone */ }
  }
  return removed;
}
```

Safety: only deletes files that were in the previous manifest. Files not tracked in the manifest are never touched.

## 6. Migration Strategy

- **Read-time only**: `migrateLock()` is called inside `readLockfile()`. Returned object has migrated entries in memory. Disk is only updated on next `writeLockfile()`.
- **No forced re-hash**: Old 12-char SHAs stay in the lockfile until the next update. The new 64-char SHA will naturally differ, triggering a re-download.
- **Version migration**: Only `""` and `"0.0.0"` are migrated to `"1.0.0"`. Valid versions like `"2.3.1"` are preserved. `"0.0.0"` was a placeholder used when no version info was available (see add.ts lines 1946, 2353, 2557).

## 7. Affected Files

| File | Change | Scope |
|------|--------|-------|
| `src/utils/version.ts` | **NEW** | extractFrontmatterVersion, bumpPatch, resolveVersion |
| `src/utils/version.test.ts` | **NEW** | Unit tests for version utilities |
| `src/lockfile/types.ts` | MODIFY | Add `files?: string[]` to SkillLockEntry |
| `src/lockfile/migration.ts` | **NEW** | migrateLockEntry, migrateLock |
| `src/lockfile/migration.test.ts` | **NEW** | Unit tests for migration logic |
| `src/lockfile/lockfile.ts` | MODIFY | Call migrateLock() in readLockfile() |
| `src/lockfile/index.ts` | MODIFY | Re-export migration functions |
| `src/updater/source-fetcher.ts` | MODIFY | computeSha overload, FetchResult.files, normalizeContent |
| `src/updater/source-fetcher.test.ts` | MODIFY | Update tests for new hash format |
| `src/commands/update.ts` | MODIFY | Ghost file cleanup, version resolution, multi-file write |
| `src/commands/add.ts` | MODIFY | Switch 6 SHA call sites, add files manifest |

## 8. Risk Assessment

| Risk | Mitigation |
|------|------------|
| Old lockfile SHAs trigger unnecessary re-downloads on first update | One-time cost. No data loss. Bootstraps new format. |
| Ghost file cleanup deletes user-added files | Only deletes files from previous `files` manifest. Unknown files untouched. |
| `bumpPatch()` on non-semver strings | Falls back to `"1.0.1"`. Invalid stored versions are corrected. |
| Breaking change for tools reading vskill.lock | `files` is optional. SHA length change invisible to tools that store but do not validate. |
| Hash mismatch old 12-char vs new 64-char | Different lengths never match. First update re-syncs. |

## 9. Testing Strategy

TDD (red-green-refactor) for all new code:

1. **`version.test.ts`**: extractFrontmatterVersion (valid, missing, invalid semver), bumpPatch (normal, edge), resolveVersion (all priority paths)
2. **`migration.test.ts`**: migrateLockEntry (version normalization, files passthrough), migrateLock (full lock object)
3. **`source-fetcher.test.ts`**: computeSha single-file vs multi-file, normalizeContent (CRLF, BOM), FetchResult.files population
4. **`update.ts` tests**: Ghost file cleanup (files removed, empty dirs cleaned, pre-migration safe), version resolution in update flow
5. **`add.ts` tests**: New lockfile entries include files array and 64-char SHA

## 10. Implementation Order

Tasks should be implemented in dependency order:

1. **T-001**: `src/utils/version.ts` + tests -- pure functions, no dependencies (US-002, US-003, US-004)
2. **T-002**: `src/lockfile/types.ts` -- add `files` field (US-006, US-007)
3. **T-003**: `src/lockfile/migration.ts` + wire into readLockfile() + tests (US-007)
4. **T-004**: `src/updater/source-fetcher.ts` -- computeSha overload, normalizeContent, FetchResult.files + tests (US-001)
5. **T-005**: `src/commands/update.ts` -- version resolution, ghost file cleanup, multi-file write (US-003, US-004, US-005, US-006)
6. **T-006**: `src/commands/add.ts` -- switch SHA call sites, add files manifest, version extraction (US-001, US-003)
