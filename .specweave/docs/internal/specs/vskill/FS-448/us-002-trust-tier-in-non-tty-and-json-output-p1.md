---
id: US-002
feature: FS-448
title: Trust tier in non-TTY and JSON output (P1)
status: completed
priority: P1
created: 2026-03-07
tldr: "**As a** developer piping `vskill find` output to other tools."
project: vskill
related_projects:
  - vskill-platform
external:
  github:
    issue: 85
    url: https://github.com/anton-abyzov/vskill/issues/85
---

# US-002: Trust tier in non-TTY and JSON output (P1)

**Feature**: [FS-448](./FEATURE.md)

**As a** developer piping `vskill find` output to other tools
**I want** the trust tier to appear in non-TTY tab-separated and JSON output
**So that** I can programmatically filter or sort skills by trust level

---

## Acceptance Criteria

- [x] **AC-US2-01**: Non-TTY tab-separated output includes trustTier as the 4th column (after stars)
- [x] **AC-US2-02**: JSON output (--json) includes the trustTier field on each result
- [x] **AC-US2-03**: Blocked skills in non-TTY output show "BLOCKED" as the 3rd column (no trust tier column)

---

## Implementation

**Increment**: [0448-trust-badges-find](../../../../../increments/0448-trust-badges-find/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
