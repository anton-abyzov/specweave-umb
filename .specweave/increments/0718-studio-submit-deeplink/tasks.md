# Tasks: Local Studio Submit-your-skill deep-link

Project: vskill-platform | Test mode: TDD (strict) | Coverage target: 90%

---

## US-002: Workspace repoUrl resolver

### T-001: [RED] Failing tests — `normalizeGitHubRemote` matrix
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given the input matrix:
  - `git@github.com:foo/bar.git` → `https://github.com/foo/bar`
  - `git@github.com:foo/bar` → `https://github.com/foo/bar`
  - `https://github.com/foo/bar.git` → `https://github.com/foo/bar`
  - `https://github.com/foo/bar/` → `https://github.com/foo/bar`
  - `git@gitlab.com:foo/bar.git` → `null`
  - `https://gitlab.com/foo/bar` → `null`
  - `https://github.example.com/foo/bar` → `null` (host check)
  - `not-a-url` → `null`
  - `""` → `null`
- When `normalizeGitHubRemote(input)` is called
- Then output matches the table
- Tests in `vskill-platform/src/app/studio/lib/repo-url-normalize.test.ts`. MUST fail RED.

---

### T-002: [GREEN] Implement `normalizeGitHubRemote`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-001
- When `normalizeGitHubRemote` is implemented per plan.md
- Then T-001 tests turn green

---

### T-003: [RED] Failing tests — `/api/v1/studio/workspace-info` endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- Given the route does not exist yet
- When `GET /api/v1/studio/workspace-info` is called and `execFile('git', ['-C', root, 'config', ...])` is mocked to return `git@github.com:owner/repo.git`
- Then response is `{ repoUrl: "https://github.com/owner/repo" }`
- Given execFile rejects (git not on PATH)
- Then response is `{ repoUrl: null }` (200, not 500)
- Given Studio workspace root does not exist (`fs.access` throws)
- Then response is `{ repoUrl: null }` and execFile is NEVER called (sanity check before shelling)
- Given the same workspace queried twice
- Then `execFile` is called once (per-process cache hit)
- **Static check**: assert that the route uses `execFile` (not `exec`) and passes argv (no shell interpolation possible) — read source and grep
- Tests in `vskill-platform/src/app/api/v1/studio/workspace-info/route.test.ts`. MUST fail RED.

---

### T-004: [GREEN] Implement workspace-info route + per-process cache
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-003
- When the route + `workspaceInfoCache` Map are implemented per plan.md
- Then T-003 tests turn green
- Implementation files: `src/app/api/v1/studio/workspace-info/route.ts`, `src/app/studio/lib/workspace-info-cache.ts`

---

## US-003: Click telemetry to submit-click endpoint

### T-005: [RED] Failing tests — `useSubmitDeepLink` hook (debounce, telemetry, fallback, swallow-error)
**User Story**: US-003 (also US-001 + US-002 wiring) | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US2-06, AC-US2-07, AC-US2-08, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed

**Test Plan**:
- Given the hook does not exist yet
- When invoked twice within 500ms
- Then only the first invocation triggers `window.open` (debounce, AC-US3-03)
- Given a workspace with `repoUrl: "https://github.com/foo/bar"`
- When invoked
- Then `window.open` is called with `https://verified-skill.com/submit?repoUrl=https%3A%2F%2Fgithub.com%2Ffoo%2Fbar` and target `_blank` and features `noopener,noreferrer` (AC-US1-05)
- Given a workspace returning `repoUrl: null`
- When invoked
- Then `window.open` URL is `https://verified-skill.com/submit` with no `?repoUrl=` (AC-US2-05)
- Given `/api/v1/studio/workspace-info` doesn't respond within 200ms
- When invoked
- Then `window.open` still fires within 250ms total, with no `?repoUrl=` (AC-US2-06)
- Given `URL` from a current page `/studio/find?q=react`
- When invoked
- Then telemetry POST body includes `q: "react"` (AC-US3-01)
- Given telemetry endpoint returns 500
- When invoked
- Then `window.open` still fires; no error thrown to user (AC-US3-04)
- Given `window.open` returns `null` (popup blocker)
- When invoked
- Then a toast with a clickable anchor is rendered (AC-US2-08)
- Given a successful click
- Then `localStorage.setItem('studio.lastSubmitOpenedAt', <ISO>)` is called (FR-002)
- Tests in `vskill-platform/src/app/studio/hooks/useSubmitDeepLink.test.ts`. MUST fail RED.

---

