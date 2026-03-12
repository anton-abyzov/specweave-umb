---
id: US-004
feature: FS-501
title: "Flag Precedence and Dry-Run Support (P2)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1550
    url: https://github.com/anton-abyzov/specweave/issues/1550
---

# US-004: Flag Precedence and Dry-Run Support (P2)

**Feature**: [FS-501](./FEATURE.md)

**As a** developer
**I want** `--repo` to take precedence over `--org`/`--pattern` and work with `--dry-run`
**So that** the CLI behavior is predictable and I can preview before cloning

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given both `--repo owner/repo` and `--org myorg` are provided, when the command runs, then `--repo` takes precedence and `--org`/`--pattern` are ignored
- [x] **AC-US4-02**: Given `--repo owner/repo` and `--dry-run`, when the command runs, then it validates the repo exists, prints what would be cloned, and does not actually clone
- [x] **AC-US4-03**: Given `--repo` with an unparseable value, when the command runs, then it exits with an error describing the supported formats

---

## Implementation

**Increment**: [0501-single-repo-clone](../../../../../increments/0501-single-repo-clone/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Implement and test dry-run and parse-error handling
