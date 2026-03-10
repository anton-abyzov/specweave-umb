---
increment: 0471-submit-rescan-feedback
title: 'Submit page: distinguish new vs rescan submissions'
type: bug
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Submit page: distinguish new vs rescan submissions

## Problem Statement

The submit page at `/submit` treats all discovered skills identically regardless of whether they already exist on the platform. When a user resubmits a repo containing skills that are already verified (stale >24h), every skill shows as "N submitted" with no indication that some are rescans of existing skills. The discovery endpoint (`POST /api/v1/submissions/discover`) already returns enrichment status (`new`/`verified`/`pending`/`rejected`) per skill via `enrichDiscoveryWithStatus`, but the frontend `DiscoveredSkill` interface drops the `status` field and never uses it.

## Goals

- Surface discovery enrichment status in the submit flow so users understand what is being newly submitted vs rescanned
- Show "Rescan >>" labels for verified skills being re-evaluated
- Adapt the summary line to reflect the mix of new and rescan submissions

## User Stories

### US-001: Rescan-aware submission feedback (P1)
**Project**: vskill-platform

**As a** skill author resubmitting a repo with existing verified skills
**I want** the submit results to distinguish between new submissions and rescans of existing skills
**So that** I understand which skills are being freshly evaluated vs re-evaluated

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the discovery endpoint returns skills with `status: "verified"`, when the `DiscoveredSkill` interface is used in the frontend, then it includes an optional `status` field of type `"new" | "verified" | "pending" | "rejected"` and preserves the value from the API response
- [x] **AC-US1-02**: Given a mixed submission with N new skills and M verified (rescan) skills, when results are displayed, then the summary line reads "N new, M rescanning" instead of "N+M submitted"; when all are rescans (N=0) it reads "M rescanning"; when all are new (M=0) it reads "N submitted" (existing behavior preserved)
- [x] **AC-US1-03**: Given a skill result where the original discovery status was `"verified"`, when the result row is rendered with a successful submission (has `id`), then it shows a "Rescan >>" link (instead of "Track >>") pointing to `/submit/{id}`
- [x] **AC-US1-04**: Given skills with discovery status `"rejected"` or `"new"`, when counted for the summary line, then both are treated as "new" submissions (no separate category for rejected)

## Out of Scope

- Backend changes to the discovery or submission endpoints
- Changes to the `pending` skill handling (already shows "Already pending" correctly)
- Staleness threshold logic (handled server-side)
- Changes to the submitting/discovering phase UI

## Technical Notes

### Dependencies
- `enrichDiscoveryWithStatus` in `src/lib/discovery-enrichment.ts` (already deployed, returns status per skill)
- Discovery API response shape (already includes `status` field on each skill object)

### Constraints
- Frontend-only change in `src/app/submit/page.tsx`
- Must preserve existing behavior for all-new submissions and pending/skipped skills

## Success Metrics

- Resubmission of a repo with verified skills shows accurate new/rescanning breakdown
- No regression in new-submission-only flow
