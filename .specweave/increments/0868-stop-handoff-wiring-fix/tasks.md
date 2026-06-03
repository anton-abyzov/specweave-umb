# Tasks: 0868 Stop-handoff wiring fix

### T-001: RED — wiring pin test + routed dispatch test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-02, AC-US1-03
**Test Plan**:
- Given the shipped `plugins/specweave/hooks/hooks.json`, When I parse its `Stop[]` group, Then a command invoking `specweave hook stop` (word-boundary, not `stop-reflect/stop-auto/stop-sync`) must be present. (Fails RED today.)
- Given a temp SpecWeave git repo with `.specweave/state/auto-mode.json`, When `hookRouter('stop', '{"reason":"auto run paused"}')` runs, Then a handoff doc is written AND the result is `{ continue: true }`.
- Given the same repo WITHOUT `auto-mode.json`, When `hookRouter('stop', '{}')` runs, Then no handoff doc is written AND the result is `{ continue: true }`.

### T-002: GREEN — wire `specweave hook stop` into hooks.json Stop[]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test Plan**:
- Given the fix, When the test suite from T-001 runs, Then the pin test and both routed tests pass.
- Given the edit, When I diff `hooks.json`, Then only one command object is added to `Stop[]` and `stop-reflect/stop-auto/stop-sync` are byte-identical.

### T-003: REFACTOR/VERIFY — full handoff + hook suite green, PreCompact untouched
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-04
**Test Plan**:
- Given the fix, When `npx vitest run` for `pre-compact.test.ts` + the new wiring test + `src/core/session/*handoff*.test.ts` runs, Then all pass (no regression).
- Given `npm run build`, When tsc compiles, Then `dist/` builds clean.
- Manual: `echo '{"reason":"x"}' | node bin/specweave.js hook stop` writes `handoff-latest.md` only when `auto-mode.json` is present.
