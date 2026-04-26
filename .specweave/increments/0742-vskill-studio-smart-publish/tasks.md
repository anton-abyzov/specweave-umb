# Tasks: vskill Studio Smart Publish (MVP): dirty-state pill + AI-commit publish drawer

**Project**: vskill
**Test Mode**: STRICT TDD (RED → GREEN → REFACTOR)
**Increment**: 0742-vskill-studio-smart-publish

---

## Phase 0 — Test Fixtures

### T-001: Set up integration-test fixture scaffolding
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: NFR-007
**Status**: [ ] pending
**Test Plan**: Given a test helper module in `src/eval-server/__tests__/fixtures/` → When called → Then it runs `git init`, `git init --bare`, `git remote add` inside `tmp/` and yields typed `{ parentRepoDir, skillDir, bareRemoteDir }` paths; `repo-no-remote` fixture yields `{ parentRepoDir, skillDir }` with no origin configured.

**Notes**: Create two fixture seed helpers:
- `src/eval-server/__tests__/fixtures/repo-with-bare-remote.ts` — creates a parent repo + skill subdir + seeded unrelated dirty change outside skill dir + bare remote wired as origin
- `src/eval-server/__tests__/fixtures/repo-no-remote.ts` — creates parent repo + skill subdir, no remote
Both helpers run real `git` binary; no mocking. Used by integration tests in Phase 4.

---

## Phase 1 — Backend git/gh Helpers (TDD: RED → GREEN → REFACTOR)

### T-002: Write failing unit tests for `inspectSkillRepo` (RED)
**User Story**: US-001 | **Satisfies ACs**: NFR-001, NFR-002, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked `execFile` via `vi.hoisted` + `vi.mock("node:child_process")` → When `inspectSkillRepo` is called for each scenario → Then: (1) not-a-repo returns `{ isRepo: false }` with all other fields zero/null; (2) repo+clean returns `{ isRepo: true, dirty: false, ahead: 0 }`; (3) repo+dirty returns `{ dirty: true, files: [{path, status}] }`; (4) repo+no-remote returns `{ hasRemote: false, remoteUrl: null }`; (5) repo+remote+ahead=2 returns `{ hasRemote: true, ahead: 2 }`. All five cases FAIL since `git-status.ts` doesn't exist yet.

**Notes**: Test file at `src/eval-server/__tests__/git-status.test.ts`. Use mock pattern from `plan.md` §Test Strategy. Mock `execFile` with callback-style `(cmd, args, cb) => cb(null, { stdout, stderr })` per the vskill ESM convention.

---

### T-003: Implement `inspectSkillRepo` in `git-status.ts` (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, NFR-001, NFR-002, NFR-004
**Status**: [ ] pending
**Test Plan**: Given T-002 tests in place → When `inspectSkillRepo(skillDir)` is implemented → Then all five T-002 test cases pass. Manual verification: `git -C <skillDir> rev-parse --is-inside-work-tree` determines `isRepo`; six sequential `execFile` calls per plan.md §git-status.ts implementation outline.

**Notes**: New file `repositories/anton-abyzov/vskill/src/eval-server/git-status.ts`. Export `GitStatus`, `GitFile`, and `inspectSkillRepo`. Add a 5-second in-memory cache keyed by `skillDir` as described in `api-routes.ts` §plan.md. Use `.js` import extensions per `--moduleResolution nodenext`.

---

### T-004: Write failing unit tests for `detectGh` (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, NFR-005, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked `execFile` → When `detectGh` is called for each scenario → Then: (1) gh-missing (ENOENT) returns `{ available: false, authenticated: false, user: null }`; (2) gh-installed-not-auth (non-zero exit from `gh auth status`) returns `{ available: true, authenticated: false, user: null }`; (3) gh-installed-auth returns `{ available: true, authenticated: true, user: 'anton' }`. Also: test that `--show-token=false` flag is always passed. All three cases FAIL since `gh-detect.ts` doesn't exist yet.

