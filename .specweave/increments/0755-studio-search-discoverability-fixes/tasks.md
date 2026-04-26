# Tasks: Studio search discoverability fixes

## Task Notation
- `T-NNN`: Task ID
- `[ ]` not started · `[x]` completed
- TDD: RED → GREEN → REFACTOR → VERIFY

---

## Phase 1: US-001 Ranking up-weight cert tier

### T-001: Write golden ranking test (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] not started

**File**: `vskill-platform/src/lib/__tests__/search-ranking.test.ts` (new)

**Test Plan**: Given 1 T4 CERTIFIED vendor skill (githubStars=24, vskillInstalls=0, name `anton-abyzov/vskill/skill-builder`) and 30 T2 VERIFIED community skills (varying stars 0-200, names containing `skill-builder`); when sorted via `searchSkills(...)` for `q=skill-builder`; then the T4 vendor skill is at index 0.

**Verify**: vitest reports the new test as failing against unchanged source (RED achieved).

---

### T-002: Update computeCertBonus to take trustTier (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04 | **Status**: [ ] not started

**File**: `vskill-platform/src/lib/search.ts` (~line 117)

**Description**: Extend `computeCertBonus(certTier)` → `computeCertBonus(certTier, trustTier)`. Apply trust multiplier: T4=2.0, T3=1.5, T2=1.0, T1=0.7, T0=0.4. CERTIFIED base stays at 100; VERIFIED base stays at 20. Update all call sites.

---

### T-003: Update sort caller to use blended rank as secondary tiebreaker (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [ ] not started

**File**: `vskill-platform/src/lib/search.ts:269-275`

**Description**: Re-order the sort comparators: cert priority first (existing), then `computeSearchRank` blended diff (was githubStars), then `githubStars` as last tiebreaker. The blended rank now includes the trust-multiplied cert bonus, so T4 vendor skills outrank lower-trust competitors regardless of star count.

---

### T-004: Verify ranking change doesn't regress neutral queries (REFACTOR)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [ ] not started

**Description**: Add a second test: synthetic input of 5 popular React-related VERIFIED skills (varying stars 100-10000) → assert ranking is still by star count (popularity-dominant) for queries where cert tier is uniform. Then run full `src/lib/__tests__/` suite.

---

### T-005: Deploy + production smoke for ranking (VERIFY)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: Stash 0751 if present, commit phase 1 changes, `npm run clean && npm run build:worker && npm run deploy`. Probe `curl https://verified-skill.com/api/v1/studio/search?q=skill-builder&limit=30` and confirm `anton-abyzov/vskill/skill-builder` is in the returned `results`. Capture in `reports/phase1-smoke.log`. Restore 0751 stash.

---

## Phase 2: US-002 LIST endpoint filters

### T-006: Write LIST filter tests (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..06 | **Status**: [ ] not started

**File**: `vskill-platform/src/app/api/v1/skills/__tests__/route.test.ts` (extend existing)

**Test Plan**: 4 new tests — (a) `?author=anton-abyzov` returns only anton-abyzov skills; (b) `?source=vendor` returns only vendor; (c) `?q=skill-builder` narrows by contains; (d) combining `?author=X&source=vendor` uses AND. Each fails RED against unmodified route.

---

### T-007: Add sanitizeFilter helper (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [ ] not started

**File**: `vskill-platform/src/lib/studio/sanitize.ts` (new) OR reuse existing search-route sanitizer.

**Description**: 200-char cap, charset whitelist `[A-Za-z0-9._/-]+`, returns null on violation (caller maps null → 400). Single helper used by both LIST endpoint and search endpoint.

---

### T-008: Wire q/author/source filters into route + getSkills (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..05 | **Status**: [ ] not started

**Files**: `src/app/api/v1/skills/route.ts` + `src/lib/data.ts`

**Description**: Parse new params in route.ts, validate via sanitizeFilter, pass to filters object. Extend `getSkills` where-clause: author OR-matches author or ownerSlug; source matches Skill.source; q OR-matches name/displayName/description with case-insensitive contains.

---

### T-009: Run targeted vitest for LIST route + data layer (GREEN)
**User Story**: US-002 | **Satisfies ACs**: regression guard | **Status**: [ ] not started

**Description**: `npx vitest run src/app/api/v1/skills/__tests__/ src/lib/__tests__/data` — all green.

---

### T-010: Deploy + smoke for LIST filters (VERIFY)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] not started

**Description**: Deploy. Probe `curl https://verified-skill.com/api/v1/skills?author=anton-abyzov` and confirm only anton-abyzov skills returned. Capture in `reports/phase2-smoke.log`.

---

## Phase 3: US-003 isVendor backfill

### T-011: Write isVendor backfill test (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [ ] not started

