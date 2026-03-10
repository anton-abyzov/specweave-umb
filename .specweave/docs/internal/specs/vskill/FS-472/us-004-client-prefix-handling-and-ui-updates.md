---
id: US-004
feature: FS-472
title: "Client Prefix Handling and UI Updates"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill author using the Activation Panel."
project: vskill
---

# US-004: Client Prefix Handling and UI Updates

**Feature**: [FS-472](./FEATURE.md)

**As a** skill author using the Activation Panel
**I want** clear visual feedback on which prompts were auto-classified
**So that** I can understand and trust the test results

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Given a prompt with no prefix, when sent to the server, then the client sends `expected: "auto"` instead of `"should_activate"`
- [ ] **AC-US4-02**: Given a prompt with `+` prefix, when sent to the server, then the client sends `expected: "should_activate"` with the prefix stripped
- [ ] **AC-US4-03**: Given activation results containing auto-classified prompts, when displayed in the UI, then an "Auto" badge is shown next to the resolved expectation
- [ ] **AC-US4-04**: Given the Activation Panel help text, when viewing the prompt input area, then it documents all three conventions: no prefix (auto), `+` (activate), `!` (not activate)

---

## Implementation

**Increment**: [0472-activation-auto-classify](../../../../../increments/0472-activation-auto-classify/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-005**: Update WorkspaceContext to send "auto" for unprefixed prompts and handle "+" prefix
- [ ] **T-006**: Add Auto badge in ActivationPanel result rows and update help text
