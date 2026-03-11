---
id: US-001
feature: FS-486
title: LLM Returns Eval Change Suggestions
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 72
    url: https://github.com/anton-abyzov/vskill/issues/72
---

# US-001: LLM Returns Eval Change Suggestions

**Feature**: [FS-486](./FEATURE.md)

**As a** skill author
**I want** the AI Edit LLM call to analyze my current evals and suggest test case changes alongside SKILL.md edits
**So that** I get a complete picture of what needs updating in one pass

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill with existing evals, when the user submits an AI Edit instruction, then the improve endpoint sends current evals to the LLM and returns an `evalChanges` array alongside `improved` and `reasoning`
- [x] **AC-US1-02**: Given a skill with no evals.json, when the user submits an AI Edit instruction, then the LLM receives an empty evals array and may suggest new test cases from scratch
- [x] **AC-US1-03**: Each eval change object contains `action` (add | modify | remove), `reason` string, and the full eval case data (for add/modify) or the target eval id (for remove)
- [x] **AC-US1-04**: Given the LLM response does not contain a valid `---EVAL_CHANGES---` section, then the endpoint returns the SKILL.md result normally with an empty `evalChanges` array (graceful degradation)

---

## Implementation

**Increment**: [0486-smart-ai-edit](../../../../../increments/0486-smart-ai-edit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Extend Backend Types and API Shape for Eval Changes
- [x] **T-002**: Extend improve-routes.ts -- Prompt Construction, Response Parsing, Graceful Degradation
