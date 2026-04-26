---
increment: 0759-studio-publish-push-and-open-submit
title: "Studio: Publish (push + open pre-filled submit page)"
generated: "2026-04-26"
status: planned
test_mode: TDD
---

# Tasks: 0759 — Studio: Publish (push + open pre-filled submit page)

## AC Coverage Table

| AC ID | Description | Covered By |
|---|---|---|
| AC-US1-01 | Publish button present when `hasRemote: true` | T-013, T-014 |
| AC-US1-02 | Publish button absent from DOM when `hasRemote: false` | T-013, T-014 |
| AC-US1-03 | Button disabled + loading while request in-flight | T-013, T-014 |
| AC-US1-04 | `useGitRemote` stores `{ remoteUrl, branch, hasRemote }` from GET /git-remote | T-009, T-010 |
| AC-US1-05 | GET /git-remote failure → `hasRemote` defaults false → no button | T-009, T-010 |
| AC-US2-01 | GET /git-remote with valid remote → `{ remoteUrl, branch, hasRemote: true }` | T-001, T-002 |
| AC-US2-02 | GET /git-remote with no remote → `{ remoteUrl: null, hasRemote: false }` HTTP 200 | T-001, T-002 |
| AC-US2-03 | POST /git-publish on exit 0 → `{ success: true, commitSha, branch, remoteUrl, stdout, stderr }` | T-003, T-004 |
| AC-US2-04 | POST /git-publish on non-zero exit → HTTP 500 `{ success: false, stderr }` | T-003, T-004 |
| AC-US2-05 | Subprocess timeout → HTTP 500 `{ success: false, stderr: "timeout" }` | T-003, T-004 |
| AC-US2-06 | Workspace path validated against allowlist before git exec | T-003, T-004 |
| AC-US3-01 | Success → `window.open` called once with correct URL and `noopener,noreferrer` | T-013, T-014 |
| AC-US3-02 | SSH URL normalized to HTTPS form | T-005, T-006 |
| AC-US3-03 | HTTPS URL with .git suffix stripped | T-005, T-006 |
| AC-US3-04 | Success toast shows short SHA (7 chars), branch name, "Opening…" | T-013, T-014 |
| AC-US3-05 | Failure → button re-enabled, error toast with stderr, no `window.open` | T-013, T-014 |
| AC-US4-01 | `?repo=` valid URL → input pre-filled on mount | T-016, T-017 |
| AC-US4-02 | No `?repo=` param → input empty | T-016, T-017 |
| AC-US4-03 | Malformed `?repo=` → input empty, no error UI | T-016, T-017, T-018 |
| AC-US4-04 | Pre-filled input is editable (not read-only) | T-016, T-017 |
| AC-US4-05 | Form NOT auto-submitted on mount even when pre-filled | T-016, T-017, T-019 |

---

## Phase 1 — Backend (vskill eval-server)

### T-001: RED — Failing tests for GET /git-remote route handler
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given a mocked `child_process.spawn` (via `vi.hoisted()` + `vi.mock()`) that exits 0 with stdout `https://github.com/owner/repo.git` for `git remote get-url origin` and `main` for `git rev-parse --abbrev-ref HEAD`
When `getGitRemote` handler is called
Then it resolves with HTTP 200 `{ remoteUrl: "https://github.com/owner/repo.git", branch: "main", hasRemote: true }`

Given a mocked spawn that exits non-zero for `git remote get-url origin` (no remote configured)
When `getGitRemote` handler is called
Then it resolves with HTTP 200 body `{ remoteUrl: null, branch: "main", hasRemote: false }`
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/git-routes.test.ts` (NEW)
**Estimated effort**: S

---

### T-002: GREEN — Implement GET /git-remote
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-06 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-001 failing tests exist
When `makeGitHandlers(root)` is implemented with a `getGitRemote` method that spawns `git remote get-url origin` and `git rev-parse --abbrev-ref HEAD` using `child_process.spawn` with an explicit argv array (NOT shell-string interpolation) and validates `root` against the workspace allowlist
Then all T-001 tests pass
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/git-routes.ts` (NEW)
**Estimated effort**: M

