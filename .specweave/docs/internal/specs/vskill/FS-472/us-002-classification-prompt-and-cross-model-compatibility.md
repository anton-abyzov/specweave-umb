---
id: US-002
feature: FS-472
title: "Classification Prompt and Cross-Model Compatibility"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill author using different LLM providers."
project: vskill
external:
  github:
    issue: 68
    url: "https://github.com/anton-abyzov/vskill/issues/68"
---

# US-002: Classification Prompt and Cross-Model Compatibility

**Feature**: [FS-472](./FEATURE.md)

**As a** skill author using different LLM providers
**I want** the classification prompt to work across Claude, Llama, Qwen, and other models
**So that** auto-classification is reliable regardless of the selected provider

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given a classification request, when the LLM is called, then the prompt uses only skill name and tags (NOT the full description) and requests minimal JSON output `{"related": true/false}`
- [ ] **AC-US2-02**: Given the classification LLM returns invalid JSON or errors, when processing the result, then the system defaults to `should_activate` (backward compatibility)
- [ ] **AC-US2-03**: Given a SKILL.md with no frontmatter name or tags, when the test runs, then classification is skipped entirely and unlabeled prompts default to `should_activate`

---

## Implementation

**Increment**: [0472-activation-auto-classify](../../../../../increments/0472-activation-auto-classify/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-003**: Harden classifyExpectation prompt and fallback behavior
