---
id: FS-409
title: "FS-409G: Research: Sub-agents for skill execution"
type: feature
status: completed
priority: P1
created: 2026-03-10
lastUpdated: 2026-03-10
tldr: "Currently, SpecWeave skills like `/sw:increment`, `/sw:tdd-cycle`, and `/sw:do` execute inline within the main Claude Code conversation context."
complexity: low
stakeholder_relevant: true
---

# FS-409G: Research: Sub-agents for skill execution

## TL;DR

**What**: Currently, SpecWeave skills like `/sw:increment`, `/sw:tdd-cycle`, and `/sw:do` execute inline within the main Claude Code conversation context.
**Status**: completed | **Priority**: P1
**User Stories**: 1

![FS-409G: Research: Sub-agents for skill execution illustration](assets/feature-fs-409.jpg)

## Overview

Currently, SpecWeave skills like `/sw:increment`, `/sw:tdd-cycle`, and `/sw:do` execute inline within the main Claude Code conversation context. This can lead to context window pressure, no parallelism, and main conversation blocking. Research whether Claude Code sub-agents could be used to execute skills in isolated contexts.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0409G-sub-agent-skill-research](../../../../../increments/0409G-sub-agent-skill-research/spec.md) | ✅ completed | 2026-03-10 |

## User Stories

- [US-001: Evaluate Sub-Agent Skill Execution](./us-001-evaluate-sub-agent-skill-execution.md)
