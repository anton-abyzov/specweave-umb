---
increment: 0376-fix-dora-metrics-pipeline
title: Fix broken DORA metrics pipeline and dashboard
type: bug
priority: P1
status: completed
created: 2026-02-25T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Bug Fix: Fix broken DORA metrics pipeline and dashboard

## Overview

Fix CFR/lead-time threshold mismatches between code and documentation, update stale goals that no longer reflect current performance, and correct dashboard text inconsistencies.

## User Stories

### US-001: Fix CFR threshold boundary (P1)
**Project**: specweave

**As a** developer reviewing DORA metrics
**I want** the CFR tier classifier to match documented thresholds (0-15% = Elite)
**So that** a 15% CFR is correctly classified as Elite, not High

**Acceptance Criteria**:
- [x] **AC-US1-01**: `classifyChangeFailureRate(15)` returns `'Elite'` (was returning `'High'` due to strict `< 15`)
- [x] **AC-US1-02**: `classifyChangeFailureRate(30)` returns `'High'` (boundary inclusive)
- [x] **AC-US1-03**: `classifyChangeFailureRate(45)` returns `'Medium'` (boundary inclusive)
- [x] **AC-US1-04**: Existing tier classifications for values not on boundaries remain unchanged

---

### US-002: Fix dashboard documentation inconsistencies (P1)
**Project**: specweave

**As a** user reading the DORA dashboard
**I want** the documented thresholds to match the actual code
**So that** I can trust the tier classifications shown

**Acceptance Criteria**:
- [x] **AC-US2-01**: metrics.md Lead Time High benchmark reads "1 hour to 1 week" (was "1 day to 1 week")
- [x] **AC-US2-02**: metrics.md CFR benchmarks read "0-15%", "15-30%", "30-45%" (was "16-30%", "31-45%")
- [x] **AC-US2-03**: Goals section updated to reflect current performance: DF=Elite (100/mo), Lead Time=High (3.4h), CFR=Elite (0%), MTTR=N/A

## Out of Scope

- Changing the cron refresh frequency
- Adding new DORA metrics
- Modifying the GitHub Actions workflow structure
