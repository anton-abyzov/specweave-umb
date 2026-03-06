---
increment: 0440-fix-anthropic-skills-search
generated_by: sw:test-aware-planner
test_mode: TDD
coverage_target: 90
by_user_story:
  US-003: [T-001, T-002]
  US-001: [T-003, T-004]
  US-002: [T-005, T-006, T-007]
---

# Tasks: Fix Anthropic Skills Missing from Search

## User Story: US-003 - Sync VENDOR_ORGS Lists Across Codebase

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 0 completed

---

### T-001: Sync VENDOR_ORGS in crawl-worker/sources/vendor-org-discovery.js and crawl-worker/lib/vendor-detect.js

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `crawl-worker/sources/vendor-org-discovery.js` has VENDOR_ORGS with only 4 orgs (anthropics, openai, google-gemini, google)
- **When** the file is updated to add microsoft, vercel, cloudflare and a source-of-truth comment
- **Then** VENDOR_ORGS contains all 7 orgs and the comment references `src/lib/trust/trusted-orgs.ts`

- **Given** `crawl-worker/lib/vendor-detect.js` has TRUSTED_ORGS with only 4 orgs
- **When** the file is updated to add microsoft, vercel, cloudflare and a source-of-truth comment
- **Then** `isVendorRepo("https://github.com/microsoft/repo")` returns `{ isVendor: true, org: "microsoft" }`
- **And** `isVendorRepo("https://github.com/vercel/repo")` returns `{ isVendor: true, org: "vercel" }`
- **And** `isVendorRepo("https://github.com/cloudflare/repo")` returns `{ isVendor: true, org: "cloudflare" }`

**Test Cases**:
1. **Unit** (node:test): new file `crawl-worker/__tests__/vendor-detect.test.js`
   - `isVendorRepo_returnsTrue_forMicrosoft()`: assert isVendorRepo returns isVendor=true for microsoft URL
   - `isVendorRepo_returnsTrue_forVercel()`: assert true for vercel
   - `isVendorRepo_returnsTrue_forCloudflare()`: assert true for cloudflare
   - `isVendorRepo_returnsTrue_forOriginal4Orgs()`: regression — anthropics, openai, google-gemini, google still work
   - `isVendorRepo_returnsFalse_forUnknownOrg()`: assert false for random org
   - **Coverage Target**: 95%

2. **Unit** (node:test): `crawl-worker/__tests__/vendor-org-discovery.test.js`
   - New describe "TC-034: VENDOR_ORGS contains all 7 vendor orgs": mock microsoft org with a SKILL.md repo; verify it appears in orgBreakdown
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `crawl-worker/sources/vendor-org-discovery.js` line 20: replace `["anthropics", "openai", "google-gemini", "google"]` with `["anthropics", "openai", "google-gemini", "google", "microsoft", "vercel", "cloudflare"]`
2. Add comment above VENDOR_ORGS: `// Source of truth: src/lib/trust/trusted-orgs.ts — keep in sync manually`
3. Edit `crawl-worker/lib/vendor-detect.js` lines 6-8: replace TRUSTED_ORGS array with all 7 orgs
4. Add same source-of-truth comment above TRUSTED_ORGS in vendor-detect.js
5. Write `crawl-worker/__tests__/vendor-detect.test.js` with unit tests for all 7 orgs
6. Add TC-034 describe block to `crawl-worker/__tests__/vendor-org-discovery.test.js`
7. Run `node --test crawl-worker/__tests__/vendor-detect.test.js` to verify green

---

### T-002: Document post-deploy re-crawl step for AC-US3-04

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the VENDOR_ORGS lists have been updated and the crawl-worker is deployed to all 3 VMs
- **When** a manual vendor-org-discovery re-crawl is triggered on each VM
- **Then** previously filtered repos (e.g. anthropics/skill-creator with 0 stars) are submitted to the platform and appear in Postgres

