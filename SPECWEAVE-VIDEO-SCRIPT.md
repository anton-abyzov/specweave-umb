# SpecWeave Intro — Finishing Script

**Goal:** finish the SpecWeave intro you started end of March. You have **8:47 already recorded** in your voice (`/Users/antonabyzov/Movies/DaVinci/Specweave_start_unfinished.mov`). This script continues from the exact word it cuts off on and runs the whole thing to **~23 minutes**.

**⚠️ CURRENT EDIT STATE (reconciled 2026-06-02):** The real assembly is **NOT** in `hyperframes-demo` — it's in **`repositories/anton-abyzov/specweave/video/hyperframes/`** (HeyGen HyperFrames; `npm run dev` to preview, `npm run render` to export). As of May 7 it already has: the raw 8:47 auto-trimmed by **SmartCut v4 → a 6:06 tight master** (`assets/master_tight.mp4`, 43 cuts / 32% dead air removed, sentence-aware — recovered "docs"/"with"/"And not only"), **11 timed motion overlays** (`assets/overlays.json`, covering the 0–269s pitch), and a fully-wired composition (`index.html`, root timeline = 366.61s). It is **not yet rendered** to a final MP4, and it stops at the WC2026 teaser (~6:06). The reusable Skill Studio overlays referenced in PART 5③ still live separately under `hyperframes-demo/scratch/skill-studio-intro/`.

**How to read this:** `>>` = what you say (narration). `[ ]` = what's on screen / B-roll / overlay. Timecodes are cumulative and approximate. Everything from **PART 5 onward is new** — that's what you record next.

---

## PART 1–4 — What you already have (recorded, 0:00 → ~8:47)

This is a recap of your existing take so you can see the seam. **Do not re-record** — it's already in your voice. Transcript recovered to `/tmp/sw-video/specweave-vo.txt`.

| # | Beat | Your words (paraphrased from the take) | On screen |
|---|---|---|---|
| 1 | **Cold open** (0:00–0:35) | Boris Cherny: *"Coding is largely solved… everyone's going to be a product manager."* He's right — but he left out the hard part. | Boris quote card → your face cam |
| 2 | **The mess** (0:35–2:00) | The coding is solved, but *everything around the coding is a mess.* Specs in the root, docs in random folders, plans overwritten next session. No structure, no memory. Not built for brownfield, multi-repo, multi-tech. Can't produce skills as you work. | Screen montage of scattered files |
| 3 | **The real shift** (2:00–3:30) | It's not just writing code through LLMs — it's doing *everything* through LLMs. Research, architecture questions, specs and edge cases, slides, prep. Before you touch a line of code, AI has interviewed you, written acceptance criteria, broken work into testable tasks. If you're still doing it by hand, you're competing against people who aren't. | B-roll: research, slides, planning |
| 4 | **Meet SpecWeave** (3:30–5:30) | A system that handles all of it — specs, code, tests, docs, GitHub sync, social posts, skill creation, learning from mistakes. It's called **SpecWeave** and it's open source. Works with any AI coding tool — Claude Code, Codex, Cursor. It helped me build and launch **10 projects in 3 months**. | SpecWeave logo / GitHub |
| 5 | **Structure is the multiplier** (5:30–8:00) | Permanent, searchable spec / plan / tasks files inside an **increment** — a folder = a product increase. TDD by default. **Living documentation** on by default — ADRs capture context, problem, reality, question, decision. Saves the LLM time, minimizes hallucinations. Auto-syncs with GitHub, Jira, Azure DevOps. **600+ increments, 500+ npm releases, 3,000+ commits.** | Open a real increment folder; ADR file |
| 6 | **Projects teaser — CUTS OFF HERE** (8:00–8:47) | *"Let's take a brief look at the 10 projects I've built. Almost all of them are in the App Store. … World Cup 2026 Travel — a mobile app and website that helps you follow your favorite players and teams… find the best ticket with integrations: FIFA, StubHub, SeatGeek… and not only — the system helps you build the trip: budget, flights, hotels, the full itinerary from day one to day end—"* | WC2026 app screens |

