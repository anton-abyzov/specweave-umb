# 0258: Queue Resilience & Smart Resubmission

## Problem Statement

The submission processing queue has 50 items stuck in non-terminal states (TIER1_SCANNING, RECEIVED, AUTO_APPROVED, TIER2_SCANNING). Root cause: `max_batch_timeout: 10s` in wrangler.jsonc kills workers mid-processing, and there is no recovery mechanism. Additionally:
- Published skill slugs collide across repos (last publisher wins)
- KV list() calls don't paginate past 1,000 keys (already at 1,084 skills)
- Crawler re-submits entire repos after 7-day TTL, ignoring already-verified skills
- No observability into queue health or discovery stats

## User Stories

### US-001: As a platform operator, I want stuck submissions to recover automatically
- **AC-US1-01**: [ ] Queue consumer wraps processSubmission() in a timeout (25s) so partial failures are caught
- **AC-US1-02**: [ ] `max_batch_timeout` increased to 30s to give processing enough headroom
- **AC-US1-03**: [ ] Tier 2 LLM call has an explicit 8-second timeout; on timeout, falls back to Tier 1 scoring
- **AC-US1-04**: [ ] A recovery cron runs every hour, finds submissions stuck in non-terminal states for > 5 minutes, and re-enqueues them (max 1 retry, then FAILED)

### US-002: As a platform operator, I want published skills to never collide across repos
- **AC-US2-01**: [ ] Slug generation includes repo owner and name: `{owner}-{repo}-{skillName}`
- **AC-US2-02**: [ ] Existing 1,084 skills continue to resolve (backward compat via fallback lookup)

### US-003: As a platform operator, I want the crawler to only submit new/retryable skills
- **AC-US3-01**: [ ] Before submitting a repo, crawler checks each discovered skill against existing submissions
- **AC-US3-02**: [ ] Skills in PUBLISHED/PENDING states are skipped; only NEW and REJECTED skills are submitted
- **AC-US3-03**: [ ] Crawler logs show "skipped N already-verified, submitted M new" per repo

### US-004: As a platform operator, I want visibility into queue and discovery health
- **AC-US4-01**: [ ] GET /api/v1/admin/queue/status returns: stuck count, processing rate, avg duration, DLQ count
- **AC-US4-02**: [ ] KV list calls use cursor-based pagination to handle > 1,000 keys

### US-005: As an external user, I want rate limits to prevent abuse
- **AC-US5-01**: [ ] Single-submit: 10 requests per IP per hour (existing)
- **AC-US5-02**: [ ] Bulk-submit: 5 requests per IP per hour (existing from 0253)
- **AC-US5-03**: [ ] Discovery endpoint: 20 requests per IP per hour
- **AC-US5-04**: [x] GitHub-authenticated submissions get higher limits (30/hour)

## Non-Functional Requirements

- **NFR-01**: Recovery cron must complete within 10s (scan + re-enqueue)
- **NFR-02**: Slug migration must not break existing skill URLs/references
- **NFR-03**: All changes backward compatible with existing API consumers

## Out of Scope

- Webhook-based re-verification on repo push (future increment)
- Admin UI for manual queue management (0251 covers this)
- External SAST worker scaling (already at 4 Hetzner machines)
