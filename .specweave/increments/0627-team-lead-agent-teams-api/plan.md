---
increment: 0627-team-lead-agent-teams-api
---

# Architecture Plan

## Overview

All changes are documentation/prompt edits to SKILL.md and 5 agent template files in `/Users/antonabyzov/.claude/plugins/cache/specweave/sw/1.0.0/skills/team-lead/`. No TypeScript code changes. The existing custom protocols (STATUS heartbeat, sw-closer, bypassPermissions) are preserved — new native features are layered on top, not replacements.

## Files to Modify

| File | Lines Added | Section |
|------|------------|---------|
| `SKILL.md` | ~80 | Sections 0.7, 3, 6, 6b, 8b, 8c, 9 |
| `agents/backend.md` | ~8 | After COMPLETION block |
| `agents/frontend.md` | ~8 | After COMPLETION block |
| `agents/database.md` | ~8 | After COMPLETION block |
| `agents/testing.md` | ~8 | After COMPLETION block |
| `agents/security.md` | ~8 | After COMPLETION block |

## Architecture Decisions

### ADR-1: Keep compensating controls as fallbacks
The STATUS heartbeat, Phase 3 bash script, and bypassPermissions are battle-tested. New native features are additive — the old controls remain as fallbacks in case native features have bugs.

### ADR-2: QUERY_READY is opt-in via agent templates
Agents enter idle state by sending QUERY_READY. Only implementation agents (backend, frontend, database, testing, security) get idle querying. Planning agents (pm, architect), brainstorm agents, and researchers don't — their lifecycle is different.

### ADR-3: TeammateIdle hook is documented but not auto-configured
The skill documents the hook and its circuit breaker requirement but doesn't auto-write settings.json. Users opt-in by adding the hook configuration themselves.

### ADR-4: broadcast scoped to shutdown + global announcements only
Point-to-point remains the default for corrections and task-specific messages. Broadcast is explicitly limited to avoid thundering-herd responses and token cost amplification.

## Implementation Phases

### Phase 1: Communication Protocol (US-001, US-003)
- Add QUERY_READY, QUERY, SHUTDOWN_AUTHORIZED to Section 6
- Add broadcast to Section 6
- Add Section 6b direct user interaction

### Phase 2: Workflow Updates (US-001, US-002)
- Add Section 0.7 display mode configuration
- Update Section 8b stuck detection exclusion
- Update Section 9 workflow with idle query phase
- Update Section 9 Phase 1 and Phase 3 cleanup
- Add Section 8c TeammateIdle hook

### Phase 3: Agent Templates (US-001)
- Add QUERY_READY idle phase to all 5 templates

## Technical Challenges

### Challenge 1: Context saturation during idle queries
Agents at 15-task cap may not process follow-up queries well.
**Solution**: Task-count guard — only query agents with <12 tasks completed.

### Challenge 2: TeammateIdle hook infinite loops
Hook returning exit code 2 indefinitely.
**Solution**: Document mandatory circuit breaker (max 3 re-engagements per agent).
