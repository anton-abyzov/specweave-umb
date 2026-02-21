---
id: US-005
feature: FS-283
title: Blocklist Auto-Propagation from Security Reports
status: active
priority: P1
created: 2026-02-21
project: vskill-platform
---
# US-005: Blocklist Auto-Propagation from Security Reports

**Feature**: [FS-283](./FEATURE.md)

platform admin
**I want** confirmed malware security reports to automatically create blocklist entries
**So that** I do not need to manually duplicate data between the reports and blocklist systems

---

## Acceptance Criteria

- [x] **AC-US5-01**: When a SecurityReport is resolved with `resolutionNote` containing "confirmed_malware" or "confirmed malware", a BlocklistEntry is automatically created for the reported `skillName`
- [x] **AC-US5-02**: The auto-created BlocklistEntry includes: `threatType` from the report's `reportType`, `severity` set to "critical", `reason` from the report's `description`, `evidenceUrls` from the report's `evidenceUrls`
- [x] **AC-US5-03**: If a BlocklistEntry already exists for the skill name, it is not duplicated (idempotent)
- [ ] **AC-US5-04**: The admin UI shows a confirmation when auto-propagation occurs

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

