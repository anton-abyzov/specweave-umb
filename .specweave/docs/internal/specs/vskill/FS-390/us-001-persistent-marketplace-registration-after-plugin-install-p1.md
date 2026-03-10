---
id: US-001
feature: FS-390
title: "Persistent marketplace registration after plugin install (P1)"
status: completed
priority: P1
created: 2026-02-28
tldr: "**As a** developer installing plugins from a marketplace repo."
project: vskill
---

# US-001: Persistent marketplace registration after plugin install (P1)

**Feature**: [FS-390](./FEATURE.md)

**As a** developer installing plugins from a marketplace repo
**I want** the marketplace to be registered using its GitHub source identifier
**So that** Claude Code can resolve the marketplace for future operations (list, update, uninstall) without relying on a temp directory that gets deleted

---

## Acceptance Criteria

- [x] **AC-US1-01**: `installMarketplaceRepo()` calls `registerMarketplace()` with `${owner}/${repo}` (GitHub shorthand) instead of `tmpDir`
- [x] **AC-US1-02**: `registerMarketplace()` JSDoc `@param` is updated from "Absolute path to the repo root" to document it accepts any valid marketplace source (path, URL, or GitHub `owner/repo`)
- [x] **AC-US1-03**: The shallow clone to tmpDir is still performed (needed for fallback extraction), but tmpDir is no longer passed to `registerMarketplace()`
- [x] **AC-US1-04**: `tryNativeClaudeInstall()` continues to use `resolve(basePath)` (local persistent path) -- no change needed there

---

## Implementation

**Increment**: [0390-fix-marketplace-source-registration](../../../../../increments/0390-fix-marketplace-source-registration/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: RED - Write tests asserting GitHub source registration
- [x] **T-002**: GREEN - Fix registerMarketplace call in installMarketplaceRepo
- [x] **T-003**: REFACTOR - Update registerMarketplace JSDoc and parameter name
- [x] **T-004**: Final verification
