---
id: US-002
feature: FS-318
title: Create sw:sync-docs skill
status: complete
priority: P1
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1255
    url: https://github.com/anton-abyzov/specweave/issues/1255
---
# US-002: Create sw:sync-docs skill

**Feature**: [FS-318](./FEATURE.md)

SpecWeave user
**I want** a `/sw:sync-docs` skill that syncs living docs for an increment
**So that** Step 10 of `/sw:done` can invoke it and I can also run it manually

---

## Acceptance Criteria

- [x] **AC-US2-01**: A new skill at `plugins/specweave/skills/sync-docs/SKILL.md` exists with proper frontmatter (description, argument-hint)
- [x] **AC-US2-02**: The skill invokes `LivingDocsSync.syncIncrement()` for the given increment ID
- [x] **AC-US2-03**: The skill accepts an optional "review" mode argument that validates sync completeness without modifying files
- [x] **AC-US2-04**: The skill handles errors gracefully and reports sync results (files created/updated count)

---

## Implementation

**Increment**: [0318-post-closure-sync-pipeline](../../../../../increments/0318-post-closure-sync-pipeline/spec.md)

