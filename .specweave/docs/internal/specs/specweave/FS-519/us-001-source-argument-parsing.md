---
id: US-001
feature: FS-519
title: "Source Argument Parsing"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-001: Source Argument Parsing

**Feature**: [FS-519](./FEATURE.md)

**As a** developer
**I want** to pass a GitHub shorthand, full URL, or local path to `specweave get`
**So that** I do not need to remember different commands for different source formats

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the argument `owner/repo`, when the source parser runs, then it returns `{ type: "github", owner: "owner", repo: "repo", cloneUrl: "https://github.com/owner/repo.git" }`
- [x] **AC-US1-02**: Given the argument `https://github.com/org/my-repo`, when the source parser runs, then it returns `{ type: "github", owner: "org", repo: "my-repo", cloneUrl: "https://github.com/org/my-repo.git" }`
- [x] **AC-US1-03**: Given the argument `git@github.com:org/repo.git`, when the source parser runs, then it returns `{ type: "github", owner: "org", repo: "repo", cloneUrl: "git@github.com:org/repo.git" }`
- [x] **AC-US1-04**: Given the argument `./path/to/repo`, when the source parser runs, then it returns `{ type: "local", absolutePath: "<resolved absolute path>" }`
- [x] **AC-US1-05**: Given a non-GitHub git URL like `https://gitlab.com/org/repo`, when the source parser runs, then it returns `{ type: "git", cloneUrl: "https://gitlab.com/org/repo", owner: "org", repo: "repo" }`

---

## Implementation

**Increment**: [0519-specweave-add-command](../../../../../increments/0519-specweave-add-command/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
