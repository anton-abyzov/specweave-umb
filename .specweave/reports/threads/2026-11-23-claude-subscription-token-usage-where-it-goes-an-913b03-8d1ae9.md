---
title: "Claude subscription token usage: where it goes and why limits end early (November 23, 2026)"
thread: "thread:delegated-task:command%3Amcp%3A24262d5b-943a-49ce-86d8-7d0f7380b00c%3Adelegate-task%3A72587851-113f-4924-ab29-7e5435b71ec2"
threadTitle: "Claude subscription token burn investigation"
savedAt: "2026-11-23T06:53:44.501Z"
date: November 23, 2026
author: Fable 5.2 on M5 (investigation), Gemini 4 Neon via GitHub Copilot Enterprise (adversarial review)
status: final. Reviewed by Gemini 4 Neon on November 23 (verdict "fix first"); its findings are folded in and listed under "Review"
scope: m4 and M5 transcripts and app run tables, October 24 to November 23, 2026
---

# Claude subscription token usage: where it goes and why limits end early

## Answer in five lines

1. **Prompt caching works.** The cache hit ratio on m4 is 96.6% to 97.9% every working day since November 7, the same as late October (96.0% to 97.6%). It is not the cause.
2. **Switching and handoffs are not the main cause.** Every cold rewrite on m4 since November 17, whatever triggered it, adds up to 9.3% of weighted tokens. Model changes inside a session are 0.6%. Account switches and handoffs start a new session, so their cost sits inside that 9.3% and cannot exceed it.
3. **Token volume is lower than in October, but the mix changed.** Fable 5.2 went from 0.5% of weighted tokens (October 24 to 30) to 33% (November 14 to 20) and 45% (November 21 to 23). A Fable token takes several times more of the weekly limit than an Opus token (my estimates run from 2 to 8 times, see the calibration), and Fable also has its own weekly limit, which fills first on the accounts that carry Fable work.
4. **The advisor, new on November 16 to 17, added Fable load to every thread:** Claude's built-in advisor (671 consults on m4, each re-sending the whole thread uncached, 99% on Fable) and the app's advisor child threads, which on M5 load 162 connector tool definitions and then thrash on compaction.
5. **The rest is volume:** November 18 and 19 ran 2.4 times the daily average on m4 (about 100 Claude worker threads a day), and one multi-agent thread on November 22 used 188M weighted tokens in eight hours.

**What I could not measure:** between none and a third of the limit points consumed have no matching tokens in what I read (two estimates disagree, see the calibration). m1, m3, win and linux-mini were not read, compaction calls are not logged, and use of the same accounts outside these machines is invisible. The ranking below is of what was measured.

Four Claude subscriptions were rotated on m4 in these two weeks. Each went from near 0% to 100% of its weekly limit in one to two days of heavy use (admin@: 5% to 100% in 31 hours, November 17 06:00 to November 18 13:07 UTC).

## Method and units

- Source: every `~/.claude/projects/**/*.jsonl` transcript on m4 (11,977 files, 397,632 API responses, 1,811 sessions) and M5 (151 files, 4,110 responses, 131 sessions), deduplicated by message id. Thread titles, runs, handoffs and routines come from each machine's app database, read only through `specwithcode db query`. Limit percent history comes from each machine's `usage-limit-history.json`.
- Unit: **weighted tokens** (input-equivalent), the same as the November 2 study: input 1, cache read 0.1, 5-minute cache write 1.25, 1-hour cache write 2, output 5. These are API price ratios. They are not a bill, and the subscription limit may weigh tokens differently.
- Days in token tables are US Eastern (fixed UTC-5, so October 24 to November 1 are off by one hour). Counts from the app database (runs, handoffs, routines) are by UTC day, 5 hours ahead. November 23 is partial (to about 01:45).
- Advisor tokens are counted separately. The built-in advisor's tokens sit in `usage.iterations` and are not in the response's top-level usage, so any counter that reads only the top level misses them.

Coverage gaps:

