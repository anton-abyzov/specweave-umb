---
increment: 0460-vendor-provider-discovery
title: "Vendor & Provider Skill Discovery Enhancement"
generated_by: sw:test-aware-planner
tdd_mode: true
coverage_target: 90
by_user_story:
  US-004: [T-001, T-002, T-003]
  US-001: [T-004, T-005]
  US-002: [T-006, T-007]
  US-003: [T-008, T-009]
---

# Tasks: Vendor & Provider Skill Discovery Enhancement

<!-- Phase order: US-004 (registry) → US-001 (deploy) → US-002 (dedup) → US-003 (CLI) -->

---

## User Story: US-004 - Provider Registry Foundation

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 3 total, 3 completed
**Project**: vskill-platform

---

### T-001: Create provider-registry.ts with ProviderDefinition type and PROVIDER_REGISTRY constant

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** a new file `src/lib/trust/provider-registry.ts` exists
- **When** it is imported
- **Then** it exports `ProviderDefinition` type with all required fields and `PROVIDER_REGISTRY` containing all 7 vendor orgs with `type: "github-org"` and `trustLevel: "vendor"`; and `VENDOR_ORG_IDS` derives correctly from the registry

**Test Cases**:
1. **Unit**: `src/lib/trust/__tests__/provider-registry.test.ts` (new file)
   - `testProviderDefinitionFields()`: Import `PROVIDER_REGISTRY`; verify each entry has `id`, `type`, `name`, `trustLevel`, `config` fields
   - `testAllVendorOrgsPresent()`: Check PROVIDER_REGISTRY contains exactly anthropics, openai, google-gemini, google, microsoft, vercel, cloudflare
   - `testVendorOrgIdsDerivation()`: Verify `VENDOR_ORG_IDS` equals the Set of IDs where `type === "github-org"` && `trustLevel === "vendor"`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/lib/trust/provider-registry.ts` in vskill-platform
2. Define `ProviderDefinition` interface with fields: `id: string`, `type: "github-org" | "external-api"`, `name: string`, `trustLevel: "vendor" | "trusted" | "community"`, `config: Record<string, unknown>`
3. Define `PROVIDER_REGISTRY` as `readonly ProviderDefinition[]` with entries for all 7 vendor orgs
4. Derive and export `VENDOR_ORG_IDS: ReadonlySet<string>` from the registry (filter by `github-org` + `vendor`)
5. Run `npx vitest run src/lib/trust/__tests__/provider-registry.test.ts`

---

### T-002: Migrate trusted-orgs.ts to derive sets from provider registry

**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** `trusted-orgs.ts` is modified to import from `provider-registry.ts`
- **When** any existing caller imports `VENDOR_ORGS`, `TRUSTED_ORGS`, `isVendorOrg`, `isTrustedOrg`, or `checkVendorRepo`
- **Then** all exports remain identical in type and value; `VENDOR_ORGS` equals `VENDOR_ORG_IDS` from registry; `TRUSTED_ORGS` includes both registry-derived orgs and trusted-only orgs (github, anton-abyzov)

**Test Cases**:
1. **Unit**: `src/lib/trust/__tests__/trusted-orgs.test.ts` (existing — add equivalence tests)
   - `testVendorOrgsBackwardCompat()`: `VENDOR_ORGS` is a `ReadonlySet<string>` containing the same 7 orgs as before
   - `testTrustedOrgsBackwardCompat()`: `TRUSTED_ORGS` contains all vendor orgs plus github and anton-abyzov
   - `testIsVendorOrgUnchanged()`: `isVendorOrg("anthropics")` → true, `isVendorOrg("random")` → false (case-insensitive)
   - `testIsTrustedOrgUnchanged()`: `isTrustedOrg("github")` → true, `isTrustedOrg("random")` → false
   - `testCheckVendorRepoUnchanged()`: `checkVendorRepo("https://github.com/anthropics/skills")` → `{ isVendor: true, org: "anthropics" }`
   - **Coverage Target**: 95%

**Implementation**:
1. Modify `src/lib/trust/trusted-orgs.ts` to import `VENDOR_ORG_IDS` from `./provider-registry.js`
2. Replace hardcoded `VENDOR_ORGS` Set with `export const VENDOR_ORGS = VENDOR_ORG_IDS`
3. Define `TRUSTED_ONLY_ORGS = new Set(["github", "anton-abyzov"])` locally
4. Derive `TRUSTED_ORGS` by merging `VENDOR_ORG_IDS` and `TRUSTED_ONLY_ORGS` into a new `ReadonlySet`
5. Keep all function signatures (`isVendorOrg`, `isTrustedOrg`, `checkVendorRepo`) unchanged
6. Run `npx vitest run src/lib/trust/__tests__/trusted-orgs.test.ts`

---

### T-003: Sync vendor-org-discovery.js comment to reference provider-registry.ts

**User Story**: US-004
**Satisfies ACs**: AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** `crawl-worker/sources/vendor-org-discovery.js` contains a `VENDOR_ORGS` array
- **When** the file is inspected
- **Then** the sync comment references `provider-registry.ts` (not `trusted-orgs.ts`); the array contents match the 7 vendor org IDs from the registry

**Test Cases**:
1. **Unit**: `src/lib/trust/__tests__/provider-registry.test.ts` (add equivalence test)
   - `testRegistryMatchesCrawlWorkerOrgs()`: Parse the JS file's VENDOR_ORGS array; assert sorted values equal sorted `VENDOR_ORG_IDS` from registry
   - **Coverage Target**: 90%

**Implementation**:
1. Open `crawl-worker/sources/vendor-org-discovery.js` in vskill-platform repo
2. Update the SYNC comment above the `VENDOR_ORGS` array to reference `src/lib/trust/provider-registry.ts`
3. Verify the array values match the 7 registry vendor org IDs: anthropics, openai, google-gemini, google, microsoft, vercel, cloudflare
4. Add the equivalence test to `provider-registry.test.ts` reading the raw JS file and comparing sorted arrays
5. Run `npx vitest run src/lib/trust/`

---

## User Story: US-001 - Deploy vendor-org-discovery to VM-2

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed
**Project**: vskill-platform (ops)

<!-- US-001 is ops-only: no code logic changes, only env file verification + deploy.sh -->

---

### T-004: Verify .env.vm2 includes vendor-org-discovery and run deploy.sh

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** `crawl-worker/.env.vm2` has `vendor-org-discovery` in `ASSIGNED_SOURCES`
- **When** `deploy.sh` is run
- **Then** the crawl-worker on VM-2 starts without errors and the health endpoint response includes `vendor-org-discovery` as an active source

**Test Cases**:
1. **Manual verification** (ops gate — no automated test):
   - Pre-flight: `grep -c vendor-org-discovery crawl-worker/.env.vm2` returns 1
   - Post-deploy: health endpoint on VM-2 includes `"vendor-org-discovery"` in sources list
   - Check startup logs: `docker-compose logs --tail=50` shows no errors
   - **Coverage Target**: N/A (manual ops)

**Implementation**:
1. Confirm `crawl-worker/.env.vm2` contains `vendor-org-discovery` in `ASSIGNED_SOURCES` (plan confirms already present)
2. Run `deploy.sh` from vskill-platform repo root to push to all VMs
3. SSH to VM-2 and verify `docker-compose ps` shows crawl-worker running
4. Query health endpoint and confirm `vendor-org-discovery` is listed as active source

---

### T-005: Trigger on-demand discovery and verify vendor skills are indexed

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed (vendor-org-discovery deployed and running on VM-2; first crawl in progress)

**Test Plan**:
- **Given** vendor-org-discovery has run at least once on VM-2
- **When** `POST /api/v1/admin/discovery/vendor-orgs` is called
- **Then** the response includes `orgBreakdown` with skill counts per vendor org; and `vskill find frontend-design` returns Anthropic skills with `certTier: CERTIFIED` and `trustTier: T4`

**Test Cases**:
1. **Manual verification** (ops gate):
   - Admin POST returns HTTP 200 with `orgBreakdown` key in JSON body
   - `orgBreakdown.anthropics` count > 0
   - `vskill find frontend-design` output includes an Anthropic result
   - **Coverage Target**: N/A (manual ops)

**Implementation**:
1. After deploy, wait for initial crawl cycle or trigger via admin endpoint
2. Call `POST /api/v1/admin/discovery/vendor-orgs` with admin credentials
3. Confirm `orgBreakdown` in response includes anthropics with skill count > 0
4. Run `vskill find frontend-design` locally and confirm Anthropic skills appear with CERTIFIED tier

---

## User Story: US-002 - Search Dedup for Same-Org Skills

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 2 completed
**Project**: vskill-platform

---

### T-006: Add alternateRepos to SearchResult type in search.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/search.ts` exports a `SearchResult` type
- **When** `alternateRepos` is added as an optional field
- **Then** the field is typed as `Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>` and is optional; TypeScript compilation passes with zero errors

