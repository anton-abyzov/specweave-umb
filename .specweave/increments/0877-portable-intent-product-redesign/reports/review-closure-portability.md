# Independent closure portability review

**Verdict: confirmed fixed; no actionable findings in T-19/T-20.** Reviewed combined commit `8052b9bd9a331be8217e80644febd76dd7fd6549` from an isolated detached worktree, `/tmp/specweave-0877-closure-review`. Reviewer did not implement T-19 or T-20 and changed no source.

## Confirmed behavior

The pure validator in `src/core/intent/validation.ts` is now used by both `portable-context.ts` and the dashboard intent store. Shared types originate in core and are re-exported for dashboard projections. Required fields, safe positive revisions, timestamps, nullable execution facts, and execution metadata are checked consistently. A corrupt higher revision cannot turn unfinished work into completed work in SessionStart or the handoff while the dashboard still shows it unfinished. Both readers keep the last valid revision and explicitly disclose incomplete history.

`handoff-pointer.ts` serializes in-project output paths relative to the project. The writer uses that serializer, and SessionStart resolves pointers through ownership checks plus canonical owned fallback locations. Existing explicit external destinations remain absolute. The new resolver rejects parent traversal, foreign-platform absolute paths, control characters, missing/unowned files, and relative symlinks that escape the project. Ownership checks read at most an 8192-byte tail. Existing increment-local handoffs and legacy format markers remain supported.

Templates retain the existing gate unchanged: AGENTS is 90 lines and CLAUDE is 89 lines. The added continuity advice points to the intent board without expanding the always-loaded template budget.

## Independent verification

Node 22.20.0, `PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never`, no browser automation:

```text
Test Files  8 passed (8)
     Tests  98 passed (98)
```

Ran `lightweight-intents`, `minimal-hooks`, `work-board`, and `instruction-templates`, plus the four source handoff suites (`work-handoff`, `handoff-doc-format`, `handoff-secret-scrub`, `handoff-git-state`). Output: `review-closure-portability-tests.log`.

An independent disposable-filesystem probe passed 21 additional assertions covering custom relative paths, spaces/Unicode, relocation, external output, legacy markers, symlink/parent escape rejection, foreign Windows paths on POSIX, control characters, foreign ownership, large-document tail markers, and malformed intent records. Script and output: `review-closure-portability-probes.mts` / `.log`. `git diff --check` passed; source worktree stayed clean.

This focused review does not replace root’s combined full unit/coverage/build run. Explicit absolute external handoffs intentionally remain host-specific; portability is guaranteed for in-project output copied with the project.
