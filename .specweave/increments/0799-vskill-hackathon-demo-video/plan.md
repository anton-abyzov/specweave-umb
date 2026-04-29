# Plan — Skill Studio Hackathon Demo Video

## Architecture

### Render target
- Composition id: `HackathonDemo` (registered in `repositories/anton-abyzov/vskill-platform/src/remotion/Root.tsx`)
- Resolution: 1920×1080, 30 fps, ≤4500 frames (= 150s)
- Output: `repositories/anton-abyzov/vskill-platform/out/hackathon-demo.mp4`
- Engine: Remotion 4.0.427 (already installed in vskill-platform)

### Scene topology
The composition is a `<TransitionSeries>` of independent scene components (mirrors existing `SkillStudioDemo.tsx` pattern). Each scene is ~10–25s and consumes script + timing from a central `script.ts` module.

```
HackathonDemo (≤150s)
├── HookProblem        (12s)  — version drift / sync pain visualized
├── BrandReveal        (4s)   — "Skill Studio" logo + tagline lock
├── BrowseGrid         (15s)  — 100k+ skills, security badge, model picker
├── UpdateButton       (10s)  — toast → click → green tick (cross-machine sync)
├── AuthorCreate       (20s)  — `vskill new hi-anton` + AI-Assisted form (REUSE StudioAICreate vocabulary)
├── AuthorEvals        (12s)  — eval generation success badges
├── AuthorPublish      (15s)  — submit → verifiedskill.com → security scan PASSED
├── ConsumeInstall     (10s)  — scope picker (project/user/global), install confirmation
├── ConsumeBugSurface  (15s)  — Claude REPL: ask "2+2", reply "Hi, enter" — RED highlight
├── AuthorFix          (12s)  — split-screen edit + commit + auto-resubmit
├── ConsumeSyncUpdate  (12s)  — Studio update toast → click → 1.0.1 → re-run "Hi Anton ✓"
├── Outro              (8s)   — verifiedskill.com URL + tagline + GitHub link
└── (transitions: 12 × 15-frame fades = +6s overlap budget)
```

Total = 145s ± with transition overlap. Stretch: drop one 12s scene to land at 130s.

### Data model

**`src/remotion/scenes/hackathon/script.ts`** — single source of truth for narration + scene meta:
```ts
export type Scene = {
  id: string;
  durationFrames: number;
  voiceText: string;        // exactly what ElevenLabs will speak
  voiceStartFrame: number;  // when narration begins inside the scene
  caption?: string;         // optional on-screen pull-quote
};
export const SCRIPT: Scene[] = [ /* 12 scenes */ ];
```

The voiceover MP3 is generated **once** from the concatenated `voiceText` (with appropriate silence padding). The composition aligns its master timeline to this pre-rendered audio — scenes trigger on absolute frame offsets, not on per-scene audio chunks. This is the simplest reliable approach.

### Voice generation pipeline

Standalone Node script: `repositories/anton-abyzov/vskill-platform/scripts/generate-hackathon-voiceover.mjs`
1. Read `SCRIPT` from `src/remotion/scenes/hackathon/script.ts` (run via `tsx`).
2. Build a single SSML-ish text by concatenating `voiceText` segments with `[silence:N]` markers (ElevenLabs accepts plain text + we manage silence via `ffmpeg` post-processing).
3. POST `/v1/text-to-speech/{voice_id}` with `model_id: eleven_v3` (most expressive). Voice ID strategy: try Anton's clone (`CXBq9AgXLrBIJkfnV9hg`) first; if quality is off, fall back to `21m00Tcm4TlvDq8ikWAM` (Rachel — proven professional).
4. Save raw MP3 to `public/hackathon-demo/voiceover-raw.mp3`.
5. Run `ffmpeg` post-process: normalize loudness (`loudnorm`), pad to exactly 150s, add light reverb tail. Output: `public/hackathon-demo/voiceover.mp3`.
6. Update `script.ts` `voiceStartFrame` values from the actual silence-detection output (use `silencedetect` filter from `remotion-best-practices/rules/silence-detection.md`).

### Background music

- Source: pick from existing royalty-free instrumentals (search `repositories/anton-abyzov/vskill-platform/public/audio/` first; if empty, use a CC0 ambient loop downloaded into `public/hackathon-demo/bgm.mp3`).
- Mix: `ffmpeg -filter_complex "[1:a]volume=0.18[bgm];[0:a][bgm]amix=inputs=2:duration=longest"` — voiceover at 0 dB, BGM ducked to ~−15 dB.
- Composed in the Remotion `<Audio>` tag with `volume={0.18}` for BGM and `volume={1.0}` for voiceover.

### Reuse map (existing → new)

