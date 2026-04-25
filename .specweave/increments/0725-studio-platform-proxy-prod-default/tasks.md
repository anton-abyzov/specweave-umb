# Tasks: Studio platform-proxy default to verified-skill.com (502 hotfix)

## Task Notation

- `T-###`: Task ID
- `[ ]`: Not started
- `[x]`: Completed

---

### T-001: [TDD-RED] Pin default URL to verified-skill.com via failing unit test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
  - Given: `VSKILL_PLATFORM_URL` is unset (the test deletes it after saving the original)
  - When: `getPlatformBaseUrl()` is called
  - Then: it returns `"https://verified-skill.com"` exactly (no trailing slash, no port)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/platform-proxy.test.ts` (add one `it()` inside the existing `describe("getPlatformBaseUrl")` block; save+restore `process.env.VSKILL_PLATFORM_URL` around the assertion)
**Notes**:
  - Hermetic — no live network call. The existing `beforeAll` sets the env to a fake-port URL, so the new test must `delete` before asserting and restore in `finally`.
  - At RED time the assertion fails because `DEFAULT_PLATFORM_URL` is still `"http://localhost:3017"`.

---

### T-002: [TDD-GREEN] Switch DEFAULT_PLATFORM_URL to https://verified-skill.com
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
  - Given: T-001's failing test
  - When: `DEFAULT_PLATFORM_URL` in `src/eval-server/platform-proxy.ts:34` is changed to `"https://verified-skill.com"`
  - Then: T-001 passes; `npx vitest run src/eval-server/__tests__/platform-proxy.test.ts` reports 13/13 green (12 pre-existing + 1 new)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts` (line 34 — single literal change)

---

### T-003: [REFACTOR] Update header + inline comments to reflect new default
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: code change from T-002 landed and tests are green
  - When: header block (lines 1–29) and the `Target URL is configurable…` inline note are rewritten to say `default https://verified-skill.com`, mention parity with `src/api/client.ts` `DEFAULT_BASE_URL`, and document the explicit local-dev opt-in
  - Then: a `grep -n 'localhost:3017' src/eval-server/platform-proxy.ts` shows the constant is gone and only appears (if at all) inside the local-dev opt-in example sentence; tests still 13/13 green
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts` (header comment + the inline `// - Target URL is configurable…` block)

---

### T-004: Run full platform-proxy test file + targeted regression
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**:
  - Given: T-001..T-003 landed
  - When: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-server/__tests__/platform-proxy.test.ts` is executed
  - Then: 13/13 tests pass — including the env-set path, trailing-slash strip, the 502-on-unreachable envelope, GET/POST forwarding, hop-by-hop strip, and SSE content-type passthrough — proving the default-change doesn't regress the existing contract
**Files**:
  - none (verification only)

---

### T-005: Rebuild vskill dist and sanity-check the compiled default
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**:
  - Given: T-004 green
  - When: `cd repositories/anton-abyzov/vskill && npm run build` succeeds, then `node -e "process.env.VSKILL_PLATFORM_URL=''; import('./dist/eval-server/platform-proxy.js').then(m => console.log(m.getPlatformBaseUrl()))"` is executed
  - Then: build completes with no TS errors; node prints `https://verified-skill.com`
**Files**:
  - none (build artifact only — `dist/eval-server/platform-proxy.js` regenerated)

---

### T-006: Live verification against the running studio (port 3162)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**:
  - Given: T-005 green AND the existing `vskill studio` process on port 3162 is restarted to pick up the rebuilt dist
  - When: a `curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:3162/api/v1/skills/check-updates" -X POST -H 'Content-Type: application/json' -d '{"skills":["anthropic-skills/pdf"]}' -m 6` is issued without `VSKILL_PLATFORM_URL` set
  - Then: HTTP code is `200` (was `502` before the fix); a follow-up `curl -s "http://localhost:3162/api/v1/skills/stream?skills=anthropic-skills%2Fpdf" -m 4 -o /tmp/sse.txt` produces a body that contains `: connected` (proxied SSE keepalive)
**Files**:
  - none (live verification only)

---

### T-007: Commit + sync sequence
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: T-001..T-006 green
  - When: in `repositories/anton-abyzov/vskill`, the platform-proxy.ts + platform-proxy.test.ts changes are committed with a one-line subject under 72 chars referencing 0725 (no AI/Claude/Anthropic mentions per project commit rules), and pushed
  - Then: `git status` is clean in the vskill repo; the umbrella's `.specweave/increments/0725-…` files have been written (spec.md, plan.md, tasks.md, metadata.json) and tracked
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts`
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/platform-proxy.test.ts`
