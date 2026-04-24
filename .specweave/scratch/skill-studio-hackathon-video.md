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

### 00:00 — 00:08 · COLD-OPEN (Hollywood style, no face)

`[B-ROLL — broll-01-cold-open.mp4]`

Dim dev office at night. Monitor glow. Pull-in on a blinking cursor. Seven translucent tool logos (Claude, Cursor, Codex, ChatGPT, VS Code, Copilot, Gemini) appear around the monitor, each tethered by a fragile blue-light thread to a single glowing SKILL.md badge. The threads pulse. Badge flares white. All seven logos ignite in unison. Teal/amber grade. Rising sub-bass + synth pulse.

`[VOICEOVER — Anton, over clip]`
> *"Every AI tool you use — is about to know the same skill. Not because they talked to each other. Because you wrote it **once**."*

---

### 00:08 — 00:18 · HOOK PAYOFF

`[FACE — tight, solid background]`
> *"I built this in a week for Anthropic's hackathon. Three minutes — I'll show you what it does, why it matters, and why Claude Code alone can't ship this without **you** in the loop."*

*(Beat. Smile. Cut.)*

---

### 00:18 — 00:28 · WHAT IS A SKILL? (the hands montage)

`[B-ROLL — broll-02-hands-montage.mp4]`

Four 2-second vignettes: child's hands at a laptop, chef's hands folding dough, scientist's gloved hands at a microscope, elderly musician's hands on piano keys. The glowing SKILL.md badge materializes with a soft chime in each scene.

`[VOICEOVER — over clip]`
> *"A skill is the smallest unit of know-how. A checklist. A playbook. What a senior teaches a junior on day one. Your grandma's recipe for pierogi is a skill."*

---

### 00:28 — 00:55 · THE TECHNICAL BIT (keep accessible)

`[SCREEN — code.claude.com/docs/en/skills, zoom to 'Create a SKILL.md file' box]`

`[FACE — 30% corner]`
> *"Anthropic turned that idea into one file. A `SKILL.md`. Name. Description. Markdown instructions. That's it. Claude reads it when it's relevant — or you call it with a slash. No code required."*

`[ANIM — Hyperframes bracket-callout on three frontmatter lines: name, description, allowed-tools]`

> *"A kid can write one. An AI **cannot** write a great one without you — because the taste, the judgment, the 'we always do it this way' — that part is yours."*

**[OPTIONAL — if @trq212 tweet text is pasted in: weave a 1-line quote here as counterpoint or reinforcement]**

---

### 00:55 — 01:05 · THE PROBLEM (the lock-in break)

`[B-ROLL — broll-03-lockin-break.mp4]`

Seven tool logos floating, each padlocked to a dim SKILL.md with a thick red chain. A bright SKILL.md badge flies in, strikes the center, all chains shatter in slow-mo. Logos pulse in unison. Mood: liberating.

`[VOICEOVER — over clip]`
> *"Here's the catch. You wrote the skill for Claude. Cool. Switch to Cursor. Codex. Windsurf. Copilot. Fifty-three tools. Each one wants a different format — so you write it five times, or you stay locked in. **That's what Skill Studio fixes.** Watch."*

---

### 01:05 — 01:55 · LIVE DEMO — GENERATE

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

### 01:55 — 02:30 · USE IT IN A PROJECT

`[SCREEN — terminal: `cd ~/projects/my-api && ls .claude/skills/` — the new `pr-reviewer/` directory is there]`

> *"Skill Studio dropped the file into my project. No npm install, no registry dance. It's on disk."*

`[SCREEN — open Claude Code in the same folder, type `/pr-reviewer`]`

`[ANIM — zoom on the slash-command autocomplete]`

> *"Claude Code picks it up. Live. Same skill — I could point Codex or Cursor at the same folder and it'd work there too. That's the 'universal' part."*

---

### 02:30 — 02:38 · PREVIEW THE MAGIC (cinematic, no face)

`[B-ROLL — broll-04-sse-magic.mp4]`

Split screen. A keystroke in the terminal launches a comet of light across the gap; it strikes a dashboard icon, which pulses and shifts color. Toast slides in from the top-right. Mood: instant, magical.

`[VOICEOVER — over clip]`
> *"Okay — this is the part I'm most proud of."*

---

### 02:38 — 03:10 · THE MAGIC — LIVE

`[SCREEN — Skill Studio on left, terminal on right. Skill icon in Studio is neutral gray.]`

`[SCREEN — in terminal, edit `pr-reviewer/SKILL.md`, change a line, save.]`

`[SCREEN — within a second, the Studio icon pulses and shifts color. Toast: "Skill updated — v1.0.1 → v1.0.2".]`

`[ANIM — Hyperframes overlay: dotted line from file-save to icon, labeled "SSE"]`

