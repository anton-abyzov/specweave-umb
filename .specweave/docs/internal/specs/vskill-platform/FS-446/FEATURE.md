---
id: FS-446
title: "Rename Authors to Publishers + Show publisher/skill-name Format"
type: feature
status: completed
priority: P1
created: "2026-03-07T00:00:00.000Z"
lastUpdated: 2026-03-10
tldr: "The vskill-platform UI uses 'Authors' to refer to skill owners, but 'Publishers' better reflects their role: they publish skills to the marketplace."
complexity: high
stakeholder_relevant: true
---

# Rename Authors to Publishers + Show publisher/skill-name Format

## TL;DR

**What**: The vskill-platform UI uses "Authors" to refer to skill owners, but "Publishers" better reflects their role: they publish skills to the marketplace.
**Status**: completed | **Priority**: P1
**User Stories**: 5

## Overview

The vskill-platform UI uses "Authors" to refer to skill owners, but "Publishers" better reflects their role: they publish skills to the marketplace. Additionally, skills are currently shown by name alone, which can be ambiguous when multiple publishers have similarly named skills. Adopting a `publisher/skill-name` display format (analogous to GitHub's `owner/repo`) eliminates ambiguity.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0446-rename-authors-to-publishers](../../../../../increments/0446-rename-authors-to-publishers/spec.md) | ✅ completed | 2026-03-07T00:00:00.000Z |

## User Stories

- [US-001: URL Rename with Backwards-Compatible Redirects](./us-001-url-rename-with-backwards-compatible-redirects.md)
- [US-002: UI Text and Navigation Rename](./us-002-ui-text-and-navigation-rename.md)
- [US-003: Skill Display with publisher/skill-name Format](./us-003-skill-display-with-publisher-skill-name-format.md)
- [US-004: TypeScript Type and Function Renames](./us-004-typescript-type-and-function-renames.md)
- [US-005: CSS Class and File Renames](./us-005-css-class-and-file-renames.md)