---

### T-003: RED — Failing tests for POST /git-publish handler
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given mocked spawn that exits 0 with stdout "Everything up-to-date\n" and stderr ""
When `postGitPublish` handler is called
Then it returns HTTP 200 `{ success: true, commitSha, branch, remoteUrl, stdout, stderr }`

Given mocked spawn that exits 1 with stderr "rejected: non-fast-forward"
When `postGitPublish` handler is called
Then it returns HTTP 500 `{ success: false, stdout: "", stderr: "rejected: non-fast-forward" }`

Given mocked spawn that never exits and `GIT_PUBLISH_TIMEOUT_MS` is set to 100ms
When the timeout fires
Then the subprocess is killed and the response is HTTP 500 `{ success: false, stderr: "timeout" }`

Given a workspace path that is NOT in the allowlist
When `postGitPublish` handler is called
Then it returns HTTP 403 without spawning any subprocess
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/git-routes.test.ts` (MODIFY — add publish test cases)
**Estimated effort**: S

---

### T-004: GREEN — Implement POST /git-publish
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-003 failing tests exist
When `postGitPublish` is implemented using `child_process.spawn("git", ["push"], { cwd: root })` with a 60s timeout (configurable via `GIT_PUBLISH_TIMEOUT_MS` env var), workspace allowlist check before spawn, and stdout/stderr collected into buffers on data events
Then all T-003 tests pass
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/git-routes.ts` (MODIFY)
**Estimated effort**: M

---

### T-005: RED — Failing tests for SSH→HTTPS URL normalizer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given input `git@github.com:owner/repo.git`
When `normalizeRemoteUrl` is called
Then it returns `https://github.com/owner/repo`

Given input `https://github.com/owner/repo.git`
When `normalizeRemoteUrl` is called
Then it returns `https://github.com/owner/repo`

Given input `https://github.com/owner/repo` (no .git suffix)
When `normalizeRemoteUrl` is called
Then it returns `https://github.com/owner/repo` unchanged

Given an unrecognized format such as `ssh://custom-host/repo`
When `normalizeRemoteUrl` is called
Then it throws an error (or returns null — explicit error path, not silent passthrough)
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/normalizeRemoteUrl.test.ts` (NEW)
**Estimated effort**: S

---

### T-006: GREEN — Implement normalizeRemoteUrl utility
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-005 failing tests exist
When `normalizeRemoteUrl(raw: string): string` is implemented as a pure function with two regex branches — one for `git@github.com:owner/repo(.git)?` and one for `https://github.com/owner/repo(.git)?` — with a throw on unrecognized input
Then all T-005 tests pass and the function has no side effects
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/normalizeRemoteUrl.ts` (NEW)
**Estimated effort**: S

---

### T-007: Mount git routes in eval-server entry
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given `git-routes.ts` exports `registerGitRoutes(router, root)`
When `eval-server.ts` is modified to import and call `registerGitRoutes(router, root)` alongside the existing `registerAuthoringRoutes` call
Then `GET /api/git-remote` and `POST /api/git-publish` return non-404 responses (verified in T-020 manual smoke test)
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts` (MODIFY)
**Estimated effort**: S

---

