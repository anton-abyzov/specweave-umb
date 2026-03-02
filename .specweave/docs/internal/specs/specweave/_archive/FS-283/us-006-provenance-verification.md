---
id: US-006
feature: FS-283
title: Provenance Verification
status: complete
priority: P2
created: 2026-02-21
project: vskill-platform
---
# US-006: Provenance Verification

**Feature**: [FS-283](./FEATURE.md)

platform maintainer
**I want** to verify that a skill submitter is the owner or collaborator of the submitted repository
**So that** impostor submissions (claiming ownership of another user's repo) are detected and flagged

---

## Acceptance Criteria

- [x] **AC-US6-01**: During submission processing, the platform verifies that the submitter's GitHub username matches the repository owner or is listed as a collaborator via the GitHub API
- [x] **AC-US6-02**: If provenance verification fails, the submission is flagged with a "provenance_mismatch" warning (not auto-rejected, but requiring manual review)
- [x] **AC-US6-03**: If provenance verification succeeds, a `provenanceVerified: true` flag is stored on the Submission record
- [x] **AC-US6-04**: The trust score computation gives 20% weight to provenance verification (verified = full points, unverified = 0, mismatch = negative modifier)

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

