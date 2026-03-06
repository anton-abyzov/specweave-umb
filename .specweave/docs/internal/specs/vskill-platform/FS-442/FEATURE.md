---
id: FS-442
title: "Rework Skill Evaluation System"
type: feature
status: completed
priority: P1
created: 2026-03-06T00:00:00.000Z
lastUpdated: 2026-03-06
tldr: "The current vskill-platform eval system uses blind A/B comparison (with-skill vs without-skill) judged by a single LLM call that returns a holistic 0-100 score and a verdict."
complexity: high
stakeholder_relevant: true
---

# Rework Skill Evaluation System

## TL;DR

**What**: The current vskill-platform eval system uses blind A/B comparison (with-skill vs without-skill) judged by a single LLM call that returns a holistic 0-100 score and a verdict.
**Status**: completed | **Priority**: P1
**User Stories**: 7

![Rework Skill Evaluation System illustration](assets/feature-fs-442.jpg)

## Overview

The current vskill-platform eval system uses blind A/B comparison (with-skill vs without-skill) judged by a single LLM call that returns a holistic 0-100 score and a verdict. This approach has three critical weaknesses:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md) | ✅ completed | 2026-03-06T00:00:00.000Z |

## User Stories

- [US-001: Assertion-Based Grading (P1)](./us-001-assertion-based-grading-p1.md)
- [US-002: Rubric Scoring (P1)](./us-002-rubric-scoring-p1.md)
- [US-003: V2 Verdict Logic (P1)](./us-003-v2-verdict-logic-p1.md)
- [US-004: Multi-Run Variance Analysis (P2)](./us-004-multi-run-variance-analysis-p2.md)
- [US-005: Enhanced Prompt and Assertion Generation (P2)](./us-005-enhanced-prompt-and-assertion-generation-p2.md)
- [US-006: Re-Verification Queue (P2)](./us-006-re-verification-queue-p2.md)
- [US-007: Backward-Compatible Schema Extension (P1)](./us-007-backward-compatible-schema-extension-p1.md)