**⟵ The recording stops mid-sentence here, on the World Cup Travel app. PART 5 picks it up.**

---

## PART 5 — Finish the project tour (NEW · ~8:47 → 14:30)

> You wanted **3–4 highlighted projects, the rest mentioned briefly.** Below is my recommended set — **swap any of these**, they're modular 60–90s blocks. Highlight = short feature walkthrough; Mention = one line in a montage.
>
> **Highlights:** ① WC2026 Travel (continue) · ② EasyChamp · ③ Skill Studio / verified-skill.com · ④ AnyModel
> **Brief mentions:** Edufeed · Lulla · SketchMate · CCX · Obsidian Second-Brain

### ① WC2026 Travel & Ticket Companion — continue (8:47 → 10:00)
*(Pick up the cut without a beat. Jira project key for this one is literally `WTTC`.)*

>> "—from day one to the final whistle. And here's the part that matters for this video: I didn't build this the old way. I described it once — what it's for, who it's for, the ticketing integrations, the trip builder — and SpecWeave turned that into a spec, a plan, and a tested task list before I wrote a line of code. The FIFA, StubHub and SeatGeek integrations? Each one is its own increment, with its own acceptance criteria and tests. When something broke, I didn't lose the context — it's all written down in the spec. That's the whole point. Now let me show you the rest, faster."

[ Screen-record the WC2026 app: follow-a-team flow → stats → ticket redirect → trip builder. Lower-third chip: `WC2026 Travel · built with SpecWeave` ]

### ② EasyChamp (10:00 → 11:15)
>> "EasyChamp is the one with real users on it. It's a sports-competition platform — you run leagues and tournaments end to end. The fun part is the match engine: real FIFA-style player attributes feeding a statistical simulator, which I used to run a full **World Cup 2026 simulation**. This is not a toy. It's a production system with a database, a sync worker, an auth layer — and every one of those pieces went through the same spec-first loop. When you've got real users, 'the AI sort of wrote it' is not good enough. You need to know what it built and that it's tested. That's what the increments give me."

[ EasyChamp dashboard → a simulated WC2026 match → standings. Chip: `EasyChamp · production · real users` ]

### ③ Skill Studio / verified-skill.com (11:15 → 12:45)
>> "Remember early on I said these systems can't produce *skills* as you work? This is my answer to that. Anthropic shipped **Skills** in October 2025 — reusable prompts — but they're just loose Markdown files. No versioning, no tests, no way to trust one you didn't write. **Skill Studio** is the missing layer: author a skill, generate tests against its contract, version it, and install it into any AI tool — Claude Code, Cursor, Codex — with one command. And **verified-skill.com** is the registry behind it: over **110,000 skills**, every single one security-scanned before it's listed. Because the same week Claude Code's source leaked, a popular npm package got backdoored. 'Trust but verify' isn't a slogan here — it's a scanner."

[ `npx vskill@latest studio` boots → marketplace → security-scan PASS → install picker. Reuse the `skill-studio-intro` overlays: `at-0_38_marketplace`, `at-0_25-localhost-no-cloud`. Chip: `verified-skill.com · 110K+ scanned` ]

### ④ AnyModel (12:45 → 13:45)
>> "AnyModel is the plumbing. One interface, every model — GPT, Gemini, DeepSeek, Codex, local Ollama, three hundred-plus models — with smart retries and format translation so you never rewrite your code to switch brains. It's what lets me run the cheapest capable model for grunt work and the strongest one for the hard reasoning, without changing a thing upstream."

[ AnyModel CLI: same prompt routed to 3 different models. Chip: `anymodel.dev · 300+ models, one API` ]

### Brief mentions — rapid montage (13:45 → 14:30)
>> "And there's more, quickly: **Edufeed**, an education app. **Lulla**, **SketchMate** — both shipping on the App Store. **CCX** — clean-room AI coding CLIs in Go, Rust and .NET for people who don't want a 114-megabyte Node binary. And my **Obsidian second brain** — 6,700 notes that ingest, link, and organize themselves on a schedule. Ten projects in three months. Every one of them rode on the workflow I'm about to actually show you."