**File**: `vskill-platform/src/lib/submission/__tests__/publish.test.ts` (extend existing)

**Test Plan**: when publish() is invoked with a vendor-classified skill input (labels include `vendor`), assert that `db.submission.update({ where: { id }, data: { isVendor: true } })` is called once. Also assert idempotent: when submission.isVendor is already true, no update is called.

---

### T-012: Add isVendor backfill to publish.ts (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..03 | **Status**: [ ] not started

**File**: `vskill-platform/src/lib/submission/publish.ts`

**Description**: After `db.skill.upsert(...)` in the PUBLISHED transition, check `labels.includes("vendor") || certMethod === "VENDOR_AUTO"`. If true and `submission.isVendor !== true`, call `db.submission.update({...})`. Wrap in try/catch with logged warning on failure (don't block publish).

---

### T-013: Run publish.ts vitest (GREEN)
**User Story**: US-003 | **Satisfies ACs**: regression guard | **Status**: [ ] not started

**Description**: `npx vitest run src/lib/submission/` — all green.

---

### T-014: Deploy + smoke for isVendor (VERIFY)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] not started

**Description**: Deploy. The user's existing submission `sub_7a70abb7-0d97-4e29-822a-bdbdb00b61d3` won't be backfilled (out of scope), but a fresh test publish would. For verification, query an existing submission post-deploy and confirm the code path is reachable. Capture in `reports/phase3-smoke.log`.

---

## Phase 4: US-004 KV auto-reindex

### T-015: Investigate existing search-index/ folder (analysis)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 setup | **Status**: [ ] not started

**Description**: Read `vskill-platform/src/lib/search-index/` (the folder is in 0751's untracked work — confirmed via `git status` earlier). Determine if 0751 already shipped a consumer-side index updater. Document findings in `reports/phase4-investigation.md`. Outcome: pick approach (waitUntil vs queue).

---

### T-016: Write KV-update test (RED)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01..02 | **Status**: [ ] not started

**Description**: Mock `getCloudflareContext().env.SEARCH_CACHE_KV.put`. Stub `ctx.waitUntil`. Assert that publishing a submission causes one KV `put` call with the new skill's shard key.

---

### T-017: Implement KV update path (GREEN)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01..02, AC-US4-05 | **Status**: [ ] not started

**Description**: In `publish.ts` PUBLISHED transition, after submission update, call (via `ctx.waitUntil` from `@opennextjs/cloudflare`):
```typescript
ctx.waitUntil((async () => {
  try { await updateKvShardForSkill(skill); }
  catch (err) { console.warn("kv_reindex_failed:", { id: submission.id, err: String(err) }); }
})());
```
The `updateKvShardForSkill` helper lives in `src/lib/search-index/` (extend existing or create). It writes the sharded KV entry that `searchSkillsEdge` reads.

---

### T-018: Run vitest for publish + search-index (GREEN)
**User Story**: US-004 | **Satisfies ACs**: regression guard | **Status**: [ ] not started

**Description**: `npx vitest run src/lib/submission/ src/lib/search-index/ src/lib/__tests__/` — all green.

---

### T-019: Deploy + smoke for auto-reindex (VERIFY)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] not started

**Description**: Deploy. Submit a test skill (e.g., from a sandbox repo) → wait 60s → query `/api/v1/skills/search?q=<unique-test-string>` → confirm test skill appears. If it doesn't, the queue/waitUntil path failed — diagnose and fix. Capture in `reports/phase4-smoke.log`.

---

## Phase 5: Closure

### T-020: Full vitest suite green (regression check)
**User Story**: all | **Satisfies ACs**: regression guard | **Status**: [ ] not started

**Description**: `npx vitest run` from `vskill-platform/`. Confirm no NEW failures attributable to 0755 (the 13 pre-existing unrelated failures owned by 0690 are still acceptable).

---

### T-021: Sync, close, commit
**User Story**: all | **Satisfies ACs**: closure | **Status**: [ ] not started

**Description**: Mark all tasks complete in tasks.md, all ACs in spec.md (auto-checked by sync hook). Run `specweave sync-living-docs 0755-...` and the standard sw:done pipeline (code-review, simplify, grill, judge-llm, validate). Commit only the umbrella's `.specweave/increments/0755-...` artifacts plus the vskill-platform source/test commits in vskill-platform. Match the closure pattern from 0754.

---

## Summary

- **Tasks**: 21 across 5 phases
- **User-visible impact**: phase 1 (ranking) is the user's actual pain — the rest are quality improvements
- **Risk**: medium — phase 4 has the highest blast radius (publish path); phases 1-3 are isolated
- **Stoppable**: each phase has its own deploy gate; we can stop after any phase if a problem appears
