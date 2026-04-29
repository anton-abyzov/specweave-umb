---
status: completed
---
# Spec — Skill Studio Hackathon Demo Video

## Context

Anton recorded a 4:46 raw screen demo of Skill Studio for the Anthropic hackathon (late submission Apr 27). The raw video is too long, contains him on camera + voice, and isn't packaged for distribution. We will replace it with a Remotion-rendered 2:30 max demo: professional ElevenLabs voiceover, mirrored real-product UI, sleek transitions, captivating value proposition.

Source video: `/Users/antonabyzov/Movies/DaVinci/Hackathon Anthropic Skill Studio Full.mov` (4:46, 1920×1080@25fps).
Full transcript: `assets/source-transcript.txt` (this folder).

Existing design system (REUSE, do not rebuild): `repositories/anton-abyzov/vskill-platform/src/remotion/` — already has 22 scenes, design tokens (Geist Mono, dark + green/cyan/blue/purple), TerminalFrame, AgentIcon, BigText, TransitionWipe components, and a `studio/` folder with 7 existing scenes.

ElevenLabs: API key + Anton's cloned voice (`CXBq9AgXLrBIJkfnV9hg`) available. We can use Anton's cloned voice OR a default professional voice — choice deferred to script-brainstorm output.

## Problem

1. **Hook** — Anthropic skills are powerful but versioning + cross-machine sync is painful for both authors and consumers.
2. **Need** — Show that Skill Studio solves both flows in <2:30 with no narrator-on-camera, no off-message digression.
3. **Constraint** — Final ≤ 150 seconds (2:30). Stretch goal: 135s (2:15). 1920×1080 @ 30fps. MP4 H.264.

## User Stories

### US-1 — Submit a sleek demo video
**As** a hackathon viewer, **I want** a tight, professional demo, **so that** I understand Skill Studio's value in under 3 minutes without watching raw screen-recording.
- [x] **AC-US1-01**: Final MP4 duration is ≤ 150 seconds. *(Verified by `ffprobe`.)*
- [x] **AC-US1-02**: 1920×1080 resolution, 30 fps, H.264, AAC audio. *(Verified by `ffprobe`.)*
- [x] **AC-US1-03**: No live-action footage of Anton — 100% Remotion-rendered visuals + ElevenLabs voiceover.
- [x] **AC-US1-04**: Background music ducked under voiceover (instrumental, royalty-free or generated SFX).

### US-2 — Open with the pain point
**As** a viewer, **I want** the first 12 seconds to show why this matters, **so that** I keep watching.
- [x] **AC-US2-01**: Opening hook (0–12s) frames the version-drift / sync-pain problem with on-screen typography and visual metaphor (e.g., diverging skill versions across machines).
- [x] **AC-US2-02**: Skill Studio brand reveal lands by 0:15.

### US-3 — AUTHORING flow visualized
**As** a skill author, **I want** to see the full create→AI-generate→eval→publish loop, **so that** I understand the authoring value in one continuous beat.
- [x] **AC-US3-01**: Scene shows `vskill new <skill>` command + browser opening to Studio.
- [x] **AC-US3-02**: Scene shows AI-Assisted skill generation (description → "Hi Anton" SKILL.md) using Anthropic Skill Creator badge.
- [x] **AC-US3-03**: Scene shows eval/test generation with success badge ("Skill generated", "8 test cases created" — REUSE existing StudioAICreate visual language).
- [x] **AC-US3-04**: Scene shows version 1.0.0 → publish to verifiedskill.com → security scan PASSED.

### US-4 — CONSUMING flow visualized
**As** a skill consumer, **I want** to see install + bug + sync-update, **so that** I understand the real cross-machine pain getting solved.
- [x] **AC-US4-01**: Scene shows install at project/user/global scope chooser.
- [x] **AC-US4-02**: Scene shows running Claude → bug surfaces ("Hi, enter" instead of "Hi Anton").
- [x] **AC-US4-03**: Scene shows author side (different machine metaphor) fixing → push → re-scan → 1.0.1 published.
- [x] **AC-US4-04**: Scene shows update-available toast in Studio → one-click update → rerun shows skill working.

### US-5 — Sleek production value
**As** a viewer, **I want** the video to feel premium, **so that** the product feels worth installing.
- [x] **AC-US5-01**: Smooth transitions (fade/slide via `@remotion/transitions`) between scenes — no abrupt cuts.
- [x] **AC-US5-02**: At least 2 zoom-in highlights (e.g., on the Generate button, on the Update button) using `interpolate` scale + clip.
- [x] **AC-US5-03**: Reuses existing design tokens (`COLORS`, `FONTS` from `constants.ts`) — visual continuity with existing PromoVideo and SkillStudioDemo compositions.
- [x] **AC-US5-04**: Final outro shows `verifiedskill.com` URL + tagline.

### US-6 — Reproducible render
**As** Anton, **I want** the render to be reproducible and parametrized, **so that** I can tweak voice/script without rewriting code.
- [x] **AC-US6-01**: New composition registered in `Root.tsx` (id: `HackathonDemo`).
- [x] **AC-US6-02**: Voiceover audio stored at `public/hackathon-demo/voiceover.mp3` and loaded via `staticFile()`.
- [x] **AC-US6-03**: Script + per-scene timing externalized to a `script.ts` data module (no hardcoded copy in scene components).
- [x] **AC-US6-04**: `npx remotion render HackathonDemo out/hackathon-demo.mp4` succeeds end-to-end.

## Non-Goals

- Building a new Remotion project from scratch — we extend the existing vskill-platform composition library.
- Localization / subtitles (can be added later if Anthropic submission requires).
- Actual upload/distribution — only deliverable is the rendered MP4 + the source code.
- Replacing the existing PromoVideo/SkillStudioDemo compositions — we add a third composition, leave the others untouched.
- Custom on-screen Anton avatar/persona generation.

## Success Metrics

- Total wall-clock production time: ≤ 60 minutes from script-lock to rendered MP4.
- File size: ≤ 60 MB (sane for upload).
- Render exit code 0, ffprobe duration ≤ 150 s, no scene below 3s, no scene over 30s.
