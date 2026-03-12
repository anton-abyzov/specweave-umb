---
increment: 0507-vskill-update-all-sources
generated_by: sw:test-aware-planner
tdd_mode: true
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005, T-006]
  US-002: [T-003, T-004, T-005, T-006]
  US-003: [T-003, T-004, T-005, T-006]
  US-004: [T-005, T-006]
  US-005: [T-003, T-004]
---

# Tasks: vskill update — unified skill update across all source types

---

## User Story: US-001 — Source-Aware Update Routing

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Tasks**: 6 total, 0 completed

---

### T-001: Write failing tests for source-resolver.ts

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- **Given** a lockfile `source` string in any recognized or unrecognized format
- **When** `parseSource(source)` is called
- **Then** it returns a typed discriminated union with the correct `type` and parsed fields

**Test Cases**:
1. **Unit**: `src/resolvers/source-resolver.test.ts`
   - `parsesRegistrySource()`: `"registry:sw"` → `{ type: "registry", skillName: "sw" }`
   - `parsesGithubFlatSource()`: `"github:owner/repo"` → `{ type: "github", owner: "owner", repo: "repo" }`
   - `parsesGithubPluginSource()`: `"github:owner/repo#plugin:name"` → `{ type: "github-plugin", owner, repo, pluginName: "name" }`
   - `parsesMarketplaceSource()`: `"marketplace:owner/repo#name"` → `{ type: "marketplace", owner, repo, pluginName: "name" }`
   - `parsesLocalSource()`: `"local:specweave"` → `{ type: "local", baseName: "specweave" }`
   - `parsesEmptyStringAsUnknown()`: `""` → `{ type: "unknown", raw: "" }`
   - `parsesUnrecognizedPrefixAsUnknown()`: `"ftp:something"` → `{ type: "unknown", raw: "ftp:something" }`
   - `parsesGithubWithoutSlashAsUnknown()`: `"github:noslash"` → `{ type: "unknown", raw: "github:noslash" }`
   - `parsesMarketplaceWithoutHashAsUnknown()`: `"marketplace:owner/repo"` → `{ type: "unknown", raw: "marketplace:owner/repo" }`
   - `parsesRegistryWithSlashInName()`: `"registry:owner/skill"` → `{ type: "registry", skillName: "owner/skill" }`
   - **Coverage Target**: 95% (pure logic, no I/O)

**Implementation**:
1. Create `src/resolvers/source-resolver.test.ts` with all test cases above
2. Import `parseSource` from `./source-resolver.js` (file does not exist yet — tests will fail RED)
3. Run `npx vitest run src/resolvers/source-resolver.test.ts` — confirm all tests fail RED

---

### T-002: Implement src/resolvers/source-resolver.ts to pass tests

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- **Given** the failing tests from T-001 exist
- **When** `src/resolvers/source-resolver.ts` is created with `parseSource()` implementation
- **Then** all 10 tests in `source-resolver.test.ts` pass GREEN