### T-008: REFACTOR — Extract subprocess logic, audit for shell injection
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-06 | **Status**: [x] completed
**Phase**: REFACTOR
**Test Plan**:
Given T-002 and T-004 are implemented
When `git-routes.ts` is reviewed
Then no `exec`, `shell: true`, or template-literal argv patterns are present; any duplicated stdout/stderr collection logic between the two handlers is extracted to a shared helper (e.g., `runGitCommand(args, cwd, timeoutMs)`); all T-001 and T-003 tests still pass after refactor
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/git-routes.ts` (MODIFY)
**Estimated effort**: S

---

## Phase 2 — Frontend (vskill eval-ui)

### T-009: RED — Failing tests for useGitRemote hook
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given `fetch` is mocked (via `vi.stubGlobal`) to return `{ remoteUrl: "https://github.com/owner/repo.git", branch: "main", hasRemote: true }`
When `useGitRemote()` mounts using `renderHook`
Then `fetch` is called exactly once with `/api/git-remote` and the hook state settles to `{ hasRemote: true, remoteUrl: "https://github.com/owner/repo.git", branch: "main", loading: false, error: null }`

Given `fetch` throws a network error
When `useGitRemote()` mounts
Then the hook state settles to `{ hasRemote: false, remoteUrl: null, branch: null, loading: false, error: <Error> }`
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/useGitRemote.test.ts` (NEW)
**Estimated effort**: S

---

### T-010: GREEN — Implement useGitRemote hook
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-009 failing tests exist
When `useGitRemote.ts` is implemented with a `useEffect` with empty deps array that calls `api.gitRemote()`, stores the result in `useState`, and defaults `hasRemote` to `false` on error
Then all T-009 tests pass and the hook never fires more than once per mount
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useGitRemote.ts` (NEW)
**Estimated effort**: S

---

### T-011: RED — Failing tests for api.ts new methods
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given the existing `apiFetch` wrapper is mocked
When `api.gitRemote()` is called
Then it invokes `apiFetch` with `GET /api/git-remote` and returns the parsed JSON response

When `api.gitPublish()` is called
Then it invokes `apiFetch` with `POST /api/git-publish` (no body required) and returns the parsed JSON response
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/api.git.test.ts` (NEW)
**Estimated effort**: S

---

### T-012: GREEN — Add gitRemote() and gitPublish() to api.ts
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-011 failing tests exist
When `gitRemote()` and `gitPublish()` are added to `src/eval-ui/src/api.ts` using the existing `apiFetch` wrapper pattern (matching the style of other methods in that file)
Then all T-011 tests pass and no second fetch abstraction is introduced
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (MODIFY)
**Estimated effort**: S

---

### T-013: RED — Failing component tests for Publish button
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US3-01, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given `useGitRemote` is mocked to return `{ hasRemote: true, remoteUrl: "git@github.com:owner/repo.git", branch: "main" }`
When `EditorPanel` renders
Then a button with accessible name "Publish" is present in the DOM

Given `useGitRemote` is mocked to return `{ hasRemote: false }`
When `EditorPanel` renders
Then no element with accessible name "Publish" exists in the DOM (not hidden — element must be absent)

Given `useGitRemote` returns `hasRemote: true` and the Publish button is clicked with `api.gitPublish` left pending
When the component re-renders during the in-flight request
Then the Publish button has the `disabled` attribute and shows a loading indicator

Given `api.gitPublish` resolves with `{ success: true, commitSha: "abc1234def5678", branch: "main", remoteUrl: "git@github.com:owner/repo.git" }`
When the click handler completes
Then `window.open` is called exactly once with first arg `https://verified-skill.com/submit?repo=https%3A%2F%2Fgithub.com%2Fowner%2Frepo` and third arg `noopener,noreferrer`, and a `studio:toast` CustomEvent is dispatched with `detail` containing the short SHA "abc1234" (7 chars), branch "main", and the word "Opening"