| Machine | Status |
|---|---|
| m4 | Read in full. |
| M5 | Read in full. Transcripts start November 16. |
| m1 | **Not read.** It is online (m4 lists it as reachable) but not joined to M5. Both routes through m4 were refused by design: a file relay ("M5 started this work, and it moves files only with M5") and a thread list (`outside_grant_scope`: "This thread runs M5's work, which may reach only the threads it launched on m1."). What I can say: m1's current Claude sign-in is a fifth account (shared with m3) at 2% for the week that resets November 28. That says nothing about m1 running on one of the four rotated accounts earlier, so m1's share is unknown. To read it, m1 has to be joined to M5 the way m4 is; then the same scan runs there. |
| m3 | Same current account as m1, 2% used. Not read, share unknown. |
| win, linux-mini | Unreachable from M5 during the run. Not read. |

Compaction requests are not written to transcripts, so their cost is missing from all numbers here.

## Numbers

### Weekly totals, m4 plus M5 (millions of weighted tokens)

| Week | Opus main | Opus subagents | Fable main and subagents | Fable advisor | Sonnet, Haiku | Total | Fable share |
|---|---:|---:|---:|---:|---:|---:|---:|
| October 24 to 30 | 1,780 | 2,839 | 22 | 0 | 4 | 4,646 | 0.5% |
| October 31 to November 6 | 1,351 | 1,117 | 5 | 0 | 238 | 2,711 | 0.2% |
| November 7 to 13 | 705 | 355 | 418 | 0 | 232 | 1,710 | 24% |
| November 14 to 20 | 1,173 | 495 | 731 | 132 | 90 | 2,621 | 33% |
| November 21 to 23 (3 days) | 31 | 200 | 149 | 40 | 5 | 425 | 45% |

### By day and machine (millions of weighted tokens, advisor included)

| Day | m4 | M5 | m4 Opus main | m4 Opus subagents | m4 Fable main | m4 advisor consults |
|---|---:|---:|---:|---:|---:|---:|
| November 12 | 550.7 | | 79.3 | 119.3 | 210.3 | 0 |
| November 13 | 312.1 | | 241.0 | 36.6 | 14.5 | 0 |
| November 14 | 286.3 | | 135.0 | 71.0 | 72.3 | 0 |
| November 15 | 183.7 | | 76.8 | 31.4 | 67.9 | 0 |
| November 16 | 375.0 | 1.8 | 58.8 | 186.6 | 110.1 | 72 |
| November 17 | 260.7 | 1.8 | 114.3 | 43.5 | 38.3 | 75 |
| November 18 | 692.5 | 8.3 | 389.5 | 70.8 | 174.3 | 199 |
| November 19 | 677.7 | 0.4 | 361.1 | 89.4 | 165.1 | 169 |
| November 20 | 2.6 | 130.3 | 0.3 | 1.4 | 0.6 | 1 |
| November 21 | 56.9 | 21.9 | 3.3 | 21.9 | 22.0 | 24 |
| November 22 | 274.2 | 0 | 19.2 | 175.5 | 53.9 | 108 |
| November 23 (partial) | 61.4 | 10.5 | 6.8 | 2.5 | 44.7 | 23 |

Effort on m4, November 17 to 23 (millions): Opus medium 409 main plus 155 subagents, Opus high 308 main plus 241 subagents, Fable medium 225, Opus xhigh 172, Fable high 169, Sonnet high 73, Fable max 59, Fable xhigh 45.

### Where November 17 to 23 went (m4 plus M5, 2,199M weighted)

| Category | Weighted | Share of tokens | Estimated share of measured limit points |
|---|---:|---:|---:|
| Fable main threads | 565M | 26% | 38% to 59% |
| Opus main threads | 932M | 42% | 12% to 31% |
| Built-in advisor consults (Fable) | 156M | 7% | 10% to 16% |
| Opus subagents | 406M | 18% | 5% to 14% |
| M5 advisor child threads (Fable) | 52M | 2% | 3.5% to 5.5% |
| Sonnet and Haiku | 82M | 4% | 1% to 3% |
| Fable subagents | 6M | 0.3% | under 1% |

The last column is a band, not a measurement. Its low end assumes Fable costs 2 times Opus per weighted token, its high end 8 times (see the calibration for where those come from). Fable main threads are first across the whole band. Opus main threads and advisor consults can swap at the high end.

### Largest threads active since November 17

Totals are for the whole life of the session, so the long-lived ones include earlier weeks. The Weighted column excludes advisor consults, which are in their own column.

