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
complexity: medium
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 6
    url: "https://github.com/anton-abyzov/vskill-platform/milestone/6"
---

# Skill Eval Infrastructure

## TL;DR

**What**: Skills across vskill (42 plugin skills) and specweave (48 skills) lack a systematic evaluation framework.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 2

## Overview

Skills across vskill (42 plugin skills) and specweave (48 skills) lack a systematic evaluation framework. The only existing evals.json is a manually-authored file for the social-media-posting skill. There is no CLI tooling to scaffold, run, or report on evals. The platform has stub eval API routes but no web editor for browsing or editing eval definitions. Without eval infrastructure, there is no way to measure whether skills actually work, detect regressions, or enforce quality standards at scale.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0439-skill-eval-infrastructure](../../../../../increments/0439-skill-eval-infrastructure/spec.md) | ⏳ ready_for_review | 2026-03-05 |

## User Stories

- [US-WEB-001: Web Eval Viewer and Editor (P1)](./us-web-001-web-eval-viewer-and-editor-p1.md)
- [US-WEB-002: GitHub Commit from Web Editor (P1)](./us-web-002-github-commit-from-web-editor-p1.md)

## Related Projects

This feature spans multiple projects:

- [vskill](../../vskill/FS-439/)
- [specweave](../../specweave/FS-439/)