Given `api.gitPublish` resolves with `{ success: false, stderr: "rejected push details here" }`
When the click handler completes
Then `window.open` is NOT called, a `studio:toast` error CustomEvent is dispatched with `detail` containing the first 200 chars of stderr, and the Publish button is no longer disabled
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/EditorPanel.publish.test.tsx` (NEW)
**Estimated effort**: M

---

### T-014: GREEN — Add Publish button to EditorPanel.tsx
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US3-01, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-013 failing tests exist
When `EditorPanel.tsx` is modified near line 370 to: (1) call `useGitRemote()` at the top of the component, (2) add `const [publishing, setPublishing] = useState(false)`, (3) conditionally render a Publish button only when `hasRemote === true`, (4) implement `handlePublish` that sets `publishing = true`, calls `api.gitPublish()`, calls `normalizeRemoteUrl` on the response `remoteUrl`, calls `window.open('https://verified-skill.com/submit?repo=' + encodeURIComponent(normalized), '_blank', 'noopener,noreferrer')` on success, dispatches `studio:toast` CustomEvent on both success and failure paths, and resets `publishing = false` in a finally block
Then all T-013 tests pass
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/EditorPanel.tsx` (MODIFY)
**Estimated effort**: M

---

### T-015: REFACTOR — Extract URL construction helper if duplicated
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Phase**: REFACTOR
**Test Plan**:
Given T-014 is implemented
When the code that builds `https://verified-skill.com/submit?repo=<encoded>` is reviewed
Then if the pattern `normalizeRemoteUrl` + `encodeURIComponent` + base URL string appears more than once it is extracted to a single `buildSubmitUrl(remoteUrl: string): string` helper; otherwise no change is needed; all T-013 tests still pass after any refactor
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/normalizeRemoteUrl.ts` (MODIFY — possibly extend)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/EditorPanel.tsx` (MODIFY — possibly extract)
**Estimated effort**: S

---

## Phase 3 — Platform (vskill-platform /submit)

### T-016: RED — Failing tests for ?repo= query param parser
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Phase**: RED
**Test Plan**:
Given `useSearchParams` from `next/navigation` is mocked to return a params object with `repo=https://github.com/owner/repo`
When the submit page component mounts (via React Testing Library `render`)
Then the URL input value equals `https://github.com/owner/repo`

Given `useSearchParams` returns no `repo` key
When the component mounts
Then the URL input value is empty string

Given `useSearchParams` returns `repo=not-a-github-url`
When the component mounts
Then the URL input value is empty string and no element with `role="alert"` or error class exists in the DOM

Given the input was pre-filled from a valid param
When the user fires a change event with a new value
Then the input reflects the user's typed value (onChange is not blocked or reset)

Given `useSearchParams` returns a valid `?repo=` value
When the component mounts
Then no submit or discover network request is made automatically
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/submit/__tests__/page.prefill.test.ts` (NEW)
**Estimated effort**: S

---

### T-017: GREEN — Modify submit/page.tsx to read ?repo= and pre-fill input
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**:
Given T-016 failing tests exist
When `src/app/submit/page.tsx` is modified to: (1) add a `useEffect` that reads `window.location.search` (equivalent to `useSearchParams` for a client-side read, avoids Suspense boundary requirement), (2) validates the `repo` param against `GITHUB_REPO_VALIDATION_RE`, and calls `setRepoUrl(param)` only when the regex matches, and (3) NOT call any form submission or discover API on mount
Then all T-016 tests pass

*Implementation note*: `window.location.search` was used instead of `useSearchParams()` from next/navigation — functionally equivalent for a client-side read, simpler (no Suspense boundary needed). Spec FR-005 updated to reflect both as valid approaches.
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/submit/page.tsx` (MODIFY)
**Estimated effort**: M

---

