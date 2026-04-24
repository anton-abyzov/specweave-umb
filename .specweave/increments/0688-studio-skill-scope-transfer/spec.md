---
increment: 0688-studio-skill-scope-transfer
title: "Studio Skill Scope Transfer"
type: feature
priority: P2
status: planned
created: 2026-04-23
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Skill Scope Transfer

## Overview

vskill-studio currently shows skills grouped by scope (OWN, INSTALLED, GLOBAL) but offers no way to move a skill between scopes. Users who find a useful INSTALLED skill and want to edit/distribute it must manually `cp -r` into `./skills/`; conversely, users who author an OWN skill and want to test it against Claude Code must manually copy into `.claude/skills/`. This increment delivers two bidirectional, in-studio actions — **Promote to OWN** (INSTALLED/GLOBAL → OWN) and **Test-install** (OWN → INSTALLED/GLOBAL) — plus a provenance-gated **Revert**, with FLIP motion, 5-second Undo toast, persistent "promoted from" chip, and an append-only studio-wide operations log surfaced as a right-side drawer. All transport reuses the existing SSE infrastructure (no WebSocket added).

**Target repo:** `repositories/anton-abyzov/vskill` (vskill CLI / studio UI).
**Sync project:** `specweave`.

## User Stories

### US-001: Promote INSTALLED/GLOBAL skill to OWN (P2)
**Project**: specweave

**As a** vskill-studio user who discovered a useful installed skill
**I want** a "Promote to OWN" context-menu action on INSTALLED/GLOBAL rows that copies the skill into my `./skills/` directory with a visible motion cue
**So that** I can edit and distribute the skill without manually shelling out to `cp -r`

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Right-clicking an INSTALLED or GLOBAL skill row shows a "Promote to OWN" menu item; clicking it issues `POST /api/skills/:plugin/:skill/promote` over SSE, which streams events `started → copied → indexed → done` and on `done` the row is FLIP-animated into the OWN section with a single 150ms accent-color pulse on the landed row. (Plan AC1)
- [ ] **AC-US1-02**: If `prefers-reduced-motion: reduce` is set at the OS or browser level, the promote completes with an instant re-parent — no flight animation, no accent pulse, no toast auto-animation. (Plan AC3)
- [ ] **AC-US1-03**: If `./skills/<name>/` already exists and the request does not include `?overwrite=true`, the server returns HTTP 409 and makes zero filesystem changes; the error surfaces to the user via the existing toast error channel. (Plan AC4)
- [ ] **AC-US1-04**: Promote writes a `.vskill-meta.json` provenance sidecar into the new `./skills/<name>/` directory containing `{ promotedFrom, sourcePath, promotedAt, sourceSkillVersion? }` conforming to the `Provenance` type defined in plan.md.
- [ ] **AC-US1-05**: The context-menu action is reachable via keyboard only (existing menu nav pattern) and triggering it with Enter produces the same result as mouse-click, including focus management.

---

### US-002: Test-install OWN skill into INSTALLED or GLOBAL (P2)
**Project**: specweave

**As a** vskill-studio user who just authored an OWN skill
**I want** a "Test-install" action on OWN rows that copies the skill into `.claude/skills/` (project) or `~/.claude/skills/` (global)
**So that** Claude Code can consume the skill immediately without me running `vskill add` manually

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Right-clicking an OWN skill row shows a "Test-install" action; invoking it issues `POST /api/skills/:plugin/:skill/test-install` which reuses the same `copyFileSync` code path as the `vskill add` command (no duplicated copy logic). (Plan AC5)
- [ ] **AC-US2-02**: Passing `?dest=global` targets `~/.claude/skills/<name>/` instead of the default project-scoped `.claude/skills/<name>/`; omitting the query param defaults to INSTALLED (project). (Plan AC5)
- [ ] **AC-US2-03**: On SSE `done`, the skill appears in the INSTALLED (or GLOBAL, per `dest`) section via scanner refresh; if motion is enabled, a FLIP animation mirrors the promote direction.
- [ ] **AC-US2-04**: Test-install against a destination that already contains the skill returns HTTP 409 unless `?overwrite=true`, matching the promote collision semantics in AC-US1-03.

---

### US-003: Undo and Revert with persistent provenance chip (P2)
**Project**: specweave

