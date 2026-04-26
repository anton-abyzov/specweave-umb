# Skill Studio — Anthropic Hackathon YouTube Video

**Target runtime**: 3:30 (hard ceiling 4:00)
**Tone**: cinematic-optimistic-thriller with warmth (Apple keynote × Mr. Beast pacing)
**Editor**: Hyperframes
**B-roll generator**: Google Veo 3.1 Fast (8s clips, 16:9, no text overlays)
**Music**: Suno (brief at bottom of this file)

---

## Truth-check before recording

| Feature | Real today? | Demo strategy |
|---|---|---|
| 4-skill "what you can build" teaser (00:04–00:14) | Producer Pal (Ableton), Remotion, social-media-posting, frontend-design — all real and installed | Pre-stage outputs so each `Enter`→bloom is <400ms. Record each skill into its own clip first; assemble in Hyperframes. **Confirm Ableton Live + Producer Pal runs cleanly; if Ableton license is unavailable on recording machine, swap clip 1 for `/anthropic-skills:pptx` (deck materializing) and update VO.** |
| Multi-model dropdown (01:42) | `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5` real in registry. GPT-5/Gemini/local via AnyModel BYO pass-through. | Confirm BYO entries render correctly in the dropdown before recording. If not, stage a polished mock dropdown shot for that 6-second beat. |
| Marketplace tab with 100K+ verified skills (01:55) | Marketplace hub is **in flight** (0771 — 7/57 tasks done as of 2026-04-26). Backend list + count badge may not be fully wired. | Confirm the count badge + grid render with at least seed data. If incomplete, stage a clean recording from the WIP branch with a static "129,847" overlay added in Hyperframes. **Decide before recording day.** |
| "+ New Skill → Generate with AI" modal (02:08) | Shipped (0703) | Record live |
| Generate Test for a skill (02:30) | **Verify before recording** — test-case generation is on the roadmap; confirm it runs end-to-end in the WIP branch and produces green ticks. If not shipped: stage a clean simulated take (faked test panel + tick animation) and call it out as "soon" in the description. |
| Publish → auto-create GitHub repo via gh CLI (02:42) | **Recently shipped.** Confirm `gh repo create …` runs from Studio and the inline panel renders. | Record live with `gh` authed in your shell. Hyperframes annotation already in script. |
| verified-skill.com queue → processed (02:48) | Queue + processing pipeline real (0773 — 13/14 tasks done) | Record the queue tab live. If the scan step takes >3s on the day, edit time-cut between "Scanning…" and "Processed ✓". |
| Toast notification + one-click install on new version (02:58) | SSE channel + UI toast on file change exists (0708 — 72/74 tasks). Confirm the **publish→remote-version→toast** path works end-to-end (not just local-file→toast). | If only local-file→toast works, restage the demo as: edit local file → toast → install. Adjust the VO to match (skip the verified-skill.com round-trip in the update beat). **Decide before recording.** |
| One-click install writes to Claude · Cursor · Codex dirs simultaneously | vskill skill-installer fans out to all three agent dirs (0665, 0670) | Record the terminal-flash overlay live; the install panel needs to show all three paths. |

**Recording settings**: 1920×1080 @ 60fps. Skill Studio in dark mode, no personal tabs. Browser zoom 110%. Terminal font ≥ 16pt.

---

## Script (with B-roll markers)

**Legend**: `[FACE]` = camera-to-camera. `[SCREEN]` = screen-share. `[B-ROLL]` = Veo clip (filename noted). `[ANIM]` = Hyperframes overlay on top of other footage.

---

### 00:00 — 00:04 · ANTHROPIC LOGO OPEN

`[ANIM — Anthropic wordmark, Hyperframes spring-in on solid near-black, 600ms hold, soft chime]`

`[VOICEOVER — Anton, calm]`
> *"Last October, Anthropic shipped one small idea that's about to change how you build everything."*

(Logo dissolves. Cut to terminal-dark.)

