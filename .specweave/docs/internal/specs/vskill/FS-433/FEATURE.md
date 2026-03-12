---
id: FS-433
title: Marketplace Unregistered Plugin Discovery
type: feature
status: ready_for_review
priority: P1
created: 2026-03-05
lastUpdated: 2026-03-07
tldr: When a repo author adds a new plugin directory (e.g.,
  `plugins/marketing/`) to their GitHub repo but has not updated
  `.claude-plugin/marketplace.json`, users running `npx vskill i owner/repo`
  cannot see or install the new plugin.
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 9
    url: "https://github.com/anton-abyzov/vskill/milestone/9"
---

# Marketplace Unregistered Plugin Discovery

## TL;DR

**What**: When a repo author adds a new plugin directory (e.g., `plugins/marketing/`) to their GitHub repo but has not updated `.claude-plugin/marketplace.json`, users running `npx vskill i owner/repo` cannot see or install the new plugin.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 5

## Overview

When a repo author adds a new plugin directory (e.g., `plugins/marketing/`) to their GitHub repo but has not updated `.claude-plugin/marketplace.json`, users running `npx vskill i owner/repo` cannot see or install the new plugin. The marketplace manifest is the only source of truth for the plugin picker, so filesystem-only plugins are invisible. This creates a gap where authors ship code but consumers cannot access it until the manifest catches up.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0433-marketplace-unregistered-plugin-discovery](../../../../../increments/0433-marketplace-unregistered-plugin-discovery/spec.md) | ⏳ ready_for_review | 2026-03-05 |

## User Stories

- [US-001: Discover Unregistered Plugin Directories](./us-001-discover-unregistered-plugin-directories.md)
- [US-002: Display Unregistered Plugins in Picker UI](./us-002-display-unregistered-plugins-in-picker-ui.md)
- [US-003: Gate Unregistered Plugin Installation Behind --force](./us-003-gate-unregistered-plugin-installation-behind-force.md)
- [US-004: Non-TTY and Auto-Select Mode Handling](./us-004-non-tty-and-auto-select-mode-handling.md)
- [US-005: Repo Re-Submission for Platform Scanning](./us-005-repo-re-submission-for-platform-scanning.md)
