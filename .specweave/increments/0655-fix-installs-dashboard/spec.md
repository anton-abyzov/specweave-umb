---
increment: 0655-fix-installs-dashboard
title: "Fix admin installs dashboard unique machines + sort"
type: bug
priority: P1
status: active
created: 2026-04-01
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix admin installs dashboard unique machines + sort

## Overview

The admin installs dashboard inflates "Unique Machines" because `ipHash` uses a daily-rotating salt — the same machine on different days produces different hashes. Additionally, default sort is by total events instead of recency.

## User Stories

### US-001: True unique machine counting (P1)
**Project**: vskill-platform

**As an** admin
**I want** the installs dashboard to show true unique machines (not machine-days)
**So that** I can understand actual adoption across distinct users/machines

**Acceptance Criteria**:
- [x] **AC-US1-01**: InstallEvent has a `machineHash` field using a static (non-rotating) salt
- [x] **AC-US1-02**: Both install API endpoints populate `machineHash` on every new event
- [x] **AC-US1-03**: Admin stats SQL uses `COALESCE(machineHash, ipHash)` for unique machine count, falling back to ipHash for pre-migration rows
- [x] **AC-US1-04**: Prisma migration adds nullable `machineHash` column with index

---

### US-002: Fix default sort order (P1)
**Project**: vskill-platform

**As an** admin
**I want** the installs leaderboard sorted by most recent install first
**So that** I can see which skills are actively being installed

**Acceptance Criteria**:
- [x] **AC-US2-01**: Default sort key is `lastInstallAt` descending (not `totalEvents`)

## Out of Scope

- Backfilling `machineHash` for existing rows (natural population over time)
- Removing `ipHash` (still needed for daily dedup)
