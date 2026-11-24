---
title: "Gemini 4 Neon: what to build to show its strengths"
thread: "thread:delegated-task:command%3Amcp%3A5203f9f6-1c70-4578-a8a9-fc4f6def2ca7%3Adelegate-task%3A0eb947fb-028a-49a8-873f-12d917639e91"
threadTitle: "Gemini 4 Neon showcase build ideas"
savedAt: "2026-11-20T19:20:22.111Z"
date: "November 20, 2026"
status: "Proposal, nothing built"
top_pick: "The boring test: 120 invoices into a live Sheet"
---

# Gemini 4 Neon: what to build to show its strengths

Google released Gemini 4 Neon on November 18, 2026. It is two days old, so almost every number below comes from Google or from a launch partner, and nearly every public demo was built in Google's own Antigravity tool. Nothing here has been run in SpecWithCode yet.

**Recommendation: build idea 1 first.** Most Neon demos on X are games or 3D scenes. Two replies under a widely shared demo thread ask for the opposite: real work data, where one invented number matters. Google's own Sheet demo is large but unscored and built by an agent swarm. A Sheet checked against an answer key is the missing piece, Neon's finance and low-fabrication claims point at it, and SpecWithCode already ships the Sheet it needs.

## The ideas, ranked

| # | Idea | Strength it shows | Effort | Depends on |
|---|---|---|---|---|
| 1 | The boring test: 120 invoices into a live Sheet | Finance work, low fabrication | 1 to 2 days | Shipped Sheets |
| 2 | One prompt, three models, one wall | Speed, one-shot visuals | 2 to 3 days | Shipped `html_render`, delegation |
| 3 | Say a mod, get a mod | Follows instructions, small exact edits | 1 to 2 days | Shipped mods (text and buttons only) |
| 4 | Spec to animated launch deck | Pure-code motion, clear writing | 2 days | Design slides |
| 5 | Review theater: findings pinned on a map of the diff | Large context, security review | 3 to 4 days | Copilot context size, unknown |

## What Neon is good at, and who says so

| Strength | Evidence | Measured by |
|---|---|---|
| Fast | About 127 tokens per second on OpenRouter against about 46 for Gemini 4 Carbon | Third party (OpenRouter, quoted on Hacker News and DEV) |
| Cheap per task | $3 in and $15 out per million tokens; $3.74 per task at high against $7.76 for Carbon | Google (price), Artificial Analysis (cost per task) |
| Agentic coding | Coding Agent Index 58.6, first place; Terminal-Bench 4.1 65.2% | Artificial Analysis, cited by Google |
| Invents less | AA-Omniscience hallucination rate 14% against 50% for Opus 5.5 and 55% for GPT-6.2 Sol; "lowest fabrication rate yet" | Artificial Analysis; Google's own tests |
| Finance, tax and legal work | First on Vals Tax Agent Bench (54.89%) and Legal Research Bench (56.25%); first on most Surge AI finance and spreadsheet benchmarks | Vals and Surge AI as reported in launch coverage; I did not re-read these two in Google's post |
| One-shot visuals from code alone | One image into an animated 3D robot dog, a 3D rain scene, a sailing ship, a pure-JavaScript motion video | Single posts on X, unverified |
| Easy to steer | Second on steerability in Agent Arena (from a search summary, not re-read); "fewer unrequested changes"; Theo Browne: "They're so far ahead here it's insane" | Agent Arena, GitHub's changelog relaying Google, one X post |
| Long input | 1,048,576-token window; reads spreadsheets, PDFs, charts, audio and video | Google |

### What cuts against it

- **The demos depend on Google's harness.** All four official demos and the "17 demos in a day" thread ran in Antigravity, mostly with `/swarm`. Google's own SWE-sweep number is 12.8% in a bare harness and 39.0% in Antigravity. Through GitHub Copilot in SpecWithCode, expect less than the showcase. This is why ideas 1 to 4 lean on speed, cost, single-prompt output and number accuracy, and none needs a swarm.
- **It is wordy and slow at the top setting.** At xhigh: 56.5 seconds to first token, 141,631 output tokens per task, $6.44 per task. Use high, the default.
- **Opinions on quality differ.** Opus 5.5 still leads Terminal-Bench 4.1 (65.8%) and FrontierCode 2.0 (47.3%), as eesel reads Google's table. One Hacker News commenter puts Neon far below Carbon on a private benchmark; another finds it better on contained work.
- **Prompts, attempt counts and token cost of Google's demos are not published.**