**Notes**: Test file at `src/eval-server/__tests__/gh-detect.test.ts`. Assert `execFileMock` was called with `['auth', 'status', '--show-token=false']` — never `--show-token=true` or omitted.

---

### T-005: Implement `detectGh` in `gh-detect.ts` (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, NFR-005
**Status**: [ ] pending
**Test Plan**: Given T-004 tests in place → When `detectGh()` is implemented → Then all three T-004 test cases pass. Token MUST NOT appear in stdout captured, logs, or response.

**Notes**: New file `repositories/anton-abyzov/vskill/src/eval-server/gh-detect.ts`. Export `GhStatus` and `detectGh`. Must always pass `--show-token=false` to `gh auth status`. Parse username defensively with `as ([\w.-]+)` regex on a line containing `github.com` — if parse fails, `user = null` but `authenticated = true`.

---

### T-006: Extract shared `execFileSafe` helper if duplication exists (REFACTOR)
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: NFR-002
**Status**: [ ] pending
**Test Plan**: Given T-003 and T-005 implementations → When compared for `execFile` wrapping patterns → Then if both duplicate the promisify + error-handling wrapper, extract a shared `execFileSafe` helper into `src/eval-server/exec-safe.ts`; if duplication is minimal (< 5 lines shared), skip extraction. All existing tests still pass after any refactor.

**Notes**: Judgment call — the pattern is small enough that inlining is also fine. Only extract if both modules duplicate the `promisify(execFile)` + ENOENT error shape.

---

## Phase 2 — Backend Routes (TDD)

### T-007: Write failing route handler tests for `GET /git-status` (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, NFR-001, NFR-007
**Status**: [ ] pending
**Test Plan**: Given supertest + mocked `inspectSkillRepo` + `detectGh` → When `GET /api/skills/:plugin/:skill/git-status` is called → Then: (1) response shape includes `{ ok: true, gitStatus: {...}, gh: {...} }`; (2) path-traversal attempt (`plugin = '../../../etc'`) returns 400 via `assertContained`; (3) unknown skill returns 404. All cases FAIL since `git-routes.ts` doesn't exist yet.

**Notes**: Test file at `src/eval-server/__tests__/git-routes.test.ts`. Verify `assertContained` enforcement — the route must not accept raw filesystem paths from the client (NFR-001).

---

### T-008: Implement `GET /git-status` route and register in `eval-server.ts` (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US2-01, AC-US3-01, NFR-001
**Status**: [ ] pending
**Test Plan**: Given T-007 tests in place → When routes are implemented → Then all T-007 tests pass. Also inject `gitStatus` into `SkillInfo` in `api-routes.ts` GET skill detail handler.

**Notes**: New file `repositories/anton-abyzov/vskill/src/eval-server/git-routes.ts`. Register via `registerGitRoutes(router, root)` in `src/eval-server/eval-server.ts:24,94` (import + call). Modify `src/eval-server/api-routes.ts` to call `inspectSkillRepo(skillDir)` and embed result in `GET /api/skills/:plugin/:skill` response under `gitStatus` and `gh` fields. Use defensive null — if `inspectSkillRepo` throws, return `gitStatus: null`.

---

### T-009: Write failing tests for `POST /git-diff` (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, NFR-004, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked `execFile` for `git diff` → When `POST /api/skills/:plugin/:skill/git-diff` is called → Then: (1) response is `{ ok: true, diff: string }`; (2) diff is scoped — parent-repo unrelated change NOT in output (mock returns empty diff for unrelated paths); (3) `assertContained` rejects path-traversal. All cases FAIL since endpoint doesn't exist yet.

**Notes**: Extend test file at `src/eval-server/__tests__/git-routes.test.ts`. Assert `execFile` was called with `['diff', '--', skillDir]` — never `git diff` unscoped (NFR-004).

---

