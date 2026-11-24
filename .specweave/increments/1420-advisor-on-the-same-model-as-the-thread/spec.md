# 1420 Advisor on the same model as the thread

## Problem

Anton, November 18, 2026, 11:15 PM: "If our thread was on the same model as advisor (for example, Fable 5.2 in both cases), then maybe it doesn't make sense to call advisor."

How the advisor model is picked today (app repository `repositories/anton-abyzov/specwithcode` at `aac065c36`):

- **The app's own advisor** (Settings > Models > Advisor on, or the thread set to On). The order is the saved advisor model, then Claude Fable 5.2 on each source billed by plan, then the Review track (`advisorOrder`, `packages/shared/src/advisor.ts`). A model never advises itself (1371 AC-12): `resolveAdvisor`, `preferredAdvisor` and `claudeAdvisorPairAllowed` skip the thread's own model.
  - An Opus 5.5 thread gets Fable 5.2 through Claude's own advisor, which reads the whole transcript.
  - A Fable 5.2 thread skips Fable and gets the first Review track model. On m4 the saved Review track starts with Muse Wonder Full at Extra High, in the machine's `adversarialReview.reviewers`. That runs through the studio-code tool, on a brief of at most 24,000 tokens.
  - Claude's own advisor is used only while the thread's context is under `builtInContextLimit` (default 200,000 tokens, `advisorRouteForContext`). Past that limit the thread moves to the brief.
