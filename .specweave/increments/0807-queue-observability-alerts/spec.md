---
increment: 0807-queue-observability-alerts
title: "Smart email alerts for verified-skill queue health"
type: feature
priority: P1
status: active
created: 2026-04-29
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Smart email alerts for verified-skill queue health

## Overview

Detect queue stalls, drain-rate drops, stale heartbeats, orphan growth, LLM-fallback spikes, and submission max-retries on verified-skill.com. Send severity-tiered, deduped emails to `admin@easychamp.com`. Roll low-priority signals into a 4×/day digest. Surface fired alerts in the `/admin/queue` page with an Acknowledge action.

## Problem

The queue can stall silently. The user just witnessed a submission (`sub_40bce2cc`) sitting in `RECEIVED` with no progress, with no automatic notification — and a recent successful submission had to wait 12+ hours for pickup. Existing alerting covers only two coarse signals (`queue-stuck`, `vm-down`) and emails go to a personal address. Operators need smart, multi-signal alerts at a shared inbox with severity tiers, dedup, cooldown, and a digest mode.

## User Stories

### US-001: Configurable alert recipients (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** alert emails delivered to `admin@easychamp.com` (overrideable via env)
**So that** the team mailbox sees them, not a single person's gmail

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `ALERT_RECIPIENTS` env var is set (CSV), `sendQueueHealthAlert()` emails ALL listed addresses.
- [x] **AC-US1-02**: When `ALERT_RECIPIENTS` is unset, default recipient is `admin@easychamp.com` (never the previous hardcoded gmail).
- [x] **AC-US1-03**: A unit test asserts the recipient resolution logic for: unset / single / CSV / whitespace-trimmed / dedup.

---

### US-002: Multi-signal detection (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** alerts on the signals that actually matter — drain stalled, VM heartbeat stale, orphan count growing, LLM provider chain failovers, max-retry submissions
**So that** I learn about real problems instead of staring at the queue page

**Acceptance Criteria**:
- [x] **AC-US2-01**: A `drain-stalled` alert fires when `drainRate.last1h === 0` AND `oldestActive` exists.
- [x] **AC-US2-02**: A `heartbeat-stale` alert fires when `vmHeartbeat.ageMs > ALERT_HEARTBEAT_STALE_MS` (default 600_000 ms).
- [x] **AC-US2-03**: An `orphan-growing` alert fires when `orphanedActive.count` rose by ≥50 since the last detector run (delta tracked in KV `alerts:last-orphan-count`). On cold start (no baseline), records baseline and skips firing.
- [x] **AC-US2-04**: An `llm-fallback-spike` alert fires when combined fallback count for non-primary providers (`ai:fallback:claude:<today>` + `ai:fallback:ollama:<today>` + `ai:fallback:workers-ai:<today>`) exceeds `ALERT_LLM_FALLBACK_THRESHOLD` (default 20).
- [x] **AC-US2-05**: A `submission-max-retries` alert fires once per submission when `processingAttempts >= 3` and the submission is in an active state.
- [x] **AC-US2-06**: All detectors run from a single `POST /api/v1/internal/alerts-evaluator` (cron-auth), wired into the existing `*/10 * * * *` light cron cohort.

---

### US-003: Severity tiers, dedup, cooldown, digest (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** critical alerts immediately, warnings deduped on a window, and routine info rolled into a daily digest
**So that** my inbox isn't a stream of duplicates and I can still spot patterns

**Acceptance Criteria**:
- [x] **AC-US3-01**: Each alert kind maps to a severity:
  - `critical`: `vm-down`, `drain-stalled`
  - `warning`: `queue-stuck`, `heartbeat-stale`, `orphan-growing`, `submission-max-retries`
  - `info`: `llm-fallback-spike` (digest only)
- [x] **AC-US3-02**: `critical` alerts fire immediately while the condition holds, with a 1h dedup window per `(kind, key)`.
- [x] **AC-US3-03**: `warning` alerts have a 6h dedup window per `(kind, key)`.
- [x] **AC-US3-04**: `info` alerts never fire as standalone emails — recorded for digest only.
- [x] **AC-US3-05**: Digest email summarizes counts per kind + last 5 samples per kind, sent at the next heavy-cohort tick after 09:00 / 13:00 / 17:00 / 21:00 UTC. If no events in window, no email is sent.
- [x] **AC-US3-06**: Dedup keys live in `ALERTS_KV` with shape `alerts:dedup:{kind}:{key}` (TTL = window length). `POST /api/v1/admin/alerts/{id}/ack` clears the dedup key.

---

### US-004: Surface in admin queue page (P2)
**Project**: vskill-platform

**As an** admin
**I want** to see recent alerts on the admin queue page and acknowledge them
**So that** I can quickly assess current pain without checking my inbox

**Acceptance Criteria**:
- [x] **AC-US4-01**: `GET /api/v1/admin/alerts/recent` (REVIEWER+ auth) returns the last 20 fired alerts (`{id, timestamp, kind, severity, dedupKey, acknowledged, payload}`).
- [x] **AC-US4-02**: `POST /api/v1/admin/alerts/{id}/ack` (REVIEWER+ auth) marks the alert acknowledged AND clears its dedup KV key so the next cron pass can re-fire if conditions persist.
- [x] **AC-US4-03**: A `RecentAlertsPanel` component renders above the existing tabs on `/admin/queue` and shows alerts grouped by severity with an Acknowledge button per row.
- [x] **AC-US4-04**: A Playwright e2e test asserts: panel renders → seeded alert visible → click Acknowledge → reload → alert moves to "Acknowledged" section.

## Success Criteria

- Within one cron tick (≤10 min) of a real queue stall, a critical email arrives at `admin@easychamp.com`.
- Repeat conditions do not spam: same `(kind, key)` cannot email more often than its dedup window.
- Daily digest summarizes everything that didn't qualify for an immediate email.
- `/admin/queue` shows the recent alerts without an extra page load.
- Vitest coverage for `src/lib/alerts/*` ≥ 90%.

## Out of Scope

- Slack / Discord / PagerDuty channels (email-only this round; design leaves room).
- Per-user subscription preferences (single global recipient list).
- Mobile push notifications.
- Replacing the broken VM heartbeat producer — separate bug, separate increment. This feature only **observes** staleness.

## Dependencies

- SendGrid (already wired via `src/lib/email.ts`).
- Existing cron cohort dispatcher (`src/lib/cron/cohort-dispatch.ts`).
- Queue health snapshot (`/api/v1/queue/health`).
- AI router fallback KV writer (`src/lib/ai/ai-router.ts`).
