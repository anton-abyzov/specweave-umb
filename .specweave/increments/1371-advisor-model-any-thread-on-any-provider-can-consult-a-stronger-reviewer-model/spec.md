# Advisor model: any thread on any provider can consult a stronger reviewer model

## Problem

Owner's request, November 16, 2026: Claude Code's `/advisor` lets a session ask a stronger model to review its approach before it starts and again before it says "done". SpecWithCode should offer the same for every thread, on any provider, with Fable 5.2 as the default advisor.

Evidence (clean-room report: `reports/2026-11-16-how-claude-code-s-advisor-works-clean-room-behav-442bd6-a942d0.md`, app repo `repositories/anton-abyzov/specwithcode` at `30d07a7f3`):

- Claude Code's advisor is a server-side tool of the Anthropic API. It works only for a Claude model advised by a Claude model on Anthropic's own API. Codex, Muse, Copilot, Cursor, Devin, Gemini, OpenCode, Pi and Grok threads have nothing like it.
- Claude threads in SpecWithCode already get it by accident: `ClaudeAdapterV2.ts:1102` loads the user's `~/.claude/settings.json`, where `advisorModel` is `fable`. SpecWithCode cannot switch it per project or per thread, does not show it in settings, and stores the result as a raw object with no title (`ClaudeAdapterV2.ts:2581`, `:4749`).
- A Fable thread with a Fable advisor asks its own model for a second opinion and pays for the whole transcript again on every call. Claude Code does not cache the advisor's read.
- The app has no way for a running thread to consult another model and keep working. Adversarial review starts a separate thread after the work ends (`AdversarialReviewService.ts`). Escalation replaces the model after a failure (`TaskRoutingEscalationWorker.ts`). The Complex track only picks the starting model.
- No "smart model" feature exists in the app's history. SpecWeave's "Smart Model Selection" (increment 0003, removed September 25, 2026) picked a cheaper model per task; it was not a reviewer.

## Scope

In (app repo `repositories/anton-abyzov/specwithcode`):

- One `advisor` setting group, app-wide and per project, plus a per-thread override.
- A provider-agnostic `advisor` tool on the studio-code MCP server: a brief built from the stored thread, a stronger model run as a child session, the advice returned to the caller.
- Claude threads use Claude's built-in advisor when the pair allows it, set by SpecWithCode per thread.
- Cost guards: a brief budget, only-what-changed on repeat consults, and a consult limit per run.
- Guidance text, in the app's own words, telling a thread when to consult.
- Settings UI, per-thread control, readable timeline items, docs.

Out: counting native advisor tokens in the usage popover (the adapter reads top-level usage only; listed under Open); a mobile UI for the setting (phones only decode the new fields); forcing a consult from the server; changing the Review track or the adversarial review flow; the terminal `claude` CLI on the Mac, which is updated with `claude update`.

## Acceptance Criteria