### T-010: Implement `POST /git-diff` route (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, NFR-003, NFR-004
**Status**: [ ] pending
**Test Plan**: Given T-009 tests in place → When endpoint is implemented → Then all T-009 tests pass. Run `git -C <skillDir> diff -- <skillDir>` via `execFile`.

**Notes**: Add handler in `src/eval-server/git-routes.ts`. Return diff in `{ ok: true, diff: string }` JSON envelope. Never run raw `git diff` without `-- <skillDir>` scope.

---

### T-011: Write failing tests for `POST /git-commit-message?sse` (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked LLM SSE stream → When `POST /api/skills/:plugin/:skill/git-commit-message?sse` is called with `{ provider, model }` body → Then: (1) response is `text/event-stream`; (2) SSE emits `progress` events with token chunks; (3) final `done` event carries the full commit message string; (4) missing `provider` or `model` returns 400. All cases FAIL since endpoint doesn't exist yet.

**Notes**: Extend test file at `src/eval-server/__tests__/git-routes.test.ts`. Mock `createLlmClient` from `../eval/llm.js` via `vi.mock`. Follow the same SSE test pattern used in `improve-routes` tests.

---

### T-012: Implement `POST /git-commit-message?sse` route (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, NFR-004
**Status**: [ ] pending
**Test Plan**: Given T-011 tests in place → When endpoint is implemented → Then all T-011 tests pass. Reuse `initSSE`/`sendSSE`/`sendSSEDone` + `createLlmClient` from `improve-routes.ts:21`. System prompt per plan.md §AI Commit-Message Prompt (one line ≤72 chars, no body, no emoji, no AI references).

**Notes**: Add handler in `src/eval-server/git-routes.ts`. Diff is scoped to `skillDir` for the AI prompt (NFR-004). Reuse provider/model SSE pattern from `src/eval-server/improve-routes.ts:21-67` verbatim — same helpers, same shape.

---

### T-013: Write failing tests for `POST /git-publish?sse` — all 3 modes (RED)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-06, AC-US3-02, AC-US3-04, NFR-002, NFR-003, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked `execFile` and `inspectSkillRepo` → When `POST /git-publish?sse` is called → Then:
- `mode: 'push'`: SSE emits `staging` → `committing` → `pushing` progress events, final `done { commitSha, branch, remoteUrl }`; `git add` was called with `-- <skillDir>` scope (NFR-003)
- `mode: 'create-via-gh'`: `gh repo create` called with `--public|--private`, `--source=<repoRoot>`, `--push`; invalid visibility returns 400; unauthenticated `gh` returns 400
- `mode: 'attach-remote-and-push'`: `git remote add origin <url>` then `git push -u origin <branch>`; invalid `remoteUrl` pattern returns 400
- Idempotency: rerunning `mode: 'push'` after clean state doesn't error
All cases FAIL since endpoint doesn't exist yet.

**Notes**: Extend test file at `src/eval-server/__tests__/git-routes.test.ts`. Assert `git add` was never called as `-A` or `.` (NFR-003). Assert `remoteUrl` regex validation for `attach-remote-and-push`.

---

### T-014: Implement `POST /git-publish?sse` route — all 3 modes (GREEN)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-06, AC-US3-02, AC-US3-04, AC-US3-05, NFR-002, NFR-003, NFR-005
**Status**: [ ] pending
**Test Plan**: Given T-013 tests in place → When all three mode handlers are implemented → Then all T-013 tests pass. Mode dispatch: `push` | `create-via-gh` | `attach-remote-and-push` per plan.md §git-routes.ts.

**Notes**: Add full mode dispatch in `src/eval-server/git-routes.ts`. Use `withHeartbeat` from `sse-helpers.ts` (already used in `improve-routes.ts`) to prevent proxy idle-out on long pushes. Validate `body.visibility` strictly as `'public'` or `'private'`. Validate `body.remoteUrl` against `^https://github\.com/[\w.-]+/[\w.-]+(\.git)?$`. Frontmatter description truncated to ≤120 chars before passing to `gh repo create --description`. For `create-via-gh`, re-run `inspectSkillRepo` post-call to capture the now-attached origin URL.

