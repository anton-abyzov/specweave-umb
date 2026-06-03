# Tasks: 0870 Restore dead hooks

### T-001: Restore + register the 5 non-blocking hooks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-03
**Test Plan**: Given the recovered handlers, When copied back + added to HANDLERS, Then `specweave hook <each>` dispatches to the handler (no longer safe-default); KNOWN_UNROUTED loses those 5.

### T-002: Routed tests for the 5 restored hooks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-02
**Test Plan**: Given a temp SpecWeave repo, When `hookRouter('post-tool-use-analytics', …)` runs, Then an analytics event is appended; analogous routed assertions for session-start (stale auto-mode cleared), post-tool-use (event queued), stop-sync (queue dedup/cleared), stop-reflect (approve). All return safe shape, none block.

### T-003: Implement blocking stop-auto handler
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03
**Test Plan**: Given active auto-mode.json + pending tasks, When `hookRouter('stop-auto', …)`, Then `decision:block` with a continue reason naming the increment; all-complete → block `all_complete_needs_closure`; no/inactive/stale auto-mode → approve.

### T-004: stop-auto turn-counter safety + never-throw
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-04, AC-US2-05
**Test Plan**: Given `.stop-auto-turns` > maxTurns, When routed, Then approve (safety stop) + counter cleared; each block increments the counter; any internal error → approve.

### T-005: Empty the parity guard + full suite green + version bump
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03
**Test Plan**: Given all 6 registered, When KNOWN_UNROUTED emptied, Then hook-wiring-parity passes; `npx vitest run src/core/hooks` fully green; `npm run build` clean; package patch-bumped.