### T-006: [GREEN] Implement `useSubmitDeepLink` hook
**User Story**: US-001 + US-002 + US-003 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US2-06, AC-US2-07, AC-US2-08, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-005
- When the hook is implemented per plan.md (debounce ref, AbortController + timeout, URL constructor, fetch fire-and-forget, window.open fallback, localStorage swallow)
- Then T-005 tests turn green
- File: `src/app/studio/hooks/useSubmitDeepLink.ts`

---

## US-001: Submit CTA placements

### T-007: [RED] Failing tests — SubmitNavButton renders, has correct ARIA, calls hook on click
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- Given `SubmitNavButton` does not exist
- When rendered in `StudioLayout`
- Then it appears in the nav with label "Submit your skill", upload icon `aria-hidden`, and ARIA label including "opens new tab"
- When clicked
- Then `useSubmitDeepLink` callback is invoked once
- Tests in `vskill-platform/src/app/studio/components/SubmitNavButton.test.tsx`. MUST fail RED.

---

### T-008: [GREEN] Implement SubmitNavButton + StudioLayout integration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-007
- When `SubmitNavButton.tsx` is implemented and added to `StudioLayout`
- Then T-007 tests turn green
- Verify single source of truth: both this button AND the find-page binding (T-009) call the same `useSubmitDeepLink` hook (no duplicated logic)

---

### T-009: [GREEN] Bind 0717's `SubmitDeepLink` stub to `useSubmitDeepLink`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, FR-003 | **Status**: [x] completed

**Test Plan**:
- Given 0717's `SubmitDeepLink.tsx` stub component exists (or create it as a fallback if 0717 hasn't shipped)
- When the stub's `onClick` is bound to the `useSubmitDeepLink` hook
- Then a render in the find-page context fires the same telemetry + window.open as the nav button
- Coordinate with 0717 — if their stub uses a different prop signature, adjust hook usage accordingly (no breaking the contract)

---

## Integration

### T-010: [E2E] Playwright golden path — nav click + find-page click + URL assertion
**User Story**: All | **Satisfies ACs**: AC-US1-05, AC-US2-05, AC-US3-01 | **Status**: [x] completed

**Test Plan**:
- Given Studio dev server is running with MSW handlers for telemetry endpoint
- When Playwright clicks the nav SubmitNavButton in a workspace whose mocked git remote is `git@github.com:foo/bar.git`
- Then `page.evaluate(() => window.lastOpenedUrl)` (test-time capture of `window.open`) returns `https://verified-skill.com/submit?repoUrl=https%3A%2F%2Fgithub.com%2Ffoo%2Fbar`
- AND a POST to `/api/v1/studio/telemetry/submit-click` was recorded by MSW with `repoUrl: "https://github.com/foo/bar"`
- When Playwright navigates to `/studio/find?q=react` and clicks the banner CTA
- Then the same URL is opened AND the telemetry payload includes `q: "react"`
- When Playwright runs in a workspace with no git remote (mock `execFile` rejects)
- Then the URL has no `?repoUrl=`
- File: `vskill-platform/tests/e2e/studio-submit-deeplink.spec.ts`

---

### T-011: [REFACTOR + LIVE] Switch from MSW telemetry to live 0716 endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed (deferred live-switch documented)

**Test Plan**:
- Given sibling 0716 has deployed `/api/v1/studio/telemetry/submit-click` to dev Worker
- When the MSW gate is disabled (`STUDIO_USE_MOCKS=false`)
- Then the same Playwright spec from T-010 passes against the live endpoint
- Smoke: a row appears in `StudioTelemetry` table with `kind="submit-click"` after the click
- Document any contract drift in `reports/contract-drift-0718.md` (expected: zero)

---

## Task summary

| Task | US | TDD phase | Effort |
|---|---|---|---|
| T-001 | US-002 | RED | S |
| T-002 | US-002 | GREEN | S |
| T-003 | US-002 | RED | M |
| T-004 | US-002 | GREEN | M |
| T-005 | US-001+002+003 | RED | M |
| T-006 | US-001+002+003 | GREEN | M |
| T-007 | US-001 | RED | S |
| T-008 | US-001 | GREEN | S |
| T-009 | US-001 | GREEN (bind) | S |
| T-010 | All | E2E | M |
| T-011 | US-003 | LIVE switch | S |

Sequencing: T-001→T-002 (normalizer first; pure function, fastest path to green). T-003→T-004 (resolver depends on normalizer). T-005→T-006 (hook depends on resolver). T-007→T-008 and T-009 (placements depend on hook). T-010 needs everything green. T-011 gated on 0716 deploy.