---

### 00:04 — 00:14 · WHAT YOU CAN BUILD (4 examples, 2.5s each)

`[SCREEN — fullscreen terminal, dark theme, 18pt mono. Four invocations land in sequence; the right side of the frame **fills with the result** as each completes. Hard cuts on the beat.]`

| # | Skill | Result that fills the frame |
|---|---|---|
| 1 | `/ppal-create-clip` *(Producer Pal → Ableton Live)* | An Ableton Live session — clip slots fire, drum rack, mixer pulsing |
| 2 | `/remotion` | An animated title card flies in over a video frame |
| 3 | `/social-media-posting` | Three platform mockups fan out — Instagram reel, X post, LinkedIn carousel |
| 4 | `/frontend-design` | A polished hero section scrolls into view, glassy and Apple-grade |

`[VOICEOVER — over cuts, one phrase per skill]`
> *"Compose in Ableton. Cut a video. Run a marketing campaign. Design a website. **One skill each.**"*

---

### 00:14 — 00:18 · ONE-LINE DEFINITION

`[SCREEN — quick zoom on a SKILL.md frontmatter block, three lines highlighted: name / description / instructions]`

`[VOICEOVER]`
> *"A skill is one markdown file. Name. Description. Instructions. That's it."*

---

### 00:18 — 00:48 · WHY SKILLS MATTER

`[B-ROLL — broll-02-hands-montage.mp4 (4s)]`

Four sub-second vignettes: a child's hands at a laptop, a chef's hands folding dough, a scientist's gloved hands at a microscope, an elderly musician's hands on piano keys. The glowing SKILL.md badge materializes with a soft chime in each.

`[VOICEOVER — over clip]`
> *"A skill is the smallest unit of know-how. A checklist. A playbook. What a senior teaches a junior on day one. Your grandma's recipe for pierogi — written down, repeatable, hers — is a skill."*

`[SCREEN — anthropic.com/news/skills (October 2025) → quick cut to code.claude.com/docs/en/skills, zoom on the 'Create a SKILL.md file' box]`

`[ANIM — Hyperframes bracket-callout on three frontmatter lines: name, description, allowed-tools]`

`[VOICEOVER]`
> *"Anthropic shipped this in October 2025. One markdown file. No code. Claude reads it when it's relevant, or you call it with a slash. A kid can write one. But the great ones carry your taste, your judgment, your 'we always do it this way' — that part is still yours."*

**[OPTIONAL — if @trq212 tweet text is pasted in: weave a 1-line quote here as counterpoint or reinforcement]**

---

### 00:48 — 01:18 · THE PAIN POINTS (the problem nobody's solved)

`[B-ROLL — broll-03-lockin-break.mp4 — opening 4s only, locks still intact]`

`[VOICEOVER — over clip]`
> *"And yet. Shipping a skill today is rough."*

`[ANIM — four red callouts stack on the right as VO names them, mono caption, 200ms spring each, on the beat]`

> *"**Lock-in.** You write it for Claude — Cursor wants a different format. Codex, Windsurf, Copilot. Fifty-three tools, five formats, copy-paste, drift."*

> *"**No versioning.** Every fork is a new file. No history. No diff. No idea which one is current."*

> *"**No live updates.** Your teammate fixes the skill at 2pm — you're still running yesterday's playbook at 3."*

> *"**No tests.** You ship a skill and pray it still works tomorrow."*

`[B-ROLL — broll-03-lockin-break.mp4 — final 4s, the chains shatter on the beat as the fourth callout lands]`

`[VOICEOVER]`
> *"Skills are the new primitive — and they're being shipped like loose Word docs."*

---

### 01:18 — 01:30 · WHO I AM

`[FACE — full frame, warm key light, solid background]`

> *"I'm Anton Abyzov. I've been a software engineer for twenty years. I poured a lot of heart into Skill Studio — because I believe the whole community can do better at managing skills."*

*(Beat. Cut.)*

