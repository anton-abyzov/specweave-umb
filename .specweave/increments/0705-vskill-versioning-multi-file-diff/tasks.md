---
increment: 0705-vskill-versioning-multi-file-diff
title: "Fix vskill versioning pipeline + GitHub-backed multi-file diff"
---

# Tasks: Fix vskill versioning pipeline + GitHub-backed multi-file diff

Legend: ACs link each task back to user stories. Tests follow BDD (Given/When/Then). TDD: write the failing test first (T-NN-RED), then implement, then refactor.

## Phase A — Unblock republish (US-001)

### T-001: Route `POST /api/v1/submissions` through upsertSubmission, not raw create()
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts:717-807`
**Test Plan**:
- Given a `PUBLISHED` skill (`repoUrl="https://github.com/a/b"`, `skillName="x"`) already in the DB
- When a second `POST /api/v1/submissions` arrives for the same `(repoUrl, skillName)`
- Then response is NOT 500; response JSON does NOT include string `"Unique constraint failed"`; response matches the existing `upsertSubmission` shape (`{kind:"verified"|"requeued"|"pending"|"blocked"|"rejected", …}`)

### T-002: Harden upsertSubmission — re-enqueue on contentHash change for PUBLISHED
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/upsert.ts:101-120`
**Test Plan**:
- Given a `PUBLISHED` skill with latest `SkillVersion.contentHash = hashA`
- When `upsertSubmission` runs with a new submission whose fetched SKILL.md hashes to `hashB != hashA`
- Then `Submission.state` is set to `RECEIVED`, `SUBMISSION_QUEUE.send` is called, and `upsertSubmission` returns `{kind:"requeued", submissionId}`
- And given the same situation where fetched hash equals `hashA`, upsertSubmission returns `{kind:"verified"}` WITHOUT re-enqueueing

### T-003: Populate `manifest` on SkillVersion.create in publishSkill
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts:337-356`
**Test Plan**:
- Given `treeFiles = { "SKILL.md": "content-a", "scripts/install.sh": "content-b" }`
- When `publishSkill` creates a new SkillVersion row
- Then the created row has `manifest` populated as `[{path:"SKILL.md", sha256: sha256("content-a"), size:9}, {path:"scripts/install.sh", sha256: sha256("content-b"), size:9}]`
- And given the old test with no manifest regression, existing fields (`content`, `contentHash`, `treeHash`, `version`) still produce identical values

### T-004: Replace buildDiffSummary with manifest-aware per-file summary
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts:32-45`
**Test Plan**:
- Given oldManifest has `{a.md: hash1, b.sh: hash2}` and newManifest has `{a.md: hash1, b.sh: hash2-new, c.md: hash3}`
- When `buildDiffSummary(oldManifest, newManifest)` runs
- Then it returns `"+1 new, ~1 modified"` (not the old line-count string)
- And given no change between manifests, it returns `"no file changes"`

## Phase B — Stop ghost rows (US-002)

### T-005: admin rescan-published — skip row creation when contentHash unchanged
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts`
**Test Plan**:
- Given a skill with latest `SkillVersion.contentHash = "aaa"`
- When admin rescan runs and the refetched content also hashes to `"aaa"`
- Then no new SkillVersion row is inserted; the existing latest row is updated in place with new `certTier`/`certScore`/`certifiedAt`
- And given refetched content hashes to a different value `"bbb"`, a NEW row is created with ALL fields populated (`content`, `contentHash`, `gitSha`, `manifest` all non-empty)

### T-006: Backfill script — scripts/backfill-skill-version-ghosts.ts
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/scripts/backfill-skill-version-ghosts.ts` (NEW); `package.json` (add npm script)
**Test Plan**:
- Given a test DB with (a) row `content=""` + `gitSha="abc123"` on a GitHub repo, (b) row `content=""` + `gitSha=""` with sibling row having matching cert metadata, (c) row `content=""` + `gitSha=""` with no sibling
- When running the script with `--dry-run`
- Then stdout reports: repopulate (a), delete (b), flag (c) — and DB is unchanged
- And when running with `--apply`, the three actions are performed; (a) row now has content/contentHash/manifest populated, (b) row is deleted, (c) is logged to `to-review.log`

## Phase C — Compare endpoint (US-003, US-005)

