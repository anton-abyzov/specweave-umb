# stream-to-shorts skill: livestream to fast vertical shorts

## Problem

Short clips cut from a livestream in November 2026 flopped (69 views, 0 likes on the YouTube Short) and Anton called them "really, really, really slow". The audit (`~/.specwithcode/m4/scratch/2026-11-21-shorts-factory/research/03-skills-audit.md`) found two causes in the skills themselves:

1. No installed skill covers "multi-hour livestream to many fast vertical shorts". `video-pipeline` models one video with one stage record.
2. The existing video skills apply the long-form takes rule (keep each take whole, no silence removal, 1.1x at most) to all footage. A livestream has no retakes, so the rule only keeps the dead air in.

A second run on November 21, 2026 produced 15 clips and 2 compilations with a different method. Its scripts carry hard-coded roots, account ids and one person's text, and its lessons live only in a thread report and a memory note. That run also made three mistakes worth encoding as rules: the first render left the bottom third of every frame empty, a post lookup printed a key fragment and OAuth tokens into tool output, and alternate openings were scheduled as if they were separate posts.

## Scope

In:

- A new public skill at `repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/`: `SKILL.md`, `references/`, `scripts/` with tests, `evals/evals.json`.
- One scope line in `plugins/marketing/skills/video-pipeline/SKILL.md` pointing clips cut from live streams to the new skill.
- A written proposal (report in this increment, not an edit) for `hyperframes-best-practices` 1.3.0 (installed, no committed source), the local patch in third-party `media-use`, and a "Shorts" section for the private AI Power playbook.

Out:

- Any posting, scheduling or account call. The scripts that talk to a scheduler are tested against a fake transport only.
- Installing the skill on any machine, and any edit under `~/.claude/skills` or `~/.agents/skills`. Rollout follows the merge.
- Account ids, handles, channel names, host names, thread names or one person's captions in the public repository.
- Folding the uncommitted `video-pipeline` 1.1.0 edit that sits in the main vskill checkout into this branch. It is reported as drift.

## Acceptance Criteria

- [ ] AC-01: `SKILL.md` has frontmatter `name: stream-to-shorts` (equal to its folder), a quoted SemVer `metadata.version`, `tags` nested under `metadata`, a description of at most 1,024 characters, and `npm run lint:skills-spec` passes.
- [ ] AC-02: `SKILL.md` covers the ten stages in order: intake and census (ownership search by video id, best-quality download, word-level transcript, census before any clip is framed), moment mining with a scored candidate list and what each shot proves, shorts-mode edit rules with numeric targets, layout, captions and titles and hook variants, audio, per-platform exports, checks before scheduling, scheduling, after publishing.
- [ ] AC-03: The edit rules state in plain words that they replace the takes rule for clips cut from a live stream, and that scripted recordings with retakes keep it.
- [ ] AC-04: The layout section says safe zones limit text only and names the empty-bottom reject. `scripts/fill_check.py` fails the first renders of the November 21 run (`wave1/wave1-handoff-v2/clips/`) and passes the re-rendered ones (`wave1v3/clips/`), checked locally.
- [ ] AC-05: The platform reference keeps each number's source link, tier and retrieval date from `06-platform-specs.md`, and its safe-zone text limits text only.
- [ ] AC-06: The checks reference requires an independent reviewer for the privacy scan, a transcript-against-captions comparison, a native read of translated text and an honesty check of every title against the picture, and lists what the independent check of this run caught that the maker's scan missed (or says plainly that its reports were not available).
- [ ] AC-07: Scheduling keeps routing in `social-media-posting`. The repository diff contains no account id, handle, channel name, real video id, host name or scratch path (denylist grep is empty).
- [ ] AC-08: `scripts/plan_schedule.py` output holds these properties under test: minimum spacing per account including existing posts, no rolling window over its cap, existing posts never moved, a hook variant never gets its own slot, per-account daily cap, quiet hours, time zones through `zoneinfo`.
- [ ] AC-09: The post helper prints only an allowlist of fields, redacts credential fields by key name in every path that prints or writes (lookups, error bodies, receipts), and refuses to update or delete a post that is not in this batch's receipts or not still queued. Tests use a fake transport and build fake secrets at run time.
- [ ] AC-10: The cutter port gives the same shot list, crop windows, title font size and caption events as the script that ran, on the run's example specs (checked locally against the original; only synthetic fixtures are committed).
- [ ] AC-11: `python3 -m unittest discover` over the skill's tests passes, covering cut plan, spacing and cap planner, caption word fixes and redaction. A smoke render on a generated test source runs end to end, or the report says exactly what could not be run.
- [ ] AC-12: After publishing is covered: verification of live posts, a retention log with fixed columns, and a decision rule (`scripts/retention_log.py decide`), with the rule that an alternate opening is held until the first version's 72-hour read.
- [ ] AC-13: `video-pipeline/SKILL.md` gains one scope line and a patch version bump. Nothing else in it changes.
- [ ] AC-14: The proposal report gives exact wording and location for each of the three places it cannot edit.