> *"Server-Sent Events. Push, not poll. My file system told the Cloudflare hub, the hub told Studio, Studio told me. One second, end to end."*

`[SCREEN — click the toast. Diff view opens, line-by-line.]`

> *"And I get the **diff** — not 'something changed', exactly what changed. Because when skills are live infrastructure, knowing what changed matters as much as knowing that it changed."*

---

### 03:10 — 03:30 · CLOSE

`[FACE — full frame]`
> *"A skill is a recipe. Skill Studio writes it, ships it to every tool you use, and tells you the instant someone improves it. Anthropic gave us the standard. I'm making it **universal** and **live**."*

`[ANIM — end card: verified-skill.com, Anton's GitHub, "Built for the Anthropic hackathon, April 2026"]`

> *"Link's below. Fork it. Break it. Ship me a skill."*

---

## B-roll inventory (all 8s, Veo 3.1 Fast, 16:9)

| File | Used at | Mood |
|---|---|---|
| `broll-01-cold-open.mp4` | 0:00 | Hollywood cold-open, tense-to-promising |
| `broll-02-hands-montage.mp4` | 0:18 | Warm, human, cinematic |
| `broll-03-lockin-break.mp4` | 0:55 | Tension → release |
| `broll-04-sse-magic.mp4` | 2:30 | Magical, instant, satisfying |

All saved to: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/scratch/`

---

## Hyperframes animation beats

| Time | Beat | Direction |
|---|---|---|
| 00:08 | Face-cam appears | 150ms wipe from center |
| 00:34 | Frontmatter bracket | 3 lines of the SKILL.md YAML get a yellow bracket that slides in from the left, 200ms each, staggered |
| 00:55 | Tool-row X-drop | 7 tool logos in a row, red X overlays appear on 6, staggered 80ms. 7th (Skill Studio) pulses green |
| 01:15 | ⌘K zoom-ring | Circle overlay, 3px stroke, 40% darken outside ring. Hyperframes `<ZoomIn>` |
| 01:20 | Opus row highlight | Yellow underline band, 180ms wipe right |
| 01:45 | "Real streaming. No cut." caption | Bottom third, 900ms fade in, hold 2s, fade out |
| 02:10 | `/pr-reviewer` autocomplete ring | Pulse ring, 2 beats |
| 02:45 | SSE dotted line | `stroke-dashoffset` animation from terminal save point to Studio icon, 700ms, tagged "SSE" in the middle |
| 02:48 | Icon impact | 1.15× scale pulse + color shift (gray → brand blue-violet), 300ms spring |
| 02:50 | Toast slide-in | From top-right, spring motion, 400ms |
| 03:20 | End card | Full-bleed brand color. Logo spring-in 200ms, URL fade 200ms later, credit fade 300ms later. Hold 3s |

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
- 0:00-0:18 — Deep sub-bass hum, sparse synth plucks, single rising pulse every 4 seconds. Minimal, anticipatory.
- 0:18-0:55 — Warm piano layer joins, gentle strings, human and approachable. Heartbeat-tempo drum underneath.
- 0:55-1:05 — Brief tension spike, low strings, suspended chord. Unresolved.
- 1:05-2:30 — Resolved, confident mid-tempo synth-bass groove. Think "product montage". Bright but not cheesy.
- 2:30-3:10 — Build. Add arpeggiated synth. Crescendo toward a single bright chord at 3:00.
- 3:10-3:30 — Outro. Warm resolve. One final soft chime. Silence-adjacent by end.
Instruments: analog synth pad, piano, light strings, sub-bass, minimal percussion (no snares).
No vocals. No lyrics. Instrumental only.
BPM: 92, feels like 100.
Reference vibes: Hans Zimmer's "Time" with lighter drums, 65daysofstatic's quieter work, Apple keynote background music.
```

Generate 2-3 takes, pick the one with the clearest 2:30 build-up — that's where your SSE reveal drops.

---

## Pre-recording checklist

- [ ] Confirm 0708 icon-color-change + toast works in your WIP branch (72/74 tasks). If not — simulate, and note it in the description.
- [ ] Decide model-picker OpenAI/open-source strategy: live via AnyModel BYO, or staged overlay.
- [ ] Paste @trq212 tweet text to weave into 00:28–00:55 block.
- [ ] Dark mode everywhere. Close personal tabs. Disable notifications.
- [ ] Prepare a sample project folder (`~/projects/my-api`) with a clean `.claude/` dir.
- [ ] Record face-cam and screen-share separately. Mic close (6 inches). Look at the lens during face-cam.
- [ ] Upload the 4 `broll-*.mp4` files to Hyperframes timeline first; build the skeleton around them.

---

## Budget

- 4 × Veo 3.1 Fast ≈ **$4.80**
- Suno free tier: $0
- Hyperframes: your existing license
- Total AI spend: **under $5**
