# 0253: Submission Deduplication and Repository Hierarchy

## Problem Statement

The verified-skill.com submission system has zero deduplication:
- Same skill from the same repo can be submitted unlimited times
- No check for existing pending/processing/verified submissions
- Skills are stored flat — `repoUrl` is just a string, no parent entity
- Discovery returns 123 skills for specweave repo, each submitted independently with no grouping
- Rate limit (10/IP/hour) means submitting a full marketplace takes 12+ hours

The database needs a proper hierarchy: **Repository -> Skills** (and optionally **Repository -> Plugin -> Skills** for marketplace repos).

## User Stories

### US-001: As a submitter, I want the system to check for existing submissions before creating duplicates
- **AC-US1-01**: [x] When submitting a skill that already has a PENDING/PROCESSING submission for the same (repoUrl, skillName), the system returns the existing submission instead of creating a new one
- **AC-US1-02**: [x] When submitting a skill that is already VERIFIED with the same (repoUrl, skillName), the system returns the existing skill with a "already verified" status
- **AC-US1-03**: [x] When submitting a skill that was previously REJECTED, the system allows re-submission (creates new submission)
- **AC-US1-04**: [x] The discover endpoint returns status for each skill (new/pending/verified/rejected) so the UI can show which skills need submission

### US-002: As a platform operator, I want skills grouped by repository in the database
- **AC-US2-01**: [x] A `Repository` model exists linking (owner, name) to skills and submissions
- **AC-US2-02**: [x] Creating a submission auto-creates or reuses the Repository record
- **AC-US2-03**: [x] Skills are linked to their parent Repository via FK
- **AC-US2-04**: [x] The API can query all skills for a given repository URL

### US-003: As a submitter, I want to submit all skills from a repo in one action
- **AC-US3-01**: [x] A new "bulk submit" endpoint accepts repoUrl + list of skill paths and creates submissions for all non-duplicate skills in a single request
- **AC-US3-02**: [x] Bulk submit respects dedup — skips already-pending/verified skills
- **AC-US3-03**: [x] Bulk submit returns per-skill status (created/skipped/already-verified)
- **AC-US3-04**: [x] The submit page UI uses bulk submit instead of individual POSTs

### US-004: As a submitter, I want to see which skills are already verified before submitting
- **AC-US4-01**: [x] The discover endpoint enriches each skill with its current status (new/pending/verified/rejected)
- **AC-US4-02**: [x] The submit page UI shows verification badges next to already-verified skills
- **AC-US4-03**: [x] Already-verified skills are pre-deselected in the selection UI

## Non-Functional Requirements

- **NFR-01**: Bulk submit must handle 150+ skills in a single request without timeout (Cloudflare Workers 30s limit)
- **NFR-02**: Dedup checks must be < 100ms per skill
- **NFR-03**: Backward compatible — existing single-skill POST endpoint continues to work
- **NFR-04**: Database migration must be non-breaking (additive columns/tables only)

## Out of Scope

- Plugin-level grouping in the database (UI-only concern, handled by increment 0247)
- Automated re-verification on repo changes (future webhook-based increment)
- Cross-repo skill deduplication (same skill name in different repos is allowed)