- **Pass-through** (the app's advisor off, no thread choice). The app passes nothing, so Claude Code's own `advisorModel` applies (1371 AC-11). On m4, `~/.claude/settings.json` has `"advisorModel": "fable"`, so every Claude thread gets a Fable 5.2 advisor, Fable 5.2 threads included. Meanwhile the composer's Advisor row reads "Follow project (off)" (`apps/web/src/components/chat/ThreadAdvisorMenu.tsx:136`).
  - m4 has no saved advisor setting, and all 110 consulting threads have no advisor choice.
  - Both studio-code consults were refused with "off".
  - So every Fable-on-Fable consult measured came from pass-through, not from the app.

Anton's answer on the fallback (November 19, 2026), replying to "fall back to Muse, as today": "or another model in the list of models for Complex tasks I believe! we have a list Daily, Complex, Review!" So the advisor falls back along the Complex track, not the Review track. On m4 the saved Complex track is Fable 5.2 on Claude, then GPT-6 Astra on GitHub Copilot at Extra High.

What the m4 data says (November 16 to 18, 2026). The method is in the report `.specweave/reports/threads/2026-11-19-advisor-on-the-same-model-as-the-thread-7ab1d9-4900ed.md`, and the scripts and labels are in `~/.specwithcode/m4/evidence/advisor-same-model/`.

- **Advisor model.** The advisor is `claude-fable-5-2`, per the advisor usage entries in 176 Claude session logs, counted once per message: 118 Fable-on-Fable, 223 Opus-on-Fable, 2 Opus-on-Opus and 2 Sonnet advising Haiku. The logs include sessions outside SpecWithCode and were not joined to the labelled consults.
- **Cost.** One consult takes a median 1.8 minutes either way.
  - On a Fable thread it re-reads a median 180,000 input tokens and writes 9,700 output tokens. On an Opus thread it is 160,000 and 10,000.
  - 54 of 118 Fable-on-Fable consults (46%) re-read more than 200,000 tokens, past the app's default limit for Claude's own advisor.
- **Value.** Two blinded Sonnet 5.5 labellers read what each thread did after the advice. They were not told the thread's model. The advice text itself is encrypted (`advisor_redacted_result`).

| Thread model | Consults | The thread changed course and named the advice | First consult of each thread changed course | Threads |
|---|---|---|---|---|
| Fable 5.2 (same model) | 118 | 25 (21%) | 10 of 35 (29%) | 35 |
| Opus 5.5 (stronger advisor) | 112 | 12 (11%) | 5 of 55 (9%) | 61 |

- In the 6 threads that ran under both models, 5 of 10 same-model consults and 3 of 12 stronger-model consults changed course.
- Limits:
  - Same advisor in both groups. Fable threads did harder, open-ended work, consulted 5.0 times per thread against 2.0, and narrate more.
  - "Changed course" is not "improved".
  - The data shows that same-model consults are not empty. It does not show that they beat a stronger advisor.
  - Pass-through has no context limit, so nearly half the measured same-model consults are ones the app's own route would have sent to the brief.
  - The failure counts (21% against 9%) are not used: most "failed" items closed at run end, and 24 of the 31 Fable ones were followed by text naming the advisor, some quoting its points.
- Anthropic's advisor tool allows a model to advise itself. It reads the whole transcript without tools, and it has no effort setting, only `max_tokens`. So "the same model at a higher effort" cannot be set on Claude's own route.

## Scope

In:
- **The advisor order follows the Complex track.** The order becomes the saved advisor model, then the project's Complex track. It replaces "Fable 5.2, then the Review track".
- **Same model when the thread is on the top of the order.** A Claude thread on the first model of the order is advised by that same model through Claude's own advisor, while its context is under the limit. Past the limit, it gets the next Complex track model on the brief (D-02). Today it jumps to the Review track.
- **Show the advisor.** The thread's Advisor row and each consult name the model that answers, and say when it is the thread's own model.
- **Show pass-through.** The Advisor row stops reading "Off" while Claude's own advisor is answering on that thread.

Out:
- Changing what the app's Off does to Claude's own advisor (D-03).
- Muse advisor effort (D-05).
- The time note text from PR 644.

## Acceptance Criteria

- [ ] AC-01: With the app's advisor on, a Claude thread on Claude Code with a plan, whose model is the first entry of the advisor order and whose context is under the limit, is advised by that same model through Claude's own advisor. Its session is started with `advisorModel` set to that model. On the default order, that is a Fable 5.2 thread advised by Fable 5.2.
  - Past the limit, the consult goes on the studio-code brief to the next model of the order that is not the thread's own (D-02). On m4 that is GPT-6 Astra on GitHub Copilot, at its entry's Extra High.
- [ ] AC-02: Every other pair resolves as before:
  - an Opus 5.5 thread gets Fable 5.2;
  - a thread whose own model sits later in the order still skips it;
  - the context limit and its return under half the limit are unchanged.
- [ ] AC-03: The thread's Advisor row in the composer options menu names the advisor that would answer the next consult ("Advisor: Fable 5.2"), and adds "same model as this thread" when it is.
- [ ] AC-04: A consult of Claude's own advisor is titled with the model that answered, read from the reply's advisor usage entry, for example "Asked the advisor (Fable 5.2)". This holds in pass-through too.
- [ ] AC-05: In pass-through, once Claude's own advisor has answered on a thread, that thread's Advisor row says the advice came from Claude's own setting and names the model, instead of only "Follow project (off)". No consult starts or stops because of this change.
- [ ] AC-07: The advisor order is the saved advisor model, then the project's Complex track, with each entry at its saved effort. The Review track is no longer part of it.
  - With no Complex track saved, the order is the built-in Complex track: Fable 5.2, then GPT-6 Astra.
  - Billing rules are unchanged: built-in entries never pick per-token, Vertex, paid-router or unknown-billing sources.
  - Settings > Models > Advisor shows the default model as "The Complex track".
- [ ] AC-06: Wording is in all 8 catalogs. Headless screenshots of the menu show three states, light and dark at 1280 px and light at 390 px:
  - a Fable thread on the same model;
  - an Opus thread advised by Fable;
  - pass-through.

## Approach

- **Shared rule** (`packages/shared/src/advisor.ts`):
  - `advisorOrder` takes the project's Complex track (`modelLanes.complex`, expanded like the Complex track itself) instead of `reviewers`. Its callers pass that track: `RuntimePolicy.ts` and `OrchestratorMcpService.ts` (`resolveAdvisor`).
  - `claudeAdvisorPairAllowed` allows equal identity.
  - `preferredAdvisor` takes the thread's own model when it is the first entry of `advisorOrder` and the thread is on Claude Code with a plan.
  - `resolveAdvisor` keeps skipping the thread's own model on the brief, so a thread past the limit moves to the next Complex track model.
  - A new `threadAdvisorPreview` returns `{ model, sameModel, route }` for the menu, built from the same functions so the menu and the session never disagree.
- **Server:**
  - `RuntimePolicy.ts` needs no new input.
  - `ClaudeAdapterV2.ts` reads the advisor model from `usage.iterations[].model` where `type` is `advisor_message`, for the item title (AC-04). In pass-through it records the model on the thread's latest consult so the menu can say so (AC-05). It does not parse `~/.claude/settings.json`.
- **Web** (`ThreadAdvisorMenu.tsx`): the Advisor group shows the preview line. The fixture in `apps/web/tests/advisor` gains the three states.
- **Known limits** (review round 1, GPT-6.1 Sol):
  - The menu reads the usage the web sees. A hold the server keeps after a run stopped on a limit with no usage reading is not sent to the web, so for a thread on the brief the menu can name a model the consult then skips.
  - The pass-through note reads the loaded history. A long thread whose last consult from Claude's settings is outside the loaded window shows no note until that consult loads.
  - The consult title's model is the latest one Claude reported in the session (review round 3). A consult whose reply carries no advisor usage entry, or a subagent reply held and replayed after another one, can take the model of the previous answer. Parent and subagents share one process and one advisor setting, so the models differ only in contrived cases. It affects the title, not which advisor runs.
  - A consult is marked as from Claude's settings by its title ("Asked the advisor (model) from Claude's settings"). An older client reads no model from that title and shows "Claude built-in".
- **Rejected options:**
  - Skip the advisor when the models match. That throws away the consults that changed course most often.
  - Move to the next stronger or other-family model. There is nothing stronger than Fable 5.2, so the next entry is Muse Wonder Full on a lossy brief at Extra High. Owner rules say Muse only does adversarial review and runs at High, and the reviewer would then check work its own family steered.
  - The same model at a higher effort. Claude's advisor has no effort setting.
- **Adversarial review:** the rule itself is unchanged; the reviewer is still from another family than the author. The advisor now draws from the Complex track, never the Review track, so Muse no longer advises the work it reviews later.
  - One overlap is left. A long Claude thread's advisor is GPT-6 Astra (OpenAI). If Muse cannot review, the next reviewer on m4 is GPT-6.1 Sol, which is the same family (D-04).
- **Risk:** a same-model consult costs the same as an Opus thread's consult (about 180,000 tokens of Fable). Fable advice on a subscription draws usage credits (1371 report).

## Decisions

### Asked

- D-01 Keep the advisor when the thread is already on the advisor's model? → Yes (Anton, November 19, 2026): keep it and say so in the menu. This reverses 1371 AC-12 for that case.
- D-02 What happens past the 200,000-token limit, where 46% of measured same-model consults were? Anton, November 19: fall back along the Complex track, not to Muse. Applied as AC-07, and AC-01's past-the-limit case.
  - On m4 the next model is GPT-6 Astra on Copilot at Extra High.
  - This replaces my recommendation, the same model on the brief.

### Defaulted (change any before sw-do)

- D-06 Saved Complex track entries count as the person's choice, like a saved advisor model. So an advisor on a source with unknown billing runs when the person listed it there. Built-in entries and accounts added by expansion still never pick per-token or unknown-billing sources (reversible).
- D-07 The menu names the advisor for a short thread, then "Past {limit} tokens: {model}" when a long thread would get another model. It does not read the live context size (reversible).

### Open

- D-03 Should the app's Advisor Off also switch off Claude's own advisor named in `~/.claude/settings.json`? Today pass-through gives every Claude thread on m4 a Fable advisor while the app says Off. Recommended: not now. AC-05 makes it visible first; switching it off would take the advisor away from every Claude thread on m4.
- D-04 The advisor order no longer reaches the Review track. One overlap remains: an Astra advisor, and then a GPT-6.1 Sol reviewer when Muse cannot review. Should the reviewer skip the advisor's family as well? There is no data. Proposed as a follow-up.
- D-05 is moot by default, since Muse is not in the order. It applies only when someone saves Muse as the advisor model.

## Tasks

### T-01 Shared rule and preview
- AC: AC-01, AC-02, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/advisor.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/advisor.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/advisor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RuntimePolicy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AdvisorConsult.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RuntimePolicy.advisor.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/advisor.test.ts apps/server/src/orchestration-v2/RuntimePolicy.advisor.test.ts

### T-02 Consult title and pass-through record
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.advisor.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.advisor.test.ts

### T-03 Menu line, catalogs and fixture
- AC: AC-03, AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AdvisorSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/advisor, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/work-log/presentation.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/work-log/presentation.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/TraitsPicker.advisor.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/ThreadAdvisorMenu.test.tsx src/i18n/i18n.test.ts

### T-04 Review, merge, release
- AC: AC-06 | Files: none | Test: gh pr list --repo anton-abyzov/specwithcode --search "1420 in:title" --state merged --json number --jq length | grep -qv '^0$'
