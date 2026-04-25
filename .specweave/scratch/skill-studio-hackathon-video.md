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
| `npx vskill install frontend-design` | vskill CLI ships skill-installer that fans out to Claude/Cursor/Codex (0665, 0670) | Record live. Confirm install logs show all three agent dirs being written. |
| Apple-Watch scroll-fold demo | frontend-design skill is real; the **specific page** isn't a baked example | Generate it 2–3 times **before** recording, pick the cleanest take, replay. Acceptable to use a pre-rendered page that the prompt-line "rebuilds" on cue — judges expect this for live demos. |
| "+ New Skill → Generate with AI" modal | Shipped (0703) | Record live |
| ⌘K model picker with Opus 4.7 + "routing to…" sub-line | Shipped (0703) | Record live |
| OpenAI / open-source in the dropdown | Registry has only `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5`. OpenAI/local via AnyModel BYO pass-through. | Either stage a mock dropdown, or show a real BYO entry via AnyModel. **Confirm before recording.** |
| Skill lands in a project folder, usable | Canonical installer writes per-agent dirs (0665) | Record live |
| Edit a skill → SSE push → UI badge/icon change | SSE endpoint exists; 72/74 tasks done on 0708 | **Confirm icon-color-change is working in WIP branch. If not: simulate cleanly.** |

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

### 00:18 — 00:30 · INSTALL & USE — LIVE (the split-screen reveal)

`[SCREEN — fullscreen terminal, cursor blinking. Type live, no cut:]`

```
$ npx vskill install frontend-design
```

`[ANIM — caption "vskill — universal skill installer · works in Claude, Cursor, Codex" 800ms fade-in, hold 1.5s]`

`[SCREEN — install streams: progress bar, ✓ "Installed for Claude · Cursor · Codex"]`

`[CAMERA MOVE — 700ms ease. Terminal pane slides left, lands at **1/3 width**. The right **2/3** reveals a Chromium window, dark chrome.]`

`[SCREEN — terminal (left third): type one line:]`

```
> Build an Apple-style product page for Apple Watch.
  Pin the hero. As I scroll, fold the watch open
  into its components — case, crown, sensor stack,
  band — each labeled, each in its own section.
```

`[SCREEN — right two-thirds: the page renders live. Hero pinned. As the (auto-driven) scroll advances, the watch breaks apart into sub-components, each unfolding into its own pinned section in the apple.com style. 60fps. No jank.]`

`[VOICEOVER — over the scroll]`
> *"One install. One prompt. Apple-grade scroll choreography — written by a skill anyone in this community can fork."*

(Beat. Hold the final unfolded-watch frame 400ms. Cut to face.)

---

### 00:30 — 00:38 · WHO I AM

`[FACE — tight, solid background]`
> *"I'm Anton. I built something for Anthropic's hackathon. Two more minutes — why this matters, and the one problem nobody's solved yet."*

*(Beat. Cut.)*

---

### 00:38 — 01:08 · WHAT IS A SKILL, REALLY (the deeper bit)

`[B-ROLL — broll-02-hands-montage.mp4 (4s)]`

Four sub-second vignettes: child's hands at a laptop, chef's hands folding dough, scientist's gloved hands at a microscope, elderly musician's hands on piano keys. The glowing SKILL.md badge materializes with a soft chime in each.

`[VOICEOVER — over clip]`
> *"A skill is the smallest unit of know-how. A checklist. A playbook. What a senior teaches a junior on day one. Your grandma's recipe for pierogi is a skill."*

`[SCREEN — anthropic.com/news/skills (October 2025 announcement) → quick cut to code.claude.com/docs/en/skills, zoom on the 'Create a SKILL.md file' box]`

`[FACE — 30% corner]`
> *"Anthropic shipped Skills in October 2025. One file: a `SKILL.md`. Claude reads it when it's relevant — or you call it with a slash. No code required."*

`[ANIM — Hyperframes bracket-callout on three frontmatter lines: name, description, allowed-tools]`

> *"A kid can write one. An AI **cannot** write a great one without you — because the taste, the judgment, the 'we always do it this way' — that part is yours."*

**[OPTIONAL — if @trq212 tweet text is pasted in: weave a 1-line quote here as counterpoint or reinforcement]**

---

### 01:08 — 01:20 · THE PROBLEM (the lock-in break)

`[B-ROLL — broll-03-lockin-break.mp4]`

Seven tool logos floating, each padlocked to a dim SKILL.md with a thick red chain. A bright SKILL.md badge flies in, strikes the center, all chains shatter in slow-mo. Logos pulse in unison. Mood: liberating.

`[VOICEOVER — over clip]`
> *"Here's the catch. You wrote the skill for Claude. Cool. Switch to Cursor. Codex. Windsurf. Copilot. Fifty-three tools. Each one wants a different format — so you write it five times, or you stay locked in. **That's what Skill Studio fixes.** Watch."*

