---
id: US-005
feature: FS-442
title: "Enhanced Prompt and Assertion Generation (P2)"
status: completed
priority: P1
created: 2026-03-06T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
external:
  github:
    issue: 26
    url: https://github.com/anton-abyzov/vskill-platform/issues/26
---

# US-005: Enhanced Prompt and Assertion Generation (P2)

**Feature**: [FS-442](./FEATURE.md)

**As a** platform operator
**I want** the eval pipeline to support structured assertions from `evals.json` format and auto-generate assertions when none exist
**So that** every skill can be evaluated with assertion-based grading regardless of author-provided test cases

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given a SKILL.md with an `## Evaluations` section containing evals.json-format data, when generating test cases, then the system parses and uses the structured assertions directly
- [x] **AC-US5-02**: Given a SKILL.md with a `## Test Cases` section containing `Prompt:` / `Expected:` pairs, when generating test cases, then the system converts each `Expected` value into assertions via an LLM call that produces `{ id, text, type: "boolean" }[]`
- [x] **AC-US5-03**: Given a SKILL.md with neither `## Evaluations` nor `## Test Cases`, when generating test cases, then the system fully auto-generates prompts AND assertions via LLM from the skill description and content
- [x] **AC-US5-04**: All generated assertions use `type: "boolean"` exclusively -- no regex or keyword matching types
- [x] **AC-US5-05**: Auto-generated assertions are NOT written back to the skill repository -- they exist only in the eval run data

---

## Implementation

**Increment**: [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Parse Evaluations section and convert Expected to assertions
- [x] **T-009**: Auto-generate prompts and assertions from skill description