**Test Cases**:
1. **Manual verification** (post-deploy): SSH into VMs and trigger vendor-org-discovery source; confirm new skills appear in Postgres search results on verified-skill.com
   - Not automated — manual gate per CLAUDE.md project rules

**Implementation**:
1. No code change needed for this task
2. After deploying crawl-worker (after T-001, T-003 are complete and deployed), trigger re-crawl: on each VM run the crawl-worker with vendor-org-discovery source enabled
3. Confirm anthropics/skill-creator (0-star) appears in search results on verified-skill.com

---

## User Story: US-001 - Remove Zero-Star Filter for Vendor Orgs

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

---

### T-003: Remove zero-star filter from crawl-worker/sources/vendor-org-discovery.js

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a vendor org (anthropics) has a public repo with 0 GitHub stars, fork=false, and a SKILL.md
- **When** vendor-org-discovery crawl runs
- **Then** the repo is included in discovery results (totalDiscovered increases) and its SKILL.md is submitted

- **Given** a vendor org repo with fork=true and any star count
- **When** vendor-org-discovery crawl runs
- **Then** the fork repo is still excluded (fork filter stays active)

- **Given** TC-031 existing test ("skips fork and zero-star repos") which asserts only 1 tree scan
- **When** the zero-star filter is removed
- **Then** TC-031 must be updated: zero-star-repo now gets tree-scanned, so treeRequests.length=2 and totalDiscovered=2

**Test Cases**:
1. **Unit** (node:test): `crawl-worker/__tests__/vendor-org-discovery.test.js`
   - New describe "TC-035: zero-star vendor repo is discovered": mock anthropics with 0-star non-fork repo that has SKILL.md; assert totalDiscovered=1 and treeRequests.length=1
   - Update TC-031: change assertion — treeRequests.length should be 2 (real-repo + zero-star-repo), totalDiscovered=2, fork still excluded (1 tree request maps to real-repo, 1 to zero-star-repo, fork=0)
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `crawl-worker/sources/vendor-org-discovery.js`: remove line 127 `if (item.stargazers_count === 0) continue;`
2. Update the JSDoc comment on `listOrgRepos()` from "Skips forks and zero-star repos." to "Skips forks only. Vendor orgs are trusted; star count is not a quality signal for them."
3. Update TC-031 test assertions in `crawl-worker/__tests__/vendor-org-discovery.test.js`
4. Add TC-035 test block to `crawl-worker/__tests__/vendor-org-discovery.test.js`
5. Run `node --test crawl-worker/__tests__/vendor-org-discovery.test.js` to verify all tests green

---

### T-004: Remove zero-star filter from src/lib/crawler/vendor-org-discovery.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** a vendor org repo with stargazers_count === 0 and fork === false
- **When** `listOrgRepos()` in `src/lib/crawler/vendor-org-discovery.ts` processes the GitHub API response
- **Then** the repo is added to the results array (not skipped)

- **Given** a vendor org repo with fork === true and 500 stars
- **When** `listOrgRepos()` processes it
- **Then** the repo is excluded (fork filter remains)

- **Given** a vendor org repo with stargazers_count > 0 and fork === false
- **When** `listOrgRepos()` processes it
- **Then** the repo is included (regression: existing behavior preserved)

