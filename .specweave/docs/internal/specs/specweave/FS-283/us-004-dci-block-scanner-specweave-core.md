---
id: US-004
feature: FS-283
title: DCI Block Scanner -- SpecWeave Core
status: complete
priority: P1
created: 2026-02-21
project: specweave
---
# US-004: DCI Block Scanner -- SpecWeave Core

**Feature**: [FS-283](./FEATURE.md)

skill author using the specweave security self-scan
**I want** the `scanSkillContent` function to detect DCI abuse patterns
**So that** I catch DCI security issues before submitting to the platform

---

## Acceptance Criteria

- [x] **AC-US4-01**: `security-scanner.ts` includes DCI-specific pattern checks (matching the patterns from US-002)
- [x] **AC-US4-02**: The `specweave scan-skill` CLI command reports DCI-abuse findings
- [x] **AC-US4-03**: DCI findings inside balanced code blocks are NOT downgraded to info (they remain at their original severity because DCI blocks execute even inside code fences)

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