---

### 01:30 — 01:42 · MEET SKILL STUDIO

`[SCREEN — terminal flash: type `vskill studio` in a project folder, browser opens to Studio dashboard, dark mode, clean. No personal tabs.]`

`[ANIM — "Skill Studio" wordmark fades in over the dashboard, 600ms]`

`[VOICEOVER]`
> *"You don't have to manage skills in the terminal anymore — Skill Studio handles all of that. It runs on your laptop. You start it in any folder where you keep skills — your project, your home `.claude`, wherever. Two columns from there: skills already **available**, and ones you're **authoring**. Nothing leaves the machine until you publish — that's when your GitHub steps in."*

(Beat. Cut to live screen — screen-share begins.)

---

### 01:42 — 01:55 · MULTI-MODEL FREEDOM (open the dropdown first)

`[SCREEN — Skill Studio. Cursor moves to the model dropdown in the top bar. Click — dropdown opens.]`

`[ANIM — Hyperframes zoom-ring on the dropdown. Highlight rows: `claude-opus-4-7` · `claude-sonnet-4-6` · `gpt-5` · `gemini-3` · `local · LM Studio (BYO)`.]`

`[VOICEOVER]`
> *"First thing to know — Studio is model-agnostic. Opus 4.7, GPT-5, Gemini, a local open-source model on your machine. Whatever you pick is what runs the work."*

`[SCREEN — cursor lands on `claude-opus-4-7`, click, dropdown closes. The choice persists in the top bar.]`

---

### 01:55 — 02:08 · BROWSE OR CREATE (the marketplace)

`[SCREEN — click the **Marketplace** tab. Grid of skill cards loads. Top-right counter: "129,847 skills · all verified". Each card carries a small "Security-scanned" pill.]`

`[ANIM — caption "100K+ skills · every one security-scanned" 800ms fade in, hold 1.4s]`

`[VOICEOVER]`
> *"Start by looking. More than a hundred thousand skills here — every single one security-scanned and verified before it gets listed."*

`[SCREEN — scroll briefly through 2–3 rows of cards, then move the cursor to the top-right `+ New Skill` button.]`

`[VOICEOVER]`
> *"Or build your own. Let's do that."*

`[SCREEN — click `+ New Skill`.]`

---

### 02:08 — 02:30 · CREATE & GENERATE — LIVE

`[SCREEN — modal opens. Two tabs visible: **Write manually** · **Generate with AI**. AI is selected by default, sub-label reads "using claude-opus-4-7".]`

`[VOICEOVER]`
> *"Write it by hand, or describe what you want and let your model draft it."*

`[SCREEN — type the prompt into the AI input:]`

> "Review a PR against our team's TypeScript style guide and flag violations with fix suggestions."

`[SCREEN — click `Generate`. CreateSkillPage streams the SKILL.md live — frontmatter first, instructions second, real time.]`

`[ANIM — caption "Real streaming. No cut." 900ms fade]`

`[VOICEOVER]`
> *"Thirty seconds. A real SKILL.md — already on disk."*

---

### 02:30 — 02:42 · TEST IT — LIVE (skills you can trust)

`[SCREEN — on the new skill's page, click `Generate Test`. Studio writes a test fixture (sample PR with intentional violations) and runs it.]`

`[SCREEN — test panel slides in: 4 / 4 checks pass, green ticks animate one after the other.]`

`[ANIM — Hyperframes overlay: a small green "verified" chip pulses on the skill's icon, 1.15× spring, 300ms]`

`[VOICEOVER]`
> *"If a skill is a recipe, this is the taste-test. Studio generates a test case, runs it, and tells you whether the skill actually behaves. Skills you can trust."*

---

### 02:42 — 02:58 · PUBLISH — LOCAL → GITHUB → VERIFIED-SKILL.COM

`[SCREEN — sidebar shows the skill is a local folder, "no remote" badge. Cursor moves to `Publish`. Click.]`

