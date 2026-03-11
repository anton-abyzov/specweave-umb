---
id: US-005
feature: FS-470
title: "`vskill studio` CLI Command"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 63
    url: https://github.com/anton-abyzov/vskill/issues/63
---

# US-005: `vskill studio` CLI Command

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author
**I want** to run `vskill studio` to launch the Skill Studio UI
**So that** I have a discoverable, memorable entry point separate from the `eval serve` subcommand

---

## Acceptance Criteria

- [x] **AC-US5-01**: A new top-level `studio` command is registered in `src/index.ts` via Commander, with the description "Launch the Skill Studio UI for local skill development"
- [x] **AC-US5-02**: `vskill studio` accepts the same `--root <path>` and `--port <number>` options as `vskill eval serve`
- [x] **AC-US5-03**: `vskill studio` delegates to the existing `runEvalServe()` function, reusing all port selection logic (hash-based deterministic port 3077-3177, conflict detection, auto-kill)
- [x] **AC-US5-04**: `vskill eval serve` continues to work as before (not removed, not changed)
- [x] **AC-US5-05**: The terminal output when launching via `vskill studio` says "Skill Studio" instead of "Eval UI" in the startup banner

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add `vskill studio` top-level CLI command
