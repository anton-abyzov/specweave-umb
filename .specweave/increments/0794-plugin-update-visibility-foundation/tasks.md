# Tasks — 0794 Plugin Update Visibility & Version Alignment Foundation

> Merge order: **vskill-platform** (US-002a) → **vskill** (US-002b, US-006) → **specweave** (US-001, US-003, US-004, US-005)

---

## Phase 1: vskill-platform — contentHash gate (BLOCKER for currency reporting)

### T-001: Extract canonicalContentHash helper
**User Story**: US-002a | **Satisfies ACs**: AC-US2a-01 | **Project**: vskill-platform
**Status**: [ ] pending

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/lib/integrity/canonical-hash.ts`
- Implement `canonicalContentHash(content: string): Promise<string>`:
  1. Normalize CRLF → LF
  2. Strip top-level `version:` line from frontmatter (regex, preserve nested `metadata.version`)
  3. Compute SHA-256 hex via `crypto.subtle` (match existing `trust/content-hash.ts:10-16`)
- Replace inline `createHash` at `submission/publish.ts:631` with the new helper
- Verify `check-updates/route.ts:111-347` uses the same normalization (refactor to import the helper if not)

**Test Plan**:
- File: `src/lib/integrity/__tests__/canonical-hash.test.ts`
- Given: content from `fixtures/no-frontmatter.md` → When: hashed twice → Then: same hex string
- Given: content from `fixtures/with-version.md` (`version: 1.0.0`) → When: hashed → Then: same hash as the same file with version stripped manually
- Given: content from `fixtures/version-quoted.md` → When: hashed → Then: version line stripped, hash stable
- Given: content from `fixtures/nested-metadata-version.md` → When: hashed → Then: nested `metadata.version` preserved (different hash from stripped variant)
- Given: content from `fixtures/crlf-line-endings.md` → When: hashed → Then: same hash as LF-only version

---

### T-002: Add contentHash gate to publish path
**User Story**: US-002a | **Satisfies ACs**: AC-US2a-02, AC-US2a-03, AC-US2a-04, AC-US2a-05 | **Project**: vskill-platform
**Status**: [x] completed
**Depends on**: T-001

**Implementation**:
- Locate actual publish surface: check `src/app/api/v1/skills/publish/route.ts` and `submission/publish.ts:417-428` (`contentUnchanged` logic)
- Add gate in `publishSkill()` (or the route handler if a direct endpoint exists):
  ```typescript
  const incoming = await canonicalContentHash(body.content);
  const latest = await db.skillVersion.findFirst({
    where: { skillId, namespace },
    orderBy: { createdAt: 'desc' },
    select: { contentHash: true, version: true },
  });
  if (latest && latest.contentHash === incoming) {
    return jsonResponse({ status: 'skipped', reason: 'no changes detected', version: latest.version });
  }
  ```
- Ensure rate-limit counter still consumed on `skipped` response (AC-US2a-04)
- No `SkillVersion` insert, no KV cache invalidation, no certTier bump on skip

**Test Plan**:
- File: `src/app/api/v1/skills/__tests__/publish-skip.test.ts`
- Given: identical payload POSTed twice → When: second request → Then: HTTP 200 `{ status: "skipped", reason: "no changes detected", version: "<v>" }` and no new `SkillVersion` DB row
- Given: payload with 1-char body change → When: second request → Then: new `SkillVersion` row inserted, `status: "published"` returned
- Given: first publish ever (no prior `SkillVersion`) → When: published → Then: always goes through full path (no false skip)
- DB invariant: `SELECT COUNT(*) FROM SkillVersion WHERE skillId=X GROUP BY contentHash` — no count > 1 per (skillId, namespace)

---

### T-003: Unit tests for canonical-hash parity (platform side)
**User Story**: US-002a | **Satisfies ACs**: AC-US2a-01 | **Project**: vskill-platform
**Status**: [x] completed
**Depends on**: T-001

**Implementation**:
- Add test fixture files under `src/lib/integrity/__tests__/fixtures/`
- Verify hash parity between `check-updates` path and `publish` path by calling `canonicalContentHash` with the same inputs and comparing results

**Test Plan**:
- Given: any of the 5 spec fixtures → When: hashed via `canonicalContentHash` from check-updates import path vs publish import path → Then: byte-identical hex strings (import the same module; this is a regression guard)

---

## Phase 2: vskill CLI — writeback + authored tracking

### T-004: Implement upsertFrontmatterVersion helper
**User Story**: US-002b | **Satisfies ACs**: AC-US2b-01, AC-US2b-03, AC-US2b-04 | **Project**: vskill
**Status**: [x] completed

**Implementation**:
- Create or extend `repositories/anton-abyzov/vskill/src/lib/frontmatter.ts`
- `upsertFrontmatterVersion(content: string, newVersion: string): string`:
  - Parse `^---\n([\s\S]*?)\n---\n` block
  - If `version:` line exists at top level → replace value (preserve quoting style from source)
  - Else if `description:` line → insert `version: ${newVersion}` immediately after it
  - Else → append at end of frontmatter block (before closing `---`)
  - Return full file string
- Verify: do NOT introduce a second YAML library (reuse `disk-version.ts:39-56` idiom)
- Include defensive round-trip check: `validatesAsYamlFrontmatter(result)` must pass (AC-US2b-04)

**Test Plan**:
- File: `src/lib/__tests__/frontmatter.test.ts`
- Given: SKILL.md with existing `version: 1.0.0` → When: `upsertFrontmatterVersion(content, "1.0.3")` → Then: version updated, all other fields byte-for-byte preserved, ordering unchanged
- Given: SKILL.md with no `version:` and has `description:` → When: upsert → Then: `version:` inserted on the line immediately after `description:`
- Given: SKILL.md with no `version:` and no `description:` → When: upsert → Then: `version:` appended before closing `---`
- Given: SKILL.md with quoted `version: "1.0.0"` → When: upsert → Then: output preserves quotes
- Given: a deliberately malformed YAML sequence → When: upsert → Then: `validatesAsYamlFrontmatter` returns false; function does not write

---

### T-005: Wire version writeback into submit.ts
**User Story**: US-002b | **Satisfies ACs**: AC-US2b-01, AC-US2b-02, AC-US2b-04, AC-US2b-05 | **Project**: vskill
**Status**: [x] completed
**Depends on**: T-004

**Implementation**:
- In `repositories/anton-abyzov/vskill/src/commands/submit.ts`, after `submitSkill()` returns:
  ```typescript
  if (response.status === 'skipped') {
    console.log(`No changes — version unchanged at ${response.version}`);
    return; // file untouched
  }
  // On 'published':
  const sourcePath = resolveSkillMdPath(opts);
  const before = await fs.readFile(sourcePath, 'utf8');
  const after = upsertFrontmatterVersion(before, response.version);
  if (!validatesAsYamlFrontmatter(after)) {
    console.error('Writeback would produce invalid YAML — aborting');
    process.exit(1);
  }
  await fs.writeFile(sourcePath, after, 'utf8');
  ```
- When `status: "skipped"`: print message, do NOT touch `mtime` of source file

**Test Plan**:
- File: `src/commands/__tests__/submit-writeback.test.ts`
- Given: mock registry returns `{ status: "published", version: "1.0.3" }` → When: submit runs → Then: source `SKILL.md` frontmatter `version:` is `1.0.3`; all other fields unchanged
- Given: mock registry returns `{ status: "skipped", version: "1.0.2" }` → When: submit runs → Then: source `SKILL.md` mtime unchanged (file not written); stdout contains "No changes"
- Integration: publish → read source SKILL.md → assert version field matches registry response

---

### T-006: Create authored.ts module and vskill.authored.json tracking
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-06 | **Project**: vskill
**Status**: [x] completed

**Implementation**:
- Create `repositories/anton-abyzov/vskill/src/lockfile/authored.ts`:
  - `addAuthoredSkill(name, sourcePath)` — appends to `vskill.authored.json` in project root
  - `removeAuthoredSkill(name)` — removes entry
  - `readAuthored()` — returns `Array<{ name, sourcePath, publishedAt }>`
  - File format: `{ "version": 1, "skills": { "<name>": { "sourcePath": "...", "publishedAt": "..." } } }`
- Call `addAuthoredSkill(name, sourcePath)` from `submit.ts` after successful writeback (T-005)
- Verify `vskill init` writes a `.gitignore` entry for `vskill.authored.json`; add it if missing (AC-US6-06)

**Test Plan**:
- File: `src/lockfile/__tests__/authored.test.ts`
- Given: fresh project dir → When: `addAuthoredSkill("owner/repo/skill", "skills/skill/SKILL.md")` → Then: `vskill.authored.json` created with correct shape
- Given: existing authored.json → When: same skill added again → Then: entry updated (no duplicates)
- Given: existing authored.json with two skills → When: `removeAuthoredSkill("owner/repo/skill")` → Then: only that entry removed
- Given: `readAuthored()` on missing file → Then: returns `[]` (no crash)

---

### T-007: Extend vskill outdated to poll authored skills
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05 | **Project**: vskill
**Status**: [x] completed
**Depends on**: T-006

**Implementation**:
- In `repositories/anton-abyzov/vskill/src/commands/outdated.ts`, after lockfile-driven items (lines 63-81):
  ```typescript
  const authored = readAuthored(getProjectRoot());
  for (const a of authored) {
    if (!existsSync(a.sourcePath)) {
      removeAuthoredSkill(a.name);
      console.error(`${a.name}: source path no longer exists, removed from tracking`);
      continue;
    }
    const v = readDiskVersion(a.sourcePath);
    if (!v) continue; // never published to registry — skip silently (AC-US6-05)
    items.push({ name: a.name, currentVersion: v, sha: undefined, kind: 'authored' });
  }
  ```
- Output: prefix `[authored]` for `kind='authored'` rows in text output (AC-US6-02)
- Up-to-date authored skill: no false positive (AC-US6-03)

**Test Plan**:
- File: `src/commands/__tests__/outdated-authored.test.ts`
- Given: `vskill.authored.json` with skill A at `version: 1.0.0`; registry at `1.0.0` → When: outdated runs → Then: skill A not listed as outdated, no `[authored]` in warn output
- Given: authored skill at `version: 1.0.0`; registry at `1.0.2` → When: outdated runs → Then: skill A listed with `[authored]` prefix, installed=1.0.0, available=1.0.2
- Given: authored skill whose source file no longer exists → When: outdated runs → Then: entry removed from `vskill.authored.json`, one-line stderr notice, no crash
- Given: authored skill with no published version in registry → When: outdated runs → Then: silently skipped (no warn, no error)

---

### T-008: Integration test — publish flow end-to-end (vskill side)
**User Story**: US-002b | **Satisfies ACs**: AC-US2b-05 | **Project**: vskill
**Status**: [ ] pending
**Depends on**: T-005, T-006, T-007

**Implementation**:
- Integration test that mocks the registry API and runs the full submit → writeback → outdated cycle

**Test Plan**:
- File: `src/commands/__tests__/submit-outdated-integration.test.ts`
- Given: source SKILL.md at version `1.0.0`, mock registry returns `published` with `1.0.3` → When: `vskill skill publish` → Then: source SKILL.md `version: 1.0.3`, `vskill.authored.json` has entry
- Given: immediately after above → When: `vskill outdated` (mock registry still at `1.0.3`) → Then: authored skill reported as up to date
- Given: mock registry bumped to `1.0.4` externally → When: `vskill outdated` → Then: authored skill flagged with `[authored]` prefix

---

## Phase 3: specweave — version lockstep (BLOCKER)

### T-009: Hotfix plugin.json version (one-shot commit)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- Read current version from `repositories/anton-abyzov/specweave/package.json`
- Write that version into `repositories/anton-abyzov/specweave/plugins/specweave/.claude-plugin/plugin.json`
- Commit message: `fix(plugin): align plugin.json version to package.json (0794 US-001)`
- This is a standalone commit — separate from script changes

**Test Plan**:
- Given: hotfix commit applied → When: `node -e "const a=require('./package.json').version; const b=require('./plugins/specweave/.claude-plugin/plugin.json').version; if(a!==b) process.exit(1)"` in specweave repo → Then: exit 0

---

### T-010: Extend bump-version.sh to update all three files atomically
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-009

**Implementation**:
- Extend `repositories/anton-abyzov/specweave/scripts/build/bump-version.sh` after the `npm version` line:
  ```bash
  node -e '
    const fs = require("fs");
    const v = require("./package.json").version;
    for (const p of ["plugins/specweave/.claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]) {
      const j = JSON.parse(fs.readFileSync(p, "utf8"));
      if (p.endsWith("plugin.json")) j.version = v;
      else { j.version = v; if (Array.isArray(j.plugins)) j.plugins.forEach(pl => { if (pl.name === "sw") pl.version = v; }); }
      fs.writeFileSync(p, JSON.stringify(j, null, 2) + "\n", "utf8");
    }
  '
  ```
- Existing `package.json` + CHANGELOG behavior is preserved unchanged

**Test Plan**:
- File: `tests/integration/bump-version.test.ts`
- Given: temp clone of the specweave repo at a known version → When: `./scripts/build/bump-version.sh patch` → Then: `package.json`, `marketplace.json` (root + sw entry), and `plugin.json` all have the same new SemVer string
- Given: re-run bump on already-bumped state → Then: no error, all four locations update again in lockstep

---

### T-011: Create validate-versions.cjs CI lint script
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- Create `repositories/anton-abyzov/specweave/scripts/validation/validate-versions.cjs`
- Reads and compares: `package.json.version`, `marketplace.json` root version, `marketplace.json plugins[sw].version`, `plugin.json.version`
- Exit 0: all four match
- Exit 1: drift — print unified-diff-style block naming offending file(s) and fix hint
- Exit 2: missing or malformed file
- Pattern: mirror `scripts/validation/validate-plugin-manifests.cjs` (no new deps, Node.js CJS)

**Test Plan**:
- File: `tests/unit/validate-versions.test.ts`
- Given: all four files with identical version → When: script runs → Then: exit 0
- Given: `plugin.json` at `1.0.0`, rest at `1.0.582` → When: script runs → Then: exit 1, output includes `plugin.json` labeled `← MISALIGNED`
- Given: `marketplace.json` sw entry differs from root → When: script runs → Then: exit 1, both locations called out
- Given: `plugin.json` file missing → When: script runs → Then: exit 2, lists missing path
- Given: `marketplace.json` malformed JSON → When: script runs → Then: exit 2

---

### T-012: Wire validate-versions.cjs into GitHub Actions CI
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-011

**Implementation**:
- Add `validate-versions` job to `repositories/anton-abyzov/specweave/.github/workflows/test.yml` (or new `validate-versions.yml`):
  ```yaml
  validate-versions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: node scripts/validation/validate-versions.cjs
  ```
- Mark job as required for merge to `main` via repo settings (note: branch protection config is a manual post-merge step)

**Test Plan**:
- Given: CI job added → When: drift PR pushed → Then: `validate-versions` job fails within 60s
- Given: aligned PR pushed → When: CI runs → Then: `validate-versions` job passes

---

## Phase 4: specweave — skill version stamps

### T-013: Create validate-skill-versions.cjs CI lint script
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- Create `repositories/anton-abyzov/specweave/scripts/validation/validate-skill-versions.cjs`
- Walks `plugins/specweave/skills/*/SKILL.md`
- For each file: parse frontmatter (use `gray-matter` if already a dep; else minimal regex); assert `version:` present and matches SemVer regex `^\d+\.\d+\.\d+(-[\w.-]+)?(\+[\w.-]+)?$`
- Exit 0: all pass; Exit 1: list offending paths one per line

**Test Plan**:
- File: `tests/unit/validate-skill-versions.test.ts`
- Given: SKILL.md with valid `version: 1.0.0` → Then: passes
- Given: SKILL.md with `version: 2.1.0-beta.1` (prerelease) → Then: passes
- Given: SKILL.md with `version: 2.1.0+build.42` (build metadata) → Then: passes
- Given: SKILL.md missing `version:` field → Then: fails, path listed
- Given: SKILL.md with `version: 20260427` (date) → Then: fails, path listed
- Given: SKILL.md with `version: ""` (empty) → Then: fails, path listed

---

### T-014: Stamp 47 SKILL.md files with version 1.0.0
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-013

**Implementation**:
- Create `repositories/anton-abyzov/specweave/scripts/build/stamp-skill-versions.sh` (idempotent):
  - For each `plugins/specweave/skills/*/SKILL.md`:
    - If valid `version:` present → skip, log `= skills/<name>/SKILL.md (already has version: <X>)`
    - Else → insert `version: 1.0.0` after `description:` (or end of frontmatter), log `+ skills/<name>/SKILL.md (added version: 1.0.0)`
- Run once; commit resulting 47-file diff with message referencing `0794 US-003`

**Test Plan**:
- Given: stamp script run on the 50 SKILL.md files → Then: exactly 47 files modified (those without `version:`), 3 untouched
- Given: stamp script run a second time → Then: zero files modified (idempotent, AC-US3-05)
- Given: `validate-skill-versions.cjs` run after stamp → Then: exit 0

---

### T-015: Wire validate-skill-versions.cjs into GitHub Actions CI
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-013

**Implementation**:
- Add step to `repositories/anton-abyzov/specweave/.github/workflows/skill-lint.yml`:
  ```yaml
  - name: Validate SKILL.md versions
    run: node scripts/validation/validate-skill-versions.cjs
  ```
- If `skill-lint.yml` uses `paths: plugins/specweave/skills/**`, this step fires on any skill edit

**Test Plan**:
- Given: a SKILL.md with `version:` removed pushed to PR → When: CI runs → Then: `validate-skill-versions` step fails

---

## Phase 5: specweave — doctor checkers (parallel after T-007)

### T-016: Implement PluginCurrencyChecker
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- Create `repositories/anton-abyzov/specweave/src/core/doctor/checkers/plugin-currency-checker.ts`
- Implements `HealthChecker` interface (clone structure from `installation-health-checker.ts:36-67`)
- Logic:
  1. Read `~/.claude/plugins/installed_plugins.json` → missing: return `skip`
  2. For each plugin, locate marketplace.json (local clone if present; fallback to raw GitHub URL)
  3. Cache marketplace.json at `~/.claude/specweave/cache/marketplace-{md5(url)}.json` with 5-min TTL
  4. Compare installed vs marketplace versions per plugin
  5. All current → `pass`; any outdated → `warn` with details + `fixSuggestion: "Run: specweave refresh-plugins"`
  6. Network/parse error → `warn { reason: "unable to verify" }` (NOT `fail`)
- JSON output: `pluginCurrency` key with `{ status, outdated: [{name, source, installed, available}], fixSuggestion? }`
- Register in `src/core/doctor/checkers/index.ts` and `doctor.ts`

**Test Plan**:
- File: `src/core/doctor/checkers/__tests__/plugin-currency-checker.test.ts`
- Given: installed_plugins.json missing → When: check() → Then: `{ status: "skip" }`
- Given: all plugins current (installed == marketplace) → When: check() → Then: `{ status: "pass" }`
- Given: one plugin outdated → When: check() → Then: `{ status: "warn", outdated: [{ name, installed, available }], fixSuggestion: "Run: specweave refresh-plugins" }`
- Given: marketplace.json malformed JSON → When: check() → Then: `{ status: "warn", reason: "unable to verify" }`
- Given: network error fetching marketplace → When: check() → Then: `{ status: "warn", reason: "unable to verify" }`; doctor continues to other checks
- Performance: warm-cache check() completes in ≤500ms

---

### T-017: Implement SkillCurrencyChecker
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- Create `repositories/anton-abyzov/specweave/src/core/doctor/checkers/skill-currency-checker.ts`
- Implements `HealthChecker` interface
- Logic:
  1. `which vskill` → missing: return `skip { reason: "vskill CLI not installed" }`
  2. Check `vskill.lock` in CWD → missing: return `skip`
  3. `execSync('vskill outdated --json', { timeout: 5000, cwd: projectRoot })`
  4. Parse JSON; exit 0 with `[]` → `pass`; outdated items → `warn` with list (max 10, truncated with `"… +N more"`)
  5. Timeout or non-JSON → `warn { reason: "unable to verify" }`, stderr captured (max 200 chars)
- JSON output: `skillCurrency` key mirroring `pluginCurrency` shape
- Register after `PluginCurrencyChecker` in `doctor.ts`

**Test Plan**:
- File: `src/core/doctor/checkers/__tests__/skill-currency-checker.test.ts`
- Given: `vskill` not on PATH → When: check() → Then: `{ status: "skip", reason: "vskill CLI not installed" }`
- Given: vskill on PATH, no `vskill.lock` in CWD → When: check() → Then: `{ status: "skip" }`
- Given: vskill on PATH, `vskill.lock` present, `vskill outdated --json` returns `[]` → When: check() → Then: `{ status: "pass" }`
- Given: `vskill outdated --json` returns list of 3 outdated skills → When: check() → Then: `{ status: "warn", outdated: [3 items] }` with `fixSuggestion: "Run: vskill update"`
- Given: `vskill outdated --json` returns list of 15 skills → When: check() → Then: output has max 10 lines + `"… +5 more"`
- Given: `vskill outdated --json` exits non-zero with garbage stderr → When: check() → Then: `{ status: "warn", reason: "unable to verify" }`, stderr truncated to 200 chars
- Performance: warm check() (cached vskill output) ≤500ms

---

### T-018: Integration test — specweave doctor with new checkers [completed]
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US5-01 | **Project**: specweave
**Status**: [ ] pending
**Depends on**: T-016, T-017

**Implementation**:
- Integration test using a tmp HOME with seeded `installed_plugins.json`
- Stub `vskill` binary on PATH via a shell wrapper script

**Test Plan**:
- File: `tests/integration/doctor-currency-checkers.test.ts`
- Given: tmp HOME with `installed_plugins.json` showing sw@1.0.0, marketplace at 1.0.582 → When: `specweave doctor` → Then: text output contains `Plugin Currency: warn`, lists `sw@specweave: installed=1.0.0, available=1.0.582`
- Given: `specweave doctor --json` → Then: JSON has `pluginCurrency.status === "warn"` and `skillCurrency` key present
- Given: no vskill on PATH → When: `specweave doctor` → Then: `Skill Currency: skip`, exit code unchanged (AC-US5-04)
- Performance: total doctor wall-clock overhead from new checkers ≤500ms warm, ≤2000ms cold

---

## Phase 6: Verification gates

### T-019: Version alignment diff gate (Bash verification)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-009, T-010, T-011

**Implementation**:
- Run `node scripts/validation/validate-versions.cjs` in the specweave repo and verify exit 0
- Assert all four version locations are byte-equal: `package.json`, `marketplace.json` root, `marketplace.json sw entry`, `plugin.json`

**Test Plan**:
- Given: hotfix and bump-version changes applied → When: `node scripts/validation/validate-versions.cjs` in specweave repo → Then: exit 0, no output
- Given: manually drift `plugin.json` to `0.0.1` → When: validator runs → Then: exit 1, error lists `plugin.json` as `← MISALIGNED`

---

### T-020: Skill version coverage gate (Bash verification)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-013, T-014

**Implementation**:
- Run `node scripts/validation/validate-skill-versions.cjs` in specweave repo after stamp is applied
- Assert exit 0 (all 50 SKILL.md files have valid SemVer `version:`)

**Test Plan**:
- Given: stamp script applied → When: `node scripts/validation/validate-skill-versions.cjs` → Then: exit 0
- Count check: confirm exactly 47 files were modified by the stamp script (diff shows 47 files)

---

### T-021: Manual verification gate — plugin update visibility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Project**: specweave
**Status**: [ ] pending
**Depends on**: T-009, T-010, T-012

**Implementation**:
- Publish a dot-release using the updated `bump-version.sh`
- Run `claude /plugin/list` — verify `sw@specweave` shows the new version or "update available" before refresh
- Run `claude /plugin/update sw@specweave` or `specweave refresh-plugins` — verify new version reflected

**Test Plan**:
- Given: a dot-release published with aligned `plugin.json` → When: `claude /plugin/list` → Then: `sw@specweave` version matches the new release (AC-US1-05)
- This is a manual gate per CLAUDE.md (new UI flow requires human verification)

---

### T-022: Manual verification gate — vskill phantom-bump eliminated
**User Story**: US-002a, US-002b | **Satisfies ACs**: AC-US2a-02, AC-US2b-02 | **Project**: vskill-platform
**Status**: [ ] pending
**Depends on**: T-002, T-005

**Implementation**:
- Run `vskill skill publish` twice on the same unchanged SKILL.md
- Second run must print "No changes — version unchanged at <X>" and source file must be byte-identical between runs

**Test Plan**:
- Given: source SKILL.md unchanged → When: `vskill skill publish` run a second time → Then: stdout includes "No changes — version unchanged at <X>"; `md5sum SKILL.md` before and after is identical
- This is a manual gate per CLAUDE.md

---

### T-023: Manual verification gate — specweave doctor fresh install
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Project**: specweave
**Status**: [ ] pending
**Depends on**: T-017

**Implementation**:
- Run `specweave doctor` on a machine (or subshell) where `vskill` is not on PATH
- Verify "Skill Currency" row shows `skip`, and `specweave doctor` exits 0

**Test Plan**:
- Given: PATH does not contain `vskill` → When: `specweave doctor` → Then: "Skill Currency: skip", process exits 0 (not 1)
- This is a manual gate per CLAUDE.md

---

## Task Summary

| Task | User Story | Project | Status |
|------|-----------|---------|--------|
| T-001: Extract canonicalContentHash | US-002a | vskill-platform | [ ] |
| T-002: Add contentHash gate to publish | US-002a | vskill-platform | [ ] |
| T-003: Unit tests hash parity | US-002a | vskill-platform | [ ] |
| T-004: upsertFrontmatterVersion helper | US-002b | vskill | [ ] |
| T-005: Wire version writeback into submit.ts | US-002b | vskill | [ ] |
| T-006: authored.ts + vskill.authored.json | US-006 | vskill | [ ] |
| T-007: Extend outdated to poll authored skills | US-006 | vskill | [ ] |
| T-008: Publish flow integration test | US-002b | vskill | [ ] |
| T-009: Hotfix plugin.json version | US-001 | specweave | [ ] |
| T-010: Extend bump-version.sh | US-001 | specweave | [ ] |
| T-011: validate-versions.cjs | US-001 | specweave | [ ] |
| T-012: Wire validate-versions into CI | US-001 | specweave | [ ] |
| T-013: validate-skill-versions.cjs | US-003 | specweave | [ ] |
| T-014: Stamp 47 SKILL.md files | US-003 | specweave | [ ] |
| T-015: Wire validate-skill-versions into CI | US-003 | specweave | [ ] |
| T-016: PluginCurrencyChecker | US-004 | specweave | [ ] |
| T-017: SkillCurrencyChecker | US-005 | specweave | [ ] |
| T-018: Doctor integration test | US-004, US-005 | specweave | [ ] |
| T-019: Version alignment diff gate | US-001 | specweave | [ ] |
| T-020: Skill version coverage gate | US-003 | specweave | [ ] |
| T-021: Manual gate — plugin update visibility | US-001 | specweave | [ ] |
| T-022: Manual gate — phantom-bump eliminated | US-002a, US-002b | vskill-platform | [ ] |
| T-023: Manual gate — doctor fresh install | US-005 | specweave | [ ] |
