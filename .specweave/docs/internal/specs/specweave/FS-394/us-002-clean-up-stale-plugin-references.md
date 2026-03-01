---
id: US-002
feature: FS-394
title: Clean Up Stale Plugin References
status: complete
priority: P2
created: 2026-03-01
project: specweave
external:
  github:
    issue: 1456
    url: https://github.com/anton-abyzov/specweave/issues/1456
---
# US-002: Clean Up Stale Plugin References

**Feature**: [FS-394](./FEATURE.md)

SpecWeave developer
**I want** the `VSKILL_REPO_PLUGINS` list to match the actual plugins available in the vskill marketplace
**So that** install attempts for non-existent plugins don't fail silently

---

## Acceptance Criteria

- [x] **AC-US2-01**: `k8s` is removed from `VSKILL_REPO_PLUGINS` (infra plugin covers Kubernetes)
- [x] **AC-US2-02**: `cost` is removed from `VSKILL_REPO_PLUGINS` (not in vskill marketplace)
- [x] **AC-US2-03**: `docs` is removed from `VSKILL_REPO_PLUGINS` (docs is a specweave sw-* plugin at `anton-abyzov/specweave`, not a vskill domain plugin)
- [x] **AC-US2-04**: The suggest-only mode message (line ~1266) uses the `--repo` flag syntax instead of `--plugin-dir`

---

## Implementation

**Increment**: [0394-unified-plugin-install-via-repo](../../../../../increments/0394-unified-plugin-install-via-repo/spec.md)

