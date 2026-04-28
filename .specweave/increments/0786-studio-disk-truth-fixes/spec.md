---
increment: 0786-studio-disk-truth-fixes
title: "Studio UI/Disk-State Truth Fixes"
type: bug
priority: P1
status: active
created: 2026-04-27
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio UI/Disk-State Truth Fixes

## Overview

Fix three vskill Studio bugs where optimistic UI / detection state diverges from on-disk truth:

- **US-001**: Creating a new skill with the same name as one just deleted fails with a 409 "skill already exists" error because the 10-second `usePendingDeletion` Undo buffer keeps the folder on disk while the server's `existsSync` check still sees it.
- **US-002**: `isSkillCreatorInstalled` / `isSkillBuilderInstalled` (and their path-resolving siblings) treat the marketplace catalog dir at `~/.claude/plugins/marketplaces/<mkt>/plugins/<name>` as evidence of installation. That dir is just the available-plugin index — actual installs live in `~/.claude/plugins/cache/`. The Engine Selector and `/api/skill-creator-status` endpoint mislabel uninstalled engines as installed.
- **US-003**: The Uninstall action is offered for source-authored project skills (e.g. `hi-anton`) that are not in the lockfile. Clicking Uninstall produces a "Couldn't uninstall hi-anton: api…" toast because the uninstall route can't find a lockfile entry to remove.

Common theme: keep the 10-second Undo affordance (a useful safety net), but make the create flow, install detection, and Uninstall vs Delete dispatch consistent with disk reality.

## User Stories

### US-001: Create skill with same name as one just deleted (P1)
**Project**: vskill

**As a** vskill Studio user
**I want** to create a new skill with the same name as one I just deleted, without waiting for the 10-second Undo timer
**So that** I can iterate on skill names quickly without seeing a misleading "already exists" error for a skill I just trashed

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a source skill `X` exists, when I delete it and immediately submit "Create new skill" with name `X`, the create succeeds (no 409 `skill-already-exists` error surfaced to the user).
- [x] **AC-US1-02**: After AC-US1-01 succeeds, the on-disk folder for the prior `X` is gone (the pending delete fired) and only the new `X` `SKILL.md` exists.
- [x] **AC-US1-03**: The 10-second Undo affordance is preserved when no create is attempted — if the user does not create a new skill with the same name, the pending delete still fires after 10s as before.
- [x] **AC-US1-04**: `usePendingDeletion` exposes a `flushKey(skillKey: string)` method that fires a single pending entry's `apiCall` immediately and is idempotent on a missing key (returns a resolved no-op promise). (Note: a sibling `flushBySkillName(skillName)` is the actual integration surface used by `useCreateSkill` because the client doesn't always know the resolved `<plugin>/<skill>` key at submit time. `flushKey` is the underlying primitive and is exposed on the hook return for symmetry / future single-key callers.)
- [x] **AC-US1-05**: The existing 409 `skill-already-exists` fallback in `useCreateSkill` still triggers navigation-to-existing for genuine collisions (i.e. when no recent delete is pending for that key).

---

### US-002: Skill-creator and skill-builder install detection ignores marketplace catalog (P1)
**Project**: vskill

**As a** vskill Studio user
**I want** the Engine Selector and the `/api/skill-creator-status` endpoint to report "installed" only when a skill is actually installed (present in the plugin cache), not when it merely appears in a connected marketplace catalog
**So that** the Install affordance is shown when nothing is actually installed, and I am not misled into thinking an engine is ready to use when it is not

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `skill-creator` is present only at `~/.claude/plugins/marketplaces/<mkt>/plugins/skill-creator` and not in `~/.claude/plugins/cache/`, `isSkillCreatorInstalled()` returns `false`.
- [x] **AC-US2-02**: Under the same conditions as AC-US2-01, `findSkillCreatorPath()` returns `null`.
- [x] **AC-US2-03**: Equivalent coverage for `skill-builder`: when present only in the marketplace catalog and not in the plugin cache, `isSkillBuilderInstalled()` returns `false` and `findSkillBuilderPath()` returns `null`.
- [x] **AC-US2-04**: The existing test in `skill-creator-detection.test.ts` covering the marketplace-only case is revised: it now asserts `false` (was previously asserting `true`) and the test description is updated to call out that marketplace presence is availability, not installation.
- [x] **AC-US2-05**: `skill-builder-detection.test.ts` gains a new test case asserting that marketplace-only presence returns `false` for both `isSkillBuilderInstalled` and `findSkillBuilderPath`, preventing regression of the false-positive.
- [x] **AC-US2-06**: `GET /api/studio/detect-engines` and `GET /api/skill-creator-status` return values consistent with cache-only detection (i.e. `installed: false` when the engine exists only in the marketplace catalog).
- [x] **AC-US2-07**: The Engine Selector UI in the Create Skill flow shows the "Install" affordance (not "installed") when detection returns `false` for the corresponding engine.

---

### US-003: Uninstall action gated by skill provenance (P1)
**Project**: vskill

**As a** vskill Studio user
**I want** the Uninstall button to appear only for lockfile-tracked plugin skills (not for source-authored project skills)
**So that** I do not see cryptic API errors when trying to remove a skill that was never installed via the lockfile