## Approach

Content precedence where sources disagree: this task, then the run report and the lessons memory, then the playbook's "Corrections after critique", then the playbook body, then the audit outline. Layout geometry comes from the constants in the script that ran (face y 0 to 640, title bar 640 to 760, screen 760 to 1920, caption centre y 555), not from its docstring or the playbook, which describe an earlier version.

Skill layout:

```
plugins/marketing/skills/stream-to-shorts/
  SKILL.md
  evals/evals.json
  references/  edit-rules.md  layout.md  text-and-audio.md  platform-specs.md
               checks.md  scheduling.md  retention.md  spec-format.md
  scripts/     cutplan.py  captions.py  cut_short.py  compile_wide.py
               words.py  sheet.py  fill_check.py  privacy_scan.py
               audio_check.py  music_check.py  caption_check.py
               export.py  presets.json
               plan_schedule.py  redact.py  posts.py  retention_log.py
               tests/test_*.py
```

Script contract (Python 3.9+, standard library only for anything imported at module top; optional engines are loaded lazily):

- `cutplan.py` (pure): `tight_spans`, `expand_shots`, `cover`, `zoomed`, `timeline`. Source size and layout come from arguments, defaulting to 1920x1080 and the run's layout.
- `captions.py` (pure): `apply_fixes`, `chunk_words`, `bar_font_size`, `ass_time`, `build_ass`. Translations are generic per language code.
- `cut_short.py plan|render|finish <spec.json> [--variant v] [--lang xx] --out <dir>`: ffmpeg from `--ffmpeg` or `STS_FFMPEG`, preflight for the `ass` filter, transcription command from `--transcribe-cmd` or `STS_TRANSCRIBE`, accepts any word-level JSON. Writes the master, `shots.json`, `words.json`, `metrics.json`.
- `compile_wide.py`: 16:9 compilation from the same cut specs.
- `words.py`: print transcript windows and keyword hits for the census and mining.
- `sheet.py`: contact sheet of chosen times or the default opening times (0, 0.5, 1, 2, 3 s).
- `fill_check.py <video>`: the empty-bottom reject. Exit 1 on fail.
- `privacy_scan.py <video> --out <dir> [--engine ocrmac|tesseract] [--fps 4] [--upscale 2]`: unique text lines with first time seen, risk flags as hints.
- `audio_check.py <video> [--words words.json]`: loudness, true peak, silences, speech gaps, clipped samples, words whose audio dips (cut too tight).
- `music_check.py`: tagger wrapper. A score is not a listen.
- `caption_check.py <burned-words.json> <independent-words.json>`: differences between the captions and an independent transcript of the master.
- `export.py <master> --preset P1.. --out <dir>` with `presets.json`: size-capped presets compute their bitrate.
- `plan_schedule.py <clips.json> <accounts.json> [--busy busy.json] --tz <zone> --out plan.json`: writes a plan and a calendar, never calls an API.
- `redact.py`: `redact(obj)`, `redact_text(s)`, `public_view(post)`; CLI filter on stdin.
- `posts.py --backend postiz|blotato state|show|upload|create|update|delete`: base URL and credentials from environment or an env file, injected transport, dry run unless `--go`, receipts ledger, own-and-queued guard, allowlist output.
- `retention_log.py init|decide`.

Order of work: spec, parallel build against this contract (cutter, scheduling helpers, check helpers, references), `SKILL.md` and evals, integration and local equivalence and fill checks, review, denylist grep, PR.

