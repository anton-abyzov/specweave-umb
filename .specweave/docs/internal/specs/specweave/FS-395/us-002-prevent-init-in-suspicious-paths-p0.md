---
id: US-002
feature: FS-395
title: "Prevent Init in Suspicious Paths (P0)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-002: Prevent Init in Suspicious Paths (P0)

**Feature**: [FS-395](./FEATURE.md)

**As a** developer
**I want** `specweave init` to warn me when I'm trying to initialize in a path that looks like it's deep inside a project (e.g., `src/`, `node_modules/`, `dist/`)
**So that** I don't accidentally create orphaned `.specweave/` folders in wrong locations

---

## Acceptance Criteria

- [x] **AC-US2-01**: When `specweave init` target directory path contains any suspicious segment (node_modules, src, dist, build, .git, vendor, __pycache__, .next, .nuxt, .output, coverage, tmp, temp, Resources/Audio, test, tests, __tests__, stories, storybook), init MUST refuse and show a warning
- [x] **AC-US2-02**: The warning message MUST explain why the path looks suspicious and suggest the likely project root
- [x] **AC-US2-03**: When `--force` flag is passed, the suspicious path check MUST be bypassed with a warning
- [x] **AC-US2-04**: In CI/quick mode (`--quick`), suspicious path check MUST still block (not auto-skip) unless `--force` is also passed
- [x] **AC-US2-05**: The suspicious segments list MUST be configurable/extensible (exported constant, not hardcoded inline)

---

## Implementation

**Increment**: [0395-init-location-guard-rails](../../../../../increments/0395-init-location-guard-rails/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add detectSuspiciousPath() to path-utils.ts
- [x] **T-004**: Integrate suspicious path guard into init.ts
- [x] **T-005**: Build, test, verify
