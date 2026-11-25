<!-- specweave review: reviewer=gpt-6-sol model=gpt-6-sol family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8dea0b33947728d756497b46285eadee97ea23b3 head=6e2061f8707fb65010bb4f1d6269011e9d8c8c77 at=2026-11-25T14:07:34.601Z -->
# Review: 1481 Claude MCP form elicitation
Verdict: fix first
Reviewer context: fresh Codex session; reviewed `6e2061f8707fb65010bb4f1d6269011e9d8c8c77` (PR #929).

## [high] packages/shared/src/mcpElicitationForm.ts:360 required `__proto__` field is silently omitted

An MCP schema with a required string property named `__proto__` passes parsing at `mcpElicitationForm.ts:243-249`. Validation reads the inherited prototype from an empty answers object at line 363, then `errors["__proto__"] = ...` at line 364 does not create an own error. Line 367 returns `ok: true` with empty content, and `ClaudeMcpElicitation.ts:173-175` sends `accept` with that partial content. The same plain-object assignment drops a valid value. A Node reproduction confirmed `errorKeys: []`, `contentKeys: []`, `ok: true`. Fix: use null-prototype dictionaries or Maps for values, errors and content, and test prototype-named required fields.

## [high] apps/server/src/orchestration-v2/Orchestrator.ts:9029 missing card bypasses authorization and redaction

`ClaudeMcpElicitation.ts:325-331` emits the pending runtime request before its form turn item, as separate provider events. In that interval, `getRuntimeResponseContext` can return the request with `item: undefined` (`ProjectionStore.ts:5348-5358`). `checkFormResponse` then returns `undefined` (`ClaudeFormResponses.ts:101-102`), so `Orchestrator.ts:9037` falls back to raw `command.answers`, and lines 9071 and 9269 persist them in the resolved request and effect. An accept with `answers: {}` also bypasses the form's person-only check. Fix: identify Claude MCP forms from the request itself and reject responses until the matching form item is present; never take the generic answers path for such a request.

Verification: PR diff read with `gh pr diff 929 -R anton-abyzov/specwithcode`; cited lines re-opened on the exact head. No full suite run. The existing `reports/verify.md` predates round two and reports missing PyYAML and app dependencies in this checkout, so it is not a green verification of this head.