| Thread | Machine | Active | Weighted | In subagents | Advisor | Calls | Hit ratio | Models and effort |
|---|---|---|---:|---:|---:|---:|---:|---|
| Viral explainer video factory (RU + EN) | m4 | November 22 | 170.6M | 161.5M | 17.8M | 5,388 | 96.6% | Opus high 5,165, Fable 223 |
| specweave coordinator | m4 | October 31 to November 23 | 143.3M (23.4M since November 17) | 13.0M | 0 | 3,730 | 96.4% | Opus medium, xhigh |
| Viral series: copy to new machine | m4 | November 16 to 18 | 94.7M | 71.1M | 1.2M | 3,079 | 97.1% | Opus 2,690, Fable 389 |
| Request and verify app releases | m4 | November 2 to 23 | 87.8M | 11.7M | 0 | 2,770 | 97.2% | Opus medium |
| Rethink copies, sync and handing off work | m4 | November 18 to 19 | 84.2M | 6.0M | 4.8M | 2,671 | 98.3% | Opus xhigh 2,201, Fable 470 |
| One simple flow to bring a project to another machine | m4 | November 13 to 17 | 62.1M | 0.3M | 0 | 1,898 | 98.4% | Opus high |
| PS23 Superliga via AI chat | m4 | November 15 to 18 | 58.3M | 44.0M | 8.5M | 1,848 | 97.1% | Opus 1,468, Fable 380 |
| Port T3 security and data-loss fixes | m4 | November 14 to 23 | 55.4M | 36.9M | 2.7M | 2,538 | 97.2% | Opus 2,032, Fable 506 |
| Onboarding rethink: Chrome and key setup | m4 | November 18 to 19 | 47.0M | 0.1M | 6.9M | 1,078 | 97.0% | Fable xhigh 978 |
| Advisor model redesign | m4 | November 16 to 18 | 45.0M | 30.1M | 6.0M | 1,769 | 97.6% | Opus 1,580, Fable 189 |
| Livestream shorts factory | M5 | November 20 to 21 | 19.6M | 5.4M | 1.4M | 533 | 97.2% | Fable medium |
| Advisor: 1434 account switch adversarial review | M5 | November 20 | 15.0M | 0 | 0 | 40 | 45.1% | Fable medium, 11 sessions, 17 compactions |
| Account-switch privacy | M5 | November 20 | 13.8M | 0.7M | 0.4M | 497 | 98.6% | Opus medium |
| Skills availability and pagination | M5 | November 20 | 13.7M | 0 | 0.5M | 425 | 98.6% | Fable medium |
| Advisor: Skills management clarity review | M5 | November 20 | 10.9M | 0 | 0 | 26 | 33.5% | Fable medium, 7 sessions, 9 compactions |

Every ordinary thread is at 96% to 99%. The only threads with a bad hit ratio are the M5 "Advisor: ..." threads (cause 5).

### Wake-ups, polling and multi-agent prompts on m4, November 17 to 23

Counted from the first words of each prompt (the 400 most frequent prompt openings, so small ones are undercounted).

| Prompt kind | Count |
|---|---:|
| New turn with the project context block (user or coordinator message) | 1,224 |
| Workflow tool subagent tasks ("[Workflow harness ...]") | 424 (65, 70, 160, 9, 29, 83, 8 by day) |
| Delegated task starts | 287 |
| Continuations after compaction | 259 |
| Background task notifications | 74 or more |
| "Anton explicitly authorizes recurring ..." (a recurring wake prompt) | 34 |
| Remote worker reports | 28 or more |
| Pull request updates (PR watcher) | 27 |
| Restart continuations | 12 |
| Routine runs (app table) | 5, 1, 7, 41, 50, 14 on November 18 to 23 |

Wake prompts and watchers are a few hundred turns against about 5,100 prompts in total. They matter only where they wake a long thread after its cache expired (cause 6). The Workflow subagent tasks come from Claude Code's Workflow tool; the transcripts do not say whether Ultracode or a direct request started each run. For scale, late October ran 389 to 911 such tasks a day; this week ran 8 to 160.

Account rotation on m4: the account carrying most tokens changed 35 times between November 12 and 23 at hourly resolution (9 on November 12, 8 on November 17, 1 to 4 on other days).

### Limit points against tokens (estimate)

Across the four accounts, November 12 to 23, the limit history shows about **872 weekly points** and **971 Fable-weekly points** consumed, against 3,991M weighted tokens on m4 and M5. A two-variable fit by day (12 days, through the origin) gives:

- Opus and Sonnet: about 9.7M weighted tokens per weekly point.
- Fable: about 2.6M weighted tokens per weekly point, 3.8 times the limit cost of Opus per weighted token.
- Fable's own weekly limit: 0.7M to 1.7M Fable weighted tokens per point by day, 1.4M on average.

This fit is weak, as the reviewer showed by re-running it: the Opus rate's 95% interval includes zero, the two inputs are correlated (r = 0.76), and dropping one day moves the ratio between 2.9 and 5.4. Allowing a constant term gives **about 25 points a day that no measured token explains** and pushes the ratio to 8. So up to a third of the points come from use I did not see, or the accounts are on different plans, or the limit weighs tokens differently from my unit. The single-account rates below point the other way: applied to November 17 to 23 they predict 535 to 572 points against about 506 observed, which leaves nothing unexplained.

Check on single accounts. Days where one account's own tokens are nearly all one model, and few tokens that day lack an account:

| UTC day, account | Own tokens | Fable share | Weekly points | Fable points | Tokens with no account that day | Weighted per weekly point |
|---|---:|---:|---:|---:|---:|---:|
| November 14, anton.abyzov@ (Olympus) | 110M | 5% | 21 | 9 | 5M | 5.2M |
| November 13, anton.abyzov@ (Olympus) | 163M | 0% | 21 | 0 | 106M | 7.8M or more |
| November 20, admin@ | 144M | 68% | 59 | 107 | 2M | 2.4M (about 2.0M for the Fable part) |
| November 23, admin@ (partial) | 77M | 91% | 34 | 59 | 46M | 2.3M or more |
| November 21, admin@ | 19M | 86% | 10 | 20 | 32M | 1.9M or more |

On these days Opus is about 5M to 8M weighted per weekly point and Fable about 2.0M to 2.4M, a ratio of 2.5 to 4. Together with the fit, the honest range is **2 to 8 times, most likely 3 to 4**. Fable's own limit moved at 0.9M per point on November 20 and 2.1M on November 18 on the same account (admin@ was at 100% overall for part of November 18, which may explain the difference), so 70M to 210M of Fable fills it.

For comparison, the API list prices (from the bundled Claude API reference, cached November 3) are $8 and $40 per million for Fable 5.2 input and output against $4 and $20 for Opus 5.5, and $0.20 for cache reads on both. A list-price ratio would be 2 or less on this cache-heavy mix, so the subscription limit does not simply follow list prices. Why is not known.

What this means in practice: a 20M Opus thread is 2 to 4 points of a week. The same thread on Fable is 8 to 10 weekly points and 10 to 28 Fable points. Four to ten such Fable threads end a week of Fable.

Limits of this estimate: 12 daily points, four accounts that may be on different plans, 1% to 78% of a day's tokens in sessions with no recorded account (78% on November 22), limit refreshes by the provider on November 12, 15, 19 and 20, and machines not read. The day-level fit under-predicts November 21 (23 points against 51) and November 22 (34 against 56), the two days with a large unattributed share or with machines I could not read. Treat the result as "Fable costs several times more", not as one number. The weighted unit itself is API list pricing; the subscription limit's own formula is not published.

### Cache health

| Measure | Value |
|---|---|
| Daily hit ratio on m4, October 24 to November 6 | 96.0% to 97.6% |
| Daily hit ratio on m4, November 7 to 23 (days over 1,000 calls) | 96.6% to 97.9% |
| Threads active since November 17 with over 5M weighted in their lifetime (113 threads; 97 spent over 5M inside the week) | p10 96.3%, median 97.9%, p90 98.9% |
| Cache reads as a share of weighted tokens | 51% to 65% per day |

Cold rewrites of 50K tokens or more on m4, November 17 to 23, as a share of all weighted tokens:

| Cause | Share | Count and size |
|---|---:|---|
| Return after more than 1 hour idle (includes limit-parked threads and sessions resumed after an account change) | 5.2% | 242 |
| Request shape changed (app or tool list update) | 0.8% | 44 |
| After auto-compaction | 0.8% | 124 rewrites of 66K on average; the threads were at 369K before compacting |
| Unexplained | 0.7% | 53 |
| Model changed inside a session | 0.6% | 30 |
| Subagent idle past its 5-minute cache | 0.5% | 49 |
| Session start or resume | 0.3% | 57 |
| CLI version change | 0.2% | 9 |
| **All cold rewrites** | **9.3%** | |

