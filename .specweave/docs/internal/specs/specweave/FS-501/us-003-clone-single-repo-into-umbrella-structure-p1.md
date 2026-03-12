---
id: US-003
feature: FS-501
title: Clone Single Repo into Umbrella Structure (P1)
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1549
    url: https://github.com/anton-abyzov/specweave/issues/1549
---

# US-003: Clone Single Repo into Umbrella Structure (P1)

**Feature**: [FS-501](./FEATURE.md)

**As a** developer
**I want** `--repo owner/repo` to clone into `repositories/{owner}/{repo}/`
**So that** the repo follows the existing umbrella convention and gets registered in childRepos

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given `--repo owner/repo` and the repo does not exist locally, when the clone command runs, then the repo is cloned to `repositories/{owner}/{repo}/` via the background job system
- [ ] **AC-US3-02**: Given `--repo owner/repo` and `repositories/{owner}/{repo}/.git` already exists, when the clone command runs, then it skips cloning and reports the repo is already cloned
- [ ] **AC-US3-03**: Given a successful clone, when the clone worker completes, then `config.json` umbrella.childRepos includes an entry with `id: repo`, `path: repositories/{owner}/{repo}`
- [ ] **AC-US3-04**: Given input in SSH format `git@github.com:owner/repo.git`, when the clone runs, then it uses the SSH clone URL (no PAT embedded)
- [ ] **AC-US3-05**: Given input in HTTPS or shorthand format, when the clone runs, then it uses the HTTPS clone URL with the resolved PAT

---

## Implementation

**Increment**: [0501-single-repo-clone](../../../../../increments/0501-single-repo-clone/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-004**: Write failing tests for clone path, skip, and URL format behavior
- [ ] **T-005**: Implement clone dispatch in cloneSingleGitHubRepo()