### What is not known about Neon in SpecWithCode

GitHub's changelog says Neon is generally available on Copilot Pro+, Max, Business and Enterprise, with a gradual rollout, and "billed at provider list pricing under usage-based billing". It does not state the context size Copilot allows, whether image or PDF input passes through, or which thinking levels are offered. Each idea below says what it needs.

**Where it runs.** M5 has no GitHub Copilot instance. Neon runs on the M4 (`acpRegistry_copilot`, model `gemini-4-neon`, effort High), which is where the project's reviews already use it. Every demo is built and filmed on the M4, or Copilot is added on M5 first.

**Step zero for any idea is a 10-minute probe. On M4:** one Copilot thread on Neon, one image, one PDF, one 300,000-token paste, and a read of the effort choices the picker shows.

Two more facts shape the demos. A Copilot thread cannot take a message mid-turn (increment 1437 is fixing the queue behind it), so each demo is one prompt, not a conversation. And Copilot bills Neon by usage at list price. My estimate is a few dollars per demo run, taken from Artificial Analysis's $3.74 per benchmark task at high, not from a run of ours.

### Rules every video follows

From the project's marketing decisions: open on the product's value (the plans you already pay for, one coordinator), then the demo as proof. Show the official Google Gemini and GitHub Copilot marks from `apps/web/src/components/ProviderLogoMarks.tsx`. Fictional data only. No savings claims. A number on screen is a number we measured in that run.

## 1. The boring test: 120 invoices into a live Sheet

**Pitch.** Hand Neon a year of invoices and get a working set of books in a SpecWithCode Sheet, then count how many totals are wrong.

**Strength shown.** Finance and spreadsheet work, low fabrication, long input.

**The video (45 seconds).**

1. 0 to 5 s. Hook: "Gemini 4 Neon demos are mostly games. Here is the dull test: a year of invoices, and a count of wrong totals." 
2. 5 to 12 s. A folder of 120 fictional invoices drops into a SpecWithCode thread. The model chip shows Neon through GitHub Copilot.
3. 12 to 30 s. The Sheet fills, sped up: an Invoices tab, a Ledger tab, then income statement, balance sheet and cash flow by quarter, all formulas. Three charts draw.
4. 30 to 38 s. One input is changed with a sentence ("set the tax rate to 21%"). Every dependent total and chart moves. The Sheet viewer has no cell editing today, so the change goes through the thread.
5. 38 to 45 s. An Audit tab compares each total with the known answer: "120 invoices, N wrong", with the real N. Closing line: "Your subscriptions. Your machines. One coordinator."

**Build effort: 1 to 2 days.** Sheets shipped in PR #417 with `sheet_write` and `sheet_read` for every provider, bar, line and donut charts, and currency formats. What is left: a generator for 120 fictional invoices with a known answer key, the prompt, a checker that reads the Sheet back with `sheet_read`, and the screen capture.

**Limits to design around.** The Sheet has 15 functions and no lookups, so the model is built from SUMIF and ranges, hundreds of formulas, not Google's 500,000. The workbook limit is 200,000 cells, so 120 invoices fit with room to spare. If Copilot does not pass PDFs, the invoices are text or CSV and the video says so.

**Why it beats the alternatives.** I found no scored finance demo of Neon in what I read. It is the cheapest, because the product part exists. The result is a number, so it survives the question "is this just a pretty clip". If Neon gets totals wrong, that is still an honest, publishable result, and running the same prompt on a second model in another thread turns it into idea 2 for free.

## 2. One prompt, three models, one wall

**Pitch.** The coordinator sends one prompt to Neon, Opus 5.5 and GPT-6.2 Sol at once, and a single page shows the three results being built side by side with a clock and a cost meter.

