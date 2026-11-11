# Ultracode on by default for Claude worker threads, off for coordinators

## Problem

Anton asked (November 11, 2026) for Ultra Code to be on by default for all Claude models, at least for threads, and probably not for the coordinator, including Claude models under GitHub Copilot if that is possible.

Today Ultracode is off unless someone acts:

- Each chat has an Ultracode toggle in its model menu (increment 1122). Unset means "follow the Claude workflow mode".
- Settings › Agents › Claude workflows has one mode: Disabled, On request (the default) or Automatic. Automatic turns Ultracode on for every Claude chat with an unset toggle: threads, coordinators, routines and delegated tasks alike. There is no way to say "threads yes, coordinator no".
- The default model (Settings › General › New threads › Model) can carry `ultracode: true`, but only for that one model. A thread started on another Claude model, by a lane, a tier or a fallback, does not get it.

Facts checked on November 11, 2026:

| Question | Finding | Evidence |
|---|---|---|
| Which Claude Code models can run Ultracode? | 10 of 15 in the live catalog: Opus 5.5, Opus 5, Opus 4.8, Opus 4.7, Fable 5.2, Fable 5.1, Fable 5, Sonnet 5.5, Sonnet 5, Haiku 5.5. Claude Code offers it only on models with Extra High effort. Haiku 4.5, Opus 4.6, Sonnet 4.6 and Opus 4.5 have none. | `orchestrator_capabilities`; `apps/server/src/provider/ClaudeNativeModels.ts:62` |
| Does GitHub Copilot expose Ultracode for its Claude models? | No. Copilot CLI 1.0.105 with `claude-opus-5.5` selected offers four session options: mode (agent, plan, autopilot), model, reasoning_effort (low, medium, high, xhigh, max) and allow_all. "ultra" appears 0 times in the probe and in `copilot --help`. The October 25 finding (1.0.100) still holds. | `reports/copilot-probe/probe-1.0.105.json` |
| Cursor, Devin, OpenCode, Muse | None lists an Ultracode option on any model. Muse's "Ultra" is a reasoning level gated by Meta, not multi-agent workflows. | `orchestrator_capabilities` |
| What does it cost? | Claude Code documents no multiplier. It says each request "uses more tokens and takes longer" and a subscription "reaches a session or weekly limit sooner". With Ultracode on, Claude Code also skips its Large workflow warning (above 25 agents or 1.5M projected tokens), the concurrent subagent limit and the first-launch approval. Runtime caps stay: 16 concurrent agents, 1,000 agents per run. | https://code.claude.com/docs/en/workflows |

## Scope

In: one setting that turns Ultracode on by default for Claude Code threads and leaves coordinators off; the launch rule that applies it; the settings row; the composer chip and model menu showing the effective state; a pause when Claude usage is high; a one-time notice; docs.

