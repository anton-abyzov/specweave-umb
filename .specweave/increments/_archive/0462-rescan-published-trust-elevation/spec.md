---
increment: 0462-rescan-published-trust-elevation
title: "Rescan Published Skills for Trust Elevation"
type: feature
priority: P1
status: planned
created: 2026-03-09
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rescan Published Skills for Trust Elevation

## Problem Statement

41% of published skills (34,342 out of 84,779) remain at trustTier T2 ("maybe") because they were fast-approved via Tier 1 regex scan only, without Tier 2 LLM analysis. These skills need full re-scanning to elevate to T3 ("verified"), improving overall trust quality across the registry.

## Goals

- Re-queue T1/T2 published skills through the full scanning pipeline
- Elevate trust tiers based on comprehensive T1+T2 scan results
- Provide dry-run mode for safe previewing before bulk operations
- Reuse existing pipeline infrastructure (no changes to processSubmission or publishSkill)

## User Stories

### US-001: Rescan Published Skills Endpoint (P1)
**Project**: vskill-platform

**As a** platform admin
**I want** an API endpoint that re-queues published skills with low trust tiers for full scanning
**So that** skills stuck at T1/T2 get elevated to their proper trust tier after LLM analysis

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a POST to `/api/v1/admin/rescan-published` with valid auth, when called with `{ "dryRun": true }`, then it returns counts of eligible T1/T2 published skills without creating any records
- [x] **AC-US1-02**: Given a live (non-dry-run) call, when executed, then it creates new Submission records in RECEIVED state for up to 500 eligible published skills and enqueues them to SUBMISSION_QUEUE
- [x] **AC-US1-03**: Given published skills that already have a pending Submission (state not in a terminal state), when the endpoint runs, then those skills are skipped to avoid duplicate pipeline runs
- [x] **AC-US1-04**: Given published skills with trustTier T0 (blocked) or that are on the active blocklist, when the endpoint runs, then those skills are skipped
- [x] **AC-US1-05**: Given the optional body parameter `{ "skipExistingT2": true }`, when the endpoint runs, then skills that already have a Tier 2 ScanResult are excluded from re-scanning

### US-002: Batched Pagination and Observability (P1)
**Project**: vskill-platform

**As a** platform admin
**I want** the rescan endpoint to process in batches with clear progress reporting
**So that** I can safely re-scan 34k+ skills without overwhelming the queue or losing visibility

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given more than 500 eligible skills, when the endpoint completes a batch, then the response includes `"hasMore": true` and the caller repeats until `hasMore` is false
- [x] **AC-US2-02**: Given each created Submission, when the state is set to RECEIVED, then a SubmissionStateEvent audit record is created with trigger "rescan-published: trust elevation" and actor "system"
- [x] **AC-US2-03**: Given a request without valid X-Internal-Key header or SUPER_ADMIN Bearer token, when the endpoint is called, then it returns 401/403

## Out of Scope

- Changes to processSubmission or publishSkill (existing upsert logic handles re-scans)
- UI for triggering or monitoring rescans (admin uses CLI/curl)
- Automatic scheduling/cron for the rescan endpoint
- Modifying trust tier calculation logic

## Technical Notes

### Dependencies
- Existing `processSubmission` pipeline (handles full T1+T2 scanning)
- Existing `publishSkill()` upsert (updates trust data on already-published skills)
- CF Queue `SUBMISSION_QUEUE` for enqueuing
- Prisma Skill and Submission models

### Constraints
- Batch size: 500 skills per call, queue chunks of 100 (matching bulk-reprocess pattern)
- Auth: X-Internal-Key OR SUPER_ADMIN (same as bulk-reprocess)
- Single new file: `src/app/api/v1/admin/rescan-published/route.ts`

### Architecture Decisions
- Create new Submission records rather than reusing old ones (clean audit trail, no state machine conflicts)
- Query Skill table (PUBLISHED skills by trustTier) rather than Submission table (this is skill-centric, not submission-centric)
- Follow bulk-reprocess pattern for auth, batching, response shape, and queue chunking

## Success Metrics

- T2 skill count drops from 34,342 toward 0 as rescans complete
- T3 skill count increases proportionally
- No duplicate submissions created for skills with pending pipeline runs