The script has no working detector for an account change: a switch starts a new provider session, so its cost lands on the "session start" or "idle" lines. The 9.3% total is therefore the ceiling for everything that switching, handoffs and restarts cost in cache rewrites. What a new session spends re-reading files after a summary handoff is ordinary use and is not separated here.

Other counts on m4: limit-fallback messages 1 to 19 a day, provider handoffs 4 to 37 a day, full-summary handoffs 3 to 31 a day, Fable to Opus moves inside a thread 48 since November 12. 1M context is not a factor: auto-compaction at 400K holds, and calls above 400K are at most 0.6% of tokens (an overcount, see "Review").

## Top causes, ranked

Ranked by estimated share of measured weekly limit points for November 17 to 23 (bands from the table above). Cause 6 cuts across the others and is ranked by its token share.

### 1. Fable 5.2 carries regular work, and Fable is the expensive limit (38% to 59% of points)

Evidence:
- Fable share of weighted tokens: 0.5% in late October, 33% November 14 to 20, 45% November 21 to 23.
- Fable main threads are 26% of tokens but 38% to 59% of estimated limit points for November 17 to 23.
- The Fable weekly limit fills first on the accounts that carry Fable work: admin@ is at 84% Fable against 61% overall at the last reading (November 23, 06:45 UTC), and on November 20 it gained 107 Fable points against 59 overall. It is not true of every account: anton.abyzov@ (EasyChamp) is at 90% overall against 79% Fable.
- The owner rule of November 17 says Opus 5.5 for regular work and Fable only when named. After that date m4 still ran 174M and 165M of Fable main on November 18 and 19. Typical threads: "Onboarding rethink: Chrome and key setup" (978 of 1,078 calls on Fable at xhigh, 47M, or 54M with its advisor consults), "Sync dialog, Add to another machine" (631 of 1,052), "Integrations settings" (460 of 479), "Hand off: one durable runner per routine" (558 of 872). 241 sessions used Fable since November 12 (156 on m4, 85 on M5).
- November 23, 00:00 to 01:00 Eastern: 11 parallel Fable threads at max effort on m4 used 41M weighted in one hour. In the 5.5 hours around it admin@ went from 27% to 54% overall and from 27% to 76% Fable.

