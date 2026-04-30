# Tasks: Studio header parity — repo chip + GitHub link for Copied (independent) skills

## Task Notation

- `[T###]`: Task ID
- `[ ]` not started · `[x]` completed
- **AC**: links task to acceptance criteria for bidirectional traceability
- **Test Plan**: BDD Given/When/Then per task

---

## Phase 1: Foundation — extract resolver module + add sidecar reader

### T-001: Extract `resolveSourceLink` + helpers into `src/eval-server/source-link.ts`
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] Completed

**Description**: Move `resolveSourceLink`, `detectAuthoredSourceLink`, `parseGithubRemote`, the authored-source memo + reset hook, and any local-only helpers from `src/eval-server/api-routes.ts` (lines ~930-1070) into a new self-contained module `src/eval-server/source-link.ts`. `api-routes.ts` re-exports the public surface so existing imports keep working. `buildSkillMetadata` calls the resolver from the new module.

**Implementation Details**:
- New file: `src/eval-server/source-link.ts` with public exports `resolveSourceLink`, `detectAuthoredSourceLink`, `parseGithubRemote`, `resetAuthoredSourceLinkCache`.
- `src/eval-server/api-routes.ts`: replace inline definitions with `export { resolveSourceLink, detectAuthoredSourceLink, parseGithubRemote, resetAuthoredSourceLinkCache } from "./source-link.js";`. Update internal callers (`buildSkillMetadata` at ~line 1083) to import from the new module.
- Run `tsc --noEmit` after extraction to verify no circular imports.
- All existing 0737/0743/0770 tests must continue to pass without modification.

**Test Plan**:
- **File**: `src/eval-server/__tests__/skill-metadata-source-link.test.ts` (existing) + `src/eval-server/__tests__/authored-source-link.test.ts` (existing)
- **TC-001 (regression)**: Given the existing test suites for 0737/0743/0770, When the resolver code is moved to `source-link.ts`, Then all existing tests pass without changes to the test files themselves.

---

### T-002: Implement `readCopiedSkillSidecar(skillDir)` in `source-link.ts`
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-05 | **Status**: [x] Completed

**Description**: Add a new pure helper that reads `<skillDir>/.vskill-source.json`, validates the payload, and returns `{repoUrl, skillPath}` on success or `{null, null}` on any failure. Memoize per absolute `skillDir` for the eval-server lifetime; expose `resetCopiedSkillSidecarCache()` for tests.

**Implementation Details**:
- Add module-level `Map<string, {repoUrl: string|null; skillPath: string|null}>` cache.
- `readCopiedSkillSidecar(skillDir: string): {repoUrl, skillPath}`:
  1. Resolve absolute path.
  2. If cached, return cached.
  3. `existsSync(.vskill-source.json)` → no? cache + return `{null, null}`.
  4. `readFileSync` + `JSON.parse` inside try/catch → on throw, cache + return `{null, null}`.
  5. Validate `repoUrl` is a non-empty string matching `/^https:\/\/github\.com\/[A-Za-z0-9][A-Za-z0-9-]{0,38}\/[A-Za-z0-9._-]+$/`. Failure → cache + return `{null, null}`.
  6. Validate `skillPath` is `string | null | undefined`. Coerce undefined to null.
  7. Cache + return `{repoUrl, skillPath: skillPath ?? null}`.
- Export `resetCopiedSkillSidecarCache()` for test isolation.

**Test Plan**:
- **File**: `src/eval-server/__tests__/copied-source-link.test.ts` (NEW)
- **TC-002**: Given no `.vskill-source.json` in `skillDir`, When `readCopiedSkillSidecar` runs, Then it returns `{null, null}` and never throws.
- **TC-003**: Given `.vskill-source.json` with malformed JSON (e.g. `"not json{"`), When the reader runs, Then it returns `{null, null}`.
- **TC-004**: Given valid JSON missing the `repoUrl` field, When the reader runs, Then it returns `{null, null}`.
- **TC-005**: Given `repoUrl: "http://github.com/x/y"` (non-https), When the reader runs, Then it returns `{null, null}`.
- **TC-006**: Given `repoUrl: "https://gitlab.com/x/y"`, When the reader runs, Then it returns `{null, null}`.
- **TC-007**: Given `repoUrl: "https://github.com/anton-abyzov/greet-anton-test"` and `skillPath: "SKILL.md"`, When the reader runs, Then it returns the values verbatim.
- **TC-008**: Given a successful read, When `readCopiedSkillSidecar` is called twice for the same dir, Then `readFileSync` is invoked once (memoized).
- **TC-009**: Given memoized result, When `resetCopiedSkillSidecarCache()` is called, Then the next call re-reads from disk.

---

