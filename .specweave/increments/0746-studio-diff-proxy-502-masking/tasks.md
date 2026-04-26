# Tasks: Studio diff proxy 502 masking

> Strict TDD per `.specweave/config.json`. RED → GREEN → REFACTOR.
> All paths relative to `repositories/anton-abyzov/vskill/`.

### T-001: RED — failing test for upstream 400 passthrough
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a mocked `fetch` that resolves to `{ ok: false, status: 400, json: () => ({error: "Version '1.0.1' not found"}) }`
- **When** the diff proxy handler is invoked for `/api/skills/p/s/versions/diff?from=1.0.1&to=1.0.2`
- **Then** the response status is `400` AND the response body equals `{error: "Version '1.0.1' not found"}`
- **Test file**: extend `src/eval-server/__tests__/version-routes.test.ts` with new cases under T-010 describe
- **RED**: current code emits `502 Platform API unavailable`

### T-002: RED — failing test for upstream 404 passthrough
**User Story**: US-002 | **Satisfies ACs**: AC-US1-02, AC-US2-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** mocked fetch returns `404` with `{error: "Skill not found"}`
- **When** the proxy is invoked
- **Then** response is 404 with the same body

### T-003: RED — non-JSON upstream body fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** mocked fetch returns `500` with `json()` rejecting (non-JSON body)
- **When** the proxy is invoked
- **Then** response is 500 with body `{error: "Upstream returned 500"}`

### T-004: GREEN — implement pass-through in api-routes.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** failing tests T-001/T-002/T-003
- **When** I replace the `if (!resp.ok)` branch at api-routes.ts:1913-1916 to read `resp.json()` (with try/catch fallback) and forward `resp.status` + body
- **Then** all RED tests pass; existing fetch-failure test still gets 502
- **Files modified**: `src/eval-server/api-routes.ts`

### T-005: VERIFY — full test suite + build
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the fix is in
- **When** I run `npx vitest run src/eval-server` and `npm run build`
- **Then** all tests pass; tsc produces no errors
- **No files modified** — pure verification.

### T-006: VERIFY — Playwright e2e against fresh studio install
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a freshly published vskill patch (e.g. 0.5.125) is installed via `npx vskill@0.5.125`
- **When** Playwright calls `getVersionDiff()` for a `from` version that isn't published upstream
- **Then** the response is `400` with the real upstream error message — NOT `502 Platform API unavailable`.
