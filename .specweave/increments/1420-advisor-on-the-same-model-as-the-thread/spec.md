# 1420 Advisor on the same model as the thread

## Problem

Anton, November 18, 2026, 11:15 PM: "If our thread was on the same model as advisor (for example, Fable 5.2 in both cases), then maybe it doesn't make sense to call advisor."

How the advisor model is picked today (app repository `repositories/anton-abyzov/specwithcode` at `aac065c36`):

- **The app's own advisor** (Settings > Models > Advisor on, or the thread set to On). The order is the saved advisor model, then Claude Fable 5.2 on each source billed by plan, then the Review track (`advisorOrder`, `packages/shared/src/advisor.ts`). A model never advises itself (1371 AC-12): `resolveAdvisor`, `preferredAdvisor` and `claudeAdvisorPairAllowed` skip the thread's own model.
  - An Opus 5.5 thread gets Fable 5.2 through Claude's own advisor, which reads the whole transcript.
  - A Fable 5.2 thread skips Fable and gets the first Review track model, Muse Wonder Full. That runs through the studio-code tool, on a brief of at most 24,000 tokens, at the built-in Review effort of Extra High (`packages/contracts/src/modelTracks.ts:53`).
- **Pass-through** (the app's advisor off, no thread choice). The app passes nothing, so Claude Code's own `advisorModel` applies (1371 AC-11). On m4, `~/.claude/settings.json` has `"advisorModel": "fable"`, so every Claude thread gets a Fable 5.2 advisor, Fable 5.2 threads included. Meanwhile the composer's Advisor row reads "Follow project (off)" (`apps/web/src/components/chat/ThreadAdvisorMenu.tsx:136`).
  - m4 has no saved advisor setting, and all 110 consulting threads have no advisor choice.
  - Both studio-code consults were refused with "off".
  - So every Fable-on-Fable consult measured came from pass-through, not from the app.

What the m4 data says (November 16 to 18, 2026). The method is in the report `.specweave/reports/threads/2026-11-19-advisor-on-the-same-model-as-the-thread-7ab1d9-4900ed.md`, and the scripts and labels are in `~/.specwithcode/m4/evidence/advisor-same-model/`.

- **Advisor model.** Every consult ran on `claude-fable-5-2`, read from the advisor usage entries of 176 Claude session logs: 116 advised a Fable 5.2 thread and 222 advised an Opus 5.5 thread.
- **Cost.** One consult re-reads a median 180,000 input tokens and writes 9,700 output tokens on a Fable thread; on an Opus thread it is 160,000 and 10,000. Each takes a median 1.8 minutes either way.
- **Value.** Two blinded Sonnet 5.5 labellers read what each thread did after the advice. They were not told the thread's model. The advice text itself is encrypted (`advisor_redacted_result`).

| Thread model | Consults | The thread changed course and named the advice | First consult of each thread changed course | Threads |
|---|---|---|---|---|
| Fable 5.2 (same model) | 118 | 29 (25%) | 10 of 35 (29%) | 35 |
| Opus 5.5 (stronger advisor) | 112 | 12 (11%) | 5 of 55 (9%) | 61 |

- In the 6 threads that ran under both models, 5 of 10 same-model consults and 3 of 12 stronger-model consults changed course.
- Limits:
  - Same advisor in both groups. Fable threads did harder, open-ended work, consulted 5.0 times per thread against 2.0, and narrate more.
  - "Changed course" is not "improved".
  - The data shows that same-model consults are not empty. It does not show that they beat a stronger advisor.
  - The failure counts (21% against 9%) are not used: most "failed" items closed at run end, and 24 of the 31 Fable ones were followed by text naming the advisor, some quoting its points.
- Anthropic's advisor tool allows a model to advise itself. It reads the whole transcript without tools, and it has no effort setting, only `max_tokens`. So "the same model at a higher effort" cannot be set on Claude's own route.

## Scope

In:
- **Same model on Claude's own route.** A Claude thread on the first model of the advisor order is advised by that same model through Claude's own advisor, with the whole transcript. Today it jumps to the Review track.
- **Show the advisor.** The thread's Advisor row and each consult name the model that answers, and say when it is the thread's own model.
- **Show pass-through.** The Advisor row stops reading "Off" while Claude's own advisor is answering on that thread.

Out:
- Same model on the studio-code brief route; there is no data for it.
- Changing what the app's Off does to Claude's own advisor (D-03).
- The Review track inside the advisor order (D-04).
- Muse advisor effort (D-05).
- The time note text from PR 644.

## Acceptance Criteria

- [ ] AC-01: With the app's advisor on, a Claude thread on Claude Code with a plan whose model is the first entry of the advisor order is advised by that same model through Claude's own advisor. On the default order, that is a Fable 5.2 thread advised by Fable 5.2. Its session is started with `advisorModel` set to that model, and the Review track is not used for it.
- [ ] AC-02: Every other pair resolves as before:
  - an Opus 5.5 thread gets Fable 5.2;
  - a thread on the studio-code route still skips its own model;
  - a thread past the context limit still moves to the brief and skips its own model there.
- [ ] AC-03: The thread's Advisor row in the composer options menu names the advisor that would answer the next consult ("Advisor: Fable 5.2"), and adds "same model as this thread" when it is.
- [ ] AC-04: A consult of Claude's own advisor is titled with the model that answered, read from the reply's advisor usage entry, for example "Asked the advisor (Fable 5.2)". This holds in pass-through too.
- [ ] AC-05: In pass-through, once Claude's own advisor has answered on a thread, that thread's Advisor row says the advice came from Claude's own setting and names the model, instead of only "Follow project (off)". No consult starts or stops because of this change.
- [ ] AC-06: Wording is in all 8 catalogs. Headless screenshots of the menu show three states, light and dark at 1280 px and light at 390 px:
  - a Fable thread on the same model;
  - an Opus thread advised by Fable;
  - pass-through.

## Approach

- **Shared rule** (`packages/shared/src/advisor.ts`):
  - `claudeAdvisorPairAllowed` allows equal identity.
  - `preferredAdvisor` takes the thread's own model when it is the first entry of `advisorOrder` and the thread is on Claude Code with a plan.
  - `resolveAdvisor` keeps `same-model` for the studio-code route.
  - A new `threadAdvisorPreview` returns `{ model, sameModel, route }` for the menu, built from the same functions so the menu and the session never disagree.
- **Server:**
  - `RuntimePolicy.ts` needs no new input.
  - `ClaudeAdapterV2.ts` reads the advisor model from `usage.iterations[].model` where `type` is `advisor_message`, for the item title (AC-04). In pass-through it records the model on the thread's latest consult so the menu can say so (AC-05). It does not parse `~/.claude/settings.json`.
- **Web** (`ThreadAdvisorMenu.tsx`): the Advisor group shows the preview line. The fixture in `apps/web/tests/advisor` gains the three states.
- **Rejected options:**
  - Skip the advisor when the models match. That throws away the consults that changed course most often.
  - Move to the next stronger or other-family model. There is nothing stronger than Fable 5.2, so the next entry is Muse Wonder Full on a lossy brief at Extra High. Owner rules say Muse only does adversarial review and runs at High, and the reviewer would then check work its own family steered.
  - The same model at a higher effort. Claude's advisor has no effort setting.
- **Adversarial review:** unchanged. The reviewer is still from another family than the author. Keeping the Fable thread's advisor on Fable keeps Muse out of the work it reviews later.
- **Risk:** a same-model consult costs the same as an Opus thread's consult (about 180,000 tokens of Fable). Fable advice on a subscription draws usage credits (1371 report).

## Decisions

### Asked

- D-01 Keep the advisor when the thread is already on the advisor's model? Recommended: keep it on Claude's own route and say so in the menu. This reverses 1371 AC-12 for that case. Waiting for Anton.

### Defaulted (change any before sw-do)

- D-02 The same-model rule applies only to Claude's own route, not the brief, because only that route has data (reversible).

### Open

- D-03 Should the app's Advisor Off also switch off Claude's own advisor named in `~/.claude/settings.json`? Today pass-through gives every Claude thread on m4 a Fable advisor while the app says Off. Recommended: not now. AC-05 makes it visible first; switching it off would take the advisor away from every Claude thread on m4.
- D-04 When the advisor order still reaches the Review track (Fable 5.2 unavailable), skip the family that will review the thread? There is no data. Proposed as a follow-up.
- D-05 A Muse advisor starts at the Review entry's Extra High. The owner's November 18 rule says Muse runs at High. Should the advisor follow it?

## Tasks

### T-01 Shared rule and preview
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/advisor.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/advisor.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/advisor.test.ts apps/server/src/orchestration-v2/RuntimePolicy.advisor.test.ts

### T-02 Consult title and pass-through record
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.advisor.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.advisor.test.ts

### T-03 Menu line, catalogs and fixture
- AC: AC-03, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadAdvisorMenu.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/advisor | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/ThreadAdvisorMenu.test.tsx src/i18n/i18n.test.ts

### T-04 Review, merge, release
- AC: AC-06 | Files: none | Test: gh pr list --repo anton-abyzov/specwithcode --search "1420 in:title" --state merged --json number --jq length | grep -qv '^0$'
