---
id: FS-383
title: "Fix failing develop branch tests and unblock Dependabot auto-merge pipeline"
type: feature
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
lastUpdated: 2026-02-28
tldr: "The develop branch has 69 test failures across 18 test files caused by source code refactoring that left tests pointing at old module paths and asserting stale expectations."
complexity: high
stakeholder_relevant: true
---

# Fix failing develop branch tests and unblock Dependabot auto-merge pipeline

## TL;DR

**What**: The develop branch has 69 test failures across 18 test files caused by source code refactoring that left tests pointing at old module paths and asserting stale expectations.
**Status**: completed | **Priority**: P1
**User Stories**: 6

![Fix failing develop branch tests and unblock Dependabot auto-merge pipeline illustration](assets/feature-fs-383.jpg)

## Overview

The develop branch has 69 test failures across 18 test files caused by source code refactoring that left tests pointing at old module paths and asserting stale expectations. Additionally, the Dependabot auto-merge workflow fails because GITHUB_TOKEN cannot approve PRs. This increment fixes all 69 failures and unblocks auto-merge.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md) | ✅ completed | 2026-02-27T00:00:00.000Z |

## User Stories

- [US-001: Fix module resolution failures (P1)](./us-001-fix-module-resolution-failures-p1-.md)
- [US-002: Fix assertion drift in external-issue-auto-creator tests (P1)](./us-002-fix-assertion-drift-in-external-issue-auto-creator-tests-p1-.md)
- [US-003: Fix assertion drift in GitHub sync tests (P1)](./us-003-fix-assertion-drift-in-github-sync-tests-p1-.md)
- [US-004: Fix assertion drift in CLI and plugin tests (P1)](./us-004-fix-assertion-drift-in-cli-and-plugin-tests-p1-.md)
- [US-005: Fix assertion drift in skills and infrastructure tests (P1)](./us-005-fix-assertion-drift-in-skills-and-infrastructure-tests-p1-.md)
- [US-006: Unblock Dependabot auto-merge workflow (P1)](./us-006-unblock-dependabot-auto-merge-workflow-p1-.md)