**Test Cases**:
1. **Unit** (same file as T-001): `src/resolvers/source-resolver.test.ts`
   - All 10 cases from T-001 must pass after implementation
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/resolvers/source-resolver.ts` with exported `ParsedSource` discriminated union type:
   - `{ type: "registry"; skillName: string }`
   - `{ type: "github"; owner: string; repo: string }`
   - `{ type: "github-plugin"; owner: string; repo: string; pluginName: string }`
   - `{ type: "marketplace"; owner: string; repo: string; pluginName: string }`
   - `{ type: "local"; baseName: string }`
   - `{ type: "unknown"; raw: string }`
2. Implement `parseSource(source: string): ParsedSource` with this priority order:
   - `"registry:"` prefix → `{ type: "registry", skillName: rest }`
   - `"github:{owner}/{repo}#plugin:{name}"` → `{ type: "github-plugin", owner, repo, pluginName }`
   - `"github:{owner}/{repo}"` (must contain `/` after prefix) → `{ type: "github", owner, repo }`
   - `"marketplace:{owner}/{repo}#{name}"` → `{ type: "marketplace", owner, repo, pluginName }`
   - `"local:"` prefix → `{ type: "local", baseName: rest }`
   - anything else → `{ type: "unknown", raw: source }`
3. Export `ParsedSource` type and `parseSource` function
4. Run `npx vitest run src/resolvers/source-resolver.test.ts` — confirm all GREEN

---

## User Story: US-002 — SHA-Based Change Detection
## User Story: US-003 — Security Scanning on All Sources
## User Story: US-005 — Plugin Directory Full Update

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US5-01, AC-US5-02, AC-US5-03
**Tasks (shared phase)**: T-003, T-004

---

### T-003: Write failing tests for source-fetcher.ts

**User Story**: US-002, US-003, US-005 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Test Plan**:
- **Given** a `ParsedSource` value and a skill name
- **When** `fetchFromSource(parsed, skillName)` is called
- **Then** it calls the correct GitHub/registry/marketplace utility and returns `FetchResult | null`

**Test Cases**:
1. **Unit**: `src/updater/source-fetcher.test.ts`
   - `fetchesRegistrySource()`: `type: "registry"` → calls `getSkill()`, returns `FetchResult` with content + 12-char sha
   - `fetchesGithubFlatSource()`: `type: "github"` → calls `getDefaultBranch()` then `fetch()` for `skills/{skillName}/SKILL.md`, returns `FetchResult`
   - `githubFlatFallsBackToRootSkillMd()`: primary path 404 → retries root `SKILL.md`, returns content
   - `fetchesGithubPluginAllSkills()`: `type: "github-plugin"` → calls Trees API, fetches each `plugins/{name}/skills/*/SKILL.md` in parallel, returns combined content
   - `fetchesMarketplaceLikeGithubPlugin()`: `type: "marketplace"` → same strategy as `github-plugin`
   - `returnsNullForLocalSource()`: `type: "local"` → returns `null` without any fetch call
   - `returnsNullForUnknownSource()`: `type: "unknown"` → returns `null`
   - `shaIs12CharHex()`: returned `sha` field is exactly 12 lowercase hex characters (SHA-256 truncated)
   - `propagatesGithubTokenHeader()`: when `process.env.GITHUB_TOKEN = "tok"`, fetch calls include `Authorization: token tok`
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/updater/` directory
2. Create `src/updater/source-fetcher.test.ts` using `vi.hoisted()` for all mock variables (ESM hoisting requirement):
   - Mock `../api/client.js` (`getSkill`)
   - Mock `../discovery/github-tree.js` (`getDefaultBranch`)
   - Mock global `fetch` via `vi.stubGlobal("fetch", mockFetch)`
3. Import `fetchFromSource` from `./source-fetcher.js` (file does not exist — tests fail RED)
4. Run `npx vitest run src/updater/source-fetcher.test.ts` — confirm RED

---

### T-004: Implement src/updater/source-fetcher.ts to pass tests

**User Story**: US-002, US-003, US-005 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US2-01, AC-US3-04, AC-US4-04, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed

**Test Plan**:
- **Given** the failing tests from T-003 exist
- **When** `src/updater/source-fetcher.ts` is created with all fetch strategies
- **Then** all tests in `source-fetcher.test.ts` pass GREEN

**Test Cases**:
1. **Unit** (same file): `src/updater/source-fetcher.test.ts`
   - All 9 cases from T-003 must pass GREEN
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/updater/source-fetcher.ts` with:
   - `FetchResult` interface: `{ content: string; version: string; sha: string; tier: string }`
   - `fetchFromSource(parsed: ParsedSource, skillName: string): Promise<FetchResult | null>` async function
2. Per-type strategies:
   - `registry`: delegate to `getSkill(parsed.skillName)` from `../api/client.js`, compute sha from content
   - `github` (flat): `getDefaultBranch(owner, repo)` → `fetch` `raw.githubusercontent.com/{owner}/{repo}/{branch}/skills/{skillName}/SKILL.md`; on 404 fall back to root `SKILL.md`
   - `github-plugin` and `marketplace`: fetch Trees API → filter `plugins/{pluginName}/skills/*/SKILL.md` paths → fetch all in parallel → combined SHA = `createHash("sha256").update(sortedContents.join("")).digest("hex").slice(0, 12)`
   - `local`: log dim message `"{baseName}: managed by specweave refresh-plugins — skipping"`, return `null`
   - `unknown`: return `null`
3. SHA computation (single files): `createHash("sha256").update(content).digest("hex").slice(0, 12)`
4. `GITHUB_TOKEN` propagation: include `Authorization: token ${process.env.GITHUB_TOKEN}` header in all GitHub API/raw calls when env var is set
5. All imports use `.js` extensions (ESM `nodenext` requirement)
6. Run `npx vitest run src/updater/source-fetcher.test.ts` — confirm all GREEN

---

## User Story: US-004 — Graceful Failure Handling

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: T-005, T-006

---

### T-005: Add new test cases to src/commands/update.test.ts

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-02, AC-US1-06, AC-US1-07, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the existing `update.test.ts` with 3 passing tests
- **When** 8 new test cases are added that mock `fetchFromSource` and `parseSource`
- **Then** the new tests fail RED (because `update.ts` has not been wired up yet)

**Test Cases**:
1. **Integration**: `src/commands/update.test.ts` (extend existing file)
   - `routesGithubSourceToFetchFromSource()`: entry with `source: "github:owner/repo"` → `fetchFromSource` is called, `getSkill` is NOT called
   - `skipsLocalSourceWithoutWriting()`: `fetchFromSource` returns `null` for local source → no `mkdirSync` or `writeFileSync` called
   - `fallsBackToGetSkillForUnknownSource()`: `parseSource` returns `{ type: "unknown" }` → `getSkill()` called as fallback
   - `skipsUpdateWhenShaMatches()`: `fetchFromSource` returns sha matching lockfile entry → "already up to date" logged, no write
   - `printsOldAndNewShaOnUpdate()`: sha differs → console output contains `oldsha -> newsha` pattern
   - `continuesAfterSingleSkillFetchFailure()`: `fetchFromSource` throws for first skill, second skill still writes (loop continues)
   - `writesLockfileExactlyOnce()`: `mockWriteLockfile` called exactly 1 time after loop, regardless of failures
   - `summaryIncludesFailedSkillCount()`: final console output includes names of skills that failed
   - **Coverage Target**: 90%

**Implementation**:
1. Add `vi.hoisted()` mocks at the top of `update.test.ts` for:
   - `../updater/source-fetcher.js` (`fetchFromSource`)
   - `../resolvers/source-resolver.js` (`parseSource`)
2. Update the lockfile mock in `beforeEach` to include entries with `source: "github:owner/repo"` and `source: "local:specweave"` to exercise routing
3. Add 8 new `it()` blocks in the existing `describe("updateCommand")` block
4. New tests depend on wiring in `update.ts` (not done yet) → tests fail RED
5. Run `npx vitest run src/commands/update.test.ts` — confirm existing 3 GREEN, new 8 RED

---

### T-006: Modify src/commands/update.ts to use parseSource + fetchFromSource

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the 8 new test cases from T-005 fail RED
- **When** `src/commands/update.ts` is modified to import and use `parseSource` + `fetchFromSource`
- **Then** all 11 tests in `update.test.ts` pass GREEN (3 original + 8 new)

**Test Cases**:
1. **Integration** (same file): `src/commands/update.test.ts`
   - All 11 tests must pass GREEN
   - **Coverage Target**: 90%

**Implementation**:
1. Add imports to `update.ts`:
   - `import { parseSource } from "../resolvers/source-resolver.js";`
   - `import { fetchFromSource } from "../updater/source-fetcher.js";`
2. In the per-skill update loop, replace direct `getSkill()` call with:
   - `const parsed = parseSource(entry.source || "");`
   - `let result = await fetchFromSource(parsed, name);` (wrapped in try/catch)
   - On catch: print `yellow(`  ${name}: `) + dim(err.message)`, push to `failures[]`, `continue` (`AC-US4-01`, `AC-US4-02`)
   - If `result === null` and `parsed.type === "unknown"`: print dim warning, fall back to `getSkill(name)` (`AC-US1-07`)
   - If `result === null` and `parsed.type === "local"`: `continue` (already logged in fetcher) (`AC-US1-06`)
3. SHA comparison: `result.sha === entry.sha` → log "already up to date" (`AC-US2-01`, `AC-US2-02`)
4. When SHA differs: log `name: ${entry.sha?.slice(0,12)} -> ${result.sha}` (`AC-US2-03`)
5. Call `runTier1Scan(result.content)` and print verdict/score for every fetched skill (`AC-US3-01`, `AC-US3-03`)
6. On FAIL verdict: log red message and `continue` without writing (`AC-US3-02`)
7. After write: update `lock.skills[name].sha = result.sha` (`AC-US2-04`)
8. Declare `failures: string[] = []` before loop; after loop print summary with updated count + failed names (`AC-US4-05`)
9. `writeLockfile(lock)` remains called once after the loop (`AC-US4-03`)
10. Run `npx vitest run src/commands/update.test.ts` — all 11 GREEN
11. Run `npx vitest run` — full suite passes
