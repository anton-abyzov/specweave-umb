---
id: US-001
feature: FS-296
title: Consistent Slug Computation on Submit Page
status: complete
priority: P1
created: 2026-02-21
project: vskill-platform
---
# US-001: Consistent Slug Computation on Submit Page

**Feature**: [FS-296](./FEATURE.md)

skill author who just published a skill
**I want** the "View published skill" link on the submission status page to point to the correct URL
**So that** I can verify my published skill page without manually guessing the URL

---

## Acceptance Criteria

- [x] **AC-US1-01**: The submit status page (`/submit/[id]`) imports and calls `makeSlug()` from `submission-store.ts` instead of using inline regex to compute the skill slug
- [x] **AC-US1-02**: The `ExternalScanStatus` component uses the same `makeSlug()` call for the security API URL and the security report link
- [x] **AC-US1-03**: Unit test confirms the slug on the submit page matches the slug stored in KV after `publishSkill()` runs

---

## Implementation

**Increment**: [0296-strip-prefix-rollout-fixes](../../../../../increments/0296-strip-prefix-rollout-fixes/spec.md)