---

## Phase 3 — Frontend Pill + Hook (TDD)

### T-015: Write failing component tests for `GitStatusPill` (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, NFR-007
**Status**: [ ] pending
**Test Plan**: Given `@testing-library/react` render → When `GitStatusPill` is rendered with each prop variant → Then: (1) `gitStatus=null` → renders nothing; (2) `gitStatus.isRepo=false` → renders nothing; (3) `dirty=true` → renders amber `● uncommitted` chip; (4) `dirty=false, ahead=2` → renders blue `↑2` chip; (5) `dirty=false, ahead=0` → renders nothing; (6) `dirty=true` → `title` attribute contains changed-file count and branch name (e.g. `2 files changed on main`). All cases FAIL since component doesn't exist yet.

**Notes**: Test file at `src/eval-ui/src/components/__tests__/GitStatusPill.test.tsx`. Verify inline-style color tokens — amber uses `var(--amber-9)` dot and `var(--amber-3)` background; blue uses `var(--blue-*)` tokens. No Tailwind classes.

---

### T-016: Implement `GitStatusPill.tsx` and slot into `DetailHeader.tsx` (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] pending
**Test Plan**: Given T-015 tests in place → When `GitStatusPill` is implemented and slotted → Then all T-015 tests pass. Slot in `DetailHeader.tsx:151-178` immediately after `VersionBadge` with `gap: 8`.

**Notes**: New file `repositories/anton-abyzov/vskill/src/eval-ui/src/components/GitStatusPill.tsx`. Inline-style design tokens matching `VersionBadge.tsx:27-60` — same `inline-flex`/`border 1px solid var(--border)`/`borderRadius 4`/`fontFamily var(--font-mono)`/`fontSize 12`/`tabular-nums` shape. Also extend `src/eval-ui/src/types.ts` to add `GitFile`, `GitStatus`, `GhStatus` interfaces and optional `gitStatus?`/`gh?` fields on `SkillInfo`.

---

### T-017: Write failing tests for `useGitStatus` hook (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked `fetch` (MSW or vi.mock) → When `useGitStatus` hook mounts → Then: (1) on mount, `GET /api/skills/:plugin/:skill/git-status` is called once; (2) when `studio:content-saved` CustomEvent is dispatched on `window`, the hook refetches (second call); (3) no polling occurs — a `setInterval` spy is never called; (4) `refresh()` returned by hook triggers an additional refetch. All cases FAIL since hook doesn't exist yet.

**Notes**: Test file at `src/eval-ui/src/hooks/__tests__/useGitStatus.test.tsx`. Use `renderHook` from `@testing-library/react`. Verify the hook subscribes to `window` CustomEvent `studio:content-saved` (not `CONTENT_SAVED` action dispatch).

---

### T-018: Implement `useGitStatus.ts` and wire `CONTENT_SAVED` dispatch (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] pending
**Test Plan**: Given T-017 tests in place → When `useGitStatus` is implemented and `WorkspaceContext.tsx` is modified → Then all T-017 tests pass. After `saveContent()` at `WorkspaceContext.tsx:223`, emit `window.dispatchEvent(new CustomEvent('studio:content-saved', { detail: { plugin, skill } }))`.

**Notes**: New file `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useGitStatus.ts`. Modify `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx:223` to dispatch the CustomEvent after `dispatch({ type: "CONTENT_SAVED" })`. Also add four API wrappers to `src/eval-ui/src/api.ts` next to `applyImprovement` at line 449: `getGitStatus`, `getGitDiff`, `streamCommitMessage`, `streamPublish`.

---

## Phase 4 — PublishDrawer + Integration (TDD + E2E)

