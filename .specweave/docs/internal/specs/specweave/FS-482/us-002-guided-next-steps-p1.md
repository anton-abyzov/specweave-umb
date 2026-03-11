---
id: US-002
feature: FS-482
title: Guided Next Steps (P1)
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1529
    url: https://github.com/anton-abyzov/specweave/issues/1529
---

# US-002: Guided Next Steps (P1)

**Feature**: [FS-482](./FEATURE.md)

**As a** developer
**I want** clear guidance after init on what commands to run next
**So that** I know how to configure external tools and start working

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given a successful init, when the completion output is displayed, then it shows 3 follow-up commands: `specweave sync-setup`, `specweave increment "feature"`, and `specweave migrate-to-umbrella` with brief descriptions
- [ ] **AC-US2-02**: Given a successful init, when the summary banner is displayed, then it shows the project name, detected adapter, detected provider, and language
- [ ] **AC-US2-03**: Given any adapter (Claude, Cursor, Generic), when next steps are displayed, then verbose adapter-specific instruction blocks are removed in favor of the universal command list
- [ ] **AC-US2-04**: Given a successful init, when the output is displayed, then documentation and GitHub links are still present

---

## Implementation

**Increment**: [0482-simplify-init](../../../../../increments/0482-simplify-init/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-006**: Verify guided commands appear in next-steps output
- [ ] **T-007**: Verify summary banner shows project/adapter/provider/language