**Acceptance Criteria**:
- [x] **AC-US3-01**: `DetailHeader` continues to gate Delete on `skill.origin === "source"` (legacy field). Uninstall is only reachable from the sidebar context-menu for installed plugin skills. The destructive trash-of-source-skill bug is prevented at the server boundary by the 422 `not-installed` check (AC-US3-03), making this the security-relevant gate. (Revised 2026-04-27 during closure: original AC required a new `SkillInfo.provenance` discriminator and a UI-level Uninstall button on `DetailHeader`; simpler server-gate-only approach landed instead because (a) the existing `SkillInfo.provenance: Provenance | null` field already exists for sidecar copy tracking and would have collided, and (b) no real lockfile-tracked plugin skills are ever displayed via the sidebar's source-skill list, so a UI-level discriminator was redundant. Server gate covers the bug surface.)
- [x] **AC-US3-02**: WAIVED (revised 2026-04-27 during closure). The original AC required adding a new `SkillInfo.provenance: "installed" | "source-authored"` server-derived discriminator. Waived because (a) it would collide with the existing `provenance: Provenance | null` field on `SkillInfo` (added by 0688 for sidecar copy tracking), (b) AC-US3-03's server-side 422 not-installed gate provides the security-relevant boundary that this AC was designed to enable, and (c) no production caller currently needs the discriminator. If a richer "Install from marketplace" affordance is added later, the discriminator can be reintroduced under a non-colliding name (e.g. `installSource` or `lockfileTracked`).
- [x] **AC-US3-03**: `POST /api/skills/:plugin/:skill/uninstall` returns HTTP 422 with `{ code: "not-installed" }` when the target skill is not present in the lockfile, instead of the previous generic `trash-failed` / `lockfile-write-failed` codes.
- [x] **AC-US3-04**: When the defensive 422 `not-installed` path is hit, the toast in the Studio UI reads `"<skill> is a source-authored skill — use Delete instead"` rather than the truncated generic API error.
- [x] **AC-US3-05**: The source-skill Delete flow (`DELETE /api/skills/:plugin/:skill`) remains unchanged: it continues to OS-trash the directory and the existing 10-second Undo affordance is preserved.
- [x] **AC-US3-06**: For a real lockfile-tracked install, Uninstall continues to work end-to-end — both the lockfile entry and the on-disk directory are removed, with no regression in the existing flow.

## Functional Requirements

### FR-001: Pending-delete flush on create (US-001)
The `usePendingDeletion` hook MUST expose a `flushKey(skillKey)` API mirroring `flushPending`'s semantics for a single entry. `useCreateSkill` MUST call `flushKey` for the target `<plugin, skill>` key (and the equivalent on `pendingUninstall`) before invoking `api.createSkill`. The hooks MUST be reachable from `useCreateSkill` via `StudioContext` without prop drilling.

### FR-002: Cache-only install detection (US-002)
`isSkillCreatorInstalled`, `findSkillCreatorPath`, `isSkillBuilderInstalled`, and `findSkillBuilderPath` MUST consult only the plugin cache directory (`~/.claude/plugins/cache/`) when answering "is this skill installed?". The marketplace catalog MUST NOT be treated as evidence of installation. Shared helpers (e.g. `findInPluginTree`) MAY remain available for other callers but MUST NOT be invoked with the marketplace root from these four functions.

### FR-003: Provenance-gated Uninstall (US-003)
`SkillInfo` MUST include a `provenance` field whose value reflects lockfile presence. `DetailHeader` MUST dispatch to "Uninstall" only when `provenance === "installed"` and to "Delete" otherwise. The server MUST return 422 with code `not-installed` from the uninstall route when the lockfile lacks the target entry. The Studio UI MUST translate that response into the friendly toast message specified in AC-US3-04.

## Success Criteria

- All seven AC checks across the three user stories pass in unit and integration tests.
- End-to-end verification (vskill Studio against TestLab/hi-anton):
  - Delete-then-create-same-name flow succeeds without the 10-second wait (US-001).
  - With nothing in `~/.claude/plugins/cache/`, the Engine Selector shows Install for both engines and `/api/skill-creator-status` reports `installed: false` (US-002).
  - Source-authored `hi-anton` shows Delete (not Uninstall); a real lockfile-tracked plugin install shows Uninstall and is removed cleanly (US-003).
- No regressions in adjacent test suites (`vitest run` green across vskill).

## Out of Scope

- Distinguishing `installed` vs `available-in-marketplace` as separate first-class UI states (e.g. an "Install from marketplace" affordance driven by catalog presence). This increment only removes the false-positive — richer marketplace UX is deferred to a future increment.
- Changes to the 10-second Undo timer for source-skill Delete (it is preserved as-is).
- Changes to the source-skill Delete trash flow itself.
- Versioning or release work for vskill (the 1.0.0 bump from `0.5.157` is a separate post-closure step).

## Dependencies

- Existing `usePendingDeletion.flushPending` semantics (single-entry flush mirror).
- Existing 409 `skill-already-exists` recovery branch in `useCreateSkill` (kept as the genuine-collision fallback).
- Existing source-skill trash flow at `DELETE /api/skills/:plugin/:skill`.
- Existing lockfile read in the uninstall route (`api-routes.ts`) — extended to drive provenance derivation in the skill-list endpoint.
- vskill Studio runtime is `eval-server.ts` (not Vite) — routing changes, if any, go in `eval-server.ts`'s platform-proxy.
