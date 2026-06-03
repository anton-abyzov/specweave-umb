# Tasks: 0869 Hook wiring audit + recurrence guard

### T-001: RED — parity test detects the 6 dead hooks (empty allowlist)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-03
**Test Plan**:
- Given the plugin hooks.json and the router HANDLERS, When the parity test runs with KNOWN_UNROUTED empty, Then it FAILS listing exactly session-start, post-tool-use, post-tool-use-analytics, stop-reflect, stop-auto, stop-sync.
- Given the live 4, When asserted, Then user-prompt-submit/pre-tool-use/pre-compact/stop are all registered.

### T-002: GREEN — allowlist the 6 known-dead + stale-entry guard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test Plan**:
- Given KNOWN_UNROUTED = the 6 dead names, When the test runs, Then it passes (invoked ⊆ registered ∪ KNOWN_UNROUTED).
- Given a KNOWN_UNROUTED entry not present in hooks.json, When the stale-entry assertion runs, Then it fails — so restoring a hook forces allowlist cleanup.

### T-003: VERIFY — audit report complete + suite green
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-04
**Test Plan**:
- Given the report, When reviewed, Then all 10 hooks, the root-cause commit (0f81519b1), connected places, and the per-hook restoration plan are documented.
- Given the full hooks suite, When `npx vitest run src/core/hooks` runs, Then all pass.