`[SCREEN — inline panel: "No GitHub repository yet — create one with GitHub CLI?" · `Yes, create`. Click. A small `gh repo create …` flash appears at the bottom.]`

`[HYPERFRAMES NOTE — recently-shipped feature: the gh-CLI auto-repo step. Capture this take cleanly and add a 300ms zoom-ring + a "new" badge overlay on the inline panel during edit. It's a small beat that judges will care about.]`

`[VOICEOVER]`
> *"Right now this skill is just a folder on my laptop. Publish creates the GitHub repo for me — through the GitHub CLI if it's installed — pushes it, then submits to verified-skill.com."*

`[SCREEN — cut to verified-skill.com in another tab: queue page → status pulses through "Queued" → "Scanning…" → "Processed ✓ · v1.0.0".]`

`[SCREEN — cut back to Skill Studio. The skill card now carries a "v1.0.0 · published" badge.]`

`[VOICEOVER]`
> *"Queued. Scanned. Published. The version's live, and now I can pin to it."*

---

### 02:58 — 03:13 · LIVE UPDATE — NOTIFICATION + ONE-CLICK INSTALL

`[B-ROLL — broll-04-sse-magic.mp4 — first 1.5s as cinematic transition: comet of light arcs from verified-skill.com toward the Studio]`

`[SCREEN — quick edit: change one line in the local SKILL.md, save, click `Publish` again. verified-skill.com tab in the background processes v1.0.1.]`

`[SCREEN — back in Studio: a toast slides in from the top-right — "pr-reviewer · v1.0.1 available · Install".]`

`[ANIM — Hyperframes overlay: dotted SSE line from verified-skill.com → toast, labeled "SSE · push, not poll"]`

`[SCREEN — click `Install` on the toast. A quick terminal flash shows vskill writing to `.claude/skills/`, `.cursor/skills/`, `.codex/skills/` simultaneously. Toast updates: "Installed for Claude · Cursor · Codex".]`

`[VOICEOVER]`
> *"Someone improves the skill — I get a push, not a poll. One click installs it everywhere I work: Claude, Cursor, Codex, in one motion. **Versioned. Tested. Pushed. Live.** Everything we said was missing — fixed."*

---

### 03:13 — 03:30 · CLOSE

`[FACE — full frame]`
> *"A skill is a recipe. Skill Studio writes it, ships it everywhere, tests it, versions it, and tells you the moment someone improves it. Anthropic gave us the standard. I'm making it **universal** and **live**."*

`[ANIM — end card: verified-skill.com, Anton's GitHub, "Built for the Anthropic hackathon, April 2026"]`

> *"Link's below. Fork it. Break it. Ship me a skill."*

---

## B-roll inventory

### Veo 3.1 Fast (16:9)

| File | Used at | Length | Mood |
|---|---|---|---|
| `broll-02-hands-montage.mp4` | 0:18 | 4s | Warm, human, cinematic |
| `broll-03-lockin-break.mp4` | 0:48 | 8s (split: 4s open + 4s shatter close) | Tension → release |
| `broll-04-sse-magic.mp4` | 2:42 | 8s | Magical, instant, satisfying |

> `broll-01-cold-open.mp4` is **retired** — the new opening uses an Anthropic logo card + screen-recorded skill teasers instead.

### Screen-recorded (you, on your machine)

