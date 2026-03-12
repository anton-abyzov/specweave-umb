---
id: US-001
feature: FS-503
title: "Mark submission as vendor before publishing (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** vendor organization (e.g., anthropics, openai)."
project: vskill-platform
---

# US-001: Mark submission as vendor before publishing (P1)

**Feature**: [FS-503](./FEATURE.md)

**As a** vendor organization (e.g., anthropics, openai)
**I want** my submitted skills to have `isVendor=true` set on the submission record before `publishSkill()` runs
**So that** the publish pipeline correctly assigns CERTIFIED tier, vendor labels, and T4 trust score

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a submission from a vendor org repo (e.g., `github.com/anthropics/my-skill`), when `processSubmission` detects vendor status via `isVendorRepo()`, then the submission's `isVendor` field is set to `true` in both KV and DB before `publishSkill()` is called
- [ ] **AC-US1-02**: Given a `markVendor(id, org)` function in `submission-store.ts`, when called with a valid submission ID and org name, then it updates the KV entry's `isVendor` to `true` and persists the same to the DB submission record
- [ ] **AC-US1-03**: Given a submission from a non-vendor org (e.g., `github.com/random-user/skill`), when `processSubmission` runs, then `markVendor` is NOT called and `isVendor` remains `false`

---

## Implementation

**Increment**: [0503-vendor-auto-certification-fix](../../../../../increments/0503-vendor-auto-certification-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Add markVendor() to submission-store.ts
- [ ] **T-002**: Call markVendor in processSubmission vendor fast-path