### T-007: src/lib/github/compare.ts — githubCompare() with KV cache + isValidSha + filterBySkillPath
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/github/compare.ts` (NEW)
**Test Plan**:
- Given valid SHAs and a mocked successful GitHub 200 response with 5 files
- When `githubCompare` runs with a KV mock
- Then the function returns the parsed body, `KV.put(cacheKey, ..., {expirationTtl:300})` was called; a second call hits cache and does NOT call fetch
- And given `isValidSha("not-a-sha")` returns false; `isValidSha("4f2285d")` returns true; `filterBySkillPath(files, "plugins/x/SKILL.md")` returns only files under `plugins/x/`

### T-008: New route GET /api/v1/skills/[o]/[r]/[s]/versions/compare
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/compare/route.ts` (NEW)
**Test Plan**:
- Given both versions have valid gitSha and the repo is on GitHub (with a mocked GitHub 200)
- When `GET /versions/compare?from=X&to=Y` is called
- Then response is `{source:"github", baseSha, headSha, files:[…], githubCompareUrl}` and `githubCompareUrl.startsWith("https://github.com/")`
- And given one version has empty gitSha, response is `{source:"local-content", files:[{filename:"SKILL.md", …}]}`
- And given GitHub returns 429, response falls back to `source:"local-content"` with no 5xx

### T-009: Version detail route exposes manifest/treeHash/gitSha
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/[version]/route.ts:25-41`
**Test Plan**:
- Given a SkillVersion row with `manifest` set to JSON `[{path:"SKILL.md", sha256:"a", size:10}]`, `treeHash:"t1"`, `gitSha:"abc123"`
- When `GET /versions/1.0.0`
- Then response contains `manifest: [{path:"SKILL.md", sha256:"a", size:10}]` (parsed, not stringified), `treeHash:"t1"`, `gitSha:"abc123"`
- And given a legacy row where `manifest = null`, response has `manifest: null` (not `[]`)

## Phase D — Compare UI (US-003)

### T-010: src/lib/diff/parse-unified-patch.ts — parseUnifiedPatch()
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/diff/parse-unified-patch.ts` (NEW)
**Test Plan**:
- Given a GitHub-style patch string `"@@ -1,2 +1,3 @@\n line1\n-line2\n+line2a\n+line3"`
- When `parseUnifiedPatch(patch)` runs
- Then output is `[{type:"same",content:"line1",oldNum:1,newNum:1}, {type:"remove",content:"line2",oldNum:2}, {type:"add",content:"line2a",newNum:2}, {type:"add",content:"line3",newNum:3}]`

### T-011: Update versions/compare/page.tsx — file tree + per-file renderer + fallback banner + GitHub link
**User Story**: US-003 | **AC**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/versions/compare/page.tsx`
**Test Plan**:
- Given the compare endpoint returns `source:"github"` with 3 files
- When the page mounts
- Then a file tree shows 3 entries with `+N/-M` badges; clicking a file renders its parseUnifiedPatch output in UnifiedDiff; "View on GitHub" link is visible with the correct URL
- And given `source:"local-content"`, the page shows the "Showing SKILL.md diff only" banner and no GitHub link

### T-012: Integration test — scout 4f2285d...71a9132 golden case
**User Story**: US-003 | **AC**: AC-US3-06 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/tests/integration/versions-compare-github.test.ts` (NEW); `repositories/anton-abyzov/vskill-platform/tests/fixtures/github-compare-scout-4f2285d-71a9132.json` (NEW)
**Test Plan**:
- Given a fixture recorded from the live `GET /repos/anton-abyzov/vskill/compare/4f2285d...71a9132` filtered to files under `plugins/skills/skills/scout/`
- When `GET /api/v1/skills/anton-abyzov/vskill/scout/versions/compare?from=4f2285d&to=71a9132` runs with fetch mocked to the fixture
- Then response has `files.length === 4`, `files.some(f => f.filename.endsWith("SKILL.md"))`, total additions sum to 590 and deletions sum to 8, at least one patch contains the substring `"Skill Discovery"`

## Phase E — CLI (US-004)