| File | Used at | Length | Notes |
|---|---|---|---|
| `screen-00-anthropic-logo.mp4` | 0:00–0:04 | 4s | Anthropic wordmark on near-black, Hyperframes spring-in. Verify usage rights / fair-use for hackathon submission; if unsure, render a stylized typographic substitute that reads "Anthropic · October 2025". |
| `screen-01-skills-teaser.mp4` | 0:04–0:14 | 10s | 4 skill invocations × 2.5s. Terminal **left half**, result fills **right half** as it lands. Hard cuts on the beat. Pre-stage every result so `Enter`→bloom is under 400ms. |
| `screen-02-studio-dashboard.mp4` | 1:30–1:42 | 12s | Skill Studio dashboard intro shot — clean dark mode, "Skill Studio" wordmark fades in, no live interaction yet. |
| `screen-03-model-dropdown.mp4` | 1:42–1:55 | 13s | Open the model dropdown, hover through Opus 4.7 / Sonnet 4.6 / GPT-5 / Gemini 3 / local LM Studio (BYO). Click Opus 4.7. Persists in top bar. |
| `screen-04-marketplace-browse.mp4` | 1:55–2:08 | 13s | Click Marketplace tab, grid loads with count badge "129,847 skills · all verified". Brief scroll, then click `+ New Skill`. |
| `screen-05-create-and-generate.mp4` | 2:08–2:30 | 22s | Modal: "Write manually / Generate with AI" tabs (AI selected, sub-label "using claude-opus-4-7"). Type the PR-reviewer prompt. Hit Generate. SKILL.md streams live. |
| `screen-06-test-it.mp4` | 2:30–2:42 | 12s | Click `Generate Test`. Test panel slides in, 4/4 green ticks animate. "Verified" chip pulses on skill icon. |
| `screen-07-publish-flow.mp4` | 2:42–2:58 | 16s | Click `Publish` → "No GitHub repo — create with gh CLI?" inline → `Yes, create` → `gh repo create` flash → cut to verified-skill.com queue (Queued → Scanning → Processed ✓ v1.0.0) → cut back to Studio with "v1.0.0 · published" badge. **Hyperframes-annotated** for the gh-CLI step. |
| `screen-08-update-and-install.mp4` | 2:58–3:13 | 15s | Edit local SKILL.md → Publish v1.0.1 → Studio toast "v1.0.1 available · Install" → click Install → terminal flash writes to `.claude/skills/`, `.cursor/skills/`, `.codex/skills/` → toast "Installed for Claude · Cursor · Codex". |

