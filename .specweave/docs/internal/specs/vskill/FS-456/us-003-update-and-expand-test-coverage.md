---
id: US-003
feature: FS-456
title: "Update and expand test coverage"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** developer maintaining the vskill CLI."
project: vskill
external:
  github:
    issue: 27
    url: https://github.com/anton-abyzov/vskill/issues/27
---

# US-003: Update and expand test coverage

**Feature**: [FS-456](./FEATURE.md)

**As a** developer maintaining the vskill CLI
**I want** tests that verify the corrected `safeProjectRoot()` and new boundary guards
**So that** regressions are caught immediately

---

## Acceptance Criteria

- [x] **AC-US3-01**: TC-012 in `add.test.ts` is updated to assert `safeProjectRoot()` calls `findProjectRoot()` instead of asserting the old stub behavior
- [x] **AC-US3-02**: New tests in `add.test.ts` cover: findProjectRoot integration, null fallback to cwd, HOME guard fallback, and `--cwd` bypass
- [x] **AC-US3-03**: New tests in `canonical.test.ts` cover: `resolveAgentSkillsDir` rejects `../` traversal, `ensureCanonicalDir` throws on HOME for non-global, and `ensureCanonicalDir` allows subdirectories of HOME

---

## Implementation

**Increment**: [0456-prevent-unwanted-agent-dotfolders](../../../../../increments/0456-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Update TC-012 and add new safeProjectRoot tests in add.test.ts
- [x] **T-004**: Add boundary guard tests in canonical.test.ts
