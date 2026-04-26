---
increment: 0737-studio-skill-source-github-link
title: "Studio skill detail — clickable GitHub source link"
generated: "2026-04-26T02:35:00Z"
source: grill-filled
version: "1.0"
status: complete
---

# Quality Rubric: 0737 — Studio skill detail clickable GitHub source link

## Criteria

### C-001: All ACs satisfied with code evidence
- **Evaluator**: sw:grill
- **Requirement**: Every AC in spec.md (US1-01..04) maps to concrete code + test
- **Result**: [x] PASS — 10/10 ACs verified; see grill-report.json acCompliance.results

### C-002: New code paths have unit tests
- **Evaluator**: sw:grill
- **Requirement**: buildSkillMetadata, lockfile write helpers, DetailHeader byline rendering all covered
- **Result**: [x] PASS — 15 new test cases across 3 files, all passing

### C-003: Backward compatibility preserved
- **Evaluator**: sw:grill
- **Requirement**: Existing lockfiles without sourceRepoUrl/sourceSkillPath continue to load and render
- **Result**: [x] PASS — defensive `?? null` reads, copy-chip fallback path covered by tests

### C-004: Spec scope honored
- **Evaluator**: sw:grill
- **Requirement**: No silent expansions beyond stated FRs/ACs
- **Result**: [!] PARTIAL — same commit also bundles ~120 lines of 0736 work (postSkillUpdate streaming, resolveInstalledSkillIds). Does not contradict any AC; documented as INFO finding in code-review.

### C-005: No production regressions introduced
- **Evaluator**: sw:grill
- **Requirement**: Released vskill@0.5.115 must not break existing skill detail rendering
- **Result**: [!] FAIL — at ship time, nested-layout marketplace plugins received broken /blob/HEAD/SKILL.md anchors when only sourceRepoUrl was written (no sourceSkillPath). Surfaced in production, fixed in subsequent closed increment 0743 (already shipped as vskill@0.5.124).

## Summary

10/10 ACs pass at the time of closure. One LOW correctness regression (C-005) escaped to production, was diagnosed within hours, and remediated in increment 0743 with new tests preventing recurrence. Net: closure gate clear; downstream fix already shipped.
