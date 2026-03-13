---
id: US-003
feature: FS-519
title: "Register in Umbrella Config"
status: not_started
priority: P1
created: 2026-03-13
tldr: "**As a** developer."
project: specweave
---

# US-003: Register in Umbrella Config

**Feature**: [FS-519](./FEATURE.md)

**As a** developer
**I want** the cloned repo to be automatically registered in the umbrella config
**So that** SpecWeave recognizes it as a child repo for increments and sync

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given an umbrella workspace and a cloned repo at `repositories/org/repo/`, when registration runs, then `config.json` has a new entry in `umbrella.childRepos` with `id`, `path`, `name`, and `prefix`
- [ ] **AC-US3-02**: Given `--prefix BE` is passed, when registration runs, then the child repo entry uses prefix `"BE"`
- [ ] **AC-US3-03**: Given no `--prefix` is passed, when registration runs, then the prefix defaults to the first 3 uppercase characters of the repo name
- [ ] **AC-US3-04**: Given the repo is already present in `umbrella.childRepos` (matching by id), when registration runs, then no duplicate entry is created and the command prints "Already registered in umbrella config"
- [ ] **AC-US3-05**: Given `--role backend` is passed, when registration runs, then the child repo entry includes `role: "backend"` in its config

---

## Implementation

**Increment**: [0519-specweave-add-command](../../../../../increments/0519-specweave-add-command/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
