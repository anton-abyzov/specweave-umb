# Tasks: Webhook path-filter + frontmatter-driven version bumps

## Phase 0: Residual cleanup (US-003) — ALREADY DONE via direct SQL

### T-000: Phase A + Phase B SQL cleanup
**AC**: AC-US3-01..04
**Action**: Two `BEGIN/COMMIT` transactions executed against prod DB. Phase A: 97 skills with real rows had 169 pending rows deleted, currentVersion+lastSeenSha reset to latest real row. Phase B: 82 skills with only-pending rows had 601 pending rows deleted; the newest survivor's contentHash rewritten from `sha256:pending:<gitSha>` to `sha256:legacy:<gitSha>`; currentVersion+lastSeenSha reset to the survivor.
**Result**: `SELECT count(*) FROM "SkillVersion" WHERE "contentHash" LIKE 'sha256:pending:%'` returned `0`.
**Status**: [x] completed

---

## Phase 1: Webhook path-filter (US-001)

### T-001: TC-W01..W06 — failing tests for webhook path-filter [RED]
**AC**: AC-US1-06
**File**: `src/app/api/v1/webhooks/github/__tests__/route.test.ts`
**Test plan**:
- TC-W01 — push touches one skill's path (out of three tracked) → 1 enqueue + 2 skips, response `{enqueued:1, skipped:2}`.
- TC-W02 — push touches NONE of three tracked skill paths → 0 enqueues + 3 skips.
- TC-W03 — `commits` array missing → fall back to enqueue-all (3 enqueues, 0 skips).
- TC-W04 — `commits` array empty → fall back to enqueue-all (preserve correctness on huge-push truncation).
- TC-W05 — skill with `skillPath: null` (legacy) → always enqueued regardless of changedPaths.
- TC-W06 — metric `webhook.skipped.path-mismatch` is emitted with each filtered skillId.
**Status**: [x] completed

### T-002: Webhook path-filter impl [GREEN]
**AC**: AC-US1-01..05
**File**: `src/app/api/v1/webhooks/github/route.ts`
**Test**: Given T-001 RED → add `collectChangedPaths` + `skillTouched` + filter `matches` → TC-W01..W06 pass; existing webhook tests still pass.
**Status**: [x] completed

---

## Phase 2: Frontmatter-driven bumps (US-002)

### T-003: TC-F01..F04 — failing tests for frontmatter version logic [RED]
**AC**: AC-US2-06
**File**: `src/lib/skill-update/__tests__/scanner.test.ts` (append + update existing TC-S02)
**Test plan**:
- TC-F01 — frontmatter version `1.2.0` > current `1.1.0` → SkillVersion written with `version: "1.2.0"` (NOT `1.1.1`).
- TC-F02 — frontmatter version `1.1.0` === current `1.1.0`, content changed → SKIP bump, advance `lastSeenSha`, emit `scanner.bump.skipped.no-frontmatter-bump`.
- TC-F03 — frontmatter version `1.0.0` < current `1.1.0` (downgrade) → SKIP bump, do NOT advance `lastSeenSha`, emit `scanner.bump.rejected.downgrade`.
- TC-F04 — no frontmatter version field at all → fall back to `deriveNextVersion`, emit `scanner.bump.fallback.no-frontmatter`.
- (Existing TC-S02 updated to bump frontmatter version so it stays in the bump path.)
**Status**: [x] completed

### T-004: Frontmatter-driven bump impl [GREEN]
**AC**: AC-US2-01..05
**File**: `src/lib/skill-update/scanner.ts`
**Test**: Given T-003 RED → import `readFrontmatterVersion`, add `compareSemver`, branch on result → TC-F01..F04 pass; existing scanner tests still pass.
**Status**: [x] completed

---

## Phase 3: Verification + deploy

### T-005: vitest + tsc on 0813 paths
**Cmd**: `npx vitest run src/lib/skill-update src/app/api/v1/webhooks/github` then `npx tsc --noEmit 2>&1 | grep -E "(skill-update|webhooks/github|inject-version-if-missing)"`
**Status**: [x] completed

### T-006: Build + deploy to Cloudflare prod
**Cmd**: `rm -rf .open-next && npm run build && npm run build:worker && npm run deploy`
**Status**: [x] completed

### T-007: Production smoke
**Action**:
1. Push an unrelated commit to a tracked repo. Confirm webhook response `{enqueued:0, skipped:N}` for skills whose paths weren't touched.
2. Verify `count(*) FROM "SkillVersion" WHERE "contentHash" LIKE 'sha256:pending:%'` is still `0` (residual cleanup persisted).
3. Wait for next `*/10` cron tick. Verify NO new SkillVersion rows appear for `anton-abyzov/vskill/remotion-best-practices` (still 1 row, version 1.1.0).
**Status**: [x] completed

### T-008: Commit + push (vskill-platform + umbrella)
**Status**: [x] completed
