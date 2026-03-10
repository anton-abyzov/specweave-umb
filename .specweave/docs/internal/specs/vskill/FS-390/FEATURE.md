---
id: FS-390
title: "Fix marketplace temp dir registered as source"
type: feature
status: completed
priority: P1
created: 2026-02-28
lastUpdated: 2026-03-10
tldr: "When `vskill install owner/repo` installs from a Claude Code plugin marketplace, `installMarketplaceRepo()` clones the repo to a temp directory and calls `registerMarketplace(tmpDir)`."
complexity: medium
stakeholder_relevant: true
---

# Fix marketplace temp dir registered as source

## TL;DR

**What**: When `vskill install owner/repo` installs from a Claude Code plugin marketplace, `installMarketplaceRepo()` clones the repo to a temp directory and calls `registerMarketplace(tmpDir)`.
**Status**: completed | **Priority**: P1
**User Stories**: 2

![Fix marketplace temp dir registered as source illustration](assets/feature-fs-390.jpg)

## Overview

When `vskill install owner/repo` installs from a Claude Code plugin marketplace, `installMarketplaceRepo()` clones the repo to a temp directory and calls `registerMarketplace(tmpDir)`. This registers the ephemeral temp path as the marketplace source with Claude Code. After the temp dir is cleaned up, the marketplace reference becomes stale -- `claude plugin list`, marketplace updates, and plugin management silently fail until the user manually runs `claude plugin marketplace remove`.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0390-fix-marketplace-source-registration](../../../../../increments/0390-fix-marketplace-source-registration/spec.md) | ✅ completed | 2026-02-28 |

## User Stories

- [US-001: Persistent marketplace registration after plugin install (P1)](./us-001-persistent-marketplace-registration-after-plugin-install-p1.md)
- [US-002: Test coverage for GitHub source registration (P1)](./us-002-test-coverage-for-github-source-registration-p1.md)
