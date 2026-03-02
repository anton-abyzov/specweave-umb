---
id: US-003
feature: FS-391
title: "Plan Skill Markdown Previews (P1)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** developer using `/sw:plan`
**I want** to see task dependency DAGs in side-by-side previews when choosing between execution strategies
**So that** I can visualize the critical path and parallelism before approving the plan."
project: specweave
---

# US-003: Plan Skill Markdown Previews (P1)

**Feature**: [FS-391](./FEATURE.md)

**As a** developer using `/sw:plan`
**I want** to see task dependency DAGs in side-by-side previews when choosing between execution strategies
**So that** I can visualize the critical path and parallelism before approving the plan

---

## Acceptance Criteria

- [x] **AC-US3-01**: `/sw:plan` SKILL.md includes instructions to use `AskUserQuestion` with `markdown` DAG previews for task ordering decisions
- [x] **AC-US3-02**: DAG previews show task IDs, names, dependencies, parallel lanes, and critical path annotation
- [x] **AC-US3-03**: SKILL.md includes at least 1 complete example of AskUserQuestion with DAG preview

---

## Implementation

**Increment**: [0391-askuserquestion-markdown-previews](../../../../../increments/0391-askuserquestion-markdown-previews/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