### T-019: Write failing component tests for `PublishDrawer` mode state machine (RED)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, NFR-006, NFR-007
**Status**: [ ] pending
**Test Plan**: Given mocked API calls + SSE streams → When `PublishDrawer` is rendered for each mode → Then:
- `mode='push'`: header shows repo root + branch + remote URL; diff preview renders; AI message streams into textarea; `Commit & Push` button visible; clicking `Regenerate` aborts current stream and re-streams; clicking `Cancel` closes without side effects
- `mode='create-via-gh'`: primary button reads `Create on GitHub & Push`; `public/private` radio renders; clicking calls `POST /git-publish?sse` with `mode: 'create-via-gh'`
- `mode='attach-remote-and-push'`: primary button reads `Create on GitHub`; clicking opens `window.open` with URL-encoded name+description (NFR-006); drawer enters polling state; after simulated 200 response, auto-calls `POST /git-publish?sse` with `mode: 'attach-remote-and-push'`; after 60s timeout, transitions to paste-url state; `Cancel` in any state closes cleanly
All cases FAIL since component doesn't exist yet.

**Notes**: Test file at `src/eval-ui/src/components/__tests__/PublishDrawer.test.tsx`. Mock `window.open`. Verify `encodeURIComponent` applied to skill name + description in the GitHub URL (NFR-006). Description truncated to ≤120 chars before encoding.

---

### T-020: Implement `PublishDrawer.tsx`, `Publish` button in `EditorPanel.tsx`, and API wrappers (GREEN)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, NFR-006
**Status**: [ ] pending
**Test Plan**: Given T-019 tests in place → When drawer is implemented → Then all T-019 tests pass. Publish button visible when `gitStatus?.isRepo && (dirty || ahead > 0 || !hasRemote)`; disabled with tooltip when `!gitStatus?.isRepo`.

**Notes**: New file `repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishDrawer.tsx`. Mirrors `OpsDrawer.tsx` (420px right, `createPortal`, esc-close). Mode computed via `computeMode(gitStatus, gh)` per plan.md. `Publish` button added to `src/eval-ui/src/pages/workspace/EditorPanel.tsx:370`. SSE streaming via `AbortController` — `Regenerate` aborts current stream and reopens. On `done` event: fire `studio:toast` CustomEvent, call `onClose`, call `useGitStatus.refresh()`. Polling for `attach-remote-and-push`: `setInterval(2000)`, max 30 iterations (60s), `clearInterval` on 200 or timeout. On timeout, show paste-URL input.

---

### T-021: Integration test — Path A (push to bare remote) (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, NFR-003, NFR-004, NFR-007
**Status**: [ ] pending
**Test Plan**: Given `repo-with-bare-remote` fixture from T-001 → When `POST /git-publish?sse` with `mode: 'push'` is called using real `git` binary → Then: (1) commit lands on bare remote (`git log` on bare remote shows new commit); (2) commit is scoped — unrelated file outside skillDir is NOT in the commit; (3) rerunning the same publish after clean state doesn't error (idempotent). FAILS until real git integration is confirmed working end-to-end.

**Notes**: Integration test file at `src/eval-server/__tests__/git-publish-integration.test.ts`. Uses real `git` binary (no mocks). Fixture from T-001. Assertions via `execFile('git', ['-C', bareRemoteDir, 'log', '--oneline'])`.

---

### T-022: Integration test — Path B (gh shim) (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, NFR-002, NFR-005, NFR-007
**Status**: [ ] pending
**Test Plan**: Given `repo-no-remote` fixture + a `gh` shim script on PATH that records args and creates a bare repo → When `POST /git-publish?sse` with `mode: 'create-via-gh'` is called → Then: (1) shim was called with correct args including `--source=<repoRoot>` and `--push`; (2) `--show-token` is never passed; (3) after success, re-running `inspectSkillRepo` shows `hasRemote: true`. FAILS until integration is confirmed.

**Notes**: Extend integration test file at `src/eval-server/__tests__/git-publish-integration.test.ts`. `gh` shim is a small shell script added to `PATH` for the test process only.

---