**Strength shown.** Speed (127 against 46 tokens per second), cost per task, one-shot visuals from code.

**The video (40 seconds).**

1. 0 to 6 s. Hook: "Three AI plans, one app. Which one finishes first?" Three provider logos.
2. 6 to 10 s. One sentence typed to the coordinator: "Turn this photo into an animated 3D scene, code only."
3. 10 to 28 s. A three-column wall. Each column shows the thread streaming, then the running scene. Clocks and token counts tick.
4. 28 to 36 s. All three scenes animate together. A result row: time, tokens, cost.
5. 36 to 40 s. Closing line.

**Build effort: 2 to 3 days.** Delegation to three providers and `html_render` exist. New work: one wall page that frames three rendered outputs and reads each thread's time and token use, plus two or three prompts worth filming.

**Limits.** Not verified: that one `html_render` page can frame three other outputs and read each thread's token use; if it cannot, the wall is a small new view. Needs image input through Copilot; without it the prompt is text only ("a sailing ship on water"), which is what the X examples mostly were anyway. Neon may lose a round. Film the real result.

**Why it beats the alternatives.** A side-by-side race is something only a multi-provider app can show; a single-model clip can be made anywhere. It is the idea closest to SpecWithCode's own pitch. It ranks second because the outcome is not ours to control and the wall page is new work.

## 3. Say a mod, get a mod

**Pitch.** Describe a change to SpecWithCode in one sentence and Neon writes the mod; you approve it and it appears in the sidebar.

**Strength shown.** Following instructions exactly, small targeted output, speed.

**The video (35 seconds).**

1. 0 to 5 s. Hook: "Make the app yours. One sentence."
2. 5 to 10 s. Typed: "Show me a pane with every increment waiting on review, and a button that opens its thread."
3. 10 to 20 s. Neon writes about 60 lines. The approval dialog shows what the mod may read.
4. 20 to 30 s. Approve. A chip appears in the sidebar with a count; the pane opens; a button opens a thread.
5. 30 to 35 s. Two more mods flash by. Closing line.

**Three mods to ship with it.**

- **Review queue.** Increments waiting on a review, with a count chip. Fitting, since Neon is the project's reviewer model.
- **Increment radar.** Active increments grouped by state, one button each.
- **Thread roll call.** Threads that are blocked or waiting, most urgent first.

**Build effort: 1 to 2 days.** Mods exist: a sandboxed worker, up to 4 panes and 16 commands, a status chip with counts, and three read permissions (list threads, open a thread, list SpecWeave items). A mod can draw only boxes, text and buttons. The work is a short skill that teaches any model the mod format, the three mods, and capture. Charts or anything that writes would need a protocol change and a security review, about a week more, so they are out. Not verified: that the two list calls return review and blocked state; if they do not, the Review queue mod needs one more field from the host.

**Why it beats the alternatives.** It is the only idea that answers "customize it the way you want". It ranks third because a pane of text and buttons is plain on video, and because a mod this small does not separate Neon from other models.

## 4. Spec to animated launch deck

**Pitch.** Point Neon at an increment's `spec.md` and get a six-slide animated deck, drawn entirely in code, inside SpecWithCode.

**Strength shown.** Motion design from pure code, clear and direct writing.

**The video (40 seconds).**

1. 0 to 5 s. Hook: "The feature is done. The deck writes itself."
2. 5 to 10 s. A spec is dropped on a thread.
3. 10 to 32 s. The deck plays: title, the problem, a before and after diagram that animates, three numbers, what shipped.
4. 32 to 40 s. One slide is edited by a sentence and redraws. Closing line.

**Build effort: about 2 days.** Design slides exist (increments 0975 and 1051, known to me only by their titles; I did not open the slide code). Needed: a deck template on the project's design system, the prompt, and a check that animation runs in the slide viewer. That last point is unverified.

**Why it beats the alternatives.** It turns the X trend (a motion video from JavaScript alone) into something a team uses weekly. It ranks fourth because slide quality is a matter of taste and harder to prove than a count of wrong totals.

