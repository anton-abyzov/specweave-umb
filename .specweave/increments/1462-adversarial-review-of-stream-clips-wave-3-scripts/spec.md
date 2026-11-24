# Adversarial review of stream clips wave 3 scripts

## Problem

Five short-video scripts (wave 3, P1 to P5) cut from Anton's livestreams were written by Claude Fable 5.2 and need a hostile cross-model review before anything is rendered or posted. The source text lives at `/Users/anton/.specwithcode/m4/scratch/2026-11-24-stream-clips/review/scripts-v1.md` (copy: `.specweave/reports/threads/wave3-stream-clips-scripts-v1.md`).

## Scope

In: verdict per video (SHIP, FIX with exact wording, KILL), findings checked against the word-timed transcripts, recorded with `specweave review --record`. Out: editing the scripts, rendering, posting.

## Acceptance Criteria

- [x] AC-01: Report in sw-review shape (second line `Verdict: fix first`), under 700 words, answering the seven questions in the scripts file.
- [x] AC-02: Recorded via `specweave review --record` with `--model muse-wonder-full-1.0` and the reviewed head.

## Approach

Read the whole scripts file, verify joined quotes in `work/pain.json` (+820 s) and `work/chrome.json`, write the report, build SpecWeave 3.1.23 from `repositories/anton-abyzov/specweave` (installed 3.1.22 lacks `--record`) and record it. Created only to hold the recorded review; closure stays with the marketing work's owner.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- Record against umbrella HEAD `66cf93ad16cb67a183f51c37afd34331c9ae42c2`; the scripts file itself is untracked outside Git.
### Open
- none

## Tasks

### T-01 Adversarial review of scripts v1, recorded
- AC: AC-01, AC-02 | Files: reports/reviews/review-muse-wonder-full-1.0-1.md | Test: specweave review 1462 --record reports (recorded, verdict fix first)
