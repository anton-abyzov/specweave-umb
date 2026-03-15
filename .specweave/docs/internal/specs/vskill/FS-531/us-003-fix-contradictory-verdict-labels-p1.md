---
id: US-003
feature: FS-531
title: "Fix Contradictory Verdict Labels (P1)"
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** skill developer reviewing benchmark verdicts."
project: vskill
---

# US-003: Fix Contradictory Verdict Labels (P1)

**Feature**: [FS-531](./FEATURE.md)

**As a** skill developer reviewing benchmark verdicts
**I want** the verdict tier to correctly distinguish between "skill outperforms a weak baseline" and "skill is actually degrading"
**So that** I am not confused by a positive delta paired with a DEGRADING label

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given baseline=0% and skill=33% (passRate < 0.4 AND skillAvg > baselineAvg), when the verdict is computed, then the tier is EMERGING
- [x] **AC-US3-02**: Given baseline=50% and skill=30% (passRate < 0.4 AND skillAvg <= baselineAvg), when the verdict is computed, then the tier is DEGRADING
- [x] **AC-US3-03**: Given passRate >= 0.4, when the verdict is computed, then the existing tier logic applies unchanged (INEFFECTIVE at >= 0.4, MARGINAL at >= 0.6, EFFECTIVE at >= 0.8 with skillAvg > baselineAvg + 1)
- [x] **AC-US3-04**: Given any verdict display, when the delta label renders, then it reads "Rubric Delta" instead of "Delta"

---

## Implementation

**Increment**: [0531-benchmark-comparison-ux](../../../../../increments/0531-benchmark-comparison-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