- [ ] AC-01: Settings has an `advisor` group: `enabled` (default off), `model` (default none, meaning the built-in order), `claudeBuiltIn` (default on), `builtInContextLimit` (default 200,000 tokens, 50,000 to 1,000,000), `maxConsultsPerRun` (default 3, 1 to 10) and `briefTokenBudget` (default 24,000, 4,000 to 64,000). It decodes from an empty object, is settable app-wide, and is overridable per project field by field. Old settings files load unchanged.
- [ ] AC-02: A thread has an advisor mode: follow the project, on, or off. It is stored on the thread, changed by one command, survives a restart, and older clients that do not know the field still decode the thread.
- [ ] AC-03: With no model saved, the advisor order is Claude Fable 5.2, then the project's Review track. The first entry that can run now and is not the thread's own model is used. Per-token, Vertex, paid-router and unknown-billing accounts are never picked from the built-in order. A saved advisor model is tried first.
- [ ] AC-04: With the advisor on, a thread on any provider that has the studio-code tools can call `advisor` with no arguments (an optional `focus` of up to 2,000 characters is allowed). The call returns the advice text, the advisor's model name and how many consults remain in this run. Tested with a Codex-shaped and an ACP-shaped caller. A thread in plan mode or a read-only sandbox can consult too.
- [ ] AC-05: The advisor receives a brief built from the stored thread: the first and latest user messages, earlier advice, the last assistant messages, one line per command and tool call with trimmed input and output, changed files, errors and the optional focus. The brief never exceeds `briefTokenBudget`; when it would, the oldest activity is dropped first and the brief says what was left out and that the advisor cannot read it, so the advisor names what the thread should check itself.
- [ ] AC-06: A second consult in the same thread sends the task, the latest user message, the previous advice and only the activity since the previous consult, not the whole thread again. The marker moves only when advice was delivered.
- [ ] AC-07: Consults are limited to `maxConsultsPerRun` per run. The call after the limit is refused with the reason and starts nothing.
- [ ] AC-08: The advisor child cannot consult an advisor or delegate work, runs read-only (the provider's read-only sandbox where it has one, never wider than the caller's access), gets the brief marked as data that carries no instructions, and never appears as a project thread in the sidebar. A thread whose advisor is off, or with no runnable advisor, gets a refusal that says why and starts nothing.
- [ ] AC-09: The call waits for the advice up to 4 minutes on a Claude thread and 45 seconds on any other provider, whose tool calls end sooner (Codex ends an MCP tool call at 60 seconds by default). After that it returns "still working", the advice arrives as a wake-up, and calling `advisor` again picks up the same consult instead of starting another. The turn is not failed.
- [ ] AC-10: A Claude thread uses Claude's built-in advisor when `claudeBuiltIn` is on, the thread runs on Claude Code signed in to Anthropic, the advisor is a different Claude model that Anthropic's published advisor compatibility table accepts for the thread's model (Sonnet 4.6 or more capable, and at least as capable as the thread's model; a model the table does not list is not eligible), and the thread's context is under `builtInContextLimit`. The pair is chosen from the advisor order and the settings, never from live usage, so a usage reading does not restart the session. SpecWithCode passes the advisor model to that session itself. Once the context passes the limit the thread moves to the SpecWithCode route and returns only when the context falls under half the limit. A change takes effect at the thread's next turn. The studio-code `advisor` tool stays available on these threads, so a built-in advisor that Claude did not start still leaves the thread an advisor.
- [ ] AC-11: Claude sessions never get two advisors. The built-in advisor is switched off for the session when the thread's advisor is off by the thread's own choice, when the thread uses the SpecWithCode route, and in every advisor child, even when `~/.claude/settings.json` names one. With the app and project setting off and no thread choice, SpecWithCode passes nothing and Claude's own setting applies as it does today.
- [ ] AC-12: A thread already running the advisor's model is not advised by itself: it uses the next entry of the order, or is refused with the reason.
- [ ] AC-13: When the advisor is on and the thread has the studio-code tools, the thread's instructions include a short paragraph in the app's own words: consult after orientation and before substantive work, again before reporting done, and when stuck; make results durable first; raise a conflict with the evidence instead of switching silently. It tells the thread to use a built-in `advisor` tool when it has one and the studio-code `advisor` tool otherwise. No text from Claude Code's prompt is used. The paragraph is absent when the advisor is off.
- [ ] AC-14: Settings > Models shows an "Advisor" section: the switch, the model (with "Fable 5.2, then the Review track" as the default), the Claude built-in switch with its usage-credits note and context limit, and the two limits. The project dialog shows the same rows with "Inherited" and "Overridden for this project" states and a reset. Both are found by settings search.
- [ ] AC-15: The composer's options menu has an "Advisor" row for the thread: Follow project, On, Off. It writes AC-02 and shows the effective state.
- [ ] AC-16: In the timeline a consult reads "Asked the advisor" with the advisor's model, and opens to the advice. A built-in Claude advisor result shows its text, or "Advice applied (hidden by Claude)" for a redacted result, or "Advisor unavailable" with the code for an error, which is marked as failed. No raw JSON.
- [ ] AC-17: New UI strings exist in all 8 phrase catalogs, and the i18n test passes.
- [ ] AC-18: A headless fixture renders the Advisor section (app and project scope), the composer row and the timeline item in light and dark at 390px and desktop width; screenshots are saved to this increment's `reports/`.
- [ ] AC-19: `docs/studio/advisor.md` explains what the advisor does, the two routes, the cost guards and the settings, citing only Anthropic's public documentation.
- [ ] AC-20: On a development server one consult from a thread that is not on Claude returns advice, inside the wait or as a wake-up, and the evidence (thread, models, seconds, brief size) is saved to this increment's `reports/`. The tool-call timeout that Codex and the ACP agents apply is recorded there.
- [ ] AC-21: The iOS and Android decoders accept a thread and settings that carry the new fields.

## Approach

Two routes behind one setting.

**Built-in route (Claude advised by Claude).** Anthropic runs the advisor server-side on the full transcript inside the same request, so nothing is resent by the client and the advice is the best available. SpecWithCode only decides the model and passes `advisorModel` in the session's flag settings (`makeClaudeQueryOptions`), or `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` in the session environment when the built-in advisor must be off. Both were checked on the managed Claude Code 2.1.325 on November 16, 2026: the flag setting overrides the user's own `advisorModel`, the variable removes the tool, and an empty `advisorModel` does not (it fell back to another model). The value joins `queryIdentity` so a change restarts the session at the next turn. Because every built-in call reads the whole transcript again, uncached, with no call limit, this route is used only while the thread's context is under `builtInContextLimit`.

