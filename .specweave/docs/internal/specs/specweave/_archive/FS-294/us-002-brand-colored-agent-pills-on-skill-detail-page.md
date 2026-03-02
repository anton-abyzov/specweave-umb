---
id: US-002
feature: FS-294
title: Brand-colored agent pills on skill detail page
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1232
    url: "https://github.com/anton-abyzov/specweave/issues/1232"
---
# US-002: Brand-colored agent pills on skill detail page

**Feature**: [FS-294](./FEATURE.md)

user viewing a skill detail page
**I want** the "Works with" section to show brand-colored pill badges with icons
**So that** the agent compatibility section looks consistent with the homepage and is easier to scan

---

## Acceptance Criteria

- [x] **AC-US2-01**: Each agent in the "Works with" section renders as a rounded pill with the agent's brand color (from `AGENT_COLORS`) as a tinted background and border
- [x] **AC-US2-02**: Agents that have an entry in `AGENT_ICONS` show the brand icon (13x13px) to the left of the name
- [x] **AC-US2-03**: Agents without an icon entry but with a color entry show a small colored dot indicator
- [x] **AC-US2-04**: Agents without any branding data render a plain pill (no crash, graceful fallback)
- [x] **AC-US2-05**: The visual style matches the homepage featured agents section (rounded pills, mono font, icon + name)

---

## Implementation

**Increment**: [0294-skill-page-agent-pills](../../../../../increments/0294-skill-page-agent-pills/spec.md)