**Test Cases**:
1. **Unit** (Vitest): new file `src/lib/crawler/vendor-org-discovery.test.ts`
   - Mock `fetch` globally via `vi.fn()` returning a Response with JSON array of repos
   - `listOrgRepos_includes_zeroStarNonForkRepo()`: mock returns [{fork:false, stargazers_count:0, name:"skill-creator", ...}]; assert result.length=1
   - `listOrgRepos_excludes_forkRepo()`: mock returns [{fork:true, stargazers_count:100, name:"forked", ...}]; assert result.length=0
   - `listOrgRepos_includes_highStarRepo()`: regression — mock returns [{fork:false, stargazers_count:500, name:"skill-x", ...}]; assert result.length=1
   - `listOrgRepos_paginates_correctly()`: first page returns PER_PAGE items, second page returns 0; assert all items collected
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/lib/crawler/vendor-org-discovery.ts` line 104: remove `if (item.stargazers_count === 0) continue;`
2. Update JSDoc comment on `listOrgRepos()` from "Skips forks and zero-star repos." to "Skips forks only. Vendor orgs are trusted; star count is not a quality signal for them."
3. Write `src/lib/crawler/vendor-org-discovery.test.ts` with unit tests using vi.fn() for fetch
4. Run `npx vitest run src/lib/crawler/vendor-org-discovery.test.ts` to verify green

---

## User Story: US-002 - Add CertTier Boost to Search Ranking

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 0 completed

---

### T-005: Add computeCertBonus() and update computeSearchRank() in src/lib/search.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05
**Status**: [ ] pending

**Test Plan**:
- **Given** a SearchIndexEntry with certTier="CERTIFIED"
- **When** `computeCertBonus(entry)` is called
- **Then** it returns 100

- **Given** a SearchIndexEntry with certTier="VERIFIED"
- **When** `computeCertBonus(entry)` is called
- **Then** it returns 20

- **Given** a SearchIndexEntry with certTier="UNVERIFIED" or any other string
- **When** `computeCertBonus(entry)` is called
- **Then** it returns 0

- **Given** a CERTIFIED skill with 0 GitHub stars and a VERIFIED skill with 500 stars, both matching query "skill-creator" with equal relevance (exact name match = 100)
- **When** `computeSearchRank()` is called for each with query ["skill-creator"]
- **Then** CERTIFIED rank = 100*0.5 + 0*0.3 + 100*0.2 = 70.0; VERIFIED rank = 100*0.5 + popularityOf500stars*0.3 + 20*0.2; since CERTIFIED rank=70 > VERIFIED rank (approx 50 + pop*0.3 + 4), CERTIFIED wins

- **Given** the existing `computePopularityScore()` function
- **When** tested with trustScore=80, githubStars=1000, npmDownloadsWeekly=500
- **Then** result equals 80*0.4 + log10(1001)/5*100*0.45 + log10(501)/6*100*0.15 (unchanged weights)

**Test Cases**:
1. **Unit** (Vitest): `src/lib/search.test.ts` — new describe block "computeCertBonus"
   - `computeCertBonus_returns100_forCertified()`: certTier="CERTIFIED" → 100
   - `computeCertBonus_returns20_forVerified()`: certTier="VERIFIED" → 20
   - `computeCertBonus_returns0_forUnverified()`: certTier="UNVERIFIED" → 0
   - `computeCertBonus_returns0_forUnknownTier()`: certTier="BLOCKED" → 0
   - **Coverage Target**: 95%

2. **Unit** (Vitest): `src/lib/search.test.ts` — new describe block "computeSearchRank certTier boost"
   - `certifiedZeroStars_outranks_verified500Stars_equalRelevance()`: numeric proof that CERTIFIED (0 stars) rank > VERIFIED (500 stars) rank at equal relevance=100
   - `computePopularityScore_weights_unchanged()`: regression — 40% trust, 45% stars, 15% downloads weights verified
   - **Coverage Target**: 90%

**Implementation**:
1. Add `export function computeCertBonus(entry: SearchIndexEntry): number` to `src/lib/search.ts` after `computePopularityScore`:
   ```ts
   export function computeCertBonus(entry: SearchIndexEntry): number {
     if (entry.certTier === "CERTIFIED") return 100;
     if (entry.certTier === "VERIFIED") return 20;
     return 0;
   }
   ```
2. Update `computeSearchRank()` body from `return relevance * 0.6 + popularity * 0.4;` to:
   ```ts
   const certBonus = computeCertBonus(entry);
   return relevance * 0.5 + popularity * 0.3 + certBonus * 0.2;
   ```
3. Update JSDoc on `computeSearchRank()`: change "relevance (60%) + popularity (40%)" to "relevance (50%) + popularity (30%) + certTier bonus (20%)"
4. Add `computeCertBonus` to the import line in `src/lib/search.test.ts`
5. Add new test cases to `src/lib/search.test.ts`
6. Run `npx vitest run src/lib/search.test.ts` to verify green (including all existing tests pass)

---

### T-006: Add certTier secondary sort to Postgres tsvector path in searchSkills()

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the tsvector query in `searchSkills()` currently has `ORDER BY rank DESC, "trustScore" DESC, "npmDownloadsWeekly" DESC`
- **When** the ORDER BY is updated to add certTier sort
- **Then** the SQL contains `ORDER BY rank DESC, CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC, "trustScore" DESC, "npmDownloadsWeekly" DESC`

- **Given** the mock $queryRaw returns a VERIFIED row before a CERTIFIED row (simulating DB without sort)
- **When** `searchSkills()` is called
- **Then** the ORDER BY embedded in the SQL call passed to $queryRaw includes the certTier CASE expression (verified by inspecting the mock call args)

**Test Cases**:
1. **Unit** (Vitest): `src/lib/search.test.ts` — new describe block "searchSkills tsvector certTier sort"
   - `tsvectorQuery_includes_certTier_orderBy()`: call searchSkills({query:"test"}), capture the Prisma.sql object passed to $queryRaw, convert to string and assert it contains `CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END`
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `src/lib/search.ts` tsvector ORDER BY on line 329:
   - Old: `ORDER BY rank DESC, "trustScore" DESC, "npmDownloadsWeekly" DESC`
   - New: `ORDER BY rank DESC, CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC, "trustScore" DESC, "npmDownloadsWeekly" DESC`
2. Add test in `src/lib/search.test.ts` for tsvector certTier ORDER BY (inspect mock call args via mockQueryRaw.mock.calls[0][0])
3. Run `npx vitest run src/lib/search.test.ts` to verify green

---

### T-007: Add certTier secondary sort to Postgres ILIKE fallback path in searchSkills()

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the ILIKE fallback query in `searchSkills()` currently has `ORDER BY "trustScore" DESC, "githubStars" DESC, "npmDownloadsWeekly" DESC`
- **When** the ORDER BY is updated to add certTier sort
- **Then** the SQL contains `ORDER BY CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC, "trustScore" DESC, "githubStars" DESC, "npmDownloadsWeekly" DESC`

- **Given** the tsvector query returns empty and ILIKE fallback triggers
- **When** the second $queryRaw call is made
- **Then** its SQL argument includes the certTier CASE expression as primary sort

**Test Cases**:
1. **Unit** (Vitest): `src/lib/search.test.ts` — new describe block "searchSkills ILIKE fallback certTier sort"
   - `ilikeFallback_includes_certTier_orderBy()`: mock first $queryRaw to return [] (triggers ILIKE); call searchSkills({query:"xyz"}); capture second $queryRaw call args; assert SQL contains `CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END`
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `src/lib/search.ts` ILIKE fallback ORDER BY on line 354:
   - Old: `ORDER BY "trustScore" DESC, "githubStars" DESC, "npmDownloadsWeekly" DESC`
   - New: `ORDER BY CASE WHEN "certTier" = 'CERTIFIED' THEN 0 ELSE 1 END ASC, "trustScore" DESC, "githubStars" DESC, "npmDownloadsWeekly" DESC`
2. Add test in `src/lib/search.test.ts` for ILIKE fallback certTier ORDER BY
3. Run `npx vitest run src/lib/search.test.ts` to verify all T-005, T-006, T-007 tests green
4. Run full Vitest suite: `cd repositories/anton-abyzov/vskill-platform && npx vitest run` to confirm no regressions