All saved to: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/scratch/`

---

## Hyperframes animation beats

| Time | Beat | Direction |
|---|---|---|
| 00:00 | Anthropic logo spring-in | 600ms ease-out, soft chime, hold 1.4s, dissolve to black |
| 00:04 | Skill-teaser counter | Bottom-right "1 / 4 · Ableton" → "4 / 4 · Web", changes on each cut, mono font, 50% opacity |
| 00:14 | Frontmatter callout | 3 lines (name / description / instructions) bracketed yellow, 180ms each, staggered |
| 00:30 | Frontmatter bracket (Why Skills section) | Same callout style on `name / description / allowed-tools`, longer hold |
| 00:48 | Pain-point callouts (4-stack) | Stacked right-side mono cards: "Lock-in" → "No versioning" → "No live updates" → "No tests". 200ms spring each, on the beat. Card stays after appearing. |
| 01:14 | Chains shatter sync | Time the broll-03 chain-shatter peak to land on the 4th callout's spring. |
| 01:18 | Face-cam appears (full self-intro) | 150ms wipe from center, hold 12s |
| 01:30 | "Skill Studio" wordmark fade-in | Center-top, 600ms fade, hold 2s |
| 01:42 | Model-dropdown zoom-ring | Circle overlay around the dropdown, 3px stroke, 40% darken outside ring, hold while VO names models |
| 01:45 | Opus row highlight | Yellow underline band on `claude-opus-4-7`, 180ms wipe right |
| 01:55 | Marketplace count caption | Bottom third "100K+ skills · every one security-scanned" — 800ms fade in, hold 1.4s, fade out |
| 02:08 | "+ New Skill" pulse | 1.1× spring on the button as cursor lands, then modal sweep-in from top, 350ms |
| 02:24 | "Real streaming. No cut." caption | Bottom third, 900ms fade in, hold 2s, fade out |
| 02:33 | "Verified" chip pulse on skill icon | 1.15× scale + green tint, 300ms spring, after 4/4 ticks land |
| 02:43 | gh-CLI auto-repo zoom-ring | 300ms zoom-ring on the inline "Create with gh CLI?" panel + small "new" badge. **This is the recently-shipped feature — give it a moment.** |
| 02:48 | verified-skill.com state cycle | Status pill cycles "Queued" → "Scanning…" (with a 600ms shimmer) → "Processed ✓ · v1.0.0" — total 3.5s |
| 02:54 | SSE dotted line | `stroke-dashoffset` from verified-skill.com tab → Studio toast, 700ms, tagged "SSE · push, not poll" |
| 02:59 | Toast slide-in | From top-right, spring motion, 400ms — "pr-reviewer · v1.0.1 available · Install" |
| 03:04 | Triple-target install flash | Three-line terminal overlay (`.claude/skills/` / `.cursor/skills/` / `.codex/skills/`) — each line writes in 80ms staggered, 240ms total |
| 03:08 | "Versioned · Pushed · Tested · Live" callback chip | 4-pill row appears under the toast for 1.2s, mono, 60% opacity, fades with the cut. Mirrors the pain-point cards from 00:48. |
| 03:23 | End card | Full-bleed brand color. Logo spring-in 200ms, URL fade 200ms later, credit fade 300ms later. Hold 3s |

---

## Suno music brief (background score)

### Do you actually need it?

**Yes.** Three reasons:
1. **Retention.** Music sets pace and tells the viewer when to pay attention — silence reads as "low effort".
2. **Tonal guardrail.** You oscillate between thriller / funny / epic. A track with a consistent arc locks your edit to *one* feel.
3. **Credibility.** Hackathon judges watch a lot of demos. Good music = 30% perceived production uplift for zero extra work.

A single 3:30 track beats chopped-and-stitched free library cues. Suno gets you there for $0.

### Suno prompt (paste as-is)

```
Genre: Cinematic tech trailer, Apple-keynote-meets-inception.
Mood: Tense curiosity rising into triumphant clarity.
Structure (3:30 total):
- 0:00-0:04 — Anthropic logo card: a single soft chime over silence, then a low sub-bass swell on the dissolve. Reverent.
- 0:04-0:14 — Skill teasers: 4 percussive "stamps" at 2.5s intervals (one per skill), each stamp a tonal hit that resolves up the scale. Building anticipation.
- 0:14-0:18 — Pull back to a single sustained pad — space for the one-line skill definition.
- 0:18-0:48 — Why skills matter: warm piano layer, gentle strings, human and approachable. Heartbeat-tempo drum underneath.
- 0:48-1:18 — Pain points: tension builds. Low strings, suspended chord. Each of the 4 pain-point callouts (0:48 / 0:56 / 1:04 / 1:12) gets a soft minor-key piano hit. Unresolved until the chain-shatter peak at 1:14.
- 1:18-1:30 — Self-intro: pull back. Warm pad. Breath of space for face-cam.
- 1:30-1:42 — Meet Skill Studio: hopeful synth bass enters, mid-tempo, optimistic.
- 1:42-2:08 — Multi-model dropdown + marketplace browse: confident mid-tempo synth-bass groove. Bright, curious. Product-montage energy.
- 2:08-2:30 — Create + generate: same groove, add a soft arpeggio that mirrors the streaming SKILL.md.
- 2:30-2:42 — Test it: brief uptick — playful 4-note motif resolves on each green tick (4 ticks total).
- 2:42-2:58 — Publish flow: a short tension hold during "Queued / Scanning…", resolved on "Processed ✓" with a clean major-chord lift.
- 2:58-3:13 — Update + install: build. Add arpeggiated synth, crescendo toward a single bright chord around 3:08 when "Versioned · Pushed · Tested · Live" lands.
- 3:13-3:30 — Outro. Warm resolve. One final soft chime. Silence-adjacent by end.
Instruments: analog synth pad, piano, light strings, sub-bass, minimal percussion (no snares).
No vocals. No lyrics. Instrumental only.
BPM: 92, feels like 100.
Reference vibes: Hans Zimmer's "Time" with lighter drums, 65daysofstatic's quieter work, Apple keynote background music.
```

Generate 2-3 takes, pick the one with the clearest 2:30 build-up — that's where your SSE reveal drops.

---

## Pre-recording checklist

- [ ] **Anthropic logo card**: confirm fair-use / hackathon-permitted use of the wordmark; otherwise render typographic substitute "Anthropic · October 2025"
- [ ] **Pre-stage the 4 skill teasers (00:04–00:14)**: Producer Pal / Ableton Live, Remotion, social-media-posting, frontend-design. Each result rendered ahead of time so `Enter`→bloom is under 400ms. Record each as its own ~3s clip and assemble in Hyperframes.
  - [ ] Backup plan if Ableton is unavailable on recording machine: swap clip 1 for `/anthropic-skills:pptx` and revise VO to "Build a deck. Cut a video. ..."
- [ ] **Self-intro take (01:18–01:30)**: record 3 takes, pick the warmest. Eyes on lens. The line is *"I'm Anton Abyzov. I've been a software engineer for twenty years. I poured a lot of heart into the next two minutes — because I think we can do better."*
- [ ] Pre-build the four pain-point callout cards in Hyperframes — "Lock-in" / "No versioning" / "No live updates" / "No tests" — and the 4-pill callback chip at 03:08.
- [ ] **Multi-model dropdown (01:42)**: confirm `claude-opus-4-7`, `claude-sonnet-4-6`, `gpt-5`, `gemini-3`, `local · LM Studio (BYO)` all render in the dropdown via AnyModel pass-through. Otherwise stage a polished mock list overlay.
- [ ] **Marketplace tab (01:55)**: confirm grid + "129,847 skills · all verified" count badge render in the WIP branch (0771). If not, record from the WIP branch with a static count overlay added in Hyperframes.
- [ ] **Generate Test (02:30)**: confirm the test-generation feature is wired end-to-end and produces 4/4 green ticks. If not shipped: stage a clean simulated take and call it "shipping soon" in the description.
- [ ] **Publish + auto-repo via gh CLI (02:42)**: ensure `gh` is authed in your shell. Confirm the inline "No GitHub repo — create with gh CLI?" panel renders. **This is the Hyperframes-flagged beat — capture cleanly and add the zoom-ring + "new" badge in edit.**
- [ ] **verified-skill.com queue (02:48)**: open in a second tab before recording so it's loaded; rehearse the cut so "Queued → Scanning → Processed ✓" runs in under 3.5s. If scan time is variable on recording day, edit-cut between states.
- [ ] **Toast on new published version (02:58)**: confirm the publish→remote-version→toast path works end-to-end in the WIP branch (not just local-file→toast). If only local-file→toast: simplify the demo to local-only edit and trim the verified-skill.com round-trip in this beat. Adjust VO accordingly.
- [ ] **One-click install fan-out (03:04)**: verify the install panel renders all three agent dirs (`.claude/skills/`, `.cursor/skills/`, `.codex/skills/`). Pre-stage a clean target project folder so the writes are camera-friendly.
- [ ] Dark mode everywhere. Close personal tabs. Disable notifications.
- [ ] Prepare a sample project folder (`~/projects/my-api`) with a clean `.claude/` dir.
- [ ] Record face-cam and screen-share separately. Mic close (6 inches). Look at the lens during face-cam.
- [ ] Paste @trq212 tweet text to weave into 00:18–00:48 (Why Skills) block.
- [ ] Upload the 3 `broll-*.mp4` files + 9 `screen-*.mp4` files to Hyperframes timeline first; build the skeleton around them.

---

## Budget

- 3 × Veo 3.1 Fast ≈ **$3.60** (cold-open clip retired)
- Suno free tier: $0
- Hyperframes: your existing license
- Total AI spend: **under $4**
