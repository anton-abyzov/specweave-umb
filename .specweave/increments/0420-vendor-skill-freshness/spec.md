---
increment: 0420-vendor-skill-freshness
title: "Vendor Skill Freshness"
type: bug
priority: P1
status: completed
created: 2026-03-03
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Vendor Skill Freshness

## Problem Statement

14 of 16 official Anthropic skills from `anthropics/skills` are missing from vskill search results. The discovery pipeline's 30-day dedup TTL prevents re-scanning vendor repos for new skills, and the cron job excludes `vendor-orgs` from its discovery sources. When Anthropic (or any vendor org) adds new skills, they remain invisible until an admin manually triggers a force re-import.

## Goals

- All skills from VENDOR_ORGS repos are always discoverable via `npx vskill find`
- New vendor skills appear in search within 1 hour of being added to their repo
- No manual intervention needed to keep vendor skill catalog current

## User Stories

### US-001: Vendor skills bypass discovery dedup (P0)
**Project**: vskill-platform

**As a** vskill user searching for official skills
**I want** vendor org skills to always be re-submitted during discovery
**So that** new skills from Anthropic, OpenAI, and other vendors appear in search automatically

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a candidate from `vendor-orgs` source where `hasBeenDiscovered` returns true, when `processRepo` processes it, then the candidate is NOT skipped and is submitted for processing
- [x] **AC-US1-02**: Given a candidate from `github-code` source where `hasBeenDiscovered` returns true, when `processRepo` processes it, then the candidate IS skipped (existing dedup behavior preserved)

---

### US-002: Vendor discovery runs on cron schedule (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** vendor-orgs discovery to run automatically on the hourly cron
**So that** vendor skill freshness doesn't depend on manual admin intervention

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the cron scheduled handler fires at the :00 minute, when discovery runs, then `vendor-orgs` is included in the sources list alongside `npm`
- [x] **AC-US2-02**: Given vendor-orgs discovery runs hourly with dedup bypass, when a vendor adds a new skill, then it appears in search results within ~1 hour

## Out of Scope

- Changes to the standalone `runVendorOrgDiscovery` function (already supports `force`)
- Changes to the `import-vendor-skills.ts` script
- KV search index rebuild logic (already auto-updates via queue on publish)
- New admin endpoints

## Dependencies

- `src/lib/crawler/github-discovery.ts` — main discovery orchestrator with `processRepo`
- `scripts/build-worker-entry.ts` — generates cron scheduled handler
- `src/lib/trust/trusted-orgs.ts` — VENDOR_ORGS set (read-only, no changes)
- `DiscoveredRepo.source` field already carries source identifier ("vendor-orgs")

## Success Criteria

- `npx vskill find pptx` returns Anthropic's official PPTX skill with CERTIFIED tier
- All 16 skills from `anthropics/skills` are discoverable via search
- No manual admin intervention required for ongoing vendor freshness