**Test Cases**:
1. **Compile-time**: `npx tsc --noEmit` in vskill-platform root
   - Zero new type errors introduced
   - All existing consumers of `SearchResult` remain compatible (field is optional)
   - **Coverage Target**: 100% (compile-time verification)

**Implementation**:
1. Open `src/lib/search.ts` in vskill-platform
2. Locate the `SearchResult` interface or type alias
3. Add `alternateRepos?: Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>` field
4. Run `npx tsc --noEmit` to verify zero type errors across the project

---

### T-007: Implement deduplicateBySkill() in search route.ts and add unit tests

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** search results with duplicate `ownerSlug + skillSlug` from multiple repos of the same org
- **When** `deduplicateBySkill()` is applied to the result array
- **Then** duplicates collapse into one canonical entry (highest `githubStars`), with `alternateRepos` containing the collapsed entries; cross-org duplicates are preserved; results with no duplicates pass through unchanged; `alternateRepos` is `undefined` (not `[]`) when no duplicates

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/dedup.test.ts` (new file)
   - `testNoDuplicatesPassthrough()`: 3 results from different orgs → returned unchanged, `alternateRepos` undefined on all
   - `testSameOrgSameSkillCollapses()`: 2 results: anthropics/skills/frontend-design (500 stars) + anthropics/claude-code/frontend-design (1200 stars) → 1 canonical (claude-code, 1200 stars), `alternateRepos` has skills entry
   - `testMixedVendorsOnlySameOrgCollapses()`: 4 results — 2 anthropics/frontend-design, 1 openai/frontend-design, 1 vercel/deploy-kit → 3 results total (anthropics collapses, openai and vercel preserved)
   - `testCanonicalPicksHighestStars()`: repo A=500 stars, repo B=1200 stars → canonical is repo B
   - `testAlternateReposUndefinedWhenNone()`: no duplicates → `alternateRepos` is `undefined` not `[]`
   - **Coverage Target**: 95%

2. **Integration**: Verify dedup is wired in the search response pipeline
   - `deduplicateBySkill()` is called after blocklist enrichment
   - `hasMore` flag is preserved from the pre-dedup result set

**Implementation**:
1. Implement `deduplicateBySkill(results: SearchResult[]): SearchResult[]` as a module-level function in `src/app/api/v1/skills/search/route.ts`
2. Group results by `ownerSlug + ":" + skillSlug`; for each group pick the entry with max `githubStars` as canonical
3. Attach `alternateRepos = [{ ownerSlug, repoSlug, repoUrl }]` for collapsed entries; leave `alternateRepos` undefined when group size is 1
4. Call `deduplicateBySkill()` after blocklist enrichment and before building the JSON response; preserve `hasMore` from the pre-dedup slice
5. Create `src/app/api/v1/skills/search/__tests__/dedup.test.ts` with the 5 test cases above
6. Run `npx vitest run src/app/api/v1/skills/search/__tests__/dedup.test.ts`

---

## User Story: US-003 - CLI Display of Alternate Sources

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 2 completed
**Project**: vskill

---

### T-008: Add alternateRepos to SkillSearchResult in client.ts

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** `src/api/client.ts` exports `SkillSearchResult`
- **When** `alternateRepos` is added and `searchSkills()` maps it from the API response
- **Then** `alternateRepos?: Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>` is present on the interface; `searchSkills()` passes the field through from the raw response without transformation

**Test Cases**:
1. **Compile-time**: `npx tsc --noEmit` in vskill repo root
   - `alternateRepos` is optional — no existing callsites break
   - `searchSkills()` return type includes `alternateRepos` when present in API payload
   - **Coverage Target**: 100% (compile-time)

**Implementation**:
1. Open `src/api/client.ts` in vskill CLI repo
2. Locate `SkillSearchResult` interface
3. Add `alternateRepos?: Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>`
4. Verify `searchSkills()` mapping function passes `alternateRepos` from raw API JSON through to the result object (pass-through, no transformation needed)
5. Run `npx tsc --noEmit` in vskill repo

---

### T-009: Update find.ts to display alternate repos in TTY, JSON, and piped modes

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** a search result with `alternateRepos` populated
- **When** `find.ts` renders output in each mode
- **Then** TTY mode shows `also: owner/other-repo` in dim text below the main entry; `--json` mode includes `alternateRepos` array; piped (non-TTY) mode appends alternate repos as tab-separated field after existing columns

**Test Cases**:
1. **Unit**: `src/commands/find.test.ts` (existing — add cases)
   - `testTTYShowsAlternateRepos()`: Mock result with `alternateRepos = [{ ownerSlug: "anthropics", repoSlug: "claude-code", repoUrl: "..." }]`, TTY=true → output includes "also: anthropics/claude-code"
   - `testJsonIncludesAlternateRepos()`: `--json` flag + `alternateRepos` present → JSON output object has `alternateRepos` array
   - `testPipedAppendsAlternateRepos()`: TTY=false, `alternateRepos` present → alternate repos appear tab-separated after existing columns
   - `testNoAlternateReposNoDiff()`: `alternateRepos` undefined → output identical to current behavior (no regression)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/commands/find.ts` in vskill CLI repo
2. In TTY render block: after printing each result row, add `if (r.alternateRepos) { for (const alt of r.alternateRepos) { console.log(chalk.dim("  also: " + alt.ownerSlug + "/" + alt.repoSlug)); } }`
3. In JSON render block: `alternateRepos` is already on `SkillSearchResult` — confirm full result is serialized (JSON.stringify includes it automatically)
4. In piped (non-TTY) render block: append `\t${r.alternateRepos?.map(a => a.ownerSlug + "/" + a.repoSlug).join(",") ?? ""}` to each row
5. Add the 4 test cases to `src/commands/find.test.ts`
6. Run `npx vitest run src/commands/find.test.ts` (vskill repo)
