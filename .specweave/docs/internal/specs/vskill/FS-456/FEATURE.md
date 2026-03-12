---
id: FS-456
title: "Prevent unwanted agent dot-folder creation"
type: feature
status: completed
priority: P1
created: "2026-03-09T00:00:00.000Z"
lastUpdated: 2026-03-10
tldr: "Running `vskill add` from a parent or umbrella directory creates agent dot-folders (`.aider/`, `.kiro/`, `.pi/`, `.codex/`, `.cursor/`, `.agent/`, `.windsurf/`, etc.) in the wrong location."
complexity: medium
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 12
    url: 'https://github.com/anton-abyzov/vskill/milestone/12'
externalLinks:
  jira:
    epicKey: 'SWE2E-104'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-104'
    syncedAt: '2026-03-10T09:44:32.312Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 169
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/169'
    syncedAt: '2026-03-10T09:44:32.764Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Prevent unwanted agent dot-folder creation

## TL;DR

**What**: Running `vskill add` from a parent or umbrella directory creates agent dot-folders (`.aider/`, `.kiro/`, `.pi/`, `.codex/`, `.cursor/`, `.agent/`, `.windsurf/`, etc.) in the wrong location.
**Status**: completed | **Priority**: P1
**User Stories**: 3

## Overview

Running `vskill add` from a parent or umbrella directory creates agent dot-folders (`.aider/`, `.kiro/`, `.pi/`, `.codex/`, `.cursor/`, `.agent/`, `.windsurf/`, etc.) in the wrong location. The root cause is twofold: `safeProjectRoot()` in `src/commands/add.ts` is a stub that always returns `process.cwd()` instead of walking up to find the actual project root, and the installer in `canonical.ts` lacks boundary guards to prevent directory creation above the project root or at HOME.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0456-prevent-unwanted-agent-dotfolders](../../../../../increments/0456-prevent-unwanted-agent-dotfolders/spec.md) | ✅ completed | 2026-03-09T00:00:00.000Z |

## User Stories

- [US-001: Fix safeProjectRoot to resolve actual project root](./us-001-fix-safeprojectroot-to-resolve-actual-project-root.md)
- [US-002: Add boundary guards in canonical installer](./us-002-add-boundary-guards-in-canonical-installer.md)
- [US-003: Update and expand test coverage](./us-003-update-and-expand-test-coverage.md)
