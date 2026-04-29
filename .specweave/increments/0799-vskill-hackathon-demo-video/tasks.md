# Tasks — Skill Studio Hackathon Demo Video

> Each task names its owning agent, the spec ACs it satisfies, and a Given/When/Then test plan.

---

### T-001: Lock the script
**Owner**: orchestrator | **AC**: AC-US2-01, AC-US3-01..04, AC-US4-01..04 | **Status**: [x] completed
**Given** three brainstorm-produced candidate scripts exist in `reports/script-*.md`
**When** the orchestrator synthesizes a winning script obeying the 150s budget
**Then** `src/remotion/scenes/hackathon/script.ts` is written with `SCRIPT: Scene[]` covering all 12 scenes, total `durationFrames` ≤ 4500 (150s @ 30fps), and `voiceText` strings concatenate to ≤ 350 spoken words

---

### T-002: Generate ElevenLabs voiceover
**Owner**: voice-agent | **AC**: AC-US1-04, AC-US6-02 | **Status**: [x] completed
**Test**:
**Given** `script.ts` exists with the locked narration
**When** `node scripts/generate-hackathon-voiceover.mjs` runs against ElevenLabs `eleven_v3` model
**Then** `public/hackathon-demo/voiceover.mp3` exists, ffprobe duration is between 130s and 150s, peak loudness is between −16 and −14 LUFS, and a backup raw file is saved at `voiceover-raw.mp3`

---

### T-003: Provide background music track
**Owner**: voice-agent | **AC**: AC-US1-04 | **Status**: [x] completed
**Test**:
**Given** voiceover.mp3 exists
**When** voice-agent searches `public/audio/` and either copies an existing instrumental loop or downloads a CC0 ambient track
**Then** `public/hackathon-demo/bgm.mp3` exists at ~150s, ducked to roughly −15 dB relative to voiceover (verified by `ffmpeg -af volumedetect`)

---

### T-004: Build scenes 1–6 (Hook, Brand, Browse, Update, AuthorCreate, AuthorEvals)
**Owner**: remotion-scenes-a | **AC**: AC-US2-01, AC-US2-02, AC-US3-01..03, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test**:
**Given** `script.ts` is locked with timing for these 6 scenes
**When** scenes-a writes `Hook.tsx`, `Brand.tsx`, `Browse.tsx`, `Update.tsx`, `AuthorCreate.tsx`, `AuthorEvals.tsx` under `scenes/hackathon/` and exports them
**Then** each scene component renders without runtime error in `npx remotion studio`, uses `COLORS`/`FONTS` from `constants.ts`, and AuthorCreate contains a `<ZoomHighlight>` on the Generate button per AC-US5-02

---

### T-005: Build scenes 7–12 (AuthorPublish, ConsumeInstall, BugSurface, AuthorFix, SyncUpdate, Outro)
**Owner**: remotion-scenes-b | **AC**: AC-US3-04, AC-US4-01..04, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**Test**:
**Given** `script.ts` is locked
**When** scenes-b writes `AuthorPublish.tsx`, `ConsumeInstall.tsx`, `ConsumeBugSurface.tsx`, `AuthorFix.tsx`, `ConsumeSyncUpdate.tsx`, `Outro.tsx`
**Then** scenes render in studio, Outro contains `verifiedskill.com` text, ConsumeSyncUpdate contains a `<ZoomHighlight>` on the Update button, all use existing design tokens

---

### T-006: Wire HackathonDemo composition + audio + register in Root
**Owner**: remotion-assembly | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US5-01, AC-US6-01, AC-US6-03 | **Status**: [x] completed
**Test**:
**Given** all 12 scene components exist and voiceover.mp3 + bgm.mp3 are in `public/hackathon-demo/`
**When** assembly creates `HackathonDemo.tsx` with `<TransitionSeries>` + scene `<Audio>` tags + bgm overlay, and registers it in `Root.tsx` with id `HackathonDemo`, durationInFrames = sum of scene durations
**Then** `npx remotion render HackathonDemo /tmp/hackathon-test.mp4 --frames=0-30` produces a non-empty 30-frame MP4 with audio

---

### T-007: Full render at 1920×1080@30fps
**Owner**: remotion-assembly | **AC**: AC-US1-01, AC-US1-02, AC-US6-04 | **Status**: [x] completed
**Test**:
**Given** smoke render passed
**When** `npx remotion render HackathonDemo out/hackathon-demo.mp4` runs to completion
**Then** `out/hackathon-demo.mp4` exists, `ffprobe` reports duration ≤ 150s, width=1920, height=1080, fps=30, codec=h264, audio codec=aac

---

### T-008: Final verification + smoke watch
**Owner**: orchestrator | **AC**: AC-US1-01, AC-US1-04, AC-US5-01 | **Status**: [x] completed
**Test**:
**Given** the rendered MP4
**When** orchestrator runs `ffprobe` checks + extracts first/last 1s frames as PNG previews
**Then** all spec ACs are checked off in spec.md, file size is ≤ 60 MB, and preview frames show non-blank content with brand reveal in the first 4s and verifiedskill.com in the last 4s
