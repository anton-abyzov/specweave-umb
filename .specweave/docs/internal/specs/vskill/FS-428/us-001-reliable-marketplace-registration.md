---
id: US-001
feature: FS-428
title: "Reliable marketplace registration"
status: completed
priority: P2
created: 2026-03-05T00:00:00.000Z
tldr: "**As a** plugin developer."
project: vskill
external:
  github:
    issue: 13
    url: https://github.com/anton-abyzov/vskill/issues/13
---

# US-001: Reliable marketplace registration

**Feature**: [FS-428](./FEATURE.md)

**As a** plugin developer
**I want** marketplace registration to never use temp directory paths
**So that** my plugins don't break after install

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a source path matching the `os.tmpdir()` prefix, when `registerMarketplace()` is called, then the temp path is detected and skipped with a clear warning message logged to stderr
- [x] **AC-US1-02**: Given any call to `registerMarketplace()`, when the underlying `claude plugin marketplace add` command runs, then stderr is captured and the return type is `{ success: boolean; stderr?: string }` instead of bare `boolean`
- [x] **AC-US1-03**: Given a failed registration, when `registerMarketplace()` detects the failure, then it retries once after deregistering the stale entry via `claude plugin marketplace remove`, returning success only if the retry succeeds

---

## Implementation

**Increment**: [0428-plugin-install-reliability](../../../../../increments/0428-plugin-install-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Update tests for all changed modules
