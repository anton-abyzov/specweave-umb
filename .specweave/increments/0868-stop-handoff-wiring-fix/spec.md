---
increment: 0868-stop-handoff-wiring-fix
title: Fix dead Stop-handoff wiring (0867 AC-US7-02)
type: bug
priority: P1
status: completed
created: 2026-06-03T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: Gated Stop auto-handoff never fires in production (0867 AC-US7-02)

## Overview

Increment 0867 shipped a gated **Stop** auto-handoff: when an auto/handoff session is
active (`.specweave/state/auto-mode.json` present), a turn-end (Stop) should auto-write a
work-handoff doc + `.diff`, the same way PreCompact does. The handler (`handleStop` in
`src/core/hooks/handlers/pre-compact.ts`) is correct and self-gates, and the hook-router
maps the event key `'stop' → handleStop`. **But nothing ever invokes it**: the plugin's
`plugins/specweave/hooks/hooks.json` `Stop[]` array only runs `specweave hook stop-reflect`,
`stop-auto`, and `stop-sync` — never `specweave hook stop`. So the router's `'stop'` entry
is unreachable and the Stop auto-handoff never runs in the shipped product (confirmed in
the published `specweave@1.0.588` tarball). The existing unit tests pass because they call
`handleStop()` **directly**, masking the dead wiring with a green false-positive.

## Problem

- `hooks.json` `Stop[]` → `stop-reflect | stop-auto | stop-sync` only. No `stop`.
- `hook-router.ts` `HANDLERS['stop'] → pre-compact.js#handleStop` exists but is never dispatched.
- `pre-compact.test.ts` calls `handleStop()` directly → the wiring gap is invisible to CI.
- Net effect: AC-US7-02 ("a Stop, under an active auto session, auto-writes a handoff") is
  **not satisfied at runtime**, even though every related unit test is green.

## Goal

The Stop hook, under an active auto session, actually writes a handoff — wired through the
real plugin → CLI → router → handler path — and a test exercising that real path (plus a
wiring pin) prevents the regression from recurring. PreCompact behavior and the existing
`stop-reflect/stop-auto/stop-sync` entries are left untouched.

## Decision

Use **option (b)**: add a `specweave hook stop` invocation to the `hooks.json` `Stop[]`
array (mirroring the existing safe-fallback command shape). This is minimal and matches the
router's pre-existing `'stop' → handleStop` mapping. Option (a) — folding `handleStop` into
`stop-auto` — was rejected: `stop-auto` is itself **not** registered in the Node hook-router
(`specweave hook stop-auto` currently returns the safe default), so folding into it would
chain onto an unrelated, separately-routed path and muddy ownership.

## User Stories

### US-001: Stop auto-handoff fires through the real plugin wiring (P1)
**Project**: specweave

**As a** developer whose auto/handoff session ends a turn (Stop) while low on tokens
**I want** the Stop hook to actually auto-write a handoff (as PreCompact already does)
**So that** a portable handoff exists at turn-end during an auto session, not just on compaction.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `plugins/specweave/hooks/hooks.json` `Stop[]` includes a command that runs
  `specweave hook stop` (using the same `command -v specweave && … || { cat >/dev/null; echo '{"decision":"approve"}'; }` safe-fallback shape and a `timeout`), so the router's `'stop' → handleStop` entry is reachable. The existing `stop-reflect`/`stop-auto`/`stop-sync` entries are preserved unchanged.
- [x] **AC-US1-02**: A test drives a Stop event through the **real dispatcher** (`hookRouter('stop', stdin)`), not a direct `handleStop()` call: with `auto-mode.json` present it writes a handoff doc; absent, it writes nothing. Both return the safe `{ continue: true }` shape.
- [x] **AC-US1-03**: A wiring **pin test** parses `hooks.json` and asserts the `Stop` array contains a `specweave hook stop` invocation (distinct from `stop-reflect/stop-auto/stop-sync`), so the wiring cannot silently regress.
- [x] **AC-US1-04**: PreCompact wiring and behavior are unchanged; the full existing `pre-compact.test.ts` suite plus all other handoff tests stay green; no edits to `stop-reflect/stop-auto/stop-sync` behavior.

## Out of Scope

- Whether `stop-reflect/stop-auto/stop-sync` are themselves correctly routed in the Node
  hook-router (runtime probe suggests they hit the "unknown event type" safe default). That
  is a separate, larger investigation — flagged, not fixed here.
- Any change to PreCompact, the handoff doc format, or the builder.

## Success Criteria

- `npx vitest run` for the hook handler + any new wiring test passes.
- `hooks.json` `Stop[]` runs `specweave hook stop`; a routed Stop with `auto-mode.json`
  present writes a handoff; absent, it does not.
- The corrected wiring ships in a republished CLI so the global binary fires the Stop handoff.

## Dependencies

- 0867 handoff builder + `pre-compact.ts` handler (`handle`, `handleStop`), `hook-router.ts`,
  `hook.ts` (`specweave hook` entry), `plugins/specweave/hooks/hooks.json`.
