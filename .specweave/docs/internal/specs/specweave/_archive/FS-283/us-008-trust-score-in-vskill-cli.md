---
id: US-008
feature: FS-283
title: Trust Score in vskill CLI
status: complete
priority: P2
created: 2026-02-21
project: vskill
---
# US-008: Trust Score in vskill CLI

**Feature**: [FS-283](./FEATURE.md)

developer using the vskill CLI
**I want** to see the trust tier and score when installing or inspecting a skill
**So that** I can make an informed decision about whether to install it

---

## Acceptance Criteria

- [x] **AC-US8-01**: `vskill install <skill>` displays the trust tier (T0-T4) and trust score (0-100) before installation
- [x] **AC-US8-02**: T0 (blocked) skills show a red warning and require explicit `--force` flag to install
- [x] **AC-US8-03**: T1 (unscanned) skills show an amber warning about unverified status
- [x] **AC-US8-04**: `vskill info <skill>` includes trust tier, trust score, and provenance verification status in its output

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

