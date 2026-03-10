---
id: US-002
feature: FS-456
title: "Add boundary guards in canonical installer"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** CLI maintainer."
project: vskill
external:
  github:
    issue: 26
    url: https://github.com/anton-abyzov/vskill/issues/26
---

# US-002: Add boundary guards in canonical installer

**Feature**: [FS-456](./FEATURE.md)

**As a** CLI maintainer
**I want** the installer to reject path traversal in agent definitions and HOME directory installs
**So that** malformed registry data or misconfigured roots cannot pollute the filesystem outside the project

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given an agent definition with `localSkillsDir` containing `../` that would resolve above `projectRoot`, when `resolveAgentSkillsDir()` is called for a non-global install, then it throws an error
- [x] **AC-US2-02**: Given `base` equals `os.homedir()` exactly, when `ensureCanonicalDir()` is called with `global: false`, then it throws an error with a clear message
- [x] **AC-US2-03**: Given `base` is a subdirectory of HOME (not HOME itself), when `ensureCanonicalDir()` is called with `global: false`, then it creates the directory normally

---

## Implementation

**Increment**: [0456-prevent-unwanted-agent-dotfolders](../../../../../increments/0456-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: Add path traversal guard in resolveAgentSkillsDir() and HOME guard in ensureCanonicalDir()
