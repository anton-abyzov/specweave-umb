---
project: specweave
---

# FS-409G: Research: Sub-agents for skill execution

## Overview
Currently, SpecWeave skills like `/sw:increment`, `/sw:tdd-cycle`, and `/sw:do` execute inline within the main Claude Code conversation context. This can lead to context window pressure, no parallelism, and main conversation blocking. Research whether Claude Code sub-agents could be used to execute skills in isolated contexts.

## User Stories

### US-001: Evaluate Sub-Agent Skill Execution
**As a** SpecWeave developer
**I want** to understand whether skills can run as sub-agents
**So that** we can improve context efficiency and enable parallel skill execution

#### Acceptance Criteria
- [x] AC-US1-01: Evaluate feasibility of sub-agent skill execution with Claude Code Agent tool
- [x] AC-US1-02: Document trade-offs (context isolation vs. shared state, token cost, latency)
- [x] AC-US1-03: Prototype at least one skill (e.g., `/sw:grill`) running as a sub-agent