### T-013: vskill/src/api/client.ts — compareVersions() helper
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/api/client.ts`
**Test Plan**:
- Given a mocked fetch returning 200 with `{source,files,githubCompareUrl}`
- When `compareVersions("owner/repo/skill", "1.0.0", "1.0.1")` is called
- Then fetch is called with URL `https://verified-skill.com/api/v1/skills/owner/repo/skill/versions/compare?from=1.0.0&to=1.0.1` and the parsed body is returned

### T-014: vskill/src/commands/diff.ts — command implementation (color/--stat/--json/--files)
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/commands/diff.ts` (NEW)
**Test Plan**:
- Given compareVersions is mocked to return 2 files
- When `diffCommand("skill", "1.0.0", "1.0.1", {})` runs with TTY=true
- Then stdout contains ANSI color codes (`\x1b[32m`, `\x1b[31m`) and both file patches
- And given `{stat:true}`, stdout contains exactly 2+1 lines (`filename +N -M` × 2 + total line) and no patch bodies
- And given `{json:true}`, stdout is valid JSON containing `source` and `files`
- And given `{files:"scripts/**"}`, only files matching the glob appear in stdout

### T-015: vskill/src/index.ts — register diff command in commander
**User Story**: US-004 | **AC**: AC-US4-06 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/index.ts`
**Test Plan**:
- Given the CLI binary
- When `vskill diff --help` is invoked
- Then exit code is 0 and stdout lists `--stat`, `--json`, `--files`

### T-016: CI job — windows-latest runner verifies vskill diff on Windows
**User Story**: US-004 | **AC**: AC-US4-05 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/.github/workflows/ci.yml`
**Test Plan**:
- Given a GitHub Actions matrix job on `windows-latest`
- When it runs `npx vskill diff anton-abyzov/vskill/scout 1.0.0 1.0.1 --json`
- Then exit code is 0 and stdout is valid JSON
- And given `vskill diff --help`, exit code is 0

## Phase F — Deployment & Verification

### T-017: wrangler.jsonc — GITHUB_TOKEN secret binding + KV cache binding reuse
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/wrangler.jsonc`
**Test Plan**:
- Given `wrangler secret put GITHUB_TOKEN` has been run in the target environment
- When the compare endpoint runs
- Then `env.GITHUB_TOKEN` is non-empty at runtime (verified via e2e smoke test hitting the endpoint in a staging CF environment)

### T-018: End-to-end smoke — publish a test skill change and verify new version visible
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill-platform/tests/e2e/republish-smoke.spec.ts` (NEW)
**Test Plan**:
- Given a seeded test skill in `PUBLISHED` state with SkillVersion v1.0.0
- When a POST /api/v1/submissions arrives with a new commit SHA whose SKILL.md content differs
- Then after the queue consumer processes it, `SELECT * FROM SkillVersion WHERE skillId=...` returns 2 rows (v1.0.0 unchanged, new v1.0.1 with `content != ""`, `contentHash != ""`, `gitSha != ""`, `manifest != null`)

### T-019: Backfill run in staging — dry-run review + apply
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Files**: operations runbook (output of backfill dry-run)
**Test Plan**:
- Given the backfill script with `--dry-run` is run against staging
- When the operator reviews the proposed actions log
- Then the log is signed off (manual gate); `--apply` is then run; post-apply query `SELECT COUNT(*) FROM SkillVersion WHERE content='' AND gitSha!=''` returns 0

### T-020: Documentation — README sections for `vskill diff` + /versions/compare
**User Story**: US-004 | **AC**: AC-US4-06 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/README.md`; `repositories/anton-abyzov/vskill-platform/README.md`
**Test Plan**:
- Given the updated READMEs
- When a user reads the "Compare skill versions" section
- Then it includes (a) the `vskill diff` usage block with all flags, (b) the API endpoint path + response shape, (c) a note about Windows support

## Execution notes

- Tasks 1–4 are the critical hotfix bundle (Phase A) — prioritize; can ship before the rest.
- Tasks 5–6 are the ghost-row cleanup (Phase B). T-006 runs against staging first.
- Tasks 7–12 add the compare endpoint + UI. Golden test (T-012) must be green before UI ships.
- Tasks 13–16 add the CLI. T-016 (Windows CI) is the blocker for AC-US4-05.
- Tasks 17–20 are deployment/docs glue.
- Total: **20 tasks**, est. 2–3 days per phase (10 effective dev days for a single engineer; parallelizable 2–3x with multiple).
