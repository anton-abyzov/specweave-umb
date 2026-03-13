---
id: FS-519
title: "specweave add CLI command"
type: feature
status: planned
priority: P1
created: 2026-03-13
lastUpdated: 2026-03-13
tldr: "Adding repositories to a SpecWeave umbrella workspace requires manual steps: cloning with git, placing into the correct `repositories/{org}/{repo}/` directory, editing config.json to register in `childRepos`, and optionally running `specweave init`."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-194'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-194'
    syncedAt: '2026-03-13T03:52:19.434Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1226
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1226'
    syncedAt: '2026-03-13T03:52:29.744Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# specweave add CLI command

## TL;DR

**What**: Adding repositories to a SpecWeave umbrella workspace requires manual steps: cloning with git, placing into the correct `repositories/{org}/{repo}/` directory, editing config.json to register in `childRepos`, and optionally running `specweave init`.
**Status**: planned | **Priority**: P1
**User Stories**: 5

![specweave add CLI command illustration](assets/feature-fs-519.jpg)

## Overview

Adding repositories to a SpecWeave umbrella workspace requires manual steps: cloning with git, placing into the correct `repositories/{org}/{repo}/` directory, editing config.json to register in `childRepos`, and optionally running `specweave init`. There is no single command that handles "give me this repo and make it part of my workspace." The existing `migrate-to-umbrella --add-repo` creates NEW GitHub repos, but there is no command for cloning and registering EXISTING repos.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0519-specweave-add-command](../../../../../increments/0519-specweave-add-command/spec.md) | ⏳ planned | 2026-03-13 |

## User Stories

- [US-001: Source Argument Parsing](./us-001-source-argument-parsing.md)
- [US-002: Clone Repository](./us-002-clone-repository.md)
- [US-003: Register in Umbrella Config](./us-003-register-in-umbrella-config.md)
- [US-004: Add Command Orchestration](./us-004-add-command-orchestration.md)
- [US-005: sw:add Skill Definition](./us-005-sw-add-skill-definition.md)
