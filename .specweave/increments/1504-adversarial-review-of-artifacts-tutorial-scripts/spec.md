# Adversarial review of artifacts tutorial scripts

## Problem

Seven short vertical tutorial scripts (V1 to V7) for SpecWithCode artifacts features, written by Claude Opus 5.5, need a hostile cross-model review before voice recording, rendering or posting. The source text lives at `/Users/anton/.specwithcode/m4/scratch/2026-11-27-artifacts-tutorials/scripts/scripts-v1.md`, with the review at `/Users/anton/.specwithcode/m4/scratch/2026-11-27-artifacts-tutorials/scripts/review-muse-r1.md`.

## Scope

In: hook, clarity, claim accuracy against the released 1.0.448 capture proof, pacing at 2.6 words per second, series order, verbatim replacement lines, two alternative hooks and a short title per video, recorded with `specweave review --record`. Out: editing the scripts, capturing, rendering, posting.

## Acceptance Criteria

- [x] AC-01: Report in sw-review shape (second line `Verdict: fix first`) covering V1 to V7 on all five lenses in Scope.
- [x] AC-02: Recorded via `specweave review --record` with `--model muse-wonder-full-1.0` and the reviewed head.

## Approach

Read the whole scripts file, check every claim against the capture proof in the review brief, write the report, run SpecWeave 3.1.23 from `repositories/anton-abyzov/specweave` (installed 3.1.22 lacks `--record`) and record it. Created only to hold the recorded review; closure stays with the marketing work's owner.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- Record against umbrella HEAD `fb8fbc904218b9c7a4e6152c8e88f583b1a2872f`; the scripts file itself is untracked outside Git.
### Open
- none

## Tasks

### T-01 Adversarial review of scripts v1, recorded
- AC: AC-01, AC-02 | Files: reports/reviews/review-muse-wonder-full-1.0-1.md | Test: specweave review 1504 --record reports (recorded, verdict fix first)
