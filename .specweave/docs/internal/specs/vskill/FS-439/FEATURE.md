---
id: FS-439
title: Skill Eval Infrastructure
type: feature
status: ready_for_review
priority: P1
created: 2026-03-05
lastUpdated: 2026-03-07
tldr: Skills across vskill (42 plugin skills) and specweave (48 skills) lack a
  systematic evaluation framework.
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 6
    url: https://github.com/anton-abyzov/vskill/milestone/6
---

# Skill Eval Infrastructure

## TL;DR

**What**: Skills across vskill (42 plugin skills) and specweave (48 skills) lack a systematic evaluation framework.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 5

![Skill Eval Infrastructure illustration](assets/feature-fs-439.jpg)

## Overview

Skills across vskill (42 plugin skills) and specweave (48 skills) lack a systematic evaluation framework. The only existing evals.json is a manually-authored file for the social-media-posting skill. There is no CLI tooling to scaffold, run, or report on evals. The platform has stub eval API routes but no web editor for browsing or editing eval definitions. Without eval infrastructure, there is no way to measure whether skills actually work, detect regressions, or enforce quality standards at scale.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0439-skill-eval-infrastructure](../../../../../increments/0439-skill-eval-infrastructure/spec.md) | ⏳ ready_for_review | 2026-03-05 |

## User Stories

- [US-CLI-001: Scaffold Evals for a Skill (P0)](./us-cli-001-scaffold-evals-for-a-skill-p0.md)
- [US-CLI-002: Run Evals Locally (P0)](./us-cli-002-run-evals-locally-p0.md)
- [US-CLI-003: Eval Coverage Report (P1)](./us-cli-003-eval-coverage-report-p1.md)
- [US-CLI-004: Batch Generate Evals (P1)](./us-cli-004-batch-generate-evals-p1.md)
- [US-CLI-005: Validate Evals Schema on Load (P1)](./us-cli-005-validate-evals-schema-on-load-p1.md)

## Related Projects

This feature spans multiple projects:

- [vskill-platform](../../vskill-platform/FS-439/)
- [specweave](../../specweave/FS-439/)