### T-018: REFACTOR — Confirm no auto-submit and no error UI on malformed param
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-05 | **Status**: [x] completed
**Phase**: REFACTOR
**Test Plan**:
Given T-017 is implemented and renders with a malformed `?repo=` param
When the component is inspected after mount
Then no element with `role="alert"`, `.error`, `.toast`, or any error-indicating class is present in the DOM; no `fetch` or axios call to `/api/v1/submissions` was made during the mount cycle; all T-016 tests still pass
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/submit/page.tsx` (MODIFY — remove any accidental error UI if present)
**Estimated effort**: S

---

## Phase 4 — E2E + Verification

### T-019: E2E — Playwright: Publish click → popup URL matches ?repo= param
**User Story**: US-001, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US3-01, AC-US4-05 | **Status**: [x] completed
**Phase**: E2E
**Test Plan**:
Given the studio is started against a fixture workspace where `GET /api/git-remote` responds with `{ remoteUrl: "git@github.com:owner/test-repo.git", branch: "main", hasRemote: true }` and `POST /api/git-publish` responds with `{ success: true, commitSha: "abc1234def5678", branch: "main", remoteUrl: "git@github.com:owner/test-repo.git" }` (routes intercepted via Playwright `page.route`)
When the studio page loads and the Publish button appears
Then `page.locator('button[aria-label="Publish"]')` is visible

When the Publish button is clicked
Then the button becomes disabled (loading state), and `page.waitForEvent('popup')` returns a popup whose URL matches the regex `https://verified-skill\.com/submit\?repo=https%3A%2F%2Fgithub\.com%2Fowner%2Ftest-repo`
**Files**:
- `repositories/anton-abyzov/vskill/e2e/studio-publish.spec.ts` (NEW)
**Estimated effort**: M

---

### T-020: Manual verification — studio against real throwaway repo
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US2-03, AC-US3-01, AC-US4-01 | **Status**: [x] completed
**Phase**: E2E
**Test Plan**:
Given a real throwaway GitHub repo with at least one commit and a configured git remote (SSH or HTTPS) in the local workspace
When `vskill studio` is launched, the workspace opened, and the Publish button clicked
Then a real `git push` subprocess runs (exit 0), the browser opens `https://verified-skill.com/submit?repo=<encoded-https-url>`, the URL input on the platform submit page is pre-filled with the repo URL, the Save button is unaffected by the new Publish button, and the existing discover/submit flow on the platform continues to work normally
**Files**: N/A (manual verification — no new files)
**Estimated effort**: S

---

### T-021: Run all tests, capture coverage, save reports
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: (all) | **Status**: [x] completed
**Phase**: E2E
**Test Plan**:
Given all unit and E2E tests from T-001 through T-019 are implemented and passing
When `npx vitest run --coverage` is executed in both `repositories/anton-abyzov/vskill` and `repositories/anton-abyzov/vskill-platform`
Then coverage for `git-routes.ts`, `normalizeRemoteUrl.ts`, `useGitRemote.ts`, and the `page.tsx` pre-fill logic is >= 90%; all 21 tasks are complete; coverage JSON and Playwright HTML reports are saved under `.specweave/increments/0759-studio-publish-push-and-open-submit/reports/`
**Files**:
- `.specweave/increments/0759-studio-publish-push-and-open-submit/reports/` (NEW dir — output only)
**Estimated effort**: S

---

## Phase 5 — AI commit message + commit/push for dirty trees

Added in follow-up after initial 0759 close. All tasks below are completed and shipped in vskill@0.5.132.

### T-022: RED — Tests for /api/git/diff handler
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Phase**: RED
**Test Plan**: Given mocked spawn returning staged + unstaged diff + porcelain status; When `makePostGitDiffHandler(root)` is called; Then the response body is `{ hasChanges, diff, fileCount }` with combined diff text and the count derived from porcelain output.
**Files**: `src/eval-server/__tests__/git-commit-message.test.ts` (NEW)

### T-023: GREEN — Implement /api/git/diff
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**: Given T-022 failing; When `collectDiffSummary(root, timeoutMs)` runs `git diff --staged` + `git diff` + `git status --porcelain` in parallel via `Promise.all`; Then T-022 passes.
**Files**: `src/eval-server/git-routes.ts` (MODIFY — add `collectDiffSummary` + `makePostGitDiffHandler`)