## 5. Review theater: findings pinned on a map of the diff

**Pitch.** Neon reviews a whole pull request in one read and the result opens as a map of the changed files with each finding pinned at its line.

**Strength shown.** Long input, security review (SEC-bench Pro 90.5%, cited by Google), low fabrication.

**The video (45 seconds).**

1. 0 to 6 s. Hook: "A second opinion from a different AI, on every change."
2. 6 to 15 s. A pull request with 40 changed files. Review starts on Neon.
3. 15 to 35 s. A treemap of the diff fills in; pins drop on files; clicking one shows the finding and the code line.
4. 35 to 45 s. A finding is fixed by a Claude Code thread; the pin turns green. Closing line.

**Build effort: 3 to 4 days.** Neon already runs the project's reviews through Copilot. New work: a structured findings file from `sw-review`, and one report page that draws the map.

**Why it ranks last.** It depends on how much context Copilot gives Neon, which is unknown, and it is the most new code. It is the most useful day to day, so it is worth doing after the probe.

## Suggested order

1. On M4: run the 10-minute Copilot probe.
2. Build idea 1 and film it.
3. Rerun idea 1's prompt on two other models; if the comparison is interesting, build the wall from idea 2 around it.
4. Idea 3 as a short follow-up clip.

## Sources

Google and GitHub:

- [Introducing Gemini 4 Neon (Google)](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/)
- [Gemini 4 Neon in GitHub Copilot (GitHub changelog)](https://github.blog/changelog/2026-11-18-gemini-4-neon-in-github-copilot)
- [Sundar Pichai on X](https://x.com/sundarpichai/status/2123167780988125621)
- [Google Gemini on X](https://x.com/GeminiApp/status/2123168704662012079)

Reviews and discussion:

- [eesel: Gemini 4 Neon review (Artificial Analysis figures per setting)](https://www.eesel.ai/blog/gemini-4-neon-review)
- [DEV: Gemini 4 Neon review](https://dev.to/aleksei_aleinikov/gemini-4-neon-review-61-intelligence-index-127-toks-and-315-vs-opus-55-485n)
- [explainx: six official demos, reviewed](https://explainx.ai/blog/gemini-4-neon-use-cases-demos-antigravity-swarm-ski-simulator-turing-november-2026)
- [Hacker News thread](https://news.ycombinator.com/item?id=50552424) (read in part)
- [9to5Google launch report](https://9to5google.com/2026/11/18/gemini-4-neon-announcement/)
- [MindStudio: benchmarks and hands-on tests](https://www.mindstudio.ai/blog/gemini-4-neon-release)

X, read in the signed-in Chrome on November 20, 2026 (nothing posted or liked):

- [Search: gemini 4 neon](https://x.com/search?q=gemini%204%20neon&src=typeahead_click)
- [Min Choi: 10 examples](https://x.com/minchoi/status/2123630368620220846): [robot dog](https://x.com/minchoi/status/2123630369983357156), [3D rain scene](https://x.com/minchoi/status/2123630374832005279), [sailing ship](https://x.com/minchoi/status/2123630379072450884), [17 demos in a day](https://x.com/minchoi/status/2123630386320216516), [motion video in JavaScript](https://x.com/minchoi/status/2123630389109662015)
- [Theo Browne on ease of use](https://x.com/theo/status/2123619214061977920)
- [Chubby: 17 demos thread](https://x.com/kimmonismus/status/2123168299890704735) and [Coding Agent Index note](https://x.com/kimmonismus/status/2123221275594403932)
- The gap: [Jose Medina, "a year of invoices"](https://x.com/jose_medina/status/2123766395091705945) and [Jorge Lemos, "one invented number costs a lot more than a buggy game"](https://x.com/JorgeLemosIA/status/2123717052053803279)

Inside the project:

- Sheets: `repositories/anton-abyzov/specwithcode/packages/shared/src/officeSheet/`, PR #417, increment 1342
- Mods: `repositories/anton-abyzov/specwithcode/apps/web/src/mods/protocol.ts` and `sandbox.ts`
- Copilot turn limits: increment 1437
