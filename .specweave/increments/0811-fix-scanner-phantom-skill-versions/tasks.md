# Tasks: Fix scanner phantom SkillVersion bumps

## Task Notation
- `[T###]`: Task ID
- `[ ]` not started · `[x]` completed
- TDD phases: `[RED]` failing test → `[GREEN]` minimal impl

---

## Phase 1: Scanner content-hash gate (US-001)

### T-001: TC-S01..S05 — failing tests for scanner content-hash gate [RED]
**AC**: AC-US1-06
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (append new describe)
**Test plan**:
- TC-S01 — same content → no bump (mock fetch returns `8eda5a1a7566...`-equivalent SKILL.md, prior SkillVersion has the same real hash).
- TC-S02 — different content → bump with REAL hash (no `pending:` prefix in written row).
- TC-S03 — fetch fails → falls through to legacy bump-with-pending-hash; metric `scanner.contentfetch.failed` emitted.
- TC-S04 — legacy `sha256:pending:<sha>` previous row + new fetch returns content matching the legacy commit's content → still dedups.
- TC-S05 — first publish (no previous SkillVersion row) → bumps with real hash.
**Status**: [x] completed

### T-002: Implement content-hash gate in scanner.ts [GREEN]
**AC**: AC-US1-01..05
**File**: `src/lib/skill-update/scanner.ts`
**Test**: Given T-001 RED → implement `fetchSkillMdAtSha`, `sha256Hex`, `getLatestSkillVersion`, and the dedup branch in `scanOneSkill` → TC-S01..S05 pass; existing scanner tests still pass.
**Status**: [x] completed

---

## Phase 2: Backfill admin endpoint (US-002)

### T-003: TC-B01..B05 — failing tests for backfill route [RED]
**AC**: AC-US2-07
**File**: `src/app/api/v1/admin/skills/[id]/backfill-content-hashes/__tests__/route.test.ts` (NEW)
**Test plan**:
- TC-B01 — non-admin → 401/403.
- TC-B02 — non-existent skill id → 404.
- TC-B03 — dryRun=true on phantom-shaped fixture (3 rows: real, pending matching real, pending matching real) → returns `{scanned:3, recomputed:2, deleted:2, finalCurrentVersion:"1.1.0", dryRun:true}` with NO DB mutations.
- TC-B04 — dryRun=false on same fixture → returns the same numbers AND skill row + version rows are mutated.
- TC-B05 — idempotent re-run after collapse → `{scanned:1, recomputed:0, deleted:0}`.
**Status**: [x] completed

### T-004: Implement backfill route [GREEN]
**AC**: AC-US2-01..06
**Files**: `src/app/api/v1/admin/skills/[id]/backfill-content-hashes/route.ts` (NEW)
**Test**: Given T-003 RED → implement the POST handler per plan.md → TC-B01..B05 pass.
**Status**: [x] completed

---

## Phase 3: Verification + deploy

### T-005: vitest + tsc on all 0811 paths
**AC**: success criteria
**Cmd**: `npx vitest run src/lib/skill-update src/app/api/v1/admin/skills` then `npx tsc --noEmit 2>&1 | grep -E "(skill-update|backfill-content-hashes)"`
**Status**: [x] completed

### T-006: Build + deploy to Cloudflare prod
**Cmd**: `mv public/hackathon-demo/out/hackathon-demo.mp4 /tmp/0811-mp4-bk && rm -rf .open-next && npm run build && npm run build:worker && npm run deploy && mv /tmp/0811-mp4-bk public/hackathon-demo/out/hackathon-demo.mp4`
**Status**: [x] completed

### T-007: Production backfill on remotion-best-practices (US-003)
**AC**: AC-US3-01
**Action**: POST `/api/v1/admin/skills/anton-abyzov/vskill/remotion-best-practices/backfill-content-hashes` (`{owner}/{repo}/{skill}` canonical path, NOT `[id]`) — dryRun then live.
**Result**: `{scanned:3, recomputed:2, deleted:2, finalCurrentVersion:"1.1.0", finalLastSeenSha:"0bd4b5e59d0e1fb4f675b44f573f082a546cfe21"}`. Public API now returns single v1.1.0 row with real `8eda5a1a756612...` content hash (no `pending:` prefix).
**Status**: [x] completed

### T-007b: Mass backfill across the entire registry (USER FOLLOW-UP)
**Action**: Iterated through all 5,442 skills with `sha256:pending:` rows via 12-way parallel curl loop against the deployed admin endpoint.
**Result**:
- Before: 11,131 pending rows / 5,442 affected skills / 20,836 total SkillVersion rows.
- After: 750 pending rows / 171 affected skills / 10,065 total SkillVersion rows.
- Resolved: 10,381 phantom rows (93%) / 5,271 skills cleaned (97%) / 10,771 phantom rows DELETED.
- Residual 171 skills are repos where SKILL.md was renamed/moved/deleted in source — fetch returns 404, hash can't be recomputed. Forward fix prevents new phantoms; residual can be hand-pruned later.
**Status**: [x] completed

### T-008: Wait for next `*/10` cron tick + verify no re-bump
**AC**: AC-US3-02
**Action**: Waited for `*/10` cron at 06:50 UTC. Re-queried versions API for `anton-abyzov/vskill/remotion-best-practices`.
**Result**: Still exactly 1 version row. Scanner did NOT re-bump despite the previous v1.1.2 gitSha being unchanged. Content-hash dedup gate confirmed working in production.
**Status**: [x] completed

### T-009: Playwright e2e
**AC**: AC-US3-03
**File**: `tests/e2e/skills-versions.spec.ts` (or extend existing skills suite)
**Test**: Given the live API → When test fetches `/api/v1/skills/anton-abyzov/vskill/remotion-best-practices/versions` → Then exactly 1 version, `version === "1.1.0"`, `contentHash` does NOT start with `sha256:pending:`. Also visit the public versions page on the deployed site and assert one row in the version history.
**Status**: [x] completed

### T-010: Commit + push (vskill-platform + umbrella)
**Status**: [x] completed
