# Review — 0877 SpecWeave product site and minimal hooks

Verdict: ship · original medium finding resolved in `6c98afff8` · 0 open findings (0 critical, 0 high).

Reviewer context: independent subagent for T-03. This reviewer authored the separate Verified Skills platform change and does **not** approve that change here.

Scope: SpecWeave `v2.0.3..1489f3891` in `/tmp/specweave-0877-root`, plus the existing router, Stop/session handlers, session-ID validation, and auto-mode marker creation needed to assess compatibility. Dashboard, sync, package release, and personal skill removal are outside this review.

## Resolved [medium] plugins/specweave/hooks/run.mjs:21 — fast path rejects supported session identifiers

The new session-marker lookup requires `CLAUDE_SESSION_ID` to match `[a-zA-Z0-9_-]+`. Existing `validateSessionId()` accepts `conversation.01` (it rejects path separators, `..`, and null bytes), and `stop.ts` resolves that per-session directory. When that session has `active: true` and the global fallback has `active: false`, the new fast path reads the global file and returns `{}`. The explicitly active session therefore loses its continuation loop.

Reproduced against the old supervisor and the new supervisor with the same built router, project, pending task, pending AC, and marker files:

```text
CLAUDE_SESSION_ID=conversation.01
.specweave/state/sessions/conversation.01/auto-mode.json: {"active":true,"incrementIds":["0001-review"]}
.specweave/state/auto-mode.json: {"active":false}
v2.0.3: {"decision":"block","reason":"0001-review: 1 task(s) / 1 AC(s) remain. Run sw:do to continue."}
1489f3891: {}
```

The built `validateSessionId('conversation.01')` returns that identifier without error. The relevant launcher lines and the validator were reopened after reproduction. Reproduction script: `artifacts/site-hooks-review/repro-session-id.cjs` (the worktree path is declared at its top).

Fix: use the same path-safe session-ID policy as the state manager in the zero-dependency launcher, retaining traversal rejection, and add a scoped-marker case with a supported dotted identifier and a conflicting global marker.

## Verification and observations

- Three focused hook suites passed: 32 tests, including default manifest parity, worker-free ordinary Stop events, active auto mode, legacy launcher compatibility, and private CLI cache behavior. Log: `artifacts/site-hooks-review/hooks-tests.log`.
- Production site E2E passed with explicit `headless: true`, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`: homepage, Product, Integrations, Getting started, integration ownership docs, clipboard copying, keyboard/card selection, integration disclosure, mobile navigation, no horizontal overflow, no runtime errors. Log/screenshots: `artifacts/site-hooks-review/`.
- New site board is explicitly labeled illustrative; it does not present example metrics as user telemetry. Docs distinguish card state from increment verification, explicit handoff from automatic snapshots, and model/provider/harness roles.
- Optional-integration content explicitly limits pull to reporting and labels future reconciliation requirements as future work. It does not guarantee live bidirectional sync.
- PreToolUse and PreCompact are removed from the default manifest while compatibility handlers remain callable. Ordinary Stop events avoid the CLI worker; disabled hooks return before the worker.
- No critical/high correctness or security regression was confirmed in this scope. Existing unrelated README claims were not treated as new diff findings. This review is not a whole-repository audit or a deployed-service check.

## Fix verification

Rechecked `6c98afff8` independently with the original reproduction. The corrected launcher and v2.0.3 both return the same pending-work block for `conversation.01`. The launcher now matches the session manager policy: non-empty IDs without slash, backslash, `..`, or null are accepted. Three focused hook suites pass after the fix: 35 tests. No other code was changed by this reviewer.