**SpecWithCode route (everything else).** A new studio-code tool `advisor`:

1. Resolve the thread's effective advisor (thread mode, then project, then app) and the candidate order (`packages/shared/src/advisor.ts`).
2. Refuse when off, when the caller is an advisor child, or when the run's limit is used up.
3. Build the brief (`apps/server/src/orchestration-v2/AdvisorBrief.ts`) from projection records with its own item renderer, since `historicalMessage` drops tool calls. One UTF-8 byte counts as one token, as the handoff budget does. The cursor for "since the last consult" is the previous consult's item.
4. Start a child through the existing delegated-task path with the picked model and its saved effort, wait up to 4 minutes, return the child's final text. A longer run returns "still working" and wakes the caller, as `delegate_task` already does.
5. Archive the child once its advice is read, so advisor children do not pile up.

The child is marked as an advisor child on its delegated-task record; that mark is what refuses nested consults and delegation.

Files, in order:

- `packages/contracts/src/advisor.ts` (new): `AdvisorSettings`, patch, defaults, `ThreadAdvisorMode`, tool input and result.
- `packages/contracts/src/settings.ts`, `orchestrationV2.ts`, `orchestratorMcp.ts`, `environment.ts`, `index.ts`: one key, one thread field, one command, one capability flag, exports.
- `packages/shared/src/advisor.ts` (new): effective mode, candidate order, Claude rank rule, route choice, guidance text.
- `packages/shared/src/projectSettings.ts`, `studioMcpToolPresentation.ts`: merge line and tool label.
- `apps/server/src/orchestration-v2/AdvisorBrief.ts` (new), `Orchestrator.ts`, `ProjectionStore.ts`, a migration if the thread field needs a column.
- `apps/server/src/mcp/toolkits/orchestrator/tools.ts`, `handlers.ts`, `OrchestratorMcpService.ts`: the tool and `consultAdvisor`.
- `apps/server/src/claudeModelOptions.ts`, `Adapters/ClaudeAdapterV2.ts`: pass-through, off switch, readable results.
- `apps/server/src/provider/RuntimeInstructions.ts` and the Pi extension source: guidance.
- `apps/web/src/components/settings/AdvisorSettings.tsx` (new), `ModelSettingsPanel.tsx`, `ProjectWorkspaceSettings.tsx`, `projectOverrideRows.ts`, `scopedSettings.ts`, settings search, `TraitsPicker.tsx`, timeline presentation, phrase catalogs.
- `scripts/studio-fleet/settings_continuity.py`, `docs/studio/advisor.md`, an `apps/web/tests/advisor` fixture.

Rejected:

- Calling the Anthropic API directly for every provider. It needs a per-token key, which the spending rules forbid, and Codex or Muse transcripts are not in Anthropic's format.
- Forwarding the whole stored timeline. Stored tool output is already trimmed to 64K characters per item, so "the whole transcript" would be large and still incomplete. A budgeted brief plus the working folder, read-only, is cheaper and honest about what is missing. The advisor child gets no thread-reading tool: `studio_thread_read` is not read-only (it acknowledges deliveries), and the child may call read-only tools only.
- Reusing `resolveReviewer` as is. It always skips the author's model family, which would rule out Fable advising Opus.
- A boolean in `modelSelection.options`. Options are per provider and are dropped when the model changes; "follow the project" needs three states.
- One long-lived advisor session per thread fed with deltas. It saves a few thousand tokens of harness start-up per consult but adds a second lifecycle (idle sessions, a changed advisor model, context growth). The stateless brief already sends only the delta.

Risks: clients other than Claude Code may drop a tool call that is silent for more than 5 minutes, so the wait is capped at 4; a redacted built-in result cannot be shown; the built-in route with a Fable advisor bills to Claude usage credits, which the settings row states.

## Review

