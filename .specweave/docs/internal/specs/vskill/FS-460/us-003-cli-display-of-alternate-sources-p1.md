---
id: US-003
feature: FS-460
title: "CLI display of alternate sources (P1)"
status: completed
priority: P0
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** CLI user running `vskill find`."
project: vskill
related_projects: [vskill-platform]
external:
  github:
    issue: 40
    url: https://github.com/anton-abyzov/vskill/issues/40
---

# US-003: CLI display of alternate sources (P1)

**Feature**: [FS-460](./FEATURE.md)

**As a** CLI user running `vskill find`
**I want** to see alternate source repos when a result has them
**So that** I know the skill is available from multiple repos and can choose

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given the `SkillSearchResult` interface in `client.ts`, when updated, then it includes `alternateRepos?: Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>`
- [x] **AC-US3-02**: Given a search result with `alternateRepos` and TTY output, when displayed, then a line reading `also: owner/other-repo` appears in dim text below the main entry
- [x] **AC-US3-03**: Given a search result with `alternateRepos` and `--json` flag, when output is rendered, then the `alternateRepos` array is included in the JSON object
- [x] **AC-US3-04**: Given a search result with `alternateRepos` and piped (non-TTY) output, when displayed, then alternate repos are appended as a tab-separated field after existing columns

---

## Implementation

**Increment**: [0460-vendor-provider-discovery](../../../../../increments/0460-vendor-provider-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Add alternateRepos to SkillSearchResult in client.ts
- [x] **T-009**: Update find.ts to display alternate repos in TTY, JSON, and piped modes
