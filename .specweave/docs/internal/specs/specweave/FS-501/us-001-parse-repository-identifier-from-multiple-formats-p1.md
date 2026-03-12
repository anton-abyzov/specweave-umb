---
id: US-001
feature: FS-501
title: Parse Repository Identifier from Multiple Formats (P1)
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1547
    url: https://github.com/anton-abyzov/specweave/issues/1547
---

# US-001: Parse Repository Identifier from Multiple Formats (P1)

**Feature**: [FS-501](./FEATURE.md)

**As a** developer
**I want** to provide a repo in any common format (owner/repo, HTTPS URL, SSH URL)
**So that** I don't have to remember a specific format when cloning

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given input `owner/repo`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-02**: Given input `github.com/owner/repo`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-03**: Given input `https://github.com/owner/repo`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-04**: Given input `git@github.com:owner/repo.git`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-05**: Given input `invalid-string`, when parseRepoIdentifier() is called, then it returns null

---

## Implementation

**Increment**: [0501-single-repo-clone](../../../../../increments/0501-single-repo-clone/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Write failing tests for parseRepoIdentifier()
- [ ] **T-002**: Implement parseRepoIdentifier() to make tests pass