Rejected alternatives:

- A "shorts mode" inside `video-pipeline`: it models one video with one stage record and gates before graphics; a stream factory is one source with many clips, each with its own state.
- Shipping the run's scripts as they are: they carry a scratch root, a real scheduler host, account ids and captions.
- A posting helper with a routing table: account ids do not belong in a public skill, and `social-media-posting` already owns routing.
- A Pillow caption fallback for ffmpeg builds without libass: the run used libass; the cutter preflights and names where to get a build that has it.

Risks:

- The scheduler helpers cannot be exercised against a live service in this increment. They are a port of calls that ran on November 21, 2026, tested against a fake transport, and the skill says so.
- `fill_check.py` is a heuristic. It is validated on this run's bad and fixed renders and stays a hint next to the contact sheet.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: The skill lives in the public `marketing` plugin with generic fixture names; Anton's channels, voice and cadence go to the private playbook proposal → default (the audit's recommendation).
- D-02: A hook variant gets no slot until the base clip's 72-hour read releases it, and then only on accounts where the base did not run → default (lessons memory; the run scheduled variants as posts, which the lesson reverses).
- D-03: Rolling post caps are parameters of the accounts file, not constants, because the sources disagree on whether the scheduler plan's cap counts posts or accounts → default.
- D-04: `video-pipeline` goes from 1.0.0 to 1.0.1 for the scope line; the uncommitted 1.1.0 edit in the main checkout is reported, not folded in → default.
- D-05: The increment is created without a commit in the umbrella checkout, which sits on another thread's branch with unrelated changes → default.

### Open
- none

## Tasks

### T-01 Cutter and captions port with equivalence check
- AC: AC-10, AC-11 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/cutplan.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/captions.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/cut_short.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/compile_wide.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/words.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/sheet.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_cutplan.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_captions.py | Test: python3 -m unittest discover -s plugins/marketing/skills/stream-to-shorts/scripts/tests -p "test_c*.py"

### T-02 Schedule planner, redaction, post helper and retention log
- AC: AC-08, AC-09, AC-12, AC-11 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/plan_schedule.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/redact.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/posts.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/retention_log.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_plan_schedule.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_redact.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_posts.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_retention_log.py | Test: python3 -m unittest discover -s plugins/marketing/skills/stream-to-shorts/scripts/tests -p "test_[pr]*.py"

### T-03 Check helpers and exports
- AC: AC-04, AC-06, AC-11 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/fill_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/privacy_scan.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/audio_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/music_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/caption_check.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/export.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/presets.json, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_checks.py, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_export.py | Test: python3 -m unittest discover -s plugins/marketing/skills/stream-to-shorts/scripts/tests -p "test_[ce][hx]*.py"

### T-04 References
- AC: AC-03, AC-04, AC-05, AC-06, AC-07, AC-12 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/edit-rules.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/layout.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/text-and-audio.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/platform-specs.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/checks.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/scheduling.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/retention.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/references/spec-format.md | Test: grep -c "retrieved" plugins/marketing/skills/stream-to-shorts/references/platform-specs.md

### T-05 SKILL.md, evals and the video-pipeline scope line
- AC: AC-01, AC-02, AC-03, AC-13 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/SKILL.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/evals/evals.json, repositories/anton-abyzov/vskill/plugins/marketing/skills/video-pipeline/SKILL.md | Test: npm run lint:skills-spec

### T-06 Integration: full tests, smoke render, fill check on the run's renders, denylist grep
- AC: AC-04, AC-07, AC-10, AC-11 | Files: repositories/anton-abyzov/vskill/plugins/marketing/skills/stream-to-shorts/scripts/tests/test_smoke.py | Test: python3 -m unittest discover -s plugins/marketing/skills/stream-to-shorts/scripts/tests

### T-07 Proposal for the three places outside this repository, and the pull request
- AC: AC-14 | Files: .specweave/increments/1439-stream-to-shorts-skill-livestream-to-fast-vertical-shorts/reports/proposal-takes-rule-scope.md | Test: test -s .specweave/increments/1439-stream-to-shorts-skill-livestream-to-fast-vertical-shorts/reports/proposal-takes-rule-scope.md