### T-024: RED — Tests for /api/git/commit-message handler
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-10 | **Status**: [x] completed
**Phase**: RED
**Test Plan**: Given mocked spawn (dirty diff) + mocked `createLlmClient` returning a fake message; When the handler receives a body `{ provider, model }`; Then the response body is `{ message }`, `createLlmClient` was called with the body's provider+model, and the user prompt sent to the LLM contains the diff text. Cover: clean tree → 400; LLM error → 500; >10K diff → truncated.
**Files**: `src/eval-server/__tests__/git-commit-message.test.ts` (MODIFY)

### T-025: GREEN — Implement /api/git/commit-message
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-10 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**: Given T-024 failing; When `makePostGitCommitMessageHandler` reads body, runs `collectDiffSummary`, returns 400 on clean, truncates payload at 10K, calls `createLlmClient({provider, model}).generate(systemPrompt, userPrompt)`; Then T-024 passes.
**Files**: `src/eval-server/git-routes.ts` (MODIFY)

### T-026: RED — Tests for extended /api/git/publish (with commitMessage)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-11, AC-US5-12 | **Status**: [x] completed
**Phase**: RED
**Test Plan**: Given mocked spawn for status/add/commit/push/metadata sequence; When body is `{ commitMessage }` AND tree is dirty; Then spawn is called with `["status","--porcelain"]`, `["add","-A"]`, `["commit","-m",msg]`, `["push"]` in that order. Cover: clean tree skips add+commit; commit failure → 500 + no push; argv-only (shell-injection safety).
**Files**: `src/eval-server/__tests__/git-commit-message.test.ts` (MODIFY)

### T-027: GREEN — Extend POST /api/git/publish to handle commitMessage
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-11, AC-US5-12 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**: Given T-026 failing; When the handler reads `body.commitMessage`, on dirty runs `git status --porcelain` then `git add -A` then `git commit -m "<msg>"` (argv array, no shell), bails on commit failure with 500 before push; Then T-026 passes.
**Files**: `src/eval-server/git-routes.ts` (MODIFY)

### T-028: RED — Tests for api.gitDiff, api.gitCommitMessage, api.gitPublish(commitMessage)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**Phase**: RED
**Test Plan**: Given mocked global fetch; Verify api.gitDiff calls POST /api/git/diff; api.gitCommitMessage calls POST /api/git/commit-message with provider+model in JSON body; api.gitPublish forwards commitMessage in the body when provided.
**Files**: `src/eval-ui/src/__tests__/api.git-phase5.test.ts` (NEW)

### T-029: GREEN — Add api.gitDiff, api.gitCommitMessage; modify api.gitPublish signature
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**Phase**: GREEN
**Files**: `src/eval-ui/src/api.ts` (MODIFY)

### T-030: RED — PublishDrawer component tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07, AC-US5-08, AC-US5-09 | **Status**: [x] completed
**Phase**: RED
**Test Plan**: jsdom + react-dom/client; mock api; cover auto-generate on mount, controlled textarea, Commit & Push success path (window.open + toast + onClose), failure path (toast, no open, no close), Cancel, Regenerate, empty-message disable.
**Files**: `src/eval-ui/src/components/__tests__/PublishDrawer.test.tsx` (NEW)

### T-031: GREEN — Implement PublishDrawer component
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02–09 | **Status**: [x] completed
**Phase**: GREEN
**Files**: `src/eval-ui/src/components/PublishDrawer.tsx` (NEW)

### T-032: GREEN — Wire PublishButton to open drawer on dirty + pass provider/model from EditorPanel
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-11 | **Status**: [x] completed
**Phase**: GREEN
**Test Plan**: Existing PublishButton tests still pass (api.gitDiff falls through to push when not mocked → preserves clean-tree behaviour). EditorPanel passes `config?.provider`, `config?.model` from `useConfig()` to PublishButton.
**Files**: `src/eval-ui/src/components/PublishButton.tsx` (MODIFY), `src/eval-ui/src/pages/workspace/EditorPanel.tsx` (MODIFY)

