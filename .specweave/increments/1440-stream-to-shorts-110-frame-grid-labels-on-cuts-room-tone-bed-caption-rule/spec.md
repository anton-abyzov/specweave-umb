# stream-to-shorts 1.1.0: frame grid, labels on cuts, room-tone bed, caption rule

## Problem

`stream-to-shorts` 1.0.0 merged on November 21, 2026 (vskill PR #241, increment 1439). The fix rounds on that night's batch of clips showed four things the skill gets wrong or does not say.

1. A caption was changed on the word of a second transcript. Of 39 caption changes made after the independent check, 3 were wrong: two were the second transcript mishearing (a product name heard as a number, "assistant" as "system"), and one was made on a transcript that ran across the join between two clips of a compilation. The skill says "every difference is either a fix or a note".
2. Stream audio that passed through a noise gate has digital silence in every pause. The skill says to lay room tone from the same recording, and such a recording has none. The cutter has no way to fill the pauses.
3. The cutter renders each shot with `-t <seconds>` at 30 frames a second and joins shots with the concat filter. A shot whose length is not a whole number of frames gets a picture longer than its sound, and the filter pads the sound with silence. Measured on a four-segment fixture with the merged code: 162 frames rendered, and silent runs of 1,537, 1,058, 498 and 498 samples at the joins. Every cut after the first drifts off the planned time, so a label timed from the plan sits a few frames off its cut.
4. A media swap on a queued post was treated as done when the scheduler answered 201. Nothing compared the file the scheduler holds with the final master.

Also open from 1439: vskill has no changelog line or plugin version for the new skill.

## Scope

In:

- `repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/`: cutter, captions, wide compiler, audio and caption checks, their tests, the references, `SKILL.md` (version 1.1.0) and evals.
- `repositories/anton-abyzov/vskill/CHANGELOG.md`, `plugins/marketing/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: an Unreleased line and marketing plugin 1.7.0.

Out:

- Any posting, scheduling or account call.
- `hyperframes-best-practices`, `media-use` and the private playbook. The proposal in 1439 stays a proposal.
- A vskill CLI release.

## Acceptance Criteria

- [ ] AC-01: Every shot from `cutplan.expand_shots` carries `frames`, a whole number of output frames at 30 a second. A span is rounded down, never past its end or into a dropped range, and loses under one frame. A segment that starts where the one before it ended, on the same picture and sound, starts where that one really ended.
- [ ] AC-02: A render of a fixture with segment lengths between frames and two speeds gives a base cut with exactly the planned number of frames and exactly 1,600 samples a frame, and the picture jumps on the planned frames only.
- [ ] AC-03: A label starts on the frame of the cut nearest to its typed start and ends on the frame of a later cut. In the rendered master the label is on every frame of its shot and on none before or after. `metrics.json` lists where each label landed.
- [ ] AC-04: A spec `bed` between -80 and -40 dBFS lays noise at that level under the clip, before the limiter. On a fixture with gated pauses the master has no dropout with the bed and at least three without it, and its quietest fifth of 50 ms windows lies between -58 and -52 dBFS for a bed of -55.
- [ ] AC-05: `audio_check.py` marks a pause over 0.35 s CHECK and over 0.5 s WARN. The docs give 0.3 s as the cut and 0.35 s as the cap.
- [ ] AC-06: `caption_check.py` prints that a difference is a question, not a fix. With `--shots` it prints the source key and time of each difference and marks one within 0.5 s of a jump in the sound.
- [ ] AC-07: `references/checks.md`, `references/text-and-audio.md` and `SKILL.md` state the caption rule: change only on a transcript of the source with sentence context where two models agree; never on an isolated half-second or across an edit point; on an even split caption the reading that fits the picture, record it as a judgment and keep the source excerpt.
- [ ] AC-08: `references/checks.md` and `references/scheduling.md` require, after any media swap, a hash comparison between the file each scheduler holds and the final master.
- [ ] AC-09: The skill's tests pass on Python 3.9 and 3.12, the skills lint passes, and the diff against `main` has no personal path, handle or host.
- [ ] AC-10: `SKILL.md` is version 1.1.0, the marketing plugin is 1.7.0 in both manifests, and the changelog has an Unreleased line for the skill.
- [ ] AC-11: A shot from a source at 24, 25, 29.97 or 60 frames a second, and a slowed shot, render exactly their planned frames and 1,600 samples a frame. A clean render prints no WARN, `duration_s` equals `planned_s`, and the master's sound is fading out at its last frame, in the cutter and in the wide compilation. A shot that reads past the end of its source gets a WARN.
- [ ] AC-13: Every shot shows its own source frames: none dropped or held in place of the next, at a cut or at the end of the source, in the stack and full layouts, with `g_in`, at speeds 0.25 and 0.5, and in the wide compilation. A shot that starts past the end of its source stops the run before any encode. Segment numbers (`a_in`, `g_in`, `vol`, `z`, `punch`, `gap`, `face_dy`, `gate`) are checked in the spec, and `g_in` on a `full` segment is refused.
- [ ] AC-14: A cut that measures above 0 LUFS renders with a WARN and a true peak at or under -0.5 dBTP. Nothing read past a shot's `out` is heard, however short the shot. A read that starts within 0.1 s of its source's end stops the run. A negative `in`, a `max_zoom` or top-level `punch` that is not above 0 are refused.
- [ ] AC-12: Shots are split by their length on screen. A bad `labels` entry, a `shot` that is not above 0 and a non-finite `speed` are refused before anything is rendered. A label typed past the end of the cut is left out and reported. `caption_check.py --shots` exits 2 on a malformed shot list. `metrics.json` names the label text that was burned.

## Approach

1. `cutplan.py`: `FPS` and `AUDIO_RATE`. `expand_shots` counts each span in whole output frames (rounded down), splits it on frame boundaries, and carries a contiguous span's start from the real end of the one before. `timeline` counts in frames. `shot_audio_filter` pads or trims each shot's sound to its frame count. `cut_frames` and `snap_label` place labels.
2. `cut_short.py`: `-frames:v` per shot; `bed` validation, `bed_gain` (measured with `volumedetect`, since noise sources differ by build) and `audio_args`; `label_report`, `planned_s` and a warning when the cut and the plan differ.
3. `captions.py`: `cut_time` writes an ASS time for a cut frame (the last hundredth before the frame's time, so the event is never a frame late); `placed_labels`; `build_ass(shots=...)`.
4. `compile_wide.py`: the same frame limit, moment marks on cut times, a bed when a spec has one.
5. `audio_check.py`: pause cap 0.35 s. `caption_check.py`: the note, `--shots`.
6. Docs, evals, version, changelog, plugin manifests.

7. After the first review: the picture of every shot is put on the 30-frame grid, its last frame is held and the frame count cuts it (`cutplan.shot_grid`), because a cap alone ends a 24-frame source or a slowed shot one or two frames early and the encoder then ends the sound with it. After the second review the grid moved ahead of crop and scale on every picture input: behind `scale` the last real frame of each shot was dropped and the one before it held. Each input is read half a second past its shot (`cutplan.read_length`); a speed outside 0.5 to 100 is retimed in `atempo` steps. The length of a base cut is its counted frames over 30, not the container's duration, and intermediates carry no B-frames.

Rejected: rounding spans to the nearest frame (can grow into a dropped range); a default bed (wrong for a recording that has its own room tone); stopping a render whose label sits past the end of a shorter variant (the label is left out with a note instead).

Risk: the shot list of an existing spec changes by under one frame a span, so the equivalence script from 1439 no longer prints `ALL EQUAL`. That is the point of the change.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 `bed` is off unless the spec sets it.
- D-02 A label's typed times choose the shot; the cutter always moves it onto cuts.
- D-03 Pause cap 0.35 s is the CHECK line in `audio_check.py`; the cut still leaves 0.3 s.

### Open
- none

## Tasks

### T-01 Frame grid in the plan, the render and the wide compiler
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/cutplan.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/cut_short.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/compile_wide.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_cutplan.py | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest tests.test_grid.FrameGrid tests.test_cutplan

### T-02 Labels on cuts
- AC: AC-03 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/captions.py | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest tests.test_grid.LabelsOnCuts

### T-03 Room-tone bed and pause cap
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/audio_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_checks.py | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest tests.test_grid.Bed tests.test_grid.PausesAndRoomTone tests.test_checks

### T-04 Caption differences: the note and the source place
- AC: AC-06 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/caption_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_grid.py | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest tests.test_grid.CaptionDifferencesInTheSource

### T-05 Render test
- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_smoke.py | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest tests.test_smoke

### T-07 Review fixes: exact frames at any source rate, input checks, doc mismatches
- AC: AC-11, AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/cutplan.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/cut_short.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/compile_wide.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/captions.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/caption_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_grid.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_smoke.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_spec.py | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest tests.test_grid tests.test_smoke tests.test_spec

### T-06 References, SKILL.md, evals, version, changelog and manifests
- AC: AC-07, AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/SKILL.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/checks.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/text-and-audio.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/edit-rules.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/spec-format.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/scheduling.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/evals/evals.json, repositories/anton-abyzov/vskill/CHANGELOG.md, repositories/anton-abyzov/vskill/plugins/marketing/.claude-plugin/plugin.json, repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json | Test: cd repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts && python3 -B -m unittest discover -s tests -t .
