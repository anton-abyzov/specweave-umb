---
id: US-002
feature: FS-519
title: "Clone Repository"
status: not_started
priority: P1
created: 2026-03-13
tldr: "**As a** developer."
project: specweave
---

# US-002: Clone Repository

**Feature**: [FS-519](./FEATURE.md)

**As a** developer
**I want** `specweave add` to clone a remote repository into the correct directory
**So that** I do not need to manually clone and place repos

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given an umbrella workspace and source `owner/repo`, when the clone runs, then the repo is cloned to `repositories/owner/repo/`
- [ ] **AC-US2-02**: Given a non-umbrella workspace and source `owner/repo`, when the clone runs, then the repo is cloned to `./repo/` in the current directory
- [ ] **AC-US2-03**: Given `--branch feature-x` is passed, when the clone runs, then the repo is cloned with `git clone --branch feature-x`
- [ ] **AC-US2-04**: Given the target directory `repositories/owner/repo/` already exists and contains a `.git` directory, when clone is attempted, then the clone step is skipped and the command prints "Repository already exists at <path>, skipping clone"
- [ ] **AC-US2-05**: Given git authentication fails during clone, when the error is caught, then the command prints an error message suggesting `gh auth login` or SSH key setup

---

## Implementation

**Increment**: [0519-specweave-add-command](../../../../../increments/0519-specweave-add-command/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
