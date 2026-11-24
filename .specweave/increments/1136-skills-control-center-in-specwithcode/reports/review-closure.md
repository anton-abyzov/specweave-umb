# Review: 1136 skills control center closure

Verdict: fix first · risk: high · 42 changed files · 3 findings (1 high, 2 medium)
Reviewer context: fresh child session; did not implement the change. Reviewed merged commit `3e423ef4dec0878ca0e524cabf6664abce24146d` using `git show`, without changing the owning checkout. Review date: 2026-10-29.

## Evidence

The retained `reports/task-T-06.txt` records 46 passing focused server tests in four files at 2026-10-29T02:13:37Z. The task ledger records the broader contracts, authorization, inventory and web tests. These are prior run receipts, not a new execution. No `reports/verify.json` existed at review time; the parent is performing fresh closure/release verification. No live settings or provider turns were used.

## [high] Plugin Undo loses the target after the plugin is disabled

`apps/server/src/project/ProjectSkillsActionsRpc.ts:86` resolves every action, including the Undo enable action, through a currently discovered skill row. `apps/server/src/provider/Drivers/ClaudeSkills.ts:737` drops a plugin entirely when its merged `enabledPlugins` value is false. After a successful Turn off plugin and the triggered rescan, that plugin's skill has no Claude presence (and ordinarily no row), so the inverse toggle fails with `skill_not_found`; even a row retained through another provider fails `presenceOf` in `ProjectSkillsToggles.ts:103`. This breaks the promised Undo on the normal successful path. The current toggle tests supply a fixed context directly and do not exercise disable → rescan → resolve → Undo. Keep a validated installed-plugin target addressable after disabling, or use a server-issued reversible action receipt with the original target; test the complete round trip.

## [medium] The per-skill switch for Claude plugin skills reports a change Claude ignores

`apps/server/src/project/ProjectSkillsToggles.ts:186` plans a `skillOverrides` write for every Claude presence, including `scope: "plugin"`, and line 233 reports the planner's effective state. `apps/web/src/components/settings/ProjectSkillActions.logic.ts:58` exposes that switch without excluding plugins. Claude plugin discovery explicitly does not apply `skillOverrides` (`ClaudeSkills.ts:703`) and emits plugin skills as enabled (`ClaudeSkills.ts:785`). The existing provider test at `ClaudeSkills.test.ts:1205` documents this behavior. Thus disabling a plugin skill reports success/off while the agent still loads it. Refuse this unsupported operation on the server and show the whole-plugin control with a reason in the UI, unless an actual supported per-skill mechanism is available.

## [medium] Update to latest can apply a different version than the confirmed preview

`apps/server/src/project/ProjectSkillsActions.ts:378` reads the registry again on both preview and apply and picks its first version; `ProjectSkillsActions.ts:426` binds the preview only to the lock hash. If version B is published after a preview for version A, the unchanged lock passes the apply check and version B is installed without being previewed. `ProjectSkillControls.tsx:286` sends the original `update-latest` action, so the client does not pin the previewed target either. Bind the selected version in the preview/expected data and refuse drift, or convert the proposal to an exact version action while preserving the prior pin policy. Add a deterministic changing-registry fixture.

## Other inspected areas

The action RPC scope selection distinguishes Claude settings-file writes from operations that invoke a CLI/app server. Fleet push validates machine ids and version provenance, groups by destination scope, passes each destination project id, and preserves one result per selected machine. Fixed argv construction avoids shell evaluation. The earlier fixes for legacy global lock scope, nested project lock selection, overridden config writes, and higher-precedence Claude local settings are present in the merged source.

The findings above are new closure-review findings, not claims that the earlier reviewers left their reported findings unresolved. No release or installed acceptance is claimed by this report.