**As a** vskill-studio user who just promoted a skill
**I want** a 5-second Undo toast immediately after promote AND a persistent "Promoted from …" chip with a Revert button on OWN rows that have provenance
**So that** I can quickly cancel an accidental promote and still reverse a promote later via a deliberate affordance

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Immediately after a successful promote, a toast with `role="status"` appears for 5 seconds containing an "Undo" action; clicking Undo within the window calls the revert endpoint, which physically deletes `./skills/<name>/` and appends a `promote-reverted` op to the log. The original `promote` op is NOT erased — the log is append-only. (Plan AC2)
- [ ] **AC-US3-02**: After promote, a "Promoted from `<source-path>`" chip appears on the OWN row labeled with the source scope (INSTALLED or GLOBAL); it renders prominently for 30 seconds, then shrinks to a small persistent provenance badge that stays visible until the user reverts or explicitly dismisses it. (Plan AC9)
- [ ] **AC-US3-03**: The Revert button is hidden entirely on OWN rows that have no `.vskill-meta.json` sidecar — skills authored from scratch cannot be reverted, because revert is a delete operation and would destroy user-authored work. (Plan AC10)
- [ ] **AC-US3-04**: Revert is gated by provenance: hitting the revert endpoint for a skill without `.vskill-meta.json` returns HTTP 400 and changes no files.
- [ ] **AC-US3-05**: The toast is keyboard-dismissable with Esc, and the Undo button is reachable via Tab from the toast focus ring.

---

### US-004: Studio operations log (JSONL) + OpsDrawer + StatusBar chip (P2)
**Project**: specweave

**As a** vskill-studio user
**I want** every file-changing operation logged to an append-only JSONL file and surfaced through a right-side drawer toggled from a StatusBar chip
**So that** I can audit what the studio has done to my filesystem and see live updates while working

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Every promote, test-install, and revert operation appends exactly one newline-terminated JSON line to `~/.vskill/studio-ops.jsonl` with shape `{id, ts, op, skillId, fromScope, toScope, paths, actor}` conforming to the `StudioOp` type in plan.md; the append is atomic (no partial writes observable under concurrent operations). (Plan AC6)
- [ ] **AC-US4-02**: The StatusBar renders an ops-count chip showing the number of ops in the current session; clicking the chip toggles the OpsDrawer open/closed, and Esc closes the drawer returning focus to the chip. (Plan AC7)
- [ ] **AC-US4-03**: OpsDrawer renders a virtualized newest-first list (reuses existing `react-virtuoso` integration) where each row is expandable to show source/dest paths, timestamp, and raw op JSON. (Plan AC8)
- [ ] **AC-US4-04**: OpsDrawer subscribes to `GET /api/studio/ops/stream` (SSE) and live-prepends new op entries as they are appended to the log — no polling, no manual refresh required. (Plan AC8)
- [ ] **AC-US4-05**: Initial OpsDrawer load paginates via `GET /api/studio/ops?before=<ts>&limit=N` so opening against a large log does not block the UI.
- [ ] **AC-US4-06**: When the drawer is open, focus is trapped inside it (existing focus-trap pattern); pressing Esc closes the drawer and returns focus to the StatusBar chip.

## Success Criteria

- Zero manual `cp -r` operations needed for a round-trip promote → edit → test-install → revert flow.
- Every file change attributable to studio is discoverable via `~/.vskill/studio-ops.jsonl` within one line-append of the operation completing.
- FLIP animation honors `prefers-reduced-motion` on 100 % of tested paths.
- All 10 plan ACs have at least one covering spec AC (see Traceability table below).

## Out of Scope

- Syncing promoted skills back to any registry or `vskill publish` integration
- Multi-agent scope beyond Claude (Cursor, Windsurf) — the tri-scope agent picker stays as-is from increment 0686
- Log filtering / search UI — promote drawer to a dedicated page only when volume demands it
- Read-only op events (navigation, selection) — log is file-change only per user directive
- Log compaction / rotation automation — defer until the file grows large enough to matter

## Dependencies

- Increment 0686 (tri-scope + agent picker) — provides GLOBAL scope plumbing this increment builds on.
- Existing SSE transport (`src/eval-ui/src/lib/sse.ts`) — reused for promote / test-install / revert / ops stream endpoints.
- Existing `copyFileSync` logic in `src/commands/add.ts:100-104` — lifted into a shared helper and reused by test-install.
- Existing `react-virtuoso` usage — reused for OpsDrawer virtualization.

## Traceability (plan AC → spec AC)

| Plan AC | Spec AC |
|---|---|
| AC1 (FLIP on promote) | AC-US1-01 |
| AC2 (Undo toast deletes copy + logs revert op) | AC-US3-01 |
| AC3 (reduced-motion instant re-parent) | AC-US1-02 |
| AC4 (409 on collision without overwrite) | AC-US1-03 |
| AC5 (Test-install uses vskill add code path, `?dest=global` supported) | AC-US2-01, AC-US2-02 |
| AC6 (JSONL append atomic, correct schema) | AC-US4-01 |
| AC7 (StatusBar ops-count chip toggles OpsDrawer) | AC-US4-02 |
| AC8 (OpsDrawer virtualized + live SSE updates) | AC-US4-03, AC-US4-04 |
| AC9 (Provenance chip persists, labeled with source) | AC-US3-02 |
| AC10 (Revert button hidden without provenance) | AC-US3-03 |
