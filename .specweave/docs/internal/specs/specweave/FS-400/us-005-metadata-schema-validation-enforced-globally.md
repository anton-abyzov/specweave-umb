---
id: US-005
feature: FS-400
title: "Metadata schema validation enforced globally"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer."
---

# US-005: Metadata schema validation enforced globally

**Feature**: [FS-400](./FEATURE.md)

**As a** developer
**I want** increment metadata schema enforced at both creation and load time
**So that** malformed metadata never gets written and is caught immediately if introduced manually

---

## Acceptance Criteria

- [x] **AC-US5-01**: `MetadataManager.create()` enforces required fields: `id` (must be full slug), `status`, `type` (from standard vocab), `created` (not `createdAt`), `externalLinks` (initialized to `{}`)
- [x] **AC-US5-02**: `MetadataManager.load()` validates and auto-corrects: missing `externalLinks` → adds `{}`, `createdAt` → renamed to `created`, short `id` → expanded to full slug
- [x] **AC-US5-03**: Non-standard `type` values (e.g., "enhancement") are mapped to the closest standard value (e.g., "feature") with a warning
- [x] **AC-US5-04**: A shared `validateMetadataSchema()` function is used by both create and load paths — single source of truth for the schema contract

---

## Implementation

**Increment**: [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
