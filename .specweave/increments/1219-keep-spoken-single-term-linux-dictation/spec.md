# 1219 Keep spoken single-term Linux dictation

## Problem

Linux dictation drops a correctly recognized spoken term when it equals the vocabulary prompt.

## Scope

Transcript filtering after local recognition.

## Acceptance Criteria

- [ ] AC-01 A spoken single vocabulary term survives filtering.
- [ ] AC-02 Quiet echoes and a replay of the vocabulary list are still filtered.

## Approach

Use the peak and the actual vocabulary terms when judging prompt echoes.

## Tasks

### T-01 Keep recognized spoken terms

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/vocabulary.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/vocabulary.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/ipc/methods/voice.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/desktop" && node ../../node_modules/vite-plus/bin/vp test run src/voice/vocabulary.test.ts --maxWorkers=1
