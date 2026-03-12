---
id: US-001
feature: FS-387
title: "Scope blocklist matching to sourceUrl"
status: completed
priority: P1
created: "2026-02-27T00:00:00.000Z"
tldr: "**As a** platform admin."
project: vskill-platform
---

# US-001: Scope blocklist matching to sourceUrl

**Feature**: [FS-387](./FEATURE.md)

**As a** platform admin
**I want** blocklist entries to be scoped to the specific source repo/registry, not just the skill name
**So that** blocking a malicious "google" skill from one repo does not block legitimate "google" skills from other repos

---

## Acceptance Criteria

- [x] **AC-US1-01**: `processSubmission` early blocklist check matches on `skillName` AND (`sourceUrl` matches repoUrl OR `sourceUrl IS NULL` for global bans)
- [x] **AC-US1-02**: `finalize-scan` route early blocklist check uses the same scoped matching logic
- [x] **AC-US1-03**: `blocklist/check` API endpoint accepts optional `repoUrl` param and uses scoped matching
- [x] **AC-US1-04**: Blocklist entries with `sourceUrl = null` act as global name bans (backward compat)
- [x] **AC-US1-05**: `upsertBlocklistEntry` dedup lookup includes `sourceUrl` so entries from different repos do not merge
- [x] **AC-US1-06**: Existing seed data entries continue to work correctly -- they block their specific malicious repos
- [x] **AC-US1-07**: `repo-block` route continues to work correctly, creating per-repo scoped blocklist entries

---

## Implementation

**Increment**: [0387-blocklist-dedup-poisoning-fixes](../../../../../increments/0387-blocklist-dedup-poisoning-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
