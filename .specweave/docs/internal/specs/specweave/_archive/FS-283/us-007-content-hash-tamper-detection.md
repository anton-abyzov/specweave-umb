---
id: US-007
feature: FS-283
title: Content Hash Tamper Detection
status: active
priority: P2
created: 2026-02-21
project: vskill-platform
---
# US-007: Content Hash Tamper Detection

**Feature**: [FS-283](./FEATURE.md)

platform maintainer
**I want** to detect when a skill's content changes after it was scanned
**So that** post-scan tampering is caught before the tampered content reaches users

---

## Acceptance Criteria

- [x] **AC-US7-01**: The scan pipeline records the SHA-256 hash of the SKILL.md content at scan time in the ScanResult record
- [x] **AC-US7-02**: Before publishing a skill version, the content hash is re-verified against the scanned content hash
- [x] **AC-US7-03**: If hashes do not match, the submission is moved to a "RESCAN_REQUIRED" state and the previous scan results are invalidated
- [ ] **AC-US7-04**: The admin UI shows a tamper warning when content hash mismatch is detected

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

