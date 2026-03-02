---
id: US-002
feature: FS-306
title: Write Published Skills to Prisma Skill Table
status: complete
priority: P0
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1246
    url: "https://github.com/anton-abyzov/specweave/issues/1246"
---
# US-002: Write Published Skills to Prisma Skill Table

**Feature**: [FS-306](./FEATURE.md)

platform operator
**I want** every published skill to be persisted in the Prisma `Skill` table
**So that** I have a durable, queryable source of truth that survives KV corruption

---

## Acceptance Criteria

- [x] **AC-US2-01**: `publishSkill()` in `submission-store.ts` upserts a record into `Skill` table (via Prisma) in addition to writing to KV; uses `repoUrl` + `name` for dedup
- [x] **AC-US2-02**: Prisma `Skill` fields populated from submission + scan data: name (slug), displayName (skillName), description, author (extracted from repoUrl), repoUrl, category (default "development"), currentVersion ("1.0.0"), certTier (SCANNED), certMethod (AUTOMATED_SCAN), certScore, certifiedAt, labels (["community","verified"])
- [x] **AC-US2-03**: If Prisma write fails (e.g., DB unreachable), the KV-only path still succeeds (graceful degradation)
- [x] **AC-US2-04**: Extensibility metadata (extensible, extensionPoints) stored as JSON in Skill labels or a new column if needed
- [x] **AC-US2-05**: Unit tests cover: successful dual write, Prisma failure with KV success, duplicate skill upsert updates instead of errors

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)

