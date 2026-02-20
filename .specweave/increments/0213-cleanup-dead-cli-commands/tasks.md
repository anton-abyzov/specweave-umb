# Tasks: Cleanup Dead CLI Commands

### T-001: Delete orphaned version.ts
**Satisfies ACs**: AC-01 | **Status**: [x] completed
Delete `src/commands/version.ts` which exports `versionCommand()` that is never imported or used anywhere in the codebase.

### T-002: Verify tests pass
**Satisfies ACs**: AC-02 | **Status**: [x] completed
Run `pnpm test` in vskill to confirm no regressions.
