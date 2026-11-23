---
title: "Round 1 verification"
thread: "thread:delegated-task:command%3Amcp%3A376a3928-db98-4e7d-b629-58c24dc3364f%3Adelegate-task%3A1441-neon-review-round-2"
threadTitle: "Ultracode on track rows review"
increment: "1441-ultracode-on-model-track-rows-so-threads-started-on-a-track-run-with-it"
savedAt: "2026-11-23T06:16:12.728Z"
---

**Verdict: ship** (approve — 0 critical, 0 high, 0 medium; 1 remaining low UI finding)

- **Reviewed commit:** `41b9d765cc7ea1c5476aba240e0777bc02d2d6c3` (`1441-ultracode-track-rows`, PR `anton-abyzov/specwithcode#821`, diff `f4c0898fe..41b9d765c` + full branch vs `origin/main`)
- **Report updated:** `/Users/anton/Projects/github/specweave-umb/.specweave/increments/1441-ultracode-on-model-track-rows-so-threads-started-on-a-track-run-with-it/reports/review-gemini-4-neon.md`

### Round 1 verification
1. **`[high]` `modelLanes.ts` moved branch (`withRunnableTrackUltracode`) — Verified fixed.** `packages/shared/src/modelLanes.ts:577-584` strips `ultracode: true` via `withRunnableTrackUltracode` (`packages/shared/src/modelTracks.ts:435-442`) using canonical `model?.slug ?? chosen.model`; `laneEntryUnavailable` (`modelLanes.ts:322-325`) already excludes unloaded/empty `provider.models`. Covered in `modelLanes.test.ts` and `TracksLaunch.test.ts:245-252`.
2. **`[high]` `remoteLaunchModel.ts:150-152` unmoved remote launches — Verified fixed.** Now returns `decision.selection` when `!decision.moved`. Remote arrival is safe: `translateModel` forwards options only to a matching-driver provider listing the model, `ThreadMessageIntake.launchThread` does not reject extra options, and `apps/server/src/claudeModelOptions.ts:219` gates emitted CLI settings on `supportsBoolean("ultracode")`.
3. **`[high]` `ws.ts:1462` & `TracksLaunch.ts:82-85` (`seededFromTrack`) — Verified fixed.** One-model projects return `kept` at `TracksLaunch.ts:77-81` before stripping; explicit composer picks and `TraitsPicker` toggles set `modelSelectionExplicit: true` (`composerDraftStore.ts:3336`), so `sendModelUnnamed` is `false`. Covered in `TracksLaunch.test.ts:215-243`.
4. **`[medium]` `ModelTracksSettings.tsx:309-318, 667` (`TrackUltracodeToggle`) — Verified fixed.** Checks `props.sources` entries matching `selection.instanceId` against `source.slug`.
5. **`[medium]` `ProjectModelsPopover.tsx:255` (#5b) — Verified fixed** (`hasBoolean(trackEntry, track.model, "ultracode")`).
6. **`[medium]` `firstDailyTrackEntry` ignoring `provider.enabled` (#5a) — Declined (accepted).** Confirmed against `origin/main` that `firstDailyTrackEntry` extracted `projectDraftModelSelection`'s pre-existing `listed` predicate verbatim.

### Remaining finding (non-blocking)
- **`[low]` `apps/web/src/components/settings/ModelTracksSettings.tsx:634,665` — 390px narrow-viewport overlap.** Inspecting `/Users/anton/Projects/github/specweave-umb/.specweave/increments/1441-ultracode-on-model-track-rows-so-threads-started-on-a-track-run-with-it/reports/tracks-ultracode-dark-390.png` contradicts the claim that adding `</>` did not introduce the overlap: on Daily row 2 (`GPT-6.1 Sol`, no `</>`), `then GitHub Copilot Enterprise Ready` fits cleanly beside `Medium`, whereas on Daily row 1 (`Claude Opus 5.5`), adding `<TrackUltracodeToggle>` inside the non-wrapping `SortableRow` flex row (`line 408`) narrows `<div className="min-w-0 flex-1">` (`line 579`) so the unwrapping source `<li className="flex items-center gap-1">` (`line 634`) overflows and its `Ready` badge collides directly with `</>`. Fix: add `flex-wrap min-w-0` to the `<li>` at line 634.

### Other checks & ledger note
- Audited all `routeWorkerTask` / `resolveLaneRouting` callers (`OrchestratorMcpService.ts:2349`, `handlers.ts:815-820`, `TracksLaunch.ts:125-133`, `remoteLaunchModel.ts:150-152`) for identity checks (`decision.selection === baseline`): safe because `withTrackEntryUltracode` allocates a new object when adding `ultracode: true`.
- **On M5:** `/Users/anton/.specwithcode/commands/specweave` is version `3.1.22` (no `--record` flag), so `specweave review --record` exited with `error: unknown option '--record'`. Record `/Users/anton/Projects/github/specweave-umb/.specweave/increments/1441-ultracode-on-model-track-rows-so-threads-started-on-a-track-run-with-it/reports/review-gemini-4-neon.md` against `--model gemini-4-neon --head 41b9d765cc7ea1c5476aba240e0777bc02d2d6c3` using a SpecWeave build that includes `--record`.