### T-033: Live smoke test against umbrella repo
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Phase**: E2E
**Test Plan**: Built vskill@0.5.132 locally, spawned `eval serve --root <umbrella>`, hit `POST /api/git/diff` against this very repo with 22 unstaged file changes; received `{ hasChanges: true, fileCount: 22, diff: "diff --git a/.specweave/config.json…" }` — confirms real git diff subprocess invocation, not mocked.
**Files**: N/A (smoke verification)

---

## Phase 6 — Sidebar dirty indicator

Added in follow-up. All tasks below are completed and shipped in vskill@0.5.138.

### T-034: RED — Tests for getDirtySkillIds pure resolver
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**Files**: `src/eval-ui/src/utils/__tests__/getDirtySkillIds.test.ts` (NEW). 8 cases: dirty intersection, empty input, skill dir == workspace root, sibling-prefix safety, outside-root defense, porcelain prefix tolerance, skill ID format.

### T-035: GREEN — Implement getDirtySkillIds
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**Files**: `src/eval-ui/src/utils/getDirtySkillIds.ts` (NEW). Pure function, no Node `path` dep (POSIX string prefix check).

### T-036: RED — Tests for GET /api/git/status
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03 | **Status**: [x] completed
**Files**: `src/eval-server/__tests__/git-status.test.ts` (NEW). 4 cases: parsed porcelain paths, clean tree, non-git repo (exit 128 → empty array), argv-only spawn safety.

### T-037: GREEN — Implement makeGetGitStatusHandler + register route
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03 | **Status**: [x] completed
**Files**: `src/eval-server/git-routes.ts` (MODIFY). Reuses existing `runGitCommand` helper, strips status prefix with regex `/^[ MADRCU?!]{1,2} +/`, fail-soft on non-zero exit.

### T-038: api.gitStatus client + useDirtySkills hook
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05 | **Status**: [x] completed
**Files**: `src/eval-ui/src/api.ts` (MODIFY), `src/eval-ui/src/hooks/useDirtySkills.ts` (NEW). 5 s default poll, listens to `studio:content-saved`, returns Set on every render derived from latest skill list via skillsRef.

### T-039: SkillRow dirty prop + amber dot indicator
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [x] completed
**Files**: `src/eval-ui/src/components/SkillRow.tsx` (MODIFY). New optional `dirty?: boolean` prop, renders 7×7px amber dot with `data-testid="skill-row-dirty-dot"`, `aria-label="Uncommitted changes"`, descriptive tooltip.

### T-040: Plumb dirtySkillIds through Sidebar / SectionList / PluginGroup
**User Story**: US-006 | **Satisfies ACs**: AC-US6-06 | **Status**: [x] completed
**Files**: `src/eval-ui/src/components/Sidebar.tsx` (MODIFY) — added `dirtySkillIds?: Set<string>` prop, threaded through 5 SectionList callsites + the inline `renderSkill` callbacks. `src/eval-ui/src/components/PluginGroup.tsx` (MODIFY) — added prop, passed to its SkillRow.

### T-041: Wire useDirtySkills in App.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05, AC-US6-06 | **Status**: [x] completed
**Files**: `src/eval-ui/src/App.tsx` (MODIFY). Hook called with `(visibleSkills, activeProject?.path ?? null)`; result passed to `<Sidebar dirtySkillIds={...}>`.

### T-042: Live smoke test: dirty dot round-trip
**User Story**: US-006 | **Satisfies ACs**: AC-US6-07 | **Status**: [x] completed
**Test Plan**: Built vskill@0.5.138, started `eval serve --root <greet-anton repo>` in browser, verified greet-anton row in AUTHORING > SKILLS section showed amber dot when SKILL.md was modified + NOTES.md added. Reverted edits, waited one poll cycle (≤5s), confirmed dot disappeared. Performed via Playwright preview tools against the real running studio — not mocked.
