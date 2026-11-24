# Review — 0877 final portability

Original verdict: fix required. Three confirmed medium findings, no critical or high findings. Remediation is committed; final independent root verification is pending.

Reviewer context: independent subagent reviewing T13 (9fc91cac7) and hook/CI fixes (6c98afff8, 9a9edda86) against combined SpecWeave HEAD 68102744b. Dashboard T12/T16 authored by this reviewer were excluded from independent approval. Root requested remediation after this review; the reviewer then authored T19/T20 and cannot independently approve those fixes.

## [medium] src/core/intent/portable-context.ts:48 — corrupt completion hides valid open work

At 9fc91cac7, portable discovery accepts a newer snapshot when updatedAt is null or execution metadata is malformed. The dashboard rejects that same snapshot. Reproduction with the built modules: a valid active revision 1 followed by revision 2 with state done and updatedAt null produces dashboard active + warning, while startup context says 0 open intents with no warning. The next agent loses the unfinished request from its summary.

Remediation 4bc26e486: move the portable intent types and complete persisted-record validator into pure core modules. Dashboard, startup context and handoff summaries share the validator. No dashboard runtime is imported by hooks. Invalid snapshots preserve the last valid state and disclose incomplete history. Two new regressions failed first and pass after the fix, including inline handoff evidence.

## [medium] src/templates/AGENTS.md.template:12 — added guidance breaks the existing template length gate

The added intent-board row takes AGENTS.md.template from 90 to 91 lines. Reproduced unchanged instruction-templates.test.ts:109: expected 91 <= 90, exit 1. Root first identified this in the full unit run; this reviewer independently reran and confirmed it.

Remediation 4bc26e486: remove one redundant blank line from both instruction templates. Portable intent guidance remains intact. All 17 original template tests pass; the limit and assertions were unchanged.

## [medium] src/core/hooks/handlers/session-start.ts:115 — absolute saved pointer loses a relocated handoff

T13 reads handoff-latest.txt as an absolute path, while a lightweight handoff lives in .handoff/HANDOFF.md and has no increment fallback. Reproduction: create a handoff, copy the project to another directory, delete the original; the moved handoff file exists but SessionStart returns an empty object. The previous write-pointer format predates T13, but T13's new discovery path fails this portability case.

Remediation ecaa15073: internal destinations are saved relative to the project; explicit external output paths remain absolute. Startup also checks owned canonical .handoff/HANDOFF.md and root HANDOFF.md files to recover legacy absolute pointers after relocation. Pointer targets must be regular owned handoff documents, verified with a bounded marker read. Escaping relative paths and relative symlink escapes are rejected; unrelated root handoff files are ignored. Three relocation/path-boundary regressions failed first and pass after the fix; the external-output preservation test passed before and after.

## Other reviewed changes

No confirmed regression in the Stop-hook session-ID correction or docs startup readiness changes. The fast path uses the same forbidden-path characters as session-state-manager; dot, space and Unicode fixture IDs remain Windows-valid. Ordinary inactive turns skip the worker, while explicit scoped auto sessions load it. The docs workflow pins the serving/crawling CLIs, waits for an HTTP success before crawling, fails after the readiness window and cleans up the spawned server. This was a source review; the reviewer did not claim a successful remote workflow run.

## Verification

- Initial independent hook/handoff selection: 3 files, 26 tests passed.
- T19 regressions: 2 failed first; template regression separately failed first. After remediation: 4 files, 47 tests passed, including existing dashboard, hook and unchanged template gates.
- T20 regressions: 3 failed first. After remediation: 2 files, 26 tests passed; final 11-test lightweight suite reran after the regular-file guard and passed.
- Full npm run build passed for T19 and T20; final TypeScript no-emit check and git diff --check passed.
- No browser automation, source publication, registry mutation or personal installation changes were performed by this reviewer during this pass.
