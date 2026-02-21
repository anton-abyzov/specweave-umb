---
id: US-001
feature: FS-294
title: Shared agent branding constants
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1231
    url: "https://github.com/anton-abyzov/specweave/issues/1231"
---
# US-001: Shared agent branding constants

**Feature**: [FS-294](./FEATURE.md)

developer
**I want** AGENT_COLORS and AGENT_ICONS to live in a single shared lib file
**So that** both the homepage and skill detail page can import them without duplication

---

## Acceptance Criteria

- [x] **AC-US1-01**: A new shared file `src/lib/agent-branding.ts` exports `AGENT_COLORS` and `AGENT_ICONS` with the same data currently in `src/app/page.tsx`
- [x] **AC-US1-02**: `src/app/page.tsx` imports `AGENT_COLORS` and `AGENT_ICONS` from the shared file instead of defining them inline
- [x] **AC-US1-03**: No duplicate definitions of `AGENT_COLORS` or `AGENT_ICONS` exist in the codebase

---

## Implementation

**Increment**: [0294-skill-page-agent-pills](../../../../../increments/0294-skill-page-agent-pills/spec.md)

