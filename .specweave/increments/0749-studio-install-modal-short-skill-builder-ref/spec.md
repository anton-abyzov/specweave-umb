---
increment: 0749-studio-install-modal-short-skill-builder-ref
title: 'Studio install modal: use short skill-builder ref'
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio install modal — use short skill-builder ref

## Overview

The Skill Studio "Install VSkill skill-builder" modal currently shows the install command as:

```
$ vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder
```

The duplicated `skills/skills` segment looks like a typo and confuses users. It comes from the literal disk path inside the vskill repo (`plugins/<plugin=skills>/skills/<skill=skill-builder>/SKILL.md`), but the `vskill install` CLI already supports a clean 3-part shorthand `owner/repo/skill-name` that resolves to the same file via marketplace plugin probing (`add.ts:1961-1992`).

This increment swaps both the modal display string and the eval-server spawn argv from the long path to the canonical short form `anton-abyzov/vskill/skill-builder`. Resolution is identical (proven by the existing CLI test suite); only the displayed/spawned argv string changes.

## User Stories

### US-001: Show clean skill-builder install command in Studio modal (P1)
**Project**: vskill

**As a** Skill Studio user clicking "Install" next to the VSkill skill-builder authoring engine
**I want** the install confirmation modal to show a clean, canonical install command
**So that** I'm not confused by a duplicated path segment that looks like a typo and so that copying the command into another shell yields a tidy, professional install line

**Acceptance Criteria**:
- [x] **AC-US1-01**: The Install VSkill skill-builder confirmation modal displays exactly `$ vskill install anton-abyzov/vskill/skill-builder` (no `plugins/skills/skills` segment).
- [x] **AC-US1-02**: When the user clicks "Run install", the eval-server spawns `vskill` with argv `["install", "anton-abyzov/vskill/skill-builder"]` — i.e., what the modal shows is exactly what gets executed (display↔spawn parity).
- [x] **AC-US1-03**: The install completes successfully end-to-end against the real vskill CLI — the 3-part ref resolves to `plugins/skills/skills/skill-builder/SKILL.md` via existing marketplace plugin probing, no CLI change required, no install regression.
- [x] **AC-US1-04**: All `Install VSkill skill-builder` modal copy outside the command pre block is unchanged (title, security note, "Cancel" / "Run install" buttons, success/failure stages, SSE live tail).

---

### US-002: Tests stay locked to the displayed/spawned command (P1)
**Project**: vskill

**As a** vskill maintainer
**I want** unit tests that pin both the displayed command string and the spawned argv to the new short ref
**So that** any future regression that re-introduces the long `plugins/skills/skills` form (or any other drift between what the modal shows and what the server runs) breaks the build instead of shipping silently

**Acceptance Criteria**:
- [x] **AC-US2-01**: `InstallEngineModal.test.tsx` asserts that the rendered command preview for the `vskill` engine equals `vskill install anton-abyzov/vskill/skill-builder` (existing display-string test updated, no new test added).
- [x] **AC-US2-02**: `install-engine-routes.test.ts` asserts that the spawned argv for engine `vskill` equals `["install", "anton-abyzov/vskill/skill-builder"]` (existing argv test updated, no new test added).
- [x] **AC-US2-03**: Both updated tests fail BEFORE the source change (RED) and pass AFTER (GREEN) — TDD discipline preserved.

## Functional Requirements

### FR-001: Display↔spawn argv parity
The string shown in the InstallEngineModal command preview MUST equal `"vskill " + INSTALL_COMMANDS.vskill.args.join(" ")` so users see exactly what the server will run. Any future engine added to the allow-list must satisfy this same parity.

### FR-002: No CLI changes
The `vskill` CLI (`add.ts`, `discoverSkills`, `installSingleSkillLegacy`) is OUT OF SCOPE. The 3-part `owner/repo/skill` resolution path it already exposes is what makes this fix safe; we rely on it but do not modify it.

## Success Criteria

- After the fix, the modal command preview reads `$ vskill install anton-abyzov/vskill/skill-builder` (clean, canonical).
- A real install run from Studio (Confirm → Run install → SSE → Done) succeeds against the published `anton-abyzov/vskill` repo.
- `npx vitest run` in the vskill repo passes the updated `InstallEngineModal.test.tsx` and `install-engine-routes.test.ts` files.
- `grep -r "anton-abyzov/vskill/plugins/skills/skills/skill-builder" src/` returns zero hits in the vskill repo (the long form is gone from displayable / spawnable code).

## Out of Scope

- vskill CLI changes (`add.ts`, marketplace detection, discovery) — relied upon as-is.
- vskill-platform repo (the public website at verified-skill.com) — its install commands are sourced from a database, not from these constants; separate concern.
- The `claude-plugin install skill-creator` argv for the Anthropic engine — already short and canonical, no change.
- Surfacing the upstream install error message in the modal failure stage — the failure UI is unchanged.
- Backwards-compat alias for the long-form ref in CLI parsing — `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder` already worked and continues to work; we only stop *displaying* it.

## Dependencies

- vskill CLI ≥ 0.5.x with marketplace 3-part probing in `add.ts` (already shipping).
- `.claude-plugin/marketplace.json` in the vskill repo with the `skills` plugin entry pointing at `./plugins/skills` (already present).
- `plugins/skills/skills/skill-builder/SKILL.md` on the default branch (already present, referenced by 0670).
