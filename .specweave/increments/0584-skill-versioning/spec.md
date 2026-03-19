---
increment: 0584-skill-versioning
title: Skill Versioning for Verified Skills
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Versioning for Verified Skills

## Problem Statement

The current `computeSha()` in `source-fetcher.ts` hashes only SKILL.md content (truncated to 12 hex chars). Agent files (`agents/*.md`, `commands/*.md`) can change without triggering an update, causing silent staleness. There is no semantic versioning, no change detection across all skill files, and no handling of file deletions between versions. Developers cannot tell what version of a skill they have installed or whether it is current.

## Goals

- Detect changes across ALL files in a skill (SKILL.md, agents/*.md, commands/*.md) using a deterministic full-file hash
- Support semantic versioning (X.Y.Z) with frontmatter declaration and auto-increment patch fallback
- Skip updates when nothing has changed (no-op detection)
- Remove locally cached files that were deleted upstream (ghost file cleanup)
- Migrate existing lockfiles to the new format without breaking backward compatibility

## User Stories

### US-001: Full-File Hash Computation (P1)
**Project**: vskill
**As a** skill consumer
**I want** the CLI to hash all files in a skill deterministically
**So that** any change to any file (not just SKILL.md) triggers an update

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill with files `SKILL.md`, `agents/a.md`, `agents/b.md`, when computing the hash, then all three files are included in the hash computation
- [x] **AC-US1-02**: Given multiple files, when computing the hash, then files are sorted by path (case-sensitive ascending) and concatenated as `"path\0content\n"` per file before SHA-256 hashing
- [x] **AC-US1-03**: Given the hash output, when it is produced, then it is a full 64-character hex string (not truncated to 12)
- [x] **AC-US1-04**: Given file content with CRLF line endings, when computing the hash, then CRLF is normalized to LF before hashing
- [x] **AC-US1-05**: Given file content with a UTF-8 BOM prefix, when computing the hash, then the BOM is trimmed before hashing

---

### US-002: Frontmatter Version Extraction (P1)
**Project**: vskill
**As a** skill author
**I want** to declare a semantic version in my SKILL.md frontmatter
**So that** consumers see the version I intended rather than an auto-generated one

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a SKILL.md with `version: 2.1.0` in its YAML frontmatter, when the frontmatter is parsed, then the version `"2.1.0"` is extracted and returned
- [x] **AC-US2-02**: Given a SKILL.md with no `version` field in frontmatter, when the frontmatter is parsed, then `undefined` is returned for the version field
- [x] **AC-US2-03**: Given a SKILL.md with `version: not-semver`, when the frontmatter is parsed, then the invalid value is ignored and `undefined` is returned

---

### US-003: Version Resolution Logic (P1)
**Project**: vskill
**As a** skill consumer
**I want** the CLI to resolve a skill version from either frontmatter or hash comparison
**So that** every installed skill has a meaningful semantic version

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a skill with `version: 3.0.0` declared in frontmatter, when installing or updating, then version `"3.0.0"` is used regardless of hash comparison
- [x] **AC-US3-02**: Given a skill with no version declaration and a hash that differs from the stored hash, when updating, then the patch version is auto-incremented (e.g., `1.0.0` becomes `1.0.1`)
- [x] **AC-US3-03**: Given a skill with no version declaration and a hash identical to the stored hash, when updating, then the update is skipped entirely (no file writes, no version bump)
- [x] **AC-US3-04**: Given a skill being installed for the first time with no version declaration, when installing, then version `"1.0.0"` is assigned

---

### US-004: Auto-Increment Patch on Change (P1)
**Project**: vskill
**As a** skill consumer
**I want** the CLI to auto-bump the patch version when a skill changes without a declared version
**So that** I can see version progression even when authors do not declare versions

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a skill at version `1.0.0` with no frontmatter version, when `vskill update` detects a new hash, then the lockfile version becomes `1.0.1`
- [x] **AC-US4-02**: Given a skill at version `1.2.5` with no frontmatter version, when `vskill update` detects a new hash, then the lockfile version becomes `1.2.6`
- [x] **AC-US4-03**: Given a skill with a frontmatter version `2.0.0` and a stored version `1.0.3`, when `vskill update` runs, then the lockfile version becomes `2.0.0` (frontmatter takes precedence over auto-increment)

---

### US-005: No-Change Detection (P1)
**Project**: vskill
**As a** skill consumer
**I want** the CLI to skip updates when the skill has not changed
**So that** unnecessary file writes and version bumps are avoided

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a skill whose full-file hash matches the stored hash in the lockfile, when `vskill update` runs, then no files are written to disk
- [x] **AC-US5-02**: Given a skill whose full-file hash matches the stored hash, when `vskill update` runs, then the lockfile entry is not modified (version, sha, updatedAt all unchanged)
- [x] **AC-US5-03**: Given a skill whose full-file hash matches the stored hash, when `vskill update` runs, then a "no changes" message is printed (not an "updated" message)

---

### US-006: Ghost File Cleanup (P1)
**Project**: vskill
**As a** skill consumer
**I want** the CLI to delete local files that were removed in a newer version of a skill
**So that** stale files from previous versions do not persist and cause confusion

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given a skill previously installed with files `[SKILL.md, agents/a.md, agents/b.md]` and a new version containing only `[SKILL.md, agents/a.md]`, when updating, then `agents/b.md` is deleted from the local installation directory
- [x] **AC-US6-02**: Given a skill update that removes files, when the update completes, then the lockfile `files` array reflects only the files present in the new version
- [x] **AC-US6-03**: Given a skill with no previous `files` manifest in the lockfile (pre-migration entry), when updating, then no files are deleted (safe fallback) and the new manifest is stored

---

### US-007: Lockfile Migration (P1)
**Project**: vskill
**As a** skill consumer
**I want** the lockfile to auto-migrate old entries on read
**So that** upgrading vskill does not require manual lockfile edits

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given a lockfile entry with `version: ""`, when the lockfile is read, then the version is set to `"1.0.0"` in memory
- [x] **AC-US7-02**: Given a lockfile entry with `version: "0.0.0"`, when the lockfile is read, then the version is set to `"1.0.0"` in memory
- [x] **AC-US7-03**: Given a lockfile entry with no `files` field, when the lockfile is read, then `files` defaults to `undefined` (not an empty array) and no ghost file deletion is attempted
- [x] **AC-US7-04**: Given a lockfile entry with a valid `version: "2.3.1"`, when the lockfile is read, then the version is preserved unchanged

## Out of Scope

- Server-side version storage or registry API changes (Phase 2, specweave-platform)
- Version constraint syntax (e.g., `^1.0.0`, `~2.1`) for dependency resolution
- Changelog generation or diff display between versions
- Major/minor version auto-increment (only patch is auto-incremented)
- Rollback to a previous version of a skill
- Version pinning in project configuration

## Technical Notes

### Dependencies
- `node:crypto` (createHash) -- already imported in source-fetcher.ts
- `node:fs` (unlink) -- for ghost file deletion

### Constraints
- Lockfile format must remain backward compatible (new `files` field is optional)
- Hash algorithm change (12-char truncated to 64-char full) must not break existing lockfile reads

### Architecture Decisions
- **Full SHA-256 hex (64 chars)**: Truncating to 12 chars increases collision risk. Full hex is cheap to store and unambiguous
- **Deterministic hash format**: `"path\0content\n"` with sorted paths ensures identical input produces identical hash regardless of OS or fetch order
- **Content normalization**: CRLF to LF and BOM trimming applied before hashing on both client and server to prevent platform-dependent hash divergence
- **Server version authoritative**: Frontmatter version is an advisory override. When the server provides a version, it takes precedence. Frontmatter is the fallback for non-registry sources (GitHub, local)
- **Manifest in lockfile**: The `files` string array in `SkillLockEntry` tracks which files belong to a skill version, enabling ghost file detection without re-fetching

## Non-Functional Requirements

- **Performance**: Full-file hash computation completes in under 50ms for skills with up to 50 files
- **Compatibility**: Lockfile migration is transparent -- old vskill versions ignore the new `files` field, new versions auto-migrate old entries
- **Security**: SHA-256 ensures integrity verification. BOM/CRLF normalization prevents hash manipulation via encoding variations

## Edge Cases

- **Skill with only SKILL.md (no agents)**: Hash computed from single file; `files` manifest contains one entry
- **Empty file content**: File included in hash with empty content string (path\0\n)
- **Skill with nested directories**: e.g., `agents/sub/deep.md` -- path sorting and hashing works at any depth
- **Concurrent updates**: Two `vskill update` runs race on the same lockfile -- last write wins (existing behavior, no change)
- **Corrupted lockfile version**: Non-semver string in existing lockfile version field -- treated as `"1.0.0"` during migration
- **Files field already present**: Lockfile entry with existing `files` array is used as-is for ghost file comparison

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Hash change breaks all existing "up to date" checks, forcing re-download of every skill | 0.8 | 3 | 2.4 | Expected one-time cost on first `vskill update` after upgrade; document in changelog |
| Ghost file deletion removes user-modified files | 0.2 | 7 | 1.4 | Only delete files that appear in the OLD manifest but not the NEW manifest; never delete files outside the skill directory |
| Lockfile migration corrupts entries with unusual version strings | 0.1 | 8 | 0.8 | Migration only touches `""` and `"0.0.0"` values; all other values pass through unchanged |

## Success Metrics

- 100% of skill files are included in hash computation (verified by unit tests)
- Zero silent staleness: any file change triggers an update or explicit skip message
- Lockfile migration handles all existing production lockfile formats without error
- Ghost file cleanup removes 100% of orphaned files after version update
