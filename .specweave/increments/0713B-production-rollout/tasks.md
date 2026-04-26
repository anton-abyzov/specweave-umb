---
increment: 0713B-production-rollout
title: "Queue Pipeline Restoration (P0) — Production Rollout Tasks"
test_mode: manual
parent: 0713-queue-pipeline-restoration
---

# Tasks

Operator-only execution. No code changes expected. Each task maps to a manual command that must be run with production credentials.

## Phase 1 — production deploy + verify

### T-101: DEPLOY — Phase 1 to production
**User Story**: US-101 | **Satisfies ACs**: AC-US101-01 | **Status**: [ ] pending
- `cd repositories/anton-abyzov/vskill-platform`
- `npm run build && npx wrangler deploy` (or the project's existing deploy script — check `package.json scripts.deploy`)
- Confirm deploy reports success and the new version ID is live.

### T-102: VERIFY — manual stats cron tick
**User Story**: US-101 | **Satisfies ACs**: AC-US101-02, AC-US101-04 | **Status**: [ ] pending
- Run `wrangler tail` in one terminal.
- Wait for next 10-min cron tick (or trigger manually).
- Confirm `submissions:stats-cache` `generatedAt` updates within 11 min and `degraded: false`.
- Document outcome in this task or PR description.

### T-103: VERIFY — list endpoint smoke test
**User Story**: US-101 | **Satisfies ACs**: AC-US101-03 | **Status**: [ ] pending
- `curl -s 'https://verified-skill.com/api/v1/submissions?state=all&sort=createdAt&sortDir=desc&limit=10' | jq '.items | length'` → expect ≥ 10.
- `curl -s 'https://verified-skill.com/api/v1/submissions?state=active&limit=5' | jq` → expect submission objects (or `warning: list_empty_total_mismatch` if truly empty).

### T-104: EXECUTE — drain stuck hyperframes rows
**User Story**: US-102 | **Satisfies ACs**: AC-US102-01, AC-US102-02 | **Status**: [ ] pending
- `node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5 --dry-run` → review 6 intended drains.
- `node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5` → execute.
- Within 60 seconds, all 6 IDs (`sub_4ce1d8a7…`, `sub_e64164f1…`, `sub_1ce97022…`, `sub_79d9e244…`, `sub_b8642378…`, `sub_4a5b43de…`) transition out of RECEIVED.
- Verify via `curl https://verified-skill.com/api/v1/submissions/<id> | jq '.submission.state'`.

### T-105: EXECUTE — backfill state-history against production
**User Story**: US-103 | **Satisfies ACs**: AC-US103-01, AC-US103-02 | **Status**: [ ] pending
- `node scripts/backfill-state-history.ts --dry-run | head -50` → review counts.
- `node scripts/backfill-state-history.ts` → execute.
- Verify 6 hyperframes records have well-formed history via `curl /api/v1/submissions/<id> | jq '.submission.stateHistory'`.

## Phase 2 — UX deploy + verify

### T-106: DEPLOY — Phase 2 to production
**User Story**: US-104 | **Satisfies ACs**: AC-US104-01 | **Status**: [ ] pending
- If Phase 1 already shipped Phase 2 changes (single deploy), mark complete and move on.
- Else: `cd repositories/anton-abyzov/vskill-platform && npx wrangler deploy`.

### T-107: VERIFY — Phase 2 UX no-flip + sort
**User Story**: US-104 | **Satisfies ACs**: AC-US104-02, AC-US104-03 | **Status**: [ ] pending
- Visit `https://verified-skill.com/queue` in a clean browser session.
  - URL stays `/queue` (no redirect to `?filter=published`).
  - "all" tab/view renders.
- Visit `https://verified-skill.com/queue?filter=all`.
  - Top row's createdAt is the max in the visible page (newest first).
- Visit each tab; confirm ONE time column (not dual Submitted | Updated).
- Confirm "Counters refreshing…" ribbon appears if stats are degraded (synthetic test only — should be absent post-recovery).

## Operational gate (for closure)

Per 0713 rubric: monitor for 24 hours post-deploy. Close this increment only when:
1. `submissions:stats-cache` `generatedAt` recent (< 11 min) on every check
2. No `list_empty_total_mismatch` warnings in logs
3. RECEIVED-row count in DB does not climb above 50
4. No 503 spike on `/api/v1/submissions` in CF analytics