[ Fast 3–4s cuts of each, name chips. End on a grid of all logos. ]

---

## PART 6 — From scratch: the workflow (NEW · 14:30 → 19:00)

*This is the heart. Screen-record a real terminal + your AI tool. No mockups.*

### 6a. Install + init (14:30 → 15:45)
>> "Let me show you the whole thing from zero. One install."

[ Terminal: `npm install -g specweave` ]

>> "Then I drop into any project and initialize."

[ Terminal: `cd my-app && specweave init` — let the real output play. Point at the 'Next steps' block. ]

>> "Init isn't just making folders. It detects your stack, it can detect compliance standards if you're in a regulated shop, and it wires up your issue tracker — GitHub, Jira, or Azure DevOps — right here. That's it. Setup's done."

> **Note:** the old init printed a wrong command in 'Next steps' (`specweave increment`). That's fixed — it now correctly says `specweave create-increment`. Make sure you record on a build that has the fix (≥ 1.0.586).

### 6b. One request → a spec (15:45 → 17:00)
>> "Now I don't write code. I describe what I want."

[ In Claude Code / Cursor: type `/sw:increment "build a user authentication system"` ]

>> "Watch what comes back. Not code — a **spec**. User stories. Acceptance criteria, numbered: AC-US1-01, AC-US1-02. A plan with the architecture. And a task list where **every task already has a test** — given this, when that, then this. A product manager and an architect did their job before a single line got written. And I get to **review the plan** before anything happens. This is the step everyone skips, and it's the step that saves you."

[ Open the generated `spec.md`, `plan.md`, `tasks.md` side by side. Highlight the AC-IDs and the Given/When/Then blocks. ]

### 6c. Execute with tests (17:00 → 18:00)
>> "Now I let it build."

[ Terminal/agent: `/sw:do` (or `/sw:auto` for the unattended version). Show tests running after a task; a checkbox flipping to done; an AC flipping to checked in spec.md. ]

>> "Task by task. It runs the tests after each one. A task can't be marked done until its test passes — and as the tests pass, the acceptance criteria check themselves off in the spec. `/sw:auto` does this unattended for hours. I've literally shipped features while asleep."

### 6d. The payoff — it's just files (18:00 → 19:00)
>> "Here's the thing Cursor Rules and CLAUDE.md can't give you."

[ Open the `.specweave/increments/####-auth/` folder in the file tree. ]

>> "It's just Markdown. In your repo. Versioned. Diffable. Six months from now, anyone — including the AI — can open this folder and see exactly what was decided and why. Cursor tells the AI *use Tailwind*. SpecWeave tells the AI: *build a checkout flow with five acceptance criteria, test it, review it, sync it to Jira, and close it.* That's the difference between an instruction and a spec."

---

## PART 7 — Why teams adopt it: sync + quality gates (NEW · 19:00 → 21:30)

### 7a. External-tool sync (19:00 → 20:15)
>> "Everything I've shown works solo. This is what makes it work for a **team**."

[ Split screen: a SpecWeave increment ↔ a GitHub issue / Jira board / ADO board. ]

>> "SpecWeave syncs in both directions, but it's smart about it. The **content** — stories, acceptance criteria — flows *out* to your tracker. The **status** — open, closed, who's on it — flows *back in*. And your **commits and PRs** get posted onto the right issue automatically, grouped under the right story. A feature becomes an Epic or a Milestone. A user story becomes an issue. A task becomes a checkbox. So when I close an increment, the Jira story closes itself. When my PM closes an issue on their board, SpecWeave reads it back. Nobody double-enters anything. The board is never out of date. That's the tax this removes."

