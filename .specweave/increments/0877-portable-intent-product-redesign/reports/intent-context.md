# Lightweight intent continuity

Commit `7c0ec901a`, based on SpecWeave `17b3ac847`. Worktree: `/tmp/specweave-0877-intent-context`.

Before this change, a project containing only lightweight intent cards produced no SessionStart work context. An explicit handoff omitted those requests, and the session hook did not follow the writer’s `handoff-latest.txt` pointer for no-increment handoffs. Three regression tests failed against the existing code.

The shared read-only intent summary now folds latest revisions from `.specweave/intents/board.jsonl`, excludes completed intents, and supplies at most three IDs/titles/states plus the total and file pointer. It reads at most 2 MiB, discloses unreadable/oversize histories, scrubs secrets, and changes no board state. SessionStart and explicit/inline handoffs reuse it. Handoffs link to the source board and retain redaction counts. SessionStart follows the existing explicit-handoff pointer. AGENTS/CLAUDE templates explain where a new harness can find unfinished small requests.

No model inference, native transcript scan, new CLI command, or per-tool hook is added. The bounded summary identifies planning state explicitly; it does not claim verification or close an increment.

Validation: five new regressions pass, including secret handling, unchanged source history, incomplete history, and oversized-file fallback. Nine suites / 88 hooks and handoff tests pass. `npm run build` passes at version2.1.0. Red/green/broad/build logs are in `artifacts/intent-context/`. Root review remains required; the authoring lane does not approve this change.