### T-003: Wire sidecar branch into `resolveSourceLink` precedence
**User Story**: US-002 | **AC**: AC-US2-03, AC-US2-04 | **Status**: [x] Completed

**Description**: Insert a new branch in `resolveSourceLink` between the lockfile fallback and the authored detector tail call. New order: lockfile-with-sourceRepoUrl → lockfile-legacy → sidecar → authored.

**Implementation Details**:
- In `source-link.ts` `resolveSourceLink(skillDir, root)`:
  - Existing logic for lockfile entry (with `sourceRepoUrl` and legacy `source: github:...` branches) stays unchanged.
  - When NO lockfile entry exists for `skillName` or `parentName` (current line 1036): replace `return detectAuthoredSourceLink(skillDir);` with:
    ```ts
    const sidecar = readCopiedSkillSidecar(skillDir);
    if (sidecar.repoUrl) return sidecar;
    return detectAuthoredSourceLink(skillDir);
    ```

**Test Plan**:
- **File**: `src/eval-server/__tests__/authored-source-link.test.ts` (extend with new `describe("resolveSourceLink with sidecar", …)`)
- **TC-010**: Given no lockfile entry AND `<skillDir>/.vskill-source.json` valid, When `resolveSourceLink` runs, Then it returns the sidecar's values.
- **TC-011**: Given a lockfile entry with `sourceRepoUrl` AND a sidecar, When `resolveSourceLink` runs, Then it returns the lockfile values (sidecar ignored).
- **TC-012**: Given no lockfile AND a sidecar AND a github-rooted parent `.git` (would otherwise trigger 0770), When `resolveSourceLink` runs, Then it returns the sidecar values (authored detector NOT called).
- **TC-013**: Given a malformed sidecar AND a github-rooted parent `.git`, When `resolveSourceLink` runs, Then it returns the authored detector's result (sidecar fall-through works).

---

## Phase 2: Core data path — capture provenance at copy time

### T-004: Modify `transfer()` to write `.vskill-source.json` after copy
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] Completed

**Description**: After `copyOwnSkillFiltered` / `copyPluginFiltered` complete in `src/studio/lib/scope-transfer.ts:118`, compute `sourceLink = resolveSourceLink(sourcePath, req.root)` and write `<destPath>/.vskill-source.json` if `sourceLink.repoUrl` is non-null.

**Implementation Details**:
- Import `resolveSourceLink` from `../../eval-server/source-link.js`.
- After the copy direction branch (lines 138-142), before `emit({type: "copied"})`:
  ```ts
  const sourceLink = resolveSourceLink(sourcePath, req.root);
  if (sourceLink.repoUrl) {
    writeFileSync(
      join(destPath, ".vskill-source.json"),
      JSON.stringify(sourceLink, null, 2)
    );
  }
  ```
- Note: `writeFileSync` and `join` already imported. No new imports beyond `resolveSourceLink`.
- Verify `sourcePath` was the *source* skill directory (line 119) — confirmed.

**Test Plan**:
- **File**: `src/studio/lib/__tests__/scope-transfer.test.ts` (extend; create if absent)
- **TC-014**: Given a source skill at `<root>/skills/A` whose `resolveSourceLink` returns `{repoUrl: "https://github.com/x/y", skillPath: "SKILL.md"}`, When `transfer({fromScope: "own", toScope: "global", skill: "A"})` runs, Then `<home>/.claude/skills/A/.vskill-source.json` exists with the JSON-stringified `{repoUrl, skillPath}`.
- **TC-015**: Given a source skill where `resolveSourceLink` returns `{null, null}`, When `transfer` runs, Then NO `.vskill-source.json` is written in the destination.
- **TC-016**: Given a source skill with its OWN `.vskill-source.json` pointing to repo X (and no lockfile), When `transfer` runs, Then the destination's new `.vskill-source.json` ALSO points to repo X (verified by reading the destination JSON; chained-copy semantics).

---

### T-005: Filter `.vskill-source.json` in `copyOwnSkillFiltered`
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] Completed

**Description**: Add `.vskill-source.json` to the OWN-scope root-level skip list in `copyOwnSkillFiltered` (scope-transfer.ts:101).

**Implementation Details**:
- Line 104: `if (!relBase && entry === ".vskill-meta.json") continue;` → `if (!relBase && (entry === ".vskill-meta.json" || entry === ".vskill-source.json")) continue;`

**Test Plan**:
- **File**: `src/studio/lib/__tests__/scope-transfer.test.ts` (extend)
- **TC-017**: Given a source dir at OWN scope containing `.vskill-meta.json` AND `.vskill-source.json`, When `copyOwnSkillFiltered` runs, Then the destination contains NEITHER file at the root.

---

