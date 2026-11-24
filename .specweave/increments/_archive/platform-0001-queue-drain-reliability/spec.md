---
increment: 0001-queue-drain-reliability
title: "Submission Queue Drain Reliability"
status: active
priority: P0
type: incident
created: 2026-05-14
---

# Submission Queue Drain Reliability

## Problem Statement

The verified-skill.com submission queue is stuck with old `RECEIVED` submissions, while the VM worker fleet may appear healthy. The system currently allows the scanner drain path to fail silently or remain misconfigured long enough for the oldest submission age to exceed 1180 hours. The dashboard also appears stale, so production user/submission activity must be verified against the database rather than UI impressions alone.

## Goals

- Restore submission draining in production.
- Identify whether the root cause is worker health, callback/auth config, database reachability, queue claim logic, or stale infrastructure.
- Decide whether to keep the current server topology, reuse an existing Postgres-capable server, or migrate to a new production database/server.
- Add prevention: health checks, runbook clarity, and operational safeguards so the queue cannot silently stall for days.
- Verify real user activity and recent submissions from production data.

## User Stories

### US-001: Production Queue Diagnosis
**Project**: vskill-platform
**As an** operator
**I want** the stuck queue investigated from API, database, and VM logs
**So that** the exact failure mode is known before changing infrastructure

**Acceptance Criteria**:
- [x] **AC-US1-01**: `/api/v1/admin/queue-health` and relevant admin/internal endpoints are checked against production.
- [x] **AC-US1-02**: Production database counts identify `RECEIVED`, in-flight, terminal, and oldest submissions.
- [x] **AC-US1-03**: VM/service logs show whether scanner workers are running, failing callbacks, failing claims, or unable to reach dependencies.
- [x] **AC-US1-04**: Root cause is documented in the increment task notes.

### US-002: Production Data Freshness
**Project**: vskill-platform
**As an** operator
**I want** real user and submission activity checked directly in the database
**So that** stale dashboard data is separated from real lack of usage

**Acceptance Criteria**:
- [x] **AC-US2-01**: Recent users, installs, submissions, and skill activity are queried from production.
- [x] **AC-US2-02**: The investigation distinguishes genuine usage from synthetic/backfill/test data where possible.
- [x] **AC-US2-03**: Findings include whether anyone is actively submitting to the platform now.

### US-003: Reliable Queue Draining
**Project**: vskill-platform
**As an** operator
**I want** the queue drain path repaired or migrated
**So that** `RECEIVED` submissions progress without manual intervention

**Acceptance Criteria**:
- [x] **AC-US3-01**: Scanner workers are running against the correct production database and callback URL.
- [x] **AC-US3-02**: A stuck submission can be claimed and moved out of `RECEIVED` in production.
- [x] **AC-US3-03**: The production queue health check returns below alert thresholds after remediation.
- [x] **AC-US3-04**: If database/server migration is chosen, data is migrated and cut over with verified reads/writes.

### US-004: Prevention
**Project**: vskill-platform
**As an** operator
**I want** guardrails around the queue worker fleet
**So that** this failure is detected and remediated before multi-day backlog forms

**Acceptance Criteria**:
- [x] **AC-US4-01**: Worker deployment/configuration is repeatable from repo scripts or documented commands.
- [x] **AC-US4-02**: Monitoring differentiates healthy VMs from healthy queue draining.
- [x] **AC-US4-03**: A runbook or code change explains how to inspect and restart/remediate the scanner drain path.
- [x] **AC-US4-04**: Verification commands are recorded without exposing secrets.

### US-005: Deploy-Proof Queue Health
**Project**: vskill-platform
**As an** operator
**I want** queue-health fixes to be rebuilt, deployed, and smoke-checked automatically
**So that** stale generated Worker bundles cannot keep paging on fixed code

**Acceptance Criteria**:
- [x] **AC-US5-01**: `npm run deploy` rebuilds `.next` and `.open-next/worker-with-queues.js` before Cloudflare deployment.
- [x] **AC-US5-02**: Deployment fails if production `/api/v1/internal/queue-health-check` does not report schema v2 with `updatedAt` as the age basis.
- [x] **AC-US5-03**: Public `/api/v1/queue/health` reports schema v2 and `oldestActive.ageBasis: updatedAt`.
- [x] **AC-US5-04**: Production queue-health is verified after deployment without exposing secrets.
- [x] **AC-US5-05**: Deploy smoke tolerates Cloudflare propagation delay and verifies the internal alert contract in dry-run mode.

### US-006: Self-Healing Queue Alerting
**Project**: vskill-platform
**As an** operator
**I want** queue alerting to remediate stale rows before paging
**So that** transient queue drift does not re-alert every few days

**Acceptance Criteria**:
- [x] **AC-US6-01**: The cron-triggered queue-health alert path runs stale-RECEIVED recovery before deciding to email.
- [x] **AC-US6-02**: Cloudflare scheduled recovery and queue-health alerting are sequenced in one `waitUntil`, not racing as parallel jobs.
- [x] **AC-US6-03**: Dry-run deploy smoke verifies the internal alert contract without triggering recovery, alert email, or throttle mutation.
- [x] **AC-US6-04**: Smart `drain-stalled` alerts require an actually old active row, not merely any fresh active work item.
- [x] **AC-US6-05**: The generated Worker bundle contract asserts queue-health alerting remains sequenced after stale-received recovery.

## Out of Scope

- Rebuilding the scanner engine unrelated to queue draining.
- Broad dashboard redesign.
- Deleting production user data.
