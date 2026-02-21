---
id: FS-238
title: Complete uninstall support for specweave and vskill
type: feature
status: completed
priority: P1
created: 2026-02-18T00:00:00.000Z
lastUpdated: 2026-02-19
tldr: "Add uninstall/remove commands at all levels: `vskill remove` for
  individual skills, `specweave uninstall` for full project cleanup, and npm
  preuninstall lifecycle scripts for `npm uninstall -g` cleanup."
complexity: low
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 2
    url: https://github.com/anton-abyzov/specweave-umb/milestone/2
---

# Complete uninstall support for specweave and vskill

## TL;DR

**What**: Add uninstall/remove commands at all levels: `vskill remove` for individual skills, `specweave uninstall` for full project cleanup, and npm preuninstall lifecycle scripts for `npm uninstall -g` cleanup.
**Status**: completed | **Priority**: P1
**User Stories**: 1

## Overview

Add uninstall/remove commands at all levels: `vskill remove` for individual skills, `specweave uninstall` for full project cleanup, and npm preuninstall lifecycle scripts for `npm uninstall -g` cleanup.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0238-complete-uninstall-support](../../../../../increments/0238-complete-uninstall-support/spec.md) | ✅ completed | 2026-02-18T00:00:00.000Z |

## User Stories

- [US-002: Uninstall SpecWeave from a project (P1)](./us-002-uninstall-specweave-from-a-project-p1-.md)

## Related Projects

This feature spans multiple projects:

- [vskill](../../vskill/FS-238/)
- [specweave, vskill](../../specweave, vskill/FS-238/)