---

### 01:20 — 02:10 · LIVE DEMO — GENERATE (this is Skill Studio)

`[SCREEN — open Skill Studio locally. Land on dashboard.]`

`[FACE — 30% corner, 2 sec]`
> *"This is Skill Studio. Runs on my laptop. No cloud, no login."*

`[SCREEN — click `+ New Skill`, modal opens. Type: "Review a PR against our team's TypeScript style guide and flag violations with fix suggestions"]`

`[SCREEN — hit ⌘K. Model picker opens.]`

`[ANIM — Hyperframes zoom-ring on the picker, highlight the "routing to claude-opus-4-7[1m]" sub-line]`

> *"Model picker. Opus 4.7 — Anthropic's newest — is what I'll use to generate. But watch this—"*

`[SCREEN — scroll picker, pause briefly on GPT-5, Gemini 3, a local LM Studio entry via AnyModel BYO]`

> *"—I can route to GPT-5, Gemini, or a local open-source model on my machine. Because the skill I'm generating is universal, the **generator** is too."*

`[SCREEN — click Opus 4.7. Hit Generate. CreateSkillPage streams the SKILL.md live — frontmatter first, instructions second.]`

`[ANIM — caption "Real streaming. No cut." 900ms fade]`

> *"Thirty seconds. Done. That's a real SKILL.md — runnable in Claude Code right now."*

---

### 02:10 — 02:35 · USE IT IN A PROJECT (now in Claude Code)

> **Note**: opening already showed install + use via vskill. This section pivots: **same skill, different agent (Claude Code)** — proves portability. Trim 5s vs. previous cut.

`[SCREEN — terminal: `cd ~/projects/my-api && ls .claude/skills/` — the new `pr-reviewer/` directory is there]`

> *"Skill Studio dropped the file into my project. No npm install, no registry dance. It's on disk."*

`[SCREEN — open Claude Code in the same folder, type `/pr-reviewer`]`

`[ANIM — zoom on the slash-command autocomplete]`

> *"Claude Code picks it up. Live. Same skill — I could point Codex or Cursor at the same folder and it'd work there too. That's the 'universal' part."*

---

### 02:35 — 02:43 · PREVIEW THE MAGIC (cinematic, no face)

`[B-ROLL — broll-04-sse-magic.mp4]`

Split screen. A keystroke in the terminal launches a comet of light across the gap; it strikes a dashboard icon, which pulses and shifts color. Toast slides in from the top-right. Mood: instant, magical.

`[VOICEOVER — over clip]`
> *"Okay — this is the part I'm most proud of."*

---

### 02:43 — 03:13 · THE MAGIC — LIVE

`[SCREEN — Skill Studio on left, terminal on right. Skill icon in Studio is neutral gray.]`

`[SCREEN — in terminal, edit `pr-reviewer/SKILL.md`, change a line, save.]`

`[SCREEN — within a second, the Studio icon pulses and shifts color. Toast: "Skill updated — v1.0.1 → v1.0.2".]`

`[ANIM — Hyperframes overlay: dotted line from file-save to icon, labeled "SSE"]`

> *"Server-Sent Events. Push, not poll. My file system told the Cloudflare hub, the hub told Studio, Studio told me. One second, end to end."*

`[SCREEN — click the toast. Diff view opens, line-by-line.]`

> *"And I get the **diff** — not 'something changed', exactly what changed. Because when skills are live infrastructure, knowing what changed matters as much as knowing that it changed."*

---

### 03:13 — 03:30 · CLOSE

`[FACE — full frame]`
> *"A skill is a recipe. Skill Studio writes it, ships it to every tool you use, and tells you the instant someone improves it. Anthropic gave us the standard. I'm making it **universal** and **live**."*

`[ANIM — end card: verified-skill.com, Anton's GitHub, "Built for the Anthropic hackathon, April 2026"]`

> *"Link's below. Fork it. Break it. Ship me a skill."*

---

## B-roll inventory

### Veo 3.1 Fast (16:9)

| File | Used at | Length | Mood |
|---|---|---|---|
| `broll-02-hands-montage.mp4` | 0:38 | 4s | Warm, human, cinematic |
| `broll-03-lockin-break.mp4` | 1:08 | 8s | Tension → release |
| `broll-04-sse-magic.mp4` | 2:35 | 8s | Magical, instant, satisfying |

> `broll-01-cold-open.mp4` is **retired** — the new opening uses an Anthropic logo card + screen-recorded skill teasers instead.

### Screen-recorded (you, on your machine)

