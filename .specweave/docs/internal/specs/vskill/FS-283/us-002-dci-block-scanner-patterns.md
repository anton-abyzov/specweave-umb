---
id: US-002
feature: FS-283
title: DCI Block Scanner Patterns
status: complete
priority: P1
created: 2026-02-21
project: vskill
---
# US-002: DCI Block Scanner Patterns

**Feature**: [FS-283](./FEATURE.md)

security scanner maintainer
**I want** the tier1 scanner to detect malicious patterns specifically within DCI shell blocks
**So that** DCI-based attacks (credential exfiltration, config poisoning, download-and-execute) are caught before publication

---

## Acceptance Criteria

- [x] **AC-US2-01**: The scanner identifies DCI blocks in SKILL.md content (pattern: backtick command preceded by `!` within a markdown section titled "Project Overrides" or "Project Context")
- [x] **AC-US2-02**: DCI blocks containing credential file reads (`~/.ssh/`, `~/.aws/`, `.env`) are flagged as critical severity
- [x] **AC-US2-03**: DCI blocks containing network calls (`curl`, `wget`, `fetch`, `nc`) are flagged as critical severity
- [x] **AC-US2-04**: DCI blocks containing writes to agent config files (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.specweave/`) are flagged as critical severity
- [x] **AC-US2-05**: DCI blocks containing obfuscation (base64 decode, hex escapes, eval) are flagged as critical severity
- [x] **AC-US2-06**: DCI blocks containing download-and-execute patterns (curl|sh, wget|sh) are flagged as critical severity
- [x] **AC-US2-07**: At least 12 new DCI-specific patterns are added to the scanner with tests for each
- [x] **AC-US2-08**: Legitimate DCI blocks (standard skill-memories lookup pattern) are not flagged (false positive suppression via safe-context patterns)

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