| Existing asset | New scene that reuses it |
|----------------|--------------------------|
| `components/TerminalFrame.tsx` | HookProblem, ConsumeBugSurface, ConsumeSyncUpdate |
| `components/BigText.tsx` | HookProblem, Outro |
| `components/AgentIcon.tsx` | BrowseGrid, AuthorCreate (model picker) |
| `components/TransitionWipe.tsx` | inter-scene transitions (where slide() isn't enough) |
| `scenes/studio/StudioIntro.tsx` | borrow brand reveal → BrandReveal |
| `scenes/studio/StudioAICreate.tsx` | AuthorCreate visual language (purple AI-Assisted, success badges) |
| `scenes/studio/StudioMultiModel.tsx` | BrowseGrid (model picker chips) |
| `constants.ts` (COLORS, FONTS) | every scene |

New scenes live under `src/remotion/scenes/hackathon/`. The existing Studio scenes are NOT modified — we cherry-pick visual idioms and create siblings.

### Highlight zooms (AC-US5-02)

Implemented via a `<ZoomHighlight>` HOC wrapping a child for N frames:
```ts
const scale = interpolate(frame, [in, in+10, out-10, out], [1, 1.25, 1.25, 1], {…});
const x = interpolate(scale, [1, 1.25], [0, -targetX*0.25]);
```
Two zooms minimum: (1) on Generate button in AuthorCreate, (2) on Update button in ConsumeSyncUpdate.

## Phasing & agent assignment

### Phase 0 — Setup (this orchestrator)
- Create + activate increment ✅
- Spawn brainstorm team (next)

### Phase 1 — Script convergence (BRAINSTORM team, 3 agents in parallel)
- `script-creative` — narrative + emotional arc lens
- `script-marketing` — conversion + value-prop lens
- `script-engineer` — technical clarity + accuracy lens
Output: 3 candidate scripts → orchestrator synthesizes the winning script into `script.ts`.

### Phase 2 — Implementation (3 agents, mostly parallel)
Upstream contracts:
- Script (`script.ts`) — produced by orchestrator after brainstorm.
- Voice MP3 (`public/hackathon-demo/voiceover.mp3`) — produced by `voice-agent` first (gates the timing).

Downstream:
- `remotion-scenes-a` — implements scenes 1–6 (Hook, Brand, Browse, Update, AuthorCreate, AuthorEvals)
- `remotion-scenes-b` — implements scenes 7–12 (AuthorPublish, ConsumeInstall, ConsumeBugSurface, AuthorFix, ConsumeSyncUpdate, Outro)
- `remotion-assembly` — wires the `HackathonDemo` composition in `Root.tsx`, integrates audio, renders, verifies. Spawns AFTER scenes-a + scenes-b complete.

Voice and scene work can proceed in parallel — Voice uses `script.ts` output only.

### Phase 3 — Render + verify (orchestrator)
- `npx remotion render HackathonDemo out/hackathon-demo.mp4` from vskill-platform
- `ffprobe` checks: duration ≤ 150s, 1920×1080, 30 fps, audio present
- Smoke-watch: open MP4, eyeball first/last 5s

### Phase 4 — Closure (sw:sw-closer subagent)
- code-review-report.json, simplify, grill, judge-llm gates
- `specweave complete 0799` updates metadata to `closed`
- Sync to GitHub (no remote configured — skip)

## File ownership

| Agent | WRITE patterns |
|-------|----------------|
| script-creative / marketing / engineer | `.specweave/increments/0799-*/reports/script-{role}.md` only |
| voice-agent | `repositories/anton-abyzov/vskill-platform/scripts/generate-hackathon-voiceover.mjs`, `public/hackathon-demo/**` |
| remotion-scenes-a | `src/remotion/scenes/hackathon/Hook*.tsx`, `Brand*.tsx`, `Browse*.tsx`, `Update*.tsx`, `Author{Create,Evals}.tsx`, `script.ts` (READ only after orchestrator writes it) |
| remotion-scenes-b | `src/remotion/scenes/hackathon/AuthorPublish.tsx`, `Consume*.tsx`, `AuthorFix.tsx`, `Outro.tsx` |
| remotion-assembly | `src/remotion/HackathonDemo.tsx`, `src/remotion/Root.tsx` (Composition entry only), `out/**` |

`constants.ts` is READ-ONLY for all agents (existing design tokens are authoritative).

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Render time blows out | Render at 1920×1080 directly, use `--concurrency 4`, accept ~5–10 min |
| ElevenLabs voice clone too inconsistent | Fall back to Rachel (`21m00Tcm4TlvDq8ikWAM`) — set in script-engineer brief |
| Audio + scene drift | Generate voice FIRST, then read its real duration via `ffprobe` and align scene timing in `script.ts` |
| Existing Studio scenes shadow new work | New work in `scenes/hackathon/` namespace; never edit `scenes/studio/*` |
| BGM not on disk | Voice agent searches public/, falls back to silent pad track if no BGM found (+flag for manual add) |
| Total > 150s | Cut UpdateButton scene first (10s), then trim BrowseGrid by 5s |

## Acceptance gates

- spec.md ACs all checked (`Edit("spec.md", "[ ]", "[x]")` per AC after verification)
- All tests in tasks.md pass
- Render exit code 0
- ffprobe duration ≤ 150s