- Reviewer: meta (muse-wonder-1.0)
- Depth: deep
- Required: yes

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Off by default. A consult spends the strongest model's tokens, and on the built-in route a Fable advisor bills to usage credits. Reversible in Settings.
- D-02 Claude threads prefer Claude's built-in advisor (full transcript, same request). One switch turns that off so they use the SpecWithCode route on the plan instead.
- D-03 Default order is Fable 5.2, then the Review track (Muse Wonder 1.0 at Extra High, GPT-6.1 Sol, Gemini 4 Carbon).
- D-04 The advisor must be a different model from the thread's. Claude Code allows equal rank; here that is treated as waste.
- D-05 Timing is the model's judgement, guided by text. The server does not force a consult.
- D-06 Limits default to 3 consults per run and a 24,000-token brief.
- D-07 Claude's built-in advisor is used only while the thread's context is under 200,000 tokens. Above that each call would re-read the whole context at the advisor's price, so the thread moves to the budgeted brief.
- D-08 The tool waits a short time and then hands the advice over as a wake-up. Codex ends an MCP tool call at 60 seconds by default (its `tool_timeout_sec`), and an advisor on Fable often needs longer, so a single long blocking call would fail there.
- D-09 Claude's own advisor is chosen from the advisor order and settings, not from live usage. A Fable account at its limit then answers "Advisor unavailable" and the thread still has the studio-code tool.
- D-10 The Claude pair rule is built from Anthropic's public compatibility table only. The numbers found in the Claude Code binary are not used.
### Open
- Checked on Claude Code 2.1.325, November 16, 2026: a session that already consulted one advisor model kept it after a resume that named another, so a changed advisor model reaches a Claude thread only after its context is compacted or cleared. Switching the built-in advisor off on a resumed session worked.
- The same check showed each built-in call reading the whole context again (84,565 input tokens, none cached, in a session with one short exchange), which is what `builtInContextLimit` guards.
- Providers without a read-only sandbox the app can set (Pi, OpenCode 2, Antigravity) run an advisor child in Supervised mode: it asks before writing and nobody answers, so the consult ends as "failed" with a plain message and the child is stopped and archived.
- Native advisor tokens are not counted in SpecWithCode's usage numbers (the Claude adapter reads top-level usage only).
- The settings files `settings.ts`, `projectSettings.ts`, `projectOverrideRows.ts`, `ProjectWorkspaceSettings.tsx` and `settings_continuity.py` are shared with increment 1339; this increment adds one line to each and the 1339 thread is told.

## Tasks

### T-01 Contracts: advisor settings, thread mode, tool schemas
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/advisor.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/advisor.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestratorMcp.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/settings_continuity.py | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/contracts/src/advisor.test.ts

### T-02 Shared: effective mode, advisor order, route and guidance
- AC: AC-03, AC-10, AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/advisor.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/advisor.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/projectSettings.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/adversarialReview.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/studioToolSummary.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/advisor.test.ts

### T-03 Server: brief builder with budget and delta
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/AdvisorBrief.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/AdvisorBrief.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/AdvisorBrief.test.ts

### T-04 Server: advisor tool, consult service, limits and thread mode command
- AC: AC-02, AC-04, AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AdvisorConsult.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AdvisorConsult.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/SubagentProjection.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RuntimePolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RuntimePolicy.advisor.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderAdapter.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/testkit/OrchestratorScenario.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/claudeReadOnlyMcpTools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/studioReadOnlyTools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/AdvisorConsult.test.ts apps/server/src/orchestration-v2/RuntimePolicy.advisor.test.ts

### T-05 Claude threads: built-in advisor pass-through, off switch, readable results
- AC: AC-10, AC-11, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/claudeModelOptions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/claudeModelOptions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/claudeModelOptions.test.ts

### T-06 Guidance in thread instructions for every provider
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/RuntimeInstructions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/piStudioMcpExtensionSource.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/RuntimeInstructions.test.ts

### T-07 Web: Advisor settings section, project scope, search
- AC: AC-14, AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AdvisorSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AdvisorSettings.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelSettingsPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/projectOverrideRows.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/scopedSettings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSettingsSearch.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/AdvisorSettings.test.tsx src/i18n/i18n.test.ts

### T-08 Web: per-thread Advisor row and timeline item
- AC: AC-15, AC-16, AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/TraitsPicker.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.test.tsx, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/threadCommands.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/work-log/presentation.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/ThreadAdvisorMenu.test.tsx

### T-10 Live consult from a non-Claude thread and phone decoders
- AC: AC-20, AC-21 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCWireTests, repositories/anton-abyzov/specwithcode/apps/android/wire/src/test | Test: evidence file reports/live-consult.md exists and names the caller model, advisor model and seconds

### T-09 Headless fixture, screenshots and docs
- AC: AC-18, AC-19 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/advisor, repositories/anton-abyzov/specwithcode/docs/studio/advisor.md, repositories/anton-abyzov/specwithcode/docs/operations/checks.md | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/advisor/vite.config.ts && node apps/web/tests/advisor/verify.mjs "$PWD/../../../.specweave/increments/1371-advisor-model-any-thread-on-any-provider-can-consult-a-stronger-reviewer-model/reports/fixture"
