# 0763 — Tasks

## T-001: Switch queue avg_score query to Skill.certScore
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a `Skill` table with mixed certScore values (NULL, 0, positive), when the cron's Phase 1b query runs, then it returns the rounded average of positive certScore values, in <2s, never `0` if at least one positive value exists.

## T-002: Add `verifiedCount` prop + `formatSearchPlaceholder` to HeroSearch
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given verifiedCount=115343, formatSearchPlaceholder returns `"Search 115,000+ verified skills..."`. Given verifiedCount=undefined or 0, returns `"Search verified skills..."`. Given verifiedCount=42, returns `"Search 42+ verified skills..."`.

## T-003: Wire `stats.verifiedCount` from page.tsx into `<HeroSearch>`
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given the home page renders with `getHomeStats()` returning `{verifiedCount: 115343, ...}`, when `<HeroSearch>` is rendered as a child, then the `<input>` `placeholder` attribute reads `Search 115,000+ verified skills...`.

## T-004: Add HeroSearch unit tests for the three placeholder branches
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Vitest + RTL render with each `verifiedCount` value, assert `screen.getByPlaceholderText` matches expected string.

## T-005: Document Skill-vs-Submission counter divergence
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Deliverable is a markdown report at `reports/findings.md` listing every numeric counter on home + queue + their data sources, plus the recommendation about labels. No automated test (documentation artifact).

## T-006: Fix Worker Skill query column (`status` → `certTier`) + VM stats-compute syntax + queries
**User Story**: US-003 / US-003B | **AC**: AC-US3-A1, AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given the Worker `queue-stats-refresh.ts` Phase 1b and `ensureFreshStats` watchdog now query `"certTier"` (not `"status"`), when the existing 35 vitest cases run against mocked Skill rows, then they pass. Given the VM `stats-compute.js` is now syntactically valid (no `*/10` JSDoc terminator) and queries Skill.certScore + certTier, when `node -e "import('./sources/stats-compute.js')"` runs, then it imports without error.

## T-007: Add KV-merge to /api/v1/internal/stats/queue route handler
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given five new vitest cases for prior-KV merge behavior in `route.test.ts`, when the route receives a VM payload that omits rejectionBreakdown / has avgProcessingTimeMs=0, then prior fields are preserved and body fields override prior fields; when prior KV is missing or corrupt, the body is written as-is.

## T-008: Deploy CF Worker + all 3 Hetzner VMs
**User Story**: US-003 / US-003B | **AC**: AC-US3-A2, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given `scripts/push-deploy.sh origin main` runs, then `verified-skill-com` Worker version is updated. Given `bash scanner-worker/deploy.sh` runs, then all 3 VMs (5.161.69.232 / 91.107.239.24 / 5.161.56.136) report healthy `/health` endpoints.

## T-009: Verify avgScore > 0 in production for two consecutive cron ticks
**User Story**: US-003 / US-003B | **AC**: AC-US3-A2, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given the deploy is live, when the next CF cron tick runs, then `curl https://verified-skill.com/api/v1/submissions/stats | jq '.avgScore, .totalSkillsAll'` returns positive integers; repeat after a further tick to confirm the value persists. Verified: 06:25:45 UTC → avgScore=97 totalSkillsAll=117564; 06:35:41 UTC → avgScore=97 totalSkillsAll=117565.