Who picks Fable (from each thread's saved routing record, Claude threads created since November 17, advisor threads excluded):

| Machine | Fable threads with a routing record | Fable threads with no routing record | Non-Fable threads |
|---|---:|---:|---:|
| M5 | 17 (lane "complex", moved from an Opus 5.5 baseline) | 12 | 48 |
| m4 | 6 (lane "complex") | 42, all created by an agent through the app's tools | 331 |

- On M5 the mechanism is recorded: the launching agent classes the task as complex and the Complex track's first model is Fable 5.2. Of 16 such threads with a saved reason, 10 say "Hardest work (the coordinator judged it): Claude · Claude Fable 5.2."; the other 6 were classed from the task text (creative, hard debugging, new design, named as complex).
- On m4 most Fable threads carry no routing record. They were created by another agent (a coordinator or a parent thread) through the app's tools. About half of m4's Fable tokens since November 17 sit in threads that mix Opus and Fable calls (35 sessions, about 225M), the rest in threads that are Fable throughout (25 sessions, about 182M).
- m4's settings hold `modelLanes.complex` as Fable 5.2 first, then GPT-6 Astra.

So on M5 an agent's "complex" judgement puts most Fable work there. On m4 the record cannot tell three cases apart: the agent chose Fable, the agent passed on its own model, or the user asked for Fable and the agent relayed it (this investigation is such a case). Reading the launch briefs of those 42 threads would settle it; I did not.

Fix:
- Tighten the guidance agents get for the "complex" lane: Fable only when the user or the brief names it, as the November 17 rule says. This is prompt text in the app, so it is a code change. The same for naming a model in a launch, if the m4 briefs show agents choosing Fable on their own.
- Or change the Complex track order so Opus 5.5 comes first (a setting, per project or global). This is the quickest lever but it also moves work that should be on Fable.
- Effort is a small lever here: Fable at max is 59M for the week (2.9% of m4) and at xhigh 45M. Worth a rule, not a priority.
- Show Fable-weekly beside the overall percent wherever a model is picked.

### 2. Volume on November 18 and 19, in long Opus threads (12% to 31% of points)

Evidence:
- m4 ran 692M and 678M on November 18 and 19 against an average of 284M for November 13 to 17 (2.4 times). Claude worker sessions: 93 and 105 a day. Opus runs: 819 and 940 a day against 258 on November 17. Work ran in all 24 hours, with up to 49 sessions in one hour.
- 46% of all weighted tokens since November 17 are main-thread calls made at 200K to 400K of context, and another 20% at 100K to 200K. Every call re-reads the whole context, so cost grows with calls times context even at a 97% hit ratio.
- 2,811 of 5,116 prompts in threads active since November 17 arrived at more than 200K of context (lifetime counts for those threads; up to 693 calls that carried an advisor consult are counted one band too high, which could lower the 46% to about 43%).

Fix:
- Keep the existing rule and apply it: a fresh worker for an unrelated request once a thread is past about 200K.
- The 400K auto-compaction threshold was decided on November 2. The evidence is the same as then, so I am not re-proposing 200K.
- Plan by points: at 5M to 10M per point, a 690M Opus-heavy day is most or all of a week on one subscription.

### 3. The built-in advisor re-sends the whole thread uncached, on Fable (10% to 16% of points)

Evidence:
- 671 consults on m4 since November 16 (none before), 41 on M5. 667 of 671 ran on Fable; 434 were called from Opus threads.
- Each consult sends 187K input tokens on average and returns 11K output: 244K weighted per consult. The advisor's usage entry reports no cache read and no cache write on any of M5's consults (41 in my count; the reviewer found 49 entries a little later, all the same); m4's aggregate counts them the same way.
- 4% of m4's weighted tokens on November 16 and 6% to 12% a day from November 17.
- The app's Usage does not count them: `apps/server/src/provider/ClaudeTurnTokenUsage.ts` reads only the top-level usage and never the `iterations` list (checked on `origin/main`).
- How the app steers this today (`origin/main`): `packages/contracts/src/advisor.ts` has the app advisor **off by default**, a built-in context limit of 200,000 tokens and 3 consults per run. When it is on, a thread past the limit stops using Claude's built-in advisor and asks through the app's advisor tool, which starts an "Advisor: ..." child thread (cause 5); it returns to the built-in one under half the limit. The 3-per-run cap applies only to the app's tool. Claude's built-in advisor has no per-run cap.
- On m4 these consults do not go through the app's limits. Three facts: m4's app settings have no `advisor` entry (so the app advisor is off there by default), m4's `/Users/antonabyzov/.claude/settings.json` has `advisorModel: "fable"`, and 265 of 675 consults sent more than 200,000 tokens (largest 367K), which the app's route would not allow. So Claude Code's own advisor setting is answering, on Fable, for every thread on m4 whatever its model. M5 has the app advisor on.
- For scale: all other uncached input on m4 since October 24 is 0.84M tokens. Advisor input is 126M.

Fix:
- Quickest lever, a setting on m4 that I did not touch: `advisorModel` in `/Users/antonabyzov/.claude/settings.json`. Removing it, or turning the app advisor on in m4's settings so its 200,000 limit and model order apply, stops the uncapped Fable consults.
- Decide the open question D-03 from 1420: should the app's "Off" also switch off Claude Code's own advisor? Today it does not, which is how m4 ended up here.
- The accepted decision of November 19 (1420, D-01) keeps the same-model advisor and sends everything else along the Complex track, which starts with Fable. Its evidence was quality (consults changed the thread's course 21% of the time on the same model, 11% for Fable advising Opus), not cost. The cost side is new: for an Opus thread the Fable advisor is the less useful and the more expensive choice. So the proposal revises 1420 for one case only: an Opus thread is advised by Opus.
- Do not lower the 200,000 limit to save tokens until cause 5 is fixed: a lower limit sends more consults down the child-thread route, which is the one that thrashes.
- A per-run cap for the built-in advisor does not exist and would be new code.
- Count advisor iterations in the app's Usage (code).

### 4. Multi-agent runs on Opus (5% to 14% of points)

Evidence:
- "Viral explainer video factory (RU + EN)", November 22 on m4: 188.4M weighted in 8.2 hours (170.6M plus 17.8M of advisor consults), 5,165 Opus calls and 223 Fable calls (4,625 at high effort, 763 at medium), 60 subagents, 70 advisor consults. That one thread is 69% of the day. Its sessions carry no account id (78% of that day's tokens do not), so the account is known by timing only: anton.abyzov@ (EasyChamp) gained 48 weekly points that UTC day against 30M of its own recorded tokens.
- Subagents were 64% of m4's tokens on November 22 and 10% to 17% on November 17 to 19. Subagents run on a 5-minute cache; cold subagent starts and idles are about 500M weighted over the whole period since October 24 (starts 260M, idles past the 5-minute cache 237M).
- This is the cause the estimate is least sure about. The day-level fit under-predicts exactly this day, so the true cost of a run like this may be higher than its rank says.

Fix:
- Enforce the standing rule (at most 10 agents unless named; search, review and verify agents on a cheaper model). That run had 60.
- Subagents default to Sonnet 5.5 at medium unless the brief names Opus.

### 5. The app's advisor child threads thrash on M5 (3.5% to 5.5% of points)

Evidence:
- M5, November 20: 38 "Advisor: ..." threads (41 in total), 51.6M weighted, 29% of everything M5 has used. 3.2 calls per session on average, hit ratio 38% overall.
- These are the child threads the app's advisor tool starts: for callers that are not Claude, and for Claude threads past the 200,000 built-in limit. Each is a read-only Claude session. Read-only sessions get the tool list `["Read", "Glob", "Grep"]` (`apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts:402`). With no tool search in that list, Claude Code loads the full definitions of all 162 claude.ai connector tools (Amplitude, Supermetrics, Gmail, Slack, Drive, Sheets, Calendar and others): 695K characters, about 280K tokens, as a 1-hour cache write.
- With the 101K base that puts a 3-call session at 390K, so it auto-compacts, the definitions load again, and it compacts again: 82 such loads and 48 compactions on November 20. One thread ended with Claude Code's own "Autocompact is thrashing" stop and returned no advice.
- m4's transcripts show no such loads, but m4 also has no advisor child sessions of this kind in the period, so m4 neither confirms nor rules out the same fault there.

Fix (code, small):
- Start advisor child sessions without claude.ai connectors (`ENABLE_CLAUDEAI_MCP_SERVERS=false` or strict MCP config, as the capability probe in `apps/server/src/provider/ClaudeProvider.ts:355-360` already does), or include tool search in their tool list. Scope it to advisor children, not to every read-only session: other read-only threads may use connectors on purpose.
- End an advisor child at its first auto-compaction and return what it has.

### 6. Cold rewrites after an hour idle (5.2% of tokens, spread across the causes above)

Evidence:
- 242 rewrites in November 17 to 23 (403 since November 12), 216K tokens each on average.
- The app's idle compaction before the cache expires is off: `compactBeforeCacheExpires` is absent from m4's settings, and off is the default. Transcripts show 103 `/compact` runs on October 25 to 27 and none since.
- Long-lived threads woken by routines or watchers pay this every time: "specweave coordinator" 72 rewrites, "Request and verify app releases" 37 (465 prompts, 285 of them above 200K), "EasyChamp coordinator" 22 (hit ratio 88%), "Daily SEO watch" 16, "DCFC Square daily dues sync" 16 (hit ratio 84%).

Fix:
- Routines start a fresh thread from state in a file (already the rule; these threads predate it).
- `compactBeforeCacheExpires` is an option, with a cost: it compacts every idle top-level thread above 200K at about 54 minutes, including threads nobody returns to, and each compaction is a paid call. I did not measure how often an idle thread above 200K is resumed, so I cannot say it pays. If tried, measure a week before and after. It skips delegated workers by design.

## What is not a cause

| Suspect | Finding |
|---|---|
| Prompt caching broken | No. Hit ratio unchanged at about 97%. |
| Model switches and fallback hops | 0.6% of tokens inside a session, 1 to 19 fallback messages a day. Not the main cause. |
| Machine handoffs | 3 to 31 full-summary handoffs a day on m4. Their rewrite cost is inside the 9.3% for all cold rewrites; not measured on its own. |
| Account switches | Four accounts were rotated; the leading account changed 35 times in 12 days. The rewrite cost is inside the 9.3% for all cold rewrites; not measured on its own. |
| 1M context | At most 0.6% of tokens above 400K. |
| Coordinators | 1.4% of m4 tokens since November 17. |
| App releases (127 between November 13 and 20) | Request-shape rewrites are 0.8%. |
| Project context prefix | 1,224 injections on m4 since November 17, under 1%. |
| Routines and wake prompts | 41 to 50 routine runs a day on m4 on November 21 and 22, a few hundred wake and watcher turns in the week; the cost is in cause 6. |

## What changed around November 17 to 23

- November 10 to 12: Fable 5.2 enters daily use.
- November 14 to 18: model tracks; the Complex track starts on Fable 5.2.
- November 16 to 17: advisor ships (1371). Consults start November 16.
- November 16: M5 joins. On November 20 most work ran on M5.
- November 17: admin@ account signed in; 100% by November 18.
- November 18 and 19: the two heaviest days since October, on two accounts at once.
- November 22: one 60-subagent run.

## Decisions for the owner

These are settings or code, and I changed nothing.

1. Keep Fable for named requests: tighten what agents are told about the "complex" lane and about naming a model in a launch, or put Opus 5.5 first in the Complex track. Recommended.
2. Advisor on m4: remove `advisorModel: "fable"` from Claude Code's settings or turn the app advisor on there; decide D-03; have Opus advise Opus threads (revises 1420 for that case). Recommended.
3. Subagents default to Sonnet 5.5; enforce the 10-agent cap. Recommended.
4. Stop advisor child sessions loading connector tools, and count advisor consults in Usage (two small code changes). Recommended.
5. Idle compaction for long-lived threads: only as a measured one-week trial. Optional.
6. Join m1 to M5 so its transcripts can be read. Optional, closes the largest coverage gap.

No saving is claimed for any of these. Each needs a before and after measurement with the same script.

## Review

Gemini 4 Neon (high effort, through GitHub Copilot Enterprise on M5) reviewed the first draft against the two result files, the script, M5's transcripts and `origin/main`. Verdict: "fix first". Thread: "Adversarial review: Claude token usage report".

Accepted and applied in this version:

| Finding | What changed |
|---|---|
| The 3.7 ratio rests on a weak 12-day fit; a constant term shows about 25 unexplained points a day | Point estimates replaced by bands (2 to 8 times); the possible unexplained share (none to a third) is now in the summary |
| The advisor fix ignored what `origin/main` already does (off by default, 200,000 limit, 3 per run on the app's tool, child-thread route past the limit) | Cause 3 fix rewritten; causes 3 and 5 are now linked |
| Headline numbers that did not match the result files (November 23 row, Viral thread 188M and 8.2 hours, M5 advisor threads 29% and 38%, effort list, cold-rewrite counts from mixed date ranges, 369K was the size before compaction) | All corrected |
| Account switches and handoffs were dismissed on the 0.6% model-change line alone | Now bounded by the 9.3% total for all cold rewrites |
| Idle compaction has a cost on abandoned threads; the connector fix should be scoped to advisor children; max effort is a small lever | Fixes reworded |

Known defects in `usage_scan.py`, not re-run (the effect is bounded and does not move a conclusion):

- A response that carries an advisor consult reports its context about twice too large (693 calls on m4, 49 on M5). Affected: the above-400K share (overstated), the above-200K prompt count, and each session's largest context. The same calls lose a few cache-write tokens (68K on M5 in total).
- Calls from October 24 to November 10 without a recorded cache lifetime were treated as 5-minute, which invented 80 "idle past 5 minutes" rewrites (34M) in that period. The November 17 to 23 numbers are not affected.
- Sessions without an account record (all subagent files) are 1% to 78% of a day.
- Thread tables keep the 1,500 largest sessions; the rest (42M) are in totals only.

The reviewer could not check m4's raw transcripts (only the result file is on M5), the accounts' plan tiers, or the count of 127 app releases.

Not reviewed a second time: this revised version.

## Evidence

- Script: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/usage_scan.py`
- m4 aggregates: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/m4-v3.json`
- M5 aggregates: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/m5-v3.json`
- Limit calibration: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/calib.py` (by day) and `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/calib2.py` (by account and day)
- Summary view: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/view.py`
- m4 worker thread: "Claude token usage scan on m4" on m4 (Codex, branch `specweave-studio/claude-token-usage-scan`, no commits). It left three result files on m4 in `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-23-claude-token-usage/` (`m4.json`, `m4-v2.json`, `m4-v3.json`), script copies under `/Users/antonabyzov/.specwithcode/m4/userdata/transfers/`, and its worktree `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/specweave-studio-31cda37a`. All are safe to delete.
- Nothing was changed: no code, no settings, no commits.