### T-006: Filter `.vskill-source.json` in `copyPluginFiltered`
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] Completed

**Description**: Add `.vskill-source.json` to the exclusion list in `src/shared/copy-plugin-filtered.ts` so it never propagates through `* → OWN` copies either.

**Implementation Details**:
- Read `src/shared/copy-plugin-filtered.ts`, locate `shouldSkipFromCommands` or equivalent exclusion function/list.
- Append `.vskill-source.json` to whatever shape it uses (array, switch, regex). Match the existing pattern for `.vskill-meta.json` if present.

**Test Plan**:
- **File**: `src/shared/__tests__/copy-plugin-filtered.test.ts` (extend; verify or create)
- **TC-018**: Given a source dir containing `.vskill-source.json` at the root, When `copyPluginFiltered` runs, Then the destination does not contain it.

---

## Phase 3: UI parity — RepoLink chip + byline integration

### T-007: Create `src/eval-ui/src/components/RepoLink.tsx`
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] Completed

**Description**: New small component that renders a clickable `owner/repo` anchor when `repoUrl` parses, returns `null` otherwise. Reuses `canonicalRepoUrl` from `SourceFileLink.tsx`. Style mirrors `AuthorLink`.

**Implementation Details**:
- Export `parseOwnerRepo(repoUrl: string): { owner: string; repo: string } | null`:
  - Run `repoUrl` through `canonicalRepoUrl` (imported from `./SourceFileLink`).
  - `new URL(canonicalized)` inside try/catch.
  - Validate `hostname` is `github.com` or `www.github.com` (case-insensitive).
  - Split path on `/`, drop empties; require exactly 2 segments (`owner`, `repo`).
  - Validate owner against `/^[A-Za-z0-9][A-Za-z0-9-]{0,38}$/`.
  - Strip trailing `.git` from repo. Validate non-empty after strip.
  - Return `{owner, repo}` or `null`.
- Export `RepoLink({ repoUrl })`:
  - If `!repoUrl` → return `null`.
  - `parseOwnerRepo(repoUrl)` null → return `null`.
  - Render `<a data-testid="repo-link" href={`https://github.com/${owner}/${repo}`} target="_blank" rel="noopener noreferrer" style={{...AuthorLink-style...}}>{owner}/{repo}</a>`.

**Test Plan**:
- **File**: `src/eval-ui/src/components/__tests__/RepoLink.test.tsx` (NEW)
- **TC-019**: Given `repoUrl="https://github.com/anton-abyzov/greet-anton-test"`, When rendered, Then `<a>` has `href="https://github.com/anton-abyzov/greet-anton-test"`, `target="_blank"`, `rel="noopener noreferrer"`, and visible text `anton-abyzov/greet-anton-test`.
- **TC-020**: Given `repoUrl=null`, When rendered, Then the component returns `null` (no DOM output).
- **TC-021**: Given `repoUrl="https://github.com/x/y/tree/feature/foo"`, When rendered, Then `href="https://github.com/x/y"` (canonicalized).
- **TC-022**: Given `repoUrl="https://github.com/x/y/blob/main/skills/a/SKILL.md"`, When rendered, Then `href="https://github.com/x/y"`.
- **TC-023**: Given `repoUrl="https://github.com/x/y.git"`, When rendered, Then `href="https://github.com/x/y"` (trailing `.git` stripped).
- **TC-024**: Given `repoUrl="https://www.github.com/X/Y"`, When rendered, Then `href="https://github.com/X/Y"`.
- **TC-025**: Given `repoUrl="https://gitlab.com/x/y"`, When rendered, Then component returns `null`.
- **TC-026**: Given `repoUrl="not a url"`, When rendered, Then component returns `null`.

---

### T-008: Insert `<RepoLink>` into `DetailHeader.tsx` byline
**User Story**: US-004 | **AC**: AC-US4-04, AC-US4-05 | **Status**: [x] Completed

**Description**: Modify `DetailHeader.tsx` byline (lines 290-318) to render `<AuthorLink>` → `<RepoLink>` → `<SourceFileLink>` in that order. Existing wrapper, layout, and `data-testid` unchanged.

**Implementation Details**:
- Import `RepoLink` from `./RepoLink`.
- After `<AuthorLink>` JSX (line 312) and before `<SourceFileLink>` JSX (line 313), insert `<RepoLink repoUrl={skill.repoUrl ?? null} />`.
- Existing `flexWrap: "wrap"` + `gap: 10` layout already provides spacing; no separator span needed initially. (Architect can refine to add `·` separators if visual scanning is poor — non-blocking.)