### 7b. Quality is enforced, not hoped (20:15 → 21:30)
>> "And 'done' actually means something. Before an increment can close, it runs the gates: a multi-agent **code review**, a **simplify** pass, a **grill** that tries to break the work, and an LLM **judge**. Plus a per-feature **rubric** that the increment has to measurably pass. If a gate fails, it doesn't close — it stays open and tells me why. The reason 36% of AI skills ship with security flaws is that nobody put a gate in front of them. SpecWeave's gate is on by default."

[ Show a `sw:done` run: code-review → simplify → grill → judge → rubric → closed-or-blocked. ]

---

## PART 8 — What shipped since I hit record (NEW · 21:30 → 22:45)

>> "I started recording this back in March. A couple of big things landed since, worth thirty seconds each."

>> "**One — Opus 4.8.** SpecWeave and Skill Studio both run on Anthropic's newest Opus out of the box now. Smarter planning, smarter reviews, same workflow."

>> "**Two — dynamic, multi-agent workflows.** There's a team-lead mode now: it fans one request out to a swarm of agents working in parallel, each owning its own increment, and merges the result. The autonomous loop got tighter too — implement, test, fix, repeat, until it's actually done."

>> "**Three — the gates got real.** That rubric I just showed you now genuinely blocks closure, and there's a verify step that actually *runs the app* after a change so a skipped test can't masquerade as green. The whole external-sync path — GitHub, Jira, Azure DevOps — got hardened so progress reliably reaches your tracker."

[ Quick chips for each: `Opus 4.8 default` · `multi-agent team-lead` · `live rubric gates + verify-runtime` ]

---

## PART 9 — Close (NEW · 22:45 → 23:30)

>> "That's SpecWeave. The coding is solved — but everything *around* the coding is where you win or lose now. Structure is the multiplier. It's open source, it works with whatever AI tool you already use, and it's one install away."

[ Full-screen card: ]
```
npm install -g specweave
github.com/anton-abyzov/specweave   ·   spec-weave.com   ·   verified-skill.com
```

>> "Start building while we still have this insane advantage. I'll see you in the next one — where I go deep on a single project, start to finish, live. Like, subscribe, and I'll put the links below."

[ End card + subscribe. ]

---

## Production notes

- **Total runtime:** ~23:30. The existing take is now a **6:06 tight cut** (down from the raw 8:47 after SmartCut) — plan the math off 6:06, not 8:47. You're adding ~14:45 of new narration on top.
- **Record PARTS 5–9** in your voice to match the existing take (same mic, same energy — the take is confident and direct; keep that).
- **Screen recordings to capture:** WC2026 app flow · EasyChamp match sim · `npx vskill studio` · AnyModel multi-model route · a real `specweave init` → `/sw:increment "auth"` → `/sw:do` → `/sw:done` session (record on ≥1.0.586 so the init fix is in) · a sync split-screen (increment ↔ GitHub/Jira/ADO).
- **Reusable overlays** already rendered in `hyperframes-demo/scratch/skill-studio-intro/`: marketplace-counts, localhost-no-cloud, skills-primitive, bell-pulse, validated. Style + the 4 accent colors are documented in that folder's READMEs.
- **Assemble** in HyperFrames at `repositories/anton-abyzov/specweave/video/hyperframes/` (`npm run dev`): the 6:06 tight master + its 11 overlays are already on the timeline; append the new PART 5–9 segments, add chips/overlays for the project tour (currently un-overlaid past 269s).
- **Chapters** (for YouTube description): 0:00 Problem · 3:30 Meet SpecWeave · 8:00 10 projects · 14:30 From scratch · 19:00 Team sync & gates · 21:30 What's new · 22:45 Close.
- **Stat discipline:** keep the numbers you already said (600+ increments, 500+ releases, 10 projects/3 months). The 110K+ scanned-skills figure is verified (registry shows 110,949 published).

## Swap list (your call — say the word)
If you'd rather highlight your **consumer App Store apps** over dev tools, the easiest swaps in PART 5:
- Promote **Edufeed / Lulla / SketchMate** from "mention" → "highlight" (drop AnyModel or Skill Studio to "mention").
- Keep **WC2026 Travel** as the lead either way — your recording already commits to it.
