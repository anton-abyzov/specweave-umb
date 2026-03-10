---
id: US-001
feature: FS-461
title: "Fetch GitHub Stars at Publish Time"
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** skill searcher."
project: vskill-platform
---

# US-001: Fetch GitHub Stars at Publish Time

**Feature**: [FS-461](./FEATURE.md)

**As a** skill searcher
**I want** newly published skills to show their GitHub star count immediately
**So that** I can assess skill popularity from the first search result

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill being published, when `publishSkill()` runs, then it fetches GitHub stars via the GitHub REST API (5s timeout) before the DB upsert and stores the result in `githubStars`
- [x] **AC-US1-02**: Given the GitHub API is unavailable or times out, when `publishSkill()` runs, then it falls back to `githubStars: 0` without failing the publish
- [x] **AC-US1-03**: Given a skill is published with fetched stars, when the search shard is updated, then the shard entry reflects the fetched star count (not 0)

---

## Implementation

**Increment**: [0461-skill-star-freshness](../../../../../increments/0461-skill-star-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
