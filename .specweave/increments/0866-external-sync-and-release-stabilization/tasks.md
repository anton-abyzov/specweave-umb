# 0866 — Tasks

### T-001: Fix onboarding command strings (init + auto)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a fresh temp dir → When `specweave init` runs on the new build → Then "Next steps" shows `specweave create-increment` (a real command) and never `specweave increment "feature"`.
**Note**: Already applied in `src/cli/helpers/init/next-steps.ts:201` and `src/cli/commands/auto.ts:321`.

### T-002: Regression test for init next-steps output
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given the init next-steps renderer → When it prints the guided commands → Then the output contains `create-increment` and does NOT contain `increment "`. Add a `.test.ts` (Vitest) asserting both.

### T-003: Build specweave + publish 1.0.586 to npm
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given local 1.0.586 with the F1/F2 fixes → When `npm run rebuild` succeeds and `npm publish --otp <recovery-code>` runs → Then `npm view specweave@1.0.586 version` returns 1.0.586. Obtain OTP recovery code via Obsidian; STOP+report if unavailable (do not burn codes guessing).

### T-004: Create GitHub releases v1.0.585 + v1.0.586, fix "Latest"
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given the tags on origin → When `gh release create v1.0.585` (backfill, not latest) and `gh release create v1.0.586 --latest` run with CHANGELOG notes → Then both releases exist and `gh release view --json isLatest` shows 1.0.586 is Latest. Push `v1.0.586` tag; delete stray local tag `v1.0.58`.

### T-005: JIRA Story issue type
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given SWE2E lacks "Story" → When Story is added to its issue-type scheme (or US→available-type mapping is configured) → Then `specweave sync-health` reports JIRA issue types ✓ with no "Missing issue types: Story" warning.

### T-006: Live round-trip — create test increment, sync to all 3, verify
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given a throwaway single-US increment (e.g. 0900-sync-roundtrip-test) with a fully-filled spec.md → When `node repositories/anton-abyzov/specweave/bin/specweave.js sync-progress 0900-… --force` runs from repo root → Then a GitHub issue, a Jira SWE2E epic, and an ADO SpecWeaveSync work item are created, and their URLs/IDs are written into the increment's metadata.json. Verify each link resolves.

### T-007: Cleanup live round-trip artifacts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given the items created in T-006 → When `gh issue close`, Jira delete, and ADO delete run → Then none remain in any tracker, the test increment is abandoned/removed, and no externalLinks pollution is left behind.

### T-008: Re-verify health green end-to-end
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: AC-US2-01, AC-US4-01 | **Status**: [x] completed
**Test**: Given the published 1.0.586 → When `npm i -g specweave@1.0.586` then `specweave sync-health` runs in the umbrella repo → Then GitHub ✓, Jira ✓ (incl. issue types), ADO ✓ (no false "missing credentials").
