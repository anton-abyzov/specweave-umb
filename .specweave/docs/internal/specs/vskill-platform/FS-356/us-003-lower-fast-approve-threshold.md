---
id: US-003
feature: FS-356
title: Lower Fast-Approve Threshold
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
---
# US-003: Lower Fast-Approve Threshold

**Feature**: [FS-356](./FEATURE.md)

platform operator
**I want** the fast-approve threshold lowered from 85 to 75
**So that** more code-skills with clean Tier 1 scans skip the expensive Tier 2 LLM analysis, reducing processing time and AI API costs

---

## Acceptance Criteria

- [x] **AC-US3-01**: `FAST_APPROVE_THRESHOLD` constant in `process-submission.ts` is changed from 85 to 75
- [x] **AC-US3-02**: The fast-approve short-circuit logic (`hasCodeFiles && tier1WeightedScore > FAST_APPROVE_THRESHOLD`) remains unchanged -- only the threshold value changes
- [x] **AC-US3-03**: Pure prompt-only skills are still never fast-approved (the `hasCodeFiles` guard remains)

---

## Implementation

**Increment**: [0356-scale-queue-throughput](../../../../../increments/0356-scale-queue-throughput/spec.md)

