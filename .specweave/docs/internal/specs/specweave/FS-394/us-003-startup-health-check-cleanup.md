---
id: US-003
feature: FS-394
title: Startup Health Check Cleanup
status: complete
priority: P2
created: 2026-03-01
project: specweave
external:
  github:
    issue: 1457
    url: https://github.com/anton-abyzov/specweave/issues/1457
---
# US-003: Startup Health Check Cleanup

**Feature**: [FS-394](./FEATURE.md)

SpecWeave developer
**I want** the startup health check to not reference the removed marketplace directory
**So that** startup scripts don't log false warnings about missing directories

---

## Acceptance Criteria

- [x] **AC-US3-01**: `startup-health-check.sh` does not reference `~/.claude/plugins/marketplaces/specweave` as a dependency
- [x] **AC-US3-02**: The `SPECWEAVE_DIR` variable in startup-health-check.sh is updated or removed if it only pointed to the marketplace directory

---

## Implementation

**Increment**: [0394-unified-plugin-install-via-repo](../../../../../increments/0394-unified-plugin-install-via-repo/spec.md)