**Test Plan**:
- **File**: `src/eval-ui/src/components/__tests__/DetailHeader.byline.test.tsx` (extend)
- **TC-027**: Given `skill.repoUrl="https://github.com/x/y"` and `skill.skillPath="SKILL.md"`, When `<DetailHeader skill={skill}/>` renders, Then the byline contains three children in order: `data-testid="author-link"`, `data-testid="repo-link"`, `data-testid="source-file-link"`.
- **TC-028**: Given `skill.repoUrl=null`, When `<DetailHeader skill={skill}/>` renders, Then the byline does NOT contain `data-testid="repo-link"` (chip absent).
- **TC-029**: Given `skill.repoUrl="https://github.com/x/y"`, When `<DetailHeader skill={skill}/>` renders, Then `data-testid="repo-link"` has `href="https://github.com/x/y"`.

---

## Phase 4: Tests, build, verification

### T-009: Run server-side test suite
**User Story**: All | **Status**: [x] Completed

**Description**: Run all server tests including the new sidecar tests + extended authored tests + scope-transfer tests. Verify regression on existing 0737/0743/0770 suites.

**Test Plan**:
- `cd repositories/anton-abyzov/vskill && npm run build && npx vitest run src/eval-server/__tests__/ src/studio/lib/__tests__/ src/shared/__tests__/`
- All TCs from T-001..T-006 pass. Existing skill-metadata-source-link.test.ts and authored-source-link.test.ts unchanged green.

---

### T-010: Run UI test suite
**User Story**: US-004 | **Status**: [x] Completed

**Description**: Run all UI component tests including the new RepoLink test + extended DetailHeader.byline test.

**Test Plan**:
- `cd repositories/anton-abyzov/vskill/src/eval-ui && npx vitest run src/components/__tests__/RepoLink.test.tsx src/components/__tests__/DetailHeader.byline.test.tsx src/components/__tests__/DetailHeader.source-link.test.tsx src/components/__tests__/SourceFileLink.test.tsx`
- All TCs from T-007..T-008 pass. Existing DetailHeader.byline.test.tsx, DetailHeader.source-link.test.tsx, SourceFileLink.test.tsx unchanged green.

---

### T-011: Build vskill + UI bundle
**User Story**: All | **Status**: [x] Completed

**Description**: Produce a fresh local build covering both server (`dist/`) and UI bundle so `vskill studio` from this checkout serves the new code.

**Test Plan**:
- `cd repositories/anton-abyzov/vskill && npm run build`
- Verify `dist/` is rebuilt with new timestamps; verify the UI bundle inside it includes `RepoLink`.

---

### T-012: Manual studio verification with preview tools
**User Story**: All | **AC**: All ACs (integration) | **Status**: [x] Completed

**Description**: Self-install + launch studio on a non-default port (do NOT ask user to restart their session per memory `feedback_self_install_vskill.md`). Reproduce the user's screenshot scenario, capture proof.

**Test Plan**:
- Launch: `node dist/bin.js studio --port 3137 --force` (per memory `project_vskill_studio_runtime.md`).
- `preview_start` against `http://localhost:3137`.
- Trigger a fresh Copy via Studio promote flow OR directly create a `.vskill-source.json` in an existing Personal-scope skill dir to validate the data path.
- Open `/#/skills/personal/.claude/<skill>` for the test skill.
- `preview_snapshot` to confirm three byline chips: author + repo + file.
- `preview_screenshot` for proof artifact in `reports/`.
- Open a marketplace-installed skill (lockfile path) → confirm three chips render.
- Open an authored skill in the umbrella repo (0770 path) → confirm three chips render.
- Open a skill with `repoUrl=null` → confirm NO repo chip renders, byline matches pre-change layout.
- `preview_stop`.

---

### T-013: Sync living docs + close out
**User Story**: All | **Status**: [x] Completed

**Description**: Run `specweave sync-living-docs 0809-...` to publish spec/plan/tasks into `.specweave/docs/internal/specs/`. After all gates pass, close via `/sw:done`.

**Test Plan**:
- `specweave sync-living-docs 0809-studio-copied-skill-source-link-and-repo-chip` exits 0.
- `/sw:done 0809-...` runs the closure pipeline (code-review → simplify → grill → judge-llm → PM 3-gate validation) and emits `increment.done` to `.specweave/state/event-queue/pending.jsonl`.

---

## Summary

- **13 tasks**, mapped 1:1 to ACs across **4 user stories** (3 P1 + 1 P2).
- **Domains**: server (eval-server, studio/lib, shared), UI (eval-ui/components), tests (vitest + RTL).
- **Estimated complexity**: Medium (cross-cutting touch on resolver + transfer + UI, but each touch is small and well-bounded by existing patterns from 0737/0743/0770).
- **Recommended execution**: `/sw:do 0809-...` (sequential, full control). Auto mode acceptable since the increment is well-scoped.
