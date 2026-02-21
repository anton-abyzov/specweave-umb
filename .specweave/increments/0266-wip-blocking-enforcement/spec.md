# 0266 — WIP Blocking Enforcement

## Overview

Add a two-tier confirmation gate to `/sw:increment` that blocks when work-in-progress
increments exist. Users must explicitly acknowledge and bypass the gate before a new
increment can be created. At the configured hard cap, the warning escalates but the
user can still proceed with any confirmation.

## User Stories

### US-001: WIP Gate on Increment Creation

As a developer, I want to be warned when I have in-flight increments before creating
a new one, so that I don't lose focus by accumulating too many parallel streams.

**Acceptance Criteria:**

- [x] AC-US1-01: When WIP count is 0, `/sw:increment` proceeds without interruption
- [x] AC-US1-02: When WIP count >= 1 (non-emergency type), show list of in-flight increments and stop
- [x] AC-US1-03: User can bypass the soft gate by replying with any text
- [x] AC-US1-04: Hotfix/bug types show a brief notice but do not block
- [x] AC-US1-05: When WIP count >= hardCap, show escalated warning with stronger language
- [x] AC-US1-06: Even at hardCap, user can proceed by replying with any text
- [x] AC-US1-07: Gate lists each WIP increment with its status and ID
- [x] AC-US1-08: Gate suggests `/sw:done <id>` and `/sw:pause <id>` as alternatives

## WIP Definition

In-flight (WIP) = any increment with status in: `planning`, `active`, `ready_for_review`

## Configuration

Uses existing `config.json` limits:
```json
"limits": {
  "maxActiveIncrements": 3,
  "hardCap": 7,
  "allowEmergencyInterrupt": true
}
```

`hardCap` determines when the escalated warning triggers. No values change.
