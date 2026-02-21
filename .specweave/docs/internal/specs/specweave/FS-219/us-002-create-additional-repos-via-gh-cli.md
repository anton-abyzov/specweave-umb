---
id: US-002
feature: FS-219
title: Create Additional Repos via gh CLI
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1195
    url: https://github.com/anton-abyzov/specweave/issues/1195
---
# US-002: Create Additional Repos via gh CLI

**Feature**: [FS-219](./FEATURE.md)

developer setting up a multi-repo workspace
**I want** the migration tool to help me create additional repositories
**So that** I can start a microservices architecture from the umbrella

---

## Acceptance Criteria

- [x] **AC-US2-01**: After migration, the command prompts the user to define additional repositories (name, description, visibility)
- [x] **AC-US2-02**: If `gh` CLI is available and authenticated, repos are created on GitHub via `gh repo create`
- [x] **AC-US2-03**: If `gh` CLI is not available or not authenticated, provides clear setup instructions and falls back to creating local directories only
- [x] **AC-US2-04**: New repos are cloned/created into the umbrella's `repositories/{org}/{repo-name}/`
- [x] **AC-US2-05**: Each new repo is registered in `umbrella.childRepos[]` with prompted prefix and auto-detected metadata

---

## Implementation

**Increment**: [0219-multi-repo-migrate](../../../../../increments/0219-multi-repo-migrate/spec.md)