| File | Used at | Length | Notes |
|---|---|---|---|
| `screen-00-anthropic-logo.mp4` | 0:00–0:04 | 4s | Anthropic wordmark on near-black, Hyperframes spring-in. Verify usage rights / fair-use for hackathon submission; if unsure, render a stylized typographic substitute that reads "Anthropic · October 2025". |
| `screen-01-skills-teaser.mp4` | 0:04–0:14 | 10s | 4 skill invocations × 2.5s. Terminal **left half**, result fills **right half** as it lands. Hard cuts on the beat. Pre-stage every result so `Enter`→bloom is under 400ms. |
| `screen-02-vskill-install.mp4` | 0:18–0:22 | 4s | Live `npx vskill install frontend-design`, full-screen terminal, install streams cleanly to ✓ |
| `screen-03-apple-watch-scroll.mp4` | 0:22–0:30 | 8s | Split-screen post camera-move: terminal 1/3 left, Chromium 2/3 right. Auto-driven scroll plays the watch-fold animation. Pre-render and replay — do not depend on a live LLM call hitting timing. |

All saved to: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/scratch/`

---

## Hyperframes animation beats

| Time | Beat | Direction |
|---|---|---|
| 00:00 | Anthropic logo spring-in | 600ms ease-out, soft chime, hold 1.4s, dissolve to black |
| 00:04 | Skill-teaser counter | Bottom-right "1 / 4 · Ableton" → "4 / 4 · Web", changes on each cut, mono font, 50% opacity |
| 00:14 | Frontmatter callout | 3 lines (name / description / instructions) bracketed yellow, 180ms each, staggered |
| 00:18 | "vskill — universal skill installer" caption | Bottom third, 800ms fade in, hold 1.5s, fade out |
| 00:21 | Camera move | 700ms ease — full-frame terminal slides to 1/3 left; right 2/3 reveals Chromium pane (no jank, motion-blurred edge) |
| 00:30 | Face-cam appears | 150ms wipe from center |
| 00:55 | Frontmatter bracket (deeper section) | Same callout style, longer hold |
| 01:08 | Tool-row X-drop | 7 tool logos in a row, red X overlays on 6, staggered 80ms. 7th (Skill Studio) pulses green |
| 01:30 | ⌘K zoom-ring | Circle overlay, 3px stroke, 40% darken outside ring |
| 01:35 | Opus row highlight | Yellow underline band, 180ms wipe right |
| 02:00 | "Real streaming. No cut." caption | Bottom third, 900ms fade in, hold 2s, fade out |
| 02:15 | `/pr-reviewer` autocomplete ring | Pulse ring, 2 beats |
| 02:48 | SSE dotted line | `stroke-dashoffset` from terminal save → Studio icon, 700ms, tagged "SSE" in the middle |
| 02:51 | Icon impact | 1.15× scale pulse + color shift (gray → brand blue-violet), 300ms spring |
| 02:53 | Toast slide-in | From top-right, spring motion, 400ms |
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
- 0:18-0:30 — Install + Apple-watch reveal: kinetic mid-tempo groove kicks in on the camera move; arpeggio mirrors the scroll-driven unfold. Bright, confident.
- 0:30-0:38 — Pull back. Warm pad, breath of space for face-cam intro.
- 0:38-1:08 — Warm piano layer, gentle strings, human and approachable. Heartbeat-tempo drum underneath.
- 1:08-1:20 — Brief tension spike, low strings, suspended chord. Unresolved.
- 1:20-2:35 — Resolved, confident mid-tempo synth-bass groove. Think "product montage". Bright but not cheesy.
- 2:35-3:13 — Build. Add arpeggiated synth. Crescendo toward a single bright chord around 3:00.
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
- [ ] **Pre-render the Apple-Watch scroll page** with frontend-design 2–3 times; pick the cleanest take. Stage replay so the live prompt-line cues a pre-rendered file (not a live LLM call) — no timing risk on judging day.
- [ ] **Verify `npx vskill install frontend-design`** writes to all three agent dirs (Claude / Cursor / Codex) and the install log is camera-friendly.
- [ ] Confirm 0708 icon-color-change + toast works in your WIP branch (72/74 tasks). If not — simulate, and note it in the description.
- [ ] Decide model-picker OpenAI/open-source strategy: live via AnyModel BYO, or staged overlay.
- [ ] Paste @trq212 tweet text to weave into 00:38–01:08 block.
- [ ] Dark mode everywhere. Close personal tabs. Disable notifications.
- [ ] Prepare a sample project folder (`~/projects/my-api`) with a clean `.claude/` dir.
- [ ] Record face-cam and screen-share separately. Mic close (6 inches). Look at the lens during face-cam.
- [ ] Upload the 3 `broll-*.mp4` files + 4 `screen-*.mp4` files to Hyperframes timeline first; build the skeleton around them.

---

## Budget

- 3 × Veo 3.1 Fast ≈ **$3.60** (cold-open clip retired)
- Suno free tier: $0
- Hyperframes: your existing license
- Total AI spend: **under $4**