Out: Ultracode for GitHub Copilot, Cursor, Devin or any non-Claude-Code provider (they do not offer it, and the app does not fake it with `/fleet`, Autopilot or Max effort); an equivalent "strongest mode by default" for Codex, Muse or others; a per-model list; an app-level cap on workflow size (Claude Code's own Dynamic workflow size setting stays as the user set it); the phone app's thread settings, which keep showing the stored toggle (the worker machine still applies the default).

## Acceptance Criteria

- [ ] AC-01: A project thread on a Claude Code model that offers Ultracode, with the toggle not set, starts with Claude's `ultracode` setting on. Its chip reads, for example, "High · Ultracode" and the menu marks On with a Default badge.
- [ ] AC-02: With the toggle not set, coordinators (project and personal assistant), routine threads and delegated tasks start with Ultracode off under "Threads" and on under "All chats".
- [ ] AC-03: A toggle set in the chat (On or Off) wins over the default. Workflows Disabled turns Ultracode off everywhere. "Ultracode by default: Off" in Settings › Agents, or in one project's settings, restores today's behavior.
- [ ] AC-04: Models and providers without Ultracode (Claude Haiku 4.5, Opus 4.6; every GitHub Copilot, Cursor and Devin model) start exactly as before, show no Ultracode chip and raise no "dropped" notice. A thread that falls back from Claude to another provider and returns gets the default again without any stored option.
- [ ] AC-05: A Claude instance signed in with an API key stays off by default; the chat toggle still turns it on.
- [ ] AC-06: When Claude's session or weekly usage is at or above 80%, the default stops applying until the reset and the chip reads "Ultracode paused". A toggle set to On in the chat is unaffected. Unknown usage does not pause.
- [ ] AC-07: The first Claude thread opened after the update shows one notice with "Keep it on" and "Turn off". "Turn off" sets the default to Off. The notice never returns after either choice.
- [ ] AC-08: A machine whose stored mode is Automatic keeps Ultracode on for every unset Claude chat, and its settings read "On request" plus "All chats".
- [ ] AC-09: Headless captures (`headless: true`) show the settings row, the chip in each state, the menu and the notice in light and dark at 1440 and 390 wide.

## Approach

Mockups (static HTML, not app code) and headless captures are in `reports/mockups/`:

- `reports/mockups/settings-ultracode-default-light.png`, `reports/mockups/settings-ultracode-default-dark.png`
- `reports/mockups/settings-ultracode-default-phone-light.png`, `reports/mockups/settings-ultracode-default-phone-dark.png`
- `reports/mockups/composer-default-on-menu-light.png`, `reports/mockups/composer-default-on-menu-dark.png`
- `reports/mockups/composer-chip-states-light.png`, `reports/mockups/composer-chip-states-dark.png`
- `reports/mockups/first-time-notice-light.png`, `reports/mockups/first-time-notice-dark.png`
- Source: `reports/mockups/mockup.html` (`?view=settings|composer|states|notice&theme=light|dark`), captured with `reports/mockups/shoot.mjs`.

### Where the default lives

One new server setting, `claudeUltracodeDefault`: `"off" | "threads" | "all"`, default `"threads"`. Same scope as `claudeWorkflowMode`: per machine, with a per-project override (added to `PROJECT_SCOPED_SERVER_SETTING_KEYS`). It is not per provider instance and not per model.

The default is resolved when a turn starts. It is never written into a thread's saved model selection, so:

- turning the setting off later reaches every chat that never chose;
- handoffs, fallbacks and moves between machines carry nothing extra, and each machine applies its own setting;
- an older server ignores the unknown key and keeps today's behavior.

Rejected: stamping `ultracode: true` into each new thread's selection (it would outlive the setting, travel to machines that cannot run it and trigger "dropped Ultracode" notices on every fallback); putting it only on the default model (covers one model); a fourth workflow mode (older servers fail to decode an unknown literal).

### The rule

One pure function in `packages/shared/src/ultracodeDefault.ts`, used by the server at launch and by the web composer for the chip, so both name the same state:

1. Workflows Disabled: off.
2. The chat's toggle is set: that value.
3. The model has no Ultracode toggle: off, nothing is sent.
4. Default is `off`: off.
5. Chat kind: a thread (a chat a person or a coordinator starts in a project) is on. A coordinator, a routine thread or a delegated task (a child whose parent is not a coordinator) is on only under `all`.
6. The Claude instance bills an API key: off.
7. Claude session or weekly usage at or above 80%: off, shown as paused.

The stored mode `automatic` reads as mode On request plus default `all`, which is what it does today. The mode select keeps Disabled and On request; changing the new row on such a machine writes both keys. No SQL migration.

Server: `RuntimePolicy.ts` already resolves `claudeWorkflowMode` per project and has the thread. It adds the resolved default (on, off or paused) to the runtime policy; `resolveClaudeUltracode` in `ClaudeWorkflowPolicy.ts` takes it in place of the `mode === "automatic"` test. The effective value is already part of the Claude query key (`ClaudeAdapterV2.ts`), so an idle chat reopens with resume when it changes and a running workflow keeps the value it started with. One-shot text generation still never sends Ultracode.

### How the user turns it off

- One chat: model menu › Ultracode › Off (exists today).
- One project: project settings › Agents › Ultracode by default › Off.
- The machine: Settings › Agents › Claude workflows › Ultracode by default › Off, or "Turn off" on the one-time notice.
- Everything, including explicit toggles: Workflows › Disabled (exists today).

### Cost and guards

Risk: the default changes what every Claude thread costs without the user choosing it. Each substantive task becomes a multi-agent workflow, Claude Code drops its own large-workflow warning, and subscription limits arrive sooner. Nobody has measured the multiplier here, so the copy says "more", never a number.

Guards, in order of weight:

1. Coordinators, routines and delegated tasks stay off. A coordinator routes; a routine runs unattended and repeatedly; a delegated task inside an Ultracode thread would multiply a fan-out by another fan-out.
2. The chip always shows the effective state ("· Ultracode", or "· Ultracode paused"), and the menu says why ("on by default for threads").
3. The default pauses at 80% of a Claude limit and resumes at the reset.
4. API-key instances are excluded, because there the extra tokens are money, not quota.
5. A one-time notice names the change and offers "Turn off".

Other risks: the first turn of each existing idle Claude thread after the update reopens its query once (resume, one prompt-cache miss). A usage reading that crosses 80% mid-thread reopens it once more. Both are single events per thread.

### Files, in order

`packages/contracts/src/settings.ts`, `packages/shared/src/ultracodeDefault.ts`, `apps/server/src/orchestration-v2/RuntimePolicy.ts`, `apps/server/src/orchestration-v2/ProviderAdapter.ts`, `apps/server/src/provider/ClaudeWorkflowPolicy.ts`, `apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts`, `apps/web/src/components/settings/AgentInstructionsSettings.tsx`, `apps/web/src/components/chat/TraitsPicker.tsx`, `apps/web/src/components/chat/ChatComposer.tsx`, `docs/studio/claude-workflows.md`.

## Decisions

### Asked
- none (the owner's request fixed the direction: on for threads, coordinator probably off; the task asked for a recommendation on each open point)

### Defaulted (change any before sw-do)
- D-01 Where the default lives → one machine setting with a per-project override, resolved at launch, default "Threads". Alternative: per model or per provider instance; rejected as more switches for the same effect (reversible).
- D-02 Which chats count as threads → chats a person or a coordinator starts in a project. Coordinators, the personal assistant, routines and delegated tasks stay off. Alternative: include delegated tasks; costs a fan-out inside a fan-out (reversible, it is one line of the rule).
- D-03 Which models → every Claude Code model that offers the toggle (10 of 15 today), Haiku 5.5 included. No per-model list; the chat toggle covers exceptions (reversible).
- D-04 GitHub Copilot → not included. Copilot 1.0.105 offers no such option for its Claude models, and `/fleet` or Autopilot plus Max is not the same thing. If Copilot adds an option, it is a small follow-up (reversible).
- D-05 "All models" → Claude Code only. No other provider has a multi-agent session switch to default on (reversible).
- D-06 Existing threads → the default applies from each thread's next turn, not only to new threads, because a stored "unset" has always meant "follow the setting". Alternative: new threads only; needs a creation marker and leaves the chip inconsistent across threads (reversible).
- D-07 Existing installs → they get "Threads" too, with the one-time notice. Alternative: default on for fresh installs only, existing installs see the notice as an offer. Pick this if the release should not change anyone's usage unasked (reversible).
- D-08 Usage pause → on, fixed at 80% of the session or weekly window, no new setting. Alternative: drop T-05 for a smaller change (reversible).
- D-09 API-key Claude instances → excluded from the default (reversible).
- D-10 Automatic mode → folded into the new row as "All chats"; the stored value keeps working (reversible).
- D-11 Name → "Ultracode", the label the app and Claude Code already use (reversible).

### Open
- none

## Tasks

### T-01 Setting and the shared rule
- AC: AC-03, AC-04, AC-05, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/ultracodeDefault.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/ultracodeDefault.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode-dev/packages/shared && ../../node_modules/.bin/vp test run src/ultracodeDefault.test.ts

### T-02 The server applies the default at launch
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/RuntimePolicy.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/RuntimePolicy.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProviderAdapter.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/ClaudeWorkflowPolicy.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/ClaudeWorkflowPolicy.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && ../../node_modules/.bin/vp test run src/orchestration-v2/RuntimePolicy.test.ts src/provider/ClaudeWorkflowPolicy.test.ts src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts src/claudeModelOptions.test.ts

### T-03 Settings row, project override and the folded Automatic mode
- AC: AC-03, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/AgentInstructionsSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/projectOverrideRows.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/zh.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && ../../node_modules/.bin/vp test run src/components/settings/settingsSearch.test.ts src/components/settings/AgentInstructionsSettings.test.tsx

### T-04 Chip and menu show the effective state
- AC: AC-01, AC-02, AC-04, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/TraitsPicker.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/TraitsPicker.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/composerProviderState.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/ultracode-toggle/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/ultracode-toggle/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/ultracode-toggle/vite.config.ts && node apps/web/tests/ultracode-toggle/verify.mjs ~/.specwithcode/m4/evidence/ultracode-default-1295

### T-05 Pause the default when Claude usage is high
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/ultracodeDefault.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/ultracodeDefault.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/RuntimePolicy.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/RuntimePolicy.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/TraitsPicker.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev/packages/shared && ../../node_modules/.bin/vp test run src/ultracodeDefault.test.ts && cd ../../apps/server && ../../node_modules/.bin/vp test run src/orchestration-v2/RuntimePolicy.test.ts

### T-06 One-time notice
- AC: AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/UltracodeDefaultNotice.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/UltracodeDefaultNotice.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/ultracode-toggle/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/ultracode-toggle/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && ../../node_modules/.bin/vp test run src/components/chat/UltracodeDefaultNotice.test.tsx

### T-07 Docs
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/docs/studio/claude-workflows.md, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/ultracode-toggle/README.md | Test: cd repositories/anton-abyzov/specwithcode-dev && grep -q "Ultracode by default" docs/studio/claude-workflows.md && node scripts/studio-brand-audit.mjs

### T-08 Verify and close 1295
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: none | Test: specweave verify 1295-ultracode-on-by-default-for-claude-worker-threads-off-for-coordinators
