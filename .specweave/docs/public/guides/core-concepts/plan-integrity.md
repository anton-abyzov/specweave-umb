# Plan Integrity: The Plan-First Change Protocol

**The plan is the source of truth. Code is a derivative. When anything changes, update the plan first.**

This is SpecWeave's most important operational rule. Every other workflow depends on it.

## The Problem

When AI agents or developers implement features, they regularly discover things that weren't anticipated during planning:

- A better architectural approach
- A missing requirement
- A flaw in the original design
- A user requesting new behavior mid-implementation

The natural instinct is to "just fix it in code" and move on. This creates **spec-implementation discrepancy** — the plan says one thing, the code does another. Over time, the specs become untrustworthy, documentation drifts, and the entire specification-driven workflow breaks down.

## The Rule

```
Plan → Code (always)
Code → Plan (never)
```

**Whenever something needs to change during implementation, follow this protocol:**

1. **STOP implementation** — do not push through with a stale plan
2. **Update the plan** — edit spec.md, plan.md, and/or tasks.md
3. **Review consistency** — ensure changes are coherent across all three files
4. **Resume implementation** — work from the corrected plan

This is non-negotiable regardless of the source of the change.

## When Does This Apply?

| Trigger | Example | What to Update |
|---------|---------|----------------|
| **AI discovers better approach** | WebSocket needs different auth strategy | plan.md (architecture), possibly tasks.md |
| **User requests new feature** | "Add rate limiting to the API" | spec.md (new AC), plan.md (design), tasks.md (new tasks) |
| **User changes requirements** | "Actually, make it async instead of sync" | spec.md (updated AC), plan.md (revised approach), tasks.md |
| **Test reveals spec gap** | E2E test exposes missing validation | tasks.md (add validation task), possibly spec.md (add AC) |
| **External dependency changes** | Library API changed since planning | plan.md (updated integration approach) |
| **Bug reveals design flaw** | Race condition in planned approach | plan.md (revised design), tasks.md (updated implementation) |

## Why This Matters

### Plans are cheap, code is expensive

Changing a few lines in spec.md takes seconds. Refactoring, re-testing, and debugging code takes hours. By keeping the plan current, you catch problems at the cheapest possible point.

### Specifications must be trustworthy

If specs don't match code, they become "documentation that everyone ignores." SpecWeave's entire value proposition — traceability, living docs, compliance audit trails — depends on specs accurately reflecting what was built and why.

### AI agents are most efficient with accurate plans

AI coding agents (Claude Code, Cursor, Copilot) generate better code when working from a clear, accurate plan. A stale plan causes the agent to produce code that needs to be reworked, wasting tokens and time.

### Flaw amplification

A small flaw in the plan amplifies into a disproportionate amount of bad code. Fixing the plan early prevents a cascade of rework:

```
Small plan flaw → Many lines of wrong code → Expensive rework
Small plan fix  → Correct code from the start → No rework
```

## Common Anti-Patterns

### "I'll update the spec later"

**Problem**: You never do. Or you do, but incompletely. The spec and code slowly diverge.

**Fix**: Update the spec *before* writing the code. It takes 30 seconds and prevents hours of drift.

### "It's just a small change, no need to update the plan"

**Problem**: Small changes accumulate. After 10 "small" untracked changes, the spec is fiction.

**Fix**: If it's small enough to not need a plan update, it's small enough to do the plan update quickly.

### "The user asked for it, so I'll just add it"

**Problem**: User requests are still changes. Adding them directly to code without updating the spec means the spec no longer describes the system.

**Fix**: Treat user requests as plan changes first, code changes second. The route is: user request → update spec/plan/tasks → implement from updated plan.

### "I'm in the flow, I don't want to stop"

**Problem**: Momentum feels productive, but implementing from a stale plan produces code that needs rework.

**Fix**: The 2-minute plan update saves the 2-hour rework. Always stop.

## Practical Examples

### Example 1: AI Discovers Better Approach

```
During T-003 (TypingIndicatorManager), you realize Redis pub/sub
would be more efficient than the planned WebSocket broadcast.

1. Stop implementing T-003
2. Update plan.md: Replace "WebSocket broadcast" with "Redis pub/sub"
3. Update tasks.md: Add Redis setup task, update T-003 description
4. Resume /sw:do from updated T-003
```

### Example 2: User Requests New Feature

```
User: "Add message read receipts to the chat"
(Not in original spec — only typing indicators were planned)

1. Stop current task
2. Update spec.md: Add US-004 (Read Receipts) with AC-IDs
3. Update plan.md: Add ReadReceiptManager component
4. Update tasks.md: Add T-009, T-010 for read receipt implementation
5. Resume /sw:do
```

### Example 3: Test Reveals Spec Gap

```
E2E test shows chat doesn't handle WebSocket disconnection gracefully.
The spec never mentioned reconnection behavior.

1. Stop current task
2. Update spec.md: Add AC-US1-04 (graceful reconnection)
3. Update tasks.md: Add reconnection handling task
4. Resume /sw:do
```

## For AI Agents (Claude Code, Cursor, etc.)

This rule is enforced in both [CLAUDE.md](/CLAUDE.md) and [AGENTS.md](/AGENTS.md):

- **Claude Code**: Plan Integrity is Section 5 of Workflow Orchestration. The agent must stop, update plan files, then resume implementation.
- **Non-Claude tools**: Follow the same protocol manually. After updating spec/plan/tasks, run `/sw:progress-sync` to keep external trackers in sync.

## Summary

- **One rule**: Plan first, code second. Always.
- **One protocol**: Stop → update plan → review consistency → resume
- **One reason**: Specs must be trustworthy. If they drift from code, the entire system fails.
- **No exceptions**: Whether the change is AI-discovered, user-requested, or test-revealed.

---

**Related:**
- [Philosophy: Plan as Source of Truth](/docs/overview/philosophy#1-plan-as-source-of-truth)
- [Implementation Workflow](/docs/workflows/implementation#plan-is-the-source-of-truth)
- [Planning Workflow](/docs/workflows/planning)
- [What is an Increment?](/docs/guides/core-concepts/what-is-an-increment)