### T-023: Integration test — Path C (no gh, MSW mock + 60s timeout fallback) (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05, NFR-007
**Status**: [ ] pending
**Test Plan**: Given `repo-no-remote` fixture + MSW intercepting `https://api.github.com/repos/<owner>/<name>` → When poll-detect flow runs → Then: (1) on simulated 200, `POST /git-publish?sse` with `mode: 'attach-remote-and-push'` is called and push succeeds; (2) when MSW keeps returning 404 for 60s+, paste-URL input appears; (3) submitting a URL in paste-URL state triggers `mode: 'attach-remote-and-push'` and push succeeds. FAILS until integration is confirmed.

**Notes**: Extend integration test file. MSW intercepts `api.github.com` — test programmatically flips mock from 404 to 200 mid-poll. Verify rate-limit budget: ≤30 requests per drawer-open (NFR-007 context).

---

### T-024: Fix any integration-test failures and confirm all pass (GREEN)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-06, AC-US3-02, AC-US3-04, AC-US3-05, NFR-007
**Status**: [ ] pending
**Test Plan**: Given T-021, T-022, T-023 integration tests → When bugs surfaced by real-git execution are fixed → Then all three integration test suites pass. Run `npx vitest run src/eval-server/__tests__/git-publish-integration.test.ts`.

**Notes**: Common failure modes: wrong `repoRoot` vs `skillDir` passed to `git remote add`; missing `git config user.email/name` in fixture; `gh` shim PATH not inherited by `execFile`. Fix at source, don't workaround in tests.

---

### T-025: E2E test — studio publish drawer, all 3 paths (E2E)
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, NFR-007
**Status**: [ ] pending
**Test Plan**: Given Playwright + `npx vskill@<dev-version> studio` against three fixtures → When each path is exercised → Then:
- Path A: edit SKILL.md → Save → amber pill visible within one render cycle → click Publish → drawer opens with diff + AI message → click Regenerate → new message streamed → click Commit & Push → toast shows commit SHA + branch → pill clears → bare remote `git log` confirms commit
- Path B: same flow, `mode=create-via-gh`, `gh` shim on PATH → drawer shows `Create on GitHub & Push` → one-click creates repo + pushes → toast names new repo URL
- Path C: same flow, `gh` shimmed missing, MSW mocks `api.github.com` → drawer shows `Create on GitHub` → window.open called with URL-encoded params → poll detects 200 → auto-push → toast + pill clears; sub-scenario: 60s timeout → paste-URL input appears → submit URL → push succeeds

**Notes**: E2E test file at `repositories/anton-abyzov/vskill/e2e/studio-publish-drawer.spec.ts`. Follow verification steps from plan.md §Verification. Run `npx playwright test e2e/studio-publish-drawer.spec.ts`.

---

## Phase 5 — Closure

### T-026: Run `/sw:done` — code-review → simplify → grill → judge-llm → PM gates
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: NFR-007
**Status**: [ ] pending
**Test Plan**: Given all tasks T-001 through T-025 marked complete → When `/sw:done` is invoked → Then code-review report shows no critical/high/medium findings; simplify pass completes; grill report is written; judge-llm report is written (or waived); PM validation passes all 14 ACs and 7 NFRs. If any gate fails, fix the finding and re-run the gate (max 3 iterations per gate).

**Notes**: Run `npx vitest run` (unit + integration) and `npx playwright test` before invoking `/sw:done`. Fix any remaining findings before declaring the increment closed. Do NOT ask the user — auto-close per CLAUDE.md workflow.

---

### T-027: Ship vskill via `/sw:npm`
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: NFR-007
**Status**: [ ] pending
**Test Plan**: Given increment closed by T-026 → When `/sw:npm` is invoked → Then: commit → tag → `npm publish` → GitHub Release → `git push` completes without error; new vskill version is visible on `npmjs.com/package/vskill`.

**Notes**: Standard `/sw:npm` flow per CLAUDE.md. This is the deploy step — run immediately after T-026 closes the increment.
