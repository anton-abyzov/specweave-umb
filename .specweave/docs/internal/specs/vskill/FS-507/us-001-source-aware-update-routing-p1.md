---
id: US-001
feature: FS-507
title: "Source-Aware Update Routing (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill user."
project: vskill
---

# US-001: Source-Aware Update Routing (P1)

**Feature**: [FS-507](./FEATURE.md)

**As a** vskill user
**I want** `vskill update` to parse the lockfile `source` field and fetch from the correct origin
**So that** skills installed from any source type are updated properly instead of failing silently

---

## Acceptance Criteria

- [x] **AC-US1-01**: `source` field is parsed into a typed discriminant: `registry:`, `github:` (flat), `github:...#plugin:` (plugin dir), `marketplace:`, `local:`
- [x] **AC-US1-02**: `registry:name` sources fetch via existing `getSkill()` API call (unchanged behavior)
- [x] **AC-US1-03**: `github:owner/repo` sources fetch SKILL.md from `raw.githubusercontent.com` using detected default branch
- [x] **AC-US1-04**: `github:owner/repo#plugin:name` sources with `pluginDir === true` re-fetch the full plugin directory (all `skills/*/SKILL.md` files under the plugin)
- [x] **AC-US1-05**: `marketplace:owner/repo#name` sources re-fetch `marketplace.json` from GitHub raw URL, resolve the plugin source path, then fetch the SKILL.md content
- [x] **AC-US1-06**: `local:*` sources print an informational skip message ("managed by specweave refresh-plugins") and do not attempt a fetch
- [x] **AC-US1-07**: Missing or unrecognized source prefixes fall back to registry lookup via `getSkill()` with a dim warning printed

---

## Implementation

**Increment**: [0507-vskill-update-all-sources](../../../../../increments/0507-vskill-update-all-sources/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Add new test cases to src/commands/update.test.ts
- [x] **T-006**: Modify src/commands/update.ts to use parseSource + fetchFromSource
